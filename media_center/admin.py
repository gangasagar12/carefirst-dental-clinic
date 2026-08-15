from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from unfold.admin import ModelAdmin
from .models import VideoCategory, Video

@admin.register(VideoCategory)
class VideoCategoryAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Video)
class VideoAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('title', 'platform', 'category', 'is_featured', 'is_published', 'published_date')
    list_editable = ('is_featured', 'is_published')
    list_filter = ('platform', 'category', 'playlist', 'is_featured', 'is_published')
    search_fields = ('title', 'video_id')
    prepopulated_fields = {'slug': ('title',)}

