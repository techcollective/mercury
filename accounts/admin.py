from django.contrib import admin
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import autoselect_fields_check_can_add
from accounts.models import Customer, Product, Service, PaymentMethod, \
                           InvoiceStatus, Invoice, Payment, Quote, \
                           InvoiceProductEntry, InvoiceServiceEntry, Deposit, \
                           QuoteProductEntry, QuoteServiceEntry


class AjaxTabularInline(admin.TabularInline):
    def get_formset(self, request, obj=None, **kwargs):
        formset = super(AjaxTabularInline,self).get_formset(request,obj,**kwargs)
        autoselect_fields_check_can_add(formset.form,self.model,request.user)
        return formset


class ServiceInline(AjaxTabularInline):
    extra = 1
    verbose_name = "Service"
    verbose_name_plural = "Services"
    form = make_ajax_form(InvoiceServiceEntry, {"service": "service_name"},
                          autofill={"service": {"field": "cost", "related_field": "price"}})


class ProductInline(AjaxTabularInline):
    extra = 1
    verbose_name = "Product"
    verbose_name_plural = "Products"
    form = make_ajax_form(InvoiceProductEntry, {"product": "product_name"},
                          autofill={"product": {"field": "cost", "related_field": "price"}})


class InvoiceProductInline(ProductInline):
    model = InvoiceProductEntry


class InvoiceServiceInline(ServiceInline):
    model = InvoiceServiceEntry


class QuoteProductInline(ProductInline):
    model = QuoteProductEntry


class QuoteServiceInline(ServiceInline):
    model = QuoteServiceEntry


class InvoicePaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    exclude = ["deposit"]
    show_last = True


class DepositPaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class InvoiceAdmin(AjaxSelectAdmin):
    search_fields = ["customer__name"]
    form = make_ajax_form(Invoice, {"customer": "customer_name"})
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created", "date_due", "status", "comment"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    inlines = [InvoiceServiceInline, InvoiceProductInline,
               InvoicePaymentInline]
    date_hierarchy = "date_created"
    def post_save(self, instance):
        instance.update_tax()



class QuoteAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Information", {"fields": ["customer", "date_created", "comment"]}),
        ("Totals", {"fields": ["subtotal", "total_tax", "grand_total"]}),
    ]
    readonly_fields = ["subtotal", "total_tax", "grand_total"]
    inlines = [QuoteServiceInline, QuoteProductInline]
    date_hierarchy = "date_created"


class CustomerAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Contact Information", {"fields": ["phone_number", "email_address"]}),
        ("Address", {"fields": ["address", "city", "state", "zip_code"]}),
    ]


class DepositAdmin(admin.ModelAdmin):
    inlines = [DepositPaymentInline]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Payment)
admin.site.register(Deposit, DepositAdmin)
