from django.urls import path
from .views import SplitPaymentView


urlpatterns = [
    path('api/v1/splits/', SplitPaymentView.create_split_payment, name='create_split'),
    path('api/v1/splits/all/', SplitPaymentView.list_all, name='list_all_splits'),  # move up
    path('api/v1/splits/<str:product_id>/', SplitPaymentView.get_split_rules, name='get_split_rules'),
]
