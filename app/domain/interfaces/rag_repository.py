from typing import Protocol, List, Dict, Any

class RAGRepository(Protocol):
    def adicionar_documento(self, conteudo: str, doc_id: str, metadata: dict = None) -> None:
        """Gera o embedding e insere/atualiza na coleção."""
        ...

    def remover_documento(self, doc_id: str) -> None:
        """Remove um documento pelo ID."""
        ...

    def listar_documentos(self) -> List[Dict[str, Any]]:
        """Lista todos os documentos indexados."""
        ...

    def buscar_documentos_similares(self, query: str, n_results: int = 3) -> str:
        """Busca semântica básica."""
        ...

    def busca_hibrida(self, intencao: str, keyword: str, n_results: int = 3) -> str:
        """Busca combinando semântica e BM25."""
        ...
