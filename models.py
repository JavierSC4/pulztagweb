# models.py

from extensions import db
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import current_app, redirect, url_for, flash, request
from datetime import datetime
import uuid

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=True)  # Cambiado a True
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)
    must_change_password = db.Column(db.Boolean, default=True)

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
    image_file = db.Column(db.String(100), nullable=True, default='default.jpg')
    template = db.Column(db.String(20), nullable=False, default='template1')

    # Definir la relación con User
    owner = db.relationship('User', backref=db.backref('pulzcards', lazy=True))

    def __repr__(self):
        return f"Pulzcard('{self.card_name}', '{self.email}')"
    
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100), nullable=False)
    redirect_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tag_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    def __repr__(self):
        return f"Tag('{self.tag_name}', '{self.redirect_url}', '{self.tag_id}')"
    
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin  # Verifica si el usuario es admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))