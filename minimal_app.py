import os

from flask import Flask
from extensions import db, migrate

app = Flask(__name__, instance_relative_config=True)

# Crear el directorio 'instance' si no existe
instance_dir = os.path.join(app.instance_path)
os.makedirs(instance_dir, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_dir, "site.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'test_secret_key')

db.init_app(app)
migrate.init_app(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Asegura que la base de datos y las tablas se creen
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')