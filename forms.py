# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, ValidationError
from models import User  # Importar desde models.py
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Correo Electrónico', validators=[
                        DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[
                             DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Crear Cuenta')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Este nombre de usuario ya está en uso. Por favor, elige otro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'Este correo electrónico ya está registrado. Por favor, inicia sesión o usa otro correo.')


class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[
                        DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')


class UpdateAccountForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Correo Electrónico', validators=[
                        DataRequired(), Email()])
    password = PasswordField('Nueva Contraseña', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirmar Nueva Contraseña',
                                     validators=[EqualTo('password')])
    submit = SubmitField('Actualizar Perfil')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'Este nombre de usuario ya está en uso. Por favor, elige otro.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'Este correo electrónico ya está registrado. Por favor, usa otro correo.')


class RequestResetForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[
                        DataRequired(), Email()])
    submit = SubmitField('Solicitar Restablecimiento de Contraseña')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                'No hay una cuenta asociada a este correo electrónico.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[
                             DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Restablecer Contraseña')


class PulzcardForm(FlaskForm):
    card_name = StringField('Nombre de Tarjeta', validators=[DataRequired()])
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    organization = StringField(
        'Nombre Organización', validators=[DataRequired()])
    position = StringField('Cargo', validators=[DataRequired()])
    phone = StringField('Número Telefónico', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[
                        DataRequired(), Email()])
    website = StringField('Página Web', validators=[DataRequired(), URL()])
    address = StringField('Dirección', validators=[DataRequired()])
    submit = SubmitField('Crear Tarjeta')
