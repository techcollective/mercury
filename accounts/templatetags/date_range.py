from django.template import Library
from django.contrib.admin.widgets import AdminDateWidget
from django import forms

register = Library()


class DateRangeForm(forms.Form):
    invoice__date_created__gte = forms.DateField(widget=AdminDateWidget,
                                                 label="Start date")
    invoice__date_created__lte = forms.DateField(widget=AdminDateWidget,
                                                 label="End date")

@register.inclusion_tag('admin/date_range.html')
def date_range(cl):
    form = DateRangeForm()
    # cl.model_admin.date_range
    return {"cl": cl, "form": form}
