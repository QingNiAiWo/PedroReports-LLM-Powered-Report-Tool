# api/middleware/authentication.py
from fastapi import Request, HTTPException, status, Response
from typing import Callable, Awaitable
from core.config.settings import get_settings, Settings
from core.logging.logger import get_logger

logger = get_logger(__name__)

async def api_key_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]  
) -> Response:
    """API key validation middleware"""
    settings: Settings = get_settings() 
    
    if settings.ENVIRONMENT.lower() == "development":
        return await call_next(request)
    
    if request.url.path in [
        "/docs",
        "/redoc",
        "/openapi.json",
        f"{settings.API_V1_STR}/health",
    ]:
        return await call_next(request)
    
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Missing API key",
                "message": "Please provide an API key using the X-API-Key header"
            }
        )
    
    if api_key != settings.API_KEY:
        logger.warning("Invalid API key provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Invalid API key",
                "message": "The provided API key is not valid"
            }
        )
    
    return await call_next(request)