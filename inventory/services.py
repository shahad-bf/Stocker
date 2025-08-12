"""
Notification services for inventory management
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from products.models import Product
from notifications.models import Notification
from accounts.models import UserProfile


class NotificationService:
    """Service class for handling notifications"""
    
    @staticmethod
    def create_notification(notification_type, title, message, product=None, user=None, priority='medium'):
        """Create a new notification"""
        notification = Notification.objects.create(
            type=notification_type,
            title=title,
            message=message,
            product=product,
            user=user,
            priority=priority
        )
        return notification
    
    @staticmethod
    def send_email_notification(notification, recipients=None):
        """Send email notification to recipients"""
        if not recipients:
            # Get all managers and admins
            recipients = User.objects.filter(
                profile__role__in=['admin', 'manager'],
                is_active=True
            ).values_list('email', flat=True)
            recipients = [email for email in recipients if email]
        
        if not recipients:
            return False
        
        try:
            # Prepare email content
            subject = f"[Inventory Alert] {notification.title}"
            
            # Render HTML template
            html_message = render_to_string('emails/notification_email.html', {
                'notification': notification,
                'site_name': 'Inventory Plus',
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'
            })
            
            # Create plain text version
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                html_message=html_message,
                fail_silently=False,
            )
            
            # Update notification status
            notification.is_email_sent = True
            notification.email_sent_at = timezone.now()
            notification.save()
            
            return True
            
        except Exception as e:
            print(f"Failed to send email notification: {e}")
            return False
    
    @staticmethod
    def check_low_stock_alerts():
        """Check for products with low stock and create notifications"""
        from django.db import models
        
        low_stock_products = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=models.F('minimum_stock')
        ).exclude(
            # Don't create duplicate notifications for the same product in the last 24 hours
            notifications__type='low_stock',
            notifications__created_at__gte=timezone.now() - timedelta(hours=24)
        )
        
        notifications_created = 0
        for product in low_stock_products:
            if product.stock_quantity == 0:
                # Out of stock - urgent priority
                notification = NotificationService.create_notification(
                    notification_type='out_of_stock',
                    title=f'Out of Stock: {product.name}',
                    message=f'Product "{product.name}" (SKU: {product.sku}) is completely out of stock. Immediate restocking required.',
                    product=product,
                    priority='urgent'
                )
            else:
                # Low stock - high priority
                notification = NotificationService.create_notification(
                    notification_type='low_stock',
                    title=f'Low Stock Alert: {product.name}',
                    message=f'Product "{product.name}" (SKU: {product.sku}) is running low. Current stock: {product.stock_quantity}, Minimum: {product.minimum_stock}',
                    product=product,
                    priority='high'
                )
            
            # Send email notification
            NotificationService.send_email_notification(notification)
            notifications_created += 1
        
        return notifications_created
    
    @staticmethod
    def check_expiry_alerts():
        """Check for products nearing expiry and create notifications"""
        from django.db import models
        
        today = timezone.now().date()
        warning_days = 7  # Alert 7 days before expiry
        urgent_days = 3   # Urgent alert 3 days before expiry
        
        # Products expiring soon (within warning_days)
        expiring_soon = Product.objects.filter(
            is_active=True,
            has_expiry=True,
            expiry_date__isnull=False,
            expiry_date__lte=today + timedelta(days=warning_days),
            expiry_date__gt=today
        ).exclude(
            # Don't create duplicate notifications
            notifications__type='expiry_soon',
            notifications__created_at__gte=timezone.now() - timedelta(hours=24)
        )
        
        # Expired products
        expired_products = Product.objects.filter(
            is_active=True,
            has_expiry=True,
            expiry_date__isnull=False,
            expiry_date__lt=today
        ).exclude(
            # Don't create duplicate notifications
            notifications__type='expired',
            notifications__created_at__gte=timezone.now() - timedelta(hours=24)
        )
        
        notifications_created = 0
        
        # Handle expiring soon products
        for product in expiring_soon:
            days_until_expiry = (product.expiry_date - today).days
            
            if days_until_expiry <= urgent_days:
                priority = 'urgent'
                title = f'URGENT: Product Expiring Soon - {product.name}'
                message = f'Product "{product.name}" (SKU: {product.sku}) expires in {days_until_expiry} days on {product.expiry_date}. Immediate action required!'
            else:
                priority = 'high'
                title = f'Product Expiring Soon: {product.name}'
                message = f'Product "{product.name}" (SKU: {product.sku}) expires in {days_until_expiry} days on {product.expiry_date}. Please review inventory.'
            
            notification = NotificationService.create_notification(
                notification_type='expiry_soon',
                title=title,
                message=message,
                product=product,
                priority=priority
            )
            
            NotificationService.send_email_notification(notification)
            notifications_created += 1
        
        # Handle expired products
        for product in expired_products:
            days_expired = (today - product.expiry_date).days
            
            notification = NotificationService.create_notification(
                notification_type='expired',
                title=f'EXPIRED PRODUCT: {product.name}',
                message=f'Product "{product.name}" (SKU: {product.sku}) expired {days_expired} days ago on {product.expiry_date}. Remove from inventory immediately!',
                product=product,
                priority='urgent'
            )
            
            NotificationService.send_email_notification(notification)
            notifications_created += 1
        
        return notifications_created
    
    @staticmethod
    def check_reorder_alerts():
        """Check for products that need reordering"""
        from django.db import models
        
        reorder_products = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=models.F('reorder_level')
        ).exclude(
            # Don't create duplicate notifications
            notifications__type='reorder_needed',
            notifications__created_at__gte=timezone.now() - timedelta(days=1)
        )
        
        notifications_created = 0
        for product in reorder_products:
            notification = NotificationService.create_notification(
                notification_type='reorder_needed',
                title=f'Reorder Needed: {product.name}',
                message=f'Product "{product.name}" (SKU: {product.sku}) has reached reorder level. Current stock: {product.stock_quantity}, Reorder level: {product.reorder_level}',
                product=product,
                priority='medium'
            )
            
            NotificationService.send_email_notification(notification)
            notifications_created += 1
        
        return notifications_created
    
    @staticmethod
    def run_all_checks():
        """Run all notification checks"""
        low_stock_count = NotificationService.check_low_stock_alerts()
        expiry_count = NotificationService.check_expiry_alerts()
        reorder_count = NotificationService.check_reorder_alerts()
        
        return {
            'low_stock': low_stock_count,
            'expiry': expiry_count,
            'reorder': reorder_count,
            'total': low_stock_count + expiry_count + reorder_count
        }
    
    @staticmethod
    def run_scheduled_checks():
        """Run all scheduled notification checks (alias for run_all_checks)"""
        return NotificationService.run_all_checks()
