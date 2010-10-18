import os
import sys
import site

# the deployment assumes the following directory structure:
# virtualenv-directory (any name is OK)
#   lib
#       python2.X
#           site-packages
#   src
#       mercury
#           deploy
#               mercury.wsgi (this file)

# add mercury to sys.path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")))

# add mercury's virtualenv
python_version = ".".join([str(x) for x in sys.version_info[0:2]])
site.addsitedir(os.path.abspath(
    os.path.join(os.path.dirname(__file__),
                 "../../../lib/python%s/site-packages" % python_version)))

os.environ['DJANGO_SETTINGS_MODULE'] = 'mercury.settings_production'

# The import has to be down here because the virtualenv path has to be added
# before the import will work.
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()