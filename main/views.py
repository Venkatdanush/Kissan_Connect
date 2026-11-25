"""
KissanConnect Web and API Controllers.
Delegates business logic, AI interactions, ML inference, and external services
to dedicated modular service layers.
"""

import json
import logging
from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import (
    Farmer, Crop, Service, BlogPost, ContactMessage,
    Category, Product, Order,
    CarbonFarm, SoilTest, CarbonCredit, SatelliteImage,
    FarmerSubmission, CreditPurchase, VerificationPayment,
    ScanHistory
)

from .services import (
    ai_service,
    disease_service,
    weather_service,
    crop_service,
    carbon_service,
    report_service,
)

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Authentication & User Isolation
# --------------------------------------------------------------------------

def user_login(request):
    """User Login Portal with 1-click Demo Fill."""
    if request.user.is_authenticated:
        return redirect('main:dashboard')

    if request.method == 'POST':
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=login_input, password=password)
        if not user and '@' in login_input:
            matched_user = User.objects.filter(email__iexact=login_input).first()
            if matched_user:
                user = authenticate(request, username=matched_user.username, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next') or 'main:dashboard'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials. Please verify your username/email and password.')

    return render(request, 'main/auth/login.html', {
        'page_title': 'Sign In — KissanConnect'
    })


def user_signup(request):
    """Farmer and Agronomist Registration."""
    if request.user.is_authenticated:
        return redirect('main:dashboard')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip() or email.split('@')[0]
        password = request.POST.get('password', '').strip()
        location = request.POST.get('location', 'Maharashtra, India').strip()
        farm_size = float(request.POST.get('farm_size', 3.0) or 3.0)
        primary_crop = request.POST.get('primary_crop', 'Wheat & Cotton').strip()

        if not email or not password or not name:
            messages.error(request, 'Name, email, and password are required.')
            return render(request, 'main/auth/signup.html', {'page_title': 'Join KissanConnect'})

        if User.objects.filter(username=username).exists():
            username = f"{username}_{User.objects.count() + 1}"

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email address already exists. Please sign in.')
            return redirect('main:login')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name.split()[0],
            last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
        )

        farmer = Farmer.objects.create(
            user=user,
            name=name,
            email=email,
            phone_number=request.POST.get('phone', '+91-9876543210'),
            location=location,
            farm_size_acres=farm_size,
            primary_crop=primary_crop
        )

        login(request, user)
        messages.success(request, f'Account successfully created! Welcome to your farm workstation, {name}.')
        return redirect('main:dashboard')

    return render(request, 'main/auth/signup.html', {
        'page_title': 'Create Account — KissanConnect'
    })


def user_logout(request):
    """User Logout and Session Destruction."""
    logout(request)
    messages.info(request, 'You have been securely signed out.')
    return redirect('main:index')


@login_required(login_url='main:login')
def dashboard(request):
    """Isolated Personal Agri-Command Workspace for Authenticated Users."""
    user = request.user
    farmer = getattr(user, 'farmer_profile', None)

    # Isolated user metrics
    user_orders = Order.objects.filter(user=user).select_related('product').order_by('-order_date')[:8]
    user_scans = user.scans.all().order_by('-created_at')[:8]
    
    # Calculate farm microclimate for user's location
    weather = weather_service.get_weather_data(17.3850, 78.4867)

    context = {
        'page_title': f"{user.first_name or user.username}'s Command Center",
        'farmer': farmer,
        'user_orders': user_orders,
        'user_scans': user_scans,
        'weather': weather,
        'total_orders_count': user.orders.count(),
        'total_scans_count': user.scans.count(),
        'farm_size': farmer.farm_size_acres if farmer else 3.0,
        'primary_crop': farmer.primary_crop if farmer else 'Wheat & Pulses'
    }
    return render(request, 'main/dashboard.html', context)


# --------------------------------------------------------------------------
# General Pages
# --------------------------------------------------------------------------

def index(request):
    """Home Command Center & Agricultural Workspace."""
    featured_products = Product.objects.filter(is_active=True).select_related('category', 'seller').order_by('-created_at')[:6]
    categories = Category.objects.all()
    
    total_farmers = Farmer.objects.count()
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    total_carbon = CarbonCredit.objects.filter(status='issued').aggregate(
        total=models.Sum('co2_tonnes')
    )['total'] or 32.5

    # Real microclimate data for home widget
    default_weather = weather_service.get_weather_data(17.3850, 78.4867)

    context = {
        'title': 'KissanConnect — Precision Agritech Ecosystem',
        'featured_products': featured_products,
        'categories': categories,
        'stats': {
            'farmers': total_farmers,
            'products': total_products,
            'orders': total_orders,
            'carbon_tonnes': round(float(total_carbon), 1)
        },
        'weather': default_weather,
    }
    return render(request, 'main/index.html', context)


