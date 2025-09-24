from rest_framework import serializers
from django.contrib.auth.models import User
from products.models import (
    FootwearProduct, FootwearCategory, Material, SizeChart, SizeConversion,
    BillOfMaterials, WholesaleCustomer, CustomDesign, ProductionOrder
)
from accounting.models import (
    Invoice, InvoiceItem, Payment, ChartOfAccounts, JournalEntry,
    TaxRate, InventoryValuation
)

# User serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id']

# Product serializers
class FootwearCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FootwearCategory
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class SizeChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeChart
        fields = '__all__'

class SizeConversionSerializer(serializers.ModelSerializer):
    size_chart = SizeChartSerializer(read_only=True)
    
    class Meta:
        model = SizeConversion
        fields = '__all__'

class BillOfMaterialsSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    cost = serializers.ReadOnlyField()
    
    class Meta:
        model = BillOfMaterials
        fields = '__all__'

class FootwearProductSerializer(serializers.ModelSerializer):
    category = FootwearCategorySerializer(read_only=True)
    available_materials = MaterialSerializer(many=True, read_only=True)
    available_sizes = SizeConversionSerializer(many=True, read_only=True)
    bom_items = BillOfMaterialsSerializer(many=True, read_only=True)
    
    class Meta:
        model = FootwearProduct
        fields = '__all__'

class FootwearProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootwearProduct
        fields = '__all__'

class WholesaleCustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = WholesaleCustomer
        fields = '__all__'

class CustomDesignSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    base_product = FootwearProductSerializer(read_only=True)
    selected_materials = MaterialSerializer(many=True, read_only=True)
    size = SizeConversionSerializer(read_only=True)
    
    class Meta:
        model = CustomDesign
        fields = '__all__'

class ProductionOrderSerializer(serializers.ModelSerializer):
    product = FootwearProductSerializer(read_only=True)
    custom_design = CustomDesignSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ProductionOrder
        fields = '__all__'

# Accounting serializers
class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = '__all__'

class ChartOfAccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccounts
        fields = '__all__'

class InvoiceItemSerializer(serializers.ModelSerializer):
    product = FootwearProductSerializer(read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    processed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    wholesale_customer = WholesaleCustomerSerializer(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    balance_due = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = '__all__'

class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Invoice
        fields = ['customer', 'wholesale_customer', 'billing_name', 'billing_address',
                 'billing_email', 'billing_phone', 'tax_id', 'due_date', 'notes',
                 'terms_conditions', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        return invoice

class JournalEntrySerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    is_balanced = serializers.ReadOnlyField()
    
    class Meta:
        model = JournalEntry
        fields = '__all__'

class InventoryValuationSerializer(serializers.ModelSerializer):
    product = FootwearProductSerializer(read_only=True)
    
    class Meta:
        model = InventoryValuation
        fields = '__all__'

# Dashboard and analytics serializers
class DashboardStatsSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    pending_invoices = serializers.IntegerField()
    overdue_invoices = serializers.IntegerField()
    active_customers = serializers.IntegerField()
    products_in_production = serializers.IntegerField()
    inventory_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_revenue = serializers.ListField(child=serializers.DictField())
    top_products = serializers.ListField(child=serializers.DictField())
    recent_orders = ProductionOrderSerializer(many=True, read_only=True)

class SizeConverterSerializer(serializers.Serializer):
    from_size = serializers.CharField(max_length=10)
    from_region = serializers.CharField(max_length=2)
    to_region = serializers.CharField(max_length=2)
    gender = serializers.CharField(max_length=1)
    converted_size = serializers.CharField(max_length=10, read_only=True)