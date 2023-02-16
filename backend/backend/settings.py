"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ['*']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# The tracking service is deployed behind reverse NGINX proxies.
# Therefore, we set the admin url here so that it redirects to the correct browser path. 
# By default, the admin site will be accessible under admin/
APP_URL = os.environ.get('APP_URL', '')
FORCE_SCRIPT_NAME = APP_URL

# When this is not set, django gives a 403 error after attempting to login
CSRF_TRUSTED_ORIGIN = os.environ.get('CSRF_TRUSTED_ORIGIN', '')
if CSRF_TRUSTED_ORIGIN:
    CSRF_TRUSTED_ORIGINS = [CSRF_TRUSTED_ORIGIN]
else:
    CSRF_TRUSTED_ORIGINS = []

# SECURITY WARNING: keep the secret key used in production secret!
if DEBUG:
    SECRET_KEY = "django-insecure-h4wvbex$t4k_adc#55mqy3d5x($(8qo5=-c_3x81vbrw*0u5pc"
else:
    SECRET_KEY = os.environ.get('DJANGO_KEY')

# SECURITY WARNING: keep the API key used in production secret!
API_KEY = os.environ.get('API_KEY', 'secret')

# Application definition

INSTALLED_APPS = [
    'tracks',
    'answers',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
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

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            # PostGIS database
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            
            'NAME': os.environ.get('POSTGRES_NAME'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST'),
            'PORT': os.environ.get('POSTGRES_PORT'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Africa/Mbabane'

USE_I18N = True

USE_TZ = True

# Configure under which URL the admin interface will be provided.
ADMIN_URL = 'admin/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = f'{APP_URL}static/'

# Collect static files in deployment so that NGINX can access them.
STATIC_ROOT =  os.path.join(BASE_DIR, 'static')

# Security warning: don't expose the media folder to the internet.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
