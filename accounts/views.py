"""
Views module for mercury accounts
"""

import StringIO

import ho.pisa as pisa

from django.contrib import messages
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseNotFound)
from django.core.urlresolvers import reverse
from django.template import loader, Context, Template, TemplateDoesNotExist

from configuration.models import Config, PdfTemplate
from accounts.models import Invoice, Quote
from accounts.exceptions import ObjectNotFound, AccountsRedirect


def get_model_name(model):
    return model._meta.verbose_name.lower()


def get_model_info(model):
    return (model._meta.app_label, model._meta.module_name)


def get_model_instance(model, id):
    try:
        instance = model.objects.get(id=id)
    except model.DoesNotExist:
        raise ObjectNotFound("Couldn't find " +
                             "%s with id %s" % (get_model_name(model), id))
    return instance


def get_template(model):
    name = get_model_name(model)
    template = Config.settings.get_setting("%s template" % name)
    error = None
    if template:
        try:
            template = loader.get_template(template)
        except TemplateDoesNotExist:
            info = get_model_info(PdfTemplate)
            error = ("Couldn't generate PDF. " +
                     "Template \"%s\" not found." % template)
            error_page = reverse("admin:%s_%s_changelist" % info)
    else:
        info = get_model_info(Config)
        error = ("Couldn't generate PDF. " +
                 "No setting for \"%s template\" found." % name)
        error_page = reverse("admin:%s_%s_changelist" % info)
    if error:
        raise AccountsRedirect(error, url=error_page)
    else:
        return template


def generate_context(invoice_or_quote):
    instance = invoice_or_quote
    data = {}
    for field in instance._meta.fields:
        data[field.name] = str(getattr(instance, field.name))
    data["customer"] = instance.customer
    data["entries"] = instance.get_entries()
    data["number"] = instance.get_number()
    context = Context(data)
    return context


def get_invoice_context(invoice_id):
    instance = get_model_instance(Invoice, invoice_id)
    context = generate_context(instance)
    context["payments"] = instance.payment_set.all()
    return context


def get_quote_context(quote_id):
    instance = get_model_instance(Quote, quote_id)
    context = generate_context(instance)
    return context


def filename_from_context(context):
    return "Invoice %s.pdf" % context["number"]


def render_pdf(html):
    buffer = StringIO.StringIO()
    result = pisa.CreatePDF(html, buffer)
    return buffer.getvalue()


def render_invoice_pdf(invoice_id):
    template = get_template(Invoice)
    context = get_invoice_context(invoice_id)
    filename = filename_from_context(context)
    pdf = render_pdf(template.render(context))
    # css in template?
    return (filename, pdf)


def render_quote_pdf(quote_id):
    template = get_template(Quote)
    context = get_quote_context(quote_id)
    filename = filename_from_context(context)
    pdf = render_pdf(template.render(context))
    return (filename, html)


def get_response(request, method, args):
    try:
        filename, response = method(*args)
    except ObjectNotFound as e:
        response = HttpResponseNotFound(str(e))
    except AccountsRedirect as e:
        messages.error(request, str(e))
        response = HttpResponseRedirect(e.url)
    else:
        response = HttpResponse(response, mimetype="application/pdf")
        header = 'attachment; filename="%s"' % filename
        response['Content-Disposition'] = header
    return response


def invoice_to_pdf(request, invoice_id):
    response = get_response(request, render_invoice_pdf, [invoice_id])
    return response


def quote_to_pdf(request, quote_id):
    response = get_response(request, render_quote_pdf, [quote_id])
    return response
