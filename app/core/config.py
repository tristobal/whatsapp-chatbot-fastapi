from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "WhatsApp Bot Microservice"
    API_V1_STR: str = "/api/v1"

    WHATSAPP_ACCESS_TOKEN: str
    WHATSAPP_VERIFY_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_API_VERSION: str

    GROQ_API_KEY: str
    GROQ_MODEL: str

    # QDRANT_URL: str | None = None # Para futura integración
    # QDRANT_API_KEY: str | None = None # Para futura integración

    LOG_LEVEL: str

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()