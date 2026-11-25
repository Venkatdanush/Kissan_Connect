from django.db import models
from django.contrib.auth.models import User

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='farmer_profile')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    farm_size_acres = models.FloatField(default=3.0)
    primary_crop = models.CharField(max_length=100, default='Wheat & Pulses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Crop(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    farmer = models.ForeignKey(Farmer, related_name='crops', on_delete=models.CASCADE)
    planting_date = models.DateField()
    harvest_date = models.DateField()

    def __str__(self):
        return self.name

class Service(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(Farmer, related_name='blog_posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.name}'

# Marketplace Models
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-tag')
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    PRODUCT_TYPES = [
        ('produce', 'Farm Produce'),
        ('fertilizer', 'Fertilizer'),
        ('pesticide', 'Pesticide'),
        ('seed', 'Seeds'),
        ('tool', 'Farm Tools'),
        ('equipment', 'Equipment'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')  # kg, liter, piece, etc.
    quantity_available = models.PositiveIntegerField()
    seller = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_organic = models.BooleanField(default=False)
    harvest_date = models.DateField(blank=True, null=True)  # For produce
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}/{self.unit}"

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    buyer_name = models.CharField(max_length=100)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=15)
    buyer_address = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.product.name}"

# Carbon Credit Models
class CarbonFarm(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('baseline_complete', 'Baseline Complete'),
        ('monitoring', 'Under Monitoring'),
        ('verified', 'Fully Verified'),
        ('suspended', 'Suspended'),
    ]
    
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='carbon_farms')
    farm_name = models.CharField(max_length=200)
    total_hectares = models.DecimalField(max_digits=10, decimal_places=2)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    baseline_soil_report = models.FileField(upload_to='carbon/soil_reports/', blank=True, null=True)
    certification_date = models.DateField(blank=True, null=True)
    organic_practices_start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.farm_name} - {self.farmer.name}"

class SoilTest(models.Model):
    farm = models.ForeignKey(CarbonFarm, on_delete=models.CASCADE, related_name='soil_tests')
    test_date = models.DateField()
    lab_name = models.CharField(max_length=200)
    organic_carbon_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    ph_level = models.DecimalField(max_digits=4, decimal_places=2)
    nitrogen_content = models.DecimalField(max_digits=6, decimal_places=2)
    phosphorus_content = models.DecimalField(max_digits=6, decimal_places=2)
    potassium_content = models.DecimalField(max_digits=6, decimal_places=2)
    report_file = models.FileField(upload_to='carbon/soil_tests/')
    gps_coordinates = models.CharField(max_length=100)
    is_baseline = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Soil Test - {self.farm.farm_name} - {self.test_date}"

class CarbonCredit(models.Model):
    CREDIT_TYPE = [
        ('soil_carbon', 'Soil Carbon Sequestration'),
        ('water_conservation', 'Water Conservation'),
        ('organic_farming', 'Organic Farming'),
        ('crop_rotation', 'Crop Rotation'),
        ('methane_reduction', 'Methane Reduction'),
    ]
    
    CREDIT_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('issued', 'Issued'),
        ('sold', 'Sold'),
        ('retired', 'Retired'),
    ]
    
    farm = models.ForeignKey(CarbonFarm, on_delete=models.CASCADE, related_name='carbon_credits')
    credit_type = models.CharField(max_length=20, choices=CREDIT_TYPE)
    co2_tonnes = models.DecimalField(max_digits=10, decimal_places=2)
    verification_period_start = models.DateField()
    verification_period_end = models.DateField()
    price_per_tonne = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=CREDIT_STATUS, default='pending')
    blockchain_hash = models.CharField(max_length=256, blank=True, null=True)
    issued_date = models.DateField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.total_value = self.co2_tonnes * self.price_per_tonne
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.credit_type} - {self.co2_tonnes}T CO₂ - {self.farm.farm_name}"

class SatelliteImage(models.Model):
    farm = models.ForeignKey(CarbonFarm, on_delete=models.CASCADE, related_name='satellite_images')
    capture_date = models.DateField()
    image_url = models.URLField(blank=True, null=True)
    ndvi_score = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    vegetation_health = models.CharField(max_length=50, blank=True, null=True)
    anomaly_detected = models.BooleanField(default=False)
    anomaly_description = models.TextField(blank=True, null=True)
    ai_analysis_complete = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Satellite - {self.farm.farm_name} - {self.capture_date}"

class FarmerSubmission(models.Model):
    SUBMISSION_TYPE = [
        ('crop_photo', 'Crop Photo'),
        ('practice_documentation', 'Practice Documentation'),
        ('gps_verification', 'GPS Verification'),
        ('progress_report', 'Progress Report'),
    ]
    
    farm = models.ForeignKey(CarbonFarm, on_delete=models.CASCADE, related_name='submissions')
    submission_type = models.CharField(max_length=30, choices=SUBMISSION_TYPE)
    submission_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='carbon/farmer_submissions/', blank=True, null=True)
    gps_latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    gps_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    notes = models.TextField()
    verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.submission_type} - {self.farm.farm_name} - {self.submission_date.date()}"

class CreditPurchase(models.Model):
    PURCHASE_TYPE = [
        ('one_time', 'One-time Purchase'),
        ('monthly', 'Monthly Subscription'),
        ('quarterly', 'Quarterly Subscription'),
        ('annual', 'Annual Subscription'),
    ]
    
    company_name = models.CharField(max_length=200)
    company_email = models.EmailField()
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    purchase_type = models.CharField(max_length=20, choices=PURCHASE_TYPE)
    credits_purchased = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    credits = models.ManyToManyField(CarbonCredit, related_name='purchases')
    payment_status = models.CharField(max_length=20, default='pending')
    
    def __str__(self):
        return f"{self.company_name} - {self.credits_purchased} credits"

class VerificationPayment(models.Model):
    PAYMENT_TYPE = [
        ('baseline', 'Baseline Payment (40%)'),
        ('mid_season', 'Mid-season Payment (30%)'),
        ('final', 'Final Payment (30%)'),
    ]
    
    farm = models.ForeignKey(CarbonFarm, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    verification_document = models.FileField(upload_to='carbon/verifications/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.payment_type} - {self.farm.farm_name} - ₹{self.amount}"


class ScanHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scans', null=True, blank=True)
    crop_name = models.CharField(max_length=100, default='Crop Foliage')
    disease_type = models.CharField(max_length=150)
    confidence = models.FloatField(default=95.0)
    is_healthy = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.disease_type} ({self.confidence}%)"
