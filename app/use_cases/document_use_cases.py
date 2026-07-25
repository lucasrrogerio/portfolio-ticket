from typing import List, Dict, Any
from app.domain.interfaces.rag_repository import RAGRepository

class DocumentUseCases:
    def __init__(self, rag_repository: RAGRepository):
        self.rag_repo = rag_repository

    def indexar_documento(self, filename: str, conteudo_texto: str) -> Dict[str, str]:
        """
        Aplica regras de negócio para indexar um documento na base de conhecimento.
        """
        if not filename.endswith('.md'):
            raise ValueError("Apenas arquivos no formato Markdown (.md) são suportados.")
            
        self.rag_repo.adicionar_documento(
            conteudo=conteudo_texto,
            doc_id=filename,
            metadata={"filename": filename}
        )
        
        return {
            "status": "SUCESSO",
            "mensagem": f"Documento '{filename}' indexado com sucesso no RAG.",
            "document_id": filename
        }

    def remover_documento(self, doc_id: str) -> Dict[str, str]:
        """Remove documento aplicando regras se houver."""
        if not doc_id:
            raise ValueError("O ID do documento não pode ser vazio.")
            
        self.rag_repo.remover_documento(doc_id)
        return {
            "status": "SUCESSO",
            "mensagem": f"Documento com ID '{doc_id}' removido com sucesso do RAG."
        }

    def listar_documentos(self) -> Dict[str, Any]:
        """Lista os documentos existentes."""
        docs = self.rag_repo.listar_documentos()
        return {
            "status": "SUCESSO",
            "quantidade": len(docs),
            "documentos": docs
        }
