from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

# Import the app and test client (conftest.py mock imports are triggered automatically)
from app.main import app

client = TestClient(app)

def test_read_root():
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200
    assert "message" in response.json()
    assert "API de IA operante" in response.json()["message"]

@patch('app.main.adicionar_documento')
def test_upload_document(mock_add):
    # Arrange
    file_content = b"### Politica de Acesso\nEsta e uma politica."
    
    # Act
    response = client.post(
        "/api/v1/documents",
        files={"file": ("acesso_conta.md", file_content, "text/markdown")}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "SUCESSO"
    mock_add.assert_called_once()

def test_upload_document_invalid_extension():
    # Act
    response = client.post(
        "/api/v1/documents",
        files={"file": ("acesso_conta.txt", b"content", "text/plain")}
    )
    
    # Assert
    assert response.status_code == 400
    assert "Apenas arquivos no formato Markdown" in response.json()["detail"]

@patch('app.main.listar_documentos')
def test_list_documents(mock_list):
    # Arrange
    mock_list.return_value = [{"id": "doc1.md", "conteudo": "teste", "metadata": {}}]

    # Act
    response = client.get("/api/v1/documents")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["quantidade"] == 1
    assert response.json()["documentos"][0]["id"] == "doc1.md"
    mock_list.assert_called_once()

@patch('app.main.remover_documento')
def test_delete_document(mock_remove):
    # Act
    response = client.delete("/api/v1/documents/acesso_conta.md")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "SUCESSO"
    mock_remove.assert_called_once_with("acesso_conta.md")

@patch('app.agents.graph_agent.processar_ticket', new_callable=AsyncMock)
def test_process_ticket_langgraph(mock_process):
    # Arrange
    mock_process.return_value = "Sua conta foi desbloqueada."
    payload = {
        "ticket_id": "TK-001",
        "texto": "minha conta bloqueou",
        "motor": "langgraph"
    }

    # Act
    response = client.post("/api/v1/tickets/process", json=payload)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "RESPONDIDO_PELA_IA"
    assert response.json()["resposta_ia"] == "Sua conta foi desbloqueada."
    mock_process.assert_called_once_with("TK-001", "minha conta bloqueou")

@patch('app.agents.agentscope_agent.processar_ticket', new_callable=AsyncMock)
def test_process_ticket_agentscope(mock_process):
    # Arrange
    mock_process.return_value = "Sua conta foi reativada."
    payload = {
        "ticket_id": "TK-002",
        "texto": "problema com faturamento",
        "motor": "agentscope"
    }

    # Act
    response = client.post("/api/v1/tickets/process", json=payload)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "RESPONDIDO_PELA_IA"
    assert response.json()["resposta_ia"] == "Sua conta foi reativada."
    mock_process.assert_called_once_with("TK-002", "problema com faturamento")
