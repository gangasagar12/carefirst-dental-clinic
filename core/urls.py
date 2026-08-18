"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from appointments.admin_views import inquiries_dashboard
from main import auth_views as custom_auth_views

from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from main.sitemaps import StaticViewSitemap, ServiceSitemap, BlogSitemap, VideoSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'blogs': BlogSitemap,
    'videos': VideoSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('api/chat/', include('chatbot.urls')),
    path('dashboard/', include('dashboard.urls')),
]

urlpatterns += i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('main.urls')),
    path('appointment/', include('appointments.urls')),
    path('blog/', include('blogs.urls')),
    path('videos/', include('media_center.urls')),
    path('admin/dashboard/', inquiries_dashboard, name='admin_dashboard'),
    path('admin/password_reset/', custom_auth_views.OTPRequestView.as_view(), name='admin_password_reset'),
    path('admin/password_reset/done/', custom_auth_views.OTPVerifyView.as_view(), name='password_reset_done'),
    path('admin/reset/confirm/', custom_auth_views.OTPPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('admin/reset/done/', custom_auth_views.OTPPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/', admin.site.urls),
)

from django.urls import re_path
from django.views.static import serve

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

handler404 = 'main.views.custom_404'
