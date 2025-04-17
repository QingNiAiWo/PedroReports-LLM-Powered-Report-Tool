# core/request_handler.py
from pathlib import Path
import uuid
from datetime import datetime
from typing import Optional

from core.logging.logger import get_logger
from core.config.paths import path_config
from domain.exceptions.custom import FileOperationError

logger = get_logger(__name__)

# 请求目录管理器：用于为每次分析任务创建唯一的目录结构，隔离数据和结果
class RequestDirectoryManager:
    """Manages unique request directories for the analysis pipeline"""
    _instance: Optional['RequestDirectoryManager'] = None  # 单例实例
    
    def __new__(cls):
        # 单例实现，保证全局只有一个RequestDirectoryManager实例
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize with base response directory path"""
        # 设置基础响应目录（所有分析任务的根目录）
        self.base_response_dir = path_config.RESPONSE_DIR
        self.current_request_dir: Optional[Path] = None  # 当前活跃的请求目录
    
    def create_request_directory(self) -> Path:
        """Create a new unique request directory with subdirectories"""
        # 创建一个新的唯一请求目录，并自动创建所有子目录
        try:
            # 生成唯一目录名，包含时间戳和UUID片段，保证不重复
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            request_dir_name = f"request_{timestamp}_{unique_id}"
            
            # 创建主请求目录（如 .../response/request_20240601_123456_abcd1234）
            request_dir = self.base_response_dir / request_dir_name
            request_dir.mkdir(parents=True, exist_ok=True)
            
            # 需要创建的所有子目录（如graphs、stats、description、code、output、data等）
            subdirs = ['graphs', 'stats', 'description', 'code', 'output', 'data']  # Added 'data'
            for subdir in subdirs:
                subdir_path = request_dir / subdir
                subdir_path.mkdir(exist_ok=True)
                logger.info(f"Created subdirectory: {subdir_path}")
            
            # 记录当前活跃的请求目录
            self.current_request_dir = request_dir
            logger.info(f"Created request directory: {request_dir}")
            return request_dir
            
        except Exception as e:
            logger.error(f"Failed to create request directory: {str(e)}")
            # 目录创建失败时抛出自定义异常
            raise FileOperationError(str(e))
    
    def get_current_request_dir(self) -> Path:
        """Get the path of current request directory"""
        # 获取当前活跃的请求目录路径
        if not self.current_request_dir:
            raise FileOperationError("No active request directory")
        return self.current_request_dir
    
    def get_subdirectory(self, subdir_name: str) -> Path:
        """Get path for a specific subdirectory in current request directory"""
        # 获取当前请求目录下指定子目录的路径
        if not self.current_request_dir:
            raise FileOperationError("No active request directory")
        
        subdir_path = self.current_request_dir / subdir_name
        if not subdir_path.exists():
            raise FileOperationError(f"Subdirectory '{subdir_name}' does not exist")
        
        return subdir_path

# Create singleton instance
# 创建全局唯一的请求目录管理器实例，供全局调用
request_manager = RequestDirectoryManager()