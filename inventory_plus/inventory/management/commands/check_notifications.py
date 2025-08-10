from django.core.management.base import BaseCommand
from django.utils import timezone
from inventory.services import NotificationService


class Command(BaseCommand):
    help = 'Check for inventory alerts and send notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['all', 'low_stock', 'expiry', 'reorder'],
            default='all',
            help='Type of notifications to check (default: all)',
        )
        parser.add_argument(
            '--send-email',
            action='store_true',
            help='Send email notifications (default: True)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually creating notifications',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Starting notification check...')
        )
        
        start_time = timezone.now()
        notification_type = options['type']
        send_email = options['send_email']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🧪 DRY RUN MODE - No notifications will be created')
            )
        
        results = {
            'low_stock': 0,
            'expiry': 0,
            'reorder': 0,
            'total': 0
        }
        
        try:
            if notification_type in ['all', 'low_stock']:
                self.stdout.write('📦 Checking low stock alerts...')
                if not dry_run:
                    count = NotificationService.check_low_stock_alerts()
                    results['low_stock'] = count
                    self.stdout.write(
                        self.style.SUCCESS(f'   ✅ Created {count} low stock notifications')
                    )
                else:
                    # For dry run, just count products that would trigger alerts
                    from products.models import Product
                    from django.db import models
                    count = Product.objects.filter(
                        is_active=True,
                        stock_quantity__lte=models.F('minimum_stock')
                    ).count()
                    self.stdout.write(
                        self.style.WARNING(f'   🧪 Would create {count} low stock notifications')
                    )
            
            if notification_type in ['all', 'expiry']:
                self.stdout.write('⏰ Checking expiry alerts...')
                if not dry_run:
                    count = NotificationService.check_expiry_alerts()
                    results['expiry'] = count
                    self.stdout.write(
                        self.style.SUCCESS(f'   ✅ Created {count} expiry notifications')
                    )
                else:
                    # For dry run, count products that would trigger alerts
                    from products.models import Product
                    from datetime import timedelta
                    today = timezone.now().date()
                    count = Product.objects.filter(
                        is_active=True,
                        has_expiry=True,
                        expiry_date__isnull=False,
                        expiry_date__lte=today + timedelta(days=7)
                    ).count()
                    self.stdout.write(
                        self.style.WARNING(f'   🧪 Would create {count} expiry notifications')
                    )
            
            if notification_type in ['all', 'reorder']:
                self.stdout.write('🔄 Checking reorder alerts...')
                if not dry_run:
                    count = NotificationService.check_reorder_alerts()
                    results['reorder'] = count
                    self.stdout.write(
                        self.style.SUCCESS(f'   ✅ Created {count} reorder notifications')
                    )
                else:
                    # For dry run, count products that would trigger alerts
                    from products.models import Product
                    from django.db import models
                    count = Product.objects.filter(
                        is_active=True,
                        stock_quantity__lte=models.F('reorder_level')
                    ).count()
                    self.stdout.write(
                        self.style.WARNING(f'   🧪 Would create {count} reorder notifications')
                    )
            
            # Calculate totals
            results['total'] = results['low_stock'] + results['expiry'] + results['reorder']
            
            # Summary
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('📊 NOTIFICATION CHECK SUMMARY'))
            self.stdout.write('='*50)
            
            if not dry_run:
                self.stdout.write(f'📦 Low Stock Notifications: {results["low_stock"]}')
                self.stdout.write(f'⏰ Expiry Notifications: {results["expiry"]}')
                self.stdout.write(f'🔄 Reorder Notifications: {results["reorder"]}')
                self.stdout.write(f'📧 Total Notifications Created: {results["total"]}')
            else:
                self.stdout.write(self.style.WARNING('🧪 DRY RUN - No notifications were actually created'))
            
            self.stdout.write(f'⏱️  Duration: {duration:.2f} seconds')
            self.stdout.write(f'🕐 Completed at: {end_time.strftime("%Y-%m-%d %H:%M:%S")}')
            
            if results['total'] > 0 and not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ Successfully processed {results["total"]} notifications!')
                )
            elif results['total'] == 0 and not dry_run:
                self.stdout.write(
                    self.style.SUCCESS('\n✅ No alerts needed - all inventory levels are good!')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during notification check: {str(e)}')
            )
            raise e
