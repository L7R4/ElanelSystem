from .base import *

# —— Producción —— 
DEBUG = False

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
