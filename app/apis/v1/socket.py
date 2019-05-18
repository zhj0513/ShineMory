from flask import Blueprint

from app.extensions import socket
from app.models import User, Message

bp = Blueprint('socket', __name__)


@socket.on('connect', namespace='/api/v1/socket')
def test_connect():
    # 连接事件处理程序可以选择返回False以拒绝连接。这样就可以在此时对客户端进行身份验证。
    socket.emit('connect_test', 'Socket Connected')
    update_message_num()
    return True


@bp.route('/send')
def send():
    socket.emit('job', 'testtest', namespace='/api/v1/socket')
    return 'message sent'


@socket.on('haha', namespace='/api/v1/socket')
def test_send(json):
    print('json' + str(json))


def update_message_num():  # 更新消息通知条数
    current_user = User.get_current_user()
    messages_num = Message.query.filter(or_(Message.user_id == current_user.id, Message.is_all is True)).count()
    socket.emit('message_num', {'message_num': messages_num}, namespace='/api/v1/socket')
    return True
