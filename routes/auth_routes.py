# routes/auth_routes.py

from flask import (
    Blueprint, render_template, request, flash, redirect, url_for
)
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from flask_mail import Message

# Importa extensiones y modelos que necesites 
# (puedes importarlos de 'extensions.py' y 'models.py')
from extensions import db, bcrypt, mail
from models import User

# Importa los formularios de autenticación 
# (RegistrationForm, LoginForm, etc.) desde tu forms.py
from forms import (
    RegistrationForm, LoginForm, ResetPasswordForm, 
    RequestResetForm, UpdateAccountForm
    # y los que ocupes para la cuenta
)

# Creamos el Blueprint. Aquí lo llamamos 'main_bp',
# tal como tú indicas que lo vas a importar en app.py
main_bp = Blueprint('main', __name__)

# ============== Rutas de Autenticación ============= #

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Ya estás logueado.', 'info')
        return redirect(url_for('home'))  # Ajustar destino si tu home está en otro blueprint
    form = RegistrationForm()
    if form.validate_on_submit():
        # Crear el usuario sin contraseña
        user = User(username=form.username.data, email=form.email.data,
                    is_admin=False, must_change_password=True)
        db.session.add(user)
        db.session.commit()

        # Generar token de reseteo
        token = user.get_reset_token()

        # Enviar correo con enlace
        try:
            msg = Message(
                'Configura tu Contraseña en PulztagWeb',
                recipients=[user.email]
            )
            reset_url = url_for('main.reset_token', token=token, _external=True)
            msg.body = f'''Hola {user.username},

Gracias por registrarte en PulztagWeb. Por favor, haz clic en el siguiente enlace para establecer tu contraseña:

{reset_url}

Si no solicitaste este registro, por favor ignora este correo.

Saludos,
Equipo de PulztagWeb
'''
            mail.send(msg)
            flash('Cuenta creada. Revisa tu correo para establecer tu contraseña.', 'success')
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            flash('Hubo un error al enviar el correo. Por favor, contacta al soporte.', 'danger')

        return redirect(url_for('main.login'))
    return render_template('register.html', title='Registrar', form=form)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Ya estás logueado.', 'info')
        return redirect(url_for('profile') + '#miPerfilSection')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if user.must_change_password:
                flash('Por favor, establece una nueva contraseña.', 'warning')
                return redirect(url_for('main.change_password'))
            flash('Has iniciado sesión correctamente.', 'success')
            return redirect(url_for('profile') + '#miPerfilSection')
        else:
            flash('Inicio de sesión fallido. Revisa el correo y la contraseña.', 'danger')
    return render_template('login.html', title='Iniciar Sesión', form=form)


@main_bp.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('home'))  # Ajustar según dónde esté tu ruta home


@main_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        current_user.must_change_password = False
        db.session.commit()
        flash('Tu contraseña ha sido actualizada.', 'success')
        return redirect(url_for('home'))
    return render_template('change_password.html', title='Cambiar Contraseña', form=form)


@main_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if not bcrypt.check_password_hash(current_user.password, form.current_password.data):
            flash('La contraseña actual es incorrecta.', 'danger')
            form.username.data = current_user.username
            return render_template('account.html', title='Perfil de Usuario', form=form)
        
        current_user.username = form.username.data
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password

        db.session.commit()
        flash('Tu cuenta ha sido actualizada.', 'success')
        return redirect(url_for('profile') + '#miPerfilSection')
    else:
        form.username.data = current_user.username

    return render_template('account.html', title='Perfil de Usuario', form=form, email=current_user.email)


@main_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        flash('Ya estás logueado.', 'info')
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_token()
            msg = Message('Recupera tu Contraseña', recipients=[user.email])
            reset_url = url_for('main.reset_token', token=token, _external=True)
            msg.body = f'''Para restablecer tu contraseña, visita el siguiente enlace:
{reset_url}

Si no solicitaste un restablecimiento de contraseña, ignora este mensaje.
'''
            mail.send(msg)
            flash('Se ha enviado un correo para restablecer tu contraseña.', 'info')
            return redirect(url_for('main.login'))
    return render_template('reset_request.html', title='Recuperar Contraseña', form=form)


@main_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        flash('Ya estás logueado.', 'info')
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('El token es inválido o ha expirado.', 'warning')
        return redirect(url_for('main.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        user.must_change_password = False
        db.session.commit()
        flash('Tu contraseña ha sido actualizada. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_token.html', title='Establecer Contraseña', form=form, token=token)