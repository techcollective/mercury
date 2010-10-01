from django.contrib import admin

from mercury.helpers import get_items_per_page

from ajax_select.admin import AjaxSelectAdmin


admin.site.disable_action('delete_selected')


class MercuryAdmin(admin.ModelAdmin):
    list_per_page = get_items_per_page()


class MercuryAjaxAdmin(MercuryAdmin, AjaxSelectAdmin):
    pass
