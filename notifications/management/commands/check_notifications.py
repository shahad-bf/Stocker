from django.core.management.base import BaseCommand
from inventory.services import NotificationService
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Check and create notifications for inventory alerts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['low_stock', 'expiry', 'reorder', 'all'],
            default='all',
            help='Type of notifications to check',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting notification checks...')
        
        notification_type = options['type']
        
        if notification_type in ['low_stock', 'all']:
            self.stdout.write('\n--- Checking Low Stock Alerts ---')
            low_stock_count = NotificationService.check_low_stock_alerts()
            self.stdout.write(f'Low stock notifications created: {low_stock_count}')
        
        if notification_type in ['expiry', 'all']:
            self.stdout.write('\n--- Checking Expiry Alerts ---')
            expiry_count = NotificationService.check_expiry_alerts()
            self.stdout.write(f'Expiry notifications created: {expiry_count}')
        
        if notification_type in ['reorder', 'all']:
            self.stdout.write('\n--- Checking Reorder Alerts ---')
            reorder_count = NotificationService.check_reorder_alerts()
            self.stdout.write(f'Reorder notifications created: {reorder_count}')
        
        # Summary
        if notification_type == 'all':
            total_count = NotificationService.run_all_checks()
            self.stdout.write('\n' + '='*50)
            self.stdout.write('SUMMARY:')
            self.stdout.write(f'Low stock alerts: {total_count["low_stock"]}')
            self.stdout.write(f'Expiry alerts: {total_count["expiry"]}')
            self.stdout.write(f'Reorder alerts: {total_count["reorder"]}')
            self.stdout.write(f'Total notifications: {total_count["total"]}')
        
        # Show recent notifications
        recent_notifications = Notification.objects.all().order_by('-created_at')[:5]
        if recent_notifications.exists():
            self.stdout.write('\n--- Recent Notifications ---')
            for notification in recent_notifications:
                status = '✓ Sent' if notification.is_email_sent else '✗ Pending'
                self.stdout.write(
                    f'- {notification.title} ({notification.priority}) - {status}'
                )
        
        self.stdout.write(self.style.SUCCESS('\nNotification checks completed!'))
