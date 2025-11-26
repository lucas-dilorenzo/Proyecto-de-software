# Google OAuth Integration - Guía de Implementación

## Configuración Completada

### 1. Dependencias

- Se ha configurado **Authlib** para OAuth 2.0
- Asegúrate de instalarlo: `pip install Authlib`

### 2. Configuración en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea o selecciona un proyecto
3. Habilita **Google+ API** (o People API)
4. Ve a **Credenciales** → **Crear credenciales** → **ID de cliente de OAuth 2.0**
5. Tipo de aplicación: **Aplicación web**
6. Configura las URIs de redirección autorizadas:

   - **Desarrollo**: `http://localhost:5000/api/auth/google/callback`
   - **Producción**: `https://tu-dominio.com/api/auth/google/callback`

7. Copia el **Client ID** y **Client Secret**
8. Agrégalos a tu configuración:

```python
# En config.py (ProductionConfig o DevelopmentConfig)
GOOGLE_CLIENT_ID = "tu-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "tu-client-secret"
```

## Flujos Implementados

### Parte Privada (Admin - Flask + Sesiones)

- **Login nativo**: `/auth/login` (ya implementado)
- Usa sesiones de Flask tradicionales
- No afectado por Google OAuth

### Parte Pública (API - Vue + JWT)

#### A) Login Nativo JWT (ya existente)

```
POST /api/auth/login_jwt
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña"
}

Response 201:
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "user_id": 123
}
```

#### B) Login con Google OAuth (NUEVO)

**Paso 1: Iniciar autenticación**

```
GET /api/auth/google/login
```

- Redirige al usuario a Google para autenticarse
- El usuario autoriza la aplicación

**Paso 2: Callback automático**

```
GET /api/auth/google/callback
```

- Google redirige aquí después de la autorización
- **Automáticamente**:
  - Si el usuario **existe**: genera JWT y devuelve token
  - Si **NO existe**: crea usuario con rol PUBLIC y devuelve JWT

**Response (201)**:

```json
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "user_id": 456,
  "message": "Login exitoso con Google"
}
```

**Response (401) - Error**:

```json
{
  "message": "Usuario bloqueado"
}
```

### C) Logout JWT (ya existente)

```
GET /api/auth/logout_jwt
```

### D) Obtener usuario autenticado (ya existente)

```
GET /api/auth/user_jwt
```

## Integración con Vue (Frontend)

### Ejemplo de implementación en Vue:

```javascript
// Google OAuth Login
async function loginWithGoogle() {
  // Redirigir a la ruta de inicio de OAuth
  window.location.href = "http://localhost:5000/api/auth/google/login";
}

// En el callback, capturar el token
// Opción 1: Si usas cookies (JWT_COOKIE)
// El token ya estará en las cookies automáticamente

// Opción 2: Si prefieres manejar el token manualmente
// Necesitas modificar el callback para redirigir a tu frontend con el token:
// /api/auth/google/callback?token=xxx
```

### Flujo recomendado para Vue:

1. **Usuario hace clic en "Login con Google"**
2. **Redirigir a**: `http://tu-backend.com/api/auth/google/login`
3. **Google autentica al usuario**
4. **Callback automático**: `/api/auth/google/callback`
5. **Backend**:
   - Verifica/crea usuario
   - Genera JWT
   - **Opción A**: Establece cookie con JWT y redirige a frontend
   - **Opción B**: Redirige a frontend con token en query param

### Opción A: Usando cookies (recomendado)

```python
# Ya está configurado en tu app:
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"
```

Tu Vue simplemente hace las peticiones y el token se envía automáticamente:

```javascript
// En axios
axios.defaults.withCredentials = true;

// Las peticiones funcionan igual que con login nativo
const response = await axios.get("/api/auth/user_jwt");
```

### Opción B: Token en URL (si prefieres control manual)

Modificar el callback para redirigir a tu frontend:

```python
# En /api/auth/google/callback, después de generar el token:
frontend_url = "http://localhost:3000/auth/callback"
return redirect(f"{frontend_url}?token={access_token}&user_id={user.id}")
```

Y en Vue capturar el token:

```javascript
// En la ruta /auth/callback de Vue
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get("token");
const userId = urlParams.get("user_id");

// Guardar en localStorage o Vuex
localStorage.setItem("access_token", token);

// Redirigir al home
router.push("/");
```

## Auto-registro de Usuarios

Cuando un usuario se autentica con Google por primera vez:

1. Se verifica si existe un usuario con ese email
2. Si **NO existe**, se crea automáticamente:

   - **Email**: del perfil de Google
   - **Nombre**: `given_name` de Google
   - **Apellido**: `family_name` de Google
   - **Rol**: `PUBLIC` por defecto
   - **Activo**: `True`
   - **Password**: hash del email (no se usará, solo login con Google)

3. Si **existe**, simplemente hace login y genera JWT

## Compatibilidad con Sistema Actual

✅ **Totalmente compatible** con tu sistema JWT existente:

- Genera el mismo tipo de JWT que el login nativo
- Usa `create_access_token(identity=str(user.id))`
- Compatible con `@jwt_required()` decorators
- Compatible con `get_jwt_identity()` en todas las rutas protegidas
- Las rutas `/api/auth/user_jwt` y `/api/auth/logout_jwt` funcionan igual

## Testing

### Probar manualmente:

1. Asegúrate de tener las credenciales de Google configuradas
2. Inicia tu servidor Flask
3. En el navegador, ve a: `http://localhost:5000/api/auth/google/login`
4. Autentica con tu cuenta de Google
5. Deberías recibir el JSON con el token

### Con curl (después del callback):

```bash
# Verificar usuario autenticado
curl -X GET http://localhost:5000/api/auth/user_jwt \
  --cookie "access_token_cookie=TU_TOKEN_AQUI"
```

## Variables de Entorno (Recomendado para Producción)

```bash
# .env o variables de sistema
export GOOGLE_CLIENT_ID="tu-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="tu-client-secret"
```

Y en `config.py`:

```python
from os import environ

class ProductionConfig(Config):
    GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = environ.get("GOOGLE_CLIENT_SECRET")
```

## Seguridad

⚠️ **IMPORTANTE**:

- Nunca subas las credenciales de Google al repositorio
- Usa variables de entorno en producción
- Configura correctamente las URIs autorizadas en Google Cloud
- En producción, habilita `JWT_COOKIE_SECURE = True` (requiere HTTPS)
- Considera habilitar `JWT_COOKIE_CSRF_PROTECT = True` en producción

## Próximos Pasos

1. ✅ Instalar Authlib: `pip install Authlib`
2. ✅ Configurar credenciales en Google Cloud Console
3. ✅ Agregar credenciales a `config.py`
4. ✅ Implementar botón "Login con Google" en Vue
5. ✅ Manejar el callback en tu frontend
6. ✅ Probar el flujo completo
