import re
from flask import Blueprint, request, abort
from flask_jwt_extended import create_access_token, jwt_required
from flask_restful import Api, Resource
from sqlalchemy import or_

from app import db
from app.apis.v1.socket import update_message_num
from app.commons.decorators import admin_required
from app.models import User, Admin, Message

bp = Blueprint('admin', __name__)
api = Api(bp)


@api.resource('/admin')
class AdminOperate(Resource):
    @jwt_required
    @admin_required
    def get(self):  # 获取用户列表
        search = request.args.get('search')
        if search:
            users = User.query.filter(
                or_(User.username.like('%' + search + '%'), User.email.like('%' + search + '%'))).all()
        else:
            users = User.query.all()
        return [user.to_dict() for user in users], 200

    @jwt_required
    @admin_required
    def post(self):  # 新增一个用户
        data = request.json
        email = data.get('email')
        username = data.get('username')
        pwd = data.get('password')
        if User.query.filter_by(email=email).first():
            abort(400, '账号已存在')
        if User.query.filter_by(username=username).first():
            abort(400, '用户名已存在')
        user = User(email=email, username=username, password=pwd)
        user.save_to_db()
        return 200

    @jwt_required
    @admin_required
    def put(self):  # 管理员修改用户信息
        data = request.json
        id = data.get('id')
        user = User.query.get(id)
        user.username = data.get('username', user.username)
        user.password = data.get('password', user.password)
        user.save_to_db()
        return 200

    @jwt_required
    @admin_required
    def patch(self):  # 管理员禁用一个用户
        data = request.json
        id = data.get('id')
        user = User.query.get(id)
        user.ban = data.get('ban', 0)
        user.save_to_db()
        return 200

    @jwt_required
    @admin_required
    def delete(self):  # 删除一个用户
        id = request.args.get('id')
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()


@api.resource('/login')
class AdminLogin(Resource):
    def post(self):  # 登录
        email = request.json.get('email')  # 以邮箱作为账号
        pwd = request.json.get('password')
        if not (email and re.match(r"^([a-zA-Z0-9._-])+@([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-]+){1,2}$", email)):
            abort(400, '邮箱格式不正确')
        admin = Admin.query.filter_by(email=email).first()
        if not admin:
            abort(400, '该账户不存在')
        elif admin.password != pwd:
            abort(400, '密码验证错误')

        access_token = create_access_token(identity=admin.to_dict())
        result = {'id': admin.id, 'name': admin.username, 'access_token': access_token}
        return result


@api.resource('/notify')
class SendAll(Resource):
    @jwt_required
    @admin_required
    def post(self):  # 管理员发送系统消息(未测试)
        body = request.json.get('body')
        send_time = round(time.time()*1000)
        message = Message(body=body, time=send_time, is_all=True)
        message.save_to_db()
        return 200
