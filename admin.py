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
        self.handle_view("delete_view", request, object_id, extra_context)
        #try:
        #    return super(MercuryAdmin, self).delete_view(request, object_id, extra_context)
        #except RedirectException as e:
        #    messages.error(request, str(e))
        #    return HttpResponseRedirect(e.url)
        #except MercuryException as e:
        #    messages.error(request, str(e))
        #    return HttpResponseRedirect(request.get_full_path())

    def handle_view(self, view_func, request, object_id, extra_context):
        try:
            parent_func = getattr(super(MercuryAdmin, self), view_func)
            resp = parent_func(request, object_id, extra_context)
        except RedirectException as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(e.url)
        except MercuryException as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(request.get_full_path())


class MercuryAjaxAdmin(MercuryAdmin, AjaxSelectAdmin):
    pass
