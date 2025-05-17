from fastapi import APIRouter, HTTPException
from app.models.chat import ChatMessageRequest, ChatMessageResponse
from app.services.meta_service import meta_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/send_message", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest):
    """
    Endpoint de ejemplo para interactuar directamente con el LLM (sin pasar por Meta).
    Útil para pruebas.
    """
    logger.info(f"Mensaje recibido en /send_message para user {request.user_id}: {request.message}")
    try:
        # reply = await llm_service.generate_response(request.message, request.user_id)
        await meta_service.send_whatsapp_message(
            to_phone_number=request.user_id, message_text=request.message
        )
        return ChatMessageResponse(user_id=request.user_id, reply=request.message)
    except Exception as e:
        logger.error(f"Error en /send_message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar el mensaje.")