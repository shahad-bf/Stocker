from django.contrib import admin
from .models import Notification, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'type', 'priority', 'user', 'product', 
        'is_read', 'is_email_sent', 'created_at'
    )
    # Enable delete permissions
    def has_delete_permission(self, request, obj=None):
        return True
    
    # Show delete action in list view
    list_per_page = 25
    list_max_show_all = 100
    # Make sure actions are shown
    actions_on_top = True
    actions_on_bottom = True
    list_filter = (
        'type', 'priority', 'is_read', 'is_email_sent', 
        'created_at', 'created_by'
    )
    search_fields = ('title', 'message', 'user__username', 'product__name')
    readonly_fields = ('id', 'created_at', 'email_sent_at', 'age_in_hours', 'is_recent')
    raw_id_fields = ('product', 'user', 'created_by')
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('type', 'title', 'message', 'priority')
        }),
        ('Related Objects', {
            'fields': ('product', 'user', 'created_by')
        }),
        ('Status', {
            'fields': ('is_read', 'is_email_sent', 'email_sent_at')
        }),
        ('Additional Data', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'age_in_hours', 'is_recent'),
            'classes': ('collapse',)
        }),
    )
    
    # Enable bulk delete action
    actions = [
        'delete_selected',  # Django's default delete action
        'حذف_الإشعارات_المحددة',  # Custom delete action in Arabic
        'mark_as_read', 'mark_as_unread', 'send_email_notifications', 
        'delete_read_notifications', 'delete_old_notifications'
    ]
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark selected notifications as unread'
    
    def send_email_notifications(self, request, queryset):
        from .services import NotificationService
        count = 0
        for notification in queryset.filter(is_email_sent=False):
            try:
                NotificationService.send_email_notification(notification)
                count += 1
            except Exception as e:
                self.message_user(request, f'Error sending email for {notification}: {e}', level='ERROR')
        
        if count:
            self.message_user(request, f'{count} email notifications sent successfully.')
    send_email_notifications.short_description = 'Send email notifications'
    
    def delete_selected_notifications(self, request, queryset):
        """Delete selected notifications with confirmation"""
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No notifications selected for deletion.', level='WARNING')
            return
        
        # Delete the notifications
        deleted_count, _ = queryset.delete()
        self.message_user(request, f'{deleted_count} notifications deleted successfully.')
    delete_selected_notifications.short_description = 'حذف الإشعارات المحددة'
    
    def حذف_الإشعارات_المحددة(self, request, queryset):
        """حذف الإشعارات المحددة"""
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'لا توجد إشعارات محددة للحذف.', level='WARNING')
            return
        
        # Delete the notifications
        deleted_count, _ = queryset.delete()
        self.message_user(request, f'تم حذف {deleted_count} إشعار بنجاح.')
    حذف_الإشعارات_المحددة.short_description = 'حذف الإشعارات المحددة'
    
    def delete_read_notifications(self, request, queryset):
        """Delete all read notifications from the selected ones"""
        read_notifications = queryset.filter(is_read=True)
        count = read_notifications.count()
        if count == 0:
            self.message_user(request, 'No read notifications found to delete.', level='WARNING')
            return
        
        deleted_count, _ = read_notifications.delete()
        self.message_user(request, f'{deleted_count} read notifications deleted successfully.')
    delete_read_notifications.short_description = 'حذف الإشعارات المقروءة'
    
    def delete_old_notifications(self, request, queryset):
        """Delete notifications older than 30 days from the selected ones"""
        from django.utils import timezone
        from datetime import timedelta
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        old_notifications = queryset.filter(created_at__lt=thirty_days_ago)
        count = old_notifications.count()
        
        if count == 0:
            self.message_user(request, 'No notifications older than 30 days found to delete.', level='WARNING')
            return
        
        deleted_count, _ = old_notifications.delete()
        self.message_user(request, f'{deleted_count} old notifications (30+ days) deleted successfully.')
    delete_old_notifications.short_description = 'حذف الإشعارات القديمة (أكثر من 30 يوم)'
    
    def age_in_hours(self, obj):
        return f"{obj.age_in_hours:.1f} hours"
    age_in_hours.short_description = 'Age'
    
    def is_recent(self, obj):
        return obj.is_recent
    is_recent.short_description = 'Recent'
    is_recent.boolean = True


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'type', 'priority', 'is_active', 
        'send_email', 'created_at'
    )
    list_filter = ('type', 'priority', 'is_active', 'send_email', 'created_at')
    search_fields = ('name', 'title_template', 'message_template')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'type', 'priority', 'is_active')
        }),
        ('Template Content', {
            'fields': ('title_template', 'message_template')
        }),
        ('Notification Settings', {
            'fields': ('send_email',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)