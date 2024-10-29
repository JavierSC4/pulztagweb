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