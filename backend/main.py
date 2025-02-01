# main.py
from fastapi import FastAPI
from core.config.settings import get_settings
from core.config.constants import Environment
from core.logging.logger import get_logger, log_execution
from api import analysis_router
from api.middleware import setup_middleware

# Initialize settings and logging
settings = get_settings()
logger = get_logger(__name__)

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    docs_url = "/docs" if settings.ENVIRONMENT.lower() != Environment.PRODUCTION else None
    redoc_url = "/redoc" if settings.ENVIRONMENT.lower() != Environment.PRODUCTION else None
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Data Analysis API with automated visualization and reporting",
        docs_url=docs_url,
        redoc_url=redoc_url,
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Include router
    prefix = settings.API_V1_STR
    logger.info(f"Adding routes with prefix: {prefix}")
    app.include_router(
        analysis_router,
        prefix=prefix
    )
    
    return app

app = create_application()

@app.on_event("startup")
@log_execution
async def startup_event():
    """Log registered routes on startup"""
    routes = [
        f"{route.methods} {route.path}"
        for route in app.routes
        if hasattr(route, "methods")
    ]
    logger.info("Registered routes:")
    for route in routes:
        logger.info(f"  {route}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT.lower() == Environment.DEVELOPMENT
    )