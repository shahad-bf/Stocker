from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_products_count', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at', 'created_by')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    prepopulated_fields = {}
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'description', 'image', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_products_count(self, obj):
        return obj.get_products_count()
    get_products_count.short_description = 'Products Count'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'sku', 'category', 'stock_quantity', 
        'unit_price', 'stock_status_display', 'is_active', 'created_at'
    )
    list_filter = (
        'category', 'unit', 'is_active', 'is_featured', 
        'has_expiry', 'created_at', 'brand'
    )
    search_fields = ('name', 'sku', 'barcode', 'description', 'brand')
    readonly_fields = ('id', 'created_at', 'updated_at', 'stock_status', 'stock_value')
    raw_id_fields = ('category', 'created_by', 'last_updated_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'barcode', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'cost_price', 'selling_price', 'unit')
        }),
        ('Stock Management', {
            'fields': ('stock_quantity', 'minimum_stock', 'maximum_stock', 'reorder_level')
        }),
        ('Product Details', {
            'fields': ('weight', 'dimensions', 'color', 'size', 'material', 'brand', 'model_number'),
            'classes': ('collapse',)
        }),
        ('Expiry Management', {
            'fields': ('has_expiry', 'expiry_date', 'shelf_life_days'),
            'classes': ('collapse',)
        }),
        ('Images and Status', {
            'fields': ('image', 'is_active', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('created_by', 'last_updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status_display(self, obj):
        return obj.stock_status_display
    stock_status_display.short_description = 'Stock Status'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)