import ajax_select

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from mercury.admin import site

admin.autodiscover()

urlpatterns = patterns('',
    (r'^ajax_select/', include('ajax_select.urls')),
    (r'^accounts/', include('accounts.urls')),
    (r'', include(site.urls)),
)

if settings.DEBUG:
    from django.views.static import serve
    media_url = settings.MEDIA_URL
    if media_url.startswith('/'):
        media_url = media_url[1:]
        urlpatterns += patterns('',
            (r'^%s(?P<path>.*)$' % media_url,
             serve,
             {'document_root': settings.MEDIA_ROOT}))
