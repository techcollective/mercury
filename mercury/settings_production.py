# Django settings for mercury.


from mercury.settings import *

DEBUG = False

INSTALLED_APPS.remove("django_extensions")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mercury',
        'USER': 'mercury',                       # Not used with sqlite3.
        'PASSWORD': 'PRODUCTION_PASSWORD_HERE',  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

CACHES = {
    'default': {
        'TIMEOUT': 86400,
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        # set a unique key_prefix for each instance sharing memcached
        'KEY_PREFIX': 'production',
    }
}
