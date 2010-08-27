"""
Views module for mercury accounts
"""

import StringIO

import ho.pisa as pisa

from django.contrib import messages
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseNotFound)
from django.template import (loader, Context, TemplateDoesNotExist,
                             TemplateSyntaxError)
from django.utils.text import capfirst

from mercury.configuration.models import Config, Template
from mercury.accounts.models import Invoice, Quote
from mercury.accounts.exceptions import ObjectNotFound, AccountsRedirect
from mercury.helpers import model_to_dict, get_changelist_url, get_change_url


def generate_context(quote_or_invoice):
    instance = quote_or_invoice
    data = model_to_dict(instance)
    data["customer"] = instance.customer
    data["entries"] = instance.get_entries()
    data["id_number"] = instance.get_number()
    data["type"] = capfirst(instance._meta.verbose_name)
    return Context(data)


class Renderer(object):
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


class HtmlRenderer(Renderer):
    def __init__(self, *args, **kwargs):
        super(HtmlRenderer, self).__init__(*args, **kwargs)
        template = Config.settings.get_setting("%s template" % self.model_name)
        error = None
        if template:
            try:
                self.template = loader.get_template(template)
            except TemplateDoesNotExist:
                error = ("Couldn't render. " +
                         "Template \"%s\" not found." % template)
                error_page = get_changelist_url(Template)
            except TemplateSyntaxError as e:
                instance = Template.objects.get(name=template)
                error = "Couldn't render template. %s" % str(e)
                error_page = get_change_url(instance)
        else:
            error = ("Couldn't render. " +
                     "No setting for \"%s template\" found." % self.model_name)
            error_page = get_changelist_url(Config)

        if error:
            raise AccountsRedirect(error, url=error_page)

    def render(self):
        return self.template.render(self.get_context())


class QuoteHtmlRenderer(HtmlRenderer):
    def __init__(self, quote_id):
        super(QuoteHtmlRenderer, self).__init__(Quote, quote_id)

    def get_context(self):
        return generate_context(self.instance)


class InvoiceHtmlRenderer(HtmlRenderer):
    def __init__(self, invoice_id):
        super(InvoiceHtmlRenderer, self).__init__(Invoice, invoice_id)

    def get_context(self):
        context = generate_context(self.instance)
        context["payments"] = self.instance.payment_set.all()
        return context


def render_pdf(html):
    buffer = StringIO.StringIO()
    result = pisa.CreatePDF(html, buffer)
    return buffer.getvalue()


class InvoicePdfRenderer(InvoiceHtmlRenderer):
    def __init__(self, *args, **kwargs):
        super(InvoicePdfRenderer, self).__init__(*args, **kwargs)
        self.filename = "Invoice %s.pdf" % self.instance.get_number()

    def render(self):
        html = super(InvoicePdfRenderer, self).render()
        return render_pdf(html)


class QuotePdfRenderer(QuoteHtmlRenderer):
    def __init__(self, *args, **kwargs):
        super(QuotePdfRenderer, self).__init__(*args, **kwargs)
        self.filename = "Quote %s.pdf" % self.instance.get_number()

    def render(self):
        html = super(QuotePdfRenderer, self).render()
        return render_pdf(html)


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
        if mimetype:
            header = 'attachment; filename="%s"' % renderer.filename
            response = HttpResponse(result, mimetype=mimetype)
            response["Content-Disposition"] = header
        else:
            response = HttpResponse(result)
    return response


def invoice_to_html(request, invoice_id):
    response = generate_response(request, InvoiceHtmlRenderer, [invoice_id])
    return response


def quote_to_html(request, quote_id):
    response = generate_response(request, QuoteHtmlRenderer, [quote_id])
    return response


# todo: mimetype is a stupid way to decide if it should be an attachment
def invoice_to_pdf(request, invoice_id):
    response = generate_response(request, InvoicePdfRenderer, [invoice_id],
                                 mimetype="application/pdf")
    return response


def quote_to_pdf(request, quote_id):
    response = generate_response(request, QuotePdfRenderer, [quote_id],
                                 mimetype="application/pdf")
    return response


def quote_to_invoice(request, quote_id):
    pass
