from app import db
from app.extensions import SLBigInteger
from app.models import User


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    time = db.Column(SLBigInteger)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    zans = db.relationship('Zan', backref='comment', cascade='all,delete', lazy='dynamic')

    def to_dict(self):
        user = User.query.get(self.user_id)
        comment_dict = {
            'comment_id': self.id,
            'body': self.body,
            'send_time': self.time,
            'user_id': self.user_id,
            'username': user.username,
            'avatar_src': user.avatar_src,
            'article_id': self.article_id,
            'zan_num': self.zans.count()
        }
        return comment_dict

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
