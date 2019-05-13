from app import db
from app.extensions import SLBigInteger


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    pic_src = db.Column(db.String(128))  # 图片路径
    video_src = db.Column(db.String(128))  # 视频路径
    time = db.Column(SLBigInteger)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # user = db.relationship('User', backref=db.backref('articles', cascade="all,delete"))

    comments = db.relationship('Comment', backref='article', cascade='all,delete', lazy='dynamic')
    zans = db.relationship('Zan', backref='article', cascade='all,delete', lazy='dynamic')

    def to_dict(self):
        article_dict = {
            'article_id': self.id,
            'user_id': self.user_id,
            'body': self.body,
            'pic_src': self.pic_src,
            'video_src': self.video_src,
            'send_time': self.time,
            'zan': self.zans.count(),
            'comments_num': self.comments.count()
        }
        return article_dict

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
