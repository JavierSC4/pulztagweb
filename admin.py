# admin.py

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request
from flask_login import current_user
from models import User, Pulzcard
from extensions import db
from flask import Flask

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('main.login'))
        return super(MyAdminIndexView, self).index()

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login', next=request.url))

# Crear una instancia de Flask-Admin
admin = Admin(name='Panel de Administración', template_mode='bootstrap3', index_view=MyAdminIndexView())

def init_admin(app):
    # Añadir vistas de modelos
    admin.init_app(app)
    admin.add_view(AdminModelView(User, db.session))
    admin.add_view(AdminModelView(Pulzcard, db.session))