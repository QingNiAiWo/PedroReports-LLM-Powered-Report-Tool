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

# 自定义日志管理器，支持单例模式和多logger实例
class CustomLogger:
    _instance: Optional['CustomLogger'] = None  # 单例实例
    _loggers = {}  # 存储所有logger对象

    def __new__(cls):
        # 单例实现，保证全局只有一个CustomLogger实例
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # 日志文件目录
        self.log_dir = path_config.LOGS_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在
        
        # 文件日志格式（包含时间、模块名、级别、消息）
        self.file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        # 控制台日志格式（只显示级别和消息）
        self.console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )

    def get_logger(self, name: str) -> logging.Logger:
        # 获取指定名称的logger实例
        if name not in self._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)  # 默认日志级别为INFO
            
            # 清除已有的handler，避免重复输出
            logger.handlers.clear()
            
            # 文件日志handler，支持自动轮转（最大10MB，最多5个备份）
            file_handler = RotatingFileHandler(
                self.log_dir / "app.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(self.file_formatter)
            file_handler.setLevel(logging.INFO)
            
            # 控制台日志handler，输出到标准输出
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self.console_formatter)
            console_handler.setLevel(logging.INFO)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            self._loggers[name] = logger
        
        return self._loggers[name]

# 获取logger实例的全局方法，带缓存，避免重复创建
@lru_cache()
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name"""
    return CustomLogger().get_logger(name)

# 日志装饰器：自动记录函数执行、异常等信息
def log_execution(func: Callable) -> Callable:
    """Decorator to log function execution"""
    logger = get_logger(func.__module__)
    
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        # 异步函数的日志包装器
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
        # 同步函数的日志包装器
        logger.info(f"Executing {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Successfully executed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    # 根据函数是否为协程，返回对应的包装器
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper