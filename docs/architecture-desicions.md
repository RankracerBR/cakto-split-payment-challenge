## Decisões de Arquitetura (architecture-decisions.md)
O sistema foi desenvolvido com uma arquitetura baseada em microsserviços utilizando Django REST Framework. As principais decisões arquiteturais incluem:

Separação de responsabilidades: Serviço dedicado para processamento de pagamentos (PaymentProcessor)

Padrão de eventos: Implementação de sistema de eventos para notificações de sucesso/falha

Atomicidade transacional: Uso de transações atômicas para garantir consistência nos pagamentos

Integração Stripe: Gateway principal para processamento de cartões

Divisão automática: Regras de split pré-definidas com fee fixo da plataforma (5%)