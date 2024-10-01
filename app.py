# app.py
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import pandas as pd
from werkzeug.utils import secure_filename
import uuid

load_dotenv()  # Cargar las variables de entorno desde .env

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Usar la variable de entorno

# Configuración de Flask-Mail usando variables de entorno
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv(
    'MAIL_USERNAME')  # Tu dirección de correo Gmail
app.config['MAIL_PASSWORD'] = os.getenv(
    'MAIL_PASSWORD')  # Contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = os.getenv(
    'MAIL_USERNAME')  # Opcional: El remitente por defecto

mail = Mail(app)

# Directorio para guardar las subidas
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensiones permitidas
ALLOWED_LOGO_EXTENSIONS = {'png', 'jpeg', 'jpg'}
ALLOWED_EXCEL_EXTENSIONS = {'xlsx', 'xls'}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


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

        # Validación básica
        if not nombre or not email or not mensaje:
            flash('Por favor, completa todos los campos.', 'danger')
            return redirect(url_for('contact'))

        # Crear y enviar el correo electrónico
        try:
            msg = Message(
                subject=f"Nuevo mensaje de {nombre}",
                recipients=['contacto@pulztag.com'],
                body=f"Nombre: {nombre}\nCorreo Electrónico: {
                    email}\n\nMensaje:\n{mensaje}"
            )
            mail.send(msg)
            flash('¡Tu mensaje ha sido enviado exitosamente!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            print(e)
            flash(
                'Hubo un error al enviar tu mensaje. Por favor, inténtalo de nuevo más tarde.', 'danger')
            return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/order', methods=['GET', 'POST'])
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
        if len(logos) > 10:
            flash('Puedes subir un máximo de 10 logos.', 'danger')
            return redirect(url_for('order'))

        saved_logos = []
        for logo in logos:
            if logo and allowed_file(logo.filename, ALLOWED_LOGO_EXTENSIONS):
                filename = secure_filename(logo.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                logo_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], unique_filename)
                logo.save(logo_path)
                saved_logos.append((filename, logo_path))
            else:
                flash('Formato de logo no permitido.', 'danger')
                return redirect(url_for('order'))

        # Manejar el archivo Excel
        excel = request.files.get('excel')
        if excel:
            if allowed_file(excel.filename, ALLOWED_EXCEL_EXTENSIONS):
                filename = secure_filename(excel.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                excel_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], unique_filename)
                excel.save(excel_path)
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
        pedido_excel_path = os.path.join(
            app.config['UPLOAD_FOLDER'], f"pedido_{uuid.uuid4().hex}.xlsx")
        df.to_excel(pedido_excel_path, index=False)

        # Enviar el correo con los archivos adjuntos
        try:
            msg = Message(
                subject="Nuevo Pedido de PulztagWeb",
                recipients=['contacto@pulztag.com']
            )
            msg.body = f"Nombre: {nombre}\nCorreo Electrónico: {
                email}\n\nMensaje:\n{mensaje}"

            # Adjuntar el archivo Excel del pedido
            with app.open_resource(pedido_excel_path) as fp:
                msg.attach(
                    "pedido.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    fp.read()
                )

            # Adjuntar los logos
            for original_filename, logo_path in saved_logos:
                with app.open_resource(logo_path) as fp:
                    # Determinar el MIME type correcto
                    ext = original_filename.rsplit('.', 1)[1].lower()
                    mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
                    msg.attach(
                        original_filename,
                        mime_type,
                        fp.read()
                    )

            # Adjuntar el archivo Excel si existe
            if excel_path:
                with app.open_resource(excel_path) as fp:
                    msg.attach(
                        os.path.basename(excel_path),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        fp.read()
                    )

            mail.send(msg)
            flash(
                'Su solicitud fue enviada exitosamente. Pronto nos pondremos en contacto contigo!', 'success')
            return redirect(url_for('order'))
        except Exception as e:
            print(e)
            flash(
                'Hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.', 'danger')
            return redirect(url_for('order'))

    return render_template('order.html')


if __name__ == '__main__':
    app.run(debug=True)
