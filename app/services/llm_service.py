from groq import Groq, AsyncGroq
from app.core.config import settings
from app.services.rag_interface import rag_service # Importa la instancia, no la clase
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GROQ_API_KEY no configurada.")
        self.client = AsyncGroq(api_key=api_key)
        # Podrías configurar el modelo aquí o pasarlo en cada llamada
        self.model = "llama3-8b-8192" # Ejemplo, verifica modelos disponibles en Groq

    async def generate_response(self, user_prompt: str, user_id: str) -> str:
        """
        Genera una respuesta usando el LLM, opcionalmente enriquecida con RAG.
        """
        context_str = ""
        try:
            # 1. (Futuro) Consultar base de conocimientos (RAG)
            # Descomentar y adaptar cuando Qdrant esté integrado
            # relevant_docs = await rag_service.search_knowledge_base(user_prompt)
            # if relevant_docs:
            #     context_items = [doc.get("payload", {}).get("text", "") for doc in relevant_docs]
            #     context_str = "\n\nContexto relevante:\n" + "\n".join(filter(None, context_items))
            #     logger.info(f"Contexto RAG para user {user_id}: {context_str}")
            pass # Placeholder para RAG
        except Exception as e:
            logger.error(f"Error al consultar RAG para user {user_id}: {e}")
            # Continuar sin contexto RAG si falla

        full_prompt = user_prompt
        if context_str:
             full_prompt = f"{context_str}\n\nBasándote en el contexto anterior si es relevante, y en tu conocimiento general, responde a la siguiente pregunta del usuario:\nUsuario: {user_prompt}"
        else:
            full_prompt = f"Usuario: {user_prompt}"


        system_message = "Eres un asistente virtual amigable y útil para WhatsApp."
        # Para modelos más recientes como Llama 3, es mejor usar solo `user` y `assistant` roles,
        # y el system prompt puede ir en el primer mensaje del `user` o en opciones de la API si lo soporta.
        # Groq podría tener una forma específica de pasar el system prompt, revisar su documentación.
        # Por ahora, lo incluimos en el primer mensaje del usuario o como una instrucción general.

        messages_payload = [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": full_prompt,
            }
        ]
        
        try:
            logger.info(f"Enviando a Groq para user {user_id}: Model={self.model}, Prompt='{full_prompt[:100]}...'")
            chat_completion = await self.client.chat.completions.create(
                messages=messages_payload,
                model=self.model,
                # temperature=0.7, # Opcional
                # max_tokens=1024, # Opcional
            )
            response_content = chat_completion.choices[0].message.content
            logger.info(f"Respuesta de Groq para user {user_id}: '{response_content[:100]}...'")
            return response_content
        except Exception as e:
            logger.error(f"Error al interactuar con Groq API para user {user_id}: {e}")
            return "Lo siento, no pude procesar tu solicitud en este momento."

llm_service = LLMService(api_key=settings.GROQ_API_KEY)