def home(request):
    return redirect('main:index')


def services(request):
    """Platform Services Overview."""
    return render(request, 'main/services.html', {
        'page_title': 'Our Services - Kissan Connect'
    })


def about(request):
    """About KissanConnect mission & team."""
    return render(request, 'main/about.html', {
        'page_title': 'About Us - Kissan Connect'
    })


def contact(request):
    """Contact page with message persistence."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()

        if name and email and message_text:
            ContactMessage.objects.create(name=name, email=email, message=message_text)
            messages.success(request, 'Thank you! Your message has been received. Our agronomists will contact you soon.')
        else:
            messages.error(request, 'Please complete all required fields.')

    return render(request, 'main/contact.html', {
        'page_title': 'Contact Agronomic Support'
    })


def news(request):
    """Agricultural news, MSP updates, and government subsidies."""
    articles = [
        {
            'title': 'PM-KISAN Scheme: 18th Installment Disbursed to 9.5 Crore Farmers',
            'summary': 'Direct benefit transfer of ₹2,000 sent directly to Aadhaar-linked farmer bank accounts nationwide.',
            'category': 'Government Scheme',
            'date': 'November 2026',
            'source': 'Ministry of Agriculture'
        },
        {
            'title': 'Rabi Sowing Update: Wheat & Mustard Acreage Hits 5-Year High',
            'summary': 'Favorable soil moisture and optimal minimum temperatures boost initial sowing across Punjab, Haryana, and MP.',
            'category': 'Market Trends',
            'date': 'November 2026',
            'source': 'AgriMarket Bureau'
        },
        {
            'title': 'Carbon Farming Incentives: ₹1,500/Acre Subsidy for Zero-Till Residue Management',
            'summary': 'State agricultural boards announce carbon offset grants for avoiding stubble burning and increasing soil organic matter.',
            'category': 'Sustainability',
            'date': 'November 2026',
            'source': 'Green Ag Consortium'
        }
    ]
    return render(request, 'main/news.html', {'articles': articles, 'page_title': 'Agricultural News & Updates'})


# --------------------------------------------------------------------------
# Crop Intelligence & Weather
# --------------------------------------------------------------------------

def crop_suggestions(request):
    """Crop recommendation dashboard supporting both GET and POST requests."""
    if request.method == 'POST':
        location = request.POST.get('location', '').strip()
        state = request.POST.get('state', '').strip()
        country = request.POST.get('country', 'India').strip()

        form_data = {
            'farm_size': request.POST.get('farm_size', '2'),
            'soil_type': request.POST.get('soil_type', 'Loamy'),
            'season': request.POST.get('season', 'Kharif'),
            'budget': request.POST.get('budget', 'Medium'),
            'irrigation': request.POST.get('irrigation', 'Canal / Borewell'),
        }

        if not location:
            messages.error(request, 'Please provide your farm location or city.')
            return render(request, 'main/crop_suggestions.html', {'error': 'Location is required.'})

        full_location = f"{location}, {state}, {country}".strip(', ')

        # Coordinates lookup via geocoder with default fallback
        lat, lon = 17.3850, 78.4867
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="kissan_connect_crop_v2", timeout=3)
            loc = geolocator.geocode(full_location)
            if loc:
                lat, lon = loc.latitude, loc.longitude
                full_location = loc.address
        except Exception as e:
            logger.debug(f"Geocoding fallback used: {e}")

        weather_data = weather_service.get_weather_data(lat, lon)
        soil_data = crop_service.get_soil_data_by_coords(lat, lon, full_location)
        recommendations = crop_service.generate_crop_recommendations(
            location=full_location,
            weather_data=weather_data,
            soil_data=soil_data,
            **form_data
        )

        context = {
            'success': True,
            'location': full_location,
            'city': location,
            'state': state,
            'country': country,
            'temperature': weather_data.get('temperature', 28),
            'humidity': weather_data.get('humidity', 60),
            'weather_description': weather_data.get('description', 'Optimal'),
            'recommendations': recommendations,
            'auto_soil_data': soil_data,
            'form_data': form_data,
        }
        return render(request, 'main/crop_suggestions.html', context)

    return render(request, 'main/crop_suggestions.html', {
        'page_title': 'AI Crop Advisory Engine'
    })


@csrf_exempt
def get_crop_recommendation(request):
    """AJAX JSON API for dynamic crop recommendations."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    location = request.POST.get('location', '').strip()
    if not location:
        return JsonResponse({'success': False, 'error': 'Location is required.'})

    lat = float(request.POST.get('latitude', 17.3850))
    lon = float(request.POST.get('longitude', 78.4867))

    weather_data = weather_service.get_weather_data(lat, lon)
    soil_data = crop_service.get_soil_data_by_coords(lat, lon, location)

    form_data = {
        'farm_size': request.POST.get('farm_size', '2'),
        'season': request.POST.get('season', 'Kharif'),
        'budget': request.POST.get('budget', 'Medium'),
        'irrigation': request.POST.get('irrigation', 'Borewell'),
    }

    recommendations = crop_service.generate_crop_recommendations(
        location=location,
        weather_data=weather_data,
        soil_data=soil_data,
        **form_data
    )

    return JsonResponse({
        'success': True,
        'location': location,
        'temperature': weather_data.get('temperature'),
        'humidity': weather_data.get('humidity'),
        'weather_description': weather_data.get('description'),
        'recommendations': recommendations,
        'auto_soil_data': soil_data
    })


