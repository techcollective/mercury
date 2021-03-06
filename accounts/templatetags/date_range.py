import datetime
import calendar

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


def context_helper(start_field, end_field):
    """
    This is an attempt to make context variables needed by the date_range.html
    template available to views that aren't going to use the template tag.
    """
    today = datetime.date.today()

    # figure out start and end dates of last month
    last_month = today.month - 1
    if last_month == 0:
        lm_year = today.year - 1
        last_month = 12
    else:
        lm_year = today.year
    lm_end_day = calendar.monthrange(lm_year, last_month)[1]
    last_month_start = datetime.date(lm_year, last_month, 1)
    last_month_end = datetime.date(lm_year, last_month, lm_end_day)

    # figure out start and end dates of last quarter for the shortcut link
    # lq = last quarter number (1-4)
    lq = ((today.month - 1) // 3)
    if lq == 0:
        lq_year = today.year - 1
        lq = 4
    else:
        lq_year = today.year
    lq_end_month = lq * 3
    lq_start_month = lq_end_month - 2
    # find out how many days are in lq_end_month
    lq_end_day = calendar.monthrange(lq_year, lq_end_month)[1]
    last_quarter_start = datetime.date(lq_year, lq_start_month, 1)
    last_quarter_end = datetime.date(lq_year, lq_end_month, lq_end_day)

    # start and end for last year
    last_year = today.year - 1
    last_year_start = datetime.date(last_year, 1, 1)
    last_year_end = datetime.date(last_year, 12, 31)

    return {"start_field": "id_" + start_field,
            "end_field": "id_" + end_field,
            "last_month_start": last_month_start,
            "last_month_end": last_month_end,
            "last_quarter_start": last_quarter_start,
            "last_quarter_end": last_quarter_end,
            "last_year_start": last_year_start,
            "last_year_end": last_year_end,
            }


@register.inclusion_tag('accounts/date_range.html', takes_context=True)
def date_range(context):
    cl = context.get("cl")
    if hasattr(cl.model_admin, "date_range"):
        field_name = cl.model_admin.date_range
        start_field = "%s__gte" % field_name
        end_field = "%s__lte" % field_name
        start_value = cl.params.get(start_field)
        end_value = cl.params.get(end_field)
        # preserve other filter settings
        other_params = [(key, cl.params[key]) for key in cl.params
                        if (key != end_field and key != start_field)]
        form = DateRangeForm({start_field: start_value,
                              end_field: end_value}, start_field=start_field,
                              end_field=end_field)
        context = {"form": form, "other_params": other_params, "cl": cl,
                   "search_box": cl.search_fields,
                   "show_result_count": (cl.result_count !=
                                         cl.full_result_count)}
        context.update(context_helper(start_field, end_field))
        return context
