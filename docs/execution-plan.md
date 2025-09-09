## Fluxo de Processamento:
Criação do Pedido: Validação dos dados e criação do registro Order

Validação do Pagamento: Verificação do método de pagamento e valor

Cobrança Stripe: Processamento da transação via Stripe API

Divisão Automática: Criação das regras de split (95% user + 5% plataforma)

Atualização de Status: Marcação do pedido como completed

Disparo de Eventos: Notificação de sucesso e trigger para payouts

Tratamento de Erros:
Transações atômicas garantem rollback em caso de falha

Status do pedido atualizado para "failed" em erros

Eventos de falha disparados para monitoring

🚀 Como Executar
# Via Makefile
make build
make up

⚙️ Variáveis de Ambiente
DJANGO_SECRET_KEY: Chave secreta do Django

DJANGO_DEBUG: Modo debug (True/False)

POSTGRES_DB: Nome do banco PostgreSQL

POSTGRES_USER: Usuário PostgreSQL

POSTGRES_PASSWORD: Senha PostgreSQL

STRIPE_SECRET_KEY: Chave secreta da API Stripe

STRIPE_PUBLISHABLE_KEY: Chave pública Stripe