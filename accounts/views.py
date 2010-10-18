"""
Views module for mercury accounts
"""

import StringIO
import os

import ho.pisa as pisa

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseNotFound)
from django.template import (loader, Context, TemplateDoesNotExist,
                             TemplateSyntaxError)
from django.utils.text import capfirst

from mercury.configuration.exceptions import NoSuchSetting
from mercury.configuration.models import Config, Template
from mercury.accounts.models import Invoice, Quote
from mercury.accounts.exceptions import ObjectNotFound, AccountsRedirect
from mercury.helpers import (model_to_dict, get_changelist_url, get_change_url,
                             get_template_name, get_pdf_as_attachment)


def fetch_resources(uri, rel):
    """
    Callback to allow pisa/reportlab to retrieve media.
    "uri" is the href attribute from the html link element.
    "rel" gives a relative path, but it's not used here.

    """
    path = os.path.join(settings.MEDIA_ROOT,
                        uri.replace(settings.MEDIA_URL, ""))
    return path


class TemplateLoader(object):
    def __init__(self, entity):
        try:
            self.template_name = get_template_name(entity)
        except NoSuchSetting as e:
            error = ("Couldn't render. " +
                     "No setting called \"%s\" was found." % str(e))
            error_page = get_changelist_url(Config)
            raise AccountsRedirect(error, url=error_page)

    def get_template(self):
        try:
            return loader.get_template(self.template_name)
        except TemplateDoesNotExist:
            error = ("Couldn't render. " +
                     "Template \"%s\" not found." % self.template_name)
            error_page = get_changelist_url(Template)
            raise AccountsRedirect(error, url=error_page)
        except TemplateSyntaxError as e:
            instance = Template.objects.get(name=self.template_name)
            error = "Couldn't render template. %s" % str(e)
            error_page = get_change_url(instance)
            raise AccountsRedirect(error, url=error_page)


class HtmlRenderer(object):
    def __init__(self, model, instance_id):
        self.model = model
        self.instance_id = instance_id
        self.model_name = self.model._meta.verbose_name.lower()
        try:
            self.instance = self.model.objects.get(id=instance_id)
        except self.model.DoesNotExist:
            raise ObjectNotFound("Couldn't find " +
                                 "%s with id %s" % (self.model_name,
                                                    self.instance_id))
        self.template = TemplateLoader(self.model_name).get_template()
        self.terms = TemplateLoader("terms and conditions").get_template()

    def render(self):
        return self.template.render(self.generate_context())

    def generate_context(self):
        data = model_to_dict(self.instance)
        data["customer"] = self.instance.customer
        data["entries"] = self.instance.get_entries()
        data["id_number"] = self.instance.get_number()
        data["type"] = capfirst(self.model_name)
        # todo: context for terms template will in future contain company name
        data["terms"] = self.terms.render(Context())
        if hasattr(self.instance, "payment_set"):
            data["payments"] = self.instance.payment_set.all()
        data["pad_rows"] = xrange(3)
        return Context(data)


class PdfRenderer(HtmlRenderer):
    def __init__(self, *args, **kwargs):
        super(PdfRenderer, self).__init__(*args, **kwargs)
        self.filename = "%s %s.pdf" % (capfirst(self.model_name),
                                       self.instance.get_number())

    def render(self):
        buffer = StringIO.StringIO()
        result = pisa.CreatePDF(super(PdfRenderer, self).render(), buffer,
                                link_callback=fetch_resources)
        return buffer.getvalue()


@login_required
def generate_response(request, render_class, args, mimetype=None):
    try:
        renderer = render_class(*args)
        result = renderer.render()
    except ObjectNotFound as e:
        response = HttpResponseNotFound(str(e))
    except AccountsRedirect as e:
        messages.error(request, str(e))
        response = HttpResponseRedirect(e.url)
    else:
        response = HttpResponse(result, mimetype=mimetype)
        if get_pdf_as_attachment():
            header = 'attachment; filename="%s"' % renderer.filename
            response["Content-Disposition"] = header
    return response


def invoice_to_html(request, invoice_id):
    response = generate_response(request, HtmlRenderer, [Invoice, invoice_id])
    return response


def quote_to_html(request, quote_id):
    response = generate_response(request, HtmlRenderer, [Quote, quote_id])
    return response


# todo: mimetype is a stupid way to decide if it should be an attachment
def invoice_to_pdf(request, invoice_id):
    response = generate_response(request, PdfRenderer, [Invoice, invoice_id],
                                 mimetype="application/pdf")
    return response


def quote_to_pdf(request, quote_id):
    response = generate_response(request, PdfRenderer, [Quote, quote_id],
                                 mimetype="application/pdf")
    return response


@login_required
def quote_to_invoice(request):
    if request.POST:
        quote = Quote.objects.get(pk=request.POST["quote_id"])
        invoice = quote.create_invoice()
        messages.info(request, "Invoice successfully created.")
        return HttpResponseRedirect(get_change_url(invoice))
    else:
        messages.error(request, ("The location %s shouldn't be directly " +
                       " browsed to.") % reverse("quote_to_invoice"))
        return HttpResponseRedirect(reverse("admin:index"))
