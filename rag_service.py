from sentence_transformers import SentenceTransformer
import chromadb

# Inicializa o modelo de embeddings (carregado apenas uma vez neste serviço)
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# Inicializa o cliente do ChromaDB
chroma_client = chromadb.PersistentClient(path="meu_banco_vetorial")
collection = chroma_client.get_or_create_collection(name="politicas_empresa")

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

def remover_documento(doc_id: str) -> None:
    """
    Remove um documento do ChromaDB pelo ID.
    """
    collection.delete(ids=[doc_id])

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

def buscar_documentos_similares(query: str, n_results: int = 1) -> str:
    """
    Gera o embedding da query e realiza busca semântica na coleção.
    Retorna o texto do documento mais similar encontrado.
    """
    query_vector = embedding_model.encode(query).tolist()
    resultados = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results
    )
    
    if resultados['documents'] and resultados['documents'][0]:
        return resultados['documents'][0][0]
    return "Sem resultados."
