FROM python:3.11-slim

# 1) Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 2) Instalamos deps del SO, incluyendo las necesarias para WeasyPrint
RUN apt-get update \
    && apt-get install -y \
    build-essential \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libharfbuzz-subset0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libjpeg62-turbo-dev \
    libopenjp2-7-dev \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3) Preparo directorio de la app
WORKDIR /app
ENV PYTHONPATH=/app/elanelsystem:$PYTHONPATH

# 4) Instalo deps de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copio el código
COPY . /app

# 6) Exponer puerto y arrancar
EXPOSE 8000
CMD ["gunicorn", "elanelsystem.wsgi:application", "--workers", "4", "--bind", "0.0.0.0:8000"]

