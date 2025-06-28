from .base import *

# —— Sólo para desarrollo —— 
DEBUG = True

# BD ligera (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ROOT_DIR / 'db.sqlite3',
    }
}