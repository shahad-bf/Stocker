from django.contrib import admin
from .models import Supplier, SupplierProduct


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'contact_person', 'phone_number', 
        'get_products_count', 'rating', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'rating', 'created_at', 'created_by')
    search_fields = ('name', 'email', 'contact_person', 'phone_number', 'tax_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'logo', 'email', 'website', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'phone_number', 'address')
        }),
        ('Business Details', {
            'fields': ('tax_number', 'payment_terms', 'rating', 'notes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_products_count(self, obj):
        return obj.get_products_count()
    get_products_count.short_description = 'Products Count'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = (
        'supplier', 'product', 'supplier_sku', 'supplier_price', 
        'lead_time_days', 'minimum_order_quantity', 'is_preferred'
    )
    list_filter = ('is_preferred', 'lead_time_days', 'last_order_date')
    search_fields = (
        'supplier__name', 'product__name', 'product__sku', 'supplier_sku'
    )
    readonly_fields = ('created_at', 'updated_at', 'price_difference', 'is_cheapest')
    raw_id_fields = ('supplier', 'product')
    
    fieldsets = (
        ('Relationship', {
            'fields': ('supplier', 'product', 'is_preferred')
        }),
        ('Supplier Details', {
            'fields': ('supplier_sku', 'supplier_price', 'lead_time_days', 'minimum_order_quantity')
        }),
        ('Order Information', {
            'fields': ('last_order_date', 'notes'),
            'classes': ('collapse',)
        }),
        ('Calculated Fields', {
            'fields': ('price_difference', 'is_cheapest'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_difference(self, obj):
        return obj.price_difference
    price_difference.short_description = 'Price Difference'
    
    def is_cheapest(self, obj):
        return obj.is_cheapest
    is_cheapest.short_description = 'Is Cheapest'
    is_cheapest.boolean = True