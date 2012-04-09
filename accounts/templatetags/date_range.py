from django.template import Library
from django.contrib.admin.widgets import AdminDateWidget
from django import forms

register = Library()


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=AdminDateWidget)
    end_date = forms.DateField(widget=AdminDateWidget)

@register.inclusion_tag('admin/date_range.html')
def date_range(cl):
    form = DateRangeForm()
    # cl.model_admin.date_range
    return {"cl": cl, "form": form}
