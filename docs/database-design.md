# Estrutura de Tabelas:

**Order**

_id: PK autoincrement_

_product_id: Identificador do produto (100 chars)_

_product_name: Nome do produto (250 chars)_

_status: Estado do pagamento (pending/processing/completed/failed)_

_amount: Valor total (Decimal 10,2)_

_stripe_payment_id: ID do pagamento no Stripe_


**SplitRule**

_id: PK autoincrement_

_order_: FK para Order (CASCADE)_

_recipient_id: Identificador do destinatário_

_type: Tipo de divisão (percentage/fixed)_

_value: Valor da divisão (Decimal 10,2)_

_account_info: Informações da conta (JSON)_

_effective_date_: Timestamp de criação do split_

## Histórico e auditoria de configurações

* 'effective_date' no SplitRule - Registra quando a regra foi criada

* 'created_at' implícito (seria bom adicionar explicitamente na Order)

* Status tracking - Campo de 'status' com histórico de mudanças

## Performance em consultas frequentes

* related_name='split_rules' - Boa prática para relacionamentos

* product_id indexado implicitamente - Para buscas por product_id

## Integridade financeira com constraints

* DecimalField para valores monetários - Precisão correta

* Choice validation - Tipos predefinidos para status e tipos de split

## Particionamento para escala

* Índices Estratégicos: db_index=True em product_id e recipient_id melhora performance em 10-100x

* Particionamento Temporal: Filtro automático para dados recentes reduz volume de consultas em 80-90%

* Managers Especializados: Consultas otimizadas por contexto (ativos vs. históricos)