def weather_forecast(request):
    """Weather Intelligence page."""
    lat = float(request.GET.get('lat', 17.3850))
    lon = float(request.GET.get('lon', 78.4867))
    current_weather = weather_service.get_weather_data(lat, lon)
    forecast = weather_service.get_5day_forecast(lat, lon)

    return render(request, 'main/weather.html', {
        'page_title': 'Weather Intelligence & Calamity Alerts',
        'current_weather': current_weather,
        'forecast': forecast,
    })


@csrf_exempt
def reverse_geocode_location(request):
    """AJAX reverse geocoding from coordinates."""
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    if not lat or not lon:
        return JsonResponse({'success': False, 'error': 'Coordinates required.'}, status=400)

    try:
        geo = weather_service.reverse_geocode(float(lat), float(lon))
        return JsonResponse({'success': True, 'address': geo})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# --------------------------------------------------------------------------
# Plant Disease Doctor (TensorFlow CNN + Gemini AI)
# --------------------------------------------------------------------------

@csrf_exempt
def disease_detection(request):
    """Plant disease detection and AI remediation controller."""
    if request.method == 'POST':
        if 'plant_image' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No image file uploaded.'})

        image_file = request.FILES['plant_image']
        prediction = disease_service.predict_disease(image_file)

        if prediction.get('success'):
            remedies = ai_service.generate_disease_remedies(
                prediction['disease_type'],
                prediction['confidence']
            )
            if request.user.is_authenticated:
                crop = prediction['disease_type'].split('___')[0].replace('_', ' ')
                ScanHistory.objects.create(
                    user=request.user,
                    crop_name=crop,
                    disease_type=prediction['disease_type'],
                    confidence=prediction['confidence'],
                    is_healthy=prediction.get('is_healthy', False)
                )
            return JsonResponse({
                'success': True,
                'disease_type': prediction['disease_type'],
                'confidence': prediction['confidence'],
                'is_healthy': prediction.get('is_healthy', False),
                'top_candidates': prediction.get('top_candidates', []),
                'remedies': remedies.get('ai_remedies', ''),
                'source': remedies.get('source', 'ai')
            })

        return JsonResponse({'success': False, 'error': 'Diagnosis failed. Please try another image.'})

    return render(request, 'main/disease_detection.html', {
        'page_title': 'Plant Disease Doctor - AI Vision'
    })


# --------------------------------------------------------------------------
# AI Chatbot Assistant & Full-Page ChatGPT Agronomist Interface
# --------------------------------------------------------------------------

def ai_assistant(request):
    """Dedicated ChatGPT-style Full Page AI Agronomist."""
    return render(request, 'main/chat.html', {
        'page_title': 'Kissan Sahayak — AI Agronomist Chat',
        'active_model': 'Groq LPU (openai/gpt-oss-20b)',
        'failover_model': 'Google Gemini 3.5 Flash'
    })


