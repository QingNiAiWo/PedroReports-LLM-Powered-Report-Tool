# api/middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from core.logging.logger import get_logger
from domain.exceptions.custom import (
    FileOperationError,
    DataProcessingError,
    CodeGenerationError,
    CodeExecutionError,
    PDFGenerationError,
    ValidationError
)

logger = get_logger(__name__)

async def error_handler_middleware(request: Request, call_next):
    """Global error handler middleware"""
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Error handling request: {str(e)}")
        return handle_exception(e)

def handle_exception(exc: Exception) -> JSONResponse:
    """Handle different types of exceptions"""
    if isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)}
        )
    elif isinstance(exc, (FileOperationError, DataProcessingError,
                         CodeGenerationError, CodeExecutionError,
                         PDFGenerationError)):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"}
        )