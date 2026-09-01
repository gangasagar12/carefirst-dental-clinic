from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Auth
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    
    # Overview
    path('', views.dashboard_home, name='home'),
    
    # Appointments
    path('appointments/', views.appointments_list, name='appointments'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/status/', views.appointment_update_status, name='appointment_update_status'),
    path('appointments/<int:pk>/edit/', views.appointment_edit, name='appointment_edit'),
    
    # Inquiries
    path('inquiries/', views.inquiries_list, name='inquiries'),
    path('inquiries/<int:pk>/toggle-read/', views.inquiry_toggle_read, name='inquiry_toggle_read'),
    path('inquiries/<int:pk>/delete/', views.inquiry_delete, name='inquiry_delete'),
    
    # Services
    path('services/', views.services_list, name='services'),
    path('services/new/', views.service_create, name='service_create'),
    path('services/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:pk>/toggle-active/', views.service_toggle_active, name='service_toggle_active'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    
    # Doctors
    path('doctors/', views.doctors_list, name='doctors'),
    path('doctors/new/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/edit/', views.doctor_edit, name='doctor_edit'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    
    # Pricing
    path('pricing/', views.pricing_list, name='pricing'),
    path('pricing/category/new/', views.pricing_category_create, name='pricing_category_create'),
    path('pricing/category/<int:pk>/edit/', views.pricing_category_edit, name='pricing_category_edit'),
    path('pricing/category/<int:pk>/delete/', views.pricing_category_delete, name='pricing_category_delete'),
    path('pricing/item/new/', views.pricing_item_create, name='pricing_item_create'),
    path('pricing/item/<int:pk>/edit/', views.pricing_item_edit, name='pricing_item_edit'),
    path('pricing/item/<int:pk>/delete/', views.pricing_item_delete, name='pricing_item_delete'),
    
    # Offers
    path('offers/', views.offers_list, name='offers'),
    path('offers/new/', views.offer_create, name='offer_create'),
    path('offers/<int:pk>/edit/', views.offer_edit, name='offer_edit'),
    path('offers/<int:pk>/delete/', views.offer_delete, name='offer_delete'),
    
    # Testimonials
    path('testimonials/', views.testimonials_list, name='testimonials'),
    path('testimonials/new/', views.testimonial_create, name='testimonial_create'),
    path('testimonials/<int:pk>/edit/', views.testimonial_edit, name='testimonial_edit'),
    path('testimonials/<int:pk>/delete/', views.testimonial_delete, name='testimonial_delete'),
    
    # Media
    path('media/', views.media_list, name='media'),
    path('media/new/', views.video_create, name='video_create'),
    path('media/<int:pk>/edit/', views.video_edit, name='video_edit'),
    path('media/<int:pk>/delete/', views.video_delete, name='video_delete'),
    
    # Hero Sliders & Banners
    path('sliders/', views.sliders_list, name='sliders'),
    path('sliders/new/', views.slide_create, name='slide_create'),
    path('sliders/<int:pk>/edit/', views.slide_edit, name='slide_edit'),
    path('sliders/<int:pk>/toggle-active/', views.slide_toggle_active, name='slide_toggle_active'),
    path('sliders/<int:pk>/delete/', views.slide_delete, name='slide_delete'),
    path('gallery/new/', views.gallery_create, name='gallery_create'),
    path('gallery/<int:pk>/delete/', views.gallery_delete, name='gallery_delete'),
    
    # Loyalty & Rewards System (No-Portal)
    path('loyalty/', views.loyalty_reception, name='loyalty_reception'),
    path('loyalty/lookup/', views.loyalty_patient_lookup, name='loyalty_lookup'),
    path('loyalty/apply-reward/', views.loyalty_apply_reward, name='loyalty_apply_reward'),
    path('loyalty/record-visit/', views.loyalty_record_visit, name='loyalty_record_visit'),
    path('loyalty/rewards/', views.loyalty_rewards_list, name='loyalty_rewards'),
    path('loyalty/rewards/<int:pk>/cancel/', views.loyalty_reward_cancel, name='loyalty_reward_cancel'),
    path('loyalty/program/', views.loyalty_program_settings, name='loyalty_program'),
    path('loyalty/transactions/', views.loyalty_transactions_list, name='loyalty_transactions'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
