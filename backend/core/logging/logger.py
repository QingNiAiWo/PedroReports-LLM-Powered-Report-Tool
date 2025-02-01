# core/logging/logger.py
import logging
import sys
from functools import lru_cache, wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Callable, Any
import asyncio

from core.config.paths import path_config
from core.config.constants import LogLevel

class CustomLogger:
    _instance: Optional['CustomLogger'] = None
    _loggers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.log_dir = path_config.LOGS_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )

    def get_logger(self, name: str) -> logging.Logger:
        if name not in self._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            
            # Clear existing handlers
            logger.handlers.clear()
            
            # File handler
            file_handler = RotatingFileHandler(
                self.log_dir / "app.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(self.file_formatter)
            file_handler.setLevel(logging.INFO)
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self.console_formatter)
            console_handler.setLevel(logging.INFO)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            self._loggers[name] = logger
        
        return self._loggers[name]

@lru_cache()
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name"""
    return CustomLogger().get_logger(name)

def log_execution(func: Callable) -> Callable:
    """Decorator to log function execution"""
    logger = get_logger(func.__module__)
    
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(f"Executing {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Successfully executed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(f"Executing {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Successfully executed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper