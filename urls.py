from django.conf.urls.defaults import *
from django.conf import settings
import ajax_select

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^ajax_select/', include('ajax_select.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    (r'', include(admin.site.urls)),
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
