## Context

O orquestrador de tickets atual usa RAG para resolver dúvidas. No entanto, para atuar como um verdadeiro orquestrador de suporte corporativo, ele precisa realizar ações (como desbloquear senhas ou consultar histórico de faturamento) em sistemas externos. Como não temos integrações com sistemas reais neste portfólio, utilizaremos a funcionalidade de *Tool Calling* dos LLMs associada a funções de *mock* em Python. 
Para simular as restrições e a latência de rede do mundo real e alimentar a stack de observabilidade (OpenTelemetry + Loki + Grafana Tempo) com traces autênticos de I/O em formato *waterfall*, cada ferramenta terá um atraso artificial.

## Goals / Non-Goals

**Goals:**
- Implementar funções em Python que simulem chamadas a sistemas de IAM, CRM e ITSM.
- Introduzir delays assíncronos (usando `asyncio.sleep()`) variando de 2s a 12s para cada ferramenta.
- Integrar essas ferramentas ao `graph_agent.py` do LangGraph, permitindo que o LLM as invoque.
- Manter o trace ID atual para que as chamadas às ferramentas apareçam no Grafana Tempo.

**Non-Goals:**
- Conectar a APIs reais.
- Implementar lógica complexa de autenticação e falhas nas ferramentas mockadas (o foco é na demonstração do *Tool Calling* e da latência).
- Modificar o fluxo do `agentscope_agent.py` (focaremos apenas no `graph_agent.py`).

## Decisions

- **Framework de Ferramentas:** Utilizaremos o decorator `@tool` do `langchain_core.tools`. Isso facilita o binding com os modelos do Langchain usados no `graph_agent.py` (`llm.bind_tools(tools)`).
- **Módulo de Ferramentas:** As ferramentas serão definidas num arquivo separado (ex: `tools.py`) para evitar poluir a definição do grafo.
- **Instrumentação:** Como estamos usando as bibliotecas do Langchain e já inicializamos o OpenTelemetry global, espera-se que as invocações de `@tool` sejam propagadas automaticamente ou facilmente envelopadas num *span* se houver necessidade (podemos usar o decorator `@tracer.start_as_current_span` nas ferramentas se a integração nativa falhar).
- **Tool Node:** Utilizaremos o nó pré-construído `ToolNode` do `langgraph.prebuilt` para processar as mensagens da invocação da ferramenta e devolvê-las ao LLM.

## Risks / Trade-offs

- **Aumento do Tempo de Resposta (Timeout):** O tempo total de resposta da API poderá ultrapassar 15 segundos facilmente. 
  - *Mitigação:* Como usamos FastAPI, a aplicação não bloqueará *threads* (async), mas o cliente esperando a resposta HTTP experimentará a demora. Isso é exatamente o comportamento desejado para enriquecer os rastreamentos do Grafana, então documentaremos isso no portfólio.
- **Custos do LLM:** Tool Calling envolve mais viagens de ida e volta ao LLM.
  - *Mitigação:* Aceitável, visto que o propósito é justamente construir e apresentar um Agentic Workflow robusto no portfólio.
