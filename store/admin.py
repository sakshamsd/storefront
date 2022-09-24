from pyexpat.errors import messages
from django.contrib import admin, messages

from . import models
from django.http.request import HttpRequest
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.db.models.query import QuerySet
# Register your models here.


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    # exclude = ['promotions']
    # readonly_fields = ['title']
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    list_display = ['title', 'unit_price',
                    'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ["collection", 'last_update', InventoryFilter]
    search_fields = ['title']
    # inlines = [TagInline]

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request, f'{updated_count} products were successfully updated', messages.ERROR)

# admin.site.register(Product, ProductAdmin) instead if this we use decorater like above for easu method


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'order_count']
    list_editable = ['membership']
    ordering = ['first_name', 'last_name']
    list_per_page = 10
    # __startswith is lookup and i is ued for cas insensetive if i removed it will be case sensitive
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='order_count')
    def order_count(self, customer):
        # admin: app_model_page
        url = (reverse('admin:store_order_changelist') + "?" +
               urlencode({'customer__id': str(customer.id)}))
        return format_html('<a href="{}">{}</a>', url, customer.order_count)

    def get_queryset(self, request: HttpRequest):  # returns queryset
        return super().get_queryset(request).annotate(
            order_count=Count('order')
        )


class OrderItemInline(admin.TabularInline):  # admin.StackInline
    # autocomplete_fields = ['product']
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['placed_at', 'payment_status', 'customer']
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]

    # def customer_name(self, order):
    #     name = order.customer.first_name + " " + order.customer.last_name
    #     return name


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        # admin: app_model_page
        url = (reverse('admin:store_product_changelist') + "?" +
               urlencode({'collection__id': str(collection.id)}))
        return format_html('<a href="{}">{}</a>', url, collection.products_count)
        # return collection.products_count

    def get_queryset(self, request: HttpRequest):  # returns queryset
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )
