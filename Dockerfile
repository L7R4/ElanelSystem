# 1. Base
FROM python:3.11-slim

# 2. Variables de entorno
ENV PYTHONUNBUFFERED 1 \
    POETRY_VIRTUALENVS_CREATE=false

# 3. Directorio de trabajo
WORKDIR /app

# 4. Instala dependencias
COPY proyecto_django/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia el código
COPY proyecto_django/ .

# 6. Recolecta estáticos (opcionalmente en build)
# RUN python manage.py collectstatic --noinput

# 7. Comando por defecto
CMD ["uvicorn", "mi_proyecto.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
