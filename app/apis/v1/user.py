import re
from flask import Blueprint, request, abort
from flask_jwt_extended import create_access_token
from flask_restful import Api, Resource

from app import db
from app.commons.decorators import admin_required
from app.commons.email import send_mail
from app.models import Users

bp = Blueprint('user', __name__)
api = Api(bp)


@api.resource('/admin')
class AdminOperate(Resource):
    # @admin_required
    def get(self):  # 获取用户列表
        users = Users.query.filter_by(authority=0).all()
        return [user.to_dict() for user in users], 200

    # @admin_required
    def post(self):  # 新增一个用户
        data = request.json
        email = data.get('email')
        name = data.get('username')
        pwd = data.get('password')
        address = data.get('address')
        user = Users(email=email, username=name, password=pwd, address=address)
        # abort(400, 'xxxxx')
        user.save_to_db()
        return 200

    def put(self):  # 管理员修改用户信息
        data = request.json
        id = data.get('id')
        user = Users.query.get(id)
        user.username = data.get('username')
        user.password = data.get('password')
        user.address = data.get('address')
        user.save_to_db()
        return 200

    # @admin_required
    def delete(self):  # 删除一个用户
        id = request.args.get('id')
        user = Users.query.get(id)
        db.session.delete(user)
        db.session.commit()


@api.resource('/login')
class UserLogin(Resource):
    def post(self):  # 登录
        email = request.json.get('email')  # 以邮箱作为账号
        pwd = request.json.get('password')
        if not (email and re.match(r"^([a-zA-Z0-9._-])+@([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-]+){1,2}$", email)):
            abort(400, '邮箱格式不正确')
        user = Users.query.filter_by(email=email).first()
        if not user:
            abort(400, '该用户不存在')
        elif user.password != pwd:
            abort(400, '密码验证错误')

        access_token = create_access_token(identity=user.to_dict())
        result = {'name': user.username, 'authority': user.authority, 'access_token': access_token}
        return result


@api.resource('/register')
class UserRegister(Resource):
    def post(self):
        data = request.json
        email = data.get('email')
        if not (email and re.match(r"^([a-zA-Z0-9._-])+@([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-]+){1,2}$", email)):
            abort(400, '邮箱格式不正确')
        username = data.get('username')
        pwd = data.get('password')
        pwd2 = data.get('password2', pwd)
        if pwd != pwd2:
            abort(400, '请重新设置密码')
        address = data.get('address')
        user = Users(email=email, username=username, password=pwd, address=address)
        user.save_to_db()
        send_mail('1264728987@qq.com', '注册成功', username)
        return 200
