from django.urls import path
from . import views

app_name = 'media_center'

urlpatterns = [
    path('', views.video_list, name='video_list'),
    path('<slug:slug>/', views.video_detail, name='video_detail'),
]
