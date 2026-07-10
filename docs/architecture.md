# 🏗 Decisões de Arquitetura

Este documento descreve as decisões técnicas do projeto, seus trade-offs e as alternativas consideradas. Se você quer saber **como rodar**, veja o [README.md](README.md). Aqui explicamos o **porquê**.

---

## 📋 Índice

- [Por que IA e não regras determinísticas?](#-por-que-ia-e-não-regras-determinísticas)
- [Por que não usar só a busca vetorial, sem a LLM?](#-por-que-não-usar-só-a-busca-vetorial-sem-a-llm)
- [Trade-offs assumidos](#trade-offs-assumidos)
- [Visão geral da arquitetura](#-visão-geral-da-arquitetura)
- [Fluxo do LangGraph](#fluxo-do-langgraph)
- [Stack tecnológica e justificativas](#-stack-tecnológica-e-justificativas)
- [Separação de responsabilidades](#-separação-de-responsabilidades)

---

## 🤔 Por que IA e não regras determinísticas?

Essa é a pergunta certa a se fazer. Antes de escolher IA generativa, vale considerar as alternativas mais simples:

### Alternativas determinísticas e seus limites

| Abordagem | Como funciona | Onde falha |
|---|---|---|
| **Keyword matching** | Busca por palavras-chave ("reembolso", "senha", "SLA") e retorna a resposta mapeada. | O cliente escreve "quero meu dinheiro de volta" — nenhuma keyword bate. Sinônimos, erros de digitação e linguagem informal quebram o sistema. |
| **Árvore de decisão / Fluxo fixo** | Chatbot com menus ("Selecione: 1-Financeiro, 2-Técnico, 3-Outro"). | Funciona para fluxos simples, mas não lida com texto livre. O cliente precisa se encaixar nas opções — e quando o problema cruza duas categorias, o fluxo trava. |
| **Regex + NLP clássico** | Classificadores treinados (ex: Naive Bayes, SVM) para categorizar o ticket e retornar templates. | Exige dataset de treinamento rotulado, retreino constante quando surgem novos tipos de chamado, e as respostas são templates rígidos (não se adaptam ao tom/contexto da pergunta). |

### Onde a IA generativa + RAG se justifica

A combinação de **busca vetorial (RAG)** + **LLM** resolve exatamente os pontos fracos acima:

- **Busca semântica**: "quero meu dinheiro de volta" é matematicamente similar a "política de reembolso" no espaço vetorial, mesmo sem compartilhar nenhuma palavra. Isso elimina a fragilidade do keyword matching.
- **Resposta contextualizada**: A LLM não devolve um template fixo — ela formula uma resposta natural, adaptada ao tom e aos detalhes específicos da pergunta do cliente.
- **Zero retreino**: Novos documentos de política são adicionados via upload (endpoint POST). Não é necessário retreinar nenhum modelo, basta indexar o novo `.md`.

---

## 🔍 Por que não usar só a busca vetorial, sem a LLM?

A busca semântica por si só **já resolve o problema de encontrar a informação certa**. O cliente pergunta *"minha conta travou"* e o ChromaDB retorna o documento sobre bloqueio de conta — sem precisar de keyword matching exato. Então por que adicionar o custo de uma LLM no topo?

**Exemplo concreto — só busca vetorial:**
> Pergunta: *"Errei a senha várias vezes e minha conta travou, preciso acessar URGENTE pra uma reunião!"*
>
> Resposta (trecho cru do documento): *"A conta é bloqueada automaticamente após 5 tentativas incorretas de login. O desbloqueio ocorre automaticamente após 30 minutos."*

Funciona. O cliente recebe a informação correta, com custo zero de LLM e resposta determinística.

**Mesmo cenário — busca vetorial + LLM:**
> Resposta reformulada: *"Entendo a urgência! Sua conta foi bloqueada por segurança após as tentativas incorretas. Ela será desbloqueada automaticamente em 30 minutos. Enquanto isso, recomendo redefinir sua senha clicando em 'Esqueci minha senha' na tela de login assim que desbloquear."*

A LLM agrega em três pontos: **tom de voz** (reconheceu a urgência), **síntese** (combinou bloqueio + redefinição de senha de trechos diferentes) e **adaptação** (resposta sob medida para a pergunta, não um copiar-colar do doc).

**Quando cada abordagem faz sentido:**

| Cenário | Melhor abordagem |
|---|---|
| Docs já escritos para o cliente (FAQ público) | Só vetorial — a LLM é custo desnecessário |
| Docs internos/técnicos que precisam de reformulação | Vetorial + LLM |
| Volume altíssimo e orçamento limitado | Só vetorial, com LLM apenas para casos de baixa confiança |
| Experiência premium de atendimento | Vetorial + LLM |

Neste projeto, os documentos em `data/policies/` são escritos em tom interno/técnico, justificando a reformulação pela LLM. Mas a arquitetura **já suporta o cenário sem LLM** — bastaria o nó `bibliotecario` retornar o contexto direto como resposta final, pulando o nó `atendente` no grafo.

---

## Trade-offs assumidos

> Nenhuma decisão técnica é de graça. Aqui estão os custos conscientes:

- **Latência**: Uma chamada à LLM leva ~1-3s. Para triagem assíncrona (o cliente não espera em tempo real), isso é aceitável. Para chat ao vivo, precisaria de cache ou streaming.
- **Custo por chamada**: Cada ticket consome tokens da API. Em volume alto, isso precisa ser monitorado. A escolha do modelo Minimax-M3 foi intencional — é significativamente mais barato que GPT-4 para tarefas de suporte.
- **Não-determinismo**: A mesma pergunta pode gerar respostas ligeiramente diferentes. A "Regra de Ouro" no prompt (responder apenas com base no contexto) mitiga isso, mas não elimina 100%. Por isso, a arquitetura prevê revisão humana antes do envio.

**Resumo**: Para um cenário com texto livre do cliente, base de conhecimento que muda com frequência e necessidade de respostas naturais (não templates), IA + RAG é a escolha correta. Se os chamados fossem categorizados via formulário com campos fixos, um sistema de regras seria mais barato e mais previsível.

---

## 🗺 Visão geral da arquitetura

```
┌─────────────────┐       HTTP        ┌──────────────────────────────┐
│  Spring Boot    │ ──────────────▶   │  FastAPI (este serviço)      │
│  (Backend)      │  POST /tickets    │                              │
└─────────────────┘                   │  main.py (API)               │
                                      │    ├── graph_agent.py        │
                                      │    │    └── LangGraph         │
                                      │    │         ├─ Bibliotecário │ ─▶ ChromaDB (busca vetorial)
                                      │    │         └─ Atendente     │ ─▶ LLM (Minimax-M3)
                                      │    └── rag_service.py        │
                                      │         └── ChromaDB + Embeddings
                                      └──────────────────────────────┘
```

### Fluxo do LangGraph

O fluxo é intencionalmente simples (dois nós sequenciais):

```
[START] ──▶ [Bibliotecário] ──▶ [Atendente] ──▶ [END]
               │                     │
               ▼                     ▼
         Busca semântica        Gera resposta
         no ChromaDB            via LLM
```

**Por que LangGraph para um fluxo tão simples?** Porque a arquitetura foi pensada para crescer. Adicionar um nó de classificação, um nó de validação de confiança ou um loop de refinamento é trivial — basta adicionar nós e arestas ao grafo, sem reescrever a lógica existente.

---

## 🛠 Stack tecnológica e justificativas

| Tecnologia | Papel | Por que essa e não outra? |
|---|---|---|
| **FastAPI** | API REST | Async nativo, documentação automática (Swagger), validação via Pydantic. Ideal para microsserviços Python. |
| **LangGraph** | Orquestração de agentes | Permite modelar o fluxo como um grafo de estados, facilitando a adição de novos nós (classificação, validação, etc.) sem reescrever código. |
| **ChromaDB** | Banco vetorial | Roda embarcado (sem infra extra), persistência em disco, API simples. Suficiente para a escala deste projeto. Em produção, migraria para Qdrant ou Pinecone. |
| **SentenceTransformers** | Geração de embeddings | Modelo multilíngue (`paraphrase-multilingual-MiniLM-L12-v2`) que roda localmente, sem custo por chamada. Essencial para suporte em português. |
| **Minimax-M3 (via OpenAI SDK)** | LLM para geração de texto | Compatível com o SDK da OpenAI (troca de provider sem alterar código), custo acessível, e desempenho adequado para tarefas de suporte N1. |

---

## 📐 Separação de responsabilidades

```
Portfolio-Ticket/
├── main.py            → Camada HTTP (entrada/saída)
├── graph_agent.py     → Orquestração (fluxo dos agentes)
└── rag_service.py     → Dados (ChromaDB + embeddings)
```

- **`main.py`** — Camada HTTP. Não contém lógica de negócio; apenas recebe requests, chama os serviços e devolve responses.
- **`graph_agent.py`** — Orquestração. Define *como* os agentes interagem (ordem, fluxo, estado). Não sabe como o banco vetorial funciona internamente.
- **`rag_service.py`** — Dados. Encapsula toda interação com o ChromaDB e o modelo de embeddings. Pode ser substituído por outro provider (ex: Pinecone) sem afetar o restante.

Essa separação garante que cada módulo pode evoluir de forma independente. Trocar o ChromaDB por Pinecone? Só muda `rag_service.py`. Adicionar um novo nó de classificação no fluxo? Só muda `graph_agent.py`. Expor um novo endpoint? Só muda `main.py`.
