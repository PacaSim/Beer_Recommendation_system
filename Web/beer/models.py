from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80))
  password = db.Column(db.String(200))
  beer = db.Column(db.String(200))
  rates = db.relationship('Rate')

class Rate(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  beer = db.Column(db.String(200))
  rating = db.Column(db.Float)
  oneline = db.Column(db.String(300))