import os
from pathlib import Path
import environ
from django.urls import reverse_lazy

# openpyxl usa lxml (si está instalado) para escribir hojas grandes en modo
# write_only. Esa vía puede fallar con errores crípticos tipo "IO_WRITE"
# (código de error de libxml2) en hojas de cientos de miles de filas, como
# las de ESTADOS en los excels de agencias. Forzamos el escritor XML puro
# de Python, que es más lento pero mucho más confiable para esos volúmenes.
# Tiene que setearse ANTES del primer "import openpyxl" en el proceso.
os.environ.setdefault("OPENPYXL_LXML", "False")

# ——— Paths & env ———
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
env = environ.Env()
environ.Env.read_env(os.path.join(ROOT_DIR.parent, '.env'))

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
    'documentos',
    'simple_history',
    'storages',
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

# ——— Supabase Storage (bucket privado, S3-compatible) ———
SUPABASE_S3_ENDPOINT_URL = env('SUPABASE_S3_ENDPOINT_URL', default='')
SUPABASE_S3_REGION = env('SUPABASE_S3_REGION', default='')
SUPABASE_S3_ACCESS_KEY_ID = env('SUPABASE_S3_ACCESS_KEY_ID', default='')
SUPABASE_S3_SECRET_ACCESS_KEY = env('SUPABASE_S3_SECRET_ACCESS_KEY', default='')
SUPABASE_STORAGE_BUCKET = env('SUPABASE_STORAGE_BUCKET', default='documentos')
SUPABASE_SIGNED_URL_EXPIRE = env.int('SUPABASE_SIGNED_URL_EXPIRE', default=3600)


# ——— Internacionalización ———
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True