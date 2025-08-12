from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Notification
from .services import NotificationService


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        ).order_by('-created_at')


class NotificationDetailView(LoginRequiredMixin, DetailView):
    model = Notification
    template_name = 'notifications/notification_detail.html'
    context_object_name = 'notification'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Mark as read when viewed
        if not obj.is_read:
            obj.mark_as_read(self.request.user)
        return obj


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.mark_as_read(request.user)
    messages.success(request, 'Notification marked as read.')
    return redirect('notifications:notification_list')


@login_required
def mark_all_notifications_read(request):
    count = Notification.objects.filter(
        Q(user=request.user) | Q(user__isnull=True),
        is_read=False
    ).update(is_read=True)
    
    messages.success(request, f'{count} notifications marked as read.')
    return redirect('notifications:notification_list')


@login_required
def send_notification_email(request, pk):
    """Send individual notification via email"""
    notification = get_object_or_404(Notification, pk=pk)
    
    if notification.is_email_sent:
        messages.warning(request, 'Email has already been sent for this notification.')
        return redirect('notifications:notification_detail', pk=pk)
    
    try:
        # Use the notification service to send email
        NotificationService.send_email_notification(notification)
        messages.success(request, f'Email sent successfully for: {notification.title}')
    except Exception as e:
        messages.error(request, f'Failed to send email: {str(e)}')
    
    return redirect('notifications:notification_detail', pk=pk)


@login_required
def send_all_notifications_email(request):
    """Send all unsent notifications via email"""
    notifications = Notification.objects.filter(
        Q(user=request.user) | Q(user__isnull=True),
        is_email_sent=False
    )
    
    if not notifications.exists():
        messages.info(request, 'No unsent notifications found.')
        return redirect('notifications:notification_list')
    
    sent_count = 0
    failed_count = 0
    
    for notification in notifications:
        try:
            NotificationService.send_email_notification(notification)
            sent_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to send email for notification {notification.id}: {str(e)}")
    
    if sent_count > 0:
        messages.success(request, f'Successfully sent {sent_count} email notifications.')
    if failed_count > 0:
        messages.warning(request, f'Failed to send {failed_count} email notifications.')
    
    return redirect('notifications:notification_list')


@login_required
def bulk_send_emails(request):
    """Bulk send emails for selected notifications"""
    if request.method == 'POST':
        notification_ids = request.POST.getlist('notification_ids')
        
        if not notification_ids:
            messages.warning(request, 'No notifications selected.')
            return redirect('notifications:notification_list')
        
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            is_email_sent=False
        )
        
        sent_count = 0
        failed_count = 0
        
        for notification in notifications:
            try:
                NotificationService.send_email_notification(notification)
                sent_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to send email for notification {notification.id}: {str(e)}")
        
        if sent_count > 0:
            messages.success(request, f'Successfully sent {sent_count} email notifications.')
        if failed_count > 0:
            messages.warning(request, f'Failed to send {failed_count} email notifications.')
    
    return redirect('notifications:notification_list')


