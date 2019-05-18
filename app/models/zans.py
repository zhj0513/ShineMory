from app import db
from app.extensions import SLBigInteger


class Zan(db.Model):
    __tablename__ = 'zans'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(SLBigInteger)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
