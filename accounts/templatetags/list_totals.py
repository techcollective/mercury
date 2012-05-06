from django import template
from django.db.models import Sum
from django.utils.text import capfirst

from mercury.helpers import get_currency_symbol


register = template.Library()


@register.inclusion_tag("accounts/list_totals.html", takes_context=True)
def list_totals(context):
    cl = context.get("cl")
    if hasattr(cl.model_admin, "list_totals"):
        prefix, suffix = get_currency_symbol()
        query_string = cl.get_query_string()
        multi_page = cl.multi_page
        if cl.show_all:
            multi_page = False
        query_set = cl.query_set
        totals = []
        kwargs = {}
        # set up arguments for aggregate()
        for total in cl.model_admin.list_totals:
            if isinstance(total, tuple):
                field = total[0]
                title = total[1]
            else:
                field = total
                title = cl.model_admin.opts.get_field(field).verbose_name
                title = capfirst(title)
            totals.append({"field": field, "title": title})
            kwargs.update({field: Sum(field)})
        # run the query
        results = query_set.aggregate(**kwargs)
        # get results ready for template
        for total in totals:
            # fixme: why or 0?
            result = results[total["field"]] or 0
            result = "%s%s%s" % (prefix, str(result), suffix)
            total.update({"total": result})
        return {"totals": totals, "multi_page": multi_page}
