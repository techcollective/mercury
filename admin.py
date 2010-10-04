from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect

from mercury.helpers import get_items_per_page
from mercury.exceptions import RedirectException

from ajax_select.admin import AjaxSelectAdmin


admin.site.disable_action('delete_selected')


class MercuryAdmin(admin.ModelAdmin):
    list_per_page = get_items_per_page()
    def delete_view(self, request, object_id, extra_context=None):
        try:
            return super(MercuryAdmin, self).delete_view(request, object_id, extra_context)
        except RedirectException as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(e.url)


class MercuryAjaxAdmin(MercuryAdmin, AjaxSelectAdmin):
    pass
