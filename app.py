# app.py

# ============================================
# Importaciones estándar de la biblioteca
# ============================================

import os
import uuid
from io import BytesIO
from random import randint
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone

# ============================================
# Importaciones de terceros
# ============================================

from flask import (
    Flask, render_template, request, flash, redirect, url_for,
    send_from_directory, send_file, jsonify, make_response, abort
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exists
from sqlalchemy.orm import joinedload
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required, current_user, login_user, logout_user, LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import pandas as pd
import qrcode
from dotenv import load_dotenv
import logging

# ============================================
# Importaciones locales
# ============================================

from extensions import mail, db, migrate, bcrypt, login_manager, oauth
from models import User, Pulzcard, Tag, Bodega, Caja, Producto, SecureModelView, DashboardItem, SurveyResponse
from forms import (
    RegistrationForm, LoginForm, UpdateAccountForm,
    RequestResetForm, ResetPasswordForm,
    PulzcardForm, EditPulzcardForm, DeletePulzcardForm,
    ContactForm, OrderForm, TagForm, EditTagForm, DeleteTagForm,
    BodegaForm, EditBodegaForm, DeleteBodegaForm,
    CajaForm, EditCajaForm, DeleteCajaForm, ProductoForm, EditProductoForm, DeleteProductoForm,
    ImportTagsForm, BulkDeleteTagForm, DeleteDashboardItemForm,
    ImportPulzcardForm, BulkDeletePulzcardForm, DeleteCajaForm, DeleteProductoForm
)

# ============================================
# Configuración de la aplicación Flask
# ============================================

from routes.auth_routes import main_bp #importación de tu blueprint de autenticación

load_dotenv()  # Carga las variables de entorno desde el archivo .env es

app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.getenv('SECRET_KEY', 'test_secret_key')

# Configuración de la Base de Datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 1800,  # Recycle connections every 30 minutes
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
}

# Directorio para guardar las vCards
VCARD_FOLDER = os.path.join(app.instance_path, 'vcards')
os.makedirs(VCARD_FOLDER, exist_ok=True)

# Directorio para guardar las subidas
UPLOAD_FOLDER = os.path.join(app.instance_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensiones permitidas
ALLOWED_LOGO_EXTENSIONS = {'png', 'jpeg', 'jpg'}
ALLOWED_EXCEL_EXTENSIONS = {'xlsx', 'xls'}

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
login_manager.init_app(app)
oauth.init_app(app)  # Inicializar `oauth` con la instancia de `app`

# Inicializar CSRFProtect
csrf = CSRFProtect(app)

# Configuración de Flask-Login
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail.init_app(app)  # Inicializar mail después de configurar

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

app.register_blueprint(main_bp)

# Inicializar Flask-Admin
admin = Admin(app, name='Panel de Administración', template_mode='bootstrap4')

# Agregar vistas con la clase SecureModelView al panel de administración
admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(Pulzcard, db.session))
admin.add_view(SecureModelView(Tag, db.session))  # Asegúrate de incluir Tag
admin.add_view(SecureModelView(Bodega, db.session))
admin.add_view(SecureModelView(Caja, db.session))
admin.add_view(SecureModelView(Producto, db.session))  # Si deseas ver Productos en admin

# Configurar el serializador
s = URLSafeTimedSerializer(app.secret_key)

tag_fields = ['tag_name', 'redirect_url']

# ============================================
# Funciones auxiliares
# ============================================

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Función para generar el ID de Bodega
def generar_id_bodega():
    # Obtener la última bodega creada
    ultima_bodega = Bodega.query.order_by(Bodega.id.desc()).first()
    if ultima_bodega:
        ultimo_numero = int(ultima_bodega.id_bodega[3:])  # Asumiendo formato 'BOD001'
        nuevo_numero = ultimo_numero + 1
    else:
        nuevo_numero = 1  # Primera bodega

    # Generar el nuevo ID con prefijo y ceros a la izquierda
    nuevo_id = f"BOD{str(nuevo_numero).zfill(3)}"
    return nuevo_id


def generar_id_caja():
    # Obtener la última caja creada
    ultima_caja = Caja.query.order_by(Caja.id.desc()).first()
    if ultima_caja:
        ultimo_numero = int(ultima_caja.id_caja[3:])  # Asumiendo formato 'CAJ001'
        nuevo_numero = ultimo_numero + 1
    else:
        nuevo_numero = 1  # Primera caja

    # Generar el nuevo ID con prefijo y ceros a la izquierda
    nuevo_id = f"CAJ{str(nuevo_numero).zfill(3)}"
    return nuevo_id

def redirect_back(default='profile'):
    next_page = request.args.get('next')
    if next_page:
        return redirect(url_for(next_page))
    elif request.referrer:
        return redirect(request.referrer)
    else:
        return redirect(url_for(default))

# Rutas Existentes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    prefilled_message = request.args.get('message')
    if prefilled_message and not form.mensaje.data:
        form.mensaje.data = prefilled_message

    if form.validate_on_submit():
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

    return render_template('contact.html', form=form)


