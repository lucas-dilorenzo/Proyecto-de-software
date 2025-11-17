# Guía de Autenticación para API REST

## Tipos de Decoradores Disponibles

### 1. `@api_auth_required`
**Uso**: Endpoints que requieren autenticación obligatoria
**Retorna**: 401 Unauthorized si no está autenticado

```python
@api_bp.route("/protected-endpoint", methods=["GET"])
@api_auth_required
def protected_endpoint():
    # Solo usuarios autenticados pueden acceder
    return jsonify({"message": "Hello authenticated user!"})
```

### 2. `@api_permission_required(UserPermission.PERMISO)`
**Uso**: Endpoints que requieren un permiso específico
**Retorna**: 
- 401 Unauthorized si no está autenticado
- 403 Forbidden si no tiene el permiso

```python
@api_bp.route("/admin/users", methods=["GET"])
@api_permission_required(UserPermission.USER_INDEX)
def list_users_admin():
    # Solo usuarios con permiso USER_INDEX pueden acceder
    return jsonify({"users": []})
```

### 3. `@api_optional_auth`
**Uso**: Endpoints donde la autenticación es opcional
**Comportamiento**: Pasa información del usuario en kwargs si está autenticado

```python
@api_bp.route("/public-content", methods=["GET"])
@api_optional_auth
def public_content(**kwargs):
    is_auth = kwargs.get('is_authenticated', False)
    user_id = kwargs.get('current_user_id')
    
    if is_auth:
        return jsonify({"message": f"Hello user {user_id}!"})
    else:
        return jsonify({"message": "Hello anonymous user!"})
```

### 4. `@api_token_auth_required`
**Uso**: Autenticación por token en header Authorization
**Header**: `Authorization: Bearer <token>`

```python
@api_bp.route("/external-api", methods=["GET"])
@api_token_auth_required
def external_api():
    # Para clientes externos con token
    return jsonify({"data": "sensitive info"})
```

## Códigos de Error Estándar

### 401 Unauthorized
```json
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication required"
  }
}
```

### 403 Forbidden
```json
{
  "error": {
    "code": "forbidden", 
    "message": "Insufficient permissions"
  }
}
```

### 404 Not Found
```json
{
  "error": {
    "code": "not_found",
    "message": "Resource not found"
  }
}
```

### 400 Bad Request
```json
{
  "error": {
    "code": "invalid_data",
    "message": "Invalid input data",
    "details": {
      "field": ["Error message"]
    }
  }
}
```

## Ejemplos de Uso en tu API

### Endpoint Público (sin autenticación)
```python
@api_bp.route("/sites", methods=["GET"])
def list_sites():
    # Cualquiera puede ver sitios públicos
    return jsonify({"sites": []})
```

### Endpoint Semi-Público (autenticación opcional)
```python
@api_bp.route("/sites/<int:site_id>/reviews", methods=["GET"]) 
@api_optional_auth
def get_site_reviews(site_id, **kwargs):
    is_auth = kwargs.get('is_authenticated', False)
    
    if is_auth:
        # Mostrar todas las reseñas
        reviews = get_all_reviews(site_id)
    else:
        # Solo reseñas aprobadas
        reviews = get_approved_reviews(site_id)
    
    return jsonify({"reviews": reviews})
```

### Endpoint Protegido (requiere autenticación)
```python
@api_bp.route("/sites/<int:site_id>/reviews", methods=["POST"])
@api_auth_required
def create_review(site_id):
    # Solo usuarios logueados pueden crear reseñas
    user_id = session.get("user_id")
    # ... crear reseña ...
    return jsonify({"message": "Review created"})
```

### Endpoint Administrativo (requiere permisos)
```python
@api_bp.route("/admin/reviews/<int:review_id>/approve", methods=["PUT"])
@api_permission_required(UserPermission.REVIEW_MODERATE)
def approve_review(review_id):
    # Solo moderadores/admins pueden aprobar
    # ... lógica de aprobación ...
    return jsonify({"message": "Review approved"})
```

## Testing con curl

### Endpoint público
```bash
curl -X GET http://localhost:5000/api/sites
```

### Endpoint protegido (sin autenticación - error 401)
```bash
curl -X POST http://localhost:5000/api/sites/1/reviews
# Retorna: {"error": {"code": "unauthorized", "message": "Authentication required"}}
```

### Endpoint con token
```bash
curl -X GET \
  -H "Authorization: Bearer your-api-token-here" \
  http://localhost:5000/api/external-endpoint
```

### Endpoint con sesión (requiere login previo)
```bash
# Primero login
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}' \
  -c cookies.txt \
  http://localhost:5000/auth/login

# Luego usar endpoint protegido
curl -X POST \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"rating":5,"comment":"Great site!"}' \
  http://localhost:5000/api/sites/1/reviews
```