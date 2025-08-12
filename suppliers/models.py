from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import uuid


class Supplier(models.Model):
    """Supplier model for managing product suppliers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    logo = models.ImageField(upload_to='suppliers/', blank=True, null=True)
    email = models.EmailField(unique=True)
    website = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    tax_number = models.CharField(max_length=50, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        blank=True, 
        null=True
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('suppliers:supplier_detail', kwargs={'pk': self.pk})

    def get_products_count(self):
        """Get count of products from this supplier"""
        return SupplierProduct.objects.filter(
            supplier=self,
            product__is_active=True
        ).count()

    def get_total_products_value(self):
        """Get total value of products from this supplier"""
        total = 0
        supplier_products = SupplierProduct.objects.filter(
            supplier=self,
            product__is_active=True
        ).select_related('product')
        
        for supplier_product in supplier_products:
            product = supplier_product.product
            total += product.stock_quantity * product.unit_price
        return total

    def get_products(self):
        """Get all products from this supplier"""
        from products.models import Product
        return Product.objects.filter(
            supplierproduct__supplier=self,
            is_active=True
        ).distinct()

    @property
    def rating_display(self):
        """Get rating as stars"""
        if not self.rating:
            return "No rating"
        
        full_stars = int(self.rating)
        half_star = (self.rating - full_stars) >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        stars = "★" * full_stars
        if half_star:
            stars += "☆"
        stars += "☆" * empty_stars
        
        return f"{stars} ({self.rating})"

    def get_contact_info(self):
        """Get formatted contact information"""
        info = []
        if self.contact_person:
            info.append(f"Contact: {self.contact_person}")
        if self.phone_number:
            info.append(f"Phone: {self.phone_number}")
        if self.email:
            info.append(f"Email: {self.email}")
        return " | ".join(info)


class SupplierProduct(models.Model):
    """Many-to-many relationship between suppliers and products with additional fields"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    supplier_sku = models.CharField(max_length=100, blank=True, null=True, help_text="Supplier's SKU for this product")
    supplier_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lead_time_days = models.IntegerField(blank=True, null=True, help_text="Days to deliver")
    minimum_order_quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    is_preferred = models.BooleanField(default=False, help_text="Is this the preferred supplier for this product?")
    last_order_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['supplier', 'product']
        ordering = ['-is_preferred', 'supplier_price']

    def __str__(self):
        return f"{self.supplier.name} - {self.product.name}"

    @property
    def price_difference(self):
        """Calculate price difference from product's unit price"""
        if not self.supplier_price:
            return None
        return self.supplier_price - self.product.unit_price

    @property
    def is_cheapest(self):
        """Check if this is the cheapest supplier for this product"""
        if not self.supplier_price:
            return False
        
        cheapest_price = SupplierProduct.objects.filter(
            product=self.product,
            supplier_price__isnull=False
        ).aggregate(min_price=models.Min('supplier_price'))['min_price']
        
        return self.supplier_price == cheapest_price