from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from models import Order
from services import PaymentProcessor


class PaymentProcessorTest(TestCase):
    def test_process_payment_success(self):
        processor = PaymentProcessor()
        order_data = {'product_id': 'prod_abc123', 'payment_method': 'credit_card'}
        split_rules = [
            {'recipient_id': 'user_creator', 'type': 'percentage', 'value': 65.0},
            {'recipient_id': 'user_partner', 'type': 'percentage', 'value': 30.0},
        ]
        
        order = processor.process_payment(order_data, split_rules)
        self.assertEqual(order.status, Order.COMPLETED)
        self.assertEqual(order.split_rules.count(), 2)


class SplitPaymentAPITest(APITestCase):
    def test_create_split_payment(self):
        url = reverse('create_split')
        data = {
            "product_id": "prod_abc123",
            "rules": [
                {
                    "recipient_id": "user_creator",
                    "type": "percentage", 
                    "value": 65.0,
                    "account_info": {"bank": "001", "account": "12345-6"}
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
