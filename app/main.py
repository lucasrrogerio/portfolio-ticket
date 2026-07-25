from fastapi import FastAPI
from app.core.observability import setup_observability
from app.presentation.api.routes import router as api_router

# Instancia o servidor FastAPI
app = FastAPI(
    title="Serviço de IA - Ticket Triage",
    description="API que utiliza LangGraph e RAG para sugerir respostas aos chamados e gerenciar a base de conhecimento.",
    version="1.0.0"
)

# Configura observabilidade (Prometheus, OpenTelemetry e Loki)
setup_observability(app)

# Registra as rotas (Presentation Layer)
app.include_router(api_router)

# Ponto de entrada limpo. Toda a lógica de negócios e orquestração
# agora reside nas camadas de Use Cases e Infrastructure.
