from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from decimal import Decimal

from .models import Order, SplitRule
from .services import PaymentProcessor


class PaymentProcessorTest(TestCase):
    def setUp(self):
        self.processor = PaymentProcessor()
        self.valid_order_data = {
            'product_id': 'prod_abc123',
            'product_name': 'Test Product',
            'payment_method_id': 'pm_card_visa',
            'amount': 100.0,
            'user_id': 'user_creator',
            'user_account_info': {'bank': '001', 'account': '12345-6'}
        }

    def test_process_payment_success(self):
        order = self.processor.process_payment(self.valid_order_data)
        
        self.assertEqual(order.status, Order.COMPLETED)
        self.assertEqual(order.split_rules.count(), 2)
        split_recipients = {r.recipient_id for r in order.split_rules.all()}
        self.assertIn('user_creator', split_recipients)
        self.assertIn(PaymentProcessor.CAKTO_RECIPIENT_ID, split_recipients)

    def test_process_payment_missing_payment_method(self):
        invalid_data = self.valid_order_data.copy()
        invalid_data.pop('payment_method_id')

        with self.assertRaises(ValueError) as context:
            self.processor.process_payment(invalid_data)
        
        self.assertIn("Payment method ID is required", str(context.exception))

    def test_process_payment_invalid_amount_zero(self):
        invalid_data = self.valid_order_data.copy()
        invalid_data['amount'] = 0
        
        with self.assertRaises(ValueError) as context:
            self.processor.process_payment(invalid_data)
        
        self.assertIn("Amount must be greater than zero", str(context.exception))

    def test_process_payment_negative_amount(self):
        invalid_data = self.valid_order_data.copy()
        invalid_data['amount'] = -10
        
        with self.assertRaises(ValueError) as context:
            self.processor.process_payment(invalid_data)
        
        self.assertIn("Amount must be greater than zero", str(context.exception))
    
    @patch('stripe.PaymentIntent.create')
    def test_process_payment_stripe_error(self, mock_stripe_create):
        mock_stripe_create.side_effect = Exception("Stripe API error")
        
        with self.assertRaises(Exception) as context:
            self.processor.process_payment(self.valid_order_data)

        self.assertIn("Stripe API error", str(context.exception))

        order = Order.objects.filter(product_id='prod_abc123').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, Order.FAILED)

    @patch('stripe.PaymentIntent.create')
    def test_process_payment_stripe_failed_status(self, mock_stripe_create):
        mock_intent = MagicMock()
        mock_intent.status = "failed"
        mock_intent.id = "pi_failed_123"
        mock_stripe_create.return_value = mock_intent
        
        with self.assertRaises(Exception) as context:
            self.processor.process_payment(self.valid_order_data)
        
        self.assertIn("Payment failed with status: failed", str(context.exception))
        order = Order.objects.filter(product_id='prod_abc123').first()
        self.assertEqual(order.status, Order.FAILED)

    def test_process_payment_empty_product_id(self):
        invalid_data = self.valid_order_data.copy()
        invalid_data['product_id'] = ''
        
        with self.assertRaises(Exception):
            self.processor.process_payment(invalid_data)

    def test_process_payment_none_amount(self):
        invalid_data = self.valid_order_data.copy()
        invalid_data['amount'] = None

        with self.assertRaises(ValueError) as context:
            self.processor.process_payment(invalid_data)
        
        self.assertIn("Amount is required", str(context.exception))

    def test_validate_payment_method(self):
        with self.assertRaises(ValueError) as context:
            self.processor._validate_payment({})
        self.assertIn("Payment method ID is required", str(context.exception))

    def test_validate_amount(self):
        processor = PaymentProcessor()
        
        test_data = {
            'payment_method_id': 'pm_123', 
            'amount': 0,
            'product_id': 'test',
            'user_id': 'user123',
            'product_name': 'Test Product'
        }
        
        with self.assertRaises(ValueError) as context:
            processor._validate_payment(test_data)
        
        self.assertIn("Amount must be greater than zero", str(context.exception))


class SplitPaymentAPITest(APITestCase):
    def setUp(self):
        self.url = reverse('create_split')
        self.valid_data = {
            "product_id": "prod_abc123",
            "product_name": "Test Product",
            "amount": 150.0,
            "payment_method_id": "pm_card_visa",
            "user_id": "user_creator",
            "user_account_info": {"bank": "001", "account": "12345-6"}
        }

    def test_create_split_payment_success(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("order_id", response.data)
        self.assertIn("status", response.data)
        self.assertEqual(response.data["status"], Order.COMPLETED)

    def test_create_split_payment_missing_required_fields(self):
        invalid_data = self.valid_data.copy()
        invalid_data.pop('product_id')
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_split_payment_empty_string_fields(self):
        invalid_data = self.valid_data.copy()
        invalid_data['product_id'] = ''
        invalid_data['user_id'] = ''
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_split_payment_invalid_amount(self):
        invalid_data = self.valid_data.copy()
        invalid_data['amount'] = 0
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_split_payment_negative_amount(self):
        invalid_data = self.valid_data.copy()
        invalid_data['amount'] = -50
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_split_payment_missing_payment_method(self):
        invalid_data = self.valid_data.copy()
        invalid_data.pop('payment_method_id')
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_get_split_rules_nonexistent_product(self):
        url = reverse('get_split_rules', kwargs={'product_id': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_get_split_rules_existing_product(self):
        self.client.post(self.url, self.valid_data, format='json')
        
        url = reverse('get_split_rules', kwargs={'product_id': 'prod_abc123'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("split_rules", response.data)
        self.assertEqual(len(response.data["split_rules"]), 2)

    def test_list_all_payments_empty(self):
        url = reverse('list_all_splits')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_list_all_payments_with_data(self):
        self.client.post(self.url, self.valid_data, format='json')
        
        url = reverse('list_all_splits')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

    def test_invalid_json_format(self):
        response = self.client.post(self.url, "invalid json", content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unexpected_exception_handling(self):
        with patch('src.services.PaymentProcessor.process_payment') as mock_process:
            mock_process.side_effect = Exception("Unexpected error")
            
            response = self.client.post(self.url, self.valid_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)


class SplitRuleModelTest(TestCase):
    def test_split_rule_creation(self):
        order = Order.objects.create(
            product_id="test_prod",
            product_name="Test Product",
            amount=Decimal('100.00'),
            status=Order.COMPLETED
        )
        
        split_rule = SplitRule.objects.create(
            order=order,
            recipient_id="recipient_123",
            type=SplitRule.PERCENTAGE,
            value=Decimal('80.00'),
            account_info={"bank": "001"}
        )
        
        self.assertEqual(split_rule.order, order)
        self.assertEqual(split_rule.recipient_id, "recipient_123")
        self.assertEqual(split_rule.type, SplitRule.PERCENTAGE)
        self.assertEqual(split_rule.value, Decimal('80.00'))


class OrderModelTest(TestCase):
    def test_order_creation(self):
        order = Order.objects.create(
            product_id="test_product",
            product_name="Test Product",
            amount=Decimal('99.99'),
            status=Order.PENDING
        )
        
        self.assertEqual(order.product_id, "test_product")
        self.assertEqual(order.status, Order.PENDING)
        self.assertIsNone(order.stripe_payment_id)

    def test_order_status_choices(self):
        order = Order.objects.create(
            product_id="test_product",
            product_name="Test Product",
            amount=Decimal('100.00'),
            status=Order.PROCESSING
        )
        
        # Teste de transição de status
        order.status = Order.COMPLETED
        order.save()
        
        self.assertEqual(order.status, Order.COMPLETED)

