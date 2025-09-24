from django.contrib import admin
from django.utils.html import format_html
from .models import (
    FootwearProduct, FootwearCategory, Material, SizeChart, SizeConversion,
    BillOfMaterials, WholesaleCustomer, CustomDesign, ProductionOrder
)

@admin.register(FootwearCategory)
class FootwearCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'material_type', 'color', 'supplier', 'cost_per_unit', 'unit_of_measure']
    list_filter = ['material_type', 'supplier']
    search_fields = ['name', 'color', 'supplier']
    list_editable = ['cost_per_unit']

@admin.register(SizeChart)
class SizeChartAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'gender', 'created_at']
    list_filter = ['region', 'gender']
    search_fields = ['name']

class SizeConversionInline(admin.TabularInline):
    model = SizeConversion
    extra = 1

@admin.register(SizeConversion)
class SizeConversionAdmin(admin.ModelAdmin):
    list_display = ['size_chart', 'size_value', 'length_mm', 'width_mm']
    list_filter = ['size_chart__region', 'size_chart__gender']
    search_fields = ['size_value']

class BillOfMaterialsInline(admin.TabularInline):
    model = BillOfMaterials
    extra = 1
    readonly_fields = ['cost']

@admin.register(FootwearProduct)
class FootwearProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'gender', 'base_price', 'customizable', 'active']
    list_filter = ['category', 'gender', 'customizable', 'active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    list_editable = ['base_price', 'active']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['available_materials', 'available_sizes']
    inlines = [BillOfMaterialsInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'category', 'gender', 'description', 'base_price')
        }),
        ('Physical Attributes', {
            'fields': ('heel_height', 'sole_thickness', 'weight')
        }),
        ('Customization', {
            'fields': ('customizable', 'available_materials', 'available_sizes')
        }),
        ('Production', {
            'fields': ('production_time_days', 'minimum_order_quantity')
        }),
        ('Status', {
            'fields': ('active', 'created_at', 'updated_at')
        }),
    )

@admin.register(BillOfMaterials)
class BillOfMaterialsAdmin(admin.ModelAdmin):
    list_display = ['product', 'material', 'component_name', 'quantity_required', 'cost']
    list_filter = ['product__category', 'material__material_type', 'component_name']
    search_fields = ['product__name', 'material__name', 'component_name']
    readonly_fields = ['cost']

@admin.register(WholesaleCustomer)
class WholesaleCustomerAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'discount_tier', 'credit_limit', 'approved', 'created_at']
    list_filter = ['discount_tier', 'approved', 'created_at']
    search_fields = ['business_name', 'contact_person', 'email', 'user__username']
    list_editable = ['approved']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Business Information', {
            'fields': ('business_name', 'tax_id', 'contact_person', 'phone', 'email')
        }),
        ('Financial Settings', {
            'fields': ('credit_limit', 'current_balance', 'discount_tier', 'payment_terms')
        }),
        ('Addresses', {
            'fields': ('billing_address', 'shipping_address')
        }),
        ('Status', {
            'fields': ('approved', 'created_at')
        }),
    )

@admin.register(CustomDesign)
class CustomDesignAdmin(admin.ModelAdmin):
    list_display = ['design_name', 'customer', 'base_product', 'total_price', 'approved', 'created_at']
    list_filter = ['approved', 'base_product__category', 'created_at']
    search_fields = ['design_name', 'customer__username', 'base_product__name']
    list_editable = ['approved']
    readonly_fields = ['total_price', 'created_at']

@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'product', 'quantity', 'status', 'expected_completion', 'total_cost']
    list_filter = ['status', 'product__category', 'start_date', 'expected_completion']
    search_fields = ['order_number', 'product__name']
    list_editable = ['status']
    readonly_fields = ['order_number', 'total_cost', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'product', 'custom_design', 'quantity', 'size_breakdown')
        }),
        ('Timeline', {
            'fields': ('start_date', 'expected_completion', 'actual_completion')
        }),
        ('Status & Costs', {
            'fields': ('status', 'material_cost', 'labor_cost', 'overhead_cost', 'total_cost')
        }),
        ('Additional Information', {
            'fields': ('created_by', 'created_at', 'notes')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_by',)
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not change:  # creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)