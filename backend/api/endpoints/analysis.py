# api/endpoints/analysis.py
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse
import os
from typing import Dict, Any
from datetime import datetime

from core.config.settings import get_settings, Settings
from core.config.paths import path_config
from core.logging.logger import get_logger
from core.request_handler import request_manager
from domain.models.requests import AnalysisRequest, AnalysisResponse
from domain.exceptions.custom import (
    FileOperationError,
    ValidationError,
)
from services.analysis.code_generator import CodeGenerator
from services.analysis.code_executor import CodeExecutor
from services.analysis.description_generator import generate_descriptions
from services.report.pdf_generator import generate_pdf

logger = get_logger(__name__)
router = APIRouter()

@router.post("/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Upload dataset for analysis"""
    try:
        # Create new request directory
        request_dir = request_manager.create_request_directory()
        path_config.set_request_directories(request_dir)
        
        # Save file to request-specific data directory
        file_path = path_config.DATA_DIR / file.filename
        logger.info(f"Saving file to: {file_path}")
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Set environment variable for data file path
        os.environ["DATA_FILE_PATH"] = str(file_path)
        
        logger.info(f"Successfully uploaded dataset: {file.filename}")
        return {
            "status": "success", 
            "filename": file.filename,
            "path": str(file_path)
        }
    except Exception as e:
        logger.error(f"Failed to upload dataset: {str(e)}")
        raise FileOperationError(str(e))

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(
    request: AnalysisRequest,
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Analyze dataset with provided questions"""
    logger.info(f"Analyzing data with questions: {request.questions}")
    
    if not os.environ.get("DATA_FILE_PATH") or not os.path.exists(os.environ["DATA_FILE_PATH"]):
        logger.error("No dataset uploaded or file not found")
        raise ValidationError("No dataset uploaded or file not found")
    
    try:
        # Get current request directory from path_config
        if not path_config.CURRENT_REQUEST_DIR:
            raise ValidationError("No active request session")
        
        # Extract request ID from directory name
        request_id = path_config.CURRENT_REQUEST_DIR.name
        logger.info(f"Processing request ID: {request_id}")
        
        # Step 1: Generate visualization code
        generator = CodeGenerator()
        code_result = generator.generate(request.questions)
        if code_result["status"] != "success":
            logger.error(f"Code generation failed: {code_result.get('message')}")
            raise ValidationError(code_result.get("message"))
        
        # Step 2: Execute generated code
        executor = CodeExecutor()
        execution_result = executor.execute_code()
        if execution_result["status"] != "success":
            logger.error(f"Code execution failed: {execution_result.get('message')}")
            raise ValidationError(execution_result.get("message"))
        
        # Step 3: Generate descriptions
        description_results = generate_descriptions()
        if not description_results:
            logger.error("Failed to generate descriptions")
            raise ValidationError("Failed to generate descriptions")
        
        # Step 4: Generate final PDF report with custom title
        pdf_path = generate_pdf(report_title=request.reportTitle)
        if not pdf_path:
            logger.error("Failed to generate PDF")
            raise ValidationError("Failed to generate PDF")
        
        logger.info("Analysis completed successfully")
        
        return {
            "status": "success",
            "message": "Analysis completed successfully",
            "request_id": request_id,
            "timestamp": datetime.now(),
            "details": {
                "visualizations": execution_result.get("generated_files", []),
                "descriptions": len(description_results),
                "pdf_path": os.path.basename(pdf_path)
            }
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise ValidationError(str(e))


@router.get("/get-pdf")
@router.get("/get-pdf/{request_id}")
async def get_pdf(
    request_id: str = None,
    settings: Settings = Depends(get_settings)
) -> FileResponse:
    """Get PDF report for specific request ID or most recent if not specified"""
    try:
        logger.info(f"Retrieving PDF{'for request ID: ' + request_id if request_id else ' (most recent)'}")
        
        if request_id:
            # If request ID provided, look in that specific directory
            request_dir = path_config.RESPONSE_DIR / request_id
            if not request_dir.exists():
                logger.error(f"Request directory not found: {request_dir}")
                raise ValidationError(f"Request not found: {request_id}")
        else:
            # Find the most recent request directory
            request_dirs = [d for d in path_config.RESPONSE_DIR.glob("request_*") if d.is_dir()]
            if not request_dirs:
                logger.error("No request directories found")
                raise ValidationError("No analysis results found")
            
            request_dir = max(request_dirs, key=os.path.getctime)
            logger.info(f"Using most recent request directory: {request_dir.name}")
        
        output_dir = request_dir / "output"
        if not output_dir.exists():
            logger.error(f"Output directory not found: {output_dir}")
            raise ValidationError("Output directory not found")
        
        # Find the PDF file
        pdf_files = list(output_dir.glob("*.pdf"))
        if not pdf_files:
            logger.error(f"No PDF files found in {output_dir}")
            raise ValidationError("No PDF files found")
        
        latest_pdf = max(pdf_files, key=os.path.getctime)
        logger.info(f"Found PDF file: {latest_pdf}")
        
        if not latest_pdf.exists():
            logger.error(f"PDF file not found: {latest_pdf}")
            raise ValidationError("PDF file not found")
        
        return FileResponse(
            path=str(latest_pdf),
            media_type="application/pdf",
            filename=latest_pdf.name
        )
    except Exception as e:
        logger.error(f"Error retrieving PDF: {str(e)}")
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(str(e))