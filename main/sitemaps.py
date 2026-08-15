from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from main.models import Service
from blogs.models import Post
from media_center.models import Video

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['main:home', 'main:about', 'main:clinic', 'main:doctors', 
                'main:why_choose', 'main:clinic_gallery', 'main:smile_transformations', 
                'main:services_list', 'main:pricing', 'main:contact', 'blogs:blog_list', 'media_center:video_list']

    def location(self, item):
        return reverse(item)

class ServiceSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return Service.objects.all()

    def location(self, item):
        return reverse('main:service_detail', args=[item.slug])

class BlogSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Post.objects.filter(is_published=True)

    def location(self, item):
        return reverse('blogs:post_detail', args=[item.slug])

class VideoSitemap(Sitemap):
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        return Video.objects.filter(is_published=True)

    def location(self, item):
        return reverse('media_center:video_detail', args=[item.slug])
