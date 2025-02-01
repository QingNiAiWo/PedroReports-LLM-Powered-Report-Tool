# api/middleware/__init__.py
from fastapi import FastAPI
from .cors import setup_cors
from .logger import log_request_middleware
from .error_handler import error_handler_middleware
from .authentication import api_key_middleware
from core.config.settings import get_settings, Settings

def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the application"""
    settings: Settings = get_settings()
    
    # Setup CORS
    setup_cors(app)
    
    # Add logging middleware
    app.middleware("http")(log_request_middleware)
    
    # Add error handling middleware
    app.middleware("http")(error_handler_middleware)
    
    if settings.ENVIRONMENT.lower() != "development":
        app.middleware("http")(api_key_middleware)