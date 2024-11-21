from app import app, db
from models import User

# Establecer el contexto de la aplicación
with app.app_context():
    # Buscar al usuario por email
    user_to_delete = User.query.filter_by(email="example@example.com").first()

    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        print(f"Usuario {user_to_delete.username} eliminado.")
    else:
        print("El usuario no existe.")