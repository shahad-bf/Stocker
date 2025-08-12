from django.core.management.base import BaseCommand
from inventory.services import NotificationService
from notifications.models import Notification
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Send pending email notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force send all notifications even if already sent',
        )
        parser.add_argument(
            '--type',
            type=str,
            help='Send notifications of specific type only',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting notification sending process...')
        
        # Get notifications to send
        notifications = Notification.objects.filter(is_email_sent=False)
        
        if options['type']:
            notifications = notifications.filter(type=options['type'])
            self.stdout.write(f'Filtering by type: {options["type"]}')
        
        if options['force']:
            notifications = Notification.objects.all()
            if options['type']:
                notifications = notifications.filter(type=options['type'])
            self.stdout.write('Force mode: will send all notifications')
        
        count = notifications.count()
        self.stdout.write(f'Found {count} notifications to send')
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No notifications to send'))
            return
        
        # Send notifications
        sent_count = 0
        failed_count = 0
        
        for notification in notifications:
            try:
                result = NotificationService.send_email_notification(notification)
                if result:
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Sent: {notification.title}')
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed: {notification.title}')
                    )
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error sending {notification.title}: {e}')
                )
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total notifications: {count}')
        self.stdout.write(f'Successfully sent: {sent_count}')
        self.stdout.write(f'Failed: {failed_count}')
        
        if sent_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent {sent_count} notifications')
            )
        
        if failed_count > 0:
            self.stdout.write(
                self.style.ERROR(f'Failed to send {failed_count} notifications')
            )
