## Endpoints Disponíveis:

**POST /api/v1/splits/**
Processa um pagamento com divisão automática(Exemplo)

Request:
```json
{
  "product_id": "prod_123",
  "product_name": "Produto Exemplo",
  "amount": 100.50,
  "payment_method_id": "pm_card_visa",
  "user_id": "user_456",
  "user_account_info": {
    "bank": "Nubank",
    "account": "12345-6"
  }
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


## Validações de negócio necessárias
* Validações Atualmente Implementadas:

```python
# No PaymentProcessor._validate_payment()
def _validate_payment(self, order_data):
    if not order_data.get("payment_method_id"):
        raise ValueError("Payment method ID is required")
    if order_data.get("amount", 0) <= 0:
        raise ValueError("Amount must be greater than zero")
```

## Estados possíveis de um split
* Status da Order (Implementados):

```python
class Order(models.Model):
    PENDING = 'pending'      # ✅ Ordem criada, aguardando processamento
    PROCESSING = 'processing' # ✅ Pagamento em processamento no gateway
    COMPLETED = 'completed'  # ✅ Pagamento concluído com sucesso
    FAILED = 'failed'        # ✅ Pagamento falhou - há tratamento de erro
```
* Fluxo de Estados do Sistema:
```text
[POST /splits/] → PENDING → PROCESSING → COMPLETED
                           ↘
                            → FAILED (com rollback)
```

## Como lidar com alterações de configuração
Estratégia para Configuração Dinâmica:

* Modelo para Configurações Flexíveis

```python
# models.py (sugestão)
class SplitConfiguration(models.Model):
    recipient_id = models.CharField(max_length=100)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateTimeField(auto_now_add=True)
    effective_until = models.DateTimeField(null=True, blank=True)
```

* Migração Gradual de Configurações:

```python
# services.py (sugestão)
def get_current_config():
    # Primeiro busca configuração dinâmica, depois default
    try:
        config = SplitConfiguration.objects.filter(
            is_active=True,
            effective_from__lte=timezone.now(),
            effective_until__isnull=True
        ).latest('effective_from')
        return config.recipient_id, config.fee_percentage
    except SplitConfiguration.DoesNotExist:
        return "cakto_fee_account", Decimal('5.00')  # Fallback
```

## Estratégia de versionamento da API

* Versionamento Atual:
```python
# urls.py - Versionamento por URL (Boa prática!)
path('api/v1/splits/', SplitPaymentView.create_split_payment, name='create_split')
```

Estratégia de Evolução da API:
* Versionamento Semântico

```text
/api/v1/splits/    - Versão atual (estável)
/api/v2/splits/    - Próxima versão (em desenvolvimento)
```

Políticas de Compatibilidade:

* v1: Mantém backward compatibility por 12 meses após lançamento da v2

* Endpoints depreciados incluem headers de warning

* Documentação clara das mudanças entre versões

* Exemplo de Evolução:

```python
# v1 - Split fixo (95/5)
# v2 - Split flexível com múltiplos recipients

@api_view(['POST'])
def create_split_payment_v2(request):
    if request.version == 'v1':
        # Comportamento legacy
        return create_split_payment_v1(request)
    elif request.version == 'v2':
        # Novo comportamento com splits customizáveis
        return create_split_payment_v2(request)
```