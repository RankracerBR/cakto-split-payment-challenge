from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import SplitPaymentView


schema_view = get_schema_view(
    openapi.Info(
        title="Split Payments API",
        default_version="v1",
        description="API para gerenciar Split Payments",
        contact=openapi.Contact(email="suporte@exemplo.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/v1/splits/', SplitPaymentView.create_split_payment, name='create_split'),
    path('api/v1/splits/all/', SplitPaymentView.list_all, name='list_all_splits'),
    path('api/v1/splits/<str:product_id>/', SplitPaymentView.get_split_rules, name='get_split_rules'),

    # Rotas Swagger
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
