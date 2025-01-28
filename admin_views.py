from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash, request
from wtforms import IntegerField, TextAreaField, SelectField, StringField, DateTimeField
from wtforms.validators import DataRequired, NumberRange, Optional
from models import DashboardItem, SurveyResponse
from datetime import datetime


class SurveyResponseAdminView(ModelView):
    # Habilitar la creación, edición y eliminación
    can_create = True
    can_edit = True
    can_delete = True

    # Definir las columnas que se mostrarán en la lista
    column_list = ['id', 'item', 'rating', 'comment', 'timestamp']

    # Agregar filtros y búsqueda
    column_filters = ['rating', 'timestamp', 'item.name']
    column_searchable_list = ['comment', 'item.name']

    # Campos que se mostrarán en el formulario
    form_columns = ['item', 'rating', 'comment', 'timestamp']

    # Configurar los argumentos del formulario
    form_args = {
        'rating': {
            'validators': [DataRequired(), NumberRange(min=1, max=10)],
        },
        'comment': {
            'validators': [Optional()]
        },
        'item': {
            'query_factory': lambda: DashboardItem.query.all(),
            'allow_blank': False,
            'get_label': 'name'  # Asegúrate de que DashboardItem tiene un campo 'name'
        }
    }

    # Agregar campo de fecha al formulario
    form_extra_fields = {
        'timestamp': DateTimeField(
            'Fecha y hora',
            format='%Y-%m-%d %H:%M:%S',  # Formato de fecha
            default=datetime.utcnow,      # Fecha predeterminada
        )
    }

    def is_accessible(self):
        # Solo usuarios autenticados y administradores pueden acceder
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # Redirige a la página de login si no tiene acceso
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('login', next=request.url))