from django.contrib.admin import ModelAdmin

from mercury.helpers import get_items_per_page

from ajax_select.admin import AjaxSelectAdmin


class MercuryAdmin(ModelAdmin):
    list_per_page = get_items_per_page()


class MercuryAjaxAdmin(AjaxSelectAdmin):
    list_per_page = get_items_per_page()
