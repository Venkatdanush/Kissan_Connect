"""
Crop Recommendation and Agronomic Advisory Service for KissanConnect.
Provides rule-based agronomic modeling enhanced with generative AI insights.
"""

import re
import logging
from typing import Dict, Any, List
from django.conf import settings
import google.generativeai as genai
from .ai_service import generate_llm_response

logger = logging.getLogger(__name__)


def generate_crop_recommendations(location: str, weather_data: Dict[str, Any], soil_data: Dict[str, Any], **form_data) -> str:
    """Generate structured HTML-formatted crop recommendations with AI and fallback."""
    prompt = f"""As an expert agronomist, provide crop recommendations for:

📍 **Location:** {location}
🌡️ **Temperature:** {weather_data.get('temperature', 25)}°C
🚜 **Farm Size:** {form_data.get('farm_size', 2)} acres
🌱 **Soil Type:** {soil_data.get('soil_type', 'Loamy')}
🧪 **Soil pH:** {soil_data.get('ph_level', 6.5)}
🌿 **Soil Nitrogen (Est.):** {soil_data.get('nitrogen', 150)} kg/ha
💧 **Irrigation:** {form_data.get('irrigation', 'Canal / Borewell')}
💰 **Budget:** {form_data.get('budget', 'Medium')}
🎯 **Goal:** High Profit & Sustainable Yield

Provide:

## 🌾 TOP 3 CROPS
1. **[Crop 1 Name]** - Suitability: 9.5/10
   - Expected Yield & Profit Potential
   - Sowing Window & Harvest Timeline

2. **[Crop 2 Name]** - Suitability: 8.8/10
   - Expected Yield and Inputs required

3. **[Crop 3 Name]** - Suitability: 8.2/10
   - Expected Yield and Risk factor

## 💡 AGRONOMIC & SOIL TIPS
- Soil Preparation & Balanced NPK Schedule
- Irrigation Scheduling & Pest Management

## 💰 FINANCIAL OUTLOOK (Per Acre)
- Estimated Cost, Revenue, Net Profit Margin

Keep it concise and practical."""

    reply, provider = generate_llm_response(prompt)
    if reply:
        logger.info(f"Crop recommendations generated via {provider}")
        return format_ai_response(reply)

    fallback_text = get_enhanced_fallback_recommendations(location, weather_data, **form_data)
    return format_ai_response(fallback_text)


def format_ai_response(raw_response: str) -> str:
    """Format markdown text into rich HTML cards and badges for frontend rendering."""
    if not raw_response:
        return "<p class='text-muted'>No recommendation generated.</p>"

    # Convert Markdown headers
    html = raw_response
    html = re.sub(r'##\s*(.*?)\n', r'<h3 class="crop-section-header mt-4 mb-3 text-success font-weight-bold"><i class="fas fa-seedling me-2"></i>\1</h3>\n', html)
    html = re.sub(r'###\s*(.*?)\n', r'<h5 class="crop-sub-header mt-3 mb-2 text-dark font-weight-bold">\1</h5>\n', html)

    # Convert bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)

    # Convert bullet points
    lines = html.split('\n')
    formatted_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                formatted_lines.append('<ul class="list-unstyled ps-2 mb-3">')
                in_list = True
            item_text = stripped[2:]
            formatted_lines.append(f'<li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>{item_text}</li>')
        elif re.match(r'^\d+\.\s+', stripped):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<div class="crop-card card shadow-sm border-0 mb-3 p-3 bg-light"><div class="card-body p-0">{stripped}</div></div>')
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            if stripped:
                formatted_lines.append(f'<p class="mb-2">{stripped}</p>')

    if in_list:
        formatted_lines.append('</ul>')

    return '\n'.join(formatted_lines)


def get_enhanced_fallback_recommendations(location: str, weather_data: Dict[str, Any], **form_data) -> str:
    """Rule-based agro-climatic fallback engine."""
    temp = weather_data.get('temperature', 28)
    season = str(form_data.get('season', 'kharif')).lower()

    if 'rabi' in season or 'winter' in season or temp < 20:
        c1, c2, c3 = 'Wheat (PBW 550 / Sharbati)', 'Mustard (Pusa Bold)', 'Chickpea / Bengal Gram'
        sow_harv = 'Sow: Nov | Harvest: March-April'
    elif 'zaid' in season or 'summer' in season or temp > 33:
        c1, c2, c3 = 'Watermelon (Sugar Baby)', 'Cucumber / Summer Squashes', 'Green Gram (Moong Dal)'
        sow_harv = 'Sow: Feb-March | Harvest: May-June'
    else:  # Kharif / Monsoon
        c1, c2, c3 = 'Rice / Paddy (Basmati / IR-64)', 'Cotton (Bt Hybrid)', 'Soybean (JS 335)'
        sow_harv = 'Sow: June-July | Harvest: Oct-Nov'

    return f"""## 🌾 TOP 3 CROPS

1. **{c1}** - Suitability: 9.4/10
   - Highly adapted to {location} climate and prevailing conditions ({temp}°C).
   - Expected Yield: 18 - 24 Quintals/Acre
   - Profit Potential: ₹45,000 - ₹65,000 net profit per acre
   - Timeline: {sow_harv}

2. **{c2}** - Suitability: 8.8/10
   - Moderate water requirement, excellent cash liquidity in local mandis.
   - Expected Yield: 10 - 14 Quintals/Acre
   - Profit Potential: ₹35,000 - ₹50,000 net profit per acre

3. **{c3}** - Suitability: 8.2/10
   - High soil nitrogen fixation benefit for subsequent crop rotation.
   - Expected Yield: 7 - 10 Quintals/Acre
   - Profit Potential: ₹28,000 - ₹40,000 net profit per acre

## 💡 AGRONOMIC & SOIL TIPS
- Incorporate 5 tons/acre well-rotted farmyard manure (FYM) 2 weeks before sowing.
- Treat seeds with Trichoderma viride (4g/kg seed) to prevent damping-off and root wilt.
- Apply neem-coated urea in 3 equal splits: basal, vegetative, and panicle initiation.
- Employ micro-drip or furrow irrigation to maximize water efficiency.

## 💰 FINANCIAL OUTLOOK (Per Acre)
- **Estimated Input Cost:** ₹18,000 - ₹24,000
- **Gross Revenue Potential:** ₹65,000 - ₹85,000
- **Net Profit Margin:** 60% - 72%
- **Payback Horizon:** 3.5 - 4.5 months"""


def get_soil_data_by_coords(lat: float, lon: float, location_name: str = '') -> Dict[str, Any]:
    """Provide estimated soil characteristics based on geographic regional agro-zones."""
    # Central/Western India: Black Cotton Soil
    # Northern Indo-Gangetic Plains: Alluvial Soil
    # Southern Peninsula: Red & Laterite Soil
    if 18.0 <= lat <= 26.0 and 73.0 <= lon <= 80.0:
        soil_type = 'Black Cotton Soil (Vertisol)'
        ph = 7.6
        nitrogen = 180
        potassium = 320
        phosphorus = 18
    elif lat > 26.0:
        soil_type = 'Alluvial Loamy Soil'
        ph = 7.1
        nitrogen = 220
        potassium = 280
        phosphorus = 24
    else:
        soil_type = 'Red Sandy Loam'
        ph = 6.4
        nitrogen = 160
        potassium = 240
        phosphorus = 16

    return {
        'soil_type': soil_type,
        'ph_level': ph,
        'nitrogen': nitrogen,
        'potassium': potassium,
        'phosphorus': phosphorus,
        'organic_carbon': '0.58%'
    }
