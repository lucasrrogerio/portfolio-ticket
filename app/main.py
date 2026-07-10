import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from app.services.rag_service import adicionar_documento, remover_documento, listar_documentos
from app.core.observability import setup_observability

# Instancia o servidor FastAPI
app = FastAPI(
    title="Serviço de IA - Ticket Triage",
    description="API que utiliza LangGraph e RAG para sugerir respostas aos chamados e gerenciar a base de conhecimento.",
    version="1.0.0"
)

# Configura observabilidade (Prometheus, OpenTelemetry e Loki)
setup_observability(app)

# Modelos Pydantic para validar os dados que entram e saem da API
class TicketRequest(BaseModel):
    ticket_id: str
    texto: str
    motor: Optional[str] = "langgraph"

class TicketResponse(BaseModel):
    ticket_id: str
    status: str
    resposta_ia: str
    erro: Optional[str] = None

@app.get("/")
def root():
    return {"message": "API de IA operante. Acesse /docs para ver os endpoints."}

@app.post("/api/v1/tickets/process", response_model=TicketResponse)
async def process_ticket_endpoint(request: TicketRequest):
    """
    Recebe um chamado, passa pelo fluxo de agentes escolhido (LangGraph ou AgentScope) e retorna a resposta.
    """
    try:
        if request.motor == "agentscope":
            from app.agents.agentscope_agent import processar_ticket as processar_agentscope
            resposta_final = await processar_agentscope(request.ticket_id, request.texto)
        else:
            from app.agents.graph_agent import processar_ticket as processar_langgraph
            resposta_final = await processar_langgraph(request.ticket_id, request.texto)
        
        return TicketResponse(
            ticket_id=request.ticket_id,
            status="RESPONDIDO_PELA_IA",
            resposta_ia=resposta_final
        )
    except Exception as e:
        # Se ocorrer um erro (ex: falha na API do Minimax), devolve 500
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/documents")
async def upload_document(file: UploadFile = File(...)):
    """
    Recebe um arquivo no formato .md, extrai o texto e indexa no RAG (ChromaDB).
    """
    if not file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail="Apenas arquivos no formato Markdown (.md) são suportados.")
    
    try:
        conteudo_bytes = await file.read()
        conteudo_texto = conteudo_bytes.decode("utf-8")
        
        # Usa o nome do arquivo como ID e adiciona nos metadados
        adicionar_documento(
            conteudo=conteudo_texto,
            doc_id=file.filename,
            metadata={"filename": file.filename}
        )
        
        return {
            "status": "SUCESSO",
            "mensagem": f"Documento '{file.filename}' indexado com sucesso no RAG.",
            "document_id": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")

@app.delete("/api/v1/documents/{doc_id}")
def delete_document(doc_id: str):
    """
    Remove um documento da base do RAG (ChromaDB) pelo ID.
    """
    try:
        remover_documento(doc_id)
        return {
            "status": "SUCESSO",
            "mensagem": f"Documento com ID '{doc_id}' removido com sucesso do RAG."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover o documento: {str(e)}")

@app.get("/api/v1/documents")
def list_documents():
    """
    Lista todos os documentos atualmente indexados no RAG.
    """
    try:
        docs = listar_documentos()
        return {
            "status": "SUCESSO",
            "quantidade": len(docs),
            "documentos": docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")


