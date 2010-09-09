from django import template
from django.db.models import Sum

from mercury.helpers import get_currency_symbol

register = template.Library()

@register.inclusion_tag("accounts/total.html", takes_context=True)
def total(context, field):
    total = ""
    if "cl" in context:
        prefix, suffix = get_currency_symbol()
        qs = context["cl"].query_set
        total = qs.aggregate(Sum(field))["%s__sum" % field]
        total = total or 0
        total = "%s%s%s" % (prefix, str(total), suffix)
    return {"total": total}
