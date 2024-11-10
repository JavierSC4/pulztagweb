# script_corregir_admins.py

from app import db, app  # Importa la instancia de app y db desde tu archivo app.py
from models import User

# Script de ejemplo para corregir usuarios existentes
with app.app_context():
    users = User.query.filter_by(is_admin=True).all()  # Busca todos los usuarios con is_admin=True
    for user in users:
        if user.username != 'admin':  # Opcional: mantener el administrador principal
            user.is_admin = False  # Establecer como False para los demás
    db.session.commit()
    print("Se han corregido los permisos de administrador de los usuarios.")