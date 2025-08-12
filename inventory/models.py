from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class StockMovement(models.Model):
    """Track stock movements for audit purposes"""
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Stock Adjustment'),
        ('damaged', 'Damaged'),
        ('expired', 'Expired'),
        ('returned', 'Returned'),
        ('transfer', 'Transfer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['movement_type', 'created_at']),
            models.Index(fields=['created_by', 'created_at']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity}"

    @property
    def quantity_change(self):
        """Get the actual quantity change (positive or negative)"""
        if self.movement_type == 'in':
            return self.quantity
        elif self.movement_type == 'out':
            return -self.quantity
        else:  # adjustment
            return self.new_stock - self.previous_stock

    @property
    def total_value(self):
        """Calculate total value of this movement"""
        if self.unit_cost:
            return abs(self.quantity) * self.unit_cost
        return abs(self.quantity) * self.product.unit_price

    def save(self, *args, **kwargs):
        """Override save to ensure data consistency"""
        # Ensure quantity is positive for display purposes
        if self.quantity < 0:
            self.quantity = abs(self.quantity)
        
        super().save(*args, **kwargs)


class InventoryTransaction(models.Model):
    """Group multiple stock movements into a single transaction"""
    
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase Order'),
        ('sale', 'Sale'),
        ('adjustment', 'Inventory Adjustment'),
        ('transfer', 'Stock Transfer'),
        ('return', 'Return'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Related entities
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status and dates
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Financial information
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.reference_number}"

    def get_stock_movements(self):
        """Get all stock movements related to this transaction"""
        return StockMovement.objects.filter(reference_number=self.reference_number)

    def calculate_total(self):
        """Calculate total amount from stock movements"""
        total = 0
        for movement in self.get_stock_movements():
            if movement.unit_cost:
                total += abs(movement.quantity) * movement.unit_cost
            else:
                total += abs(movement.quantity) * movement.product.unit_price
        
        self.total_amount = total
        return total

    def complete_transaction(self, user=None):
        """Mark transaction as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if user:
            self.created_by = user
        self.save()

    def cancel_transaction(self):
        """Cancel transaction and reverse stock movements"""
        if self.status == 'completed':
            # Reverse all stock movements
            for movement in self.get_stock_movements():
                # Create reverse movement
                StockMovement.objects.create(
                    product=movement.product,
                    movement_type='adjustment',
                    quantity=abs(movement.quantity_change),
                    previous_stock=movement.product.stock_quantity,
                    new_stock=movement.product.stock_quantity - movement.quantity_change,
                    reference_number=f"REVERSE-{movement.reference_number}",
                    notes=f"Reversal of transaction {self.reference_number}",
                    created_by=movement.created_by
                )
                
                # Update product stock
                movement.product.stock_quantity -= movement.quantity_change
                movement.product.save()
        
        self.status = 'cancelled'
        self.save()


class StockAlert(models.Model):
    """Stock alert configuration for products"""
    
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('expiry_soon', 'Expiry Soon'),
        ('expired', 'Expired'),
        ('reorder_point', 'Reorder Point'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold_value = models.IntegerField(validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    
    # Recipients
    notify_users = models.ManyToManyField(User, blank=True, related_name='stock_alerts')
    notify_roles = models.JSONField(default=list, help_text="List of roles to notify")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_triggered = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['product', 'alert_type']
        ordering = ['product__name', 'alert_type']

    def __str__(self):
        return f"{self.product.name} - {self.get_alert_type_display()}"

    def should_trigger(self):
        """Check if alert should be triggered"""
        if not self.is_active:
            return False
        
        product = self.product
        
        if self.alert_type == 'low_stock':
            return product.stock_quantity <= self.threshold_value
        elif self.alert_type == 'out_of_stock':
            return product.stock_quantity == 0
        elif self.alert_type == 'expiry_soon':
            if not product.has_expiry or not product.expiry_date:
                return False
            days_until_expiry = (product.expiry_date - timezone.now().date()).days
            return days_until_expiry <= self.threshold_value
        elif self.alert_type == 'expired':
            if not product.has_expiry or not product.expiry_date:
                return False
            return product.expiry_date < timezone.now().date()
        elif self.alert_type == 'reorder_point':
            return product.stock_quantity <= self.threshold_value
        
        return False

    def trigger_alert(self):
        """Trigger the alert and create notification"""
        if not self.should_trigger():
            return None
        
        # Import here to avoid circular imports
        from notifications.models import Notification
        
        # Create notification
        notification = Notification.create_notification(
            notification_type=self.alert_type,
            title=f"{self.get_alert_type_display()}: {self.product.name}",
            message=f"Product {self.product.name} (SKU: {self.product.sku}) has triggered a {self.get_alert_type_display().lower()} alert.",
            product=self.product,
            priority='high' if self.alert_type in ['out_of_stock', 'expired'] else 'medium'
        )
        
        # Update last triggered time
        self.last_triggered = timezone.now()
        self.save()
        
        return notification