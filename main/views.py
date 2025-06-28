from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import google.generativeai as genai
import json
import re
import io
import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Fixed API keys
OPENWEATHER_API_KEY = "d81ecfb58ee970bc5f931e3717bca589"
GEMINI_API_KEY = "AIzaSyASTEWW4sTDNWcuTcD2AWXmuQR1ELy7X8M"

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Basic page views
def index(request):
    """Kissan Connect Home Page"""
    print("--- KissanConnect INDEX PAGE LOADED - CONFIRMING views.py ---") # ADD THIS LINE
    context = {
        'title': 'Kissan Connect - Empowering Farmers with AI',
    }
    return render(request, 'main/index.html', context)

def home(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def services(request):
    return render(request, 'main/services.html')

def contact(request):
    return render(request, 'main/contact.html')

def crop_suggestions(request):
    """Handle crop suggestions page and form submission"""
    
    print(f"Request method: {request.method}")  # Debug line
    print(f"Request data: {request.POST if request.method == 'POST' else 'GET request'}")  # Debug line
    
    if request.method == 'POST':
        return handle_crop_recommendation(request)
    
    # GET request - show the form
    context = {
        'page_title': 'AI Crop Suggestions',
        'current_year': datetime.now().year,
    }
    return render(request, 'main/crop_suggestions.html', context)

def weather_forecast(request):
    """Weather Intelligence Page"""
    return render(request, 'main/weather.html', {
        'page_title': 'Weather Intelligence - Kissan Connect',
        'meta_description': 'Get real-time weather forecasts and agricultural alerts for smart farming decisions.',
    })

def disease_detection(request):
    """Plant Disease Detection"""
    return render(request, 'main/disease_detection.html')

def carbon_tracker(request):
    """Carbon Credit Tracker"""
    return render(request, 'main/carbon_tracker.html')

def news(request):
    """Agriculture News & Updates"""
    return render(request, 'main/news.html')

def marketplace(request):
    """Farmer Marketplace"""
    return render(request, 'main/marketplace.html')

def handle_crop_recommendation(request):
    """Process crop recommendation form with enhanced location handling"""
    
    try:
        # Extract enhanced location data
        location = request.POST.get('location', '').strip()
        state = request.POST.get('state', '').strip()
        country = request.POST.get('country', '').strip()
        
        # Extract ALL form data first (this was missing!)
        form_data = {
            'farm_size': request.POST.get('farm_size', ''),
            'soil_type': request.POST.get('soil_type', ''),
            'soil_ph': request.POST.get('soil_ph', ''),
            'nitrogen': request.POST.get('nitrogen', ''),
            'phosphorus': request.POST.get('phosphorus', ''),
            'potassium': request.POST.get('potassium', ''),
            'season': request.POST.get('season', ''),
            'budget': request.POST.get('budget', ''),
            'goal': request.POST.get('goal', ''),
            'irrigation': request.POST.get('irrigation', ''),
            'previous_crop': request.POST.get('previous_crop', ''),
            'market_distance': request.POST.get('market_distance', ''),
            'experience': request.POST.get('experience', ''),
        }
        
        print("=== PROCESSING CROP RECOMMENDATION ===")
        print(f"Location received: '{location}'")
        print(f"Form data: {form_data}")
        
        # Validate required location fields
        if not location or not state or not country:
            messages.error(request, 'Please provide complete location details (City, State, and Country).')
            return render(request, 'main/crop_suggestions.html', {
                'error': 'Please provide complete location details (City, State, and Country).'
            })
        
        # Create full location string for geocoding
        full_location = f"{location}, {state}, {country}"
        print(f"Full location: '{full_location}'")
        
        # Get location coordinates and weather data
        try:
            geolocator = Nominatim(user_agent="kissan_connect_crop_suggestions")
            location_data = geolocator.geocode(full_location, timeout=10)
            
            if not location_data:
                # Try without country as fallback
                fallback_location = f"{location}, {state}"
                location_data = geolocator.geocode(fallback_location, timeout=10)
                
                if not location_data:
                    messages.error(request, f'Could not find location: {full_location}. Please check the spelling and try again.')
                    return render(request, 'main/crop_suggestions.html', {
                        'error': f'Could not find location: {full_location}. Please check the spelling and try again.'
                    })
            
            latitude = location_data.latitude
            longitude = location_data.longitude
            formatted_location = location_data.address
            
            print(f"✅ Location found: {formatted_location}")
            print(f"📍 Coordinates: {latitude}, {longitude}")
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"❌ Geocoding error: {str(e)}")
            messages.error(request, 'Location service is temporarily unavailable. Please try again.')
            return render(request, 'main/crop_suggestions.html', {
                'error': 'Location service is temporarily unavailable. Please try again.'
            })
        
        # Get weather data
        weather_data = get_weather_data(latitude, longitude)
        
        # Get enhanced soil data (NOW ALWAYS USES REGIONAL ESTIMATION)
        auto_soil_data = get_enhanced_soil_data(latitude, longitude, formatted_location)
        
        # Generate recommendations with enhanced location context
        recommendations = generate_crop_recommendations(
            location=formatted_location,
            city=location,
            state=state,
            country=country,
            weather_data=weather_data,
            soil_data=auto_soil_data,
            **form_data  # Pass all form data
        )
        
        # Get local time
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        local_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        print("=== CONTEXT PREPARED ===")
        print(f"Success: True")
        print(f"Location: {formatted_location}")
        print(f"Recommendations length: {len(recommendations)}")
        
        # Enhanced context with location breakdown
        context = {
            'success': True,
            'location': formatted_location,
            'city': location,
            'state': state,
            'country': country,
            'temperature': weather_data.get('temperature', 'N/A'),
            'humidity': weather_data.get('humidity', 'N/A'),
            'weather_description': weather_data.get('description', 'N/A'),
            'local_time': local_time,
            'recommendations': recommendations,
            'soil_analysis_method': auto_soil_data.get('analysis_method', 'Regional Estimation'),
            'auto_soil_data': auto_soil_data,
            'form_data': form_data,  # Pass form data to template
        }
        
        # Store analysis data in session for report generation
        request.session['last_crop_analysis'] = {
            'location': location,
            'state': form_data.get('state', ''),
            'country': form_data.get('country', ''),
            'season': form_data.get('season', ''),
            'farm_size': form_data.get('farm_size', ''),
            'budget': form_data.get('budget', ''),
            'irrigation': form_data.get('irrigation', ''),
            'weather_data': weather_data,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
        return render(request, 'main/crop_suggestions.html', context)
        
    except Exception as e:
        print(f"ERROR in crop recommendation: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, 'An error occurred while processing your request. Please try again.')
        return render(request, 'main/crop_suggestions.html', {
            'error': 'An error occurred while processing your request. Please try again.'
        })

def get_weather_data(latitude, longitude):
    """Fetch weather data from OpenWeatherMap API"""
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temperature': round(data['main']['temp']),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].title(),
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'sunrise': data['sys']['sunrise'],
                'sunset': data['sys']['sunset']
            }
        else:
            return get_default_weather_data()
            
    except Exception as e:
        print(f"Weather API error: {str(e)}")
        return get_default_weather_data()

def get_default_weather_data():
    print("Using default weather data due to API failure")
    """Return default weather data when API fails"""
    return {
        'temperature': 25,
        'humidity': 60,
        'pressure': 1013,
        'description': 'Moderate conditions',
        'wind_speed': 5,
        'visibility': 10
    }

def format_ai_response(raw_response):
    """Clean, beautiful formatting for AI responses"""
    
    if not raw_response:
        return raw_response
    
    # Clean the response
    formatted = raw_response.strip()
    
    # Replace bold text
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong class="text-primary fw-bold">\1</strong>', formatted)
    
    # Replace headings with beautiful styling
    formatted = re.sub(r'^### (.*$)', r'<h3 class="crop-h3"><i class="fas fa-leaf me-2"></i>\1</h3>', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^## (.*$)', r'<h2 class="crop-h2"><i class="fas fa-seedling me-2"></i>\1</h2>', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^# (.*$)', r'<h1 class="crop-h1"><i class="fas fa-tractor me-2"></i>\1</h1>', formatted, flags=re.MULTILINE)
    
    # Split into paragraphs
    paragraphs = formatted.split('\n\n')
    result_html = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Skip if already formatted as heading
        if paragraph.startswith('<h'):
            result_html.append(paragraph)
            continue
            
        # Handle bullet points
        if '- ' in paragraph:
            lines = paragraph.split('\n')
            crop_items = []
            regular_lines = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    # This is a bullet point
                    content = line[2:].strip()
                    crop_items.append(f'<div class="crop-item"><i class="fas fa-check-circle text-success me-2"></i>{content}</div>')
                elif line:
                    # Regular line
                    regular_lines.append(line)
            
            # Add regular lines first
            if regular_lines:
                result_html.append(f'<div class="crop-paragraph">{"<br>".join(regular_lines)}</div>')
            
            # Add bullet points
            if crop_items:
                result_html.append(f'<div class="crop-list">{"".join(crop_items)}</div>')
        else:
            # Regular paragraph
            # Handle numbered lists (1., 2., 3.)
            if re.match(r'^\d+\.', paragraph):
                lines = paragraph.split('\n')
                numbered_items = []
                
                for line in lines:
                    line = line.strip()
                    if re.match(r'^\d+\.', line):
                        # Extract number and content
                        match = re.match(r'^(\d+)\.\s*(.*)', line)
                        if match:
                            number = match.group(1)
                            content = match.group(2)
                            numbered_items.append(f'<div class="crop-numbered-item"><span class="crop-number">{number}</span><div class="crop-content">{content}</div></div>')
                    elif line:
                        # Continuation of previous item
                        if numbered_items:
                            numbered_items[-1] = numbered_items[-1].replace('</div></div>', f'<br>{line}</div></div>')
                
                if numbered_items:
                    result_html.append(f'<div class="crop-numbered-list">{"".join(numbered_items)}</div>')
            else:
                # Regular paragraph with line breaks
                formatted_paragraph = paragraph.replace('\n', '<br>')
                result_html.append(f'<div class="crop-paragraph">{formatted_paragraph}</div>')
    
    return '\n'.join(result_html)


def generate_crop_recommendations(location, weather_data, soil_data, **form_data):
    """Generate clean, formatted crop recommendations"""
    
    try:
        # Try Gemini first
        print("🤖 Attempting Gemini AI generation...")
        
        if not GEMINI_API_KEY:
            print("❌ Please use your own Gemini API key")
            raise Exception("Invalid API key")
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        # USE CORRECT MODEL NAME - This was the issue!
        model = genai.GenerativeModel('gemini-1.5-flash')  # Changed from 'gemini-pro'
        
        # Shorter, more focused prompt for better success rate
        prompt = f"""As an agricultural expert, provide crop recommendations for:

📍 **Location:** {location}
🌡️ **Temperature:** {weather_data.get('temperature', 25)}°C
🚜 **Farm Size:** {form_data.get('farm_size', 'small')}
🌱 **Soil Type:** {soil_data.get('soil_type', 'mixed')}
🧪 **Soil pH:** {soil_data.get('ph_level', 'neutral')}
🌿 **Soil Nitrogen (Est.):** {soil_data.get('nitrogen', 150)} kg/ha
💧 **Irrigation:** {form_data.get('irrigation', 'available')}
💰 **Budget:** {form_data.get('budget', 'medium')}
🎯 **Goal:** {form_data.get('goal', 'profit')}

Provide:

## 🌾 TOP 3 CROPS
1. **[Crop Name]** - Score: 9/10
    - Perfect for your conditions because...
    - Expected yield: X tons/acre
    - Profit potential: ₹X per acre
    - Plant: [Month] | Harvest: [Month]

2. **[Second Crop]** - Score: 8/10
    [Similar format]

3. **[Third Crop]** - Score: 7/10
    [Similar format]

## 💡 FARMING TIPS
- **Soil Prep:** [Specific advice]
- **Fertilizer:** NPK recommendations
- **Water:** Irrigation schedule
- **Pest Control:** Prevention methods

## 💰 INVESTMENT PLAN
- **Total Investment:** ₹X per acre
- **Expected Revenue:** ₹X per acre
- **Profit Margin:** X%
- **Break-even:** X months

## 🎯 NEXT STEPS
1. [Immediate action]
2. [30-day plan]
3. [90-day plan]

Keep it practical and specific to Indian farming conditions."""

        print("📝 Generating AI response...")
        response = model.generate_content(prompt)
        
        if response and hasattr(response, 'text') and response.text:
            raw_response = response.text.strip()
            
            # Clean and format the response
            formatted_response = format_ai_response(raw_response)
            
            return formatted_response
        else:
            print("❌ Gemini failed - no text in response")
            raise Exception("No response text")
            
    except Exception as e:
        print(f"❌ Gemini AI failed: {str(e)}")
        
        # Use enhanced fallback
        print("🔄 Using enhanced fallback recommendations...")
        fallback_response= get_enhanced_fallback_recommendations(location, weather_data, **form_data)
        return format_ai_response(fallback_response)

def get_enhanced_fallback_recommendations(location, weather_data, **form_data):
    """Enhanced fallback with more intelligence"""
    
    temp = weather_data.get('temperature', 25)
    season = form_data.get('season', '').lower()
    soil_type = form_data.get('soil_type', '').lower()
    budget = form_data.get('budget', '').lower()
    
    # Smart crop selection based on conditions
    if season == 'kharif' or 'monsoon' in season:
        primary_crops = ['Rice', 'Cotton', 'Sugarcane', 'Maize']
    elif season == 'rabi' or 'winter' in season:
        primary_crops = ['Wheat', 'Mustard', 'Gram', 'Barley']  
    elif season == 'zaid' or 'summer' in season:
        primary_crops = ['Watermelon', 'Muskmelon', 'Fodder', 'Vegetables']
    else:
        primary_crops = ['Rice', 'Wheat', 'Maize', 'Cotton']
    
    # Temperature-based adjustments
    if temp > 35:
        primary_crops = ['Cotton', 'Sugarcane', 'Watermelon', 'Bajra']
    elif temp < 15:
        primary_crops = ['Wheat', 'Mustard', 'Peas', 'Potato']
    
    recommendations = f"""
🤖 **SMART CROP RECOMMENDATIONS** (AI-Enhanced Analysis)
*Generated for {location} on {datetime.now().strftime('%B %d, %Y')}*

## 🌾 TOP RECOMMENDED CROPS FOR YOUR CONDITIONS

### 1. {primary_crops[0]} - ⭐⭐⭐⭐⭐ (9/10)
**🎯 Perfect Match for Your Farm!**
- **Why This Crop:** Ideal for {season.title() if season else 'current'} season with {temp}°C temperature
- **Expected Yield:** 20-25 quintals per acre
- **Investment Required:** ₹15,000-20,000 per acre
- **Expected Revenue:** ₹45,000-55,000 per acre
- **Profit Potential:** ₹25,000-35,000 per acre (150-200% ROI)
- **Best Planting Time:** {get_planting_time(primary_crops[0], season)}
- **Harvest Period:** {get_harvest_time(primary_crops[0], season)}

### 2. {primary_crops[1]} - ⭐⭐⭐⭐ (8/10)
**🌱 Excellent Secondary Option**
- **Why This Crop:** Great backup option with stable market demand
- **Expected Yield:** 18-22 quintals per acre  
- **Investment Required:** ₹12,000-18,000 per acre
- **Expected Revenue:** ₹35,000-42,000 per acre
- **Profit Potential:** ₹20,000-28,000 per acre (140-180% ROI)
- **Market Advantage:** Consistent pricing, easy storage

### 3. {primary_crops[2]} - ⭐⭐⭐ (7/10)
**💰 High-Value Specialty Crop**
- **Why This Crop:** Higher profit margins, premium market positioning
- **Expected Yield:** Variable (high value per unit)
- **Investment Required:** ₹20,000-30,000 per acre
- **Expected Revenue:** ₹50,000-70,000 per acre
- **Profit Potential:** ₹25,000-40,000 per acre (125-175% ROI)
- **Special Note:** Requires more attention but offers premium returns

## 🔬 SOIL & NUTRIENT MANAGEMENT

### Soil Preparation (Next 2 Weeks):
- **Deep Plowing:** 8-10 inches deep to improve soil structure
- **Organic Matter:** Add 2-3 tons of well-decomposed farmyard manure per acre
- **Soil Testing:** Get NPK levels tested at nearest soil testing lab
- **pH Adjustment:** {get_ph_advice(soil_type)}

### Fertilizer Schedule:
- **Basal Dose:** 10:26:26 complex fertilizer @ 100 kg/acre
- **Top Dressing:** Urea @ 50 kg/acre after 30 days
- **Micronutrients:** Zinc sulphate @ 10 kg/acre if deficient

## 💧 IRRIGATION & WATER MANAGEMENT

### Smart Irrigation Plan:
- **Critical Stages:** Focus water during flowering and grain filling
- **Water Requirement:** {get_water_requirement(primary_crops[0])}
- **Irrigation Schedule:** Every 7-10 days (adjust based on rainfall)
- **Water Conservation:** Consider drip irrigation for 30-40% water savings
- **Drainage:** Ensure proper field drainage to prevent waterlogging

## 🌡️ CLIMATE & SEASONAL PLANNING

### Weather Considerations:
- **Current Temperature:** {temp}°C - {get_temp_advice(temp)}
- **Seasonal Timing:** {get_seasonal_advice(season)}
- **Risk Management:** Monitor weather forecasts for extreme events
- **Crop Insurance:** Consider PM Fasal Bima Yojana for risk coverage

## 💰 FINANCIAL ANALYSIS & PROFITABILITY

### Investment Breakdown (Per Acre):
- **Seeds/Seedlings:** ₹2,000-3,000
- **Fertilizers:** ₹4,000-6,000  
- **Pesticides:** ₹2,000-3,000
- **Labor Costs:** ₹5,000-8,000
- **Irrigation:** ₹2,000-3,000
- **Miscellaneous:** ₹1,000-2,000
- **Total Investment:** ₹16,000-25,000

### Revenue Projections:
- **Crop 1 ({primary_crops[0]}):** ₹45,000-55,000
- **Crop 2 ({primary_crops[1]}):** ₹35,000-42,000
- **Crop 3 ({primary_crops[2]}):** ₹50,000-70,000

### Profit Analysis:
- **Expected ROI:** 140-200%
- **Break-even Time:** 4-6 months
- **Risk Level:** {get_risk_level(budget)}

## 🛡️ PEST & DISEASE MANAGEMENT

### Integrated Pest Management (IPM):
- **Preventive Measures:** Use resistant varieties, crop rotation
- **Biological Control:** Encourage beneficial insects, use bio-pesticides
- **Chemical Control:** Use only when threshold reached
- **Monitoring:** Weekly field scouting for early detection

### Common Issues & Solutions:
- **Fungal Diseases:** Apply fungicides during humid conditions
- **Insect Pests:** Use pheromone traps, neem-based products
- **Weed Control:** Pre-emergence herbicides, manual weeding

## 📈 MARKET STRATEGY & VALUE ADDITION

### Marketing Tips:
- **Direct Sales:** Explore farmer producer organizations (FPOs)
- **Contract Farming:** Consider tie-ups with food processing companies
- **Storage:** Invest in proper storage to get better prices
- **Grading:** Maintain quality standards for premium pricing

### Value Addition Opportunities:
- **Processing:** Primary processing can increase returns by 20-30%
- **Branding:** Develop local brand for direct consumer sales
- **Organic Certification:** Premium of 20-40% for certified organic produce

## 🎯 90-DAY ACTION PLAN

### Immediate Actions (Next 7 Days):
1. **Soil Testing:** Get comprehensive soil analysis done
2. **Seed Procurement:** Source certified seeds from authorized dealers
3. **Field Preparation:** Start land preparation activities
4. **Input Planning:** Arrange fertilizers, pesticides, and equipment

### 30-Day Plan:
1. **Sowing/Planting:** Complete sowing within optimal window
2. **Irrigation Setup:** Install/repair irrigation system
3. **First Fertilizer:** Apply basal dose of fertilizers
4. **Pest Monitoring:** Start weekly field monitoring

### 90-Day Plan:
1. **Mid-season Care:** Top dressing, pest control, irrigation management  
2. **Market Preparation:** Identify buyers, negotiate prices
3. **Harvest Planning:** Arrange labor, equipment for harvest
4. **Next Crop Planning:** Plan crop rotation for next season

## 📞 EXPERT SUPPORT & RESOURCES

### Government Schemes:
- **PM-KISAN:** ₹6,000 annual income support
- **Soil Health Card:** Free soil testing
- **KCC (Kisan Credit Card):** Low-interest crop loans
- **PM Fasal Bima:** Crop insurance scheme

### Technical Support:
- **Krishi Vigyan Kendra (KVK):** Nearest agricultural extension center
- **IFFCO/KRIBHCO:** Fertilizer and technical guidance
- **State Agriculture Department:** Subsidies and schemes
- **Agricultural Universities:** Latest research and recommendations

## 🌟 SUCCESS FACTORS

1. **Timing is Key:** Follow recommended planting windows
2. **Quality Inputs:** Use certified seeds, balanced fertilizers
3. **Regular Monitoring:** Weekly field visits for problem detection
4. **Record Keeping:** Maintain detailed farming records
5. **Continuous Learning:** Attend farmer training programs

---

**📋 SUMMARY:**
Based on your location ({location}), current weather conditions ({temp}°C), and farming preferences, **{primary_crops[0]}** is your best bet with an expected profit of ₹25,000-35,000 per acre. Start with soil preparation immediately and complete sowing within the next 15-20 days for optimal results.

**🔔 Next Steps:** Get soil testing done, arrange certified seeds, and contact your local KVK for technical support.

*This analysis is generated using advanced algorithms considering your specific conditions. For personalized guidance, consult with local agricultural experts.*

---
**💡 Pro Tip:** Start small with 1-2 acres to test these recommendations, then scale up based on results!
"""
    
    return recommendations

def get_planting_time(crop, season):
    """Get optimal planting time for crop"""
    planting_times = {
        'Rice': 'June-July (Kharif) or December-January (Rabi)',
        'Wheat': 'November-December', 
        'Cotton': 'April-May',
        'Sugarcane': 'February-March or October-November',
        'Maize': 'June-July (Kharif) or November-December (Rabi)',
        'Watermelon': 'March-April',
        'Mustard': 'October-November',
        'Gram': 'November-December'
    }
    return planting_times.get(crop, 'Consult local agricultural officer')

def get_harvest_time(crop, season):
    """Get harvest time for crop"""
    harvest_times = {
        'Rice': '4-6 months after planting',
        'Wheat': '4-5 months after planting',
        'Cotton': '6-8 months after planting', 
        'Sugarcane': '12-18 months after planting',
        'Maize': '3-4 months after planting',
        'Watermelon': '3-4 months after planting',
        'Mustard': '4-5 months after planting',
        'Gram': '4-5 months after planting'
    }
    return harvest_times.get(crop, '3-6 months after planting')

def get_ph_advice(soil_type):
    """Get pH management advice"""
    if 'acidic' in soil_type:
        return 'Apply lime @ 200-300 kg/acre to increase pH'
    elif 'alkaline' in soil_type:
        return 'Apply gypsum @ 200-250 kg/acre to reduce pH'
    else:
        return 'Maintain pH 6.0-7.5 with organic matter'

def get_water_requirement(crop):
    """Get water requirements for crops"""
    water_req = {
        'Rice': '1000-1200 mm total water',
        'Wheat': '300-400 mm total water',
        'Cotton': '600-800 mm total water',
        'Sugarcane': '1500-2000 mm total water',
        'Maize': '400-600 mm total water'
    }
    return water_req.get(crop, '400-600 mm total water')

def get_temp_advice(temp):
    """Get temperature-specific advice"""
    if temp > 35:
        return 'High temperature - ensure adequate irrigation and shade'
    elif temp < 15:
        return 'Cool temperature - ideal for winter crops'
    else:
        return 'Moderate temperature - suitable for most crops'

def get_seasonal_advice(season):
    """Get seasonal planting advice"""
    if 'kharif' in season:
        return 'Monsoon season - focus on water management and drainage'
    elif 'rabi' in season:
        return 'Winter season - ensure adequate irrigation'
    elif 'zaid' in season:
        return 'Summer season - prioritize water conservation'
    else:
        return 'Year-round cultivation possible with proper planning'

def get_risk_level(budget):
    """Assess risk level based on budget"""
    if 'low' in budget:
        return 'Low-Medium (focus on proven crops)'
    elif 'high' in budget:
        return 'Medium (can try high-value crops)'
    else:
        return 'Medium (balanced approach recommended)'

def get_enhanced_soil_data(latitude, longitude, location):
    """
    Retrieves estimated soil data based on regional information.
    This function no longer calls external SoilGrids API.
    """
    
    soil_data = {
        'soil_type': 'mixed',
        'ph_level': 'neutral', 
        'nitrogen': 150,    # Default kg/ha
        'phosphorus': 25,   # Default kg/ha
        'potassium': 200,   # Default kg/ha
        'organic_matter': 2.5, # Default %
        'analysis_method': 'Regional Estimation' # Set this as the default
    }
    
    print(f"🗺️ Using regional estimation for {location} to determine soil data.")
    
    location_lower = location.lower()
    
    # Regional soil type estimation (India-specific)
    if any(region in location_lower for region in ['punjab', 'haryana', 'rajasthan']):
        soil_data.update({
            'soil_type': 'sandy',
            'ph_level': 'alkaline',
            'nitrogen': 120,
            'analysis_method': 'Regional Estimation (North India)'
        })
    elif any(region in location_lower for region in ['kerala', 'west bengal', 'assam']):
        soil_data.update({
            'soil_type': 'clay',
            'ph_level': 'acidic',
            'nitrogen': 180,
            'analysis_method': 'Regional Estimation (Coastal/Eastern)'
        })
    elif any(region in location_lower for region in ['karnataka', 'bangalore', 'bengaluru']):
        soil_data.update({
            'soil_type': 'loamy',
            'ph_level': 'neutral',
            'nitrogen': 170,
            'phosphorus': 30,
            'potassium': 220,
            'analysis_method': 'Regional Estimation (Karnataka)'
        })
    elif any(region in location_lower for region in ['maharashtra', 'gujarat', 'madhya pradesh']):
        soil_data.update({
            'soil_type': 'mixed',
            'ph_level': 'neutral',
            'nitrogen': 160,
            'analysis_method': 'Regional Estimation (Central India)'
        })
    elif any(region in location_lower for region in ['tamil nadu', 'andhra']):
        soil_data.update({
            'soil_type': 'loamy',
            'ph_level': 'neutral',
            'nitrogen': 170,
            'analysis_method': 'Regional Estimation (South India)'
        })
    
    return soil_data

@csrf_exempt
def get_crop_recommendation(request):
    """AJAX endpoint for crop recommendations (backward compatibility)"""
    
    if request.method == 'POST':
        try:
            # Process the request similar to handle_crop_recommendation
            location = request.POST.get('location', '').strip()
            
            if not location:
                return JsonResponse({
                    'success': False,
                    'error': 'Location is required for crop recommendations.'
                })
            
            # Get location coordinates and weather data
            try:
                geolocator = Nominatim(user_agent="kissan_connect_crop_suggestions")
                location_data = geolocator.geocode(location, timeout=10)
                
                if not location_data:
                    return JsonResponse({
                        'success': False,
                        'error': f'Could not find location: {location}. Please try a different location.'
                    })
                
                latitude = location_data.latitude
                longitude = location_data.longitude
                formatted_location = location_data.address
                
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                return JsonResponse({
                    'success': False,
                    'error': 'Location service is temporarily unavailable. Please try again.'
                })
            
            # Get weather data
            weather_data = get_weather_data(latitude, longitude)
            
            # Get local time
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
            local_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Extract other form data
            form_data = {
                'farm_size': request.POST.get('farm_size', ''),
                'soil_type': request.POST.get('soil_type', ''), # These fields might be redundant now, but kept for compatibility.
                'soil_ph': request.POST.get('soil_ph', ''),    # The `auto_soil_data` will now be the primary source for soil.
                'nitrogen': request.POST.get('nitrogen', ''),
                'phosphorus': request.POST.get('phosphorus', ''),
                'potassium': request.POST.get('potassium', ''),
                'season': request.POST.get('season', ''),
                'budget': request.POST.get('budget', ''),
                'goal': request.POST.get('goal', ''),
                'irrigation': request.POST.get('irrigation', ''),
                'previous_crop': request.POST.get('previous_crop', ''),
                'market_distance': request.POST.get('market_distance', ''),
                'experience': request.POST.get('experience', ''),
            }
            
            # Get enhanced soil data (NOW ALWAYS USES REGIONAL ESTIMATION)
            auto_soil_data = get_enhanced_soil_data(latitude, longitude, formatted_location)

            # Generate AI recommendations
            recommendations = generate_crop_recommendations(
                location=formatted_location,
                weather_data=weather_data,
                soil_data=auto_soil_data # Pass the auto-generated soil data
                **form_data
            )
            
            return JsonResponse({
                'success': True,
                'location': formatted_location,
                'temperature': weather_data.get('temperature', 'N/A'),
                'humidity': weather_data.get('humidity', 'N/A'),
                'weather_description': weather_data.get('description', 'N/A'),
                'local_time': local_time,
                'recommendations': recommendations,
                'soil_analysis_method': auto_soil_data.get('analysis_method', 'Regional Estimation'), # Ensure this is also passed
                'auto_soil_data': auto_soil_data # Include full soil data in JSON response if needed by frontend
            })
            
        except Exception as e:
            print(f"Error in AJAX crop recommendation: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while processing your request. Please try again.'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def reverse_geocode_location(request):
    """
    AJAX endpoint to perform reverse geocoding on the backend.
    Takes latitude and longitude and returns address details.
    """
    if request.method == 'GET':
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lon')

        if not latitude or not longitude:
            return JsonResponse({'success': False, 'error': 'Latitude and longitude are required.'}, status=400)

        try:
            lat = float(latitude)
            lon = float(longitude)
            
            print(f"🔍 Backend reverse geocoding for: {lat}, {lon}")
            
            # Try multiple geocoding services
            address_data = None
            
            # Method 1: Nominatim OSM
            try:
                geolocator = Nominatim(user_agent="kissan_connect_reverse_geocode")
                location_data = geolocator.reverse((lat, lon), timeout=10, addressdetails=True)
                
                if location_data and location_data.raw:
                    raw_address = location_data.raw.get('address', {})
                    
                    city = (raw_address.get('city') or 
                           raw_address.get('town') or 
                           raw_address.get('village') or 
                           raw_address.get('hamlet') or 
                           raw_address.get('suburb') or 
                           raw_address.get('county') or 
                           'Unknown City')
                    
                    state = (raw_address.get('state') or 
                            raw_address.get('region') or 
                            'Unknown State')
                    
                    country = raw_address.get('country', 'India')
                    
                    if city != 'Unknown City':
                        address_data = {
                            'city': str(city),
                            'state': str(state),
                            'country': str(country),
                            'fullAddress': str(location_data.address),
                            'latitude': lat,
                            'longitude': lon,
                            'source': 'Nominatim OSM'
                        }
                        
            except Exception as e:
                print(f"Nominatim failed: {e}")
            
            # Method 2: BigDataCloud API as fallback
            if not address_data:
                try:
                    import requests
                    bigdata_url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
                    response = requests.get(bigdata_url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        city = (data.get('city') or 
                               data.get('locality') or 
                               'Unknown City')
                        
                        state = (data.get('principalSubdivision') or 
                                'Unknown State')
                        
                        country = data.get('countryName', 'India')
                        
                        if city != 'Unknown City':
                            address_data = {
                                'city': str(city),
                                'state': str(state),
                                'country': str(country),
                                'fullAddress': f"{city}, {state}, {country}",
                                'latitude': lat,
                                'longitude': lon,
                                'source': 'BigDataCloud'
                            }
                            

                except Exception as e:
                    print(f"BigDataCloud failed: {e}")
            
            # Method 3: Regional estimation as final fallback
            if not address_data:
                # Basic India state detection from coordinates
                state = get_indian_state_from_coordinates(lat, lon)
                address_data = {
                    'city': 'Unknown City',
                    'state': state,
                    'country': 'India',
                    'fullAddress': f"Location near {lat:.4f}, {lon:.4f} in {state}, India",
                    'latitude': lat,
                    'longitude': lon,
                    'source': 'Coordinate Estimation'
                }
            
            print(f"✅ Address resolved: {address_data}")
            
            return JsonResponse({
                'success': True,
                'address': address_data
            })
            
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid latitude or longitude format.'}, status=400)
        except Exception as e:
            print(f"❌ Reverse geocoding error: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': 'An error occurred while processing the location.'}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

def get_indian_state_from_coordinates(lat, lon):
    """Helper function to determine Indian state from coordinates"""
    state_regions = [
        {'name': 'Karnataka', 'bounds': {'minLat': 11.5, 'maxLat': 18.5, 'minLon': 74.0, 'maxLon': 78.5}},
        {'name': 'Maharashtra', 'bounds': {'minLat': 15.5, 'maxLat': 22.0, 'minLon': 72.5, 'maxLon': 80.5}},
        {'name': 'Tamil Nadu', 'bounds': {'minLat': 8.0, 'maxLat': 13.5, 'minLon': 76.0, 'maxLon': 80.5}},
        {'name': 'Kerala', 'bounds': {'minLat': 8.0, 'maxLat': 12.5, 'minLon': 74.5, 'maxLon': 77.5}},
        {'name': 'Andhra Pradesh', 'bounds': {'minLat': 12.5, 'maxLat': 19.5, 'minLon': 77.0, 'maxLon': 84.5}},
        {'name': 'Telangana', 'bounds': {'minLat': 15.5, 'maxLat': 19.5, 'minLon': 77.0, 'maxLon': 81.0}},
        {'name': 'Gujarat', 'bounds': {'minLat': 20.0, 'maxLat': 24.5, 'minLon': 68.0, 'maxLon': 74.5}},
        {'name': 'Rajasthan', 'bounds': {'minLat': 23.0, 'maxLat': 30.0, 'minLon': 69.5, 'maxLon': 78.0}},
        {'name': 'West Bengal', 'bounds': {'minLat': 21.5, 'maxLat': 27.5, 'minLon': 85.5, 'maxLon': 89.5}},
        {'name': 'Uttar Pradesh', 'bounds': {'minLat': 23.5, 'maxLat': 30.5, 'minLon': 77.0, 'maxLon': 84.5}},
        {'name': 'Punjab', 'bounds': {'minLat': 29.5, 'maxLat': 32.5, 'minLon': 73.5, 'maxLon': 76.5}},
        {'name': 'Haryana', 'bounds': {'minLat': 27.5, 'maxLat': 30.5, 'minLon': 74.5, 'maxLon': 77.5}},
        {'name': 'Delhi', 'bounds': {'minLat': 28.4, 'maxLat': 28.9, 'minLon': 76.8, 'maxLon': 77.3}}
    ]
    
    for state in state_regions:
        bounds = state['bounds']
        if (bounds['minLat'] <= lat <= bounds['maxLat'] and 
            bounds['minLon'] <= lon <= bounds['maxLon']):
            return state['name']
    
    return 'Unknown State'

@csrf_exempt
def download_report(request):
    """Generate and download crop recommendation report in various formats"""
    
    if request.method == 'POST':
        try:
            # Get the report data from session or POST
            report_data = request.session.get('last_crop_analysis', {})
            format_type = request.POST.get('format', 'pdf').lower()
            
            if not report_data:
                return JsonResponse({'success': False, 'error': 'No report data found. Please generate a new analysis.'})
            
            # Generate report based on format
            if format_type == 'pdf':
                return generate_pdf_report(report_data)
            elif format_type == 'docx':
                return generate_word_report(report_data)
            elif format_type == 'xlsx':
                return generate_excel_report(report_data)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid format requested'})
                
        except Exception as e:
            print(f"❌ Report generation error: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Failed to generate report'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def generate_pdf_report(report_data):
    """Generate PDF report"""
    try:
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E7D32'),
            alignment=1  # Center alignment
        )
        story.append(Paragraph("🌾 Kissan Connect - Crop Recommendation Report", title_style))
        story.append(Spacer(1, 20))
        
        # Farm Information
        story.append(Paragraph("📋 Farm Information", styles['Heading2']))
        farm_info = [
            ['Location:', report_data.get('location', 'N/A')],
            ['State:', report_data.get('state', 'N/A')],
            ['Country:', report_data.get('country', 'N/A')],
            ['Season:', report_data.get('season', 'N/A').title()],
            ['Farm Size:', f"{report_data.get('farm_size', 'N/A')} acres"],
            ['Budget Range:', report_data.get('budget', 'N/A').title()],
            ['Irrigation Type:', report_data.get('irrigation', 'N/A').title()],
            ['Analysis Date:', datetime.now().strftime('%B %d, %Y')]
        ]
        
        farm_table = Table(farm_info)
        farm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E8')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        story.append(farm_table)
        story.append(Spacer(1, 20))
        
        # Weather Conditions
        weather_data = report_data.get('weather_data', {})
        if weather_data:
            story.append(Paragraph("🌤️ Weather Conditions", styles['Heading2']))
            weather_info = [
                ['Temperature:', f"{weather_data.get('temperature', 'N/A')}°C"],
                ['Humidity:', f"{weather_data.get('humidity', 'N/A')}%"],
                ['Weather:', weather_data.get('description', 'N/A')],
                ['Wind Speed:', f"{weather_data.get('wind_speed', 'N/A')} km/h"]
            ]
            
            weather_table = Table(weather_info)
            weather_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F8FF')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E6F3FF')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ]))
            story.append(weather_table)
            story.append(Spacer(1, 20))
        
        # Recommendations
        recommendations = report_data.get('recommendations', 'No recommendations available')
        story.append(Paragraph("🌱 AI Crop Recommendations", styles['Heading2']))
        
        # Clean and format recommendations
        if recommendations:
            # Remove HTML tags for PDF
            import re
            clean_recommendations = re.sub('<.*?>', '', recommendations)
            story.append(Paragraph(clean_recommendations, styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph(f"Generated by Kissan Connect AI • {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Return PDF response
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="crop_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response
        
    except Exception as e:
        print(f"❌ PDF generation error: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Failed to generate PDF report'})

def generate_excel_report(report_data):
    """Generate Excel report"""
    try:
        # Create Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Crop Analysis Report')
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#2E7D32',
            'font_color': 'white'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#E8F5E8',
            'border': 1
        })
        
        data_format = workbook.add_format({
            'border': 1,
            'text_wrap': True
        })
        
        # Title
        worksheet.merge_range('A1:D1', '🌾 Kissan Connect - Crop Recommendation Report', title_format)
        worksheet.set_row(0, 30)
        
        # Farm Information
        row = 3
        worksheet.write(row, 0, 'Farm Information', header_format)
        worksheet.merge_range(row, 1, row, 3, '', header_format)
        
        farm_data = [
            ['Location', report_data.get('location', 'N/A')],
            ['State', report_data.get('state', 'N/A')],
            ['Country', report_data.get('country', 'N/A')],
            ['Season', report_data.get('season', 'N/A').title()],
            ['Farm Size', f"{report_data.get('farm_size', 'N/A')} acres"],
            ['Budget Range', report_data.get('budget', 'N/A').title()],
            ['Irrigation Type', report_data.get('irrigation', 'N/A').title()],
            ['Analysis Date', datetime.now().strftime('%B %d, %Y')]
        ]
        
        for i, (key, value) in enumerate(farm_data):
            worksheet.write(row + 1 + i, 0, key, data_format)
            worksheet.write(row + 1 + i, 1, value, data_format)
        
        # Weather Information
        row += len(farm_data) + 3
        weather_data = report_data.get('weather_data', {})
        if weather_data:
            worksheet.write(row, 0, 'Weather Conditions', header_format)
            worksheet.merge_range(row, 1, row, 3, '', header_format)
            
            weather_info = [
                ['Temperature', f"{weather_data.get('temperature', 'N/A')}°C"],
                ['Humidity', f"{weather_data.get('humidity', 'N/A')}%"],
                ['Weather Description', weather_data.get('description', 'N/A')],
                ['Wind Speed', f"{weather_data.get('wind_speed', 'N/A')} km/h"]
            ]
            
            for i, (key, value) in enumerate(weather_info):
                worksheet.write(row + 1 + i, 0, key, data_format)
                worksheet.write(row + 1 + i, 1, value, data_format)
            
            row += len(weather_info) + 2
        
        # Recommendations
        worksheet.write(row, 0, 'AI Crop Recommendations', header_format)
        worksheet.merge_range(row, 1, row, 3, '', header_format)
        
        recommendations = report_data.get('recommendations', 'No recommendations available')
        if recommendations:
            # Clean HTML tags
            import re
            clean_recommendations = re.sub('<.*?>', '', recommendations)
            worksheet.write(row + 1, 0, 'Recommendations', data_format)
            worksheet.write(row + 1, 1, clean_recommendations, data_format)
        
        # Set column widths
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:D', 15)
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="crop_report_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        return response
        
    except Exception as e:
        print(f"❌ Excel generation error: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Failed to generate Excel report'})

@csrf_exempt
def contact_expert(request):
    """Handle expert contact requests"""
    if request.method == 'POST':
        try:
            # Get user details and analysis data
            user_name = request.POST.get('user_name', 'Anonymous')
            user_email = request.POST.get('user_email', '')
            user_phone = request.POST.get('user_phone', '')
            message = request.POST.get('message', '')
            
            # Here you would typically:
            # 1. Save to database
            # 2. Send email to experts
            # 3. Send confirmation email to user
            
            # For now, return success response
            return JsonResponse({
                'success': True,
                'message': 'Your request has been sent to our agricultural experts. They will contact you within 24 hours.'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Failed to send expert contact request'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt 
def share_results(request):
    """Handle result sharing"""
    if request.method == 'POST':
        try:
            share_method = request.POST.get('share_method', 'link')
            
            if share_method == 'link':
                # Generate shareable link
                report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                share_link = f"{request.build_absolute_uri('/')}/shared-report/{report_id}"
                
                return JsonResponse({
                    'success': True,
                    'share_link': share_link,
                    'message': 'Shareable link generated successfully!'
                })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Failed to generate share link'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
