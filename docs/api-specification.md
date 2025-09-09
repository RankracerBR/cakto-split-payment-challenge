## Endpoints Disponíveis:

**POST /api/v1/splits/**
Processa um pagamento com divisão automática

Request:
```json
{
  "product_id": "prod_123",
  "product_name": "Produto Exemplo",
  "amount": 100.00,
  "payment_method_id": "pm_123",
  "user_id": "user_456",
  "user_account_info": {}
}
```

Response:

```json
{
  "order_id": 1,
  "status": "completed",
  "message": "Payment processed successfully"
}
```

**GET /api/v1/splits/{product_id}/**
Consulta as regras de divisão de um pagamento

**GET /api/v1/splits/all/**
Lista todos os pagamentos processados