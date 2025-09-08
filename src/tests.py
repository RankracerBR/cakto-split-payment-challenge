from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from .services import SplitPaymentService

class SplitPaymentTestCase(TestCase):
    
    def test_split_payment_creation(self):
        service = SplitPaymentService()
        
        rules_data = [
            {
                'recipient_id': 'user_creator',
                'rule_type': 'percentage',
                'value': Decimal('65.0'),
                'account_info': {'bank': '001', 'account': '12345-6'}
            },
            {
                'recipient_id': 'user_partner',
                'rule_type': 'percentage', 
                'value': Decimal('30.0'),
                'account_info': {'pix_key': 'partner@email.com'}
            }
        ]
        
        split_payment = service.create_split_payment(
            product_id='prod_abc123',
            rules_data=rules_data,
            effective_date=timezone.now(),
            total_amount=Decimal('100.00')
        )
        
        self.assertEqual(split_payment.rules.count(), 2)
        self.assertEqual(split_payment.status, 'pending')
