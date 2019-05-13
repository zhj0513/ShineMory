from flask_jwt_extended import get_jwt_identity

from app import db
from app.commons.time_deal import millisecond_timestamp
from app.extensions import SLBigInteger
from app.models.follows import Follow


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), unique=True)  # 邮箱作为登录账号
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(32))
    address = db.Column(db.String(128))
    about_me = db.Column(db.Text)
    member_since = db.Column(SLBigInteger, default=millisecond_timestamp)
    ban = db.Column(db.Integer, default=0)  # 0:正常 1：封禁
    avatar_src = db.Column(db.String(128))  # 头像路径

    follows = db.relationship('Follow', foreign_keys=[Follow.fan_id], backref=db.backref('fan', lazy='joined'),
                              cascade="all,delete", lazy='dynamic')
    fans = db.relationship('Follow', foreign_keys=[Follow.follow_id], backref=db.backref('follow', lazy='joined'),
                           cascade="all,delete", lazy='dynamic')
    comments = db.relationship('Comment', backref='user', cascade="all,delete", lazy='dynamic')
    # 级联删除cascade="all,delete"
    articles = db.relationship('Article', backref='user', cascade="all,delete", lazy='dynamic')  # 若没加lazy='dynamic'懒查询,则不能用count()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        user_dict = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'address': self.address,
            'about_me': self.about_me,
            'member_since': self.member_since,
            'ban': self.ban,
            'avatar_src': self.avatar_src
        }
        return user_dict

    def to_user_info_dict(self):
        user_dict = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'address': self.address,
            'about_me': self.about_me,
            'member_since': self.member_since,
            'avatar_src': self.avatar_src,
            'articles_num': self.articles.count(),
            'follows_num': self.follows.count(),
            'fans_num': self.fans.count()
        }
        return user_dict

    @staticmethod
    def get_current_user():
        current_user = get_jwt_identity()
        user_id = current_user.get('id')
        user = User.query.get(user_id)
        return user

    def is_following(self, user):
        if user.id is None:
            return False
        return self.follows.filter_by(
            follow_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(fan_id=self.id, follow_id=user.id)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        if self.is_following(user):
            f = Follow.query.filter_by(fan_id=self.id, follow_id=user.id).first()
            db.session.delete(f)  # 批量删除xxx.query.filter_by(xxx).delete(synchronize_session=False)
            db.session.commit()
