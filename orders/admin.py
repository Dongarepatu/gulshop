# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Use 'order_id' not 'order_number'
    list_display = ['order_id', 'name', 'email', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'payment_method']
    search_fields = ['order_id', 'name', 'email', 'phone']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__status']