from enum import Enum

class estadoReseña(Enum):
    """Enumerador para los estados de una reseña de sitio histórico"""

    PENDIENTE = ("pendiente", "Pendiente")
    APROBADA = ("aprobada", "Aprobada")
    RECHAZADA = ("rechazada", "Rechazada")

    def __init__(self, code, label):
        self.code = code
        self.label = label

    @classmethod
    def choices(cls):
        """Retorna las tuplas(valor, nombre) para usar en formularios WTForms"""
        return [(member.code, member.label) for member in cls]

    # @classmethod
    # def get_label(cls, code):
    #     """Obtiene la etiqueta legible para un código dado"""
    #     for status in cls:
    #         if status.code == code:
    #             return status.label
    #     return code