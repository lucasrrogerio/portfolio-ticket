from app.services import rag_service

def test_adicionar_documento():
    # Arrange
    doc_id = "doc_test.md"
    conteudo = "Este é um documento de teste para políticas."
    rag_service.embedding_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
    
    # Mock do get() para retornar o documento após a inserção (para o BM25)
    rag_service.collection.get.return_value = {
        "ids": [doc_id],
        "documents": [conteudo],
        "metadatas": [{"filename": doc_id}]
    }

    # Act
    rag_service.adicionar_documento(conteudo, doc_id, {"filename": doc_id})

    # Assert
    rag_service.collection.upsert.assert_called_once_with(
        ids=[doc_id],
        embeddings=[[0.1, 0.2, 0.3]],
        documents=[conteudo],
        metadatas=[{"filename": doc_id}]
    )
    # Garante que atualizou o index BM25
    assert rag_service.bm25_ids == [doc_id]
    assert rag_service.bm25_docs == [conteudo]

def test_busca_hibrida_sem_resultados():
    # Arrange
    rag_service.embedding_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
    rag_service.collection.query.return_value = {"ids": [[]], "documents": [[]]}
    rag_service.collection.get.return_value = {"ids": [], "documents": []}
    rag_service._atualizar_bm25() # reseta bm25

    # Act
    resultado = rag_service.busca_hibrida("login bloqueado", "bloqueio")

    # Assert
    assert resultado == "Sem resultados."

def test_busca_hibrida_com_resultados():
    # Arrange
    doc_id = "acesso.md"
    conteudo = "Sua conta é desbloqueada automaticamente em 30 minutos."
    
    rag_service.collection.get.return_value = {
        "ids": [doc_id],
        "documents": [conteudo],
        "metadatas": [{"filename": doc_id}]
    }
    rag_service._atualizar_bm25() # Atualiza o BM25 com este documento
    
    # Mock do query semântico retornar o mesmo ID
    rag_service.collection.query.return_value = {
        "ids": [[doc_id]],
        "documents": [[conteudo]]
    }
    rag_service.embedding_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]

    # Act
    resultado = rag_service.busca_hibrida("como desbloquear minha conta?", "desbloquear")

    # Assert
    assert conteudo in resultado
