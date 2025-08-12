from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import uuid


class Notification(models.Model):
    """Notification model for system alerts"""
    
    NOTIFICATION_TYPES = [
        ('low_stock', 'Low Stock Alert'),
        ('expiry_soon', 'Expiry Soon Alert'),
        ('expired', 'Expired Product Alert'),
        ('out_of_stock', 'Out of Stock Alert'),
        ('reorder_needed', 'Reorder Needed Alert'),
        ('system', 'System Notification'),
        ('user', 'User Notification'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Related objects
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='notifications'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='notifications',
        help_text="User this notification is for (if user-specific)"
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_notifications'
    )
    
    # Additional data (JSON field for extra information)
    extra_data = models.JSONField(blank=True, null=True, help_text="Additional notification data")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type', 'is_read']),
            models.Index(fields=['priority', 'created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"

    def get_absolute_url(self):
        return reverse('notifications:notification_detail', kwargs={'pk': self.pk})

    @property
    def priority_color(self):
        """Get color class for priority"""
        color_map = {
            'low': 'success',
            'medium': 'info',
            'high': 'warning',
            'urgent': 'danger',
        }
        return color_map.get(self.priority, 'secondary')

    @property
    def type_icon(self):
        """Get icon for notification type"""
        icon_map = {
            'low_stock': 'exclamation-triangle',
            'expiry_soon': 'clock',
            'expired': 'x-circle',
            'out_of_stock': 'x-circle-fill',
            'reorder_needed': 'arrow-repeat',
            'system': 'gear',
            'user': 'person',
        }
        return icon_map.get(self.type, 'bell')

    @property
    def age_in_hours(self):
        """Get notification age in hours"""
        return (timezone.now() - self.created_at).total_seconds() / 3600

    @property
    def is_recent(self):
        """Check if notification is recent (less than 24 hours)"""
        return self.age_in_hours < 24

    def mark_as_read(self, user=None):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])

    def mark_as_unread(self):
        """Mark notification as unread"""
        self.is_read = False
        self.save(update_fields=['is_read'])

    def send_email(self):
        """Mark notification as email sent"""
        self.is_email_sent = True
        self.email_sent_at = timezone.now()
        self.save(update_fields=['is_email_sent', 'email_sent_at'])

    @classmethod
    def get_unread_count(cls, user=None):
        """Get count of unread notifications"""
        queryset = cls.objects.filter(is_read=False)
        if user:
            queryset = queryset.filter(models.Q(user=user) | models.Q(user__isnull=True))
        return queryset.count()

    @classmethod
    def get_urgent_count(cls, user=None):
        """Get count of urgent notifications"""
        queryset = cls.objects.filter(priority='urgent', is_read=False)
        if user:
            queryset = queryset.filter(models.Q(user=user) | models.Q(user__isnull=True))
        return queryset.count()

    @classmethod
    def create_notification(cls, notification_type, title, message, product=None, user=None, priority='medium', extra_data=None):
        """Create a new notification"""
        return cls.objects.create(
            type=notification_type,
            title=title,
            message=message,
            product=product,
            user=user,
            priority=priority,
            extra_data=extra_data or {}
        )


class NotificationTemplate(models.Model):
    """Template for notification messages"""
    
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES)
    title_template = models.CharField(max_length=200, help_text="Use {variables} for dynamic content")
    message_template = models.TextField(help_text="Use {variables} for dynamic content")
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    send_email = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def render(self, context=None):
        """Render template with context"""
        context = context or {}
        
        title = self.title_template.format(**context)
        message = self.message_template.format(**context)
        
        return {
            'title': title,
            'message': message,
            'type': self.type,
            'priority': self.priority,
        }

    def create_notification(self, context=None, product=None, user=None):
        """Create notification from template"""
        rendered = self.render(context)
        
        notification = Notification.create_notification(
            notification_type=rendered['type'],
            title=rendered['title'],
            message=rendered['message'],
            product=product,
            user=user,
            priority=rendered['priority']
        )
        
        if self.send_email:
            # Import here to avoid circular imports
            from .services import NotificationService
            NotificationService.send_email_notification(notification)
        
        return notification