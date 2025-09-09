## Estrutura de Tabelas:

**Order**

_id: PK autoincrement_

_product_id: Identificador do produto (100 chars)_

_product_name: Nome do produto (250 chars)_

_status: Estado do pagamento (pending/processing/completed/failed)_

_amount: Valor total (Decimal 10,2)_

_stripe_payment_id: ID do pagamento no Stripe_

_created_at: Timestamp de criação_


**SplitRule**

_id: PK autoincrement_

_order_id: FK para Order (CASCADE)_

_recipient_id: Identificador do destinatário_

_type: Tipo de divisão (percentage/fixed)_

_value: Valor da divisão (Decimal 10,2)_

_account_info: Informações da conta (JSON)_