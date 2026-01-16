FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# deps SO (Postgres + WeasyPrint)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    libcairo2 libpango-1.0-0 libpangoft2-1.0-0 \
    libharfbuzz0b libharfbuzz-subset0 \
    libgdk-pixbuf-2.0-0 shared-mime-info \
    curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# deps python (cache)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# código
COPY . /app

# IMPORTANTÍSIMO: tu manage.py está en /app/elanelsystem
WORKDIR /app/elanelsystem

# usuario no root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# gunicorn usando TU wsgi (que ya fija DJANGO_SETTINGS_MODULE=elanelsystem.settings.prod)
CMD ["bash", "-lc", "gunicorn elanelsystem.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 120"]