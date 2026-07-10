## Why

Atualmente, o processamento de tickets através do grafo de agentes (LangGraph) ocorre de forma opaca (sem logs granulares). Isso dificulta o rastreamento (tracing) de um ticket específico em produção para entender por quais nós ele passou e quais ações foram tomadas pela IA. Precisamos adicionar logs estratégicos usando um *Correlation ID* (no caso, o `ticket_id`) para obtermos observabilidade sem a necessidade de manter o contexto completo em memória (stateless).

## What Changes

- Injeção do `ticket_id` no `AgentState` do LangGraph.
- Adição de logs nativos (`logging`) em cada nó crítico (`analista`, `bibliotecario`, `atendente`).
- Atualização do endpoint de processamento na API para repassar o `ticket_id` para o estado inicial do grafo.

## Capabilities

### New Capabilities
*(nenhuma capacidade de negócio nova adicionada)*

### Modified Capabilities
*(nenhuma — os requisitos comportamentais permanecem os mesmos, a mudança é estritamente não-funcional de observabilidade)*

## Impact

- **Código modificado:** `graph_agent.py`, `main.py`
- **Sistemas afetados:** Geração de logs no `stdout` / console do Uvicorn. Não há alteração no payload de entrada e saída da API.
