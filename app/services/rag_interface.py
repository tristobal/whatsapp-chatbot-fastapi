from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class RAGInterface(ABC):
    @abstractmethod
    async def search_knowledge_base(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Busca en la base de conocimientos (vectorial) información relevante para la consulta.
        Debería devolver una lista de documentos/chunks relevantes.
        """
        pass

    @abstractmethod
    async def add_document(self, document_text: str, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """
        Añade un documento a la base de conocimientos. (Opcional para este esqueleto)
        """
        pass

class QdrantRAGService(RAGInterface): # Ejemplo de futura implementación
    def __init__(self, qdrant_url: str, api_key: Optional[str] = None, collection_name: str = "whatsapp_kb"):
        # from qdrant_client import QdrantClient # Importaría aquí
        # self.client = QdrantClient(url=qdrant_url, api_key=api_key)
        # self.collection_name = collection_name
        # Aquí iría la inicialización del cliente Qdrant y la configuración de la colección.
        print(f"QdrantRAGService inicializado (simulado) para la colección: {collection_name} en {qdrant_url}")

    async def search_knowledge_base(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        # Aquí iría la lógica para vectorizar query_text y buscar en Qdrant
        print(f"Simulando búsqueda en Qdrant para: '{query_text}'")
        # Ejemplo de resultado simulado
        return [
            {"id": "doc1", "payload": {"text": "Información relevante 1 de Qdrant."}, "score": 0.9},
            {"id": "doc2", "payload": {"text": "Otro dato importante 2 de Qdrant."}, "score": 0.85},
        ]

        print(f"Simulando añadir documento a Qdrant: '{document_text[:50]}...'")
        return {"status": "simulated_add_success"}

# Por ahora, podríamos tener un RAG "dummy" o ninguno
class NoRAGService(RAGInterface):
    async def search_knowledge_base(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return [] # No devuelve contexto

    async def add_document(self, document_text: str, metadata: Optional[Dict[str, Any]] = None) -> Any:
        return {"status": "no_rag_service_active"}

# Instancia del servicio RAG (cambiar a QdrantRAGService cuando esté listo)
# rag_service: RAGInterface = QdrantRAGService(qdrant_url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
rag_service: RAGInterface = NoRAGService() # Usar este por ahora