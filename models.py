# models.py

from extensions import db
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import current_app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # Puedes agregar más campos como nombre, apellido, etc.

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
        return User.query.filter_by(email=email).first()