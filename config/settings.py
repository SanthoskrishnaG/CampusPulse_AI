"""
Django settings for CampusPulse AI platform.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
env_path = BASE_DIR / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

SECRET_KEY = os.environ.get('SECRET_KEY', 'campuspulse-development-secret-key-2026')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',

    # CampusPulse Core Apps
    'apps.accounts',
    'apps.common',
    'apps.departments',
    'apps.faculty',
    'apps.students',
    'apps.academics',
    'apps.clubs',
    'apps.events',
    'apps.complaints',
    'apps.transport',
    'apps.traffic',
    'apps.parking',
    'apps.canteen',
    'apps.energy',
    'apps.waste',
    'apps.projects',
    'apps.recommendations',
    'apps.notifications',
    'apps.analytics',
    'apps.ai_assistant',
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

ROOT_URLCONF = 'config.urls'

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
                'apps.common.context_processors.campus_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Dual-Engine Database Configuration (MySQL 8.x with zero-friction SQLite fallback)
use_mysql = os.environ.get('USE_MYSQL', 'False').lower() in ('true', '1', 't')
mysql_connected = False

if use_mysql:
    try:
        import pymysql
        conn = pymysql.connect(
            host=os.environ.get('DB_HOST', '127.0.0.1'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            port=int(os.environ.get('DB_PORT', 3306)),
            connect_timeout=2
        )
        conn.close()
        mysql_connected = True
    except Exception as e:
        print(f"[CampusPulse Notice] MySQL requested but unavailable ({e}). Falling back smoothly to SQLite.")
        mysql_connected = False

if use_mysql and mysql_connected:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'campuspulse_db'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'campuspulse.sqlite3',
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media uploads (Images, CSVs, Waste photos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:role_redirect'
LOGOUT_REDIRECT_URL = 'common:home'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

# Centralized Campus Configuration (Coimbatore Institute of Technology)
from config.campus_config import CAMPUS_CONFIG

CAMPUS_CONFIG = CAMPUS_CONFIG
CAMPUS_NAME = os.environ.get('CAMPUS_NAME', CAMPUS_CONFIG['name'])
CAMPUS_SHORT_NAME = CAMPUS_CONFIG['short_name']
CAMPUS_LAT = CAMPUS_CONFIG['latitude']
CAMPUS_LNG = CAMPUS_CONFIG['longitude']
WEATHER_API_BASE_URL = os.environ.get('WEATHER_API_BASE_URL', 'https://api.open-meteo.com/v1/forecast')

