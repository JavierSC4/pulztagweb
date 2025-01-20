# config.py

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))  # Carga las variables de entorno desde .env

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_secreta_por_defecto')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'instance', 'site_backup.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Directorios para vCards y subidas
    VCARD_FOLDER = os.path.join(basedir, 'instance', 'vcards')
    UPLOAD_FOLDER = os.path.join(basedir, 'instance', 'uploads')

    # Configuración de Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')

    # Configuraciones de OAuth (Google)
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

    # Extensiones adicionales
    ALLOWED_LOGO_EXTENSIONS = {'png', 'jpeg', 'jpg'}
    ALLOWED_EXCEL_EXTENSIONS = {'xlsx', 'xls'}
