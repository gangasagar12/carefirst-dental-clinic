from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_funnel_view, name='book'),
    path('submit/', views.submit_appointment_ajax, name='submit_ajax'),
    path('track-event/', views.track_funnel_event_api, name='track_event'),
    path('confirmation/<str:appointment_number>/', views.appointment_confirmation_view, name='confirmation'),
]
