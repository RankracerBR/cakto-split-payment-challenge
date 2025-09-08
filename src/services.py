from decimal import Decimal
from django.db import transaction
from .models import SplitPaymentModel, SplitRuleModel, PaymentLog
import logging

logger = logging.getLogger(__name__)

class SplitPaymentService:
    @transaction.atomic
    def create_split_payment(self, product_id, rules_data, effective_date, total_amount):
        try:
            # Create split payment
            split_payment = SplitPaymentModel.objects.create(
                product_id=product_id,
                total_amount=total_amount,
                effective_date=effective_date,
                status='pending'
            )
            
            # Create split rules
            for rule_data in rules_data:
                rule = SplitRuleModel.objects.create(**rule_data)
                split_payment.rules.add(rule)
            
            # Log creation
            PaymentLog.objects.create(
                split_payment=split_payment,
                event_type='created',
                details={'rules_count': len(rules_data)}
            )
            
            return split_payment
            
        except Exception as e:
            logger.error(f"Error creating split payment: {str(e)}")
            raise
    
    def process_payment(self, split_payment_id):
        try:
            split_payment = SplitPaymentModel.objects.get(id=split_payment_id)
            split_payment.status = 'processing'
            split_payment.save()
            
            # Calculate amounts for each recipient
            distributions = self._calculate_distributions(split_payment)
            
            # Process each distribution (integration with payment gateway)
            for distribution in distributions:
                self._process_individual_payment(distribution)
            
            split_payment.status = 'completed'
            split_payment.save()
            
            PaymentLog.objects.create(
                split_payment=split_payment,
                event_type='completed',
                details={'distributions': distributions}
            )
            
        except Exception as e:
            logger.error(f"Error processing payment {split_payment_id}: {str(e)}")
            split_payment.status = 'failed'
            split_payment.save()
            
            PaymentLog.objects.create(
                split_payment=split_payment,
                event_type='failed',
                details={'error': str(e)}
            )
            raise
    
    def _calculate_distributions(self, split_payment):
        distributions = []
        total_amount = split_payment.total_amount
        
        for rule in split_payment.rules.all():
            if rule.rule_type == 'percentage':
                amount = total_amount * (rule.value / Decimal('100'))
            else:  # fixed amount
                amount = rule.value
            
            distributions.append({
                'recipient_id': rule.recipient_id,
                'amount': amount.quantize(Decimal('0.01')),
                'account_info': rule.account_info
            })
        
        return distributions
    
    def _process_individual_payment(self, distribution):
        # Integrate with payment gateway (Mercado Pago/Pagarme)
        # This would be the actual implementation
        pass
