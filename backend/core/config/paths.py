from pathlib import Path
from typing import Optional
from functools import lru_cache

class PathConfig:
    _instance: Optional['PathConfig'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize all directory paths"""
        self.BASE_DIR = Path(__file__).parent.parent.parent
        self.BACKEND_DIR = self.BASE_DIR
        self.RESPONSE_DIR = self.BACKEND_DIR / "response"
        self.LOGS_DIR = self.BACKEND_DIR / "logs"
        
        # Create base directories
        self._create_base_directories()
        
        # Initialize request-specific paths as None
        self.CURRENT_REQUEST_DIR = None
        self.GRAPHS_DIR = None
        self.STATS_DIR = None
        self.CODE_DIR = None
        self.DESCRIPTION_DIR = None
        self.OUTPUT_DIR = None
        self.DATA_DIR = None 
    
    def _create_base_directories(self):
        """Create base directories"""
        directories = [
            self.LOGS_DIR,
            self.RESPONSE_DIR
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def set_request_directories(self, request_dir: Path):
        """Set paths for request-specific directories"""
        self.CURRENT_REQUEST_DIR = request_dir
        self.GRAPHS_DIR = request_dir / "graphs"
        self.STATS_DIR = request_dir / "stats"
        self.CODE_DIR = request_dir / "code"
        self.DESCRIPTION_DIR = request_dir / "description"
        self.OUTPUT_DIR = request_dir / "output"
        self.DATA_DIR = request_dir / "data" 
        
        # Create request-specific directories
        for directory in [
            self.GRAPHS_DIR,
            self.STATS_DIR,
            self.CODE_DIR,
            self.DESCRIPTION_DIR,
            self.OUTPUT_DIR,
            self.DATA_DIR  
        ]:
            directory.mkdir(parents=True, exist_ok=True)

@lru_cache()
def get_path_config() -> PathConfig:
    """Get singleton instance of PathConfig"""
    return PathConfig()

path_config = get_path_config()