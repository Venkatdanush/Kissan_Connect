"""
Django Management Command: python manage.py seed_demo_data
Populates realistic sample data for KissanConnect demo and recruitment review.
"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from main.models import (
    Farmer, Category, Product, Order,
    CarbonFarm, SoilTest, CarbonCredit, SatelliteImage,
    FarmerSubmission, CreditPurchase
)


class Command(BaseCommand):
    help = 'Seeds realistic sample data for KissanConnect demo presentation and recruitment review.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('🌱 Starting KissanConnect demo data seeding...'))

        # 1. Farmers
        farmers_data = [
            {'name': 'Rajesh Patil', 'email': 'rajesh.patil@kissan.org', 'phone_number': '+91-9876543210', 'location': 'Nashik, Maharashtra'},
            {'name': 'Gurpreet Singh', 'email': 'gurpreet.singh@kissan.org', 'phone_number': '+91-9876543211', 'location': 'Ludhiana, Punjab'},
            {'name': 'Kavitha Reddy', 'email': 'kavitha.reddy@kissan.org', 'phone_number': '+91-9876543212', 'location': 'Warangal, Telangana'},
            {'name': 'Anand Murthy', 'email': 'anand.murthy@kissan.org', 'phone_number': '+91-9876543213', 'location': 'Mysuru, Karnataka'},
        ]

        farmers = []
        for f in farmers_data:
            farmer, _ = Farmer.objects.get_or_create(email=f['email'], defaults=f)
            farmers.append(farmer)
        self.stdout.write(self.style.SUCCESS(f'✅ Seeded {len(farmers)} Farmers'))

        # 2. Categories
        cat_data = [
            ('Fresh Produce', 'Direct-from-farm organic fruits, vegetables, and staples', 'fas fa-apple-alt'),
            ('Certified Seeds', 'High germination hybrid and heirloom seeds', 'fas fa-seedling'),
            ('Organic Fertilizers', 'Bio-fertilizers, vermicompost, and neem cakes', 'fas fa-leaf'),
            ('Farming Equipment', 'Modern precision farming tools and sprayers', 'fas fa-tractor'),
        ]
        categories = {}
        for name, desc, icon in cat_data:
            c, _ = Category.objects.get_or_create(name=name, defaults={'description': desc, 'icon': icon})
            categories[name] = c
        self.stdout.write(self.style.SUCCESS(f'✅ Seeded {len(categories)} Categories'))

        # 3. Products
        products_data = [
            {
                'name': 'Organic Sharbati Wheat', 'product_type': 'produce', 'category': categories['Fresh Produce'],
                'price': 42.00, 'unit': 'kg', 'quantity_available': 500, 'seller': farmers[1],
                'is_organic': True, 'description': 'Naturally grown premium grade golden Sharbati wheat, rich in protein.'
            },
            {
                'name': 'Farm Fresh Alphonso Mangoes', 'product_type': 'produce', 'category': categories['Fresh Produce'],
                'price': 650.00, 'unit': 'dozen', 'quantity_available': 80, 'seller': farmers[0],
                'is_organic': True, 'description': 'Naturally ripened GI-tagged Devgad Alphonso mangoes.'
            },
            {
                'name': 'Hybrid Basmati Rice Seeds (Pusa 1121)', 'product_type': 'seed', 'category': categories['Certified Seeds'],
                'price': 120.00, 'unit': 'kg', 'quantity_available': 350, 'seller': farmers[1],
                'is_organic': False, 'description': 'High yielding, aroma-rich aromatic Basmati paddy seeds with 95% germination rate.'
            },
            {
                'name': 'Enriched Vermicompost (100% Organic)', 'product_type': 'fertilizer', 'category': categories['Organic Fertilizers'],
                'price': 18.00, 'unit': 'kg', 'quantity_available': 1200, 'seller': farmers[2],
                'is_organic': True, 'description': 'Laboratory tested microbial compost enriched with earthworm castings and mycorrhizae.'
            },
            {
                'name': 'Solar Powered Knapsack Crop Sprayer', 'product_type': 'tool', 'category': categories['Farming Equipment'],
                'price': 2850.00, 'unit': 'piece', 'quantity_available': 25, 'seller': farmers[3],
                'is_organic': False, 'description': '16-liter dual battery and solar powered continuous spray tank for pesticides and bio-stimulants.'
            },
            {
                'name': 'Cold-Pressed Pure Neem Oil (10,000 PPM)', 'product_type': 'pesticide', 'category': categories['Organic Fertilizers'],
                'price': 340.00, 'unit': 'liter', 'quantity_available': 150, 'seller': farmers[2],
                'is_organic': True, 'description': 'Broad-spectrum organic botanical repellent effective against sucking pests, aphids, and mites.'
            }
        ]

        products = []
        for p in products_data:
            prod, _ = Product.objects.get_or_create(name=p['name'], seller=p['seller'], defaults=p)
            products.append(prod)
        self.stdout.write(self.style.SUCCESS(f'✅ Seeded {len(products)} Marketplace Products'))

        # 4. Sample Orders
        if products:
            Order.objects.get_or_create(
                buyer_name='Aarav Mehta',
                product=products[0],
                defaults={
                    'buyer_email': 'aarav.buyer@example.com',
                    'buyer_phone': '+91-9876500001',
                    'buyer_address': 'Flat 402, Green Meadows, Pune',
                    'quantity': 25,
                    'total_price': products[0].price * 25,
                    'status': 'confirmed'
                }
            )
            Order.objects.get_or_create(
                buyer_name='Sunita Chawla',
                product=products[1],
                defaults={
                    'buyer_email': 'sunita.delhi@example.com',
                    'buyer_phone': '+91-9876500002',
                    'buyer_address': 'Sector 14, Gurugram',
                    'quantity': 4,
                    'total_price': products[1].price * 4,
                    'status': 'shipped'
                }
            )

        # 5. Carbon Credit Farms
        carbon_farms_data = [
            {
                'farmer': farmers[0],
                'farm_name': 'Sahyadri Agro-Forestry & Bio-Farm',
                'total_hectares': 14.50,
                'latitude': 19.9975,
                'longitude': 73.7898,
                'verification_status': 'verified',
                'organic_practices_start_date': date(2023, 6, 15)
            },
            {
                'farmer': farmers[2],
                'farm_name': 'Kakatiya Regenerative Soil Reserve',
                'total_hectares': 22.00,
                'latitude': 17.9689,
                'longitude': 79.5941,
                'verification_status': 'monitoring',
                'organic_practices_start_date': date(2024, 1, 10)
            }
        ]

        for cf in carbon_farms_data:
            farm, _ = CarbonFarm.objects.get_or_create(farm_name=cf['farm_name'], defaults=cf)

            # Baseline Soil Test
            SoilTest.objects.get_or_create(
                farm=farm,
                test_date=date(2024, 3, 1),
                defaults={
                    'lab_name': 'National Soil Health Testing Laboratory',
                    'organic_carbon_percentage': 0.85,
                    'ph_level': 6.8,
                    'nitrogen_content': 190.0,
                    'phosphorus_content': 22.0,
                    'potassium_content': 310.0,
                    'gps_coordinates': f"{farm.latitude}, {farm.longitude}",
                    'is_baseline': True
                }
            )

            # Satellite Image log
            SatelliteImage.objects.get_or_create(
                farm=farm,
                capture_date=date.today() - timedelta(days=5),
                defaults={
                    'ndvi_score': 0.742,
                    'vegetation_health': 'healthy',
                    'anomaly_detected': False,
                    'ai_analysis_complete': True
                }
            )

            # Carbon Credit Issuance
            credit, _ = CarbonCredit.objects.get_or_create(
                farm=farm,
                credit_type='soil_carbon',
                verification_period_start=date(2024, 1, 1),
                defaults={
                    'verification_period_end': date(2024, 12, 31),
                    'co2_tonnes': 32.50,
                    'price_per_tonne': 1450.00,
                    'total_value': 32.50 * 1450.00,
                    'status': 'issued',
                    'blockchain_hash': '0x7f9a2b8c4d1e3f5a6b7c8d9e0f1a2b3c4d5e6f7a',
                    'issued_date': date.today() - timedelta(days=15)
                }
            )

        self.stdout.write(self.style.SUCCESS('✅ Seeded Carbon Farms, Soil Tests, and Verified Credits'))

        # 6. Corporate Purchase
        CreditPurchase.objects.get_or_create(
            company_name='Tata Sustainability Ventures',
            defaults={
                'company_email': 'esg@tatagroup.example.com',
                'contact_person': 'Rohan Deshmukh (Head of Net Zero)',
                'phone_number': '+91-22-66658282',
                'purchase_type': 'annual',
                'credits_purchased': 25,
                'total_amount': 36250.00,
                'payment_status': 'completed'
            }
        )

        self.stdout.write(self.style.SUCCESS('🎉 KissanConnect database successfully populated!'))
