from .models import Order
from django.dispatch import Signal, receiver


# Define signals
payment_processed = Signal()
payment_failed = Signal()
payout_triggered = Signal()

# Event handlers
@receiver(payment_processed)
def handle_payment_processed(sender, order, **kwargs):
    """Handle successful payment"""
    print(f"Payment processed for order {order.id}")
    # Update order status, send confirmation, etc.

@receiver(payment_failed)
def handle_payment_failed(sender, order, error, **kwargs):
    """Handle failed payment"""
    print(f"Payment failed for order {order.id}: {error}")
    order.status = Order.FAILED
    order.save()

@receiver(payout_triggered)
def handle_payout(sender, order, split_rules, **kwargs):
    """Handle payout to recipients"""
    print(f"Triggering payout for order {order.id}")
    for rule in split_rules:
        print(f"Paying {rule.value}% to {rule.recipient_id}")
