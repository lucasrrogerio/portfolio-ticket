## Why

O projeto atual atua como um sistema de RAG passivo, respondendo a perguntas com base em documentos. Para demonstrar um fluxo de orquestração de agentes completo (Agentic Workflow), precisamos dar ao agente a capacidade de "agir". Como não temos integrações reais com sistemas corporativos (como Salesforce, ServiceNow ou Okta), criaremos ferramentas *mockadas* com delays aleatórios simulando I/O de rede realista (2 a 12 segundos). Isso também enriquecerá os traces do OpenTelemetry/Tempo, comprovando a utilidade da stack de observabilidade para gargalos de performance.

## What Changes

- Criação de um conjunto de funções de ferramentas (tools) simuladas (ex: `get_user_status`, `unlock_account`, `escalate_to_human`, `get_billing_history`, `process_refund`).
- Configuração de delays assíncronos (`asyncio.sleep`) com tempos realistas para cada ferramenta.
- Vinculação dessas ferramentas ao agente no LangGraph (`llm.bind_tools`).
- Atualização do prompt principal para instruir o agente a rotear tickets para a ferramenta correta baseada na intenção do usuário.

## Capabilities

### New Capabilities
- `agent-tools-simulation`: Capacidade do agente de invocar ferramentas simuladas de serviços corporativos (IAM, ITSM, CRM) para resolver ou escalonar tickets, com simulação de latência de rede realista.

### Modified Capabilities
- `ticket-processing`: O processamento de tickets deixará de ser apenas análise e RAG, e passará a incluir a decisão de acionar ferramentas antes da resposta final.

## Impact

- **Código**: Adição de um novo módulo `tools.py` e alterações no fluxo do `graph_agent.py`.
- **Performance**: O tempo de resposta final do agente aumentará significativamente (até 15+ segundos dependendo das ferramentas acionadas) para simular o mundo real.
- **Observabilidade**: O Grafana Tempo registrará rastreamentos mais longos, capturando as durações individuais de cada chamada de ferramenta.
