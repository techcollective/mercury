"""
URLs for accounts app
"""

from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('mercury.accounts.views',
    url(r'^invoice/(\d+)/pdf/$', "invoice_to_pdf",
        name="invoice_to_pdf"),
    url(r'^quote/(\d+)/pdf/$', "quote_to_pdf", name="quote_to_pdf"),
    url(r'^invoice/(\d+)/html/$', "invoice_to_html",
        name="invoice_to_html"),
    url(r'^quote/(\d+)/html/$', "quote_to_html",
        name="quote_to_html"),
    url(r'^quote/(\d+)/toinvoice/$', "quote_to_invoice",
        name="quote_to_invoice")
)
