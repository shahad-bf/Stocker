from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Category, Product
from suppliers.models import Supplier
from accounts.models import UserProfile
import random


class Command(BaseCommand):
    help = 'Create sample data for Inventory Plus'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create employee user
        employee_user, created = User.objects.get_or_create(
            username='employee',
            defaults={
                'email': 'employee@inventoryplus.com',
                'first_name': 'John',
                'last_name': 'Employee',
                'is_active': True
            }
        )
        if created:
            employee_user.set_password('emp123')
            employee_user.save()
            employee_user.profile.role = 'employee'
            employee_user.profile.department = 'Warehouse'
            employee_user.profile.save()
            self.stdout.write(f'Created employee user: {employee_user.username}')

        # Set admin user profile
        admin_user = User.objects.get(username='admin')
        admin_user.profile.role = 'admin'
        admin_user.profile.department = 'Management'
        admin_user.profile.save()

        # Create categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and components'},
            {'name': 'Office Supplies', 'description': 'Office equipment and stationery'},
            {'name': 'Furniture', 'description': 'Office and home furniture'},
            {'name': 'Books', 'description': 'Books and educational materials'},
            {'name': 'Clothing', 'description': 'Apparel and accessories'},
            {'name': 'Food & Beverages', 'description': 'Food items and drinks'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'created_by': admin_user,
                    'is_active': True
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create suppliers
        suppliers_data = [
            {
                'name': 'TechCorp Solutions',
                'email': 'contact@techcorp.com',
                'phone_number': '+1-555-0101',
                'website': 'https://techcorp.com',
                'contact_person': 'Sarah Johnson',
                'rating': 4.5
            },
            {
                'name': 'Office Pro Supply',
                'email': 'sales@officepro.com',
                'phone_number': '+1-555-0102',
                'website': 'https://officepro.com',
                'contact_person': 'Mike Chen',
                'rating': 4.2
            },
            {
                'name': 'FurnitureMax',
                'email': 'orders@furnituremax.com',
                'phone_number': '+1-555-0103',
                'website': 'https://furnituremax.com',
                'contact_person': 'Lisa Brown',
                'rating': 4.8
            },
            {
                'name': 'BookWorld Publishers',
                'email': 'info@bookworld.com',
                'phone_number': '+1-555-0104',
                'contact_person': 'David Wilson',
                'rating': 4.3
            },
        ]

        suppliers = []
        for sup_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=sup_data['name'],
                defaults={
                    'email': sup_data['email'],
                    'phone_number': sup_data['phone_number'],
                    'website': sup_data.get('website'),
                    'contact_person': sup_data['contact_person'],
                    'rating': sup_data['rating'],
                    'created_by': admin_user,
                    'is_active': True
                }
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')

        # Create products
        products_data = [
            # Electronics
            {
                'name': 'Laptop Dell Inspiron 15',
                'sku': 'DELL-INS-001',
                'category': 'Electronics',
                'unit_price': 899.99,
                'cost_price': 699.99,
                'stock_quantity': 25,
                'minimum_stock': 5,
                'unit': 'pcs',
                'description': 'High-performance laptop for business use',
                'suppliers': ['TechCorp Solutions']
            },
            {
                'name': 'Wireless Mouse Logitech',
                'sku': 'LOGI-MOU-001',
                'category': 'Electronics',
                'unit_price': 29.99,
                'cost_price': 19.99,
                'stock_quantity': 150,
                'minimum_stock': 20,
                'unit': 'pcs',
                'description': 'Ergonomic wireless mouse',
                'suppliers': ['TechCorp Solutions']
            },
            {
                'name': 'USB-C Hub 7-in-1',
                'sku': 'HUB-USB-001',
                'category': 'Electronics',
                'unit_price': 49.99,
                'cost_price': 29.99,
                'stock_quantity': 8,  # Low stock
                'minimum_stock': 15,
                'unit': 'pcs',
                'description': '7-port USB-C hub with HDMI',
                'suppliers': ['TechCorp Solutions']
            },
            
            # Office Supplies
            {
                'name': 'A4 Paper Ream',
                'sku': 'PAP-A4-001',
                'category': 'Office Supplies',
                'unit_price': 12.99,
                'cost_price': 8.99,
                'stock_quantity': 200,
                'minimum_stock': 50,
                'unit': 'pack',
                'description': 'High-quality A4 printing paper',
                'suppliers': ['Office Pro Supply']
            },
            {
                'name': 'Blue Ink Pens (Pack of 10)',
                'sku': 'PEN-BLU-001',
                'category': 'Office Supplies',
                'unit_price': 8.99,
                'cost_price': 5.99,
                'stock_quantity': 0,  # Out of stock
                'minimum_stock': 25,
                'unit': 'pack',
                'description': 'Smooth writing blue ink pens',
                'suppliers': ['Office Pro Supply']
            },
            {
                'name': 'Sticky Notes Multicolor',
                'sku': 'STI-NOT-001',
                'category': 'Office Supplies',
                'unit_price': 4.99,
                'cost_price': 2.99,
                'stock_quantity': 75,
                'minimum_stock': 20,
                'unit': 'pack',
                'description': 'Colorful sticky notes for organization',
                'suppliers': ['Office Pro Supply']
            },
            
            # Furniture
            {
                'name': 'Office Chair Executive',
                'sku': 'CHA-EXE-001',
                'category': 'Furniture',
                'unit_price': 299.99,
                'cost_price': 199.99,
                'stock_quantity': 12,
                'minimum_stock': 3,
                'unit': 'pcs',
                'description': 'Ergonomic executive office chair',
                'suppliers': ['FurnitureMax']
            },
            {
                'name': 'Standing Desk Adjustable',
                'sku': 'DSK-STD-001',
                'category': 'Furniture',
                'unit_price': 549.99,
                'cost_price': 399.99,
                'stock_quantity': 6,
                'minimum_stock': 2,
                'unit': 'pcs',
                'description': 'Height-adjustable standing desk',
                'suppliers': ['FurnitureMax']
            },
            
            # Books
            {
                'name': 'Python Programming Guide',
                'sku': 'BOO-PYT-001',
                'category': 'Books',
                'unit_price': 39.99,
                'cost_price': 24.99,
                'stock_quantity': 45,
                'minimum_stock': 10,
                'unit': 'pcs',
                'description': 'Comprehensive Python programming book',
                'suppliers': ['BookWorld Publishers']
            },
            {
                'name': 'Business Management Handbook',
                'sku': 'BOO-BUS-001',
                'category': 'Books',
                'unit_price': 49.99,
                'cost_price': 29.99,
                'stock_quantity': 2,  # Low stock
                'minimum_stock': 8,
                'unit': 'pcs',
                'description': 'Essential business management principles',
                'suppliers': ['BookWorld Publishers']
            },
        ]

        # Create products
        for prod_data in products_data:
            category = Category.objects.get(name=prod_data['category'])
            
            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'category': category,
                    'unit_price': prod_data['unit_price'],
                    'cost_price': prod_data['cost_price'],
                    'stock_quantity': prod_data['stock_quantity'],
                    'minimum_stock': prod_data['minimum_stock'],
                    'unit': prod_data['unit'],
                    'description': prod_data['description'],
                    'created_by': admin_user,
                    'is_active': True
                }
            )
            
            if created:
                # Add suppliers
                for supplier_name in prod_data['suppliers']:
                    supplier = Supplier.objects.get(name=supplier_name)
                    product.suppliers.add(supplier)
                
                self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data!\n'
                f'- Categories: {Category.objects.count()}\n'
                f'- Suppliers: {Supplier.objects.count()}\n'
                f'- Products: {Product.objects.count()}\n'
                f'- Users: {User.objects.count()}\n\n'
                f'Login credentials:\n'
                f'Admin: admin / admin123\n'
                f'Employee: employee / emp123'
            )
        )
