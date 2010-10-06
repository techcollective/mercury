from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy

from mercury.helpers import get_items_per_page
from mercury.exceptions import RedirectException, MercuryException
from mercury.accounts.models import Entry

from ajax_select.admin import AjaxSelectAdmin


# This is disabled so that the custom method that calls it can catch any
# MecuryExceptions raised during deletion. Also note that the delete_selected
# method that is called is a patched version that optionally does individual
# .delete() calls instead of queryset.delete().
admin.site.disable_action('delete_selected')


def handle_exception(request, mercury_exception):
    messages.error(request, str(mercury_exception))
    if isinstance(mercury_exception, RedirectException):
        return HttpResponseRedirect(mercury_exception.url)
    else:
        return HttpResponseRedirect(request.get_full_path())


class MercuryAdmin(admin.ModelAdmin):
    list_per_page = get_items_per_page()
    qs_delete = False
    actions = ["delete_selected_wrapper"]

    def delete_view(self, *args, **kwargs):
        return self.handle_view("delete_view", *args, **kwargs)

    def change_view(self, *args, **kwargs):
        return self.handle_view("change_view", *args, **kwargs)

    def handle_view(self, view_func, request, object_id, **kwargs):
        try:
            parent_func = getattr(super(MercuryAdmin, self), view_func)
            return parent_func(request, object_id, **kwargs)
        except MercuryException as e:
            return handle_exception(request, e)

    def delete_selected_wrapper(self, request, queryset):
        print "hello"
        try:
            return admin.actions.delete_selected(self, request, queryset)
        except MercuryException as e:
            return handle_exception(request, e)
    delete_selected_wrapper.short_description = ugettext_lazy(
                                    "Delete selected %(verbose_name_plural)s")


class MercuryAjaxAdmin(MercuryAdmin, AjaxSelectAdmin):
    pass
