import json
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.core.cache import cache
from django.conf import settings

from chatbot.models import Conversation, ChatMessage, ChatbotFeedback, ChatInteraction
from chatbot.services.chat_service import ChatService
from chatbot.tools.appointment_tools import validate_and_create_appointment
from chatbot.tools.pricing_tools import calculate_cost_estimate

def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

def check_rate_limit(request, session_id: str) -> bool:
    """
    Per-IP and Per-Session rate limiting.
    Allows up to CHATBOT_RATE_LIMIT_PER_MINUTE requests per 60 seconds.
    """
    limit = getattr(settings, 'CHATBOT_RATE_LIMIT_PER_MINUTE', 20)
    ip = get_client_ip(request)
    cache_key = f"chatbot_ratelimit_{ip}_{session_id}"
    
    current_requests = cache.get(cache_key, 0)
    if current_requests >= limit:
        return False
    
    cache.set(cache_key, current_requests + 1, timeout=60)
    return True


@require_POST
def send_message_api(request):
    """
    Primary chat endpoint: POST /api/chat/message/
    Receives user message, session ID, page context, UTM params.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload'}, status=400)

    message = data.get('message', '').strip()
    session_id = data.get('session_id', '').strip()
    current_page = data.get('current_page', '/')
    current_treatment = data.get('current_treatment', '')
    utm_params = data.get('utm_params', {})

    if not message:
        return JsonResponse({'success': False, 'error': 'Message cannot be empty.'}, status=400)

    if len(message) > 2000:
        return JsonResponse({'success': False, 'error': 'Message exceeds maximum length of 2,000 characters.'}, status=400)

    if not session_id:
        # Fallback to Django session key
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key

    # Check Rate Limit
    if not check_rate_limit(request, session_id):
        return JsonResponse({
            'success': False,
            'error': 'You have sent several messages recently. Please wait a moment before sending another message.'
        }, status=429)

    response_payload = ChatService.process_message(
        session_id=session_id,
        message=message,
        current_page=current_page,
        current_treatment=current_treatment,
        user=request.user,
        utm_params=utm_params
    )

    return JsonResponse({'success': True, 'data': response_payload})


@require_GET
def get_history_api(request):
    """
    Retrieves conversation history: GET /api/chat/history/?session_id=...
    """
    session_id = request.GET.get('session_id', '').strip()
    if not session_id and request.session.session_key:
        session_id = request.session.session_key

    if not session_id:
        return JsonResponse({'success': True, 'messages': []})

    conversation = Conversation.objects.filter(session_id=session_id, status='active').first()
    if not conversation:
        return JsonResponse({'success': True, 'messages': []})

    messages = conversation.messages.order_by('created_at')[:30]
    data = [
        {
            'id': m.id,
            'role': m.role,
            'content': m.content,
            'intent': m.intent,
            'quick_actions': m.quick_actions,
            'cards': m.cards,
            'created_at': m.created_at.strftime('%I:%M %p')
        }
        for m in messages
    ]

    return JsonResponse({'success': True, 'messages': data})


@require_POST
def submit_appointment_api(request):
    """
    Creates an appointment directly through the chat widget: POST /api/chat/appointment/
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload'}, status=400)

    result = validate_and_create_appointment(data)
    
    # Log interaction
    session_id = data.get('session_id')
    if session_id:
        conv = Conversation.objects.filter(session_id=session_id).first()
        if conv:
            ChatInteraction.objects.create(
                conversation=conv,
                intent='APPOINTMENT',
                treatment=data.get('treatment', ''),
                action='appointment_completed' if result.get('success') else 'appointment_started',
                extra_data=result
            )

    return JsonResponse(result, status=200 if result.get('success') else 400)


@require_POST
def submit_feedback_api(request):
    """
    Records helpfulness feedback: POST /api/chat/feedback/
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload'}, status=400)

    session_id = data.get('session_id')
    message_id = data.get('message_id')
    rating = data.get('rating', 'positive')
    comment = data.get('comment', '').strip()

    if not session_id:
        return JsonResponse({'success': False, 'error': 'Session ID required.'}, status=400)

    conversation = Conversation.objects.filter(session_id=session_id).first()
    if not conversation:
        return JsonResponse({'success': False, 'error': 'Conversation not found.'}, status=404)

    msg = None
    if message_id:
        msg = ChatMessage.objects.filter(id=message_id, conversation=conversation).first()

    ChatbotFeedback.objects.create(
        conversation=conversation,
        message=msg,
        rating=rating,
        comment=comment
    )

    return JsonResponse({'success': True, 'message': 'Thank you for your feedback!'})


@require_POST
def estimate_cost_api(request):
    """
    Calculates cost estimate: POST /api/chat/estimate/
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload'}, status=400)

    treatment = data.get('treatment', '')
    option = data.get('option', '')
    quantity = data.get('quantity', 1)

    estimate = calculate_cost_estimate(treatment, option, quantity)
    return JsonResponse({'success': True, 'estimate': estimate})


@require_POST
def track_interaction_api(request):
    """
    Tracks marketing interactions (e.g. WhatsApp button clicks): POST /api/chat/track/
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False}, status=400)

    session_id = data.get('session_id')
    action = data.get('action')
    treatment = data.get('treatment', '')

    if session_id and action:
        conv = Conversation.objects.filter(session_id=session_id).first()
        if conv:
            ChatInteraction.objects.create(
                conversation=conv,
                intent='MARKETING_ACTION',
                treatment=treatment,
                action=action
            )

    return JsonResponse({'success': True})
