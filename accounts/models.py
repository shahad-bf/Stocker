from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Permissions
    can_view_reports = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_delete_records = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    @property
    def is_manager(self):
        """Check if user is manager or admin"""
        return self.role in ['admin', 'manager']
    
    @property
    def is_employee(self):
        """Check if user is employee (lowest level)"""
        return self.role == 'employee'
    
    def get_full_name(self):
        """Get user's full name"""
        return self.user.get_full_name() or self.user.username
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        if self.is_admin:
            return True
        
        permission_map = {
            'view_reports': self.can_view_reports,
            'manage_users': self.can_manage_users,
            'delete_records': self.can_delete_records,
        }
        
        return permission_map.get(permission, False)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)