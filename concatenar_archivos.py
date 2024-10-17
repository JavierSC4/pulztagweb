import os

# Lista de rutas de los archivos a concatenar
archivos = [
    'app.py',
    'minimal_app.py',
    'forms.py',
    'models.py',
    'test_db.py',
    'requirements.txt',
    'static/css/style.css',
    'static/js/script.js',
    'templates/about.html',
    'templates/account.html',
    'templates/login.html',
    'templates/base.html',
    'templates/index.html',
    'templates/contact.html',
    'templates/order.html',
    'templates/products.html',
    'templates/reset_request.html',
    'templates/reset_token.html',
    'templates/register.html'
    'templates/pulzcard/card.html'
    'templates/pulzcard/index.html'
]

# Nombre del archivo de salida
salida = 'consolidado.txt'

with open(salida, 'w', encoding='utf-8') as archivo_salida:
    for ruta in archivos:
        if os.path.exists(ruta):
            archivo_salida.write(f'----- Inicio de {ruta} -----\n')
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()
                archivo_salida.write(contenido + '\n\n')
            archivo_salida.write(f'----- Fin de {ruta} -----\n\n')
        else:
            archivo_salida.write(f'----- {ruta} no encontrado -----\n\n')

print(f'Contenido concatenado en {salida}')