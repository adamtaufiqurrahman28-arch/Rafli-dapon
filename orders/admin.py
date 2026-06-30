from django.contrib import admin

from .models import MenuCategory, MenuItem, Order, OrderItem, Restaurant, Setting


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "order_mode", "is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("order_mode", "is_active")


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "sort_order")
    list_filter = ("restaurant",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "category", "price", "is_active", "is_daily")
    list_filter = ("restaurant", "category", "is_active", "is_daily")
    search_fields = ("name", "description")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_code", "customer_name", "restaurant_label", "total_price", "payment_method", "payment_status", "order_status", "created_at")
    list_filter = ("order_date", "payment_method", "payment_status", "order_status")
    search_fields = ("order_code", "customer_name", "whatsapp", "notes")
    inlines = [OrderItemInline]


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ("key", "label")
    search_fields = ("key", "label", "value")
