from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('message/', views.send_message_api, name='send_message'),
    path('history/', views.get_history_api, name='get_history'),
    path('appointment/', views.submit_appointment_api, name='submit_appointment'),
    path('feedback/', views.submit_feedback_api, name='submit_feedback'),
    path('estimate/', views.estimate_cost_api, name='estimate_cost'),
    path('track/', views.track_interaction_api, name='track_interaction'),
]
