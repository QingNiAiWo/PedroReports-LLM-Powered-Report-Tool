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

# 上传数据集API
@router.post("/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Upload dataset for analysis"""
    # 上传数据集文件，保存到后端指定目录，并设置环境变量
    try:
        # 创建新的请求目录（每次分析任务单独一个目录，便于隔离和追溯）
        request_dir = request_manager.create_request_directory()
        path_config.set_request_directories(request_dir)
        
        # 构造数据文件的保存路径（如 .../data/xxx.csv）
        file_path = path_config.DATA_DIR / file.filename
        logger.info(f"Saving file to: {file_path}")
        
        # 保存上传的文件内容到本地
        with open(file_path, "wb") as buffer:
            content = await file.read()  # 读取上传的全部内容
            buffer.write(content)
        
        # 设置环境变量，供后续分析流程读取数据文件
        os.environ["DATA_FILE_PATH"] = str(file_path)
        
        logger.info(f"Successfully uploaded dataset: {file.filename}")
        # 返回上传成功的状态、文件名和路径
        return {
            "status": "success", 
            "filename": file.filename,
            "path": str(file_path)
        }
    except Exception as e:
        logger.error(f"Failed to upload dataset: {str(e)}")
        # 上传失败时抛出自定义异常
        raise FileOperationError(str(e))

# 数据分析主API
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(
    request: AnalysisRequest,
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Analyze dataset with provided questions"""
    # 根据用户上传的数据和问题，自动完成分析、可视化、解读和报告生成
    logger.info(f"Analyzing data with questions: {request.questions}")
    
    # 检查数据文件路径是否存在，防止未上传数据直接分析
    if not os.environ.get("DATA_FILE_PATH") or not os.path.exists(os.environ["DATA_FILE_PATH"]):
        logger.error("No dataset uploaded or file not found")
        raise ValidationError("No dataset uploaded or file not found")
    
    try:
        # 获取当前请求目录，保证每次分析任务隔离
        if not path_config.CURRENT_REQUEST_DIR:
            raise ValidationError("No active request session")
        
        # 提取请求ID（目录名），用于后续追溯和文件定位
        request_id = path_config.CURRENT_REQUEST_DIR.name
        logger.info(f"Processing request ID: {request_id}")
        
        # 步骤1：自动生成可视化分析代码
        generator = CodeGenerator()
        code_result = generator.generate(request.questions)
        if code_result["status"] != "success":
            logger.error(f"Code generation failed: {code_result.get('message')}")
            raise ValidationError(code_result.get("message"))
        
        # 步骤2：执行自动生成的分析代码，生成图表和统计结果
        executor = CodeExecutor()
        execution_result = executor.execute_code()
        if execution_result["status"] != "success":
            logger.error(f"Code execution failed: {execution_result.get('message')}")
            raise ValidationError(execution_result.get("message"))
        
        # 步骤3：自动生成图表解读（AI分析）
        description_results = generate_descriptions()
        if not description_results:
            logger.error("Failed to generate descriptions")
            raise ValidationError("Failed to generate descriptions")
        
        # 步骤4：生成最终PDF报告，包含所有图表、统计和解读
        pdf_path = generate_pdf(report_title=request.reportTitle)
        if not pdf_path:
            logger.error("Failed to generate PDF")
            raise ValidationError("Failed to generate PDF")
        
        logger.info("Analysis completed successfully")
        
        # 返回分析结果，包含状态、请求ID、时间戳、可视化文件、解读数量、PDF路径等
        return {
            "status": "success",
            "message": "Analysis completed successfully",
            "request_id": request_id,
            "timestamp": datetime.now(),
            "details": {
                "visualizations": execution_result.get("generated_files", []),  # 生成的图表文件名列表
                "descriptions": len(description_results),                      # 生成的解读数量
                "pdf_path": os.path.basename(pdf_path)                         # 生成的PDF文件名
            }
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        # 捕获所有异常并抛出自定义异常
        raise ValidationError(str(e))

# 获取PDF报告API
@router.get("/get-pdf")
@router.get("/get-pdf/{request_id}")
async def get_pdf(
    request_id: str = None,
    settings: Settings = Depends(get_settings)
) -> FileResponse:
    """Get PDF report for specific request ID or most recent if not specified"""
    # 根据请求ID获取对应的PDF报告，如果未指定则获取最新的报告
    try:
        logger.info(f"Retrieving PDF{'for request ID: ' + request_id if request_id else ' (most recent)'}")
        
        if request_id:
            # 如果指定了请求ID，则查找对应目录
            request_dir = path_config.RESPONSE_DIR / request_id
            if not request_dir.exists():
                logger.error(f"Request directory not found: {request_dir}")
                raise ValidationError(f"Request not found: {request_id}")
        else:
            # 未指定请求ID，则查找最新的请求目录
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
        
        # 查找PDF文件（通常只有一个）
        pdf_files = list(output_dir.glob("*.pdf"))
        if not pdf_files:
            logger.error(f"No PDF files found in {output_dir}")
            raise ValidationError("No PDF files found")
        
        latest_pdf = max(pdf_files, key=os.path.getctime)
        logger.info(f"Found PDF file: {latest_pdf}")
        
        if not latest_pdf.exists():
            logger.error(f"PDF file not found: {latest_pdf}")
            raise ValidationError("PDF file not found")
        
        # 返回PDF文件，供前端下载
        return FileResponse(
            path=str(latest_pdf),
            media_type="application/pdf",
            filename=latest_pdf.name
        )
    except Exception as e:
        logger.error(f"Error retrieving PDF: {str(e)}")
        if isinstance(e, ValidationError):
            raise
        # 捕获所有异常并抛出自定义异常
        raise ValidationError(str(e))