@login_required
def generate_stock_notifications(request):
    """Generate real notifications based on current inventory status"""
    from products.models import Product
    from django.db import models
    from django.utils import timezone
    from datetime import timedelta
    
    notifications_created = 0
    
    try:
        # Check for low stock products
        low_stock_products = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=models.F('minimum_stock')
        ).exclude(
            # Avoid duplicates created today
            notifications__type__in=['low_stock', 'out_of_stock'],
            notifications__created_at__date=timezone.now().date()
        )
        
        for product in low_stock_products:
            if product.stock_quantity == 0:
                # Out of stock - urgent
                notification = Notification.create_notification(
                    notification_type='out_of_stock',
                    title=f'🚨 Out of Stock: {product.name}',
                    message=f'Product "{product.name}" (SKU: {product.sku}) is completely out of stock! '
                           f'Category: {product.category.name}. Immediate restocking required.',
                    product=product,
                    priority='urgent',
                    extra_data={
                        'current_stock': product.stock_quantity,
                        'minimum_stock': product.minimum_stock,
                        'category': product.category.name,
                        'unit_price': str(product.unit_price)
                    }
                )
            else:
                # Low stock - high priority
                notification = Notification.create_notification(
                    notification_type='low_stock',
                    title=f'⚠️ Low Stock Alert: {product.name}',
                    message=f'Product "{product.name}" (SKU: {product.sku}) is running low on stock. '
                           f'Current: {product.stock_quantity}, Minimum: {product.minimum_stock}, '
                           f'Category: {product.category.name}. Please reorder soon.',
                    product=product,
                    priority='high',
                    extra_data={
                        'current_stock': product.stock_quantity,
                        'minimum_stock': product.minimum_stock,
                        'category': product.category.name,
                        'unit_price': str(product.unit_price)
                    }
                )
            notifications_created += 1
        
        # Check for products that need reordering (below reorder level)
        reorder_products = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=models.F('reorder_level'),
            reorder_level__gt=0
        ).exclude(
            notifications__type='reorder_needed',
            notifications__created_at__date=timezone.now().date()
        ).exclude(
            # Don't duplicate if already has low stock alert today
            notifications__type__in=['low_stock', 'out_of_stock'],
            notifications__created_at__date=timezone.now().date()
        )
        
        for product in reorder_products:
            notification = Notification.create_notification(
                notification_type='reorder_needed',
                title=f'📦 Reorder Required: {product.name}',
                message=f'Product "{product.name}" (SKU: {product.sku}) has reached its reorder level. '
                       f'Current stock: {product.stock_quantity}, Reorder level: {product.reorder_level}. '
                       f'Consider placing a new order.',
                product=product,
                priority='medium',
                extra_data={
                    'current_stock': product.stock_quantity,
                    'reorder_level': product.reorder_level,
                    'category': product.category.name,
                    'suggested_order_quantity': max(product.maximum_stock - product.stock_quantity, 50) if product.maximum_stock else 50
                }
            )
            notifications_created += 1
        
        # Check for expiring products (if they have expiry dates)
        expiring_products = Product.objects.filter(
            is_active=True,
            has_expiry=True,
            expiry_date__isnull=False,
            expiry_date__lte=timezone.now().date() + timedelta(days=30)  # Expiring in 30 days
        ).exclude(
            notifications__type='expiry_soon',
            notifications__created_at__date=timezone.now().date()
        )
        
        for product in expiring_products:
            days_until_expiry = (product.expiry_date - timezone.now().date()).days
            
            if days_until_expiry < 0:
                # Already expired
                notification = Notification.create_notification(
                    notification_type='expired',
                    title=f'🚫 Expired Product: {product.name}',
                    message=f'Product "{product.name}" (SKU: {product.sku}) has expired on {product.expiry_date}. '
                           f'Remove from inventory immediately.',
                    product=product,
                    priority='urgent',
                    extra_data={
                        'expiry_date': str(product.expiry_date),
                        'days_expired': abs(days_until_expiry),
                        'current_stock': product.stock_quantity
                    }
                )
            else:
                # Expiring soon
                priority = 'urgent' if days_until_expiry <= 7 else 'high' if days_until_expiry <= 14 else 'medium'
                notification = Notification.create_notification(
                    notification_type='expiry_soon',
                    title=f'⏰ Expiring Soon: {product.name}',
                    message=f'Product "{product.name}" (SKU: {product.sku}) will expire in {days_until_expiry} days '
                           f'on {product.expiry_date}. Current stock: {product.stock_quantity}.',
                    product=product,
                    priority=priority,
                    extra_data={
                        'expiry_date': str(product.expiry_date),
                        'days_until_expiry': days_until_expiry,
                        'current_stock': product.stock_quantity
                    }
                )
            notifications_created += 1
        
        # Create system notification about the check
        if notifications_created > 0:
            Notification.create_notification(
                notification_type='system',
                title=f'📊 Stock Check Complete',
                message=f'Automatic stock check completed. Created {notifications_created} new notifications based on current inventory status.',
                priority='low',
                extra_data={
                    'notifications_created': notifications_created,
                    'check_time': timezone.now().isoformat(),
                    'checked_by': request.user.username
                }
            )
            messages.success(request, f'Successfully generated {notifications_created} notifications based on current inventory status!')
        else:
            messages.info(request, 'No new notifications needed. All products are within normal stock levels.')
            
    except Exception as e:
        messages.error(request, f'Error generating notifications: {str(e)}')
    
    return redirect('notifications:notification_list')


# API Views
@login_required
def notification_count_api(request):
    count = Notification.get_unread_count(request.user)
    urgent_count = Notification.get_urgent_count(request.user)
    
    return JsonResponse({
        'total_unread': count,
        'urgent_unread': urgent_count,
    })


@login_required
def recent_notifications_api(request):
    notifications = Notification.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).order_by('-created_at')[:10]
    
    data = {
        'notifications': [
            {
                'id': str(notification.id),
                'title': notification.title,
                'message': notification.message[:100] + '...' if len(notification.message) > 100 else notification.message,
                'type': notification.type,
                'priority': notification.priority,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
                'age_hours': notification.age_in_hours,
            }
            for notification in notifications
        ]
    }
    
    return JsonResponse(data)