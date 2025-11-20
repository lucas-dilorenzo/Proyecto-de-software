"""
Tests para las validaciones de imágenes
"""

import pytest
from io import BytesIO
from werkzeug.datastructures import FileStorage
from src.web.helpers.validations.images import (
    allowed_file,
    validate_file_size,
    validate_image,
    validate_images_count,
    validate_images_batch,
    get_allowed_extensions_str,
    get_max_file_size_mb,
    MAX_FILE_SIZE,
    MAX_IMAGES_PER_SITE,
)


class TestAllowedFile:
    """Tests para la validación de extensiones permitidas"""

    def test_allowed_extensions(self):
        """Verifica que las extensiones permitidas sean aceptadas"""
        assert allowed_file("image.jpg") is True
        assert allowed_file("image.jpeg") is True
        assert allowed_file("image.png") is True
        assert allowed_file("image.webp") is True
        assert allowed_file("IMAGE.JPG") is True  # Case insensitive

    def test_disallowed_extensions(self):
        """Verifica que las extensiones no permitidas sean rechazadas"""
        assert allowed_file("image.gif") is False
        assert allowed_file("image.bmp") is False
        assert allowed_file("image.svg") is False
        assert allowed_file("document.pdf") is False
        assert allowed_file("script.py") is False

    def test_no_extension(self):
        """Verifica que archivos sin extensión sean rechazados"""
        assert allowed_file("image") is False
        assert allowed_file("") is False
        assert allowed_file(None) is False


class TestValidateFileSize:
    """Tests para la validación de tamaño de archivo"""

    def test_file_within_size_limit(self):
        """Verifica que archivos dentro del límite sean aceptados"""
        # Crear un archivo de 1 MB
        file_content = b"0" * (1 * 1024 * 1024)
        file = FileStorage(
            stream=BytesIO(file_content), filename="test.jpg", content_type="image/jpeg"
        )

        is_valid, error = validate_file_size(file)
        assert is_valid is True
        assert error == ""

    def test_file_exceeds_size_limit(self):
        """Verifica que archivos que excedan el límite sean rechazados"""
        # Crear un archivo de 6 MB (excede el límite de 5 MB)
        file_content = b"0" * (6 * 1024 * 1024)
        file = FileStorage(
            stream=BytesIO(file_content),
            filename="large.jpg",
            content_type="image/jpeg",
        )

        is_valid, error = validate_file_size(file)
        assert is_valid is False
        assert "excede el tamaño máximo" in error
        assert "6.00 MB" in error

    def test_file_at_size_limit(self):
        """Verifica que archivos exactamente en el límite sean aceptados"""
        # Crear un archivo de exactamente 5 MB
        file_content = b"0" * (5 * 1024 * 1024)
        file = FileStorage(
            stream=BytesIO(file_content),
            filename="exact.jpg",
            content_type="image/jpeg",
        )

        is_valid, error = validate_file_size(file)
        assert is_valid is True
        assert error == ""


class TestValidateImage:
    """Tests para la validación completa de imagen"""

    def test_valid_image(self):
        """Verifica que una imagen válida sea aceptada"""
        file_content = b"0" * (1 * 1024 * 1024)  # 1 MB
        file = FileStorage(
            stream=BytesIO(file_content),
            filename="valid.jpg",
            content_type="image/jpeg",
        )

        is_valid, error = validate_image(file)
        assert is_valid is True
        assert error == ""

    def test_invalid_extension(self):
        """Verifica que una extensión inválida sea rechazada"""
        file_content = b"0" * (1 * 1024 * 1024)
        file = FileStorage(
            stream=BytesIO(file_content),
            filename="invalid.gif",
            content_type="image/gif",
        )

        is_valid, error = validate_image(file)
        assert is_valid is False
        assert "Formato no permitido" in error

    def test_oversized_image(self):
        """Verifica que una imagen demasiado grande sea rechazada"""
        file_content = b"0" * (6 * 1024 * 1024)  # 6 MB
        file = FileStorage(
            stream=BytesIO(file_content),
            filename="large.jpg",
            content_type="image/jpeg",
        )

        is_valid, error = validate_image(file)
        assert is_valid is False
        assert "excede el tamaño máximo" in error


class TestValidateImagesCount:
    """Tests para la validación de cantidad de imágenes"""

    def test_within_limit(self):
        """Verifica que se acepten cantidades dentro del límite"""
        is_valid, error = validate_images_count(5, 3)
        assert is_valid is True
        assert error == ""

    def test_exceeds_limit(self):
        """Verifica que se rechacen cantidades que excedan el límite"""
        is_valid, error = validate_images_count(8, 5)
        assert is_valid is False
        assert f"no puede tener más de {MAX_IMAGES_PER_SITE}" in error

    def test_at_limit(self):
        """Verifica que se acepten cantidades exactamente en el límite"""
        is_valid, error = validate_images_count(7, 3)
        assert is_valid is True
        assert error == ""

    def test_zero_images(self):
        """Verifica el caso de cero imágenes"""
        is_valid, error = validate_images_count(0, 5)
        assert is_valid is True
        assert error == ""


class TestValidateImagesBatch:
    """Tests para la validación de lotes de imágenes"""

    def test_valid_batch(self):
        """Verifica que un lote válido sea aceptado"""
        files = []
        for i in range(3):
            file_content = b"0" * (1 * 1024 * 1024)  # 1 MB cada una
            file = FileStorage(
                stream=BytesIO(file_content),
                filename=f"image{i}.jpg",
                content_type="image/jpeg",
            )
            files.append(file)

        is_valid, errors = validate_images_batch(files, 0)
        assert is_valid is True
        assert len(errors) == 0

    def test_batch_with_invalid_file(self):
        """Verifica que un lote con archivo inválido sea rechazado"""
        files = [
            FileStorage(
                stream=BytesIO(b"0" * (1 * 1024 * 1024)),
                filename="valid.jpg",
                content_type="image/jpeg",
            ),
            FileStorage(
                stream=BytesIO(b"0" * (1 * 1024 * 1024)),
                filename="invalid.gif",
                content_type="image/gif",
            ),
        ]

        is_valid, errors = validate_images_batch(files, 0)
        assert is_valid is False
        assert len(errors) > 0
        assert "invalid.gif" in errors[0]

    def test_batch_exceeds_total_limit(self):
        """Verifica que un lote que exceda el límite total sea rechazado"""
        files = []
        for i in range(8):
            file_content = b"0" * (1 * 1024 * 1024)
            file = FileStorage(
                stream=BytesIO(file_content),
                filename=f"image{i}.jpg",
                content_type="image/jpeg",
            )
            files.append(file)

        is_valid, errors = validate_images_batch(files, 5)
        assert is_valid is False
        assert len(errors) > 0
        assert "no puede tener más de" in errors[0]


class TestHelperFunctions:
    """Tests para funciones auxiliares"""

    def test_get_allowed_extensions_str(self):
        """Verifica que se retornen las extensiones permitidas como string"""
        extensions = get_allowed_extensions_str()
        assert isinstance(extensions, str)
        assert "JPG" in extensions
        assert "PNG" in extensions
        assert "WEBP" in extensions

    def test_get_max_file_size_mb(self):
        """Verifica que se retorne el tamaño máximo en MB"""
        size = get_max_file_size_mb()
        assert size == 5
        assert isinstance(size, int)
