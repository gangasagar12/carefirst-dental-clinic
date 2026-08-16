from django.test import TestCase
from main.models import PricingCategory, PricingItem, Service
from chatbot.tools.pricing_tools import get_treatment_price, calculate_cost_estimate

class PricingToolsTest(TestCase):
    def setUp(self):
        self.cat = PricingCategory.objects.create(name="Dental Filling", order=1)
        self.item1 = PricingItem.objects.create(category=self.cat, name="Composite Filling - Small", price="1,500", order=1)
        self.item2 = PricingItem.objects.create(category=self.cat, name="Composite Filling - Large", price="2,500", order=2)
        self.service = Service.objects.create(title="Dental Filling", slug="dental-filling", starting_price="1,500")

    def test_get_treatment_price_from_database(self):
        data = get_treatment_price("dental-filling")
        self.assertTrue(data['found'])
        self.assertIn("1,500", data['starting_price'])
        self.assertEqual(len(data['items']), 2)

    def test_calculate_cost_estimate_single_tooth(self):
        estimate = calculate_cost_estimate("Dental Filling", option_name="Small", quantity=1)
        self.assertIn("NPR 1,500", estimate['total_estimate'])

    def test_calculate_cost_estimate_multiple_teeth(self):
        estimate = calculate_cost_estimate("Dental Filling", option_name="Small", quantity=3)
        self.assertIn("NPR 4,500", estimate['total_estimate'])
