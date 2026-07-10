# Política de Limites de Uso da API (Rate Limiting)

## 1. Limites por Plano
Para garantir a estabilidade do serviço para todos os clientes, nossa API pública aplica limites de requisições baseados no plano de assinatura contratado:

- **Plano Básico:** 100 requisições por minuto.
- **Plano Pro:** 500 requisições por minuto.
- **Plano Enterprise:** 2.000 requisições por minuto.

## 2. Comportamento ao Exceder o Limite
- Quando o cliente atinge o limite do seu plano, a API começará a retornar o código de erro HTTP **429 Too Many Requests**.
- O header de resposta `Retry-After` informará quantos segundos o cliente deve aguardar antes de fazer uma nova requisição.

## 3. Aumentos Temporários de Limite
- Clientes do plano **Enterprise** podem solicitar um aumento temporário de limite (burst) para campanhas específicas ou migração de dados.
- Essa solicitação deve ser feita com pelo menos **48 horas de antecedência** via ticket.
- O suporte de Nível 1 deve encaminhar o pedido para a equipe de **Engenharia de Plataforma (Nível 3)**.
- Clientes dos planos Básico e Pro **NÃO** são elegíveis para aumento temporário. Se precisarem de mais limite, devem ser orientados a fazer upgrade de plano.

## 4. Bloqueio por Abuso
- Independentemente do plano, se o sistema detectar requisições maliciosas ou um pico anormal que ameace a infraestrutura, a chave de API será **revogada automaticamente**.
- Se um cliente abrir um ticket informando que sua chave foi revogada por abuso (erro 401 Unauthorized repentino acompanhado de e-mail de alerta), o analista deve transferir o caso IMEDIATAMENTE para a equipe de **Segurança (SecOps)**.
