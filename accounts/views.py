"""
Views module for mercury accounts
"""

from django.contrib import messages
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseNotFound)
from django.core.urlresolvers import reverse
from django.template import Context, Template, TemplateDoesNotExist
from django.template.loader import get_template

from configuration.models import Config, PdfTemplate
from accounts.models import Invoice, Quote


def render_pdf(request, model, id):
    name = model._meta.verbose_name.lower()
    model_info = (model._meta.app_label, model._meta.module_name)

    # get the model instance
    try:
        instance = model.objects.get(id=id)
    except model.DoesNotExist:
        return HttpResponseNotFound("Couldn't find %s with id %s" % (name, id))

    # get the template
    pdf_template = Config.settings.get_setting("%s template" % name)
    if pdf_template:
        try:
            template = get_template(pdf_template)
        except TemplateDoesNotExist:
            error = "Couldn't generate PDF. Template \"%s\" not found." % \
                                                                pdf_template
            messages.error(request, error)
            return HttpResponseRedirect(reverse("admin:%s_%s_change" % \
                                                model_info, args=[id]))
    else:
        error = "Couldn't generate PDF. No setting for \"%s template\" found."\
                % name
        messages.error(request, error)
        return HttpResponseRedirect(reverse("admin:%s_%s_change" % model_info,
                                            args=[id]))

    data = {}
    for field in instance._meta.fields:
        data[field.name] = str(getattr(instance, field.name))
    context = Context(data)
    html = template.render(context)
    return HttpResponse(html)


def invoice_to_pdf(request, invoice_id):
    response = render_pdf(request, Invoice, invoice_id)
    return response


def quote_to_pdf(request, quote_id):
    response = render_pdf(request, Quote, quote_id)
    return response
