from modeltranslation.translator import register, TranslationOptions
from .models import (
    VideoCategory, VideoPlaylist, Video
)

@register(VideoCategory)
class VideoCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(VideoPlaylist)
class VideoPlaylistTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(Video)
class VideoTranslationOptions(TranslationOptions):
    fields = ('title', 'short_description', 'seo_title', 'seo_description')

