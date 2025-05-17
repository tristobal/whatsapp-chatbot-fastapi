from pydantic import BaseModel

class ChatMessageRequest(BaseModel):
    user_id: str
    message: str

class ChatMessageResponse(BaseModel):
    user_id: str
    reply: str