from fastapi import HTTPException
from typing import Any

class BaseCustomException(HTTPException):
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)

class FileOperationError(BaseCustomException):
    def __init__(self, detail: str):
        super().__init__(detail=f"File operation failed: {detail}")

class DataProcessingError(BaseCustomException):
    def __init__(self, detail: str):
        super().__init__(detail=f"Data processing failed: {detail}")

class CodeGenerationError(BaseCustomException):
    def __init__(self, detail: str):
        super().__init__(detail=f"Code generation failed: {detail}")

class CodeExecutionError(BaseCustomException):
    def __init__(self, detail: str):
        super().__init__(detail=f"Code execution failed: {detail}")

class PDFGenerationError(BaseCustomException):
    def __init__(self, detail: str):
        super().__init__(detail=f"PDF generation failed: {detail}")

class ValidationError(BaseCustomException):
    def __init__(self, detail: str):
        super().__init__(detail=f"Validation error: {detail}", status_code=400)