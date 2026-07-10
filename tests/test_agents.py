from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from langchain_core.messages import AIMessage, HumanMessage

# Import the agent module (conftest.py mock imports are triggered automatically)
from app.agents import graph_agent

# Replace LLM instances with AsyncMock to prevent real API calls
mock_llm = AsyncMock()
mock_llm_with_tools = AsyncMock()

graph_agent.llm = mock_llm
graph_agent.llm_with_tools = mock_llm_with_tools

@pytest.fixture(autouse=True)
def reset_mocks():
    mock_llm.reset_mock()
    mock_llm_with_tools.reset_mock()

@pytest.mark.asyncio
async def test_no_analisar_intencao():
    # Arrange
    state = {
        "ticket_id": "TK-TEST-01",
        "pergunta": "minha conta bloqueou",
        "messages": []
    }
    
    # Configura o retorno do mock do LLM
    json_output = '{"intencao": "conta bloqueada", "keyword": "bloqueada"}'
    mock_llm.ainvoke.return_value = AIMessage(content=json_output)

    # Act
    resultado = await graph_agent.no_analisar_intencao(state)

    # Assert
    assert resultado["pergunta_otimizada"] == json_output
    mock_llm.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_no_gerar_resposta_direct_answer():
    # Arrange
    state = {
        "ticket_id": "TK-TEST-02",
        "pergunta": "qual o SLA de reembolso?",
        "contexto_encontrado": "O SLA de reembolso é de 5 dias úteis.",
        "messages": []
    }
    
    expected_response = "De acordo com nossa política, o prazo para reembolso é de 5 dias úteis."
    mock_llm_with_tools.ainvoke.return_value = AIMessage(content=expected_response)

    # Act
    resultado = await graph_agent.no_gerar_resposta(state)

    # Assert
    assert resultado["resposta_final"] == expected_response
    assert len(resultado["messages"]) == 1
    assert resultado["messages"][0].content == expected_response
    mock_llm_with_tools.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_no_gerar_resposta_tool_call():
    # Arrange
    state = {
        "ticket_id": "TK-TEST-03",
        "pergunta": "desbloqueie minha conta email@teste.com",
        "contexto_encontrado": "Políticas de bloqueio...",
        "messages": []
    }
    
    # Mock return value to trigger a tool call
    mock_tool_call = {
        "name": "get_user_status",
        "args": {"email": "email@teste.com"},
        "id": "call_123"
    }
    aimsg = AIMessage(content="", tool_calls=[mock_tool_call])
    mock_llm_with_tools.ainvoke.return_value = aimsg

    # Act
    resultado = await graph_agent.no_gerar_resposta(state)

    # Assert
    assert len(resultado["messages"]) == 1
    assert resultado["messages"][0].tool_calls[0]["name"] == "get_user_status"
    mock_llm_with_tools.ainvoke.assert_called_once()
