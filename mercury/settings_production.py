# Django settings for mercury.


from mercury.settings import *

DEBUG = False

INSTALLED_APPS.remove("django_extensions")

DATABASES = {
    'default': {
        'ENGINE': 'mysql',
        'NAME': 'mercury',
        'USER': 'mercury',                       # Not used with sqlite3.
        'PASSWORD': 'PRODUCTION_PASSWORD_HERE',  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
