from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email


class FormularioInicioSesion(FlaskForm):
    email = StringField(
        "email",
        validators=[
            InputRequired(message="El campo correo electrónico esta vacío."),
            Email(message="El formato del correo electrónico no es válido."),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[InputRequired(message="El campo de contraseña está vacío.")],
    )
