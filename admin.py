from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect

from mercury.helpers import get_items_per_page
from mercury.exceptions import RedirectException, MercuryException

from ajax_select.admin import AjaxSelectAdmin


admin.site.disable_action('delete_selected')


class MercuryAdmin(admin.ModelAdmin):
    list_per_page = get_items_per_page()
    def delete_view(self, *args, **kwargs):
        return self.handle_view("delete_view", *args, **kwargs)

    def change_view(self, *args, **kwargs):
        return self.handle_view("change_view", *args, **kwargs)

    def handle_view(self, view_func, request, object_id, **kwargs):
        try:
            parent_func = getattr(super(MercuryAdmin, self), view_func)
            return parent_func(request, object_id, **kwargs)
        except RedirectException as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(e.url)
        except MercuryException as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(request.get_full_path())


class MercuryAjaxAdmin(MercuryAdmin, AjaxSelectAdmin):
    pass
