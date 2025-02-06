from extensions import db
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import current_app, redirect, url_for, flash, request
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=True)  # Permitido nulo inicialmente
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    must_change_password = db.Column(db.Boolean, default=True)

    # Relaciones con otros modelos
    pulzcards = db.relationship('Pulzcard', back_populates='user', lazy=True, cascade="all, delete-orphan")
    tags = db.relationship('Tag', back_populates='user', lazy=True, cascade="all, delete-orphan")
    bodegas = db.relationship('Bodega', back_populates='user', lazy=True, cascade="all, delete-orphan")
    dashboard_items = db.relationship('DashboardItem', back_populates='user', lazy=True, cascade="all, delete-orphan")

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
    __tablename__ = 'pulzcards'
    
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
    
    # Campos para configuración de colores en el QR
    qr_fg_color = db.Column(db.String(7), nullable=False, default='#000000')
    qr_bg_color = db.Column(db.String(7), nullable=False, default='#ffffff')

    # Clave foránea hacia User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relación con User usando back_populates
    user = db.relationship('User', back_populates='pulzcards')

    def __repr__(self):
        return f"Pulzcard('{self.card_name}', '{self.email}')"

class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100), nullable=False)
    redirect_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tag_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    vistas = db.Column(db.Integer, default=0, nullable=False)
    
    # Campos para configuración de colores en el QR
    qr_fg_color = db.Column(db.String(7), nullable=False, default='#000000')
    qr_bg_color = db.Column(db.String(7), nullable=False, default='#ffffff')

    # Clave foránea hacia User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relación con User usando back_populates
    user = db.relationship('User', back_populates='tags')

    def __repr__(self):
        return f"Tag('{self.tag_name}', '{self.redirect_url}', '{self.tag_id}', Vistas: {self.vistas})"

class Bodega(db.Model):
    __tablename__ = 'bodegas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_bodega = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    ubicacion = db.Column(db.String(255), nullable=True)
    notas = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Campos para configuración de colores en el QR
    qr_fg_color = db.Column(db.String(7), nullable=False, default='#000000')
    qr_bg_color = db.Column(db.String(7), nullable=False, default='#ffffff')

    # Relación con User usando back_populates
    user = db.relationship('User', back_populates='bodegas')
    
    # Relación con Caja usando back_populates
    cajas = db.relationship('Caja', back_populates='bodega', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bodega(id_bodega='{self.id_bodega}', nombre='{self.nombre}')>"

class Caja(db.Model):
    __tablename__ = 'cajas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_caja = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(255), nullable=True)
    notas = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    bodega_id = db.Column(db.Integer, db.ForeignKey('bodegas.id', ondelete='CASCADE'), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relación con Bodega usando back_populates
    bodega = db.relationship('Bodega', back_populates='cajas')
    
    # Relación con Producto usando back_populates
    productos = db.relationship('Producto', back_populates='caja', lazy=True, cascade="all, delete-orphan")

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
    caja_id = db.Column(db.Integer, db.ForeignKey('cajas.id', ondelete='CASCADE'), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Agregar el campo 'notas'
    notas = db.Column(db.Text, nullable=True)

    # Relación con Caja usando back_populates
    caja = db.relationship('Caja', back_populates='productos')

    def __repr__(self):
        return f"<Producto(id_producto='{self.id_producto}', nombre='{self.nombre}', cantidad={self.cantidad})>"

class DashboardItem(db.Model):
    __tablename__ = 'dashboard_items'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Campos para configuración de colores en el QR
    qr_fg_color = db.Column(db.String(7), nullable=False, default='#000000')
    qr_bg_color = db.Column(db.String(7), nullable=False, default='#ffffff')

    # Relación con User usando back_populates
    user = db.relationship('User', back_populates='dashboard_items')

    # Relación con SurveyResponse usando back_populates
    responses = db.relationship('SurveyResponse', back_populates='item', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DashboardItem {self.name} for User {self.user_id}>"

class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('dashboard_items.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    
    # Relación con DashboardItem usando back_populates
    item = db.relationship('DashboardItem', back_populates='responses')

    def __repr__(self):
        return f"<SurveyResponse(item_id='{self.item_id}', rating={self.rating})>"

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin  # Verifica si el usuario es admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))