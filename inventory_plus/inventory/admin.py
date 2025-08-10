from django.contrib import admin
from .models import StockMovement, InventoryTransaction, StockAlert


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'movement_type', 'quantity', 'previous_stock', 
        'new_stock', 'created_by', 'created_at'
    )
    list_filter = ('movement_type', 'created_at', 'created_by')
    search_fields = ('product__name', 'product__sku', 'reference_number', 'notes')
    readonly_fields = ('id', 'created_at')
    raw_id_fields = ('product', 'supplier')
    
    fieldsets = (
        ('Movement Details', {
            'fields': ('product', 'movement_type', 'quantity', 'previous_stock', 'new_stock')
        }),
        ('Financial Information', {
            'fields': ('unit_cost', 'supplier')
        }),
        ('References', {
            'fields': ('reference_number', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_change_permission(self, request, obj=None):
        # Stock movements should generally not be changed after creation
        return False


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'reference_number', 'transaction_type', 'status', 
        'total_amount', 'supplier', 'created_by', 'created_at'
    )
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('reference_number', 'description', 'supplier__name')
    readonly_fields = ('id', 'created_at', 'completed_at')
    raw_id_fields = ('supplier', 'created_by')
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_type', 'reference_number', 'description', 'status')
        }),
        ('Related Entities', {
            'fields': ('supplier', 'created_by')
        }),
        ('Financial Information', {
            'fields': ('total_amount', 'tax_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'alert_type', 'threshold_value', 
        'is_active', 'email_notifications', 'last_triggered'
    )
    list_filter = ('alert_type', 'is_active', 'email_notifications', 'last_triggered')
    search_fields = ('product__name', 'product__sku')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_triggered')
    raw_id_fields = ('product',)
    filter_horizontal = ('notify_users',)
    
    fieldsets = (
        ('Alert Configuration', {
            'fields': ('product', 'alert_type', 'threshold_value', 'is_active')
        }),
        ('Notification Settings', {
            'fields': ('email_notifications', 'notify_users', 'notify_roles')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_triggered'),
            'classes': ('collapse',)
        }),
    )