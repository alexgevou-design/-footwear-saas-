from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from decimal import Decimal

from products.models import (
    FootwearProduct, FootwearCategory, Material, SizeConversion,
    WholesaleCustomer, CustomDesign, ProductionOrder
)
from accounting.models import Invoice, Payment, InventoryValuation

def home(request):
    """Homepage with product showcase"""
    featured_products = FootwearProduct.objects.filter(active=True)[:6]
    categories = FootwearCategory.objects.all()[:8]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'web/home.html', context)

def product_catalog(request):
    """Product catalog with filtering"""
    products = FootwearProduct.objects.filter(active=True)
    categories = FootwearCategory.objects.all()
    
    # Filtering
    category_id = request.GET.get('category')
    gender = request.GET.get('gender')
    search = request.GET.get('search')
    
    if category_id:
        products = products.filter(category_id=category_id)
    if gender:
        products = products.filter(gender=gender)
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_gender': gender,
        'search_query': search,
    }
    return render(request, 'web/catalog.html', context)

def product_detail(request, product_id):
    """Product detail page with customization options"""
    product = get_object_or_404(FootwearProduct, id=product_id, active=True)
    available_sizes = product.available_sizes.all()
    available_materials = product.available_materials.all()
    bom_items = product.bom_items.all()
    
    context = {
        'product': product,
        'available_sizes': available_sizes,
        'available_materials': available_materials,
        'bom_items': bom_items,
    }
    return render(request, 'web/product_detail.html', context)

@login_required
def custom_design(request, product_id):
    """Custom design tool for footwear"""
    product = get_object_or_404(FootwearProduct, id=product_id, customizable=True)
    
    if request.method == 'POST':
        # Handle custom design creation
        design_name = request.POST.get('design_name')
        size_id = request.POST.get('size')
        special_instructions = request.POST.get('special_instructions', '')
        
        if design_name and size_id:
            try:
                size = SizeConversion.objects.get(id=size_id)
                design = CustomDesign.objects.create(
                    customer=request.user,
                    base_product=product,
                    design_name=design_name,
                    size=size,
                    special_instructions=special_instructions,
                    base_price=product.base_price,
                    customization_fee=Decimal('50.00'),  # Base customization fee
                )
                
                messages.success(request, 'Custom design created successfully!')
                return redirect('web:design_detail', design_id=design.id)
            except SizeConversion.DoesNotExist:
                messages.error(request, 'Invalid size selected.')
    
    context = {
        'product': product,
        'available_sizes': product.available_sizes.all(),
        'available_materials': product.available_materials.all(),
    }
    return render(request, 'web/custom_design.html', context)

@login_required
def design_detail(request, design_id):
    """View custom design details"""
    design = get_object_or_404(CustomDesign, id=design_id, customer=request.user)
    
    context = {
        'design': design,
    }
    return render(request, 'web/design_detail.html', context)

@login_required
def dashboard(request):
    """Customer dashboard"""
    # Get user's designs and orders
    user_designs = CustomDesign.objects.filter(customer=request.user).order_by('-created_at')[:5]
    user_invoices = Invoice.objects.filter(customer=request.user).order_by('-created_at')[:5]
    
    # Check if user is a wholesale customer
    wholesale_customer = None
    try:
        wholesale_customer = WholesaleCustomer.objects.get(user=request.user)
    except WholesaleCustomer.DoesNotExist:
        pass
    
    context = {
        'user_designs': user_designs,
        'user_invoices': user_invoices,
        'wholesale_customer': wholesale_customer,
    }
    return render(request, 'web/dashboard.html', context)

@login_required
def invoice_detail(request, invoice_id):
    """Invoice detail view"""
    invoice = get_object_or_404(Invoice, id=invoice_id, customer=request.user)
    
    context = {
        'invoice': invoice,
    }
    return render(request, 'web/invoice_detail.html', context)

@login_required
def admin_dashboard(request):
    """Admin dashboard with business analytics"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('web:home')
    
    # Calculate statistics
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Revenue
    total_revenue = Invoice.objects.filter(status='paid').aggregate(
        Sum('total_amount'))['total_amount__sum'] or 0
    monthly_revenue = Invoice.objects.filter(
        status='paid', paid_date__gte=thirty_days_ago
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Orders
    total_orders = ProductionOrder.objects.count()
    pending_orders = ProductionOrder.objects.filter(status='pending').count()
    in_production = ProductionOrder.objects.filter(status='in_production').count()
    
    # Invoices
    pending_invoices = Invoice.objects.filter(status__in=['draft', 'sent']).count()
    overdue_invoices = Invoice.objects.filter(
        due_date__lt=today, status__in=['sent', 'partial']
    ).count()
    
    # Customers
    total_customers = WholesaleCustomer.objects.count()
    active_customers = WholesaleCustomer.objects.filter(approved=True).count()
    
    # Recent activity
    recent_orders = ProductionOrder.objects.order_by('-created_at')[:10]
    recent_invoices = Invoice.objects.order_by('-created_at')[:10]
    recent_payments = Payment.objects.filter(
        status='completed'
    ).order_by('-created_at')[:10]
    
    context = {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'in_production': in_production,
        'pending_invoices': pending_invoices,
        'overdue_invoices': overdue_invoices,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'recent_orders': recent_orders,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments,
    }
    return render(request, 'web/admin_dashboard.html', context)

@login_required
def size_converter(request):
    """Size conversion tool"""
    if request.method == 'POST':
        from_size = request.POST.get('from_size')
        from_region = request.POST.get('from_region')
        to_region = request.POST.get('to_region')
        gender = request.POST.get('gender')
        
        try:
            # Find the source size
            from_conversion = SizeConversion.objects.get(
                size_chart__region=from_region,
                size_chart__gender=gender,
                size_value=from_size
            )
            
            # Find equivalent size in target region
            to_conversion = SizeConversion.objects.get(
                size_chart__region=to_region,
                size_chart__gender=gender,
                length_mm=from_conversion.length_mm
            )
            
            result = {
                'success': True,
                'from_size': from_size,
                'from_region': from_region,
                'to_region': to_region,
                'converted_size': to_conversion.size_value,
                'length_mm': float(to_conversion.length_mm)
            }
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse(result)
            else:
                context = {'conversion_result': result}
                return render(request, 'web/size_converter.html', context)
                
        except SizeConversion.DoesNotExist:
            error = {'success': False, 'error': 'Size conversion not found'}
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse(error)
            else:
                messages.error(request, 'Size conversion not found')
    
    return render(request, 'web/size_converter.html')

def about(request):
    """About page"""
    return render(request, 'web/about.html')

def contact(request):
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # In a real application, you would send an email or save to database
        messages.success(request, 'Thank you for your message. We will get back to you soon!')
        return redirect('web:contact')
    
    return render(request, 'web/contact.html')