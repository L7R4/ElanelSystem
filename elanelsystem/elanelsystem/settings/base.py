import os
from pathlib import Path
import environ
from django.urls import reverse_lazy

# ——— Paths & env ———
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
env = environ.Env()
environ.Env.read_env(os.path.join(ROOT_DIR, '.env'))

# ——— Seguridad & debug ———
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', [])

# ——— Apps & middleware ———
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'sales',
    'users',
    'products',
    'liquidacion',
    'configuracion',
    'simple_history',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'elanelsystem.urls'
WSGI_APPLICATION = 'elanelsystem.wsgi.application'

# ——— Templates ———
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [ROOT_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

# ——— Email SMTP ———
EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST         = env('EMAIL_HOST')
EMAIL_PORT         = env.int('EMAIL_PORT')
EMAIL_USE_SSL      = env.bool('EMAIL_USE_SSL')
EMAIL_HOST_USER    = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD= env('EMAIL_HOST_PASSWORD')



# ——— Auth & Usuarios ———
AUTH_USER_MODEL = 'users.Usuario'
AUTHENTICATION_BACKENDS = ['users.backends.EmailBackend']
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]



# ——— Archivos estáticos y media ———
STATIC_URL = '/static/'
STATICFILES_DIRS = [ROOT_DIR / 'static']
STATIC_ROOT = ROOT_DIR.parent / 'staticfiles'
MEDIA_URL = '/public/'
MEDIA_ROOT = ROOT_DIR / 'media'

# ——— Otros ———
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
PDF_STORAGE_DIR = ROOT_DIR / 'pdfs'
LOGOUT_REDIRECT_URL = reverse_lazy('indexLogin')


# ——— Internacionalización ———
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True