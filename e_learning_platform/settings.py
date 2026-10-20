"""
Django settings for e_learning_platform project.

This file contains all configuration settings for the application.
Beginners: Think of this as the "config file" for the entire project.
"""

import os
from pathlib import Path

# BASE_DIR points to the root folder of our project (where manage.py lives)
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY: A secret password Django uses for security. Change this in production!
SECRET_KEY = 'django-insecure-elearn-platform-secret-key-change-in-production-2024'

# DEBUG: Set to True during development so we see detailed error messages
DEBUG = True

# ALLOWED_HOSTS: Which domain names can access our site. Empty list = localhost only
ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# ============================================================
# INSTALLED APPS
# These are all the Django apps our project uses.
# 'courses' is our main app that we built ourselves.
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',        # Django's built-in admin panel
    'django.contrib.auth',         # Django's authentication system (login/logout)
    'django.contrib.contenttypes', # Required by Django
    'django.contrib.sessions',     # Session management (keeps users logged in)
    'django.contrib.messages',     # Flash messages (success/error notifications)
    'django.contrib.staticfiles',  # Serves CSS, JS, images
    'courses',                     # OUR main application
]

# ============================================================
# MIDDLEWARE
# These process every request and response (like security layers).
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',        # Protects forms from attacks
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL configuration file
ROOT_URLCONF = 'e_learning_platform.urls'

# ============================================================
# TEMPLATES
# Tells Django where to find our HTML files.
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Our templates folder
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

WSGI_APPLICATION = 'e_learning_platform.wsgi.application'


# ============================================================
# DATABASE CONFIGURATION
# We use MySQL as our database.
#
# HOW TO SET UP:
# 1. Install MySQL on your computer
# 2. Open MySQL and run: CREATE DATABASE elearn_db CHARACTER SET utf8mb4;
# 3. Update the USER and PASSWORD below to match your MySQL credentials
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Use MySQL
        'NAME': 'elearn_db',                   # Database name (create this in MySQL first)
        'USER': 'root',                        # Your MySQL username
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),                        # Your MySQL password (change this!)
        'HOST': 'localhost',                   # MySQL is running on this computer
        'PORT': '3306',                        # Default MySQL port
        'OPTIONS': {
            'charset': 'utf8mb4',              # Supports all Unicode characters including emojis
        },
    }
}


# ============================================================
# PASSWORD VALIDATION
# Rules for creating passwords (keeps accounts secure).
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================================
# INTERNATIONALIZATION
# Language and time zone settings.
# ============================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # Indian Standard Time (IST)
USE_I18N = True
USE_TZ = True


# ============================================================
# STATIC FILES (CSS, JavaScript, Images)
# Django needs to know where our static files are.
# ============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Where we put our CSS/JS/images
STATIC_ROOT = BASE_DIR / 'staticfiles'   # Where 'collectstatic' puts them for deployment


# ============================================================
# MEDIA FILES (Uploaded files like certificates)
# ============================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# AUTHENTICATION SETTINGS
# Tell Django where to redirect after login/logout.
# ============================================================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'


# ============================================================
# SESSION SETTINGS
# Keeps users logged in for 7 days.
# ============================================================
SESSION_COOKIE_AGE = 604800  # 7 days in seconds
SESSION_SAVE_EVERY_REQUEST = True
