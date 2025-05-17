import pytest
from fastapi.testclient import TestClient
from app.core.config import settings # test_settings es inyectado por fixture
from unittest.mock import patch, AsyncMock

# Marcar todos los tests en este módulo como asyncio
pytestmark = pytest.mark.asyncio

def test_verify_webhook_success(client: TestClient, test_settings): # test_settings es inyectado
    params = {
        "hub.mode": "subscribe",
        "hub.challenge": "12345challenge",
        "hub.verify_token": test_settings.META_VERIFY_TOKEN # Usa el token de las settings de test
    }
    response = client.get(f"{settings.API_V1_STR}/meta/webhook", params=params)
    assert response.status_code == 200
    assert response.text == "12345challenge"

def test_verify_webhook_failure(client: TestClient):
    params = {
        "hub.mode": "subscribe",
        "hub.challenge": "12345challenge",
        "hub.verify_token": "wrong_token"
    }
    response = client.get(f"{settings.API_V1_STR}/meta/webhook", params=params)
    assert response.status_code == 403
    assert response.json() == {"detail": "Token de verificación inválido o modo incorrecto."}

async def test_receive_webhook_text_message(client: TestClient, mocked_httpx_router): # Se usa mocked_httpx_router
    # Simular un payload de mensaje de texto de WhatsApp
    # Este es un ejemplo muy simplificado, ajusta según la estructura real que esperas.
    sample_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "PHONE_NUMBER",
                        "phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID # Usa el de settings
                    },
                    "contacts": [{"profile": {"name": "Test User"}, "wa_id": "1234567890"}],
                    "messages": [{
                        "from": "1234567890", # Número del remitente
                        "id": "wamid.test_message_id",
                        "timestamp": "1600000000",
                        "text": {"body": "Hola bot"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    # Mockear el servicio LLM para que no haga una llamada real a Groq
    # y devuelva una respuesta predecible.
    # También mockear el cliente HTTP para la API de Meta.
    with patch('app.services.meta_service.llm_service.generate_response', AsyncMock(return_value="Hola! Soy el bot.")) as mock_llm_response, \
         mocked_httpx_router: # Activar el router mockeado de respx

        response = client.post(f"{settings.API_V1_STR}/meta/webhook", json=sample_payload)
        
        assert response.status_code == 200
        assert response.text == "EVENT_RECEIVED"
        
        # Verificar que el servicio LLM fue llamado con el mensaje correcto
        mock_llm_response.assert_called_once_with("Hola bot", user_id="1234567890")

        # Verificar que la llamada a la API de Meta (a través de httpx mockeado por respx) se hizo
        # Esto depende de cómo configures respx y qué assertions soporta.
        # Por ejemplo, podrías verificar que una ruta específica fue llamada.
        # El fixture mocked_httpx_router ya contiene el mock para el POST a Meta.
        # Si `assert_all_called=True` estuviera en respx, fallaría si no se llama.
        # Para ser más explícito:
        assert mocked_httpx_router["post", f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"].called


async def test_receive_webhook_unsupported_message_type(client: TestClient):
    sample_payload = { # Ejemplo de un tipo de mensaje no manejado (ej. audio)
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"value": {"messages": [{"type": "audio"}]}}]}]
    }
    # No esperamos que falle, solo que no haga ciertas acciones (como llamar al LLM)
    # Esto depende de la lógica en meta_service.py
    with patch('app.services.meta_service.llm_service.generate_response', AsyncMock()) as mock_llm_response, \
         patch('app.services.meta_service.MetaService.send_whatsapp_message', AsyncMock()) as mock_send_message:
        
        response = client.post(f"{settings.API_V1_STR}/meta/webhook", json=sample_payload)
        assert response.status_code == 200
        mock_llm_response.assert_not_called() # No debería llamar al LLM si el tipo no es 'text'
        mock_send_message.assert_not_called() # No debería intentar enviar respuesta