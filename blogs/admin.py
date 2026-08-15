from django.contrib import admin
from unfold.admin import ModelAdmin
from modeltranslation.admin import TranslationAdmin
from .models import Category, Post

@admin.register(Category)
class CategoryAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(ModelAdmin, TranslationAdmin):
    list_display = ('title', 'category', 'author', 'published_date', 'is_featured', 'is_popular', 'is_published')
    list_filter = ('category', 'is_featured', 'is_popular', 'is_published')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
