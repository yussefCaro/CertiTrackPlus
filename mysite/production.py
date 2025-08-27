from .base import *

DEBUG = False
ALLOWED_HOSTS = ['72.60.114.139', 'localhost', '127.0.0.1']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASS'),
        'HOST': config('DB_HOST'),
        'PORT': '5432',
    }
}

SECRET_KEY = config('SECRET_KEY')
