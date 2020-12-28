from flaskapp import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    address = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    #role = 

    def __repr__(self):
        return f"{self.email}"