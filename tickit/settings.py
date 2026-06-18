"""
Django settings for tickit project — HelpDesk Pro v2
Compatible with Django 5.1 + Python 3.13
"""
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Environment ────────────────────────────────────────────────────
env = environ.Env(
    DEBUG=(bool, True),
    SLA_HIGH_HOURS=(int, 4),
    SLA_MODERATE_HOURS=(int, 24),
    SLA_LOW_HOURS=(int, 72),
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# SLA hours per priority — change in .env without touching code
SLA_HOURS = {
    'High':     env('SLA_HIGH_HOURS'),
    'Moderate': env('SLA_MODERATE_HOURS'),
    'Low':      env('SLA_LOW_HOURS'),
}

# Twilio — read from .env (no longer hardcoded in models.py)
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN  = env('TWILIO_AUTH_TOKEN',  default='')
TWILIO_FROM_NUMBER = env('TWILIO_FROM_NUMBER', default='')
TWILIO_TO_NUMBER   = env('TWILIO_TO_NUMBER',   default='')

# ── Apps ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Forms
    'crispy_forms',
    'crispy_bootstrap4',       # Django 5.x requires this as separate package

    # Your apps
    'registration',
    'vats',

    # REST API (new in v2)
    'rest_framework',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tickit.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tickit.wsgi.application'

# ── Database (SQLite — same as original) ───────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Auth ───────────────────────────────────────────────────────────
AUTH_USER_MODEL     = 'registration.User'
LOGIN_URL           = 'login'
LOGIN_REDIRECT_URL  = 'home'
LOGOUT_URL          = 'logout'
LOGOUT_REDIRECT_URL = 'login'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Crispy Forms (Django 5.x requires both settings) ──────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# ── Django REST Framework ──────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

# ── Email ──────────────────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = env('EMAIL_HOST_USER',     default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

# ── Static files ───────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']   # your static/ folder with css/main.css
STATIC_ROOT = BASE_DIR / 'staticfiles'     # for collectstatic in production

# ── Misc ───────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
# NOTE: USE_L10N removed — it no longer exists in Django 4.0+, always True
