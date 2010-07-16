"""
Views module for mercury accounts
"""

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, Template, TemplateDoesNotExist
from django.template.loader import get_template

from configuration.models import Config, InvoiceTemplate
from accounts.models import Invoice


def invoice_to_pdf(request, invoice_id):
    # get the template code
    pdf_template = Config.settings.get_setting("invoice template")
    if pdf_template:
        try:
            template = get_template(pdf_template)
        except TemplateDoesNotExist:
            pdf_template = None
    if not pdf_template:
        # if there is no valid setting, grab any template
        try:
            template = InvoiceTemplate.objects.all()[0]
        except IndexError:
            messages.add_message(request, messages.ERROR,
                                 "Couldn't generate PDF. No invoice template found.")
            return HttpResponseRedirect(reverse("admin:accounts_invoice_change",
                                                args=[invoice_id]))

    # get the invoice instance
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             "Couldn't find invoice with id %s" % invoice_id)
        return HttpResponseRedirect(reverse("admin:accounts_invoice_change",
                                            args=[invoice_id]))

    template = Template(template.template)
    context = Context({"invoice": invoice})
