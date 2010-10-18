# Django settings for mercury.

import sys
import os


this_dir = os.path.abspath(os.path.dirname(__file__))
lib_path = os.path.join(this_dir, "lib")
if not lib_path in sys.path:
    sys.path.append(lib_path)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(this_dir, 'db.sqlite'),
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(this_dir, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7%hdis&vi#rv&z#6jpu-_g3s(0$+b(*!f9f-5iko*h%rc=t0d+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'mercury.custom.TemplateLoader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'mercury.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(this_dir, "templates"),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'ajax_select',
    'tinymce',
    'mercury.configuration',
    'mercury.accounts',
]

if DEBUG:
    INSTALLED_APPS += ['django_extensions']

mod = "mercury.accounts.helpers."
AJAX_LOOKUP_CHANNELS = {
    'customer_name': mod + "CustomerNameAjaxChannel",
    'product_or_service_name': mod + "ProductNameAjaxChannel",
    'invoice': mod + "InvoiceAjaxChannel",
}
del mod

TINYMCE_DEFAULT_CONFIG = {"theme": "advanced",
                          "plugins": "table, fullpage",
                          "relative_urls": False,
                          "theme_advanced_toolbar_location": "top",
                          "theme_advanced_disable": "styleselect,help",
                          "theme_advanced_buttons1_add": "backcolor",
                          "theme_advanced_buttons3_add": "tablecontrols,fullpage",
                          "force_p_newlines": False,
                          "forced_root_block": "",
                          "width": "700px",
                          "height": "500px",
                          }

LOGIN_URL = "/"
