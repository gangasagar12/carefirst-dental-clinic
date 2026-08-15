from django.shortcuts import render, get_object_or_404
from .models import Video

def video_list(request):
    videos = Video.objects.filter(is_published=True)
    from .models import VideoCategory
    categories = VideoCategory.objects.all()
    return render(request, 'media_center/video_list.html', {'videos': videos, 'categories': categories})

def video_detail(request, slug):
    video = get_object_or_404(Video, slug=slug, is_published=True)
    
    # Generate structured data
    video_schema = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": video.seo_title or video.title,
        "description": video.seo_description or video.short_description,
        "thumbnailUrl": [video.thumbnail],
        "uploadDate": video.published_date.isoformat(),
        "contentUrl": video.video_url,
        "embedUrl": video.get_embed_url()
    }
    
    related_videos = Video.objects.filter(category=video.category).exclude(id=video.id)[:3]
    
    context = {
        'video': video,
        'video_schema': video_schema,
        'related_videos': related_videos,
    }
    return render(request, 'media_center/video_detail.html', context)
