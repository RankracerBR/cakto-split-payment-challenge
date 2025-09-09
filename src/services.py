import stripe
from django.conf import settings
from django.db import transaction
from .models import Order, SplitRule
from .events import payment_processed, payment_failed, payout_triggered

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentProcessor:
    CAKTO_RECIPIENT_ID = "cakto_fee_account"
    CAKTO_FEE_PERCENTAGE = 5  # 5%

    def process_payment(self, order_data):
        order = None
        try:
            with transaction.atomic():
                # 1. Create order
                order = Order.objects.create(
                    product_id=order_data["product_id"],
                    product_name=order_data.get("product_name", ""),
                    amount=order_data.get("amount", 100.00)
                )

                # 2. Validate payment method
                self._validate_payment(order_data)

                # 3. Charge via Stripe
                payment_intent = self._charge_via_stripe(order, order_data)

                # 4. Auto split rules: user + Cakto fee
                user_percentage = 100 - self.CAKTO_FEE_PERCENTAGE
                split_rules = [
                    SplitRule.objects.create(
                        order=order,
                        recipient_id=order_data.get("user_id", "unknown_user"),
                        type=SplitRule.PERCENTAGE,
                        value=user_percentage,
                        account_info=order_data.get("user_account_info", {})
                    ),
                    SplitRule.objects.create(
                        order=order,
                        recipient_id=self.CAKTO_RECIPIENT_ID,
                        type=SplitRule.PERCENTAGE,
                        value=self.CAKTO_FEE_PERCENTAGE,
                        account_info={"platform": "cakto"}
                    )
                ]

                # 5. Update order
                order.status = Order.COMPLETED
                order.stripe_payment_id = payment_intent.id
                order.save()

                # 6. Trigger events
                payment_processed.send(sender=self.__class__, order=order)
                payout_triggered.send(sender=self.__class__, order=order, split_rules=split_rules)

                return order

        except stripe.error.StripeError as e:
            self._handle_error(order, f"Stripe error: {str(e)}")
        except Exception as e:
            self._handle_error(order, str(e))

    def _validate_payment(self, order_data):
        if not order_data.get("payment_method_id"):
            raise ValueError("Payment method ID is required")
        if order_data.get("amount", 0) <= 0:
            raise ValueError("Amount must be greater than zero")

    def _charge_via_stripe(self, order, order_data):
        amount_cents = int(float(order.amount) * 100)
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="brl",
            payment_method=order_data["payment_method_id"],
            confirm=True,
            description=f"Payment for order #{order.id}",
            metadata={"order_id": order.id, "product_id": order.product_id},
            payment_method_types=["card"],
            setup_future_usage="off_session" if order_data.get("save_payment_method") else None,
        )
        if payment_intent.status != "succeeded":
            raise Exception(f"Payment failed with status: {payment_intent.status}")
        return payment_intent

    def _handle_error(self, order, error_message):
        if order and order.pk:
            order.status = Order.FAILED
            order.save()
            payment_failed.send(sender=self.__class__, order=order, error=error_message)
        else:
            payment_failed.send(sender=self.__class__, order=None, error=error_message)
        raise Exception(error_message)
