import json
from django.test import TestCase, Client
from django.urls import reverse
from chatbot.models import Conversation, ChatMessage
from main.models import Service

class ChatAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.service = Service.objects.create(
            title="Dental Implants",
            slug="dental-implants",
            starting_price="65,000"
        )

    def test_send_opening_hours_fast_path(self):
        payload = {
            'session_id': 'test-session-123',
            'message': 'What are your opening hours?',
            'current_page': '/'
        }
        response = self.client.post(
            reverse('chatbot:send_message'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn("7:30 AM to 7:30 PM", data['data']['content'])

    def test_send_location_fast_path(self):
        payload = {
            'session_id': 'test-session-123',
            'message': 'Where is the clinic located in Kathmandu?',
            'current_page': '/'
        }
        response = self.client.post(
            reverse('chatbot:send_message'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn("Shankhamul", data['data']['content'])

    def test_page_context_pronoun_resolution(self):
        payload = {
            'session_id': 'test-session-page',
            'message': 'How much does it cost?',
            'current_page': '/services/dental-implants/',
            'current_treatment': 'dental-implants'
        }
        response = self.client.post(
            reverse('chatbot:send_message'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        conv = Conversation.objects.get(session_id='test-session-page')
        self.assertEqual(conv.current_treatment, 'dental-implants')

    def test_get_history_endpoint(self):
        conv = Conversation.objects.create(session_id='hist-session-456')
        ChatMessage.objects.create(conversation=conv, role='user', content='Hello')
        ChatMessage.objects.create(conversation=conv, role='assistant', content='Namaste! How can I help?')

        response = self.client.get(f"{reverse('chatbot:get_history')}?session_id=hist-session-456")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['messages']), 2)
