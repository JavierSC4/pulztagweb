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

    # Relaciones con otros modelos
    pulzcards = db.relationship('Pulzcard', backref='user', lazy=True)
    tags = db.relationship('Tag', backref='user', lazy=True)
    bodegas = db.relationship('Bodega', backref='user', lazy=True)

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
        except Exception:
            return None
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

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
    image_file = db.Column(db.String(100), nullable=True, default='default.jpg')
    template = db.Column(db.String(20), nullable=False, default='template1')

    # Clave foránea hacia User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Pulzcard('{self.card_name}', '{self.email}')"

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100), nullable=False)
    redirect_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tag_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    vistas = db.Column(db.Integer, default=0, nullable=False)  # Nueva columna para vistas

    # Clave foránea hacia User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Tag('{self.tag_name}', '{self.redirect_url}', '{self.tag_id}', Vistas: {self.vistas})"

class Bodega(db.Model):
    __tablename__ = 'bodega'  # Asegúrate de que el nombre de la tabla es consistente
    
    id = db.Column(db.Integer, primary_key=True)
    id_bodega = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    ubicacion = db.Column(db.String(255), nullable=True)
    notas = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relación con Caja
    cajas = db.relationship('Caja', backref='bodega', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bodega(id_bodega='{self.id_bodega}', nombre='{self.nombre}')>"

class Caja(db.Model):
    __tablename__ = 'caja'  # Asegúrate de que el nombre de la tabla es consistente
    
    id = db.Column(db.Integer, primary_key=True)
    id_caja = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(255), nullable=True)
    notas = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    bodega_id = db.Column(db.Integer, db.ForeignKey('bodega.id', ondelete='CASCADE'), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relación con Producto
    productos = db.relationship('Producto', backref='caja', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Caja(id_caja='{self.id_caja}', nombre='{self.nombre}')>"

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.String(10), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    categoria = db.Column(db.String(100), nullable=True)
    subcategoria = db.Column(db.String(100), nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    caja_id = db.Column(db.Integer, db.ForeignKey('caja.id', ondelete='CASCADE'), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Agregar el campo 'notas'
    notas = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Producto(id_producto='{self.id_producto}', nombre='{self.nombre}', cantidad={self.cantidad})>"

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin  # Verifica si el usuario es admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))