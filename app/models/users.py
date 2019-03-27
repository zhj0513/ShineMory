from app import db


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), unique=True)  # 邮箱作为登录账号
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(32))
    address = db.Column(db.String(128))

    # 级联删除
    # articles = db.relationship('Articles', backref=db.backref('user'), cascade="all,delete")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
