## 1. Configuração e Bibliotecas

- [x] 1.1 Adicionar a biblioteca `rank_bm25` às dependências do projeto (e.g. `pip install rank_bm25`)

## 2. Refatoração do Serviço de Busca (RAG Service)

- [x] 2.1 Modificar `rag_service.py` para instanciar a classe `BM25Okapi` com os textos dos documentos carregados da pasta `data/policies`.
- [x] 2.2 Criar a função `buscar_documentos_bm25(keyword: str, n_results=3)` em `rag_service.py` para retornar o ranking lexical.
- [x] 2.3 Criar a função `busca_hibrida(intencao: str, keyword: str, n_results=3)` que execute ambas as buscas e aplique o RRF (Reciprocal Rank Fusion) para combinar e re-ranquear os documentos.

## 3. Adaptação do Agente LangGraph

- [x] 3.1 Alterar o prompt em `no_analisar_intencao` (arquivo `graph_agent.py`) para extrair JSON no formato `{"intencao": "...", "keyword": "..."}`.
- [x] 3.2 Modificar `no_buscar_documentos` para extrair o JSON retornado e acionar a `busca_hibrida` ao invés da busca vetorial simples.

## 4. Testes e Validação

- [x] 4.1 Rodar a aplicação localmente e realizar chamadas na API para garantir que a palavra "Enterprise" traga os arquivos corretos sem o uso de regras de negócio fixas no prompt.
