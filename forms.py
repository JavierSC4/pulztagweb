# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField, SelectField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, Regexp
from flask_wtf.file import FileAllowed
from models import User

class VerificationForm(FlaskForm):
    verification_code = StringField('Código de Verificación', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verificar')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ese nombre de usuario ya está tomado. Por favor, elige otro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ese correo electrónico ya está en uso. Por favor, elige otro.')

class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar Sesión')

class UpdateAccountForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    password = PasswordField('Nueva Contraseña', validators=[
        Optional(),
        Length(min=8, message='La nueva contraseña debe tener al menos 8 caracteres.'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', message='La nueva contraseña debe incluir al menos una letra mayúscula, una minúscula, un número y un carácter especial.')])
    confirm_password = PasswordField('Confirmar Nueva Contraseña', validators=[Optional(), EqualTo('password', message='Las contraseñas deben coincidir')])
    submit = SubmitField('Actualizar')

class RequestResetForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Restablecimiento de Contraseña')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No hay una cuenta con ese correo electrónico. Debes registrarte primero.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres.'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', message='La contraseña debe incluir al menos una letra mayúscula, una minúscula, un número y un carácter especial (@$!%*?&).')])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Restablecer Contraseña')

class PulzcardForm(FlaskForm):
    card_name = StringField('Nombre de la Tarjeta', validators=[DataRequired()])
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    organization = StringField('Organización', validators=[DataRequired()])
    position = StringField('Cargo', validators=[DataRequired()])
    phone = StringField('Teléfono', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    website = StringField('Sitio Web', validators=[DataRequired()])
    address = StringField('Dirección', validators=[DataRequired()])
    image_file = FileField('Imagen de Perfil', validators=[FileAllowed(['jpg', 'png'])])
    template = SelectField('Plantilla', choices=[('template1', 'Plantilla 1'), ('template2', 'Plantilla 2'), ('template3', 'Plantilla 3')], validators=[DataRequired()])
    submit = SubmitField('Crear Tarjeta')

class EditPulzcardForm(FlaskForm):
    card_name = StringField('Nombre de la Tarjeta', validators=[DataRequired()])
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    organization = StringField('Organización', validators=[DataRequired()])
    position = StringField('Cargo', validators=[DataRequired()])
    phone = StringField('Teléfono', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    website = StringField('Sitio Web', validators=[DataRequired()])
    address = StringField('Dirección', validators=[DataRequired()])
    image_file = FileField('Actualizar Imagen de Perfil', validators=[FileAllowed(['jpg', 'png'])])
    template = SelectField('Plantilla', choices=[('template1', 'Plantilla 1'), ('template2', 'Plantilla 2'), ('template3', 'Plantilla 3')], validators=[DataRequired()])
    submit = SubmitField('Actualizar Tarjeta')

class DeletePulzcardForm(FlaskForm):
    submit = SubmitField('Eliminar')

class ImportPulzcardForm(FlaskForm):
    excelFile = FileField('Archivo Excel', validators=[
        DataRequired(message='Por favor, selecciona un archivo Excel.'),
        FileAllowed(['xlsx', 'xls'], 'Solo se permiten archivos de Excel (.xlsx, .xls).')
    ])
    submit = SubmitField('Importar Pulzcards')

class BulkDeletePulzcardForm(FlaskForm):
    submit = SubmitField('Eliminar Selección')

class ContactForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    mensaje = TextAreaField('Mensaje', validators=[DataRequired()])
    submit = SubmitField('Enviar')


class OrderForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    dispositivo = SelectField('Selecciona un Dispositivo', choices=[
        ('', 'Selecciona producto'),
        ('Etiqueta de Sticker de RR.SS. NFC Antimetal.', 'Etiqueta de Sticker de RR.SS. NFC Antimetal.'),
        ('Tarjetas PVC Inteligentes NFC.', 'Tarjetas PVC Inteligentes NFC.'),
        ('Soporte de Menú de Acrílico con Código QR y NFC.', 'Soporte de Menú de Acrílico con Código QR y NFC.'),
        ('Pulseras Tejidas NFC Personalizables.', 'Pulseras Tejidas NFC Personalizables.'),
        ('Pulsera NFC de silicona ecológica.', 'Pulsera NFC de silicona ecológica.'),
        ('Etiqueta NFC de Redes Sociales Epoxy.', 'Etiqueta NFC de Redes Sociales Epoxy.'),
        ('Tarjetas de Madera NFC Empresariales Personalizables', 'Tarjetas de Madera NFC Empresariales Personalizables'),
        ('Tarjeta PVC Reescribible Blanca o Negra Personalizable.', 'Tarjeta PVC Reescribible Blanca o Negra Personalizable.'),
        ('Tarjetas Redondas NFC de PVC Duro NTAG personalizables', 'Tarjetas Redondas NFC de PVC Duro NTAG personalizables')
    ], validators=[DataRequired(message="Por favor, selecciona un dispositivo.")])
    mensaje = TextAreaField('¿Qué necesitas?', validators=[DataRequired()])
    submit = SubmitField('Enviar solicitud')

class TagForm(FlaskForm):
    tag_name = StringField('Nombre de la Etiqueta', validators=[DataRequired()])
    redirect_url = StringField('URL de Redirección', validators=[DataRequired()])
    submit = SubmitField('Crear Etiqueta')

class EditTagForm(FlaskForm):
    tag_name = StringField('Nombre de la Etiqueta', validators=[DataRequired()])
    redirect_url = StringField('URL de Redirección', validators=[DataRequired()])
    submit = SubmitField('Actualizar Etiqueta')

class DeleteTagForm(FlaskForm):
    submit = SubmitField('Eliminar')

class ImportTagsForm(FlaskForm):
    excelFile = FileField('Archivo Excel', validators=[
        DataRequired(message='Por favor, selecciona un archivo Excel.'),
        FileAllowed(['xlsx', 'xls'], 'Solo se permiten archivos de Excel (.xlsx, .xls).')
    ])
    submit = SubmitField('Importar Etiquetas')

class BodegaForm(FlaskForm):
    nombre = StringField('Nombre de la Bodega', validators=[DataRequired()])
    ubicacion = StringField('Ubicación', validators=[Optional()])
    notas = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Crear Bodega')

class EditBodegaForm(FlaskForm):
    nombre = StringField('Nombre de la Bodega', validators=[DataRequired()])
    ubicacion = StringField('Ubicación', validators=[Optional()])
    notas = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Actualizar Bodega')

class DeleteBodegaForm(FlaskForm):
    submit = SubmitField('Eliminar')

class CajaForm(FlaskForm):
    nombre = StringField('Nombre de la Caja', validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[Optional()])
    notas = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Guardar')

class EditCajaForm(FlaskForm):
    nombre = StringField('Nombre de la Caja', validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[Optional()])
    notas = TextAreaField('Notas', validators=[Optional()])
    bodega_id = SelectField('Bodega', coerce=int, validators=[DataRequired()])  # Añadido para seleccionar la bodega
    submit = SubmitField('Actualizar')

class DeleteCajaForm(FlaskForm):
    submit = SubmitField('Eliminar')

class ProductoForm(FlaskForm):
    id_producto = StringField('ID Producto', validators=[DataRequired(), Length(max=10)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=255)])
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[Optional(), Length(max=100)])  # Nuevo campo
    subcategoria = StringField('Subcategoría', validators=[Optional(), Length(max=100)])  # Nuevo campo
    notas = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Guardar Producto')

class EditProductoForm(FlaskForm):
    id_producto = StringField('ID Producto', validators=[DataRequired(), Length(max=10)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=255)])
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[Optional(), Length(max=100)])
    subcategoria = StringField('Subcategoría', validators=[Optional(), Length(max=100)])
    notas = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Actualizar Producto')

class DeleteProductoForm(FlaskForm):
    submit = SubmitField('Eliminar')

class BulkDeleteTagForm(FlaskForm):
    submit = SubmitField('Eliminar Selección')

class DeleteDashboardItemForm(FlaskForm):
    submit = SubmitField('Eliminar')
    # Si necesitas, puedes añadir un campo oculto para el UUID
    item_uuid = HiddenField('UUID', validators=[DataRequired()])