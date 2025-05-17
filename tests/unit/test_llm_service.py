import pytest
from unittest.mock import AsyncMock, patch
from app.services.llm_service import LLMService
from app.core.config import settings # Importar settings para usar GROQ_API_KEY

# Marcar todos los tests en este módulo como asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def llm_service_instance():
    # Usar la GROQ_API_KEY de las settings (que puede ser una dummy para tests)
    return LLMService(api_key=settings.GROQ_API_KEY)

async def test_generate_response_success(llm_service_instance):
    # Mockear el cliente Groq dentro de LLMService
    mock_groq_client = AsyncMock()
    mock_chat_completion = AsyncMock()
    mock_chat_completion.choices = [AsyncMock()]
    mock_chat_completion.choices[0].message.content = "Hola, soy una respuesta mockeada de Groq."
    
    mock_groq_client.chat.completions.create = AsyncMock(return_value=mock_chat_completion)
    
    # Usar patch para reemplazar el cliente Groq real con el mock
    with patch.object(llm_service_instance, 'client', mock_groq_client):
        # Mockear también el servicio RAG para que no interfiera
        with patch('app.services.llm_service.rag_service.search_knowledge_base', AsyncMock(return_value=[])):
            response = await llm_service_instance.generate_response("Hola", "test_user_123")
            assert response == "Hola, soy una respuesta mockeada de Groq."
            llm_service_instance.client.chat.completions.create.assert_called_once()
            call_args = llm_service_instance.client.chat.completions.create.call_args
            assert call_args[1]['messages'][-1]['content'] == "Usuario: Hola" # O la prompt formateada

async def test_generate_response_groq_api_error(llm_service_instance):
    mock_groq_client = AsyncMock()
    mock_groq_client.chat.completions.create = AsyncMock(side_effect=Exception("Groq API Error"))

    with patch.object(llm_service_instance, 'client', mock_groq_client):
        with patch('app.services.llm_service.rag_service.search_knowledge_base', AsyncMock(return_value=[])):
            response = await llm_service_instance.generate_response("Hola", "test_user_456")
            assert response == "Lo siento, no pude procesar tu solicitud en este momento."

# Test para la lógica RAG (cuando esté más desarrollada)
async def test_generate_response_with_rag_context(llm_service_instance):
    mock_groq_client = AsyncMock()
    mock_chat_completion = AsyncMock()
    mock_chat_completion.choices = [AsyncMock()]
    mock_chat_completion.choices[0].message.content = "Respuesta con contexto RAG."
    mock_groq_client.chat.completions.create = AsyncMock(return_value=mock_chat_completion)

    # Simular que RAG devuelve contexto
    mock_rag_docs = [
        {"payload": {"text": "Contexto de prueba 1."}},
        {"payload": {"text": "Contexto de prueba 2."}}
    ]
    
    # NOTA: Para que este test pase, necesitas descomentar la lógica RAG en llm_service.py
    # y asegurarte que el mock de search_knowledge_base se llame correctamente.
    # Por ahora, como la lógica RAG está comentada, el contexto no se añadirá.
    # Para probarlo realmente, tendrías que adaptar el `expected_prompt_content`.
    
    # with patch.object(llm_service_instance, 'client', mock_groq_client), \
    #      patch('app.services.llm_service.rag_service.search_knowledge_base', AsyncMock(return_value=mock_rag_docs)) as mock_search_kb:
        
    #     response = await llm_service_instance.generate_response("Pregunta compleja", "test_user_789")
    #     assert response == "Respuesta con contexto RAG."
    #     mock_search_kb.assert_called_once_with("Pregunta compleja")
        
    #     call_args = llm_service_instance.client.chat.completions.create.call_args
    #     prompt_content = call_args[1]['messages'][-1]['content']
    #     assert "Contexto de prueba 1." in prompt_content
    #     assert "Contexto de prueba 2." in prompt_content
    #     assert "Pregunta compleja" in prompt_content
    pass # Dejar este test pendiente hasta que RAG esté activo