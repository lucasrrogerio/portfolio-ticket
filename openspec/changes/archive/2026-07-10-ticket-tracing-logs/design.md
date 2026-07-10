## Context

A arquitetura atual baseada no LangGraph não mantém contexto de logs (tracing) entre as chamadas dos nós. Como a LLM e a busca vetorial executam silenciosamente (ou apenas com logs de nível DEBUG gerados internamente pelas libs), torna-se muito difícil investigar um erro ou o raciocínio do modelo após um processamento, especialmente em ambiente de produção com alta simultaneidade.

## Goals / Non-Goals

**Goals:**
- Prover rastreabilidade nativa de cada requisição do LangGraph (entrada e saída de cada nó) utilizando o ID único do ticket recebido pela API.
- Imprimir essas mensagens no `stdout` num formato facilmente ingerível por agregadores de log (como o Kibana ou Datadog).

**Non-Goals:**
- Não iremos configurar plataformas de observabilidade de LLM baseadas em SaaS neste momento (ex: LangSmith, Langfuse ou DataDog APM).
- Não adicionaremos estado persistente/memória conversacional (MemorySaver) ao LangGraph, pois cada ticket é um processamento independente.

## Decisions

### 1. Uso da biblioteca `logging` nativa do Python
**Alternativas consideradas:** `loguru`, LangSmith.
**Decisão:** Usar `logging` que já vem built-in no Python. Como os requisitos de rastreabilidade são simples (apenas prefixar os logs com o `ticket_id`), não justifica adicionar novas dependências ao projeto.

### 2. Correlation ID no `AgentState`
**Decisão:** Adicionaremos o campo `ticket_id: str` no dicionário de estado (`AgentState`). 
**Rationale:** O LangGraph transita o estado entre todos os nós. Ao injetar o ID do ticket no nó de entrada, ele fica disponível nativamente para `no_analisar_intencao`, `no_buscar_documentos` e `no_gerar_resposta`, permitindo que todos gerem o log com o mesmo identificador sem precisar de variáveis globais de contexto (como o `contextvars`).

## Risks / Trade-offs

- **[Ruído de Logs no Terminal]** → Com logs detalhados, o terminal pode ficar verboso. (Mitigação: usar o nível de log `INFO` de forma sucinta, apontando apenas a entrada e as ações críticas, evitando logar grandes volumes de texto gerados pela LLM).
