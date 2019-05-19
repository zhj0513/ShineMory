import time

import os

import re
from flask import Blueprint, request, abort, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Api, Resource
import random
from sqlalchemy import or_

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
        elif user.password != pwd:
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
        pwd2 = data.get('password2', pwd)
        if pwd != pwd2:
            abort(400, '请重新设置密码')
        address = data.get('address')
        interest = data.get('interest')
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
        current_user = get_jwt_identity()
        id = current_user.get('id')
        user = User.query.get(id)
        data = request.json
        if not User.query.filter_by(username=data.get('username')).first():
            user.username = data.get('username')
        else:
            abort(400, '用户名已存在')
        user.address = data.get('address', user.address)
        user.about_me = data.get('about_me', user.about_me)
        user.interest = data.get('interest', user.interest)
        user.save_to_db()
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


@api.resource('/follow/<user_id>')
class UserFollow(Resource):
    @jwt_required
    def get(self, user_id):  # 判断是否已经关注
        current_user = User.get_current_user()
        target_user = User.query.get(user_id)
        return current_user.is_following(target_user)

    @jwt_required
    def post(self, user_id):  # 关注其他用户
        current_user = User.get_current_user()
        target_user = User.query.get(user_id)
        current_user.follow(target_user)
        send_time = round(time.time()*1000)
        body = current_user.username + '关注了您'
        message = Message(body=body, time=send_time, is_all=False, user_id=target_user.id)
        message.save_to_db()
        return 200

    @jwt_required
    def delete(self, user_id):  # 取消关注其他用户
        current_user = User.get_current_user()
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
    def get(self):  # 根据兴趣推荐3位用户关注(未测试)
        current_user = User.get_current_user()
        interest_list = current_user.interest.split(',') if current_user.interest else []
        if interest_list:
            interest = random.choice(interest_list)  # 取数组中的随机一个元素
            users = User.query.filter_by(User.interest.contains(interest), User.id != current_user.id).all()
        else:
            users = User.query.filter_by(User.id != current_user.id).all()
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
    def get(self):  # 获取消息列表(未测试)
        current_user = User.get_current_user()
        messages = Message.query.filter(or_(Message.user_id == current_user.id, Message.is_all is True)).all()
        messages_list = [message.to_dict() for message in messages]
        return messages_list

    @jwt_required
    def delete(self):  # 删除消息(未测试)
        message_id = request.args.get('message_id')
        message = Message.query.get(message_id)
        db.session.delete(message)
        db.session.commit()
        update_message_num()
        return 200
