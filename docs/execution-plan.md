## Fluxo de Processamento:
- Criação do Pedido: Validação dos dados e criação do registro Order

- Validação do Pagamento: Verificação do método de pagamento e valor

- Cobrança Stripe: Processamento da transação via Stripe API

- Divisão Automática: Criação das regras de split (95% user + 5% plataforma)

- Atualização de Status: Marcação do pedido como completed

- Disparo de Eventos: Notificação de sucesso e trigger para payouts

- Tratamento de Erros: Transações atômicas garantem rollback em caso de falha

- Status do pedido atualizado para "failed" em erros

- Eventos de falha disparados para monitoring

🚀 Como Executar

# Via Makefile

make build

make up

ou:

sudo make build

sudo make up


Caso precise fazer rebuild:

make rebuild

make up

ou

sudo make rebuild

sudo make up

⚙️ Variáveis de Ambiente

DJANGO_SECRET_KEY: Chave secreta do Django(Para gerar a chave: python generate_hash)
                                           
DJANGO_DEBUG: Modo debug (True/False)

POSTGRES_DB: Nome do banco PostgreSQL

POSTGRES_USER: Usuário PostgreSQL

POSTGRES_PASSWORD: Senha PostgreSQL

STRIPE_SECRET_KEY: Chave secreta da API Stripe(Chave Teste: 'Enviada pelo email')

STRIPE_PUBLISHABLE_KEY: Chave pública Stripe (Chave Teste: 'Enviada pelo email')

Obs:(Digite o comando cp .env.example .env para copiar as variáveis para o .env)
    (Ou crie manualmente a pasta e cole as variáveis com as suas respectivas chaves)

## URLS para documentação
http://127.0.0.1:8001/swagger/ # Swagger


## URLS para visualização de logs
http://localhost:8001/metrics # Django-Prometheus

http://localhost:8001/logs/ # Django-Log-Hub (Interface gráfica para logs)

