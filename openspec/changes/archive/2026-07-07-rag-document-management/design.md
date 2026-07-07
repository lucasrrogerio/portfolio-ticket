## Context

A implementação inicial inicializava o banco vetorial ChromaDB com documentos estáticos na inicialização do serviço. A lógica estava acoplada dentro do `graph_agent.py`. Para permitir que o sistema maior gerencie a base de conhecimento (adicionando e removendo políticas), precisamos de endpoints na API e de uma separação limpa de responsabilidades.

## Goals / Non-Goals

**Goals:**
- Isolar toda interação com ChromaDB e SentenceTransformers num serviço próprio (`rag_service.py`)
- Fornecer endpoints CRUD (Create, Read, Delete) para documentos na API
- Suportar upload de arquivos Markdown diretamente pela API

**Non-Goals:**
- Não suportaremos atualização de documentos (PUT). A abordagem será remover o antigo e adicionar o novo.
- Não faremos versionamento de documentos na API de IA (o Spring Boot pode fazer isso, se necessário).
- Não suportaremos outros formatos além de Markdown (`.md`) no momento.

## Decisions

### 1. Separação de responsabilidades (rag_service.py)

**Escolha:** Extrair toda a lógica de inicialização de embeddings, persistência do ChromaDB e buscas para uma classe/módulo `rag_service.py`.

**Rationale:** O `graph_agent.py` deve se preocupar apenas com a orquestração do fluxo de agentes (LangGraph), e o `main.py` com o roteamento HTTP. Encapsulando o banco vetorial, podemos no futuro trocar o ChromaDB por outro banco (ex: Pinecone) sem alterar o grafo ou a API.

### 2. Uso do `python-multipart`

**Escolha:** Adicionar `python-multipart` para suportar requisições `multipart/form-data` no FastAPI.

**Rationale:** É o pacote padrão suportado pelo FastAPI para lidar com upload de arquivos (`UploadFile`). Essencial para o endpoint de POST.

### 3. ID do documento igual ao nome do arquivo

**Escolha:** Ao fazer upload de um documento (ex: `politica_sla.md`), o ID no ChromaDB será o nome do arquivo (`politica_sla.md`).

**Rationale:** Simplifica o rastreamento e a remoção. Para deletar, basta enviar o nome do arquivo. Isso pressupõe que os nomes de arquivo sejam únicos, o que é razoável para este escopo.

## Risks / Trade-offs

- **[Nomes de arquivo duplicados]** → Como o ID é o nome do arquivo, um upload com o mesmo nome sobrescreverá o documento existente. (Mitigação: Isso pode ser visto como uma feature de atualização implícita).
- **[Formato de arquivo incorreto]** → Apenas Markdown (.md) é suportado. (Mitigação: A API deve validar a extensão antes de processar).
