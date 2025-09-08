from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import SplitPaymentSerializer
from .services import SplitPaymentService
from .models import SplitPaymentModel


class SplitPaymentView(APIView):
    
    @swagger_auto_schema(
        request_body=SplitPaymentSerializer,
        responses={201: SplitPaymentSerializer, 400: "Bad Request"}
    )
    def post(self, request):
        serializer = SplitPaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                service = SplitPaymentService()
                split_payment = service.create_split_payment(
                    product_id=serializer.validated_data['product_id'],
                    rules_data=serializer.validated_data['rules'],
                    effective_date=serializer.validated_data['effective_date'],
                    total_amount=serializer.validated_data['total_amount']
                )
                
                # Process payment asynchronously
                service.process_payment.delay(split_payment.id)
                
                return Response(
                    SplitPaymentSerializer(split_payment).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SplitPaymentStatusView(APIView):
    
    @swagger_auto_schema(
        responses={200: openapi.Response('Payment status', SplitPaymentSerializer)}
    )
    def get(self, request, transaction_id):
        try:
            payment = SplitPaymentModel.objects.get(transaction_id=transaction_id)
            return Response(SplitPaymentSerializer(payment).data)
        except SplitPaymentModel.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
