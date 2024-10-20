# app.py

import os
import uuid
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, abort
from flask_mail import Mail, Message
from dotenv import load_dotenv
import pandas as pd
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from extensions import db, migrate, bcrypt, login_manager
from models import User, Pulzcard
from forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, PulzcardForm, EditPulzcardForm

from flask_login import login_required, current_user, login_user, logout_user

from datetime import datetime

load_dotenv()

app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.getenv('SECRET_KEY', 'test_secret_key')

# Crear el directorio 'instance' si no existe
instance_dir = os.path.join(app.instance_path)
os.makedirs(instance_dir, exist_ok=True)

# Configuración de la Base de Datos
db_path = os.path.join(instance_dir, 'site.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
login_manager.init_app(app)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

# Configuración de Flask-Login
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configuración para Tokens
s = URLSafeTimedSerializer(app.secret_key)

# Directorio para guardar las subidas
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Directorio para guardar las vCards
VCARD_FOLDER = os.path.join(app.root_path, 'vcards')
os.makedirs(VCARD_FOLDER, exist_ok=True)

# Extensiones permitidas
ALLOWED_LOGO_EXTENSIONS = {'png', 'jpeg', 'jpg'}
ALLOWED_EXCEL_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Rutas de Autenticación
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Ya estás logueado.', 'info')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Tu cuenta ha sido creada! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registrar', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Ya estás logueado.', 'info')
        return redirect(url_for('home'))
    form = LoginForm()
    next_page = request.args.get('next')
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Has iniciado sesión correctamente.', 'success')
            # Obtener 'next' del formulario si no está en los argumentos
            if not next_page:
                next_page = request.form.get('next')
            # Verificación de seguridad para 'next'
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
        else:
            flash('Inicio de sesión fallido. Revisa el correo y la contraseña.', 'danger')
    return render_template('login.html', title='Iniciar Sesión', form=form)

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
        db.session.commit()
        flash('Tu contraseña ha sido actualizada. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Restablecer Contraseña', form=form)

# Rutas Existentes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        mensaje = request.form.get('mensaje')

        if not nombre or not email or not mensaje:
            flash('Por favor, completa todos los campos.', 'danger')
            return redirect(url_for('contact'))

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

    return render_template('contact.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        dispositivo = request.form.get('dispositivo')
        mensaje = request.form.get('mensaje')

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

    return render_template('order.html')

@app.route('/pulzcard', methods=['GET', 'POST'])
@login_required
def pulzcard():
    form = PulzcardForm()
    if form.validate_on_submit():
        print("Formulario validado exitosamente.")
        # Generar un ID único para la tarjeta
        card_id = str(uuid.uuid4())

        # Crear una vCard
        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{form.first_name.data} {form.last_name.data}
ORG:{form.organization.data}
TITLE:{form.position.data}
TEL;TYPE=WORK,VOICE:{form.phone.data}
EMAIL:{form.email.data}
URL:{form.website.data}
ADR;TYPE=WORK:;;{form.address.data}
END:VCARD"""

        # Guardar la vCard en un archivo
        vcard_path = os.path.join(VCARD_FOLDER, f'{card_id}.vcf')
        with open(vcard_path, 'w') as f:
            f.write(vcard)

        # Redirigir a la página de la tarjeta
        return redirect(url_for('pulzcard_card', card_id=card_id))
    else:
        print("Formulario no validado. Errores:", form.errors)
    return render_template('pulzcard/index.html', form=form)

@app.route('/pulzcard/card/<card_id>')
def pulzcard_card(card_id):
    # Leer la vCard
    vcard_path = os.path.join(VCARD_FOLDER, f'{card_id}.vcf')
    if not os.path.exists(vcard_path):
        flash('Tarjeta no encontrada.', 'danger')
        return redirect(url_for('pulzcard'))

    with open(vcard_path, 'r') as f:
        vcard = f.read()

    # Extraer información para la página personalizada
    contact_info = {}
    for line in vcard.split('\n'):
        if line.startswith('FN:'):
            contact_info['full_name'] = line.replace('FN:', '')
        elif line.startswith('ORG:'):
            contact_info['organization'] = line.replace('ORG:', '')
        elif line.startswith('TITLE:'):
            contact_info['position'] = line.replace('TITLE:', '')
        elif line.startswith('TEL'):
            contact_info['phone'] = line.split(':')[1]
        elif line.startswith('EMAIL:'):
            contact_info['email'] = line.replace('EMAIL:', '')
        elif line.startswith('URL:'):
            contact_info['website'] = line.replace('URL:', '')
        elif line.startswith('ADR'):
            contact_info['address'] = line.split(':')[1]

    return render_template('pulzcard/card.html', contact=contact_info, card_id=card_id)

@app.route('/pulzcard/vcards/<filename>')
def pulzcard_download_vcard(filename):
    return send_from_directory(VCARD_FOLDER, filename, as_attachment=True)

# Nueva Ruta: Perfil de Usuario
@app.route('/profile')
@login_required
def profile():
    # Obtener todas las Pulzcards del usuario
    pulzcards = Pulzcard.query.filter_by(user_id=current_user.id).order_by(Pulzcard.created_at.desc()).all()
    return render_template('profile.html', title='Perfil de Usuario', pulzcards=pulzcards)

# Nueva Ruta: Editar Pulzcard
@app.route('/pulzcard/edit/<int:card_id>', methods=['GET', 'POST'])
@login_required
def edit_pulzcard(card_id):
    pulzcard = Pulzcard.query.get_or_404(card_id)
    if pulzcard.owner != current_user:
        abort(403)  # Acceso prohibido

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
        pulzcard.created_at = datetime.utcnow()  # Actualizar la fecha de modificación si es necesario
        db.session.commit()
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

    return render_template('edit_pulzcard.html', title='Editar Pulzcard', form=form, pulzcard=pulzcard)

# Nueva Ruta: Eliminar Pulzcard
@app.route('/pulzcard/delete/<int:card_id>', methods=['POST'])
@login_required
def delete_pulzcard(card_id):
    pulzcard = Pulzcard.query.get_or_404(card_id)
    if pulzcard.owner != current_user:
        abort(403)  # Acceso prohibido

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

    return redirect(url_for('profile'))

# Mover la inicialización de la base de datos fuera del bloque if __name__ == '__main__'
with app.app_context():
    db.create_all()  # Asegura que la base de datos y las tablas se creen

if __name__ == '__main__':
    app.run(debug=True)