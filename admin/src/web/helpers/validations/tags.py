from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    BooleanField,
    DateField,
    SelectField,
)
from wtforms.validators import InputRequired, Length, Optional, ValidationError
from src.core.historicalSites.tags import get_tag_by_name, get_tag_by_slug, crear_slug


class TagForm(FlaskForm):
    """Formulario para validación de Tags"""

    name = StringField(
        "Nombre del Tag",
        validators=[
            InputRequired(message="El nombre es obligatorio."),
        ],
    )

    description = TextAreaField(
        "Descripción",
        validators=[
            Optional(),
            Length(max=255, message="La descripción no puede exceder 255 caracteres."),
        ],
    )

    def __init__(self, tag_id=None, *args, **kwargs):
        """
        Constructor que permite pasar el ID del tag que se está editando
        para excluirlo de las validaciones de unicidad.
        """
        super(TagForm, self).__init__(*args, **kwargs)
        self.tag_id = tag_id

    def validate_name(self, field):
        """Valida que no exista un Tag con el mismo nombre o slug."""
        if not field.data:
            return  # InputRequired se encarga de campos vacíos

        # Verificar nombre exacto
        existing_tag = get_tag_by_name(field.data)
        if existing_tag and (self.tag_id is None or existing_tag.id != self.tag_id):
            raise ValidationError("Ya existe un tag con ese nombre. Proba con otro.")

        # Verificar slug generado
        slug = crear_slug(field.data)
        existing_slug_tag = get_tag_by_slug(slug)
        if existing_slug_tag and (
            self.tag_id is None or existing_slug_tag.id != self.tag_id
        ):
            raise ValidationError("Ya existe un tag con ese nombre. Proba con otro.")
