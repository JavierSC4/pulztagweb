# minimal_app.py

import os  # Se agregó esta línea

from flask import Flask
from extensions import db, migrate

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'test_secret_key'

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