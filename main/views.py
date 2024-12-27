from django.shortcuts import render
import os
print(os.listdir(os.path.dirname(__file__)))
def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')  # Render your HTML template
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import LocationForm
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
import google.generativeai as genai
import json

OPENWEATHER_API_KEY = "d81ecfb58ee970bc5f931e3717bca589"
GEMINI_API_KEY = "AIzaSyASTEWW4sTDNWcuTcD2AWXmuQR1ELy7X8M"

# Function to get latitude and longitude from location
def get_lat_lon(location):
    geolocator = Nominatim(user_agent="weatherforecast")
    try:
        location = geolocator.geocode(location)
        if location:
            return location.latitude, location.longitude, location
        else:
            raise ValueError("Location not found")
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Error: {e}")
        raise

# Function to get timezone and local time
def get_timezone_and_local_time(lat, lon):
    obj = TimezoneFinder()
    result = obj.timezone_at(lng=lon, lat=lat)
    home = pytz.timezone(result)
    local_time = datetime.now(home)
    current_time = local_time.strftime("%I:%M %p")
    return result, current_time

# Function to get extended weather data
def get_three_month_forecast(city):
    api_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&cnt=90"
    json_data = requests.get(api_url).json()
    return json_data

# Function to predict natural calamities using the Gemini model
def predict_calamities(extended_weather_data):
    genai.configure(api_key=GEMINI_API_KEY)
    generation_config = {"temperature": 0.9, "top_p": 1, "top_k": 1, "max_output_tokens": 2048}
    model = genai.GenerativeModel("gemini-pro", generation_config=generation_config)

    prompt = f"Based on the following weather forecast data for the next three months, predict the likelihood of any natural calamities and provide preventive advice and preventive measures to prevent the crop loss due to natural calamities:\n{json.dumps(extended_weather_data, indent=2)}"
    response = model.generate_content([prompt])
    calamity_prediction = response.text.strip()
    calamity_prediction = calamity_prediction.replace("**", "").replace("- ", "")
    return calamity_prediction

# Handle AJAX request and return the result on the same page
def get_weather_data(request):
    if request.method == 'POST' and request.is_ajax():
        location = request.POST.get('location')
        try:
            lat, lon, location_obj = get_lat_lon(location)
            timezone, current_time = get_timezone_and_local_time(lat, lon)
            extended_weather_data = get_three_month_forecast(location)
            calamity_prediction = predict_calamities(extended_weather_data)

            # Prepare data to send back to the user
            context = {
                'timezone': timezone,
                'local_time': current_time,
                'coordinates': f"{round(lat, 4)}°N, {round(lon, 4)}°E",
                'calamity_prediction': calamity_prediction
            }

            # Render the result as HTML
            result_html = render_to_string('weather_result.html', context)
            return JsonResponse({'result': result_html})

        except ValueError as e:
            return JsonResponse({'result': f'<div class="alert alert-danger">{str(e)}</div>'})

    return render(request, 'index.html')

