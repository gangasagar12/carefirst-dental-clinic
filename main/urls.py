from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),

    # About section
    path('about/', views.about_us, name='about'),
    path('about/clinic/', views.our_clinic, name='clinic'),
    path('about/doctors/', views.doctors, name='doctors'),
    path('about/why-choose-us/', views.why_choose, name='why_choose'),

    # Gallery section
    path('gallery/', views.clinic_gallery, name='clinic_gallery'),
    path('gallery/smile-transformations/', views.smile_transformations, name='smile_transformations'),

    # Services section
    path('services/', views.services_list, name='services_list'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    
    # Pricing
    path('pricing/', views.pricing, name='pricing'),
    
    
    # Contact
    path('contact/', views.contact, name='contact'),
]