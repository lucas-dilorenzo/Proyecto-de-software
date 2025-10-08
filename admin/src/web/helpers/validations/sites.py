from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    BooleanField,
    DateField,
    SelectField,
)
from wtforms.validators import InputRequired, Length, NumberRange, Optional, Regexp
from datetime import date
from src.core.historicalSites.enums import ConservationStatus, SiteCategory


class SiteForm(FlaskForm):
    """Formulario para validación de sitios históricos"""

    # Campo obligatorio: nombre del sitio
    name = StringField(
        "Nombre del sitio",
        validators=[
            InputRequired(message="El nombre del sitio es obligatorio"),
            Length(
                min=3, max=200, message="El nombre debe tener entre 3 y 200 caracteres"
            ),
        ],
    )

    # Descripción corta
    description_short = StringField(
        "Descripción corta",
        validators=[
            Optional(),
            Length(
                max=500, message="La descripción corta no puede exceder 500 caracteres"
            ),
        ],
    )

    # Descripción completa
    description = TextAreaField(
        "Descripción",
        validators=[
            Optional(),
            Length(max=2000, message="La descripción no puede exceder 2000 caracteres"),
        ],
    )

    # Ciudad
    city = StringField(
        "Ciudad",
        validators=[
            Optional(),
            Length(
                min=2, max=100, message="La ciudad debe tener entre 2 y 100 caracteres"
            ),
        ],
    )

    # Provincia
    province = StringField(
        "Provincia",
        validators=[
            Optional(),
            Length(
                min=2,
                max=100,
                message="La provincia debe tener entre 2 y 100 caracteres",
            ),
        ],
    )

    # Ubicación (puede ser coordenadas)
    location = StringField(
        "Ubicación",
        validators=[
            InputRequired(message="La ubicación es obligatoria"),
            Length(max=200, message="La ubicación no puede exceder 200 caracteres"),
        ],
    )

    # Estado de conservación
    conservation_status = SelectField(
        "Estado de conservación",
        choices=ConservationStatus.choices(),
        validators=[Optional()],
    )

    # Año de declaración
    year_declared = IntegerField(
        "Año de declaración",
        validators=[
            Optional(),
            NumberRange(
                min=1,
                max=date.today().year,
                message=f"El año debe estar entre 1 y {date.today().year}",
            ),
        ],
    )

    # Categoría
    category = SelectField(
        "Categoría",
        choices=SiteCategory.choices(),
        validators=[Optional()],
    )

    # Fecha de registro
    registration_date = DateField(
        "Fecha de registro", validators=[Optional()], format="%Y-%m-%d"
    )

    # Visibilidad
    visibility = BooleanField("Visible", default=True)

    def validate_name(self, field):
        """Validación personalizada para el nombre"""
        if field.data:
            # Verificar que no contenga solo números
            if field.data.isdigit():
                raise ValueError("El nombre no puede contener solo números")

            # Verificar caracteres especiales excesivos
            special_chars = sum(
                1 for c in field.data if not c.isalnum() and not c.isspace()
            )
            if (
                special_chars > len(field.data) * 0.3
            ):  # Máximo 30% de caracteres especiales
                raise ValueError("El nombre contiene demasiados caracteres especiales")

    def validate_year_declared(self, field):
        """Validación personalizada para el año de declaración"""
        if field.data:
            current_year = date.today().year
            if field.data > current_year:
                raise ValueError("El año de declaración no puede ser futuro")

    def validate_registration_date(self, field):
        """Validación personalizada para la fecha de registro"""
        if field.data:
            if field.data > date.today():
                raise ValueError("La fecha de registro no puede ser futura")

    def validate_year_declared_vs_registration(self):
        """Validación que compara year_declared con registration_date"""
        if self.year_declared.data and self.registration_date.data:
            registration_year = self.registration_date.data.year
            if self.year_declared.data > registration_year:
                raise ValueError(
                    "El año de declaración no puede ser mayor que el año de la fecha de registro"
                )

    def validate(self, extra_validators=None):
        """Método de validación principal que incluye validaciones de múltiples campos"""
        # Ejecutar validaciones básicas primero
        rv = FlaskForm.validate(self, extra_validators)

        # Si hay errores básicos, no continuar con validaciones complejas
        if not rv:
            return False

        # Ejecutar validaciones personalizadas de múltiples campos
        try:
            self.validate_year_declared_vs_registration()
        except ValueError as e:
            # Agregar el error al campo year_declared
            self.year_declared.errors.append(str(e))
            return False

        return True
