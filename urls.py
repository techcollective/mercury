import ajax_select

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    (r'^ajax_select/', include('ajax_select.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    url(r'^accounts/invoice/pdf/(\d+)/$', "accounts.views.invoice_to_pdf",
        name="invoice_to_pdf"),
    url(r'^accounts/quote/pdf/(\d+)/$', "accounts.views.quote_to_pdf",
        name="quote_to_pdf"),
    url(r'^accounts/invoice/html/(\d+)/$', "accounts.views.invoice_to_html",
        name="invoice_to_html"),
    url(r'^accounts/quote/html/(\d+)/$', "accounts.views.quote_to_html",
        name="quote_to_html"),
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
