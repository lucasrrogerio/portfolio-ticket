from sentence_transformers import SentenceTransformer
import chromadb
from rank_bm25 import BM25Okapi

# Inicializa o modelo de embeddings (carregado apenas uma vez neste serviço)
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# Inicializa o cliente do ChromaDB
chroma_client = chromadb.PersistentClient(path="meu_banco_vetorial")
collection = chroma_client.get_or_create_collection(name="politicas_empresa")

def _atualizar_bm25():
    global bm25_index, bm25_ids, bm25_docs
    dados = collection.get()
    bm25_ids = dados.get("ids", [])
    bm25_docs = dados.get("documents", [])
    if not bm25_docs:
        bm25_index = None
        return
    tokenized_corpus = [doc.lower().split() for doc in bm25_docs]
    bm25_index = BM25Okapi(tokenized_corpus)

_atualizar_bm25()

def adicionar_documento(conteudo: str, doc_id: str, metadata: dict = None) -> None:
    """
    Gera o embedding para o conteúdo e o insere/atualiza na coleção do ChromaDB.
    """
    vetor = embedding_model.encode(conteudo).tolist()
    collection.upsert(
        ids=[doc_id],
        embeddings=[vetor],
        documents=[conteudo],
        metadatas=[metadata or {}]
    )
    _atualizar_bm25()

def remover_documento(doc_id: str) -> None:
    """
    Remove um documento do ChromaDB pelo ID.
    """
    collection.delete(ids=[doc_id])
    _atualizar_bm25()

def listar_documentos() -> list:
    """
    Lista todos os documentos indexados no ChromaDB.
    """
    dados = collection.get()
    documentos = []
    ids = dados.get("ids", [])
    docs = dados.get("documents", [])
    metadatas = dados.get("metadatas", [])
    
    for i in range(len(ids)):
        documentos.append({
            "id": ids[i],
            "conteudo": docs[i] if docs else "",
            "metadata": metadatas[i] if metadatas else {}
        })
    return documentos

def buscar_documentos_similares(query: str, n_results: int = 3) -> str:
    """
    Gera o embedding da query e realiza busca semântica na coleção.
    Retorna o texto dos documentos mais similares encontrados concatenados.
    """
    query_vector = embedding_model.encode(query).tolist()
    resultados = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results
    )
    
    if resultados['documents'] and resultados['documents'][0]:
        return "\n\n---\n\n".join(resultados['documents'][0])
    return "Sem resultados."

def buscar_documentos_bm25(keyword: str, n_results: int = 3) -> list:
    if not bm25_index or not keyword:
        return []
    tokenized_query = keyword.lower().split()
    scores = bm25_index.get_scores(tokenized_query)
    
    doc_scores = [(bm25_ids[i], bm25_docs[i], scores[i]) for i in range(len(bm25_ids)) if scores[i] > 0]
    doc_scores.sort(key=lambda x: x[2], reverse=True)
    return doc_scores[:n_results]

def busca_hibrida(intencao: str, keyword: str, n_results: int = 3) -> str:
    # 1. Busca Semântica
    sem_docs = []
    if intencao:
        query_vector = embedding_model.encode(intencao).tolist()
        resultados = collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        if resultados['ids'] and resultados['ids'][0]:
            sem_docs = resultados['ids'][0]
    
    # 2. Busca Lexical
    lex_docs = []
    if keyword:
        bm25_resultados = buscar_documentos_bm25(keyword, n_results)
        lex_docs = [doc[0] for doc in bm25_resultados]

    # 3. Reciprocal Rank Fusion (RRF)
    k = 60
    rrf_scores = {}
    
    for rank, doc_id in enumerate(sem_docs):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
        
    for rank, doc_id in enumerate(lex_docs):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)

    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    top_ids = [doc_id for doc_id, score in sorted_docs[:n_results]]

    final_docs = []
    for doc_id in top_ids:
        idx = bm25_ids.index(doc_id)
        final_docs.append(bm25_docs[idx])
        
    if final_docs:
        return "\n\n---\n\n".join(final_docs)
    return "Sem resultados."
