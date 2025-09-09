from django.db import transaction
from .models import Order, SplitRule
from .events import payment_processed, payment_failed, payout_triggered


class PaymentProcessor:
    def process_payment(self, order_data, split_rules_data):
        try:
            with transaction.atomic():
                # 1. Create order
                order = Order.objects.create(
                    product_id=order_data['product_id'],
                    amount=order_data.get('amount', 100.00)  # Default amount
                )
                
                # 2. Create split rules
                split_rules = []
                for rule_data in split_rules_data:
                    rule = SplitRule.objects.create(
                        order=order,
                        recipient_id=rule_data['recipient_id'],
                        type=rule_data['type'],
                        value=rule_data['value'],
                        account_info=rule_data.get('account_info', {})
                    )
                    split_rules.append(rule)
                
                # 3. Validate payment method (simplified)
                self._validate_payment(order_data)
                
                # 4. Charge via gateway (simulated)
                self._charge_payment(order)
                
                # 5. Update order status
                order.status = Order.COMPLETED
                order.save()
                
                # 6. Send events
                payment_processed.send(sender=self.__class__, order=order)
                payout_triggered.send(sender=self.__class__, order=order, split_rules=split_rules)
                
                return order
                
        except Exception as e:
            payment_failed.send(sender=self.__class__, order=order, error=str(e))
            raise

    def _validate_payment(self, order_data):
        """Simulate payment validation"""
        if not order_data.get('payment_method'):
            raise ValueError("Payment method required")

    def _charge_payment(self, order):
        """Simulate payment gateway charge"""
        print(f"Charging ${order.amount} for order {order.id}")
        # Simulate API call to Mercado Pago/Pagarme
        return True
