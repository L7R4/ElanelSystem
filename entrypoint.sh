#!/usr/bin/env sh
echo "===== Estructura de /app ====="
ls -R /app
echo "===== Fin de estructura ====="

# Ahora ejecuta el comando original
exec "$@"
