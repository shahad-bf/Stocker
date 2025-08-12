from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'role', 'department', 'phone', 'avatar',
        'can_view_reports', 'can_manage_users', 'can_delete_records'
    )


class UserAdmin(BaseUserAdmin):
    """Extended user admin with profile"""
    inlines = (UserProfileInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'get_role', 'get_department', 'is_staff', 'is_active'
    )
    list_filter = BaseUserAdmin.list_filter + ('profile__role', 'profile__department')
    search_fields = BaseUserAdmin.search_fields + ('profile__department',)
    
    def get_role(self, obj):
        """Get user role"""
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'No Profile'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role'
    
    def get_department(self, obj):
        """Get user department"""
        return obj.profile.department if hasattr(obj, 'profile') else 'No Profile'
    get_department.short_description = 'Department'
    get_department.admin_order_field = 'profile__department'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile admin"""
    list_display = (
        'user', 'role', 'department', 'phone', 
        'can_view_reports', 'can_manage_users', 'can_delete_records',
        'created_at'
    )
    list_filter = ('role', 'department', 'can_view_reports', 'can_manage_users', 'can_delete_records')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'department')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'department', 'phone', 'avatar')
        }),
        ('Permissions', {
            'fields': ('can_view_reports', 'can_manage_users', 'can_delete_records')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)