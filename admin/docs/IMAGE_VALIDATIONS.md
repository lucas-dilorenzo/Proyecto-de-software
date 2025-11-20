# Validaciones de Imágenes para Sitios Históricos

## Descripción

Este módulo implementa validaciones tanto del lado del servidor (backend) como del cliente (frontend) para la carga de imágenes en el sistema de gestión de sitios históricos.

## Restricciones Implementadas

### 1. Formatos Permitidos

- **JPG / JPEG**
- **PNG**
- **WEBP**

### 2. Tamaño Máximo por Archivo

- **5 MB** por imagen

### 3. Límite Total de Imágenes

- **10 imágenes máximo** por sitio histórico (incluyendo la imagen principal)

## Estructura del Código

### Backend (Python/Flask)

#### Módulo de Validaciones

**Archivo:** `src/web/helpers/validations/images.py`

Funciones principales:

- `allowed_file(filename)`: Verifica si la extensión del archivo es permitida
- `validate_file_size(file)`: Valida que el archivo no exceda el tamaño máximo
- `validate_image(file)`: Validación completa de una imagen individual
- `validate_images_count(current_count, new_count)`: Valida el número total de imágenes
- `validate_images_batch(files, current_images_count)`: Valida un lote de imágenes

#### Controlador

**Archivo:** `src/web/controllers/sites.py`

Las validaciones se aplican en:

- `create_site()`: Al crear un nuevo sitio
- `edit_site()`: Al editar un sitio existente

### Frontend (JavaScript)

#### Templates

Las validaciones del lado del cliente están implementadas en:

- `src/web/templates/historicalSites/create_site.html`
- `src/web/templates/historicalSites/edit_site.html`

Funciones JavaScript:

- `validateImageFile(file)`: Valida extensión y tamaño de un archivo
- `countCurrentImages()`: Cuenta las imágenes actuales (solo en edición)

## Flujo de Validación

### Creación de Sitio

1. **Frontend**: Validación al seleccionar archivos

   - Verifica formato y tamaño antes de mostrar preview
   - Alerta al usuario inmediatamente si hay errores
   - Previene la selección de archivos inválidos

2. **Backend**: Validación al enviar formulario
   - Valida cada imagen individual (formato y tamaño)
   - Verifica el límite total de imágenes
   - Si hay errores, muestra mensajes flash y no crea el sitio
   - Solo procede si todas las validaciones pasan

### Edición de Sitio

1. **Frontend**: Validación al agregar nuevas imágenes

   - Cuenta imágenes existentes
   - Resta imágenes marcadas para eliminar
   - Valida que el total no exceda el límite
   - Alerta al usuario si hay problemas

2. **Backend**: Validación al actualizar
   - Calcula: `imágenes_actuales - imágenes_a_eliminar + imágenes_nuevas`
   - Verifica que el resultado no exceda el límite
   - Valida cada imagen nueva individualmente
   - Si hay errores, redirige con mensajes flash

## Mensajes de Error

### Formato no permitido

```
Formato no permitido. Solo se aceptan: JPG, JPEG, PNG, WEBP
```

### Tamaño excedido

```
El archivo excede el tamaño máximo permitido de 5 MB (tamaño: X.XX MB)
```

### Límite de imágenes excedido

```
El sitio no puede tener más de 10 imágenes. Actualmente tiene X y está intentando agregar Y
```

## Uso en Templates

### Indicadores Visuales

Ambos templates muestran información clara sobre las restricciones:

```html
<div class="form-text">
  Sube la imagen principal (se mostrará como portada).<br />
  <strong>Formatos permitidos:</strong> JPG, PNG, WEBP |
  <strong>Tamaño máximo:</strong> 5 MB
</div>
```

### Atributo accept en inputs

Los inputs de archivo están configurados para sugerir solo los formatos permitidos:

```html
<input type="file" accept=".jpg,.jpeg,.png,.webp" />
```

## Testing

### Ejecutar Tests

```bash
cd admin
pytest tests/test_image_validations.py -v
```

### Cobertura de Tests

Los tests cubren:

- ✅ Validación de extensiones permitidas
- ✅ Validación de extensiones no permitidas
- ✅ Validación de tamaño de archivo
- ✅ Validación de límite de imágenes
- ✅ Validación de lotes de imágenes
- ✅ Funciones auxiliares

## Configuración

Las constantes de configuración están centralizadas en `images.py`:

```python
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB en bytes
MAX_IMAGES_PER_SITE = 10
```

Para modificar los límites, edita estas constantes y las correspondientes en JavaScript.

## Mejoras Futuras

Posibles mejoras a considerar:

1. **Validación de dimensiones**: Agregar límites de ancho/alto
2. **Compresión automática**: Redimensionar imágenes grandes automáticamente
3. **Validación de tipo MIME**: Verificar el tipo real del archivo más allá de la extensión
4. **Optimización**: Convertir automáticamente a WebP para mejor rendimiento
5. **Configuración dinámica**: Permitir configurar límites desde admin
6. **Vista previa mejorada**: Mostrar información detallada de cada imagen antes de subir

## Soporte

Para reportar problemas o sugerir mejoras, contactar al equipo de desarrollo.
