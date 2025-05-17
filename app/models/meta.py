from pydantic import BaseModel, Field
from typing import List, Optional

# Modelos para el webhook de Meta (simplificados)

class MetaMessageText(BaseModel):
    body: str

class MetaMessage(BaseModel):
    id: str
    from_number: str = Field(..., alias="from")
    timestamp: str
    text: Optional[MetaMessageText] = None
    type: str
    # Puedes añadir otros tipos de mensajes: image, audio, document, etc.

class MetaValue(BaseModel):
    messaging_product: str
    metadata: dict
    contacts: Optional[List[dict]] = None # Presente en mensajes entrantes
    messages: Optional[List[MetaMessage]] = None
    statuses: Optional[List[dict]] = None # Para actualizaciones de estado del mensaje

class MetaChange(BaseModel):
    value: MetaValue
    field: str

class MetaEntry(BaseModel):
    id: str
    changes: List[MetaChange]

class MetaWebhookRequest(BaseModel):
    object: str
    entry: List[MetaEntry]

class MetaMessageResponse(BaseModel):
    messaging_product: str = "whatsapp"
    to: str
    type: str = "text"
    text: MetaMessageText

class MetaWebhookChallengeQuery(BaseModel):
    hub_mode: str = Field(..., alias="hub.mode")
    hub_challenge: str = Field(..., alias="hub.challenge")
    hub_verify_token: str = Field(..., alias="hub.verify_token")