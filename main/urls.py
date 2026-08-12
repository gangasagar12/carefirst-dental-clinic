from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'), # Changed to 'home' instead of 'index' for better naming
    path('about/', views.about, name='about'),
    path('treatments/', views.treatments, name='treatments'),
    path('treatments/general-dentistry/', views.general_dentistry, name='general_dentistry'),
    path('treatments/dental-filling/', views.dental_filling, name='dental_filling'),
    path('treatments/crowns-bridges/', views.crowns_bridges, name='crowns_bridges'),
    path('doctors/', views.doctors, name='doctors'),
    path('gallery/', views.gallery, name='gallery'),
    path('reviews/', views.reviews, name='reviews'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),
    path('appointment/', views.appointment, name='appointment'),
    path('media/', views.media, name='media'),
    path('pricing/', views.pricing, name='pricing'),
]