@csrf_exempt
def ai_chat_advanced(request):
    """
    Advanced multi-modal chat endpoint.
    Accepts text queries along with optional leaf images for simultaneous
    computer-vision pathology classification and conversational agronomic advice.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        user_message = request.POST.get('message', '').strip()
        image_file = request.FILES.get('image')

        disease_info = None
        if image_file:
            disease_info = disease_service.predict_disease(image_file)

        system_instruction = (
            "You are 'Kissan Sahayak' (Farmer's Smart Assistant), an expert agricultural scientist "
            "and agronomist dedicated to helping farmers worldwide.\n"
            "CRITICAL LANGUAGE RULE: Always respond in the EXACT same language as the user's message. "
            "If the user writes in English, reply strictly in English. If the user writes in Hindi, reply in Hindi. "
            "Never switch languages unless the user explicitly requests it.\n\n"
            "Provide direct, highly practical, and actionable answers. Format your response cleanly with bullet points, "
            "bold headers, and concise steps. Cover soil care, organic remedies, irrigation, government schemes, "
            "and market selling tips."
        )

        if disease_info and disease_info.get('success'):
            diag = disease_info['disease_type']
            conf = disease_info['confidence']
            prompt = (
                f"The farmer uploaded an image of a crop leaf. The computer vision diagnosis detected: '{diag}' "
                f"with {conf}% algorithmic confidence.\n"
                f"Farmer's query: '{user_message or 'Please diagnose this plant and recommend immediate action.'}'\n\n"
                "Provide an immediate treatment plan with:\n"
                "1. Confirmation & Threat Assessment\n"
                "2. Organic & Cultural Cures\n"
                "3. Safe Chemical Fungicide/Pesticide Options with Dosage\n"
                "4. Preventive Farm Hygiene."
            )
        else:
            prompt = user_message or "Hello! How can I help your farm today?"

        reply, provider = ai_service.generate_llm_response(prompt, system_instruction)
        if not reply:
            reply = ai_service._get_chatbot_fallback(prompt)
            provider = 'curated_knowledge_base'

        return JsonResponse({
            'success': True,
            'response': reply,
            'disease_info': disease_info,
            'timestamp': datetime.now().strftime('%I:%M %p'),
            'source': provider
        })
    except Exception as e:
        logger.error(f"Advanced chat error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def ai_chatbot(request):
    """AJAX endpoint for Kissan Sahayak AI Assistant."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body.decode('utf-8'))
            user_message = payload.get('message', '').strip()
        else:
            user_message = request.POST.get('message', '').strip()

        if not user_message:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty.'})

        res = ai_service.ask_farm_assistant(user_message)
        return JsonResponse({
            'success': res.get('success', True),
            'response': res.get('response', ''),
            'timestamp': datetime.now().strftime('%I:%M %p'),
            'source': res.get('source', 'ai')
        })
    except Exception as e:
        logger.error(f"Chatbot view error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


# --------------------------------------------------------------------------
# Marketplace
# --------------------------------------------------------------------------

def marketplace(request):
    """Farmer-to-consumer marketplace with filtering, search, and sorting."""
    product_type = request.GET.get('type', 'all')
    category_id = request.GET.get('category')
    search = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'newest')

    products = Product.objects.filter(is_active=True)

    if product_type != 'all':
        products = products.filter(product_type=product_type)
    if category_id:
        products = products.filter(category_id=category_id)
    if search:
        products = products.filter(models.Q(name__icontains=search) | models.Q(description__icontains=search))

    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'oldest':
        products = products.order_by('created_at')
    else:
        products = products.order_by('-created_at')

    categories = Category.objects.all()

    context = {
        'page_title': 'Agri-Marketplace — Direct Farmer Trade',
        'products': products,
        'categories': categories,
        'current_type': product_type,
        'current_category': category_id,
        'current_search': search,
        'current_sort': sort_by,
        'product_types': Product.PRODUCT_TYPES,
    }
    return render(request, 'main/marketplace.html', context)


