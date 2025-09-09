from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import PaymentProcessor
from .models import Order


class SplitPaymentView:
    @api_view(['POST'])
    def create_split_payment(request):
        try:
            data = request.data

            # Order info
            order_data = {
                "product_id": data["product_id"],
                "product_name": data.get("product_name", ""),
                "amount": data.get("amount"),
                "payment_method_id": data.get("payment_method_id"),
                "user_id": data.get("user_id"),  # required for recipient
                "user_account_info": data.get("user_account_info", {})
            }

            processor = PaymentProcessor()
            order = processor.process_payment(order_data)

            return Response({
                "order_id": order.id,
                "status": order.status,
                "message": "Payment processed successfully"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET'])
    def get_split_rules(request, product_id):
        order = Order.objects.filter(product_id__iexact=product_id).first()
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        split_rules = order.split_rules.all()
        
        # Build a list of dicts
        rules_data = [
            {
                "recipient_id": rule.recipient_id,
                "type": rule.type,
                "value": float(rule.value),
                "account_info": rule.account_info
            }
            for rule in split_rules
        ]

        return Response({
            "product_id": order.product_id,
            "split_rules": rules_data
        }, status=status.HTTP_200_OK)


    @api_view(['GET'])
    def list_all(request):
        orders = Order.objects.prefetch_related("split_rules").all()
        data = []
        for order in orders:
            rules_data = [
                {
                    "recipient_id": rule.recipient_id,
                    "type": rule.type,
                    "value": rule.value,
                    "account_info": rule.account_info
                }
                for rule in order.split_rules.all()
            ]
            data.append({
                "order_id": order.id,
                "product_id": order.product_id,
                "product_name": order.product_name,
                "status": order.status,
                "amount": order.amount,
                "created_at": order.created_at,
                "split_rules": rules_data
            })
        return Response(data, status=status.HTTP_200_OK)
