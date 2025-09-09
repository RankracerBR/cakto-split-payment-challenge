# Cakto Split Payment Challenge

Tópicos:

* 1 - Especificações das documentações

* 2 - Tecnologias usadas

* 3- Overview das perguntas feitas no docx

**-1**
api-specifications[]

architecture-decisions[]

database-design[]

execution-plan[]

**-2**
- Python(Django, Django Rest)
- Docker, Docker-Compose
- Makefile
- Swagger
- Django Prometheus(Lib de terceiros para logs)
- Django Log Hub(Lib de terceiros para logs(interface gráfica))

**-3**

## Microsserviço, módulo monolítico ou arquitetura híbrida?

Arquitetura: Microsserviço

Baseado na análise do código, recomenda-se uma arquitetura de microsserviços pelos seguintes motivos:

Vantagens da Abordagem Microsserviço:

- Especialização: O sistema de split payment tem responsabilidades bem definidas e pode evoluir independentemente
- Escalabilidade Seletiva: O serviço de pagamentos pode ser escalado independentemente durante picos de transações

- Resiliência: Falhas no processamento de pagamentos não afetam outros componentes do sistema

- Deploy Independente: Novas funcionalidades de split podem ser implantadas sem impactar outros serviços


## Como garantir consistência e atomicidade nos splits?

Estratégia Implementada: Transações Distribuídas com Compensação

Abordagem Atual (Django Transactions):

```python
# Uso de transaction.atomic() para consistência no banco
with transaction.atomic():
    order = Order.objects.create(...)
    # operações de negócio
    # criação de split rules
```

Melhorias Recomendadas:

- Padrão SAGA para operações distribuídas:

```python
# Implementar SAGA pattern para coordenação entre:
# - Serviço de Pagamentos (Stripe)
# - Serviço de Split de Valores
# - Serviço de Notificações
```

- Idempotência nas Operações:

```python
# Adicionar idempotency keys nas requisições
def process_payment(self, order_data, idempotency_key):
    # Verificar se operação já foi processada
    # Garantir execução única mesmo em retries
```

- Compensation Actions:

``` python
# Implementar ações de compensação para rollback
def compensate_payment(order_id):
    # Reverter pagamento no Stripe
    # Atualizar status para failed
    # Notificar sistemas dependentes
```

## Event Sourcing Vale a Pena para Auditoria Financeira?

Sim, Altamente Recomendado para Domínio Financeiro

Vantagens do Event Sourcing:

- Auditoria Completa

- Rastreamento de todas as alterações de estado

- Histórico imutável de eventos para compliance financeiro

Implementação Sugerida:

```python
# Modelagem de eventos financeiros
class PaymentEvent(models.Model):
    EVENT_TYPES = [
        ('payment_created', 'Payment Created'),
        ('payment_processed', 'Payment Processed'),
        ('payment_failed', 'Payment Failed'),
        ('split_executed', 'Split Executed'),
    ]
    
    event_id = models.UUIDField(default=uuid.uuid4, unique=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    entity_id = models.CharField(max_length=100)  # order_id
    correlation_id = models.UUIDField()  # para rastreamento
```

Benefícios para Split de Pagamentos:

- Reconstituição do estado a qualquer momento

- Análise de tendências e relatórios financeiros

- Detecção de anomalias e fraudes

- Reconciliação financeira simplificada


## Estratégia de Deploy Sem Downtime?
Blue-Green Deployment com Feature Flags

### Estratégia Recomendada:
#### Infraestrutura como Código:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app_blue:
    build: .
    environment:
      - DEPLOYMENT=blue
    labels:
      - "traefik.http.routers.app-blue.rule=Host(`api.example.com`) && Header(`deployment`, `blue`)"
  
  app_green:
    build: .
    environment:
      - DEPLOYMENT=green
    labels:
      - "traefik.http.routers.app-green.rule=Host(`api.example.com`) && Header(`deployment`, `green`)"
```

### Migrações de Banco Zero-Downtime:

```python
# Técnicas para migrações seguras:
# 1. Migrações backward-compatible
# 2. Dual-writing durante transição
# 3. Feature flags para novas funcionalidades

# Exemplo de feature flag para novos splits:
if feature_flag.is_enabled('new_split_algorithm'):
    self._new_split_implementation(order)
else:
    self._legacy_split_implementation(order)
```

### Health Checks e Readiness Probes:

```python
# Implementar endpoints de health check
@api_view(['GET'])
def health_check(request):
    # Verificar conexão com banco
    # Verificar conexão com Stripe
    # Verificar filas de processamento
    return Response({"status": "healthy"})
```

### Rollback Automático:

```bash
# Script de deploy com rollback automático
#!/bin/bash
# Deploy para blue environment
if ! deploy_to_blue; then
    rollback_deployment
    exit 1
fi

# Wait for health checks
if ! verify_blue_health; then
    rollback_to_green
    exit 1
fi


# Switch traffic to blue
switch_traffic blue
```

## Que métricas de monitoramento são críticas?

Taxa de sucesso de pagamentos (PaymentIntent):

- Quantos pagamentos foram concluídos com sucesso versus quantos falharam.

- No seu código, isso corresponde a verificar se payment_intent.status == "succeeded" e se o signal payment_processed foi disparado.

- Métrica sugerida: % de pagamentos concluídos por período de tempo.

Falhas de pagamento (payment_failed):

- Monitorar os erros retornados pelo Stripe (stripe.error.StripeError) ou erros de validação interna.

- Importante para detectar problemas com cartões, dados inválidos ou falhas de integração.
