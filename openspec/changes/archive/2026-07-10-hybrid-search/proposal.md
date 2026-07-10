## Why

O banco de dados vetorial atual (ChromaDB) utiliza Busca Densa (Embeddings), que é excelente para recuperar significado semântico, mas possui baixa acurácia ao buscar palavras-chave exatas e nomes próprios (ex: "Enterprise", "Básico", códigos de erro). Isso exige regras fixas nos prompts ("Prompt Brittleness") para contornar descasamentos semânticos. A implementação da Busca Híbrida resolve esse problema combinando o melhor dos dois mundos: compreensão de contexto (Vetores) e precisão de palavras-chave (BM25).

## What Changes

- O nó "Analista de Intenção" passará a extrair um objeto JSON contendo a intenção semântica e a(s) palavra(s)-chave principal(is).
- Implementação do algoritmo BM25 localmente (via `rank_bm25` ou similar) para criar um índice paralelo de palavras-chave.
- O nó "Bibliotecário" passará a fazer duas buscas simultâneas: Semântica (ChromaDB) e Lexical (BM25).
- Implementação de um algoritmo de pontuação (RRF - Reciprocal Rank Fusion) para mesclar e re-ranquear os resultados das duas buscas.

## Capabilities

### New Capabilities
- `hybrid-search`: Implementação do fluxo de busca dupla com RRF (Reciprocal Rank Fusion).

### Modified Capabilities
*(nenhuma)*

## Impact

- **Código modificado:** `graph_agent.py`, `rag_service.py` (ou criação de um novo serviço dedicado).
- **Dependências:** Adição provável da biblioteca `rank_bm25`.
- **Sistemas afetados:** O fluxo de ingestão de documentos (`POST /api/v1/documents`) precisará adicionar o documento tanto no ChromaDB quanto no índice BM25 (que precisará ser serializado no disco ou regenerado no boot).
