## ADDED Requirements

### Requirement: Processar chamado via IA
O sistema SHALL receber um chamado em texto livre, buscar contexto relevante na base de conhecimento e retornar uma sugestão de resposta gerada pela LLM.

#### Scenario: Chamado com tema coberto pela base
- **WHEN** o cliente envia um chamado cujo tema está coberto por um documento de política (ex: "minha conta foi bloqueada")
- **THEN** o sistema retorna uma resposta contextualizada, baseada exclusivamente no documento encontrado, com status `RESPONDIDO_PELA_IA`

#### Scenario: Chamado sem correspondência na base
- **WHEN** o cliente envia um chamado cujo tema não possui documento correspondente na base de conhecimento
- **THEN** o sistema retorna uma resposta informando que não possui a informação e que será necessário transferir para um atendente humano

#### Scenario: Falha na LLM
- **WHEN** a chamada à LLM falha (timeout, API key inválida, erro de rede)
- **THEN** o sistema retorna erro HTTP 500 com a descrição da falha

### Requirement: Endpoint de health check
O sistema SHALL expor um endpoint raiz (`GET /`) para verificação de disponibilidade.

#### Scenario: Verificação de saúde
- **WHEN** um cliente HTTP faz `GET /`
- **THEN** o sistema retorna status 200 com mensagem indicando que a API está operante
