from .base import *

DEBUG = False
ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com']

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
