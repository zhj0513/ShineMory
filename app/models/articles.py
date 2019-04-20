from app import db
from app.extensions import SLBigInteger


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    pic_src = db.Column(db.String(128))  # 图片路径
    video_src = db.Column(db.String(128))  # 视频路径
    time = db.Column(SLBigInteger)
    zan = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # user = db.relationship('User', backref=db.backref('articles', cascade="all,delete"))

    comments = db.relationship('Comment', backref='article', cascade='all,delete')
