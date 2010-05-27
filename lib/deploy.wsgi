import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'mercury.settings_production'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

