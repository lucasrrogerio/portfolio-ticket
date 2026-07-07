import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from rag_service import buscar_documentos_similares

# ==========================================
# 1. Configurações Iniciais e Carregamento
# ==========================================

# A chave da API deve vir das variáveis de ambiente em produção!
# Caso a variável não exista, você pode dar um valor padrão temporário para testes
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "SUA_CHAVE_AQUI")

llm = ChatOpenAI(
    api_key=MINIMAX_API_KEY, 
    base_url="https://api.minimax.io/v1", 
    model="Minimax-M3"
)

# Inicializa o modelo de embeddings (o mesmo usado no notebook)
# O cliente do ChromaDB e o modelo de embeddings foram movidos para o rag_service.py

# ==========================================
# 2. Definição do Estado e Nós do LangGraph
# ==========================================

class AgentState(TypedDict):
    pergunta: str
    contexto_encontrado: str
    resposta_final: str

def gera_prompt(contexto: str, pergunta: str):
    prompt = f"""
    Você é um agente de suporte de nível 1. Sua missão é responder às dúvidas dos clientes de forma educada.

    [REGRA DE OURO]
    Responder a pergunta do usuário baseando-se ÚNICA E EXCLUSIVAMENTE nos documentos do contexto abaixo.
    Se a resposta não estiver lá, diga que não tem a informação e que será necessário transferí-lo para um atendente.
    NÃO INVENTE NADA.

    [CONTEXTO DA EMPRESA]
    {contexto}
    
    [PERGUNTA DO CLIENTE]
    {pergunta}
    """
    return prompt

def no_buscar_documentos(state: AgentState):
    pergunta = state["pergunta"]
    
    contexto = buscar_documentos_similares(pergunta, n_results=1)
    return {"contexto_encontrado": contexto}

def no_gerar_resposta(state: AgentState):
    contexto = state["contexto_encontrado"]
    pergunta = state["pergunta"]

    prompt = gera_prompt(contexto, pergunta)
    resposta = llm.invoke(prompt)

    return {"resposta_final": resposta.content}

# ==========================================
# 3. Construção do Grafo
# ==========================================

workflow = StateGraph(AgentState)
workflow.add_node("bibliotecario", no_buscar_documentos)
workflow.add_node("atendente", no_gerar_resposta)

workflow.add_edge(START, "bibliotecario")
workflow.add_edge("bibliotecario", "atendente")
workflow.add_edge("atendente", END)

orquestrador = workflow.compile()

# ==========================================
# 4. Função Principal (Exposta para a API)
# ==========================================

def processar_ticket(texto_do_ticket: str) -> str:
    """
    Função de conveniência que a API irá chamar.
    Recebe o texto puro, monta o estado inicial e roda o grafo.
    """
    estado_inicial = {"pergunta": texto_do_ticket}
    resultado = orquestrador.invoke(estado_inicial)
    
    return resultado["resposta_final"]



