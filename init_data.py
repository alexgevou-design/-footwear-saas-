from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from products.models import (
    FootwearCategory, Material, SizeChart, SizeConversion, FootwearProduct,
    BillOfMaterials, WholesaleCustomer
)
from accounting.models import ChartOfAccounts, TaxRate

class Command(BaseCommand):
    help = 'Initialize the database with sample data for FootwearCraft SaaS'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing FootwearCraft SaaS database...'))
        
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@footwearcraft.com',
                password='admin123',
                first_name='System',
                last_name='Administrator'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user: admin/admin123'))
        
        # Create sample users
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@footwearcraft.com',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS('Created demo user: demo/demo123'))
        
        # Create footwear categories
        categories_data = [
            {'name': 'Athletic Shoes', 'slug': 'athletic-shoes'},
            {'name': 'Casual Shoes', 'slug': 'casual-shoes'},
            {'name': 'Dress Shoes', 'slug': 'dress-shoes'},
            {'name': 'Boots', 'slug': 'boots'},
            {'name': 'Sandals', 'slug': 'sandals'},
            {'name': 'Sneakers', 'slug': 'sneakers'},
        ]
        
        for cat_data in categories_data:
            category, created = FootwearCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create materials
        materials_data = [
            {'name': 'Premium Leather', 'material_type': 'leather', 'color': 'Brown', 'supplier': 'Italian Leather Co.', 'cost_per_unit': Decimal('25.00')},
            {'name': 'Canvas', 'material_type': 'fabric', 'color': 'White', 'supplier': 'Textile Inc.', 'cost_per_unit': Decimal('8.50')},
            {'name': 'Rubber Sole', 'material_type': 'rubber', 'color': 'Black', 'supplier': 'Sole Solutions', 'cost_per_unit': Decimal('12.00')},
            {'name': 'Memory Foam', 'material_type': 'foam', 'color': 'White', 'supplier': 'Comfort Tech', 'cost_per_unit': Decimal('15.00')},
            {'name': 'Synthetic Leather', 'material_type': 'synthetic', 'color': 'Black', 'supplier': 'Eco Materials', 'cost_per_unit': Decimal('18.00')},
            {'name': 'Cotton Laces', 'material_type': 'fabric', 'color': 'White', 'supplier': 'Lace Masters', 'cost_per_unit': Decimal('2.50')},
        ]
        
        for mat_data in materials_data:
            material, created = Material.objects.get_or_create(
                name=mat_data['name'],
                color=mat_data['color'],
                defaults=mat_data
            )
            if created:
                self.stdout.write(f'Created material: {material.name}')
        
        # Create size charts
        size_charts_data = [
            {'name': 'US Men Sizes', 'region': 'US', 'gender': 'M'},
            {'name': 'US Women Sizes', 'region': 'US', 'gender': 'W'},
            {'name': 'EU Sizes', 'region': 'EU', 'gender': 'U'},
            {'name': 'UK Sizes', 'region': 'UK', 'gender': 'U'},
        ]
        
        for chart_data in size_charts_data:
            chart, created = SizeChart.objects.get_or_create(
                region=chart_data['region'],
                gender=chart_data['gender'],
                defaults={'name': chart_data['name']}
            )
            if created:
                self.stdout.write(f'Created size chart: {chart.name}')
        
        # Create size conversions
        us_men_chart = SizeChart.objects.get(region='US', gender='M')
        us_women_chart = SizeChart.objects.get(region='US', gender='W')
        eu_chart = SizeChart.objects.get(region='EU', gender='U')
        
        # US Men sizes
        us_men_sizes = [
            ('7', 250.0), ('7.5', 255.0), ('8', 260.0), ('8.5', 265.0),
            ('9', 270.0), ('9.5', 275.0), ('10', 280.0), ('10.5', 285.0),
            ('11', 290.0), ('11.5', 295.0), ('12', 300.0)
        ]
        
        for size_value, length in us_men_sizes:
            SizeConversion.objects.get_or_create(
                size_chart=us_men_chart,
                size_value=size_value,
                defaults={'length_mm': Decimal(str(length))}
            )
        
        # US Women sizes
        us_women_sizes = [
            ('6', 230.0), ('6.5', 235.0), ('7', 240.0), ('7.5', 245.0),
            ('8', 250.0), ('8.5', 255.0), ('9', 260.0), ('9.5', 265.0),
            ('10', 270.0), ('10.5', 275.0), ('11', 280.0)
        ]
        
        for size_value, length in us_women_sizes:
            SizeConversion.objects.get_or_create(
                size_chart=us_women_chart,
                size_value=size_value,
                defaults={'length_mm': Decimal(str(length))}
            )
        
        # EU sizes
        eu_sizes = [
            ('38', 240.0), ('39', 250.0), ('40', 260.0), ('41', 270.0),
            ('42', 280.0), ('43', 290.0), ('44', 300.0), ('45', 310.0)
        ]
        
        for size_value, length in eu_sizes:
            SizeConversion.objects.get_or_create(
                size_chart=eu_chart,
                size_value=size_value,
                defaults={'length_mm': Decimal(str(length))}
            )
        
        self.stdout.write(self.style.SUCCESS('Created size conversions'))
        
        # Create sample products
        athletic_category = FootwearCategory.objects.get(slug='athletic-shoes')
        casual_category = FootwearCategory.objects.get(slug='casual-shoes')
        
        products_data = [
            {
                'name': 'Professional Running Shoe',
                'sku': 'PRO-RUN-001',
                'category': athletic_category,
                'gender': 'U',
                'description': 'High-performance running shoe with advanced cushioning and breathable mesh upper.',
                'base_price': Decimal('129.99'),
                'customizable': True,
                'heel_height': Decimal('25.0'),
                'production_time_days': 14
            },
            {
                'name': 'Classic Canvas Sneaker',
                'sku': 'CLS-CNV-001',
                'category': casual_category,
                'gender': 'U',
                'description': 'Timeless canvas sneaker perfect for everyday wear.',
                'base_price': Decimal('79.99'),
                'customizable': True,
                'heel_height': Decimal('20.0'),
                'production_time_days': 10
            },
            {
                'name': 'Premium Leather Boot',
                'sku': 'PRM-LTH-001',
                'category': FootwearCategory.objects.get(slug='boots'),
                'gender': 'M',
                'description': 'Handcrafted leather boot with premium materials and superior comfort.',
                'base_price': Decimal('249.99'),
                'customizable': False,
                'heel_height': Decimal('30.0'),
                'production_time_days': 21
            }
        ]
        
        for prod_data in products_data:
            product, created = FootwearProduct.objects.get_or_create(
                sku=prod_data['sku'],
                defaults=prod_data
            )
            if created:
                # Add available materials and sizes
                product.available_materials.add(*Material.objects.all()[:3])
                product.available_sizes.add(*SizeConversion.objects.all()[:10])
                self.stdout.write(f'Created product: {product.name}')
                
                # Create bill of materials
                if product.name == 'Professional Running Shoe':
                    BillOfMaterials.objects.get_or_create(
                        product=product,
                        material=Material.objects.get(name='Canvas'),
                        component_name='Upper',
                        defaults={'quantity_required': Decimal('1.5'), 'notes': 'Breathable mesh upper'}
                    )
                    BillOfMaterials.objects.get_or_create(
                        product=product,
                        material=Material.objects.get(name='Rubber Sole'),
                        component_name='Sole',
                        defaults={'quantity_required': Decimal('1.0'), 'notes': 'High-grip rubber sole'}
                    )
                elif product.name == 'Premium Leather Boot':
                    BillOfMaterials.objects.get_or_create(
                        product=product,
                        material=Material.objects.get(name='Premium Leather'),
                        component_name='Upper',
                        defaults={'quantity_required': Decimal('2.0'), 'notes': 'Full grain leather upper'}
                    )
        
        # Create chart of accounts
        accounts_data = [
            {'account_code': '1000', 'account_name': 'Cash', 'account_type': 'asset'},
            {'account_code': '1200', 'account_name': 'Accounts Receivable', 'account_type': 'asset'},
            {'account_code': '1300', 'account_name': 'Inventory', 'account_type': 'asset'},
            {'account_code': '2000', 'account_name': 'Accounts Payable', 'account_type': 'liability'},
            {'account_code': '3000', 'account_name': 'Owner Equity', 'account_type': 'equity'},
            {'account_code': '4000', 'account_name': 'Sales Revenue', 'account_type': 'revenue'},
            {'account_code': '5000', 'account_name': 'Cost of Goods Sold', 'account_type': 'cogs'},
            {'account_code': '6000', 'account_name': 'Operating Expenses', 'account_type': 'expense'},
        ]
        
        for acc_data in accounts_data:
            account, created = ChartOfAccounts.objects.get_or_create(
                account_code=acc_data['account_code'],
                defaults=acc_data
            )
            if created:
                self.stdout.write(f'Created account: {account.account_name}')
        
        # Create tax rates
        tax_rates_data = [
            {'name': 'Standard Sales Tax', 'rate_percentage': Decimal('8.25'), 'jurisdiction': 'California', 'tax_type': 'Sales Tax'},
            {'name': 'NY Sales Tax', 'rate_percentage': Decimal('8.00'), 'jurisdiction': 'New York', 'tax_type': 'Sales Tax'},
            {'name': 'EU VAT', 'rate_percentage': Decimal('20.00'), 'jurisdiction': 'European Union', 'tax_type': 'VAT'},
        ]
        
        from django.utils import timezone
        for tax_data in tax_rates_data:
            tax_rate, created = TaxRate.objects.get_or_create(
                name=tax_data['name'],
                defaults={**tax_data, 'effective_date': timezone.now().date()}
            )
            if created:
                self.stdout.write(f'Created tax rate: {tax_rate.name}')
        
        # Create wholesale customer
        if not WholesaleCustomer.objects.filter(user=demo_user).exists():
            wholesale_customer = WholesaleCustomer.objects.create(
                user=demo_user,
                business_name='Demo Shoe Store',
                contact_person='Demo User',
                phone='(555) 123-4567',
                email='demo@shostore.com',
                credit_limit=Decimal('10000.00'),
                discount_tier='silver',
                billing_address='123 Demo St, Demo City, DC 12345',
                shipping_address='123 Demo St, Demo City, DC 12345',
                approved=True
            )
            self.stdout.write(f'Created wholesale customer: {wholesale_customer.business_name}')
        
        self.stdout.write(self.style.SUCCESS('\nDatabase initialization completed!'))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write(self.style.SUCCESS('Admin: admin / admin123'))
        self.stdout.write(self.style.SUCCESS('Demo User: demo / demo123'))