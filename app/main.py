from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router_v1
import logging
import uvicorn

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

app.include_router(api_router_v1, prefix=settings.API_V1_STR)

# Para ejecutar directamente con uvicorn:
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)