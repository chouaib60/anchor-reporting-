from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class RaaSException(Exception):
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, details=None):
        super().__init__(message)
        self.message = message
        self.details = details

class TemplateNotFoundError(RaaSException):
    status_code = 404
    error_code = "TEMPLATE_NOT_FOUND"

class TemplateRenderError(RaaSException):
    status_code = 422
    error_code = "TEMPLATE_RENDER_ERROR"

class StorageError(RaaSException):
    status_code = 502
    error_code = "STORAGE_ERROR"

class JobNotFoundError(RaaSException):
    status_code = 404
    error_code = "JOB_NOT_FOUND"

class JobQueueFullError(RaaSException):
    status_code = 429
    error_code = "JOB_QUEUE_FULL"

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RaaSException)
    async def raas_handler(request: Request, exc: RaaSException):
        logger.warning("%s: %s", exc.error_code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.error_code, "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        logger.exception("Erreur non gérée sur %s", request.url)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "Une erreur interne est survenue."}},
        )