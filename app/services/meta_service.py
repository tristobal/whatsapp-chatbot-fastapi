from typing import Any, Dict

import httpx
from app.core.config import settings
from app.models.meta import MetaMessageText, MetaMessageResponse
from app.services.llm_service import llm_service
from app.utils.http_client import meta_http_client # Usar el cliente HTTP configurado
from app.utils.logging import logger

class MetaService:
    async def process_webhook_message(self, payload: Dict[str, Any]) -> None:
        """
        Procesa un mensaje entrante de WhatsApp.
        Extrae el mensaje del usuario, obtiene una respuesta del LLM y la envía de vuelta.
        """
        try:
            if payload.get("object") != "whatsapp_business_account":
                logger.warning("Object 'whatsapp_business_account' not found")
                return

            # Generador para extraer mensajes de texto relevantes
            text_messages = (
                msg
                for entry in payload.get("entry", [])
                for change in entry.get("changes", [])
                for msg in change.get("value", {}).get("messages", [])
                if msg.get("type") == "text"
            )

            for message_data in text_messages:
                user_phone_number = message_data["from"]
                user_message_text = message_data["text"]["body"]
                message_id = message_data["id"]

                logger.info(f"Mensaje recibido de {user_phone_number} (ID: {message_id}): {user_message_text}")

                # Obtener y enviar respuesta
                bot_reply = await llm_service.generate_response(user_message_text, user_id=user_phone_number)
                await self.send_whatsapp_message(user_phone_number, bot_reply)
        except Exception as e:
            logger.error(f"Error procesando el webhook de Meta: {e}", exc_info=True)
            # Considerar enviar un mensaje de error genérico al usuario si es apropiado y posible


    async def send_whatsapp_message(self, to_phone_number: str, message_text: str) -> None:
        """
        Envía un mensaje de texto a un usuario de WhatsApp a través de la API de Meta.
        """
        if not settings.WHATSAPP_PHONE_NUMBER_ID or not settings.WHATSAPP_VERIFY_TOKEN:
            logger.error("WHATSAPP_PHONE_NUMBER_ID o WHATSAPP_VERIFY_TOKEN no configurados.")
            return

        url_endpoint = f"/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        message_payload = MetaMessageResponse(
            to=to_phone_number,
            text=MetaMessageText(body=message_text)
        )
        
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        try:
            response = await meta_http_client.post(
                url_endpoint,
                json=message_payload.model_dump(by_alias=True),
                headers=headers
            )
            response.raise_for_status()
            logger.info(f"Mensaje enviado a {to_phone_number}: {message_text[:50]}... Respuesta API: {response.json()}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP al enviar mensaje a {to_phone_number}: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Error genérico al enviar mensaje a {to_phone_number}: {e}")

meta_service = MetaService()