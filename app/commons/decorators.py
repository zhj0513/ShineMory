from flask_jwt_extended import get_jwt_identity
from flask import abort

from app.models import Admin


def admin_required(fun):  # 验证管理员身份
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if not Admin.query.filter_by(username=current_user.get('username')).first():
            abort(400, '权限不足')
        return fun(*args, **kwargs)
    return wrapper
