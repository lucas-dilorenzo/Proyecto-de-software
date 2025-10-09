# Configuración del entorno
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/grupo37
export FLASK_APP=app:create_app
export FLASK_DEBUG=1

# Ejecutar comandos en secuencia
echo "📦 Inicializando la base de datos..."
flask reset-db && \
echo "✅ Base de datos reseteada" && \
flask seed-db && \
echo "✅ Datos iniciales agregados" && \
flask seed-roles && \
echo "✅ Roles configurados" && \
flask seed-users && \
echo "✅ Usuarios creados" && \
echo "🎉 ¡Base de datos configurada correctamente!"