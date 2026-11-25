from django.contrib import admin
from .models import (
    Farmer, Crop, Service, BlogPost, ContactMessage, 
    Category, Product, Order,
    CarbonFarm, SoilTest, CarbonCredit, SatelliteImage, 
    FarmerSubmission, CreditPurchase, VerificationPayment
)

# Register your models here.

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'location', 'created_at')
    search_fields = ('name', 'email', 'location')
    list_filter = ('location', 'created_at')

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'planting_date', 'harvest_date')
    search_fields = ('name', 'farmer__name')
    list_filter = ('planting_date', 'harvest_date')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__name')
    list_filter = ('created_at', 'updated_at')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'description')
    search_fields = ('name', 'description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'price', 'unit', 'quantity_available', 'seller', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'seller__name')
    list_filter = ('product_type', 'category', 'is_organic', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active', 'quantity_available')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_name', 'product', 'quantity', 'total_price', 'status', 'order_date')
    search_fields = ('buyer_name', 'buyer_email', 'product__name')
    list_filter = ('status', 'order_date')
    readonly_fields = ('order_date',)
    list_editable = ('status',)

# Carbon Credit Admin Classes

@admin.register(CarbonFarm)
class CarbonFarmAdmin(admin.ModelAdmin):
    list_display = ('farm_name', 'farmer', 'total_hectares', 'verification_status', 'created_at')
    search_fields = ('farm_name', 'farmer__name', 'farmer__location')
    list_filter = ('verification_status', 'created_at')
    readonly_fields = ('created_at',)
    list_editable = ('verification_status',)

@admin.register(SoilTest)
class SoilTestAdmin(admin.ModelAdmin):
    list_display = ('farm', 'test_date', 'lab_name', 'organic_carbon_percentage', 'ph_level', 'is_baseline')
    search_fields = ('farm__farm_name', 'lab_name')
    list_filter = ('test_date', 'is_baseline', 'lab_name')
    readonly_fields = ('gps_coordinates',)

@admin.register(CarbonCredit)
class CarbonCreditAdmin(admin.ModelAdmin):
    list_display = ('farm', 'credit_type', 'co2_tonnes', 'price_per_tonne', 'total_value', 'status', 'issued_date')
    search_fields = ('farm__farm_name', 'credit_type')
    list_filter = ('credit_type', 'status', 'issued_date')
    readonly_fields = ('total_value',)
    list_editable = ('status',)

@admin.register(SatelliteImage)
class SatelliteImageAdmin(admin.ModelAdmin):
    list_display = ('farm', 'capture_date', 'ndvi_score', 'vegetation_health', 'anomaly_detected', 'ai_analysis_complete')
    search_fields = ('farm__farm_name',)
    list_filter = ('capture_date', 'vegetation_health', 'anomaly_detected', 'ai_analysis_complete')
    list_editable = ('ai_analysis_complete',)

@admin.register(FarmerSubmission)
class FarmerSubmissionAdmin(admin.ModelAdmin):
    list_display = ('farm', 'submission_type', 'submission_date', 'verified', 'gps_latitude', 'gps_longitude')
    search_fields = ('farm__farm_name', 'notes')
    list_filter = ('submission_type', 'submission_date', 'verified')
    list_editable = ('verified',)
    readonly_fields = ('submission_date',)

@admin.register(CreditPurchase)
class CreditPurchaseAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_person', 'purchase_type', 'credits_purchased', 'total_amount', 'payment_status', 'purchase_date')
    search_fields = ('company_name', 'company_email', 'contact_person')
    list_filter = ('purchase_type', 'payment_status', 'purchase_date')
    readonly_fields = ('purchase_date',)
    list_editable = ('payment_status',)

@admin.register(VerificationPayment)
class VerificationPaymentAdmin(admin.ModelAdmin):
    list_display = ('farm', 'payment_type', 'amount', 'payment_date')
    search_fields = ('farm__farm_name', 'notes')
    list_filter = ('payment_type', 'payment_date')
    readonly_fields = ('payment_date',)
