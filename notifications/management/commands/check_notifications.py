from django.core.management.base import BaseCommand
from notifications.services import NotificationService


class Command(BaseCommand):
    help = 'Check for low stock and expiry notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-emails',
            action='store_true',
            help='Send email notifications for urgent alerts',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting notification checks...'))
        
        results = NotificationService.run_scheduled_checks()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Notification check completed:\n'
                f'- Low stock alerts: {results["low_stock_alerts"]}\n'
                f'- Expiry alerts: {results["expiry_alerts"]}'
            )
        )
        
        if options['send_emails']:
            from notifications.models import Notification
            urgent_notifications = Notification.objects.filter(
                priority='urgent',
                is_email_sent=False
            )
            
            emails_sent = 0
            for notification in urgent_notifications:
                if NotificationService.send_email_notification(notification):
                    emails_sent += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Sent {emails_sent} urgent email notifications')
            )
