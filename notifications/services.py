from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from .models import Notification, NotificationTemplate
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications"""
    
    @staticmethod
    def create_notification(notification_type, title, message, product=None, user=None, priority='medium', extra_data=None):
        """Create a new notification"""
        return Notification.create_notification(
            notification_type=notification_type,
            title=title,
            message=message,
            product=product,
            user=user,
            priority=priority,
            extra_data=extra_data or {}
        )
    
    @staticmethod
    def send_email_notification(notification):
        """Send email notification"""
        try:
            # Determine recipients
            recipients = []
            
            if notification.user:
                recipients = [notification.user.email]
            else:
                # Send to all admin users
                from accounts.models import UserProfile
                admin_users = User.objects.filter(
                    profile__role__in=['admin', 'manager'],
                    email__isnull=False
                ).exclude(email='')
                recipients = [user.email for user in admin_users]
            
            if not recipients:
                logger.warning(f"No recipients found for notification {notification.id}")
                return False
            
            # Render email content
            context = {
                'notification': notification,
                'site_name': 'Inventory Plus',
            }
            
            html_message = render_to_string('emails/notification_email.html', context)
            plain_message = f"""
{notification.title}

{notification.message}

Priority: {notification.get_priority_display()}
Type: {notification.get_type_display()}
Created: {notification.created_at}

---
Inventory Plus System
"""
            
            # Send email
            send_mail(
                subject=f"[Inventory Plus] {notification.title}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                html_message=html_message,
                fail_silently=False,
            )
            
            # Mark as sent
            notification.send_email()
            logger.info(f"Email sent for notification {notification.id} to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email for notification {notification.id}: {str(e)}")
            return False
    
    @staticmethod
    def check_low_stock_alerts():
        """Check for low stock products and create notifications"""
        from products.models import Product
        
        low_stock_products = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=models.F('minimum_stock')
        ).exclude(
            notifications__type='low_stock',
            notifications__created_at__date=timezone.now().date()
        )
        
        notifications_created = 0
        for product in low_stock_products:
            notification = NotificationService.create_notification(
                notification_type='low_stock',
                title=f'Low Stock Alert: {product.name}',
                message=f'Product {product.name} (SKU: {product.sku}) is running low on stock. Current quantity: {product.stock_quantity}, Minimum required: {product.minimum_stock}',
                product=product,
                priority='high' if product.stock_quantity == 0 else 'medium'
            )
            
            # Send email if configured
            if hasattr(settings, 'SEND_LOW_STOCK_EMAILS') and settings.SEND_LOW_STOCK_EMAILS:
                NotificationService.send_email_notification(notification)
            
            notifications_created += 1
        
        return notifications_created
    
    @staticmethod
    def check_expiry_alerts():
        """Check for expiring products and create notifications"""
        from products.models import Product
        from django.utils import timezone
        from datetime import timedelta
        
        # Products expiring within 7 days
        expiry_date_threshold = timezone.now().date() + timedelta(days=7)
        
        expiring_products = Product.objects.filter(
            is_active=True,
            has_expiry=True,
            expiry_date__lte=expiry_date_threshold,
            expiry_date__gt=timezone.now().date()
        ).exclude(
            notifications__type='expiry_soon',
            notifications__created_at__date=timezone.now().date()
        )
        
        notifications_created = 0
        for product in expiring_products:
            days_until_expiry = (product.expiry_date - timezone.now().date()).days
            
            notification = NotificationService.create_notification(
                notification_type='expiry_soon',
                title=f'Product Expiring Soon: {product.name}',
                message=f'Product {product.name} (SKU: {product.sku}) will expire in {days_until_expiry} days on {product.expiry_date}',
                product=product,
                priority='high' if days_until_expiry <= 3 else 'medium'
            )
            
            notifications_created += 1
        
        # Already expired products
        expired_products = Product.objects.filter(
            is_active=True,
            has_expiry=True,
            expiry_date__lt=timezone.now().date()
        ).exclude(
            notifications__type='expired',
            notifications__created_at__date=timezone.now().date()
        )
        
        for product in expired_products:
            notification = NotificationService.create_notification(
                notification_type='expired',
                title=f'Expired Product: {product.name}',
                message=f'Product {product.name} (SKU: {product.sku}) has expired on {product.expiry_date}. Please remove from inventory.',
                product=product,
                priority='urgent'
            )
            
            notifications_created += 1
        
        return notifications_created
    
    @staticmethod
    def create_stock_movement_notification(stock_movement):
        """Create notification for significant stock movements"""
        if stock_movement.movement_type in ['out', 'damaged', 'expired']:
            # Only create notifications for significant outbound movements
            if stock_movement.quantity >= stock_movement.product.minimum_stock * 0.5:
                NotificationService.create_notification(
                    notification_type='system',
                    title=f'Significant Stock Movement: {stock_movement.product.name}',
                    message=f'{stock_movement.get_movement_type_display()} of {stock_movement.quantity} units for {stock_movement.product.name} (SKU: {stock_movement.product.sku})',
                    product=stock_movement.product,
                    priority='medium'
                )
    
    @staticmethod
    def run_scheduled_checks():
        """Run all scheduled notification checks"""
        low_stock_count = NotificationService.check_low_stock_alerts()
        expiry_count = NotificationService.check_expiry_alerts()
        
        logger.info(f"Scheduled notification check completed: {low_stock_count} low stock alerts, {expiry_count} expiry alerts created")
        
        return {
            'low_stock_alerts': low_stock_count,
            'expiry_alerts': expiry_count
        }
