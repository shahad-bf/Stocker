from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import uuid


class Category(models.Model):
    """Category model for organizing products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'pk': self.pk})

    def get_products_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """Product model for inventory items"""
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('ltr', 'Liters'),
        ('box', 'Boxes'),
        ('pack', 'Packs'),
        ('meter', 'Meters'),
        ('dozen', 'Dozens'),
        ('set', 'Sets'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    
    # Stock Management
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    minimum_stock = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    maximum_stock = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    reorder_level = models.IntegerField(default=20, validators=[MinValueValidator(0)])
    
    # Product Details
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True, help_text="L x W x H")
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Expiry Management
    has_expiry = models.BooleanField(default=False)
    expiry_date = models.DateField(blank=True, null=True)
    shelf_life_days = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    
    # Images
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Status and Metadata
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    last_updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='updated_products'
    )

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'pk': self.pk})

    @property
    def is_low_stock(self):
        """Check if product is below minimum stock level"""
        return self.stock_quantity <= self.minimum_stock

    @property
    def is_out_of_stock(self):
        """Check if product is out of stock"""
        return self.stock_quantity == 0

    @property
    def is_expired(self):
        """Check if product is expired"""
        if not self.has_expiry or not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()

    @property
    def is_expiring_soon(self):
        """Check if product is expiring within 7 days"""
        if not self.has_expiry or not self.expiry_date:
            return False
        return self.expiry_date <= (timezone.now().date() + timedelta(days=7))

    @property
    def stock_value(self):
        """Calculate total stock value"""
        return self.stock_quantity * self.unit_price
    
    @property
    def formatted_unit_price(self):
        """Get formatted unit price with SAR currency"""
        return f"{self.unit_price:.2f} SAR"
    
    @property
    def formatted_stock_value(self):
        """Get formatted stock value with SAR currency"""
        return f"{self.stock_value:.2f} SAR"

    @property
    def stock_status(self):
        """Get stock status as string"""
        if self.is_out_of_stock:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'

    @property
    def stock_status_display(self):
        """Get human readable stock status"""
        status_map = {
            'out_of_stock': 'Out of Stock',
            'low_stock': 'Low Stock',
            'in_stock': 'In Stock'
        }
        return status_map.get(self.stock_status, 'Unknown')

    def get_suppliers(self):
        """Get all suppliers for this product"""
        # This will need to be imported from suppliers app
        from suppliers.models import Supplier
        return Supplier.objects.filter(products=self)

    def days_until_expiry(self):
        """Get days until expiry"""
        if not self.has_expiry or not self.expiry_date:
            return None
        
        today = timezone.now().date()
        if self.expiry_date < today:
            return 0  # Already expired
        
        return (self.expiry_date - today).days

    def can_be_deleted(self):
        """Check if product can be safely deleted"""
        # Check if product has stock movements
        from inventory.models import StockMovement
        return not StockMovement.objects.filter(product=self).exists()

    def save(self, *args, **kwargs):
        """Override save to ensure SKU is uppercase"""
        if self.sku:
            self.sku = self.sku.upper()
        super().save(*args, **kwargs)