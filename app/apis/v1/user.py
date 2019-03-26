from flask import Blueprint, request, abort
from flask_restful import Api, Resource

from app import db
from app.models import Users

bp = Blueprint('user', __name__)
api = Api(bp)


@api.resource('/')
class UserOperate(Resource):
    def post(self):
        data = request.json
        email = data.get('email')
        name = data.get('name')
        pwd = data.get('password')
        address = data.get('address')
        user = Users(email=email, username=name, password=pwd, address=address)
        # abort(400, 'xxxxx')
        user.save_to_db()

    def delete(self):
        id = request.args.get('id')
        user = Users.query.get(id)
        db.session.delete(user)
        db.session.commit()
