from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import pandas as pd
from werkzeug.utils import secure_filename
import uuid
import imghdr  # Para verificar el tipo real de imagen

load_dotenv()  # Cargar las variables de entorno desde .env

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Usar la variable de entorno

# Configuración de Flask-Mail usando variables de entorno
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Tu dirección de correo Gmail
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Opcional: El remitente por defecto

mail = Mail(app)

# Directorio para guardar las subidas
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Extensiones permitidas
ALLOWED_LOGO_EXTENSIONS = {'png', 'jpeg', 'jpg'}
ALLOWED_EXCEL_EXTENSIONS = {'xlsx', 'xls'}


def allowed_file(filename, allowed_extensions):
    filename = filename.strip()
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower().strip() in allowed_extensions


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
        # Contar solo los logos con nombre de archivo
        valid_logos = [logo for logo in logos if logo.filename != '']
        if len(valid_logos) > 10:
            flash('Puedes subir un máximo de 10 logos.', 'danger')
            return redirect(url_for('order'))

        saved_logos = []
        for logo in valid_logos:
            filename = logo.filename.strip()
            extension = filename.rsplit('.', 1)[1].lower().strip()
            print(f"Procesando archivo: '{filename}', extensión: '{extension}'")

            if allowed_file(filename, ALLOWED_LOGO_EXTENSIONS):
                # Verificar el tipo real de la imagen
                logo_bytes = logo.read()
                image_type = imghdr.what(None, h=logo_bytes)
                logo.seek(0)  # Volver al inicio del archivo

                if image_type in ALLOWED_LOGO_EXTENSIONS:
                    # Procesar y guardar el logo
                    secure_name = secure_filename(filename)
                    unique_filename = f"{uuid.uuid4().hex}_{secure_name}"
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    logo.save(logo_path)
                    saved_logos.append((secure_name, logo_path))
                    print(f"Logo guardado: {logo_path}")
                else:
                    flash(f"Formato de logo no permitido: {filename}", 'danger')
                    return redirect(url_for('order'))
            else:
                flash(f"Formato de logo no permitido: {filename}", 'danger')
                return redirect(url_for('order'))

        # Manejar el archivo Excel
        excel = request.files.get('excel')
        if excel and excel.filename != '':
            filename = excel.filename.strip()
            if allowed_file(filename, ALLOWED_EXCEL_EXTENSIONS):
                secure_name = secure_filename(filename)
                unique_filename = f"{uuid.uuid4().hex}_{secure_name}"
                excel_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
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
        pedido_excel_path = os.path.join(app.config['UPLOAD_FOLDER'], f"pedido_{uuid.uuid4().hex}.xlsx")
        df.to_excel(pedido_excel_path, index=False)

        # Enviar el correo con los archivos adjuntos
        try:
            msg = Message(
                subject="Nuevo Pedido de PulztagWeb",
                recipients=['contacto@pulztag.com']
            )
            msg.body = f"Nombre: {nombre}\nCorreo Electrónico: {email}\n\nMensaje:\n{mensaje}"

            # Adjuntar el archivo Excel del pedido
            with app.open_resource(pedido_excel_path) as fp:
                msg.attach(
                    "pedido.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    fp.read()
                )

            # Adjuntar los logos
            for original_filename, logo_path in saved_logos:
                try:
                    print(f"Adjuntando logo: {original_filename} desde {logo_path}")
                    with app.open_resource(logo_path) as fp:
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
                with app.open_resource(excel_path) as fp:
                    msg.attach(
                        os.path.basename(excel_path),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        fp.read()
                    )

            # Imprimir los adjuntos en el mensaje
            print(f"Adjuntos en el mensaje: {msg.attachments}")

            mail.send(msg)
            flash('Su solicitud fue enviada exitosamente. ¡Pronto nos pondremos en contacto contigo!', 'success')
            return redirect(url_for('order'))
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            flash('Hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.', 'danger')
            return redirect(url_for('order'))

    return render_template('order.html')


# Configurar la aplicación para escuchar en el puerto asignado por Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)  # Cambia debug a True para depuración