import ajax_select

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    (r'^ajax_select/', include('ajax_select.urls')),
    (r'^accounts/', include('accounts.urls')),
    (r'', include(admin.site.urls)),
)
