from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Order
from .services import PaymentProcessor


class PaymentProcessorTest(TestCase):
    def test_process_payment_success(self):
        processor = PaymentProcessor()
        order_data = {
            'product_id': 'prod_abc123',
            'payment_method_id': 'pm_card_visa',
            'amount': 100.0,
            'user_id': 'user_creator',
            'user_account_info': {'bank': '001', 'account': '12345-6'}
        }
        
        order = processor.process_payment(order_data)
        
        self.assertEqual(order.status, Order.COMPLETED)
        # There should be 2 split rules: user + Cakto fee
        self.assertEqual(order.split_rules.count(), 2)
        split_recipients = {r.recipient_id for r in order.split_rules.all()}
        self.assertIn('user_creator', split_recipients)
        self.assertIn(PaymentProcessor.CAKTO_RECIPIENT_ID, split_recipients)


class SplitPaymentAPITest(APITestCase):
    def test_create_split_payment(self):
        url = reverse('create_split')
        data = {
            "product_id": "prod_abc123",
            "amount": 150.0,
            "payment_method_id": "pm_card_visa",
            "user_id": "user_creator",
            "user_account_info": {"bank": "001", "account": "12345-6"}
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("order_id", response.data)
        self.assertIn("status", response.data)
        self.assertEqual(response.data["status"], Order.COMPLETED)
