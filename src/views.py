from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import PaymentProcessor


@api_view(['POST'])
def create_split_payment(request):
    try:
        data = request.data
        
        # Extract order and split rules data
        order_data = {
            'product_id': data['product_id'],
            'amount': 100.00  # You might calculate this based on product
        }
        
        split_rules_data = data['rules']
        
        # Process payment
        processor = PaymentProcessor()
        order = processor.process_payment(order_data, split_rules_data)
        
        return Response({
            'order_id': order.id,
            'status': order.status,
            'message': 'Payment processed successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
