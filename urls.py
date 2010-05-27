from django.conf.urls.defaults import *
import ajax_select

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'', include(admin.site.urls)),
    (r'^ajax_select/', include('ajax_select.urls')),
)