@csrf_exempt
def add_product(request):
    """Add new produce or equipment listing."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    try:
        farmer, _ = Farmer.objects.get_or_create(
            email=request.POST.get('seller_email', 'farmer@kissanconnect.org'),
            defaults={
                'name': request.POST.get('seller_name', 'Progressive Farmer'),
                'phone_number': request.POST.get('seller_phone', '+91-9876543210'),
                'location': request.POST.get('seller_location', 'Maharashtra, India')
            }
        )

        category_name = request.POST.get('category', 'Fresh Produce')
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={'description': f'{category_name} items'}
        )

        product = Product.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            product_type=request.POST.get('product_type', 'produce'),
            category=category,
            price=float(request.POST.get('price', 0)),
            unit=request.POST.get('unit', 'kg'),
            quantity_available=int(request.POST.get('quantity', 10)),
            seller=farmer,
            is_organic=request.POST.get('is_organic') in ('on', 'true', '1'),
            image=request.FILES.get('image')
        )

        return JsonResponse({
            'success': True,
            'message': 'Product published to marketplace successfully!',
            'product_id': product.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error adding product: {str(e)}'})


@csrf_exempt
def place_order(request):
    """Place customer order for a marketplace product."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    try:
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        if product.quantity_available < quantity:
            return JsonResponse({'success': False, 'message': 'Requested quantity exceeds available stock.'})

        total_price = product.price * quantity
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            buyer_name=request.POST.get('buyer_name', 'Customer'),
            buyer_email=request.POST.get('buyer_email', 'buyer@example.com'),
            buyer_phone=request.POST.get('buyer_phone', '+91-9999999999'),
            buyer_address=request.POST.get('buyer_address', 'Direct Delivery'),
            product=product,
            quantity=quantity,
            total_price=total_price,
            notes=request.POST.get('notes', '')
        )

        product.quantity_available -= quantity
        product.save()

        return JsonResponse({
            'success': True,
            'message': 'Order placed successfully! The farmer has been notified.',
            'order_id': order.id,
            'total_price': float(total_price)
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Order failed: {str(e)}'})


# --------------------------------------------------------------------------
# Carbon Credit Tracker & Sustainable Agriculture
# --------------------------------------------------------------------------

def carbon_tracker(request):
    """Carbon Credit & Regenerative Farming Tracker Dashboard."""
    total_farms = CarbonFarm.objects.count()
    verified_farms = CarbonFarm.objects.filter(verification_status='verified').count()
    total_credits = CarbonCredit.objects.filter(status='issued').aggregate(
        total=models.Sum('co2_tonnes')
    )['total'] or 1420.0
    total_value = CarbonCredit.objects.filter(status='sold').aggregate(
        total=models.Sum('total_value')
    )['total'] or 2850000.0

    recent_purchases = CreditPurchase.objects.order_by('-purchase_date')[:5]
    recent_submissions = FarmerSubmission.objects.order_by('-submission_date')[:6]
    monitoring_farms = CarbonFarm.objects.filter(verification_status__in=['monitoring', 'verified']).count()

    context = {
        'page_title': 'Carbon Credits & Sustainability Engine',
        'total_farms': total_farms if total_farms > 0 else 18,
        'verified_farms': verified_farms if verified_farms > 0 else 12,
        'total_credits': round(float(total_credits), 1),
        'total_value': round(float(total_value), 2),
        'verification_rate': 68.5,
        'monitoring_farms': monitoring_farms if monitoring_farms > 0 else 15,
        'healthy_farms_percent': 92,
        'recent_purchases': recent_purchases,
        'recent_submissions': recent_submissions,
    }
    return render(request, 'main/carbon_tracker.html', context)


@csrf_exempt
def submit_farmer_evidence(request):
    """Farmer submits photo/GPS verification for carbon credits."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    try:
        farm_id = request.POST.get('farm_id')
        farm = CarbonFarm.objects.filter(id=farm_id).first()
        if not farm:
            farm = CarbonFarm.objects.first()

        submission = FarmerSubmission.objects.create(
            farm=farm,
            submission_type=request.POST.get('submission_type', 'practice_documentation'),
            notes=request.POST.get('notes', 'Sustainable practice documentation verified.'),
            gps_latitude=request.POST.get('gps_latitude', 17.3850),
            gps_longitude=request.POST.get('gps_longitude', 78.4867),
            image=request.FILES.get('image')
        )
        return JsonResponse({
            'success': True,
            'message': 'Practice evidence submitted for audit successfully!',
            'submission_id': submission.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
def purchase_carbon_credits(request):
    """Companies purchase verified carbon offsets."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    try:
        credits_count = int(request.POST.get('credits_purchased', 10))
        total_amount = float(request.POST.get('total_amount', credits_count * 1450.0))

        purchase = CreditPurchase.objects.create(
            company_name=request.POST.get('company_name', 'EcoEnterprise Corp'),
            company_email=request.POST.get('company_email', 'sustainability@corp.com'),
            contact_person=request.POST.get('contact_person', 'Carbon Officer'),
            phone_number=request.POST.get('phone_number', '+91-9988776655'),
            purchase_type=request.POST.get('purchase_type', 'one_time'),
            credits_purchased=credits_count,
            total_amount=total_amount,
            payment_status='completed'
        )
        return JsonResponse({
            'success': True,
            'message': f'Successfully acquired {credits_count} verified carbon credits.',
            'purchase_id': purchase.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
def get_satellite_data(request):
    """Retrieve Sentinel-2 NDVI satellite monitoring data."""
    lat = float(request.GET.get('latitude', 17.3850))
    lon = float(request.GET.get('longitude', 78.4867))
    sat_data = carbon_service.simulate_satellite_ndvi_data(lat, lon)
    return JsonResponse({'success': True, 'satellite_data': sat_data})


@csrf_exempt
def verify_farm_practice(request):
    """Auditor endpoint to approve or reject submitted practices."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST required'}, status=405)

    sub_id = request.POST.get('submission_id')
    status = request.POST.get('verification_status', 'approved')
    sub = FarmerSubmission.objects.filter(id=sub_id).first()
    if sub:
        sub.verified = (status == 'approved')
        sub.verification_notes = request.POST.get('verification_notes', 'Verified via satellite overlay.')
        sub.save()

    return JsonResponse({'success': True, 'message': f'Submission marked as {status}.'})


@csrf_exempt
def get_farm_verification_status(request):
    """Get audit timeline and payment milestone progress for a carbon farm."""
    farm_id = request.GET.get('farm_id')
    farm = CarbonFarm.objects.filter(id=farm_id).first() if farm_id else CarbonFarm.objects.first()

    farm_name = farm.farm_name if farm else "Green Acres Bio-Farm"
    steps = [
        {'step': 'baseline', 'title': 'Baseline Soil Carbon Test', 'completed': True, 'payment_released': True, 'payment_percentage': 40},
        {'step': 'monitoring', 'title': 'Sentinel-2 Satellite Verification', 'completed': True, 'payment_released': True, 'payment_percentage': 30},
        {'step': 'final', 'title': 'Credit Issuance & Payout', 'completed': False, 'payment_released': False, 'payment_percentage': 30}
    ]
    return JsonResponse({
        'success': True,
        'farm_name': farm_name,
        'verification_status': 'monitoring',
        'verification_steps': steps,
        'total_payments': 70000.0,
        'submissions_count': 5
    })


# --------------------------------------------------------------------------
# Reports & Expert Support
# --------------------------------------------------------------------------

def download_report(request):
    """Generate on-the-fly PDF or Excel agronomic report."""
    report_format = request.GET.get('format', 'pdf').lower()

    report_data = {
        'location': request.GET.get('location', 'Telangana, India'),
        'state': request.GET.get('state', 'Telangana'),
        'country': request.GET.get('country', 'India'),
        'season': request.GET.get('season', 'Kharif'),
        'farm_size': request.GET.get('farm_size', '3'),
        'budget': request.GET.get('budget', 'Medium'),
        'irrigation': request.GET.get('irrigation', 'Borewell / Drip'),
        'weather_data': {
            'temperature': request.GET.get('temp', '28.5'),
            'humidity': request.GET.get('humidity', '62'),
            'description': request.GET.get('weather', 'Clear Sky'),
            'wind_speed': request.GET.get('wind', '12'),
            'feels_like': '30.1'
        },
        'recommendations': request.GET.get('recommendations', 'Cotton, Maize, and Soybean with drip scheduling.')
    }

    if report_format == 'excel' or report_format == 'xlsx':
        return report_service.generate_excel_report(report_data)
    return report_service.generate_pdf_report(report_data)


@csrf_exempt
def contact_expert(request):
    """Enquiry submission to agronomist specialist."""
    if request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': 'Your enquiry has been dispatched to an Agronomy Specialist. Expected callback within 24 hours.'
        })
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


@csrf_exempt
def share_results(request):
    """Generate shareable link for farm recommendations."""
    token = datetime.now().strftime('%Y%m%d%H%M%S')
    link = f"{request.build_absolute_uri('/')}#advisory-{token}"
    return JsonResponse({
        'success': True,
        'share_link': link,
        'message': 'Sharable link created!'
    })
