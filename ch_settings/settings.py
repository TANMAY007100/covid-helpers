"""
Django settings for ch_settings project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from typing import cast
from decouple import config
from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ADMIN_URL = config('ADMIN_URL', 'admin')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', 'qwertypass')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', False, cast=bool)

ALLOWED_HOSTS = [eaddress for eaddress in config('ALLOWED_HOSTS', 'localhost').split(',')]

MESSAGE_TAGS = {
    message_constants.DEBUG: 'bg-gray-500',
    message_constants.INFO: 'bg-blue-500',
    message_constants.SUCCESS: 'bg-green-500',
    message_constants.WARNING: 'bg-yellow-500',
    message_constants.ERROR: 'bg-red-500',
}

IS_HEROKU = config('IS_HEROKU', False, cast=bool)

REDIS_HOST = config('REDIS_HOST', 'lcoalhost')
REDIS_PORT = config('REDIS_PORT', '6379')
REDIS_PASSWORD = config('REDIS_PASSWORD', 'pass')
REDIS_DB = config('REDIS_DB', '0')

REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main.apps.MainConfig'
]

if IS_HEROKU:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
else:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

ROOT_URLCONF = 'ch_settings.urls'

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

WSGI_APPLICATION = 'ch_settings.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

AUTH_USER_MODEL = 'main.User'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME', 'django_db'),
        'USER': config('DATABASE_USER', 'admin'),
        'PASSWORD': config('DATABASE_PASSWORD', 'admin'),
        'HOST': config('DATABASE_HOST', 'localhost'),
        'PORT': 5432
    }
}

#
AUTHENTICATION_BACKENDS = [
    # Needed to login by username and password in Django
    "django.contrib.auth.backends.ModelBackend",
    "main.backends.custom_backends.CustomAuthenticationBackend",
]

LOGIN_URL = '/login'

LOGOUT_REDIRECT_URL = '/'

LOGIN_REDIRECT_URL = '/'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static'

# MongoDB Settings

MONGODB_USER = config('MONGODB_USER', 'admin')
MONGODB_PASSWORD = config('MONGODB_PASSWORD', 'admin')
MONGODB_CLUSTER_ADDRESS = config('MONGODB_CLUSTER_ADDRESS', 'localhost')
MONGODB_DATABASE_NAME = config('MONGODB_DATABASE_NAME', 'local_db')
MONGODB_COLLECTION = config('MONGODB_COLLECTION', 'mongo_collect')

# Celery Settings

CELERY_TIMEZONE = "Asia/Kolkata"
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'general': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}