## Context

O projeto parte do zero — não existe infraestrutura de atendimento automatizado. O suporte é feito manualmente por analistas que buscam informações em documentos internos (Markdown) para responder chamados.

A proposta (ver `proposal.md`) define a criação de um microsserviço Python que automatize a busca e a formulação de respostas. Este documento detalha as decisões técnicas de implementação.

## Goals / Non-Goals

**Goals:**
- Implementar busca semântica em documentos de política usando embeddings vetoriais
- Orquestrar o fluxo busca → geração de resposta de forma extensível (grafo de agentes)
- Expor a funcionalidade via API REST para integração com o backend Spring Boot
- Manter o sistema simples de rodar localmente (sem infra externa)

**Non-Goals:**
- Não é objetivo ter chat em tempo real (streaming) — o fluxo é assíncrono
- Não faremos fine-tuning de modelos — usamos modelos pré-treinados
- Não implementamos autenticação/autorização neste serviço (fica no Spring Boot)
- Não fazemos text splitting/chunking — os documentos de política são pequenos o suficiente para indexar inteiros

## Decisions

### 1. ChromaDB como banco vetorial (em vez de FAISS, Pinecone ou Qdrant)

**Escolha:** ChromaDB com `PersistentClient` local.

**Alternativas consideradas:**
- **FAISS**: Mais performante para busca pura, mas sem persistência nativa e API mais baixo nível.
- **Pinecone/Qdrant**: Managed services com alta escalabilidade, mas exigem infra externa e conta/API key adicional.

**Rationale:** ChromaDB roda embarcado (sem servidor separado), persiste em disco automaticamente e tem API Pythonica simples. Para a escala deste projeto (dezenas de documentos, não milhões), é mais do que suficiente. Em produção, a migração para Qdrant seria trivial pois o `rag_service.py` encapsula toda interação.

### 2. SentenceTransformers local (em vez de API de embeddings)

**Escolha:** Modelo `paraphrase-multilingual-MiniLM-L12-v2` rodando localmente via SentenceTransformers.

**Alternativas consideradas:**
- **OpenAI `text-embedding-3-small`**: Melhor qualidade, mas custo por chamada e dependência de API externa.
- **Cohere Embed**: Similar ao OpenAI em termos de custo/dependência.

**Rationale:** Modelo multilíngue essencial para suporte em português. Roda localmente sem custo por chamada e sem latência de rede. O trade-off é o consumo de memória (~500MB), aceitável para um microsserviço dedicado.

### 3. LangGraph para orquestração (em vez de chamadas diretas)

**Escolha:** LangGraph com `StateGraph` de dois nós (Bibliotecário → Atendente).

**Alternativas consideradas:**
- **Chamada direta**: `buscar() → gerar()` em sequência, sem framework.
- **LangChain Chains**: `RetrievalQA` chain pronta.

**Rationale:** O fluxo atual é simples (dois nós sequenciais), mas o LangGraph foi escolhido pensando em extensibilidade. Adicionar um nó de classificação, validação de confiança ou loop de refinamento é trivial — basta adicionar nós e arestas ao grafo sem reescrever lógica. A abstração de `StateGraph` também torna o fluxo explícito e testável.

### 4. Minimax-M3 como LLM (em vez de GPT-4 ou modelos open-source locais)

**Escolha:** Minimax-M3 via SDK OpenAI-compatível.

**Alternativas consideradas:**
- **GPT-4/GPT-4o**: Melhor qualidade geral, mas custo significativamente maior para tarefas de suporte N1.
- **Llama 3 local**: Zero custo, mas exige GPU e infra de inferência.

**Rationale:** Custo acessível para o volume esperado, qualidade adequada para reformulação de documentos de suporte, e compatibilidade com o SDK da OpenAI (permite trocar de provider alterando apenas `base_url` e `model`, sem mudar código).

### 5. FastAPI como framework HTTP (em vez de Flask ou Django)

**Escolha:** FastAPI com Pydantic para validação.

**Rationale:** Async nativo (importante para chamadas à LLM), documentação Swagger automática, e validação de request/response via Pydantic. Ideal para microsserviços Python focados.

## Risks / Trade-offs

- **[Latência LLM ~1-3s]** → Aceitável para triagem assíncrona. Para chat ao vivo, precisaria de streaming ou cache de respostas frequentes.
- **[Custo por chamada à LLM]** → Monitorar volume. Minimax-M3 mitiga parcialmente. Alternativa: retornar só o trecho do documento (sem LLM) para casos de alta confiança.
- **[Não-determinismo da LLM]** → Prompt com "Regra de Ouro" restringe a resposta ao contexto fornecido. Arquitetura prevê revisão humana antes do envio.
- **[ChromaDB embarcado = single-process]** → Apenas um processo pode acessar o banco por vez. Em produção multi-instância, migrar para ChromaDB client-server ou Qdrant.
- **[Documentos inteiros (sem chunking)]** → Funciona para políticas curtas (~500 palavras). Se os documentos crescerem, implementar text splitting.
