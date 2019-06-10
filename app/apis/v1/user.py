import time

import os

import re
from flask import Blueprint, request, abort, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Api, Resource
import random
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, avatars
from app.apis.v1.socket import update_message_num
from app.commons.email import send_mail
from app.models import User, Message

bp = Blueprint('user', __name__)
api = Api(bp)


@api.resource('/login')
class UserLogin(Resource):
    def post(self):  # 登录
        email = request.json.get('email')  # 以邮箱作为账号
        pwd = request.json.get('password')
        if not (email and re.match(r"^([a-zA-Z0-9._-])+@([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-]+){1,2}$", email)):
            abort(400, '邮箱格式不正确')
        user = User.query.filter_by(email=email).first()
        if not user:
            abort(400, '该用户不存在')
        elif not check_password_hash(user.password, pwd):
            abort(400, '密码验证错误')
        elif user.ban == 1:
            abort(400, '该用户已被管理员禁用')

        access_token = create_access_token(identity=user.to_dict())
        result = {'user_id': user.id, 'username': user.username, 'access_token': access_token}
        return result


@api.resource('/register')
class UserRegister(Resource):
    def post(self):  # 用户注册
        data = request.json
        email = data.get('email')
        if not (email and re.match(r"^([a-zA-Z0-9._-])+@([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-]+){1,2}$", email)):
            abort(400, '邮箱格式不正确')
        if User.query.filter_by(email=email).first():
            abort(400, '账号已存在')
        username = data.get('username')
        if User.query.filter_by(username=username).first():
            abort(400, '用户名已存在')
        pwd = data.get('password')
        if len(pwd) < 6:
            abort(400, '密码过短')
        pwd2 = data.get('password2', pwd)
        if pwd != pwd2:
            abort(400, '请重新设置密码')
        address = data.get('address')
        interest = data.get('interest')
        pwd = generate_password_hash(pwd)
        user = User(email=email, username=username, password=pwd, address=address, interest=interest)
        user.save_to_db()
        send_mail(user.email, '注册成功', username)
        return 200


@api.resource('/userInfo')
class UserInfo(Resource):
    @jwt_required
    def get(self):  # 获取用户个人信息
        current_user = get_jwt_identity()
        username = current_user.get('username')
        user = User.query.filter_by(username=username).first()
        return user.to_user_info_dict()

    @jwt_required
    def post(self):  # 修改用户信息
        current_user = User.get_current_user()
        data = request.json
        if not User.query.filter_by(username=data.get('username')).first():
            current_user.username = data.get('username')
        else:
            abort(400, '用户名已存在')
        current_user.address = data.get('address', current_user.address)
        current_user.about_me = data.get('about_me', current_user.about_me)
        current_user.interest = data.get('interest', current_user.interest)
        current_user.save_to_db()
        return 200

    @jwt_required
    def patch(self):  # 用户上传头像
        current_user = get_jwt_identity()
        username = current_user.get('username')
        user = User.query.filter_by(username=username).first()
        file = request.files['avatar']
        print(file.filename)
        filename = username + '.' + file.filename.rsplit('.', 1)[1]
        file_path = os.path.join(current_app.config['UPLOADED_AVATARS_DEST'], filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            filename = avatars.save(request.files['avatar'], name=username+'.')
            user.avatar_src = os.path.join(request.url_root, 'static', 'avatar', filename)
        except Exception:
            abort(400, '文件格式错误或文件名全为中文字符')
        user.save_to_db()
        return {"user_id": user.id, "avatar_src": user.avatar_src}


@api.resource('/follow')
class UserFollow(Resource):
    @jwt_required
    def get(self):  # 判断是否已经关注
        current_user = User.get_current_user()
        user_id = request.args.get('user_id')
        target_user = User.query.get(user_id)
        return current_user.is_following(target_user)

    @jwt_required
    def post(self):  # 关注其他用户
        current_user = User.get_current_user()
        user_id = request.json.get('user_id')
        target_user = User.query.get(user_id)
        current_user.follow(target_user)
        send_time = round(time.time()*1000)
        body = current_user.username + '关注了您'
        message = Message(body=body, time=send_time, is_all=False, user_id=target_user.id)
        message.save_to_db()
        return 200

    @jwt_required
    def delete(self):  # 取消关注其他用户
        current_user = User.get_current_user()
        user_id = request.args.get('user_id')
        target_user = User.query.get(user_id)
        current_user.unfollow(target_user)
        send_time = round(time.time() * 1000)
        body = current_user.username + '对您取消了关注'
        message = Message(body=body, time=send_time, is_all=False, user_id=target_user.id)
        message.save_to_db()
        return 200


@api.resource('/recommend')
class UserRecommend(Resource):
    @jwt_required
    def get(self):  # 根据兴趣推荐3位用户关注
        current_user = User.get_current_user()
        interest_list = current_user.interest.split(',') if current_user.interest else []
        if interest_list:
            interest = random.choice(interest_list)  # 取数组中的随机一个元素
            users = User.query.filter(User.interest.contains(interest), User.id != current_user.id).all()
        else:
            users = User.query.filter(User.id != current_user.id).all()
        unfollow_users = [user for user in users if not current_user.is_following(user)]
        if len(unfollow_users) >= 3:
            recommend_users = random.sample(unfollow_users, 3)
        else:
            recommend_users = unfollow_users
        if recommend_users:
            recommend_users_dict = [user.to_dict() for user in recommend_users]
        else:
            recommend_users_dict = []
        return recommend_users_dict


@api.resource('/message')
class UserMessage(Resource):
    @jwt_required
    def get(self):  # 获取通知列表
        current_user = User.get_current_user()
        messages = Message.query.filter(or_(Message.user_id == current_user.id, Message.is_all == 1)).all()
        messages_list = [message.to_dict() for message in messages]
        return messages_list

    @jwt_required
    def delete(self):  # 删除一条通知
        message_id = request.args.get('message_id')
        message = Message.query.get(message_id)
        db.session.delete(message)
        db.session.commit()
        update_message_num()
        return 200


@api.resource('/get_followers')
class UserGetFollowers(Resource):
    @jwt_required
    def get(self):  # 获取关注者列表
        current_user = User.get_current_user()
        followers = current_user.follows.all()
        followers_list = [follow.follow_id for follow in followers] if followers else []
        if followers_list:
            users = User.query.filter(User.id.in_(followers_list)).all()
            followers_list = [user.to_dict() for user in users] if users else []
        return followers_list


@api.resource('/get_fans')
class UserGetFans(Resource):
    @jwt_required
    def get(self):  # 获取粉丝列表
        current_user = User.get_current_user()
        fans = current_user.fans.all()
        fans_list = [fan.fan_id for fan in fans] if fans else []
        if fans_list:
            users = User.query.filter(User.id.in_(fans_list)).all()
            fans_list = [user.to_dict() for user in users] if users else []
        return fans_list
