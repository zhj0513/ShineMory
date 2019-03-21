from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models import Users

bp = Blueprint('user', __name__)
api = Api(bp)


@api.resource('/')
class User(Resource):
    def post(self):
        data = request.json
        email = data.get('email')
        name = data.get('name')
        pwd = data.get('password')
        address = data.get('address')
        user = Users(email=email, username=name, password=pwd, address=address)
        user.save_to_db()
        return {"message":"ok"}, 200