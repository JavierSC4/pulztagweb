# extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_message = ''  # Elimina el mensaje
mail = Mail()  # Inicializa mail
oauth = OAuth()