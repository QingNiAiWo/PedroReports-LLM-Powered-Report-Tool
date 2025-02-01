# core/request_handler.py
from pathlib import Path
import uuid
from datetime import datetime
from typing import Optional

from core.logging.logger import get_logger
from core.config.paths import path_config
from domain.exceptions.custom import FileOperationError

logger = get_logger(__name__)

class RequestDirectoryManager:
    """Manages unique request directories for the analysis pipeline"""
    _instance: Optional['RequestDirectoryManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize with base response directory path"""
        self.base_response_dir = path_config.RESPONSE_DIR
        self.current_request_dir: Optional[Path] = None
    
    def create_request_directory(self) -> Path:
        """Create a new unique request directory with subdirectories"""
        try:
            # Generate unique directory name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            request_dir_name = f"request_{timestamp}_{unique_id}"
            
            # Create main request directory
            request_dir = self.base_response_dir / request_dir_name
            request_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            subdirs = ['graphs', 'stats', 'description', 'code', 'output', 'data']  # Added 'data'
            for subdir in subdirs:
                subdir_path = request_dir / subdir
                subdir_path.mkdir(exist_ok=True)
                logger.info(f"Created subdirectory: {subdir_path}")
            
            self.current_request_dir = request_dir
            logger.info(f"Created request directory: {request_dir}")
            return request_dir
            
        except Exception as e:
            logger.error(f"Failed to create request directory: {str(e)}")
            raise FileOperationError(str(e))
    
    def get_current_request_dir(self) -> Path:
        """Get the path of current request directory"""
        if not self.current_request_dir:
            raise FileOperationError("No active request directory")
        return self.current_request_dir
    
    def get_subdirectory(self, subdir_name: str) -> Path:
        """Get path for a specific subdirectory in current request directory"""
        if not self.current_request_dir:
            raise FileOperationError("No active request directory")
        
        subdir_path = self.current_request_dir / subdir_name
        if not subdir_path.exists():
            raise FileOperationError(f"Subdirectory '{subdir_name}' does not exist")
        
        return subdir_path

# Create singleton instance
request_manager = RequestDirectoryManager()