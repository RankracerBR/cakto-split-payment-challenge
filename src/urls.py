from django.urls import path
from .views import create_split_payment


urlpatterns = [
    path('api/v1/splits/', create_split_payment, name='create_split'),
]
