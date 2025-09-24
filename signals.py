# Django signals for products app
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductionOrder, BillOfMaterials

@receiver(post_save, sender=ProductionOrder)
def update_production_costs(sender, instance, created, **kwargs):
    """Update production costs when a production order is saved"""
    if instance.product and instance.material_cost == 0:
        # Calculate material cost from BOM
        bom_items = instance.product.bom_items.all()
        total_material_cost = sum(item.cost * instance.quantity for item in bom_items)
        instance.material_cost = total_material_cost
        
        # Simple labor cost calculation (20% of material cost)
        instance.labor_cost = total_material_cost * 0.2
        
        # Simple overhead cost calculation (10% of material + labor)
        instance.overhead_cost = (instance.material_cost + instance.labor_cost) * 0.1
        
        instance.save()