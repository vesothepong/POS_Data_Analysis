from django.contrib import admin

from .models import Order, OrderItem, OrderItemTopping


class OrderItemToppingInline(admin.TabularInline):
    model = OrderItemTopping
    extra = 0
    readonly_fields = ("topping_name", "price")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "toppings_list")

    def toppings_list(self, obj):
        return obj.toppings_summary or "-"
    toppings_list.short_description = "Toppings"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("ticket_number", "customer_name", "order_type", "payment_method", "total_amount", "created_at")
    list_filter = ("order_type", "payment_method", "created_at")
    search_fields = ("ticket_number", "customer_name", "table_number")
    inlines = [OrderItemInline]


@admin.register(OrderItemTopping)
class OrderItemToppingAdmin(admin.ModelAdmin):
    list_display = ("order_item", "topping_name", "price")
