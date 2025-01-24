import os

# Lista de rutas de los archivos a concatenar
archivos = [
    'migrations/alembic.ini',
    'migrations/env.py',
    'migrations/script.py.mako',
    'static/css/style.css',
    'static/js/script.js',
    'templates/pulzcard/card.html',
    'templates/pulzcard/index.html',
    'templates/about.html',
    'templates/account.html',
    'templates/base.html',
    'templates/contact.html',
    'templates/edit_pulzcard.html',
    'templates/index.html',
    'templates/login.html',
    'templates/order.html',
    'templates/products.html',
    'templates/profile.html',
    'templates/register.html',
    'templates/reset_request.html',
    'templates/reset_token.html',
    'templates/tags.html',
    '.gitignore',
    'app.py',
    'extensions.py',
    'forms.py',
    'minimal_app.py',
    'models.py',
    'requirements.txt',
    'site_backup.db',
    'test_db.py',
    'instance/site_new.db',
    'migrations/__pycache__/__init__.cpython-311.pyc',
    
    # Archivos adicionales de Plantillas (Templates) a agregar
    'templates/bodega_detail.html',
    'templates/caja_detail.html',
    'templates/create_bodega.html',
    'templates/create_caja.html',
    'templates/create_item.html',
    'templates/create_producto.html',
    'templates/create_tag.html',
    'templates/edit_bodega.html',
    'templates/edit_caja.html',
    'templates/edit_producto.html',
    'templates/encuesta_evaluacion.html',
    'templates/encuesta_evaluacion_semaforo.html',
    'templates/footer.html',
    'templates/head.html',
    'templates/modal_agregar_item.html',
    'templates/navbar.html',
    'templates/product_detail.html',
    'templates/product_list.html',
    'templates/productsnew.html',
    'templates/pulzcard/template1.html',
    'templates/pulzcard/template2.html',
    'templates/pulzcard/template3.html',
    'templates/qrcode_card.html',
    'templates/services.html',
    'templates/sidebar.html',
    'templates/smartcontent_options.html',
    'templates/survey_comment.html',
    'templates/survey_error.html',
    'templates/survey_thanks.html',
    'templates/users.html',
    'templates/video_base.html',
    
    # Archivos adicionales de Python a agregar
    'routes/__init__.py',
    'routes/auth_routes.py',
    'test_mail.py',
    'migrations/versions/d06faea1c24e_initial_migration.py',
]

# Nombre del archivo de salida
salida = 'consolidado.txt'

with open(salida, 'w', encoding='utf-8') as archivo_salida:
    for ruta in archivos:
        if os.path.exists(ruta):
            archivo_salida.write(f'----- Inicio de {ruta} -----\n')
            try:
                # Intenta abrir el archivo en modo texto con codificación utf-8
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    archivo_salida.write(contenido + '\n\n')
            except (UnicodeDecodeError, IsADirectoryError):
                # Si el archivo no es decodable o es un directorio, escribe un aviso
                archivo_salida.write(f'----- No se pudo leer {ruta} (archivo binario o no decodable) -----\n\n')
            archivo_salida.write(f'----- Fin de {ruta} -----\n\n')
        else:
            archivo_salida.write(f'----- {ruta} no encontrado -----\n\n')

print(f'Contenido concatenado en {salida}')