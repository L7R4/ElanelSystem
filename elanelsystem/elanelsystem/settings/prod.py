from .base import *

# —— Producción —— 
DEBUG = True

CSRF_TRUSTED_ORIGINS = [
    "https://elanelsys.com",
    "https://www.elanelsys.com",
    "https://site.elanelsys.com",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True  # opcional pero suele ayudar detrás de proxy

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# BD real (Postgres, MySQL…)
DATABASES = {
    'default': {
        'ENGINE':   env('DB_ENGINE'),
        'NAME':     env('DB_NAME'),
        'USER':     env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST':     env('DB_HOST'),
        'PORT':     env('DB_PORT'),
    }
}
