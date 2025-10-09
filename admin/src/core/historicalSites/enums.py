from enum import Enum


class ConservationStatus(Enum):
    """Enumerador para los estados de conservación de sitios históricos"""

    EXCELENTE = ("excelente", "Excelente")
    BUENO = ("bueno", "Bueno")
    REGULAR = ("regular", "Regular")
    MALO = ("malo", "Malo")
    CRITICO = ("critico", "Crítico")
    EN_RESTAURACION = ("en_restauracion", "En restauración")

    def __init__(self, code, label):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls):
        """Retorna las opciones para usar en formularios WTForms"""
        return [("", "Seleccione un estado")] + [
            (status.code, status.label) for status in cls
        ]

    @classmethod
    def get_label(cls, code):
        """Obtiene la etiqueta legible para un código dado"""
        for status in cls:
            if status.code == code:
                return status.label
        return code


class SiteCategory(Enum):
    """Enumerador para las categorías de sitios históricos"""

    MONUMENTO_NACIONAL = ("monumento_nacional", "Monumento Nacional")
    SITIO_HISTORICO = ("sitio_historico", "Sitio Histórico")
    BIEN_CULTURAL = ("bien_cultural", "Bien Cultural")
    PATRIMONIO_MUNDIAL = ("patrimonio_mundial", "Patrimonio Mundial")
    MONUMENTO_HISTORICO_NACIONAL = (
        "monumento_historico_nacional",
        "Monumento Histórico Nacional",
    )
    LUGAR_HISTORICO_NACIONAL = ("lugar_historico_nacional", "Lugar Histórico Nacional")

    def __init__(self, code, label):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls):
        """Retorna las opciones para usar en formularios WTForms"""
        return [("", "Seleccione una categoría")] + [
            (category.code, category.label) for category in cls
        ]

    @classmethod
    def get_label(cls, code):
        """Obtiene la etiqueta legible para un código dado"""
        for category in cls:
            if category.code == code:
                return category.label
        return code
