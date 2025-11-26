-- Agregar columna profile_picture a la tabla users
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500);

-- Comentario sobre la columna
COMMENT ON COLUMN users.profile_picture IS 'URL de la imagen de perfil del usuario (generalmente de Google OAuth)';
