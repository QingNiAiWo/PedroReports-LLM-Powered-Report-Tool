# api/middleware/logger.py
from fastapi import Request
import time
from core.logging.logger import get_logger

logger = get_logger(__name__)

async def log_request_middleware(request: Request, call_next):
    """Log request details and timing"""
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Calculate and log request duration
    duration = time.time() - start_time
    logger.info(f"Request completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Duration: {duration:.3f}s")
    
    return response