from app import db


class Follow(db.Model):
    __tablename__ = 'follow_fan'

    follow_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    fan_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
