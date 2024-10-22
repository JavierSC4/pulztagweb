# models.py

from extensions import db
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import current_app
from datetime import datetime
import uuid

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # Relación con Pulzcards
    pulzcards = db.relationship('Pulzcard', backref='owner', lazy=True)

    def get_reset_token(self, expires_sec=3600):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.email, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=3600):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
        except SignatureExpired:
            return None
        except:
            return None
        return User.query.filter_by(email=email).first()

class Pulzcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    organization = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    card_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Pulzcard('{self.card_name}', '{self.email}')"