## Context

O RAG atual utiliza exclusivamente a busca densa via ChromaDB. O usuário relatou que buscas envolvendo planos específicos (ex: "vantagens do plano Enterprise") perdem a força da palavra-chave exata, trazendo documentos não relacionados. O problema decorre do comportamento inerente de embeddings, que diluem termos específicos no contexto semântico global da frase.

## Goals / Non-Goals

**Goals:**
- Implementar Busca Lexical (BM25) para complementar a busca semântica.
- Combinar os resultados via Reciprocal Rank Fusion (RRF).
- Fazer com que o `Analista` no LangGraph consiga distinguir a intenção genérica da palavra-chave foco.

**Non-Goals:**
- Não migraremos para um banco de dados vetorial corporativo (ex: Qdrant, Pinecone) apenas para obter a busca BM25 nativa. A solução deve rodar em memória/local para manter o projeto leve.
- Não iremos descartar o ChromaDB. A busca lexical correrá em paralelo.

## Decisions

### 1. Biblioteca para Busca Lexical
- **Decisão:** Utilizaremos o pacote `rank_bm25` (puro Python) para indexar e buscar os documentos.
- **Alternativa (Rejeitada):** Usar o SQLite FTS5 (pesado para configurar) ou trocar o ChromaDB por um banco vetorial completo (fugiria do escopo de testes e portabilidade).

### 2. Estratégia de Atualização do BM25
- **Decisão:** O índice BM25 requer os tokens completos dos documentos. Adicionaremos uma classe em `rag_service.py` que mantém a base BM25 sincronizada com os arquivos que existem na pasta `/data/policies`. 

### 3. Integração com LangGraph
- **Decisão:** O prompt do `Analista` será configurado para retornar um dicionário JSON no formato `{"intencao": "...", "keyword": "..."}`.
- O `Bibliotecario` acionará o RRF: pontuará os documentos encontrados pelas duas engines usando a fórmula matemática RRF: `score = 1 / (k + rank)`.

## Risks / Trade-offs

- **[Complexidade de JSON no LLM]** → Forçar a LLM a responder JSON pode gerar erros de formatação. (Mitigação: Usar modo de saída JSON nativo se o Minimax suportar, ou limpar a string recebida via Regex antes do parse).
- **[Sincronização BM25/Chroma]** → Deletar um documento pode ser desafiador se o BM25 estiver apenas na memória. (Mitigação: sempre que as políticas sofrerem CRUD na API, a lista em memória do BM25 será regenerada a partir do diretório físico, garantindo consistência com o ChromaDB).
