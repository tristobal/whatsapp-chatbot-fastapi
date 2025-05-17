import pytest
from fastapi.testclient import TestClient
from app.main import app # Asegúrate que la app se pueda importar
from app.core.config import Settings, settings as app_settings
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde un .env.test si existe, o .env
# Esto es para asegurar que los tests usen una configuración controlada
# y no la de producción accidentalmente.
@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    # Intenta cargar .env.test primero, si no, .env
    # En un CI, las variables se suelen setear directamente.
    if os.path.exists(".env.test"):
        load_dotenv(".env.test", override=True)
    else:
        load_dotenv(".env", override=True)


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    # Aquí puedes sobreescribir settings para los tests si es necesario
    # Por ejemplo, usar un META_VERIFY_TOKEN específico para tests.
    # Asegúrate que las variables necesarias estén en tu .env o .env.test
    # o seteadas en el entorno de CI.
    return Settings(
        META_VERIFY_TOKEN=os.getenv("META_VERIFY_TOKEN", "test_token"),
        META_ACCESS_TOKEN=os.getenv("META_ACCESS_TOKEN", "test_access_token"),
        WHATSAPP_PHONE_NUMBER_ID=os.getenv("WHATSAPP_PHONE_NUMBER_ID", "test_phone_id"),
        GROQ_API_KEY=os.getenv("GROQ_API_KEY", "test_groq_key_dummy") # Importante si no mockeas Groq
    )

@pytest.fixture(scope="function") # 'function' scope para TestClient para aislar tests
def client(test_settings) -> TestClient:
    # Sobrescribir las settings de la app con las de test
    # Esto es un poco hacky; una mejor forma sería usar dependencias de FastAPI para settings.
    # Pero para simplicidad en el esqueleto:
    original_settings = app_settings.__dict__.copy()
    app_settings.__dict__.update(test_settings.model_dump())
    
    with TestClient(app) as c:
        yield c
    
    # Restaurar settings originales
    app_settings.__dict__.clear()
    app_settings.__dict__.update(original_settings)

# Fixture para mockear httpx (usando respx)
@pytest.fixture
async def mocked_httpx_router(test_settings):
    from respx import MockRouter
    router = MockRouter(assert_all_called=False) # False para no fallar si no todas las rutas mockeadas son llamadas

    # Mock para enviar mensajes de WhatsApp
    meta_api_version = "v19.0" # Debe coincidir con http_client.py
    meta_graph_url = f"https://graph.facebook.com/{meta_api_version}/{test_settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    router.post(meta_graph_url).respond(json={"message_id": "mocked_message_id"})
    
    yield router