@app.route('/products')
def products():
    return render_template('products.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    form = OrderForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        email = form.email.data
        dispositivo = form.dispositivo.data
        mensaje = form.mensaje.data

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
                    if os.path.exists(logo_path):
                        saved_logos.append((filename, logo_path))
                        print(f"Logo guardado: {logo_path}")
                    else:
                        flash(f"Error al guardar el logo {filename}.", 'danger')
                        return redirect(url_for('order'))
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
                    if os.path.exists(excel_path):
                        print(f"Archivo Excel guardado: {excel_path}")
                    else:
                        flash(f"Error al guardar el archivo Excel {filename}.", 'danger')
                        return redirect(url_for('order'))
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
        try:
            df.to_excel(pedido_excel_path, index=False)
            if os.path.exists(pedido_excel_path):
                print(f"Pedido guardado en: {pedido_excel_path}")
            else:
                flash("Error al guardar los detalles del pedido.", 'danger')
                return redirect(url_for('order'))
        except Exception as e:
            print(f"Error al guardar el pedido en Excel: {e}")
            flash("Hubo un error al procesar los detalles del pedido.", 'danger')
            return redirect(url_for('order'))

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
                    with open(logo_path, 'rb') as fp:
                        ext = original_filename.rsplit('.', 1)[1].lower()
                        mime_type = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
                        msg.attach(
                            original_filename,
                            mime_type,
                            fp.read()
                        )
                        print(f"Adjuntado logo: {original_filename}")
                except Exception as e:
                    print(f"Error adjuntando el logo {original_filename}: {e}")
                    flash(f"Error adjuntando el logo {original_filename}.", 'danger')
                    return redirect(url_for('order'))

            # Adjuntar el archivo Excel si existe
            if excel_path:
                try:
                    with open(excel_path, 'rb') as fp:
                        msg.attach(
                            os.path.basename(excel_path),
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            fp.read()
                        )
                        print(f"Adjuntado archivo Excel: {excel_path}")
                except Exception as e:
                    print(f"Error adjuntando el archivo Excel {excel_path}: {e}")
                    flash(f"Error adjuntando el archivo Excel {excel_path}.", 'danger')
                    return redirect(url_for('order'))

            mail.send(msg)
            print("Correo enviado exitosamente.")

            # Eliminar archivos temporales
            try:
                os.remove(pedido_excel_path)
                for _, logo_path in saved_logos:
                    os.remove(logo_path)
                if excel_path:
                    os.remove(excel_path)
                print("Archivos temporales eliminados.")
            except Exception as e:
                print(f"Error al eliminar archivos temporales: {e}")

            flash('Su solicitud fue enviada exitosamente. ¡Pronto nos pondremos en contacto contigo!', 'success')
            return redirect(url_for('order'))

        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            flash('Hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.', 'danger')
            return redirect(url_for('order'))

    return render_template('order.html', form=form)


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
            template=form.template.data
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
        return redirect(url_for('main.home'))

    # Obtener el template desde los parámetros de la URL
    selected_template = request.args.get('template')
    valid_templates = ['template1', 'template2', 'template3']

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
        return redirect(url_for('main.home'))
    return send_from_directory(VCARD_FOLDER, filename, as_attachment=True)

# 1. Ruta para importar Pulzcards
@app.route('/import/pulzcards', methods=['POST'])
@login_required
def import_pulzcards():
    form = ImportPulzcardForm()
    if form.validate_on_submit():
        file = form.excelFile.data
        if file.filename == '':
            flash('No se ha seleccionado ningún archivo para Pulzcards.', 'danger')
            return redirect(url_for('profile') + '#pulzcardsSection')

        if allowed_file(file.filename, ALLOWED_EXCEL_EXTENSIONS):
            try:
                df = pd.read_excel(file)

                # Definir las columnas que esperas
                required_columns = [
                    'card_name', 'first_name', 'last_name', 
                    'organization', 'position', 'phone',
                    'email', 'website', 'address', 'template'
                ]
                # Verificar que existan
                if not all(col in df.columns for col in required_columns):
                    flash('El archivo Excel no contiene todas las columnas requeridas para Pulzcards.', 'danger')
                    return redirect(url_for('profile') + '#pulzcardsSection')

                # Insertar
                for _, row in df.iterrows():
                    new_pulz = Pulzcard(
                        card_name=row['card_name'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        organization=row['organization'],
                        position=row['position'],
                        phone=row['phone'],
                        email=row['email'],
                        website=row['website'],
                        address=row['address'],
                        template=row['template'] if 'template' in row and pd.notna(row['template']) else 'template1',
                        user_id=current_user.id
                    )
                    db.session.add(new_pulz)
                    db.session.flush()  # Para asignar card_id

                    # Crear la vCard en archivo .vcf (similar a como lo haces en /pulzcard)
                    vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{new_pulz.first_name} {new_pulz.last_name}
ORG:{new_pulz.organization}
TITLE:{new_pulz.position}
TEL;TYPE=WORK,VOICE:{new_pulz.phone}
EMAIL:{new_pulz.email}
URL:{new_pulz.website}
ADR;TYPE=WORK:;;{new_pulz.address}
END:VCARD"""
                    vcard_path = os.path.join(VCARD_FOLDER, f'{new_pulz.card_id}.vcf')
                    with open(vcard_path, 'w') as f:
                        f.write(vcard)

                db.session.commit()
                flash('Pulzcards importadas exitosamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al importar Pulzcards: {e}', 'danger')
        else:
            flash('Formato de archivo no permitido.', 'danger')
    else:
        # Errores del formulario
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {field}: {error}", 'danger')

    return redirect(url_for('profile') + '#pulzcardsSection')


# 2. Ruta para exportar Pulzcards seleccionadas
@app.route('/export_pulzcards', methods=['POST'])
@login_required
def export_pulzcards():
    data = request.get_json()
    pulz_ids = data.get('pulz_ids', [])
    if not pulz_ids:
        return jsonify({'error': 'No se seleccionaron Pulzcards para exportar.'}), 400

    # Buscar las pulzcards del user actual
    pulzcards = Pulzcard.query.filter(Pulzcard.card_id.in_(pulz_ids), Pulzcard.user_id == current_user.id).all()
    if not pulzcards:
        return jsonify({'error': 'Pulzcards no encontradas o no pertenecen al usuario.'}), 404

    # Crear DataFrame
    df = pd.DataFrame([{
        'card_name': p.card_name,
        'first_name': p.first_name,
        'last_name': p.last_name,
        'organization': p.organization,
        'position': p.position,
        'phone': p.phone,
        'email': p.email,
        'website': p.website,
        'address': p.address,
        'template': p.template,
        'fecha_creacion': p.created_at
    } for p in pulzcards])

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Pulzcards', index=False)
    writer.close()
    output.seek(0)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=pulzcards_export.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response


# 3. Borrado masivo de Pulzcards (opcional)
@app.route('/pulzcard/delete_bulk', methods=['POST'])
@login_required
def delete_bulk_pulzcards():
    form = BulkDeletePulzcardForm()
    if form.validate_on_submit():
        selected_pulzcards = request.form.getlist('selected_pulzcards')  # array con card_id
        if not selected_pulzcards:
            flash('No se seleccionaron Pulzcards para eliminar.', 'warning')
            return redirect(url_for('profile') + '#pulzcardsSection')

        try:
            pulzcards_to_delete = Pulzcard.query.filter(
                Pulzcard.card_id.in_(selected_pulzcards),
                Pulzcard.user_id == current_user.id
            ).all()

            for p in pulzcards_to_delete:
                # Eliminar vCard del sistema de archivos
                vcard_path = os.path.join(VCARD_FOLDER, f'{p.card_id}.vcf')
                if os.path.exists(vcard_path):
                    os.remove(vcard_path)
                db.session.delete(p)

            db.session.commit()
            flash(f'{len(pulzcards_to_delete)} Pulzcard(s) eliminada(s) exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al eliminar Pulzcards: {e}', 'danger')
    else:
        flash('Formulario inválido o token CSRF no válido.', 'danger')

    return redirect(url_for('profile') + '#pulzcardsSection')

# Ruta: Perfil de Usuario
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    global tag_fields  # Declarar que tag_fields es una variable global
    pulzcards = Pulzcard.query.filter_by(user_id=current_user.id).order_by(Pulzcard.created_at.desc()).all()
    import_pulzcards_form = ImportPulzcardForm() # Instancia de Importar Pulzcards
    bulk_delete_pulzcard_form = BulkDeletePulzcardForm() # Instancia de Borrado Masivo Pulzcards (opcional)
    tags = Tag.query.filter_by(user_id=current_user.id).order_by(Tag.created_at.desc()).all()
    bodegas = Bodega.query.filter_by(user_id=current_user.id).order_by(Bodega.fecha_creacion.desc()).all()
    tag_form = TagForm()
    bodega_form = BodegaForm()
    import_tags_form = ImportTagsForm()  # Instanciar el nuevo formulario

    # Inicializar formularios de eliminación
    delete_forms = {card.id: DeletePulzcardForm(prefix=str(card.card_id)) for card in pulzcards}
    delete_tag_forms = {tag.id: DeleteTagForm(prefix=str(tag.tag_id)) for tag in tags}
    delete_bodega_forms = {bodega.uuid: DeleteBodegaForm(prefix=str(bodega.uuid)) for bodega in bodegas}
    dashboard_items = DashboardItem.query.filter_by(user_id=current_user.id).all()
    print(f"Dashboard Items para el usuario {current_user.id}: {dashboard_items}")

    if tag_form.validate_on_submit() and tag_form.submit.data:
        new_tag = Tag(
            tag_name=tag_form.tag_name.data,
            redirect_url=tag_form.redirect_url.data,
            user_id=current_user.id
        )
        db.session.add(new_tag)
        db.session.commit()
        flash('Tu etiqueta ha sido creada exitosamente.', 'success')
        return redirect(url_for('profile') + '#miPerfilSection')

    if bodega_form.validate_on_submit() and bodega_form.submit.data:
        new_bodega = Bodega(
            nombre=bodega_form.nombre.data,
            ubicacion=bodega_form.ubicacion.data,
            notas=bodega_form.notas.data,
            user_id=current_user.id
        )
        new_bodega.id_bodega = generar_id_bodega()
        db.session.add(new_bodega)
        db.session.commit()
        flash('Tu bodega ha sido creada exitosamente.', 'success')
        return redirect(url_for('profile') + '#miPerfilSection')

    if import_tags_form.validate_on_submit() and import_tags_form.submit.data:
        return redirect(url_for('import_tags'))

    # Obtener el parámetro de sección de la URL
    section = request.args.get('section', 'miPerfilSection')  # Por defecto, mostrar 'miPerfilSection'

    bulk_delete_tag_form = BulkDeleteTagForm()  # Instancia del nuevo formulario

    return render_template(
        'profile.html',
        title='Perfil de Usuario',
        pulzcards=pulzcards,
        import_pulzcards_form=import_pulzcards_form,
        bulk_delete_pulzcard_form=bulk_delete_pulzcard_form,
        tags=tags,
        bodegas=bodegas,
        tag_form=tag_form,
        bodega_form=bodega_form,
        import_tags_form=import_tags_form,
        delete_forms=delete_forms,
        delete_tag_forms=delete_tag_forms,
        delete_bodega_forms=delete_bodega_forms,
        tag_fields=tag_fields,
        bulk_delete_tag_form=bulk_delete_tag_form,
        section=section,
        dashboard_items=dashboard_items,  # Añade esta línea
    )

@app.context_processor
def inject_tag_fields():
    return dict(tag_fields=tag_fields)

@app.route('/r/<tag_id>')
def redirect_tag(tag_id):
    tag = Tag.query.filter_by(tag_id=tag_id).first()
    if tag:
        tag.vistas += 1  # Incrementa el contador de vistas
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error al incrementar vistas para la etiqueta {tag_id}: {e}")
            flash('Hubo un error al procesar tu solicitud.', 'danger')
            return redirect(url_for('profile') + '#etiquetasSection')
        return redirect(tag.redirect_url)
    else:
        flash('La etiqueta no existe o fue eliminada.', 'danger')
        return redirect(url_for('profile') + '#etiquetasSection')


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
            db.session.rollback()
            print(f"Error al eliminar etiqueta: {e}")
            flash('Hubo un error al eliminar la etiqueta. Por favor, intenta de nuevo.', 'danger')
    else:
        flash('Formulario inválido o token CSRF no válido.', 'danger')

    return redirect(url_for('profile') + '#etiquetasSection')


@app.route('/tags/delete_bulk', methods=['POST'])
@login_required
def delete_bulk_tags():
    form = BulkDeleteTagForm()
    if form.validate_on_submit():
        selected_tags = request.form.getlist('selected_tags')  # Obtiene la lista de IDs seleccionados
        if not selected_tags:
            flash('No se seleccionaron etiquetas para eliminar.', 'warning')
            return redirect(url_for('profile') + '#etiquetasSection')
        try:
            # Filtra las etiquetas que pertenecen al usuario actual y están en la lista seleccionada
            tags_to_delete = Tag.query.filter(Tag.tag_id.in_(selected_tags), Tag.user_id == current_user.id).all()
            for tag in tags_to_delete:
                db.session.delete(tag)
            db.session.commit()
            flash(f'{len(tags_to_delete)} etiqueta(s) eliminada(s) exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar etiquetas: {e}")
            flash('Hubo un error al eliminar las etiquetas. Por favor, intenta de nuevo.', 'danger')
    else:
        flash('Formulario inválido o token CSRF no válido.', 'danger')
    return redirect(url_for('profile') + '#etiquetasSection')


@app.route('/import/tags', methods=['POST'])
@login_required
def import_tags():
    form = ImportTagsForm()
    if form.validate_on_submit():
        file = form.excelFile.data
        if file.filename == '':
            flash('No se ha seleccionado ningún archivo.', 'danger')
            return redirect(url_for('profile') + '#etiquetasSection')

        if allowed_file(file.filename, ALLOWED_EXCEL_EXTENSIONS):
            try:
                df = pd.read_excel(file)
                
                # Verificar columnas requeridas
                required_columns = ['tag_name', 'redirect_url']
                if not all(col in df.columns for col in required_columns):
                    flash('El archivo Excel no contiene todas las columnas requeridas.', 'danger')
                    return redirect(url_for('profile') + '#etiquetasSection')

                # Verificar número de columnas
                if len(df.columns) != len(required_columns):
                    flash('El número de columnas del archivo no coincide con las esperadas.', 'danger')
                    return redirect(url_for('profile') + '#etiquetasSection')

                # Crear etiquetas
                for _, row in df.iterrows():
                    new_tag = Tag(
                        tag_name=row['tag_name'],
                        redirect_url=row['redirect_url'],
                        user_id=current_user.id
                    )
                    db.session.add(new_tag)
                
                db.session.commit()
                flash(f'El archivo {file.filename} ha sido importado exitosamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Hubo un error al importar el archivo: {str(e)}', 'danger')
        else:
            flash('Formato de archivo no permitido.', 'danger')
    else:
        # Mostrar errores de CSRF u otros errores del formulario
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {field}: {error}", 'danger')

    return redirect(url_for('profile') + '#etiquetasSection')


@app.route('/export_tags', methods=['POST'])
@login_required
def export_tags():
    data = request.get_json()
    tag_ids = data.get('tag_ids', [])
    
    if not tag_ids:
        return jsonify({'error': 'No se seleccionaron etiquetas para exportar.'}), 400

    tags = Tag.query.filter(Tag.tag_id.in_(tag_ids), Tag.user_id == current_user.id).all()
    if not tags:
        return jsonify({'error': 'Etiquetas no encontradas o no tienes permisos para exportarlas.'}), 404

    # Crear un DataFrame con los datos básicos y enlaces al código QR
    df = pd.DataFrame([{
        'tag_name': tag.tag_name,
        'redirect_url': tag.redirect_url,
        'url_destino': url_for('redirect_tag', tag_id=tag.tag_id, _external=True),
        'qr_link': url_for('tag_qrcode_image', tag_id=tag.tag_id, _external=True),  # Agregar enlace al código QR
        'vistas': tag.vistas,
        'created_at': tag.created_at
    } for tag in tags])

    # Crear el archivo Excel
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Etiquetas', index=False)
    writer.close()
    output.seek(0)

    # Preparar la respuesta con el archivo Excel
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=tags_export.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response


# Ruta: Editar Pulzcard
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
        return redirect(url_for('profile') + '#pulzcardsSection')
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


# Ruta: Eliminar Pulzcard
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

    return redirect(url_for('profile') + '#pulzcardsSection')


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
        return redirect(url_for('profile') + '#etiquetasSection')  # Redirección mejorada
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
        return redirect(url_for('profile') + '#etiquetasSection')  # Redirección mejorada
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
    share_url = url_for('redirect_tag', tag_id=tag.tag_id, _external=True)
    return render_template('qrcode_card.html', qr_url=qr_image_url, entity_type='Etiqueta', tag_id=tag_id, share_url=share_url)


@app.route('/pulzcard/qrcode_image/<card_id>')
@login_required
def pulzcard_qrcode_image(card_id):
    pulzcard = Pulzcard.query.filter_by(card_id=card_id, user_id=current_user.id).first_or_404()
    url = url_for('pulzcard_card', card_id=pulzcard.card_id, _external=True)  # Confirmar uso de 'pulzcard_card'
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
    share_url = url_for('pulzcard_card', card_id=pulzcard.card_id, _external=True)
    return render_template(
        'qrcode_card.html',
        qr_url=qr_image_url,
        entity_type='Pulzcard',
        tag_id=card_id,
        share_url=share_url
    )


# Nuevas rutas para Bodega y Caja con UUID y códigos QR
@app.route('/bodega/new', methods=['GET', 'POST'])
@login_required
def create_bodega():
    form = BodegaForm()
    if form.validate_on_submit():
        new_bodega = Bodega(
            nombre=form.nombre.data,
            ubicacion=form.ubicacion.data,
            notas=form.notas.data,
            user_id=current_user.id
        )
        new_bodega.id_bodega = generar_id_bodega()
        db.session.add(new_bodega)
        db.session.commit()
        flash('Tu bodega ha sido creada exitosamente.', 'success')
        return redirect(url_for('profile', section='bodegasSection'))
    return render_template('create_bodega.html', title='Crear Bodega', form=form)


@app.route('/bodega/<uuid_bodega>', methods=['GET', 'POST'])
@login_required
def view_bodega(uuid_bodega):
    bodega = Bodega.query.filter_by(uuid=uuid_bodega, user_id=current_user.id).first_or_404()
    form = CajaForm()
    delete_caja_forms = {caja.uuid: DeleteCajaForm(prefix=str(caja.uuid)) for caja in bodega.cajas}

    if form.validate_on_submit():
        nueva_caja = Caja(
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            notas=form.notas.data,
            bodega_id=bodega.id
        )
        nueva_caja.id_caja = generar_id_caja()
        db.session.add(nueva_caja)
        db.session.commit()
        flash('Caja agregada exitosamente.', 'success')
        return redirect(url_for('view_bodega', uuid_bodega=uuid_bodega))

    return render_template(
        'bodega_detail.html',
        bodega=bodega,
        form=form,
        delete_caja_forms=delete_caja_forms
    )


@app.route('/bodega/<uuid_bodega>/caja/new', methods=['GET', 'POST'])
@login_required
def create_caja(uuid_bodega):
    # Verificar si la bodega existe
    bodega = Bodega.query.filter_by(uuid=uuid_bodega, user_id=current_user.id).first_or_404()

    form = CajaForm()
    if form.validate_on_submit():
        nueva_caja = Caja(
            id_caja=generar_id_caja(),
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            notas=form.notas.data,
            bodega_id=bodega.id  # Relaciona la caja con la bodega
        )
        try:
            db.session.add(nueva_caja)
            db.session.commit()
            flash('Caja creada exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la caja: {str(e)}', 'danger')
        return redirect(url_for('view_bodega', uuid_bodega=uuid_bodega))

    return render_template('create_caja.html', form=form, bodega=bodega)


@app.route('/bodega/edit/<uuid_bodega>', methods=['GET', 'POST'])
@login_required
def edit_bodega(uuid_bodega):
    bodega = Bodega.query.filter_by(uuid=uuid_bodega, user_id=current_user.id).first_or_404()
    form = EditBodegaForm()
    if form.validate_on_submit():
        bodega.nombre = form.nombre.data
        bodega.ubicacion = form.ubicacion.data
        bodega.notas = form.notas.data
        db.session.commit()
        flash('Bodega actualizada exitosamente.', 'success')
        return redirect(url_for('profile') + '#bodegasSection')
    elif request.method == 'GET':
        form.nombre.data = bodega.nombre
        form.ubicacion.data = bodega.ubicacion
        form.notas.data = bodega.notas
    return render_template('edit_bodega.html', title='Editar Bodega', form=form, bodega=bodega)


@app.route('/bodega/delete/<uuid_bodega>', methods=['POST'])
@login_required
def delete_bodega(uuid_bodega):
    bodega = Bodega.query.filter_by(uuid=uuid_bodega, user_id=current_user.id).first_or_404()
    form = DeleteBodegaForm()
    if form.validate_on_submit():
        db.session.delete(bodega)
        db.session.commit()
        flash('Bodega eliminada exitosamente.', 'success')
    else:
        flash('Formulario inválido o token CSRF no válido.', 'danger')
    return redirect(url_for('main.profile') + '#bodegasSection')


@app.route('/bodega/qrcode_image/<uuid_bodega>')
@login_required
def bodega_qrcode_image(uuid_bodega):
    bodega = Bodega.query.filter_by(uuid=uuid_bodega, user_id=current_user.id).first_or_404()
    url = url_for('view_bodega', uuid_bodega=bodega.uuid, _external=True)
    # Generar el código QR
    qr_img = qrcode.make(url)
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route('/bodega/qrcode/<uuid_bodega>')
@login_required
def bodega_qrcode(uuid_bodega):
    bodega = Bodega.query.filter_by(uuid=uuid_bodega, user_id=current_user.id).first_or_404()
    qr_image_url = url_for('bodega_qrcode_image', uuid_bodega=bodega.uuid)
    share_url = url_for('view_bodega', uuid_bodega=bodega.uuid, _external=True)
    return render_template(
        'qrcode_card.html',
        qr_url=qr_image_url,
        entity_type='Bodega',
        tag_id=uuid_bodega,
        share_url=share_url
    )


@app.route('/caja/<uuid_caja>', methods=['GET'])
@login_required
def view_caja(uuid_caja):
    # Realizar un join entre Caja y Bodega para filtrar por user_id
    caja = Caja.query.join(Bodega).filter(
        Caja.uuid == uuid_caja,
        Bodega.user_id == current_user.id
    ).first_or_404(description='Caja no encontrada.')
    
    # Crear una instancia de DeleteProductoForm para manejar la eliminación de productos
    delete_producto_form = DeleteProductoForm()
    
    return render_template('caja_detail.html', caja=caja, delete_producto_form=delete_producto_form)


@app.route('/caja/edit/<uuid_caja>', methods=['GET', 'POST'])
@login_required
def edit_caja(uuid_caja):
    caja = Caja.query.join(Bodega).filter(
        Caja.uuid == uuid_caja,
        Bodega.user_id == current_user.id
    ).first_or_404(description='Caja no encontrada.')
    
    form = EditCajaForm()

    # Configurar dinámicamente las opciones para bodega_id
    form.bodega_id.choices = [(b.id, b.nombre) for b in Bodega.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        caja.nombre = form.nombre.data
        caja.categoria = form.categoria.data
        caja.notas = form.notas.data
        nueva_bodega_id = form.bodega_id.data

        # Verificar si la bodega existe antes de asignar
        nueva_bodega = Bodega.query.filter_by(id=nueva_bodega_id).first()
        if not nueva_bodega:
            flash('La bodega seleccionada no existe.', 'danger')
            return redirect(url_for('edit_caja', uuid_caja=uuid_caja))

        caja.bodega_id = nueva_bodega.id
        db.session.commit()
        flash('Caja actualizada exitosamente.', 'success')
        return redirect(url_for('view_bodega', uuid_bodega=nueva_bodega.uuid))
    else:
        if request.method == 'GET':
            form.nombre.data = caja.nombre
            form.categoria.data = caja.categoria
            form.notas.data = caja.notas
            form.bodega_id.data = caja.bodega_id  # Preseleccionar la bodega actual
    
    return render_template('edit_caja.html', form=form, caja=caja)


@app.route('/caja/delete/<uuid_caja>', methods=['POST'])
@login_required
def delete_caja(uuid_caja):
    caja = Caja.query.filter_by(uuid=uuid_caja).join(Bodega).filter(Bodega.user_id == current_user.id).first_or_404()
    form = DeleteCajaForm()
    bodega_uuid = caja.bodega.uuid

    if form.validate_on_submit():
        db.session.delete(caja)
        db.session.commit()
        flash('Caja eliminada exitosamente.', 'success')
    else:
        flash('Error al eliminar la caja.', 'danger')
    return redirect(url_for('view_bodega', uuid_bodega=bodega_uuid))


@app.route('/caja/qrcode_image/<uuid_caja>')
@login_required
def caja_qrcode_image(uuid_caja):
    caja = Caja.query.filter_by(uuid=uuid_caja).join(Bodega).filter(Bodega.user_id == current_user.id).first_or_404()
    url = url_for('view_caja', uuid_caja=caja.uuid, _external=True)
    # Generar el código QR
    qr_img = qrcode.make(url)
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route('/caja/qrcode/<uuid_caja>')
@login_required
def caja_qrcode(uuid_caja):
    caja = Caja.query.filter_by(uuid=uuid_caja).join(Bodega).filter(Bodega.user_id == current_user.id).first_or_404()
    qr_image_url = url_for('caja_qrcode_image', uuid_caja=caja.uuid)
    share_url = url_for('view_caja', uuid_caja=caja.uuid, _external=True)
    return render_template('qrcode_card.html', qr_url=qr_image_url, entity_type='Caja', tag_id=uuid_caja, share_url=share_url)


@app.route('/productos/<uuid_producto>', endpoint='product_detail')
@login_required
def product_detail(uuid_producto):
    """
    Vista para mostrar los detalles de un producto específico.

    Args:
        uuid_producto (str): UUID del producto.

    Returns:
        Renderiza la plantilla 'product_detail.html' con los detalles del producto.
    """
    producto = Producto.query.join(Caja).join(Bodega).filter(
        Producto.uuid == uuid_producto,
        Bodega.user_id == current_user.id
    ).first_or_404(description='Producto no encontrado.')
    
    delete_producto_form = DeleteProductoForm()
    return render_template('product_detail.html', producto=producto, delete_producto_form=delete_producto_form)


@app.route('/cajas/<uuid_caja>/productos/nuevo', methods=['GET', 'POST'])
@login_required
def create_producto(uuid_caja):
    # Verificar que la caja exista usando el uuid proporcionado
    caja = Caja.query.filter_by(uuid=uuid_caja).first_or_404(description='Caja no encontrada.')

    form = ProductoForm()
    form.caja_id = caja.id  # Asigna el ID de la caja al formulario si es necesario

    if form.validate_on_submit():
        # Verificar si ya existe un producto con el mismo ID en esta caja usando exists
        producto_existente = db.session.query(exists().where(
            Producto.id_producto == form.id_producto.data,
            Producto.caja_id == caja.id
        )).scalar()

        if producto_existente:
            flash('Ya existe un producto con este ID en la caja.', 'danger')
            return redirect(url_for('create_producto', uuid_caja=uuid_caja))

        try:
            # Crear un nuevo producto
            nuevo_producto = Producto(
                id_producto=form.id_producto.data,
                nombre=form.nombre.data,
                descripcion=form.descripcion.data,
                cantidad=form.cantidad.data,
                categoria=form.categoria.data,
                subcategoria=form.subcategoria.data,
                caja_id=caja.id,
                notas=form.notas.data
            )
            db.session.add(nuevo_producto)
            db.session.commit()
            flash('Producto añadido correctamente.', 'success')
            return redirect(url_for('view_caja', uuid_caja=caja.uuid))
        except IntegrityError:
            db.session.rollback()
            flash('El ID del producto ya existe en esta caja.', 'danger')
            return redirect(url_for('create_producto', uuid_caja=uuid_caja))
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar producto: {e}")
            flash('Ocurrió un error inesperado. Por favor, inténtalo de nuevo.', 'danger')
            return redirect(url_for('create_producto', uuid_caja=uuid_caja))

    # Mostrar errores de validación si los hay
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {field}: {error}", 'danger')

    return render_template('create_producto.html', form=form, caja=caja)


@app.route('/productos/<uuid_producto>/edit', methods=['GET', 'POST'], endpoint='edit_producto')
@login_required
def edit_producto(uuid_producto):
    """
    Vista para editar un producto específico.

    Args:
        uuid_producto (str): UUID del producto a editar.

    Returns:
        Renderiza la plantilla 'edit_producto.html' con el formulario de edición o redirige al detalle del producto.
    """
    producto = Producto.query.filter_by(uuid=uuid_producto).first_or_404()
    form = EditProductoForm(original_id_producto=producto.id_producto, obj=producto)  # Utiliza EditProductoForm

    if form.validate_on_submit():
        # Actualizar los campos del producto
        producto.id_producto = form.id_producto.data
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.cantidad = form.cantidad.data
        producto.categoria = form.categoria.data
        producto.subcategoria = form.subcategoria.data
        producto.notas = form.notas.data

        try:
            db.session.commit()
            flash('Producto actualizado exitosamente.', 'success')
            return redirect(url_for('product_detail', uuid_producto=producto.uuid))
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar el producto: {e}")
            flash('Hubo un error al actualizar el producto. Por favor, intenta de nuevo.', 'danger')

    return render_template('edit_producto.html', form=form, producto=producto)


@app.route('/productos/<uuid_producto>/delete', methods=['POST'], endpoint='delete_producto')
@login_required
def delete_producto(uuid_producto):
    """
    Vista para eliminar un producto específico.

    Args:
        uuid_producto (str): UUID del producto a eliminar.

    Returns:
        Redirige a la vista de la caja correspondiente con un mensaje de éxito o error.
    """
    producto = Producto.query.filter_by(uuid=uuid_producto).first_or_404()

    form = DeleteProductoForm()  # Asegúrate de tener un formulario CSRF para la eliminación
    if form.validate_on_submit():
        try:
            db.session.delete(producto)
            db.session.commit()
            flash('Producto eliminado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar el producto: {e}")
            flash('Hubo un error al eliminar el producto. Por favor, intenta de nuevo.', 'danger')
    else:
        flash('Formulario inválido o token CSRF no válido.', 'danger')

    return redirect(url_for('view_caja', uuid_caja=producto.caja.uuid))


@app.route('/productos/<uuid_producto>/qrcode_image', methods=['GET'])
@login_required
def producto_qrcode_image(uuid_producto):
    producto = Producto.query.filter_by(uuid=uuid_producto, caja_id=Producto.caja_id).first_or_404()
    url = url_for('product_detail', uuid_producto=producto.uuid, _external=True)
    # Generar el código QR
    qr_img = qrcode.make(url)
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route('/productos/qrcode/<uuid_producto>', methods=['GET'])
@login_required
def producto_qrcode(uuid_producto):
    # Asegurarse de que el producto pertenece a una caja del usuario actual
    producto = Producto.query.join(Caja).join(Bodega).filter(
        Producto.uuid == uuid_producto,
        Bodega.user_id == current_user.id
    ).first_or_404()
    
    qr_image_url = url_for('producto_qrcode_image', uuid_producto=producto.uuid)
    share_url = url_for('product_detail', uuid_producto=producto.uuid, _external=True)
    
    return render_template(
        'qrcode_card.html',
        qr_url=qr_image_url,
        entity_type='Producto',
        tag_id=uuid_producto,
        share_url=share_url
    )


# Rutas para DashboardItem (Definidas una sola vez)
@app.route('/create_dashboard_item', methods=['POST'])
@login_required
def create_dashboard_item():
    data = request.get_json()
    name = data.get('name')
    item_type = data.get('item_type')

    if not name or not item_type:
        return jsonify({'error': 'Datos incompletos'}), 400

    new_item = DashboardItem(
        name=name,
        item_type=item_type,
        user_id=current_user.id
    )
    db.session.add(new_item)
    db.session.commit()

    return jsonify({'uuid': new_item.uuid}), 200


@app.route('/delete_dashboard_item', methods=['POST'])
@login_required
def delete_dashboard_item():
    data = request.get_json()
    item_uuid = data.get('uuid')
    if not item_uuid:
        return jsonify({'error': 'UUID no proporcionado'}), 400

    item = DashboardItem.query.filter_by(uuid=item_uuid, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Ítem no encontrado o no autorizado'}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar el ítem.'}), 500


@app.route('/get_ratings_data', methods=['GET'])
@login_required
def get_ratings_data():
    """
    Devuelve un JSON con:
      {
        "ratings": { "1": [...], "2": [...], ..., "10": [...] },
        "dates": ["YYYY-MM-DD", ..., "YYYY-MM-DD"],
        "details": {
          "YYYY-MM-DD": [
            {"rating": 7, "comment": "Algún comentario"},
            ...
          ],
          ...
        }
      }
    """
    item_uuid = request.args.get('item_uuid')
    if not item_uuid:
        return jsonify({"error": "Falta item_uuid"}), 400

    # Verificar que el item exista y pertenezca al usuario actual
    item = DashboardItem.query.filter_by(uuid=item_uuid, user_id=current_user.id).first()
    if not item:
        return jsonify({"error": "Item no encontrado"}), 404

    # Últimos 10 días
    today = datetime.utcnow().date()
    dates = [(today - timedelta(days=i)) for i in range(10)]
    dates.sort()

    # Diccionario para totales de rating 1..10
    ratingsData = {str(r): [0]*10 for r in range(1, 11)}

    # Diccionario para detalles (día -> lista de {rating, comment})
    detailsByDay = {d.strftime('%Y-%m-%d'): [] for d in dates}

    # Rango de fechas
    start_datetime = datetime.combine(dates[0], datetime.min.time())
    end_datetime = datetime.combine(dates[-1] + timedelta(days=1), datetime.min.time())

    # Filtrar las respuestas en ese rango
    responses = SurveyResponse.query.filter(
        SurveyResponse.item_id == item.id,
        SurveyResponse.timestamp >= start_datetime,
        SurveyResponse.timestamp < end_datetime
    ).all()

    # Sumar totales y guardar detalles
    for resp in responses:
        resp_date = resp.timestamp.date()
        if resp_date in dates:
            day_index = dates.index(resp_date)
            rating_str = str(resp.rating)
            # Incrementar conteo
            if rating_str in ratingsData:
                ratingsData[rating_str][day_index] += 1

            # Guardar detalle (rating, comentario)
            date_key = resp_date.strftime('%Y-%m-%d')
            detailsByDay[date_key].append({
                "rating": resp.rating,
                "comment": resp.comment or "Sin Comentario"
            })

    # Convertir fechas a string p.e. YYYY-MM-DD
    sorted_dates_str = [d.strftime('%Y-%m-%d') for d in dates]

    return jsonify({
        "ratings": ratingsData,
        "dates": sorted_dates_str,
        "details": detailsByDay
    })


@app.route('/survey/<item_uuid>')
def survey(item_uuid):
    """
    Muestra la encuesta para un DashboardItem específico.
    - "Evaluación de Clientes" => encuesta NPS (1..10).
    - "Visualizaciones diarias" => una página placeholder.
    - "Evaluación de Semáforo" => otra encuesta, si lo deseas.
    """
    item = DashboardItem.query.filter_by(uuid=item_uuid).first()
    if not item:
        return "Este ítem no existe o ha sido eliminado.", 404

    if item.item_type == "Evaluación de Clientes":
        # Renderiza la encuesta NPS (1..10)
        return render_template('encuesta_evaluacion.html', item_uuid=item_uuid)
    elif item.item_type == "Visualizaciones diarias":
        return "Esta sección mostrará un resultado distinto para 'Visualizaciones diarias'."
    elif item.item_type == "Evaluación de Semáforo":
        return "Aquí podrías mostrar la encuesta de 1..3 (Semáforo)."
    else:
        return "Tipo de ítem desconocido."


@app.route('/survey/submit/<item_uuid>', methods=['POST'])
def submit_survey(item_uuid):
    """
    Procesa la respuesta de la encuesta. Almacena rating 1..10 y comentario.
    Muestra una pantalla de gracias (survey_thanks.html) o un template de error.
    """
    evaluation = request.form.get('evaluation')
    comment = request.form.get('comment', '')

    # Buscar el ítem
    item = DashboardItem.query.filter_by(uuid=item_uuid).first()
    if not item:
        return render_template('survey_error.html', message="Item no encontrado"), 404

    # Verificar que el item admita evaluaciones
    if item.item_type not in ["Evaluación de Clientes", "Evaluación de Semáforo"]:
        return render_template('survey_error.html', message="Este ítem no admite evaluaciones."), 400

    # Guardar la respuesta en SurveyResponse
    try:
        rating_value = int(evaluation)  # rating entre 1..10
        new_response = SurveyResponse(
            item_id=item.id,
            rating=rating_value,
            comment=comment,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_response)
        db.session.commit()

        # Retornar survey_thanks.html con rating_value
        #             ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        return render_template('survey_thanks.html', item=item, rating=rating_value), 200
        #                                    ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
        # Con "rating" pasamos el valor entero al template para mostrar 
        # un mensaje distinto según el puntaje.

    except Exception as e:
        db.session.rollback()
        return render_template('survey_error.html', message="Hubo un error al guardar tu evaluación."), 500

# --------------------------------------------------
# Rutas para generar y mostrar el Código QR de la encuesta
# --------------------------------------------------

@app.route('/survey_qrcode/<item_uuid>')
@login_required
def survey_qrcode(item_uuid):
    """
    Genera la página con el QR de la encuesta para un DashboardItem (item_uuid).
    Muestra el template qrcode_card.html.
    """
    # Verificar que el Item pertenezca al usuario logueado
    item = DashboardItem.query.filter_by(uuid=item_uuid, user_id=current_user.id).first()
    if not item:
        flash("Este ítem no existe o no te pertenece.", "danger")
        return redirect(url_for('profile'))

    # Construimos la URL de la encuesta, p. ej. /survey/<item_uuid> en forma absoluta (_external=True)
    survey_url = url_for('survey', item_uuid=item_uuid, _external=True)

    # Apuntamos a la ruta que devuelve la imagen en PNG
    # (survey_qrcode_image, que definimos abajo)
    qr_image_url = url_for('survey_qrcode_image', item_uuid=item_uuid, _external=True)

    # Reutilizamos el template qrcode_card.html
    # Parametrizamos para que se muestre "Encuesta" como entity_type
    # y la URL absoluta en "share_url" para que el usuario pueda copiarla.
    return render_template(
        'qrcode_card.html',
        qr_url=qr_image_url,
        entity_type='Encuesta',
        tag_id=item_uuid,      # Uso de "tag_id" para mantener tu estructura qrcode_card
        share_url=survey_url   # URL que el usuario puede copiar
    )


@app.route('/survey_qrcode_image/<item_uuid>')
@login_required
def survey_qrcode_image(item_uuid):
    """
    Devuelve la imagen PNG del QR, sin template intermedio.
    El QR apunta a la URL de la encuesta: /survey/<item_uuid>.
    """
    # Verificar que el Item pertenezca al usuario logueado
    item = DashboardItem.query.filter_by(uuid=item_uuid, user_id=current_user.id).first()
    if not item:
        abort(404, description="Ítem no encontrado.")

    # Construimos la URL final de la encuesta
    survey_url = url_for('survey', item_uuid=item_uuid, _external=True)

    # Generamos el QR
    img = qrcode.make(survey_url)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    # Devolvemos la imagen QR como 'image/png'
    return send_file(buf, mimetype='image/png')

@app.after_request
def add_header(response):
    """
    Deshabilita el cache del lado del navegador para evitar que
    se muestren datos antiguos.
    """
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Si tu aplicación principal se ejecuta aquí:
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)