from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

# Size and measurement models
class SizeChart(models.Model):
    """Standard size charts for different regions and footwear types"""
    REGION_CHOICES = [
        ('US', 'United States'),
        ('EU', 'European Union'),
        ('UK', 'United Kingdom'),
        ('JP', 'Japan'),
        ('CN', 'China'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('K', 'Kids'),
        ('U', 'Unisex'),
    ]
    
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=2, choices=REGION_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['region', 'gender']
    
    def __str__(self):
        return f"{self.name} ({self.region} - {self.gender})"

class SizeConversion(models.Model):
    """Size conversion table between different regional standards"""
    size_chart = models.ForeignKey(SizeChart, on_delete=models.CASCADE)
    size_value = models.CharField(max_length=10)  # e.g., "8.5", "42", "M"
    length_mm = models.DecimalField(max_digits=6, decimal_places=2)  # foot length in mm
    width_mm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ['size_chart', 'size_value']
    
    def __str__(self):
        return f"{self.size_chart.region} {self.size_value}"

# Product and customization models
class FootwearCategory(models.Model):
    """Categories of footwear products"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Footwear Categories"
    
    def __str__(self):
        return self.name

class Material(models.Model):
    """Materials used in footwear production"""
    MATERIAL_TYPES = [
        ('leather', 'Leather'),
        ('synthetic', 'Synthetic'),
        ('fabric', 'Fabric'),
        ('rubber', 'Rubber'),
        ('foam', 'Foam'),
        ('metal', 'Metal'),
        ('plastic', 'Plastic'),
    ]
    
    name = models.CharField(max_length=100)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    color = models.CharField(max_length=50)
    supplier = models.CharField(max_length=100)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    unit_of_measure = models.CharField(max_length=20, default='sq_ft')  # sq_ft, meters, pieces
    minimum_order = models.IntegerField(default=1)
    lead_time_days = models.IntegerField(default=7)
    
    def __str__(self):
        return f"{self.name} ({self.color})"

class FootwearProduct(models.Model):
    """Extended product model for footwear-specific attributes"""
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('K', 'Kids'),
        ('U', 'Unisex'),
    ]
    
    # Basic product info
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(FootwearCategory, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Footwear-specific attributes
    heel_height = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # in mm
    sole_thickness = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # in mm
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # in grams
    
    # Customization options
    customizable = models.BooleanField(default=False)
    available_sizes = models.ManyToManyField(SizeConversion)
    available_materials = models.ManyToManyField(Material)
    
    # Production info
    production_time_days = models.IntegerField(default=14)
    minimum_order_quantity = models.IntegerField(default=1)
    
    # Status and metadata
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def get_price_for_quantity(self, quantity):
        """Calculate price based on quantity (bulk pricing)"""
        if quantity >= 100:
            return self.base_price * Decimal('0.8')  # 20% discount
        elif quantity >= 50:
            return self.base_price * Decimal('0.9')  # 10% discount
        return self.base_price

class BillOfMaterials(models.Model):
    """Materials required to produce a footwear product"""
    product = models.ForeignKey(FootwearProduct, on_delete=models.CASCADE, related_name='bom_items')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_required = models.DecimalField(max_digits=8, decimal_places=3)
    component_name = models.CharField(max_length=100)  # e.g., "Upper", "Sole", "Laces"
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['product', 'material', 'component_name']
    
    def __str__(self):
        return f"{self.product.name} - {self.material.name} ({self.component_name})"
    
    @property
    def cost(self):
        return self.quantity_required * self.material.cost_per_unit

# Customer and order models
class WholesaleCustomer(models.Model):
    """B2B customer information"""
    DISCOUNT_TIERS = [
        ('bronze', 'Bronze (5%)'),
        ('silver', 'Silver (10%)'),
        ('gold', 'Gold (15%)'),
        ('platinum', 'Platinum (20%)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    tax_id = models.CharField(max_length=50, blank=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_tier = models.CharField(max_length=20, choices=DISCOUNT_TIERS, default='bronze')
    payment_terms = models.IntegerField(default=30)  # days
    
    # Contact info
    billing_address = models.TextField()
    shipping_address = models.TextField()
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Status
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.business_name
    
    def get_discount_percentage(self):
        discount_map = {
            'bronze': 5,
            'silver': 10,
            'gold': 15,
            'platinum': 20,
        }
        return discount_map.get(self.discount_tier, 0)

class CustomDesign(models.Model):
    """Customer's custom design for a footwear product"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    base_product = models.ForeignKey(FootwearProduct, on_delete=models.CASCADE)
    design_name = models.CharField(max_length=100)
    
    # Customization choices
    selected_materials = models.ManyToManyField(Material, through='DesignMaterial')
    custom_colors = models.JSONField(default=dict)  # {"upper": "#FF0000", "sole": "#000000"}
    size = models.ForeignKey(SizeConversion, on_delete=models.CASCADE)
    special_instructions = models.TextField(blank=True)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    customization_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.base_price + self.customization_fee
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.design_name} by {self.customer.username}"

class DesignMaterial(models.Model):
    """Through model for custom design materials"""
    design = models.ForeignKey(CustomDesign, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    component = models.CharField(max_length=50)  # "upper", "sole", "laces", etc.
    
    class Meta:
        unique_together = ['design', 'component']

# Production and inventory models
class ProductionOrder(models.Model):
    """Production order for manufacturing footwear"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_production', 'In Production'),
        ('quality_check', 'Quality Check'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(FootwearProduct, on_delete=models.CASCADE)
    custom_design = models.ForeignKey(CustomDesign, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    size_breakdown = models.JSONField(default=dict)  # {"US8": 10, "US9": 15, ...}
    
    # Timeline
    start_date = models.DateField(null=True, blank=True)
    expected_completion = models.DateField()
    actual_completion = models.DateField(null=True, blank=True)
    
    # Status and costs
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    material_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overhead_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"PO{timezone.now().strftime('%Y%m%d')}{self.pk or '001'}"
        
        # Calculate total cost
        self.total_cost = self.material_cost + self.labor_cost + self.overhead_cost
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"PO {self.order_number} - {self.product.name}"
