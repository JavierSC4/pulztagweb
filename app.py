# app.py

import os
import uuid
from urllib.parse import urlparse
import qrcode
from io import BytesIO
import base64
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, send_file, abort
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from random import randint
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import pandas as pd
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from extensions import mail, db, migrate, bcrypt, login_manager, oauth
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import User, Pulzcard, Tag, SecureModelView
from forms import (
    RegistrationForm, LoginForm, UpdateAccountForm,
    RequestResetForm, ResetPasswordForm,
    PulzcardForm, EditPulzcardForm, DeletePulzcardForm,
    ContactForm, OrderForm, TagForm, EditTagForm, DeleteTagForm, VerificationForm  # Importa el nuevo formulario de contacto
)
from flask_login import login_required, current_user, login_user, logout_user
from datetime import datetime

load_dotenv()

app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.getenv('SECRET_KEY', 'test_secret_key')

# Configuración de la Base de Datos
db_path = os.path.join(app.instance_path, 'site_new.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
login_manager.init_app(app)
oauth.init_app(app)  # Inicializar `oauth` con la instancia de `app`
mail.init_app(app)

# Registrar el cliente de Google OAuth
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',  # Cambiado para mayor claridad
    client_kwargs={'scope': 'openid email profile'},
)

# Inicializar Flask-Admin
admin = Admin(app, name='Panel de Administración', template_mode='bootstrap4')

# Agregar vistas con la clase SecureModelView al panel de administración
admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(Pulzcard, db.session))
admin.add_view(SecureModelView(Tag, db.session))

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail.init_app(app)  # Initialize the existing Mail instance with the app

# Inicializar CSRFProtect
csrf = CSRFProtect(app)

# Configuración de Flask-Login
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

def send_verification_email(user):
    verification_code = str(randint(100000, 999999))  # Genera un código de 6 dígitos
    user.verification_code = verification_code
    db.session.commit()

    msg = Message('Código de verificación', recipients=[user.email])
    msg.body = f'Tu código de verificación es: {verification_code}'
    mail.send(msg)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Directorio para guardar las vCards
VCARD_FOLDER = os.path.join(app.instance_path, 'vcards')
os.makedirs(VCARD_FOLDER, exist_ok=True)

