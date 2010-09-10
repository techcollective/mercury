from django import template
from django.db.models import Sum

from mercury.helpers import get_currency_symbol


register = template.Library()


@register.inclusion_tag("accounts/total.html", takes_context=True)
def total(context, field):
    total = ""
    if "cl" in context:
        prefix, suffix = get_currency_symbol()
        query_string = context["cl"].get_query_string()
        multi_page = context["cl"].multi_page
        if context["cl"].show_all:
            multi_page = False
        query_set = context["cl"].query_set
        total = query_set.aggregate(total=Sum(field))["total"]
        total = total or 0
        total = "%s%s%s" % (prefix, str(total), suffix)
        show_total = query_string != "?"
    return {"total": total, "multi_page": multi_page, "show_total": show_total}
