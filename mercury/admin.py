from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.conf.urls import patterns, url
from django.template.response import TemplateResponse

from mercury.helpers import get_items_per_page
from mercury.exceptions import RedirectException, MercuryException

from ajax_select.admin import AjaxSelectAdmin


# serve minified JS in production
MINI = ".min"
if settings.DEBUG:
    MINI = ""

def handle_exception(request, mercury_exception):
    messages.error(request, str(mercury_exception))
    if isinstance(mercury_exception, RedirectException):
        return HttpResponseRedirect(mercury_exception.url)
    else:
        return HttpResponseRedirect(request.get_full_path())


class MercuryAdminSite(admin.sites.AdminSite):
    index_template = "mercury/index.html"

    def get_urls(self):
        urls = super(MercuryAdminSite, self).get_urls()
        custom_urls = patterns('',
            url(r'^reports/$', self.admin_view(self.reports_index),
                name="reports_index")
        )
        return custom_urls + urls

    def reports_index(self, request):
        context = {"title": "Reports administration"}
        return TemplateResponse(request, "admin/reports/app_index.html",
                                context, current_app=self.name)



site = MercuryAdminSite(name="mercury")


# This is disabled so that the custom method that calls it can catch any
# MecuryExceptions raised during deletion. Also note that the delete_selected
# method that is called is a patched version that optionally does individual
# .delete() calls instead of queryset.delete().
site.disable_action('delete_selected')

# register auth app
site.register(Group, GroupAdmin)
site.register(User, UserAdmin)


class MercuryAdmin(admin.ModelAdmin):
    allowed_lookups = []

    def lookup_allowed(self, lookup, value):
        if lookup in self.allowed_lookups:
            return True
        if hasattr(self, "date_range"):
            allowed_lookups = [self.date_range + f for f in ["__gte", "__lte"]]
            if lookup in allowed_lookups:
                return True
        return super(MercuryAdmin, self).lookup_allowed(lookup, value)

    class Media:
        css = {"all": ("mercury/css/custom.css",)}
        js = ("ajax_select/js/jquery-1.7.2%s.js" % MINI,
              "ajax_select/js/autogrow%s.js" % MINI,
              )
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
        # i use a wrapper instead of a custom method so that i can use the
        # existing functionality without having to copy and paste it all.
        try:
            return admin.actions.delete_selected(self, request, queryset)
        except MercuryException as e:
            return handle_exception(request, e)
    delete_selected_wrapper.short_description = ugettext_lazy(
                                    "Delete selected %(verbose_name_plural)s")


class MercuryAjaxAdmin(MercuryAdmin, AjaxSelectAdmin):
    class Media:
        css = {
            "all": ("ajax_select/css/base/jquery.ui.all.css",)
        }
        js = ("ajax_select/js/jquery-ui-1.8.18.custom%s.js" % MINI,
              "ajax_select/js/ajax_select%s.js" % MINI,
              )
