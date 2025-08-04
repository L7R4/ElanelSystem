# Stage 1: Base build stage
FROM python:3.11-slim

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Dependencias del OS para psycopg2
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create the app directory
RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD [
"gunicorn",
"elanelasystem.wsgi:application",
"--workers", "3",
"--bind", "0.0.0.0:8000"
]

