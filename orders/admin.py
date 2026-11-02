from django.contrib import admin
from .models import Order, OrderStatusHistory

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status', 'note', 'changed_by', 'created_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'student', 'service', 'price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'customer__username', 'student__username')
    inlines = [OrderStatusHistoryInline]
