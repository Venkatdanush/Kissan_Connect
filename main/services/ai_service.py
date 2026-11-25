"""
Dual-Engine AI Service for KissanConnect.
Primary: Groq API (Ultra-fast, zero-latency inference, free-tier friendly).
Secondary: Google Gemini 3.5 Flash (Compact token budget to protect quota).
Offline: Curated Indian agronomic and plant pathology knowledge base.
"""

import logging
import requests
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


def _call_groq_api(prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
    """Execute chat completion via Groq API."""
    groq_key = getattr(settings, 'GROQ_API_KEY', None)
    if not groq_key:
        return None

    groq_models = [
        getattr(settings, 'GROQ_MODEL', 'openai/gpt-oss-20b'),
        'openai/gpt-oss-20b',
        'qwen/qwen3.8-27b',
        'openai/gpt-oss-120b',
    ]

    headers = {
        'Authorization': f'Bearer {groq_key}',
        'Content-Type': 'application/json'
    }

    messages = []
    if system_instruction:
        messages.append({'role': 'system', 'content': system_instruction})
    messages.append({'role': 'user', 'content': prompt})

    for model in groq_models:
        payload = {
            'model': model,
            'messages': messages,
            'temperature': 0.5,
            'max_tokens': 600,
        }
        try:
            resp = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=payload, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '')
                    if content:
                        logger.info(f"Groq API success with model: {model}")
                        return content.strip()
            else:
                logger.debug(f"Groq model {model} returned HTTP {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            logger.debug(f"Groq request to {model} failed: {e}")
            continue

    return None


def _call_gemini_api(prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
    """Execute request to Gemini API with strict token cap to conserve free tier."""
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        return None

    gemini_models = [
        getattr(settings, 'GEMINI_MODEL', 'gemini-3.5-flash'),
        'gemini-3.5-flash',
        'gemini-3.5-flash-lite',
        'gemini-3-flash-preview',
    ]

    headers = {'Content-Type': 'application/json'}

    for model_name in gemini_models:
        clean_model = model_name.replace('models/', '')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={api_key}"

        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 450  # Low token consumption to protect user's free tier
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts and 'text' in parts[0]:
                        logger.info(f"Gemini API success with model: {clean_model}")
                        return parts[0]['text'].strip()
        except Exception as e:
            logger.debug(f"Gemini model {clean_model} failed: {e}")
            continue

    return None


def generate_llm_response(prompt: str, system_instruction: Optional[str] = None) -> tuple[Optional[str], str]:
    """
    Unified LLM caller:
    Tries Groq first (fastest, free tier friendly), then falls back to Gemini.
    Returns (response_text, provider_name).
    """
    # 1. Try Groq
    groq_reply = _call_groq_api(prompt, system_instruction)
    if groq_reply:
        return groq_reply, 'groq'

    # 2. Try Gemini
    gemini_reply = _call_gemini_api(prompt, system_instruction)
    if gemini_reply:
        return gemini_reply, 'gemini'

    return None, 'offline'


def ask_farm_assistant(message: str) -> Dict[str, Any]:
    """Agricultural AI Chatbot assistant for farmers."""
    system_instruction = (
        "You are 'Kissan Sahayak' (Farmer's Smart Assistant), an expert agricultural scientist "
        "and agronomist dedicated to helping farmers worldwide.\n"
        "CRITICAL LANGUAGE RULE: Always respond in the EXACT same language as the user's message. "
        "If the user writes in English, reply strictly in English. If the user writes in Hindi, reply in Hindi. "
        "Never switch languages unless the user explicitly asks you to.\n\n"
        "Provide direct, highly practical, and actionable answers. Format your response cleanly with bullet points, "
        "bold headers, and concise steps. Cover soil care, organic remedies, irrigation, government schemes, "
        "and market selling tips."
    )

    reply, provider = generate_llm_response(message, system_instruction)
    if reply:
        return {
            'success': True,
            'response': reply,
            'source': provider
        }

    return {
        'success': True,
        'response': _get_chatbot_fallback(message),
        'source': 'knowledge_base'
    }


def format_markdown_to_html(md_text: str) -> str:
    """Format markdown text into rich HTML for browser rendering."""
    if not md_text:
        return ""
    import re
    html = md_text
    html = re.sub(r'###\s*(.*?)\n', r'<h5 class="mt-3 mb-2 text-success fw-bold"><i class="fas fa-check-circle me-2"></i>\1</h5>\n', html)
    html = re.sub(r'##\s*(.*?)\n', r'<h4 class="mt-4 mb-2 text-dark fw-bold">\1</h4>\n', html)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    lines = html.split('\n')
    formatted = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                formatted.append('<ul class="list-group list-group-flush mb-3">')
                in_list = True
            item = stripped[2:]
            formatted.append(f'<li class="list-group-item bg-transparent px-0 py-1"><i class="fas fa-seedling text-success me-2"></i>{item}</li>')
        else:
            if in_list:
                formatted.append('</ul>')
                in_list = False
            if stripped:
                formatted.append(f'<p class="mb-2">{stripped}</p>')
    if in_list:
        formatted.append('</ul>')
    return '\n'.join(formatted)


def generate_disease_remedies(disease_type: str, confidence: float) -> Dict[str, Any]:
    """Generate tailored organic and chemical remedies for identified plant diseases."""
    if "Healthy" in disease_type:
        raw_text = (
            "### Overview\n"
            f"**{disease_type}** confirmed with {confidence:.1f}% confidence. The plant tissue shows vigorous cellular health.\n\n"
            "### Maintenance Recommendations\n"
            "- Maintain optimal balanced drip or furrow irrigation.\n"
            "- Apply organic compost or vermicompost every 3-4 weeks to boost soil microbiome.\n"
            "- Ensure adequate plant spacing and sunlight exposure for sustained natural immunity."
        )
        return {
            'success': True,
            'disease_type': disease_type,
            'confidence': confidence,
            'ai_remedies': format_markdown_to_html(raw_text),
            'source': 'plant_pathology_engine'
        }

    prompt = (
        f"A plant leaf has been diagnosed with '{disease_type}' with {confidence:.1f}% confidence.\n"
        "As a senior plant pathologist, provide a structured management plan with:\n"
        "1. Brief Disease Overview (1-2 sentences on cause and threat level)\n"
        "2. Organic / Biological Remedies (3 practical eco-friendly treatments)\n"
        "3. Recommended Chemical Treatments (Safe fungicide/bactericide options with dosages)\n"
        "4. Preventive & Cultural Practices (Crop hygiene, watering techniques)\n\n"
        "Format with clear Markdown headings: '### Overview', '### Organic Treatments', '### Chemical Treatments', '### Prevention'."
    )

    reply, provider = generate_llm_response(prompt)
    if reply:
        return {
            'success': True,
            'disease_type': disease_type,
            'confidence': confidence,
            'ai_remedies': format_markdown_to_html(reply),
            'source': provider
        }

    return _get_curated_disease_remedies(disease_type, confidence)


def _get_chatbot_fallback(message: str) -> str:
    """Intelligent rule-based fallback when external LLMs are offline."""
    lower_msg = message.lower()
    if 'winter' in lower_msg or 'rabi' in lower_msg:
        return (
            "🌾 **Top Winter (Rabi) Crop Recommendations:**\n\n"
            "- **Wheat**: Requires cooler temperatures (15-20°C). Sow between late October and mid-November.\n"
            "- **Mustard / Rapeseed**: Low water requirement, high market oil value.\n"
            "- **Chickpeas (Gram)**: Excellent soil nitrogen fixer, minimal irrigation required.\n"
            "- **Vegetables**: Spinach, carrots, cauliflower, and peas yield fast returns.\n\n"
            "💡 *Tip:* Test soil moisture before sowing and apply balanced NPK (4:2:1) fertilizer."
        )
    elif 'summer' in lower_msg or 'zaid' in lower_msg:
        return (
            "☀️ **Top Summer (Zaid) Crop Recommendations:**\n\n"
            "- **Watermelon & Muskmelon**: High heat tolerance, excellent commercial return in 75-90 days.\n"
            "- **Cucumber & Gourds**: Quick turnaround with consistent drip irrigation.\n"
            "- **Moong Dal (Green Gram)**: Short duration (60 days) pulse that enriches the soil."
        )
    elif 'fertilizer' in lower_msg or 'soil' in lower_msg:
        return (
            "🧪 **Soil Health & Fertilizer Best Practices:**\n\n"
            "- Get your soil tested for pH, Nitrogen (N), Phosphorus (P), and Potassium (K).\n"
            "- Incorporate farmyard manure (FYM) or neem cake to improve organic matter.\n"
            "- Split nitrogen application into 2-3 stages to reduce volatilization and leaching."
        )
    elif 'pest' in lower_msg or 'disease' in lower_msg:
        return (
            "🌿 **Integrated Pest Management (IPM) Tips:**\n\n"
            "- Spray **Neem oil (5ml per liter)** with mild soap as a biological preventative against sucking pests.\n"
            "- Install yellow sticky traps (10 traps/acre) for whiteflies and aphids.\n"
            "- Remove and burn infected leaves early to stop pathogen spread."
        )
    else:
        return (
            "🌱 **KissanConnect Smart Farming Advisory:**\n\n"
            "Here are key recommendations for your farm:\n"
            "1. **Crop Health**: Monitor foliage weekly for early signs of rust, blight, or nutrient deficiency.\n"
            "2. **Water Efficiency**: Adopt drip or sprinkler irrigation to conserve up to 40% water while improving yield.\n"
            "3. **Market Access**: Connect with local buyers directly via our Marketplace to earn 15-25% higher margins by skipping middlemen.\n\n"
            "Feel free to ask specific questions about crop timing, soil fertility, or pest treatments!"
        )


def _get_curated_disease_remedies(disease_type: str, confidence: float) -> Dict[str, Any]:
    """Curated plant pathology database for offline resilience."""
    text = (
        f"### Overview\n"
        f"**{disease_type}** detected with {confidence:.1f}% algorithmic confidence. "
        "Immediate intervention is recommended to curb spread and protect crop yield.\n\n"
        "### Organic Treatments\n"
        "- Spray cold-pressed Neem oil (3-5 ml per liter of water) mixed with organic soap emulsifier.\n"
        "- Apply Trichoderma viride or Bacillus subtilis bio-fungicide to root zones.\n"
        "- Prune and destroy heavily blighted or infected foliage away from the farm.\n\n"
        "### Chemical Treatments\n"
        "- Apply Copper Oxychloride (2.5g/L) or Mancozeb (2g/L) for fungal leaf spots.\n"
        "- For bacterial blights, apply Streptocycline (1g / 10L) combined with copper fungicide.\n"
        "- Ensure full spray coverage under the leaves during cool morning or evening hours.\n\n"
        "### Preventive Measures\n"
        "- Avoid overhead irrigation; keep foliage dry.\n"
        "- Maintain optimal spacing for aeration and sunlight penetration.\n"
        "- Rotate crops with non-host species for at least two crop cycles."
    )
    return {
        'success': True,
        'disease_type': disease_type,
        'confidence': confidence,
        'ai_remedies': format_markdown_to_html(text),
        'source': 'knowledge_base'
    }
