from sentence_transformers import SentenceTransformer
import chromadb
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any
from app.domain.interfaces.rag_repository import RAGRepository

class ChromaRAGRepository(RAGRepository):
    def __init__(self):
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.chroma_client = chromadb.PersistentClient(path="meu_banco_vetorial")
        self.collection = self.chroma_client.get_or_create_collection(name="politicas_empresa")
        self.bm25_index = None
        self.bm25_ids = []
        self.bm25_docs = []
        self._atualizar_bm25()

    def _atualizar_bm25(self):
        dados = self.collection.get()
        self.bm25_ids = dados.get("ids", [])
        self.bm25_docs = dados.get("documents", [])
        if not self.bm25_docs:
            self.bm25_index = None
            return
        tokenized_corpus = [doc.lower().split() for doc in self.bm25_docs]
        self.bm25_index = BM25Okapi(tokenized_corpus)

    def adicionar_documento(self, conteudo: str, doc_id: str, metadata: dict = None) -> None:
        vetor = self.embedding_model.encode(conteudo).tolist()
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[vetor],
            documents=[conteudo],
            metadatas=[metadata or {}]
        )
        self._atualizar_bm25()

    def remover_documento(self, doc_id: str) -> None:
        self.collection.delete(ids=[doc_id])
        self._atualizar_bm25()

    def listar_documentos(self) -> List[Dict[str, Any]]:
        dados = self.collection.get()
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

    def buscar_documentos_similares(self, query: str, n_results: int = 3) -> str:
        query_vector = self.embedding_model.encode(query).tolist()
        resultados = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        
        if resultados['documents'] and resultados['documents'][0]:
            return "\n\n---\n\n".join(resultados['documents'][0])
        return "Sem resultados."

    def _buscar_documentos_bm25(self, keyword: str, n_results: int = 3) -> list:
        if not self.bm25_index or not keyword:
            return []
        tokenized_query = keyword.lower().split()
        scores = self.bm25_index.get_scores(tokenized_query)
        
        doc_scores = [(self.bm25_ids[i], self.bm25_docs[i], scores[i]) for i in range(len(self.bm25_ids)) if scores[i] > 0]
        doc_scores.sort(key=lambda x: x[2], reverse=True)
        return doc_scores[:n_results]

    def busca_hibrida(self, intencao: str, keyword: str, n_results: int = 3) -> str:
        sem_docs = []
        if intencao:
            query_vector = self.embedding_model.encode(intencao).tolist()
            resultados = self.collection.query(
                query_embeddings=[query_vector],
                n_results=n_results
            )
            if resultados['ids'] and resultados['ids'][0]:
                sem_docs = resultados['ids'][0]
        
        lex_docs = []
        if keyword:
            bm25_resultados = self._buscar_documentos_bm25(keyword, n_results)
            lex_docs = [doc[0] for doc in bm25_resultados]

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
            idx = self.bm25_ids.index(doc_id)
            final_docs.append(self.bm25_docs[idx])
            
        if final_docs:
            return "\n\n---\n\n".join(final_docs)
        return "Sem resultados."