# Directorio para guardar las subidas
UPLOAD_FOLDER = os.path.join(app.instance_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensiones permitidas (si las usas)
ALLOWED_LOGO_EXTENSIONS = {'png', 'jpeg', 'jpg'}
ALLOWED_EXCEL_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Configurar el serializador
s = URLSafeTimedSerializer(app.secret_key)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    form = VerificationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verification_code == form.code.data:
            user.is_verified = True
            user.verification_code = None  # Limpia el código
            db.session.commit()
            flash('Cuenta creada. Revisa tu correo para establecer tu contraseña.', 'success')
            return render_template('login.html', title='Iniciar Sesión', form=LoginForm())
        else:
            flash('Código de verificación incorrecto.', 'danger')
    return render_template('verify.html', form=form)

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/authorize/google')
def google_authorize():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('userinfo').json()

    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(
            username=user_info['name'],
            email=user_info['email'],
            is_verified=True  # Marcar automáticamente como verificado
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash('Inicio de sesión exitoso con Google.', 'success')
    return redirect(url_for('home'))

# Rutas de Autenticación
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Ya estás logueado.', 'info')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Crear el usuario sin contraseña
        user = User(username=form.username.data, email=form.email.data, is_admin=False, must_change_password=True)
        db.session.add(user)
        db.session.commit()

        # Generar token
        token = user.get_reset_token()

        # Enviar correo con enlace
        try:
            msg = Message(
                'Configura tu Contraseña en PulztagWeb',
                recipients=[user.email]
            )
            reset_url = url_for('reset_token', token=token, _external=True)
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

        return redirect(url_for('login'))
    return render_template('register.html', title='Registrar', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Ya estás logueado.', 'info')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if user.must_change_password:
                flash('Por favor, establece una nueva contraseña.', 'warning')
                return redirect(url_for('change_password'))
            flash('Has iniciado sesión correctamente.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Inicio de sesión fallido. Revisa el correo y la contraseña.', 'danger')
    return render_template('login.html', title='Iniciar Sesión', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
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

@app.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('home'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
        db.session.commit()
        flash('Tu cuenta ha sido actualizada.', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Perfil de Usuario', form=form)

@app.route('/reset_password', methods=['GET', 'POST'])
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
            reset_url = url_for('reset_token', token=token, _external=True)
            msg.body = f'''Para restablecer tu contraseña, visita el siguiente enlace:
{reset_url}

Si no solicitaste un restablecimiento de contraseña, por favor ignora este mensaje.
'''
            mail.send(msg)
            flash('Se ha enviado un correo para restablecer tu contraseña.', 'info')
            return redirect(url_for('login'))
    return render_template('reset_request.html', title='Recuperar Contraseña', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        flash('Ya estás logueado.', 'info')
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('El token es inválido o ha expirado.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        user.must_change_password = False
        db.session.commit()
        flash('Tu contraseña ha sido actualizada. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Establecer Contraseña', form=form, token=token)

# Rutas Existentes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()  # Crear una instancia del formulario
    
    # Verificar si hay un mensaje predefinido en los parámetros de la URL
    prefilled_message = request.args.get('message')
    if prefilled_message and not form.mensaje.data:
        form.mensaje.data = prefilled_message  # Prellenar el campo "Mensaje" si está disponible
    
    if form.validate_on_submit():  # Usar validate_on_submit para verificar el envío
        nombre = form.nombre.data
        email = form.email.data
        mensaje = form.mensaje.data

        try:
            msg = Message(
                subject=f"Nuevo mensaje de {nombre}",
                recipients=['contacto@pulztag.com'],
                body=f"Nombre: {nombre}\nCorreo Electrónico: {email}\n\nMensaje:\n{mensaje}"
            )
            mail.send(msg)
            flash('¡Tu mensaje ha sido enviado exitosamente!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            print(e)
            flash('Hubo un error al enviar tu mensaje. Por favor, inténtalo de nuevo más tarde.', 'danger')
            return redirect(url_for('contact'))

    return render_template('contact.html', form=form)  # Pasar el formulario al template

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    form = OrderForm()  # Crear una instancia del formulario
    if form.validate_on_submit():
        # Procesa el pedido
        nombre = form.nombre.data
        email = form.email.data
        dispositivo = form.dispositivo.data
        mensaje = form.mensaje.data

        # Validaciones básicas
        if not nombre or not email or not dispositivo or not mensaje:
            flash('Por favor, completa todos los campos.', 'danger')
            return redirect(url_for('order'))

        # Manejar los logos
        logos = request.files.getlist('logos')
        valid_logos = [logo for logo in logos if logo.filename != '']
        if len(valid_logos) > 10:
            flash('Puedes subir un máximo de 10 logos.', 'danger')
            return redirect(url_for('order'))

        saved_logos = []
        for logo in valid_logos:
            filename = logo.filename.strip()
            if allowed_file(filename, ALLOWED_LOGO_EXTENSIONS):
                try:
                    secure_name = secure_filename(filename)
                    unique_filename = f"{uuid.uuid4().hex}_{secure_name}"
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    logo.save(logo_path)
                    saved_logos.append((filename, logo_path))
                    print(f"Logo guardado: {logo_path}")
                except Exception as e:
                    print(f"Error al guardar el logo {filename}: {e}")
                    flash(f"Hubo un error al guardar el logo {filename}.", 'danger')
                    return redirect(url_for('order'))
            else:
                flash(f"Formato de logo no permitido: {filename}", 'danger')
                return redirect(url_for('order'))

        # Manejar el archivo Excel
        excel = request.files.get('excel')
        if excel and excel.filename != '':
            filename = excel.filename.strip()
            if allowed_file(filename, ALLOWED_EXCEL_EXTENSIONS):
                try:
                    secure_name = secure_filename(filename)
                    unique_filename = f"{uuid.uuid4().hex}_{secure_name}"
                    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    excel.save(excel_path)
                    print(f"Archivo Excel guardado: {excel_path}")
                except Exception as e:
                    print(f"Error al guardar el archivo Excel {filename}: {e}")
                    flash(f"Hubo un error al guardar el archivo Excel {filename}.", 'danger')
                    return redirect(url_for('order'))
            else:
                flash('Formato de archivo Excel no permitido.', 'danger')
                return redirect(url_for('order'))
        else:
            excel_path = None

        # Crear un DataFrame con los datos del pedido
        data = {
            'Nombre': [nombre],
            'Correo Electrónico': [email],
            'Selección de Dispositivo': [dispositivo],
            'Mensaje': [mensaje]
        }
        df = pd.DataFrame(data)

        # Guardar el DataFrame en un archivo Excel
        pedido_excel_path = os.path.join(app.config['UPLOAD_FOLDER'], f"pedido_{uuid.uuid4().hex}.xlsx")
        df.to_excel(pedido_excel_path, index=False)
        print(f"Pedido guardado en: {pedido_excel_path}")

        # Enviar el correo con los archivos adjuntos
        try:
            msg = Message(
                subject="Nuevo Pedido de PulztagWeb",
                recipients=['contacto@pulztag.com']
            )
            msg.body = f"Nombre: {nombre}\nCorreo Electrónico: {email}\nSelección de Dispositivo: {dispositivo}\n\nMensaje:\n{mensaje}"

            # Adjuntar el archivo Excel del pedido
            with open(pedido_excel_path, 'rb') as fp:
                msg.attach(
                    "pedido.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    fp.read()
                )

            # Adjuntar los logos
            for original_filename, logo_path in saved_logos:
                try:
                    print(f"Adjuntando logo: {original_filename} desde {logo_path}")
                    with open(logo_path, 'rb') as fp:
                        # Determinar el MIME type correcto
                        ext = original_filename.rsplit('.', 1)[1].lower()
                        mime_type = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
                        msg.attach(
                            original_filename,
                            mime_type,
                            fp.read()
                        )
                except Exception as e:
                    print(f"Error adjuntando el logo {original_filename}: {e}")

            # Adjuntar el archivo Excel si existe
            if excel_path:
                with open(excel_path, 'rb') as fp:
                    msg.attach(
                        os.path.basename(excel_path),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        fp.read()
                    )

            mail.send(msg)
            print("Correo enviado exitosamente.")

            # Eliminar archivos temporales
            os.remove(pedido_excel_path)
            for _, logo_path in saved_logos:
                os.remove(logo_path)
            if excel_path:
                os.remove(excel_path)
            print("Archivos temporales eliminados.")

            flash('Su solicitud fue enviada exitosamente. ¡Pronto nos pondremos en contacto contigo!', 'success')
            return redirect(url_for('order'))

        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            flash('Hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.', 'danger')
            return redirect(url_for('order'))

    return render_template('order.html', form=form)  # Pasar el formulario al template

@app.route('/create_item')
def create_item():
    return render_template('create_item.html')

# Rutas de Pulzcard
@app.route('/pulzcard', methods=['GET', 'POST'])
@login_required
def pulzcard():
    form = PulzcardForm()
    if form.validate_on_submit():
        # Handle the image file if provided
        if form.image_file.data:
            # Save the uploaded image file
            image_file = form.image_file.data
            filename = secure_filename(image_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            image_file.save(image_path)
            print(f"Image saved at: {image_path}")
        else:
            unique_filename = 'default.jpg'

        # Crear la Pulzcard con el campo de plantilla
        pulzcard = Pulzcard(
            card_name=form.card_name.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            organization=form.organization.data,
            position=form.position.data,
            phone=form.phone.data,
            email=form.email.data,
            website=form.website.data,
            address=form.address.data,
            image_file=unique_filename,
            user_id=current_user.id,
            template=form.template.data  # Añadir esta línea
        )

        # Añadir a la sesión y hacer flush para obtener card_id
        db.session.add(pulzcard)
        try:
            db.session.flush()  # Asigna card_id sin commit
            print(f"Pulzcard creada con card_id: {pulzcard.card_id}")
        except Exception as e:
            db.session.rollback()
            print(f"Error al hacer flush de Pulzcard: {e}")
            flash('Hubo un error al crear tu Pulzcard. Por favor, inténtalo de nuevo.', 'danger')
            return redirect(url_for('pulzcard'))

        # Crear y guardar la vCard
        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{pulzcard.first_name} {pulzcard.last_name}
ORG:{pulzcard.organization}
TITLE:{pulzcard.position}
TEL;TYPE=WORK,VOICE:{pulzcard.phone}
EMAIL:{pulzcard.email}
URL:{pulzcard.website}
ADR;TYPE=WORK:;;{pulzcard.address}
END:VCARD"""
        vcard_path = os.path.join(VCARD_FOLDER, f'{pulzcard.card_id}.vcf')
        print(f"Intentando guardar vCard en: {vcard_path}")

        try:
            with open(vcard_path, 'w') as f:
                f.write(vcard)
            print(f"vCard guardada exitosamente en: {vcard_path}")
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar la vCard: {e}")
            flash('Hubo un error al guardar la Pulzcard.', 'danger')
            return redirect(url_for('pulzcard'))

        # Commit de la Pulzcard y finalización
        try:
            db.session.commit()
            print("Pulzcard añadida a la base de datos correctamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear Pulzcard en la base de datos: {e}")
            flash('Hubo un error al crear tu Pulzcard. Por favor, inténtalo de nuevo.', 'danger')
            return redirect(url_for('pulzcard'))

        # Redirigir usando card_id en lugar de id
        return redirect(url_for('pulzcard_card', card_id=pulzcard.card_id))
    else:
        print("Formulario no validado. Errores:", form.errors)
    
    return render_template('pulzcard/index.html', form=form)
@app.route('/pulzcard/card/<card_id>')
def pulzcard_card(card_id):
    pulzcard = Pulzcard.query.filter_by(card_id=card_id).first()
    if not pulzcard:
        flash('Tarjeta no encontrada.', 'danger')
        return redirect(url_for('home'))
    
    # Obtener el template desde los parámetros de la URL
    selected_template = request.args.get('template')
    valid_templates = ['template1', 'template2', 'template3']  # Añade todos tus templates aquí

    # Validar el template seleccionado
    if selected_template and selected_template in valid_templates:
        template_name = f"pulzcard/{selected_template}.html"
    else:
        # Usar el template predeterminado de la Pulzcard o 'template1' si no está definido
        template_name = f"pulzcard/{pulzcard.template if pulzcard.template in valid_templates else 'template1'}.html"
    
    contact_info = {
        "full_name": f"{pulzcard.first_name} {pulzcard.last_name}",
        "organization": pulzcard.organization,
        "position": pulzcard.position,
        "phone": pulzcard.phone,
        "email": pulzcard.email,
        "website": pulzcard.website,
        "address": pulzcard.address,
        "image_file": pulzcard.image_file
    }

    return render_template(template_name, contact=contact_info, card_id=card_id)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/pulzcard/vcards/<filename>')
def pulzcard_download_vcard(filename):
    # Opcional: Validar que el archivo existe y pertenece a una Pulzcard existente
    file_path = os.path.join(VCARD_FOLDER, filename)
    if not os.path.exists(file_path):
        flash('Archivo no encontrado.', 'danger')
        return redirect(url_for('home'))
    return send_from_directory(VCARD_FOLDER, filename, as_attachment=True)

# Nueva Ruta: Perfil de Usuario
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    pulzcards = Pulzcard.query.filter_by(user_id=current_user.id).order_by(Pulzcard.created_at.desc()).all()
    tags = Tag.query.filter_by(user_id=current_user.id).order_by(Tag.created_at.desc()).all()
    tag_form = TagForm()

    # Initialize delete forms for each Pulzcard and Tag
    delete_forms = {card.id: DeletePulzcardForm(prefix=str(card.card_id)) for card in pulzcards}
    delete_tag_forms = {tag.id: DeleteTagForm(prefix=str(tag.tag_id)) for tag in tags}

    if tag_form.validate_on_submit():
        new_tag = Tag(
            tag_name=tag_form.tag_name.data,
            redirect_url=tag_form.redirect_url.data,
            user_id=current_user.id
        )
        db.session.add(new_tag)
        db.session.commit()
        flash('Tu etiqueta ha sido creada exitosamente.', 'success')
        return redirect(url_for('profile'))

    return render_template(
        'profile.html', 
        title='Perfil de Usuario', 
        pulzcards=pulzcards, 
        tags=tags, 
        tag_form=tag_form, 
        delete_forms=delete_forms,  # Pulzcard delete forms
        delete_tag_forms=delete_tag_forms  # Tag delete forms
    )

@app.route('/r/<tag_id>')
def redirect_tag(tag_id):
    # Busca la etiqueta usando tag_id en lugar de id
    tag = Tag.query.filter_by(tag_id=tag_id).first()
    if tag:
        return redirect(tag.redirect_url)
    else:
        flash('La etiqueta no existe o fue eliminada.', 'danger')
        return redirect(url_for('profile'))

@app.route('/tag/delete/<tag_id>', methods=['POST'])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()

    form = DeleteTagForm()
    if form.validate_on_submit():
        try:
            db.session.delete(tag)
            db.session.commit()
            flash('Etiqueta eliminada exitosamente.', 'success')
        except Exception as e:
            print(f"Error al eliminar etiqueta: {e}")
            flash('Hubo un error al eliminar la etiqueta. Por favor, intenta de nuevo.', 'danger')
    else:
        flash('Formulario inválido o token CSRF no válido.', 'danger')

    return redirect(url_for('profile'))

# Nueva Ruta: Editar Pulzcard
@app.route('/pulzcard/edit/<card_id>', methods=['GET', 'POST'])
@login_required
def edit_pulzcard(card_id):
    pulzcard = Pulzcard.query.filter_by(card_id=card_id, user_id=current_user.id).first_or_404()
    form = EditPulzcardForm()

    if form.validate_on_submit():
        pulzcard.card_name = form.card_name.data
        pulzcard.first_name = form.first_name.data
        pulzcard.last_name = form.last_name.data
        pulzcard.organization = form.organization.data
        pulzcard.position = form.position.data
        pulzcard.phone = form.phone.data
        pulzcard.email = form.email.data
        pulzcard.website = form.website.data
        pulzcard.address = form.address.data
        pulzcard.template = form.template.data

        # Procesar la imagen de perfil si se ha subido una nueva
        if form.image_file.data:
            # Guardar la nueva imagen
            image_file = form.image_file.data
            filename = secure_filename(image_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            image_file.save(image_path)
            
            # Actualizar el campo image_file en la base de datos
            pulzcard.image_file = unique_filename

        db.session.commit()

        # Actualizar la vCard en el sistema de archivos
        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{pulzcard.first_name} {pulzcard.last_name}
ORG:{pulzcard.organization}
TITLE:{pulzcard.position}
TEL;TYPE=WORK,VOICE:{pulzcard.phone}
EMAIL:{pulzcard.email}
URL:{pulzcard.website}
ADR;TYPE=WORK:;;{pulzcard.address}
END:VCARD"""
        vcard_path = os.path.join(VCARD_FOLDER, f'{pulzcard.card_id}.vcf')
        with open(vcard_path, 'w') as f:
            f.write(vcard)

        flash('Pulzcard actualizada exitosamente.', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.card_name.data = pulzcard.card_name
        form.first_name.data = pulzcard.first_name
        form.last_name.data = pulzcard.last_name
        form.organization.data = pulzcard.organization
        form.position.data = pulzcard.position
        form.phone.data = pulzcard.phone
        form.email.data = pulzcard.email
        form.website.data = pulzcard.website
        form.address.data = pulzcard.address
        form.template.data = pulzcard.template

    return render_template('edit_pulzcard.html', title='Editar Pulzcard', form=form, pulzcard=pulzcard)

# Nueva Ruta: Eliminar Pulzcard
@app.route('/pulzcard/delete/<card_id>', methods=['POST'])
@login_required
def delete_pulzcard(card_id):
    pulzcard = Pulzcard.query.filter_by(card_id=card_id, user_id=current_user.id).first_or_404()

    form = DeletePulzcardForm()
    if form.validate_on_submit():
        try:
            # Eliminar la vCard del sistema de archivos
            vcard_path = os.path.join(VCARD_FOLDER, f'{pulzcard.card_id}.vcf')
            if os.path.exists(vcard_path):
                os.remove(vcard_path)

            # Eliminar la Pulzcard de la base de datos
            db.session.delete(pulzcard)
            db.session.commit()
            flash('Pulzcard eliminada exitosamente.', 'success')
        except Exception as e:
            print(f"Error al eliminar Pulzcard: {e}")
            flash('Hubo un error al eliminar la Pulzcard. Por favor, intenta de nuevo.', 'danger')
    else:
        flash('Formulario inválido o token CSRF no válido.', 'danger')

    return redirect(url_for('profile'))

@app.route('/create_tag', methods=['GET', 'POST'])
@login_required
def create_tag():
    form = TagForm()
    if form.validate_on_submit():
        new_tag = Tag(
            tag_name=form.tag_name.data,
            redirect_url=form.redirect_url.data,
            user_id=current_user.id
        )
        db.session.add(new_tag)
        db.session.commit()
        flash('Tu etiqueta ha sido creada exitosamente.', 'success')
        return redirect(url_for('profile'))
    return render_template('create_tag.html', title='Crear Etiqueta', form=form)

@app.route('/tag/edit/<tag_id>', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
    tag = Tag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()
    form = EditTagForm()

    if form.validate_on_submit():
        tag.tag_name = form.tag_name.data
        tag.redirect_url = form.redirect_url.data
        db.session.commit()
        flash('Etiqueta actualizada exitosamente.', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.tag_name.data = tag.tag_name
        form.redirect_url.data = tag.redirect_url

    return render_template('edit_tag.html', title='Editar Etiqueta', form=form, tag=tag)

@app.route('/tag/qrcode_image/<tag_id>')
@login_required
def tag_qrcode_image(tag_id):
    tag = Tag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()
    url = url_for('redirect_tag', tag_id=tag.tag_id, _external=True)
    # Generar el código QR
    qr_img = qrcode.make(url)
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/tag/qrcode/<tag_id>')
@login_required
def tag_qrcode(tag_id):
    tag = Tag.query.filter_by(tag_id=tag_id, user_id=current_user.id).first_or_404()
    qr_image_url = url_for('tag_qrcode_image', tag_id=tag.tag_id)
    return render_template('qrcode_card.html', qr_url=qr_image_url, entity_type='Etiqueta', tag_id=tag_id)

@app.route('/pulzcard/qrcode_image/<card_id>')
@login_required
def pulzcard_qrcode_image(card_id):
    pulzcard = Pulzcard.query.filter_by(card_id=card_id, user_id=current_user.id).first_or_404()
    url = url_for('pulzcard_card', card_id=pulzcard.card_id, _external=True)
    # Generar el código QR
    qr_img = qrcode.make(url)
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/pulzcard/qrcode/<card_id>')
@login_required
def pulzcard_qrcode(card_id):
    pulzcard = Pulzcard.query.filter_by(card_id=card_id, user_id=current_user.id).first_or_404()
    qr_image_url = url_for('pulzcard_qrcode_image', card_id=pulzcard.card_id)
    return render_template('qrcode_card.html', qr_url=qr_image_url, entity_type='Pulzcard', tag_id=card_id)

@app.route('/test_video')
def test_video():
    return render_template('test_video.html')

# Ruta de Prueba para Crear una vCard Manualmente
@app.route('/test_vcard')
def test_vcard():
    test_vcard_content = """BEGIN:VCARD
VERSION:3.0
FN:Prueba Nombre
ORG:Prueba Organización
TITLE:Prueba Cargo
TEL;TYPE=WORK,VOICE:123456789
EMAIL:prueba@example.com
URL:https://www.prueba.com
ADR;TYPE=WORK:;;Calle Falsa 123
END:VCARD"""

    test_vcard_path = os.path.join(VCARD_FOLDER, 'test.vcf')
    try:
        with open(test_vcard_path, 'w') as f:
            f.write(test_vcard_content)
        return "Archivo de prueba vCard creado exitosamente."
    except Exception as e:
        return f"Error al crear el archivo de prueba vCard: {e}"

# Crear las tablas de la base de datos
with app.app_context():
    db.create_all()  # Asegura que la base de datos y las tablas se creen

#with app.app_context():
#    try:
#        result = User.query.first()  # Consulta básica para probar la conexión
#        print("Conexión exitosa. Primer usuario encontrado:", result)
#    except Exception as e:
#        print("Error al conectar con la base de datos:", e)

if __name__ == '__main__':
    app.run(debug=True)