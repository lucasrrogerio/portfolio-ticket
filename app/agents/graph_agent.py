import os
import logging
import json
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from app.services.rag_service import buscar_documentos_similares, busca_hibrida
from opentelemetry import trace
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt.tool_node import ToolNode
from app.agents.tools import get_user_status, unlock_account, escalate_to_human, get_billing_history, process_refund
from app.agents.prompts import ANALISTA_PROMPT, ATENDENTE_SYSTEM_PROMPT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

tracer = trace.get_tracer("langgraph_agent")

# ==========================================
# 1. Configurações Iniciais e Carregamento
# ==========================================

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "SUA_CHAVE_AQUI")

llm = ChatOpenAI(
    api_key=MINIMAX_API_KEY, 
    base_url="https://api.minimax.io/v1", 
    model="Minimax-M2.7"
)

tools = [get_user_status, unlock_account, escalate_to_human, get_billing_history, process_refund]
llm_with_tools = llm.bind_tools(tools)

# ==========================================
# 2. Definição do Estado e Nós do LangGraph
# ==========================================

class AgentState(TypedDict):
    ticket_id: str
    pergunta: str
    pergunta_otimizada: str
    contexto_encontrado: str
    resposta_final: str
    messages: Annotated[list, add_messages]

async def no_analisar_intencao(state: AgentState):
    with tracer.start_as_current_span("no_analisar_intencao") as span:
        ticket_id = state.get("ticket_id", "N/A")
        span.set_attribute("ticket.id", ticket_id)
        logger.info(f"[Ticket: {ticket_id}] [Nó: Analista] Analisando intenção da pergunta.")
        pergunta = state["pergunta"]
        prompt = f"{ANALISTA_PROMPT}\n\nPergunta original do cliente: {pergunta}\nJSON:"
        
        resposta = await llm.ainvoke(prompt)
        logger.info(f"[Ticket: {ticket_id}] [Nó: Analista] Pergunta otimizada gerada com sucesso.")
        return {"pergunta_otimizada": resposta.content.strip()}

async def no_buscar_documentos(state: AgentState):
    with tracer.start_as_current_span("no_buscar_documentos") as span:
        ticket_id = state.get("ticket_id", "N/A")
        span.set_attribute("ticket.id", ticket_id)
        logger.info(f"[Ticket: {ticket_id}] [Nó: Bibliotecário] Buscando documentos no banco vetorial e BM25.")
        
        pergunta_busca_str = state.get("pergunta_otimizada", "{}")
        intencao = state["pergunta"]
        keyword = ""
        try:
            dados_busca = json.loads(pergunta_busca_str)
            intencao = dados_busca.get("intencao", state["pergunta"])
            keyword = dados_busca.get("keyword", "")
        except Exception as e:
            logger.warning(f"[Ticket: {ticket_id}] Erro ao dar parse no JSON do Analista: {e}. Usando texto puro.")
        
        contexto = busca_hibrida(intencao, keyword, n_results=3)
        logger.info(f"[Ticket: {ticket_id}] [Nó: Bibliotecário] Documentos recuperados com sucesso (Híbrida).")
        return {"contexto_encontrado": contexto}

async def no_gerar_resposta(state: AgentState):
    with tracer.start_as_current_span("no_gerar_resposta") as span:
        ticket_id = state.get("ticket_id", "N/A")
        span.set_attribute("ticket.id", ticket_id)
        
        messages = state.get("messages", [])
        if not messages:
            logger.info(f"[Ticket: {ticket_id}] [Nó: Atendente] Inicializando lista de mensagens.")
            contexto = state.get("contexto_encontrado", "")
            pergunta = state["pergunta"]
            
            system_prompt = ATENDENTE_SYSTEM_PROMPT.format(contexto=contexto)
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=pergunta)
            ]
        
        logger.info(f"[Ticket: {ticket_id}] [Nó: Atendente] Chamando LLM com {len(messages)} mensagens.")
        resposta = await llm_with_tools.ainvoke(messages)
        logger.info(f"[Ticket: {ticket_id}] [Nó: Atendente] Resposta recebida da LLM.")
        
        return {
            "messages": [resposta],
            "resposta_final": resposta.content
        }

# ==========================================
# 3. Construção do Grafo
# ==========================================

def should_continue(state: AgentState):
    messages = state.get("messages", [])
    if not messages:
        return "end"
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "end"

workflow = StateGraph(AgentState)
workflow.add_node("analista", no_analisar_intencao)
workflow.add_node("bibliotecario", no_buscar_documentos)
workflow.add_node("atendente", no_gerar_resposta)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "analista")
workflow.add_edge("analista", "bibliotecario")
workflow.add_edge("bibliotecario", "atendente")

workflow.add_conditional_edges(
    "atendente",
    should_continue,
    {
        "tools": "tools",
        "end": END
    }
)
workflow.add_edge("tools", "atendente")

orquestrador = workflow.compile()

# ==========================================
# 4. Função Principal (Exposta para a API)
# ==========================================

async def processar_ticket(ticket_id: str, texto_do_ticket: str) -> str:
    """
    Função de conveniência que a API irá chamar.
    Recebe o ticket_id e o texto puro, monta o estado inicial e roda o grafo de forma assíncrona.
    """
    logger.info(f"[Ticket: {ticket_id}] Iniciando processamento do ticket.")
    estado_inicial = {
        "ticket_id": ticket_id, 
        "pergunta": texto_do_ticket,
        "messages": []
    }
    resultado = await orquestrador.ainvoke(estado_inicial)
    
    logger.info(f"[Ticket: {ticket_id}] Processamento concluído.")
    return resultado["resposta_final"]
