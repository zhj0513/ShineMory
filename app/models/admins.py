from app import db


class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(64))

    def to_dict(self):
        admin_dict = {
            'admin_id': self.id,
            'email': self.email,
            'username': self.username
        }
        return admin_dict
