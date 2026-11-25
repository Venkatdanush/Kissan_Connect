from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('services/', views.services, name='services'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('crop-suggestions/', views.crop_suggestions, name='crop_suggestions'),
    path('weather/', views.weather_forecast, name='weather'),
    path('disease-detection/', views.disease_detection, name='disease_detection'),
    path('carbon-tracker/', views.carbon_tracker, name='carbon_tracker'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('news/', views.news, name='news'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('chat/', views.ai_assistant, name='chat'),
    path('api/ai-chat-advanced/', views.ai_chat_advanced, name='ai_chat_advanced'),
    path('api/crop-recommendation/', views.get_crop_recommendation, name='get_crop_recommendation'),
    path('api/reverse-geocode/', views.reverse_geocode_location, name='reverse_geocode'),
    path('api/reverse-geocode-api/', views.reverse_geocode_location, name='reverse_geocode_api'),
    path('download-report/', views.download_report, name='download_report'),
    path('contact-expert/', views.contact_expert, name='contact_expert'),
    path('share-results/', views.share_results, name='share_results'),
    path('api/ai-chatbot/', views.ai_chatbot, name='ai_chatbot'),
    # Marketplace API endpoints
    path('api/add-product/', views.add_product, name='add_product'),
    path('api/place-order/', views.place_order, name='place_order'),
    # Carbon Credit API endpoints
    path('api/submit-farmer-evidence/', views.submit_farmer_evidence, name='submit_farmer_evidence'),
    path('api/purchase-carbon-credits/', views.purchase_carbon_credits, name='purchase_carbon_credits'),
    path('api/get-satellite-data/', views.get_satellite_data, name='get_satellite_data'),
    path('api/verify-farm-practice/', views.verify_farm_practice, name='verify_farm_practice'),
    path('api/get-farm-verification-status/', views.get_farm_verification_status, name='get_farm_verification_status'),
]