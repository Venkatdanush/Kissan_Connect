from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('services/', views.services, name='services'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('crop-suggestions/', views.crop_suggestions, name='crop_suggestions'),
    path('weather/', views.weather_forecast, name='weather'),
    path('disease-detection/', views.disease_detection, name='disease_detection'),
    path('carbon-tracker/', views.carbon_tracker, name='carbon_tracker'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('news/', views.news, name='news'),
    path('api/crop-recommendation/', views.get_crop_recommendation, name='get_crop_recommendation'),
    path('api/reverse-geocode/', views.reverse_geocode_location, name='reverse_geocode_api'),
    path('download-report/', views.download_report, name='download_report'),
    path('contact-expert/', views.contact_expert, name='contact_expert'),
    path('share-results/', views.share_results, name='share_results'),
]