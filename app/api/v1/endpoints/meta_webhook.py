from fastapi import APIRouter, Request, Response, HTTPException, Query
from app.core.config import settings
from app.models.meta import MetaWebhookRequest, MetaWebhookChallengeQuery
from app.services.meta_service import meta_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/webhook")
async def verify_webhook(
    request: Request,
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
):
    """
    Endpoint para la verificación del Webhook de Meta.
    Meta envía una petición GET a esta URL cuando configuras el webhook.
    """
    # Validar con Pydantic model si se prefiere, aunque Query() ya hace algo de validación
    # query_params = MetaWebhookChallengeQuery(hub_mode=hub_mode, hub_challenge=hub_challenge, hub_verify_token=hub_verify_token)

    if hub_mode == "subscribe" and hub_verify_token == settings.META_VERIFY_TOKEN:
        logger.info("Webhook verificado exitosamente.")
        return Response(content=hub_challenge, media_type="text/plain")
    else:
        logger.warning(f"Fallo en la verificación del webhook. Modo: {hub_mode}, Token recibido: {hub_verify_token}")
        raise HTTPException(status_code=403, detail="Token de verificación inválido o modo incorrecto.")

@router.post("/webhook")
async def receive_webhook(request: Request):
    """
    Endpoint para recibir notificaciones de Meta (ej. nuevos mensajes).
    """
    try:
        payload_bytes = await request.body()
        payload_str = payload_bytes.decode('utf-8') # Para logging
        logger.debug(f"Payload crudo recibido en /webhook POST: {payload_str}")

        # Validar y parsear con Pydantic
        # Puede ser útil usar un try-except aquí si la estructura del payload varía mucho
        # o si Meta envía eventos que no mapeas completamente en tus modelos.
        # Por ahora, asumimos que MetaService manejará las variaciones internas.
        payload_json = await request.json()
        # validated_payload = MetaWebhookRequest(**payload_json) # Opcional si MetaService lo hace

    except Exception as e:
        logger.error(f"Error al leer/parsear el payload del webhook: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Payload inválido: {e}")

    # Procesar el mensaje en segundo plano para responder rápidamente a Meta
    # FastAPI ejecuta las funciones `async def` en un event loop,
    # así que `await meta_service.process_webhook_message` no bloqueará otras requests,
    # pero sí mantendrá esta request abierta hasta que termine.
    # Para tareas muy largas, se podría usar BackgroundTasks.
    # from fastapi import BackgroundTasks
    # async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    #    ...
    #    background_tasks.add_task(meta_service.process_webhook_message, payload_json)
    # Pero para un chatbot, la respuesta síncrona (dentro del mismo ciclo de request/response) es usualmente preferible
    # siempre que el LLM y otras llamadas no tarden demasiado.

    logger.info("Payload del webhook recibido, delegando a MetaService.")
    await meta_service.process_webhook_message(payload_json)
    
    return Response(status_code=200, content="EVENT_RECEIVED")