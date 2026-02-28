from django.contrib import admin
from inventory.models import Product, Order, UserProfile, Supplier, ActivityLog

admin.site.site_header = "InvenTrack Admin"
admin.site.site_title = "InvenTrack"
admin.site.index_title = "Administration"


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'supplier')
    list_filter = ['category', 'supplier']
    search_fields = ['name', 'description']


class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'created_by', 'order_quantity', 'status', 'date')
    list_filter = ['status', 'date']
    search_fields = ['product__name']
    list_editable = ['status']


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'physical_address', 'mobile')
    search_fields = ['user__username']


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone')
    search_fields = ['name', 'contact_person', 'email']


class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'timestamp')
    list_filter = ['action', 'timestamp']
    search_fields = ['description', 'user__username']
    readonly_fields = ('user', 'action', 'description', 'timestamp')


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
