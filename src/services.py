import stripe

from django.conf import settings
from django.db import transaction

from .models import Order, SplitRule
from .events import payment_processed, payment_failed, payout_triggered

stripe.api_key = settings.STRIPE_SECRET_KEY


# services.py
class PaymentProcessor:
    CAKTO_RECIPIENT_ID = "cakto_fee_account"
    CAKTO_FEE_PERCENTAGE = 5  # 5%

    def process_payment(self, order_data):
        order = None
        try:
            # Validação primeiro
            self._validate_payment(order_data)
            
            # Se validação passar, processa o pagamento
            with transaction.atomic():
                order = Order.objects.create(
                    product_id=order_data["product_id"],
                    product_name=order_data.get("product_name", ""),
                    amount=order_data.get("amount", 100.00)
                )

                payment_intent = self._charge_via_stripe(order, order_data)

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

                order.status = Order.COMPLETED
                order.stripe_payment_id = payment_intent.id
                order.save()

                payment_processed.send(sender=self.__class__, order=order)
                payout_triggered.send(sender=self.__class__, order=order, split_rules=split_rules)

                return order

        except Exception as e:
            if order and order.pk:
                order.status = Order.FAILED
                order.save()
                payment_failed.send(sender=self.__class__, order=order, error=str(e))
            else:
                payment_failed.send(sender=self.__class__, order=None, error=str(e))

            raise

    def _validate_payment(self, order_data):
        """Validação rigorosa antes de qualquer operação de banco"""
        if not order_data.get("payment_method_id"):
            raise ValueError("Payment method ID is required")
        
        amount = order_data.get("amount")
        if amount is None:
            raise ValueError("Amount is required")
        
        product_name = order_data.get("product_name")
        if product_name is None:
            raise ValueError("Product name is required")
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError("Amount must be greater than zero")
        except (ValueError, TypeError):
            raise ValueError("Amount must be greater than zero")
        
        # Validar outros campos obrigatórios
        if not order_data.get("product_id"):
            raise ValueError("Product ID is required")
        
        if not order_data.get("user_id"):
            raise ValueError("User ID is required")

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

    def _handle_error(self, order, error_message, original_exception=None):
        if order and order.pk:
            order.status = Order.FAILED
            order.save()
            payment_failed.send(sender=self.__class__, order=order, error=error_message)
        else:
            payment_failed.send(sender=self.__class__, order=None, error=error_message)

        if original_exception and isinstance(original_exception, ValueError):
            raise ValueError(error_message) from original_exception
        else:
            raise Exception(error_message) from original_exception
