from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_funnel_view, name='book'),
    path('submit/', views.submit_appointment_ajax, name='submit_ajax'),
    path('track-event/', views.track_funnel_event_api, name='track_event'),
    
    # Confirmation & Management Routes (Secured by token / unique ID)
    path('confirmation/<str:access_token>/', views.appointment_confirmation_view, name='confirmation'),
    path('manage/<str:access_token>/', views.appointment_manage_view, name='manage'),
    path('manage/<str:access_token>/pdf/', views.appointment_download_pdf_view, name='download_pdf'),
    path('manage/<str:access_token>/calendar.ics', views.appointment_calendar_ics_view, name='calendar_ics'),
    path('manage/<str:access_token>/reschedule/', views.appointment_request_reschedule_view, name='request_reschedule'),
    path('manage/<str:access_token>/cancel/', views.appointment_request_cancel_view, name='request_cancel'),
]
