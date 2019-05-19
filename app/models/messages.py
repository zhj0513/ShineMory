from app import db
from app.extensions import SLBigInteger


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    time = db.Column(SLBigInteger)
    is_all = db.Column(db.Boolean)  # 用于标记是否发送给所有用户

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        message_dict = {
            'message_id': self.id,
            'body': self.body,
            'send_time': self.time,
            'user_id': self.user_id
        }
        return message_dict

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
