from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.logging import setup_logging, get_logger
from core.errors import register_exception_handlers
from core.config import get_settings
from routers import health

settings = get_settings()
setup_logging(settings.log_level)
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Démarrage API", extra={"env": settings.app_env})
    yield
    logger.info("Arrêt API")

app = FastAPI(
    title="Report as a Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(health.router, prefix="/health", tags=["Health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)