import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = str(BASE_DIR / 'staticfiles')
STATICFILES_DIRS = [
    str(BASE_DIR / 'network' / 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media')

# Make sure DEBUG is True for development
DEBUG = True

# Add this to your INSTALLED_APPS if not already there
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'network',
]
  