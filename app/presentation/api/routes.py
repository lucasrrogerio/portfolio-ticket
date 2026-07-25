from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from app.presentation.api.schemas import TicketRequest, TicketResponse
from app.use_cases.ticket_use_cases import ProcessTicketUseCase
from app.use_cases.document_use_cases import DocumentUseCases

# Dependências (Infrastructure)
from app.infrastructure.rag.chroma_service import ChromaRAGRepository
from app.infrastructure.agents.agent_factory import AgentServiceFactory

router = APIRouter()

# --- Dependency Injection Factories ---
# Em um cenário mais complexo, essas instâncias poderiam ser singleton
# registradas em um container como `dependency-injector`.
# Para FastAPI, Depends resolve bem o SRP na borda.
def get_rag_repository():
    return ChromaRAGRepository()

def get_document_use_cases(rag_repo = Depends(get_rag_repository)):
    return DocumentUseCases(rag_repository=rag_repo)
# --------------------------------------

@router.get("/")
def root():
    return {"message": "API de IA operante. Acesse /docs para ver os endpoints."}

@router.post("/api/v1/tickets/process", response_model=TicketResponse)
async def process_ticket_endpoint(
    request: TicketRequest,
    rag_repo = Depends(get_rag_repository)
):
    """
    Recebe um chamado, passa pelo fluxo de agentes escolhido (LangGraph ou AgentScope) e retorna a resposta.
    """
    try:
        agent_service = AgentServiceFactory.get_agent_service(
            motor=request.motor, 
            rag_repository=rag_repo
        )
            
        use_case = ProcessTicketUseCase(agent_service=agent_service)
        
        resultado = await use_case.execute(request.ticket_id, request.texto)
        return TicketResponse(**resultado)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/documents")
async def upload_document(
    file: UploadFile = File(...),
    use_cases: DocumentUseCases = Depends(get_document_use_cases)
):
    """
    Recebe um arquivo no formato .md, extrai o texto e indexa no RAG (ChromaDB).
    """
    try:
        conteudo_bytes = await file.read()
        conteudo_texto = conteudo_bytes.decode("utf-8")
        return use_cases.indexar_documento(file.filename, conteudo_texto)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")

@router.delete("/api/v1/documents/{doc_id}")
def delete_document(
    doc_id: str,
    use_cases: DocumentUseCases = Depends(get_document_use_cases)
):
    """
    Remove um documento da base do RAG (ChromaDB) pelo ID.
    """
    try:
        return use_cases.remover_documento(doc_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover o documento: {str(e)}")

@router.get("/api/v1/documents")
def list_documents(
    use_cases: DocumentUseCases = Depends(get_document_use_cases)
):
    """
    Lista todos os documentos atualmente indexados no RAG.
    """
    try:
        return use_cases.listar_documentos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")
