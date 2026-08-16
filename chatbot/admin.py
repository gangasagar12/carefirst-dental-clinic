from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from unfold.admin import ModelAdmin, TabularInline

from .models import Conversation, ChatMessage, ChatInteraction, ChatbotFeedback, UnansweredQuestion

class ChatMessageInline(TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['role', 'content', 'intent', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Conversation)
class ConversationAdmin(ModelAdmin):
    list_display = ['id_short', 'session_id', 'current_treatment', 'status', 'message_count', 'utm_source', 'created_at']
    list_filter = ['status', 'created_at', 'utm_source']
    search_fields = ['session_id', 'current_treatment', 'current_page']
    readonly_fields = ['id', 'session_id', 'user', 'created_at', 'updated_at']
    inlines = [ChatMessageInline]

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = "Chat ID"

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"


@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    list_display = ['id', 'conversation_link', 'role', 'content_preview', 'intent', 'created_at']
    list_filter = ['role', 'intent', 'created_at']
    search_fields = ['content', 'intent']
    readonly_fields = ['conversation', 'role', 'content', 'intent', 'quick_actions', 'cards', 'metadata', 'created_at']

    def conversation_link(self, obj):
        url = reverse('admin:chatbot_conversation_change', args=[obj.conversation.id])
        return format_html('<a href="{}">Chat {}</a>', url, str(obj.conversation.id)[:8])
    conversation_link.short_description = "Conversation"

    def content_preview(self, obj):
        return obj.content[:80] + "..." if len(obj.content) > 80 else obj.content
    content_preview.short_description = "Message"


@admin.register(ChatInteraction)
class ChatInteractionAdmin(ModelAdmin):
    list_display = ['action', 'treatment', 'intent', 'conversation', 'created_at']
    list_filter = ['action', 'treatment', 'created_at']
    search_fields = ['treatment', 'intent']
    readonly_fields = ['conversation', 'intent', 'treatment', 'action', 'extra_data', 'created_at']


@admin.register(ChatbotFeedback)
class ChatbotFeedbackAdmin(ModelAdmin):
    list_display = ['conversation_link', 'rating_badge', 'comment', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['comment']
    readonly_fields = ['conversation', 'message', 'rating', 'comment', 'created_at']

    def conversation_link(self, obj):
        url = reverse('admin:chatbot_conversation_change', args=[obj.conversation.id])
        return format_html('<a href="{}">Chat {}</a>', url, str(obj.conversation.id)[:8])
    conversation_link.short_description = "Conversation"

    def rating_badge(self, obj):
        if obj.rating == 'positive':
            return format_html('<span style="color:#10B981; font-weight:bold;">👍 Helpful</span>')
        return format_html('<span style="color:#EF4444; font-weight:bold;">👎 Not Helpful</span>')
    rating_badge.short_description = "Rating"


@admin.register(UnansweredQuestion)
class UnansweredQuestionAdmin(ModelAdmin):
    list_display = ['question', 'category', 'frequency', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['question', 'notes']
    list_editable = ['status']
