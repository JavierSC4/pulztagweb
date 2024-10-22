# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, ValidationError, Optional
from models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Crear Cuenta')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso. Por favor, elige otro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este correo electrónico ya está registrado. Por favor, inicia sesión o usa otro correo.')

class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class UpdateAccountForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Nueva Contraseña', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirmar Nueva Contraseña', validators=[EqualTo('password')])
    submit = SubmitField('Actualizar Perfil')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Este nombre de usuario ya está en uso. Por favor, elige otro.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Este correo electrónico ya está registrado. Por favor, usa otro correo.')

class RequestResetForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Restablecimiento de Contraseña')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No hay una cuenta asociada a este correo electrónico.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Restablecer Contraseña')

class PulzcardForm(FlaskForm):
    card_name = StringField('Nombre de Tarjeta', validators=[DataRequired()])
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    organization = StringField('Nombre Organización', validators=[DataRequired()])
    position = StringField('Cargo', validators=[DataRequired()])
    phone = StringField('Número Telefónico', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    website = StringField('Página Web', validators=[DataRequired(), URL()])
    address = StringField('Dirección', validators=[DataRequired()])
    submit = SubmitField('Crear Tarjeta')

class EditPulzcardForm(FlaskForm):
    card_name = StringField('Nombre de Tarjeta', validators=[DataRequired(), Length(max=100)])
    first_name = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Apellido', validators=[DataRequired(), Length(max=50)])
    organization = StringField('Nombre Organización', validators=[DataRequired(), Length(max=100)])
    position = StringField('Cargo', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Número Telefónico', validators=[DataRequired(), Length(max=20)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(), Length(max=120)])
    website = StringField('Página Web', validators=[DataRequired(), URL(), Length(max=200)])
    address = StringField('Dirección', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Actualizar Pulzcard')

class DeletePulzcardForm(FlaskForm):
    submit = SubmitField('Eliminar')

class OrderForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    dispositivo = StringField('Dispositivo', validators=[DataRequired()])
    mensaje = TextAreaField('¿Qué necesitas?', validators=[DataRequired()])
    logos = FileField('Subir Logos', validators=[Optional()])
    excel = FileField('Subir Archivo Excel', validators=[Optional()])
    submit = SubmitField('Enviar solicitud')

class ContactForm(FlaskForm):  # Nuevo formulario de contacto
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    mensaje = TextAreaField('Mensaje', validators=[DataRequired()])
    submit = SubmitField('Enviar')