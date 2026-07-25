from app.domain.interfaces.agent_service import AgentService
from app.domain.interfaces.rag_repository import RAGRepository
from app.infrastructure.agents.langgraph_agent import LangGraphAgentService
from app.infrastructure.agents.agentscope_service import AgentScopeAgentService

class AgentServiceFactory:
    @staticmethod
    def get_agent_service(motor: str, rag_repository: RAGRepository) -> AgentService:
        """
        Retorna a implementação concreta do serviço de agente com base no motor desejado.
        """
        if motor == "agentscope":
            return AgentScopeAgentService(rag_repository=rag_repository)
        
        # Default fallback
        return LangGraphAgentService(rag_repository=rag_repository)
