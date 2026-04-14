from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    entries = db.relationship("Entry", backref="user", lazy=True, cascade="all, delete-orphan")
    goal = db.relationship("Goal", backref="user", uselist=False, cascade="all, delete-orphan")
    measurements = db.relationship("Measurement", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Entry(db.Model):
    __tablename__ = "entries"

    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, db.ForeignKey("dim_date.date"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    goal_weight = db.Column(db.Float, nullable=False)
    start_weight = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

class DimDate(db.Model):
    __tablename__ = "dim_date"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    day = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)


class Measurement(db.Model):
    __tablename__ = "measurements"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    waist = db.Column(db.Float, nullable=True)
    hips = db.Column(db.Float, nullable=True)
    chest = db.Column(db.Float, nullable=True)
    neck = db.Column(db.Float, nullable=True)
    body_fat = db.Column(db.Float, nullable=True)
