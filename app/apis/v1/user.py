import re
from flask import Blueprint, request, abort
from flask_jwt_extended import create_access_token, jwt_required
from flask_restful import Api, Resource

from app import db
from app.commons.decorators import admin_required
from app.commons.email import send_mail
from app.models import User

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

        access_token = create_access_token(identity=user.to_dict())
        result = {'id': user.id, 'username': user.username, 'access_token': access_token}
        return result


@api.resource('/register')
class UserRegister(Resource):
    def post(self):
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
        user = User(email=email, username=username, password=pwd, address=address)
        user.save_to_db()
        send_mail(user.email, '注册成功', username)
        return 200
