from flask_jwt_extended import get_jwt_identity
from flask import abort


def admin_required(fun):  # 验证管理员身份
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user:
            abort(400, '权限不足')
        return fun(*args, **kwargs)
    return wrapper
