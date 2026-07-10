## MODIFIED Requirements

### Requirement: Processar chamado via IA
O sistema SHALL receber um chamado em texto livre e roteá-lo para ferramentas (`tools`) se o agente identificar necessidade de ação (ex: desbloquear conta), ou buscar contexto relevante na base de conhecimento (RAG) se for apenas uma dúvida. O agente orquestrará as ações e retornará uma sugestão de resposta final.

#### Scenario: Chamado requer ação em sistema
- **WHEN** o cliente solicita uma ação que corresponde a uma ferramenta disponível (ex: "desbloqueie minha conta")
- **THEN** o agente invoca a ferramenta apropriada, aguarda a resposta (simulando a latência do sistema) e retorna uma resposta confirmando a resolução baseada no retorno da ferramenta.

#### Scenario: Chamado com tema coberto pela base
- **WHEN** o cliente envia um chamado cujo tema está coberto por um documento de política (ex: "como funciona o reembolso") e não requer ação em ferramenta
- **THEN** o agente consulta a base (RAG), retorna uma resposta contextualizada baseada exclusivamente no documento, com status `RESPONDIDO_PELA_IA`.

#### Scenario: Falha na LLM
- **WHEN** a chamada à LLM falha (timeout, API key inválida, erro de rede)
- **THEN** o sistema retorna erro HTTP 500 com a descrição da falha.
