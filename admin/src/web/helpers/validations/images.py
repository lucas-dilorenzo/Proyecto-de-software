"""
Validaciones para carga de imágenes
"""

from werkzeug.datastructures import FileStorage
from typing import List, Tuple


# Configuración de validaciones
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB en bytes
MAX_IMAGES_PER_SITE = 10


def allowed_file(filename: str) -> bool:
    """
    Verifica si el archivo tiene una extensión permitida.

    Args:
        filename: Nombre del archivo

    Returns:
        True si la extensión es permitida, False en caso contrario
    """
    if not filename:
        return False
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_size(file: FileStorage) -> Tuple[bool, str]:
    """
    Valida el tamaño del archivo.

    Args:
        file: Archivo a validar

    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not file:
        return False, "No se proporcionó ningún archivo"

    # Obtener el tamaño del archivo
    file.seek(0, 2)  # Ir al final del archivo
    file_size = file.tell()
    file.seek(0)  # Volver al inicio

    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        return (
            False,
            f"El archivo excede el tamaño máximo permitido de 5 MB (tamaño: {size_mb:.2f} MB)",
        )

    return True, ""


def validate_image(file: FileStorage) -> Tuple[bool, str]:
    """
    Valida una imagen individual (extensión y tamaño).

    Args:
        file: Archivo de imagen a validar

    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not file or not file.filename:
        return False, "No se proporcionó ningún archivo"

    # Validar extensión
    if not allowed_file(file.filename):
        return (
            False,
            f"Formato no permitido. Solo se aceptan: {', '.join(ALLOWED_EXTENSIONS).upper()}",
        )

    # Validar tamaño
    is_valid_size, size_error = validate_file_size(file)
    if not is_valid_size:
        return False, size_error

    return True, ""


def validate_images_count(current_count: int, new_count: int) -> Tuple[bool, str]:
    """
    Valida que el número total de imágenes no exceda el límite.

    Args:
        current_count: Número de imágenes actuales del sitio
        new_count: Número de imágenes nuevas a agregar

    Returns:
        Tupla (es_válido, mensaje_error)
    """
    total = current_count + new_count

    if total > MAX_IMAGES_PER_SITE:
        return (
            False,
            f"El sitio no puede tener más de {MAX_IMAGES_PER_SITE} imágenes. Actualmente tiene {current_count} y está intentando agregar {new_count}",
        )

    return True, ""


def validate_images_batch(
    files: List[FileStorage], current_images_count: int = 0
) -> Tuple[bool, List[str]]:
    """
    Valida un lote de imágenes.

    Args:
        files: Lista de archivos a validar
        current_images_count: Número de imágenes que ya tiene el sitio

    Returns:
        Tupla (todas_válidas, lista_de_errores)
    """
    errors = []

    # Validar cantidad total
    new_count = len([f for f in files if f and f.filename])
    is_valid_count, count_error = validate_images_count(current_images_count, new_count)
    if not is_valid_count:
        errors.append(count_error)
        return False, errors

    # Validar cada archivo
    for idx, file in enumerate(files):
        if file and file.filename:
            is_valid, error = validate_image(file)
            if not is_valid:
                errors.append(f"Imagen {idx + 1} ({file.filename}): {error}")

    return len(errors) == 0, errors


def get_allowed_extensions_str() -> str:
    """
    Retorna una cadena con las extensiones permitidas para mostrar en formularios.

    Returns:
        String con extensiones separadas por comas
    """
    return ", ".join(sorted(ALLOWED_EXTENSIONS)).upper()


def get_max_file_size_mb() -> int:
    """
    Retorna el tamaño máximo de archivo en MB.

    Returns:
        Tamaño máximo en MB
    """
    return MAX_FILE_SIZE // (1024 * 1024)
