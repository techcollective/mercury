from django.template import Library


register = Library()


@register.inclusion_tag('admin/date_range.html')
def date_range(cl):
    return {"cl": cl}
