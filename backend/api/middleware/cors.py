# api/middleware/cors.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config.settings import get_settings, Settings  

def setup_cors(app: FastAPI) -> None:
    """Setup CORS middleware with settings from config"""
    settings: Settings = get_settings()  
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )