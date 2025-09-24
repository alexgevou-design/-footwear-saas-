from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.product_catalog, name='catalog'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('custom-design/<int:product_id>/', views.custom_design, name='custom_design'),
    path('design/<int:design_id>/', views.design_detail, name='design_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('size-converter/', views.size_converter, name='size_converter'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]