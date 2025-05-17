import httpx
from app.core.config import settings
from typing import Any, Dict, Optional

class HttpClient:
    def __init__(self, base_url: str = ""):
        self.base_url = base_url

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            return await client.get(endpoint, params=params)

    async def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            return await client.post(endpoint, json=json, headers=headers)

meta_http_client = HttpClient(base_url=f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/")