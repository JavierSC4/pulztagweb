# test_db.py

from sqlalchemy import create_engine
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'site.db')
db_uri = f'sqlite:///{db_path}'

engine = create_engine(db_uri)

try:
    connection = engine.connect()
    print("Conexión exitosa a la base de datos.")
    connection.close()
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")