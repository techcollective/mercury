from django.template import Library
from django.contrib.admin.widgets import AdminDateWidget
from django import forms

register = Library()


class DateRangeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        start_field = kwargs.pop("start_field")
        end_field = kwargs.pop("end_field")
        super(DateRangeForm, self).__init__(*args, **kwargs)
        self.fields[start_field] = forms.DateField(widget=AdminDateWidget,
                                                   label="Start date",
                                                   required=False)
        self.fields[end_field] = forms.DateField(widget=AdminDateWidget,
                                                   label="End date",
                                                   required=False)


@register.inclusion_tag('admin/date_range.html')
def date_range(cl):
    if hasattr(cl.model_admin, "date_range"):
        field_name = cl.model_admin.date_range
        start_field = "%s__gte" % field_name
        end_field = "%s__lte" % field_name
        start_value = cl.params.get(start_field)
        end_value = cl.params.get(end_field)
        form = DateRangeForm({start_field: start_value,
                              end_field: end_value}, start_field=start_field,
                              end_field=end_field)
        # preserve other filter settings
        other_params = [(key, cl.params[key]) for key in cl.params
                        if (key != end_field and key != start_field)]
        return {"show": True, "form": form, "other_params": other_params}
