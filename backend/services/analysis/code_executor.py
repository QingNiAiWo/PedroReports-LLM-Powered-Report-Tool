# services/analysis/code_executor.py
import os
import sys
import subprocess
import time
from typing import Dict, Any

from core.config.paths import path_config
from .code_preprocessor import process_generated_code 
from core.logging.logger import get_logger, log_execution
from domain.exceptions.custom import CodeExecutionError, FileOperationError
from .code_fixer import CodeFixer

logger = get_logger(__name__)

# 代码执行器：用于自动执行生成的分析代码，并处理输出、异常和修复
class CodeExecutor:
    def __init__(self):
        # 初始化代码修复器（用于自动修复执行失败的代码）
        self.code_fixer = CodeFixer()
    
    @log_execution
    def cleanup_previous_files(self):
        """Clean up any previous output files"""
        # 清理上一次生成的所有输出文件，避免干扰本次执行
        try:
            # 清理图表目录下所有png图片
            for file in os.listdir(path_config.GRAPHS_DIR):
                if file.endswith('.png'):
                    (path_config.GRAPHS_DIR / file).unlink()
                    
            # 清理描述目录下所有json文件（新版约定）
            for file in os.listdir(path_config.DESCRIPTION_DIR):
                if file.endswith('.json'):
                    (path_config.DESCRIPTION_DIR / file).unlink()
                    
            # 清理统计目录下所有 _stats.json 文件
            for file in os.listdir(path_config.STATS_DIR):
                if file.endswith('_stats.json'):
                    (path_config.STATS_DIR / file).unlink()
                    
            logger.info("Successfully cleaned up previous files")
        except Exception as e:
            logger.error(f"Failed to cleanup files: {str(e)}")
            # 文件操作异常，抛出自定义异常
            raise FileOperationError(str(e))
    
    def _verify_outputs(self) -> bool:
        """Verify that output files were generated"""
        # 检查输出目录下是否生成了图表和统计文件
        graph_files = list(path_config.GRAPHS_DIR.glob('*.png'))
        stats_files = list(path_config.STATS_DIR.glob('*_stats.json'))
        
        if not graph_files or not stats_files:
            # 如果没有生成任何图表或统计文件，记录详细目录内容，便于排查
            logger.error(f"Graphs directory contents: {list(path_config.GRAPHS_DIR.iterdir())}")
            logger.error(f"Stats directory contents: {list(path_config.STATS_DIR.iterdir())}")
            return False
        return True
    
    @log_execution
    def execute_code(self) -> Dict[str, Any]:
        """Execute the generated code with error handling and retries"""
        # 执行自动生成的分析代码，自动处理异常和修复
        try:
            # 生成代码的路径（如 backend/services/analysis/generated_analysis_code.py）
            code_path = path_config.CODE_DIR / "generated_analysis_code.py"
            
            # 检查代码文件是否存在
            if not code_path.exists():
                raise CodeExecutionError(f"Code file not found: {code_path}")
            
            # 执行前先清理所有旧的输出文件
            self.cleanup_previous_files()
            
            # 预处理代码（如处理numpy类型等兼容性问题）
            try:
                process_generated_code(str(code_path))
                logger.info("Successfully preprocessed generated code")
            except Exception as e:
                logger.error(f"Failed to preprocess code: {str(e)}")
                raise CodeExecutionError(f"Code preprocessing failed: {str(e)}")
            
            # 设置环境变量，保证PYTHONPATH正确
            env = os.environ.copy()
            env['PYTHONPATH'] = str(path_config.BASE_DIR)
            
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"Executing code from: {code_path}")
            
            try:
                # 使用subprocess执行生成的python代码
                result = subprocess.run(
                    [sys.executable, str(code_path)],
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=str(path_config.BASE_DIR)
                )
                
                # 记录标准输出和错误输出
                if result.stdout:
                    logger.info(f"Code output: {result.stdout}")
                if result.stderr:
                    logger.error(f"Code errors: {result.stderr}")
                
                # 如果执行失败，尝试自动修复代码
                if result.returncode != 0:
                    logger.warning("Initial execution failed. Attempting to fix code...")
                    fix_result = self.code_fixer.fix_code()
                    
                    if fix_result["status"] != "success":
                        raise CodeExecutionError("Code fixing failed")
                    
                    result.returncode = 0
                    result.stdout = fix_result["output"]
                    result.stderr = ""
            
            except Exception as e:
                # 捕获执行异常，抛出自定义异常
                raise CodeExecutionError(f"Code execution failed: {str(e)}")
            
            # 等待1秒，确保文件系统写入完成
            time.sleep(1)
            
            # 检查是否生成了输出文件
            if not self._verify_outputs():
                raise CodeExecutionError("No output files were generated")
            
            # 获取所有生成的图表文件名
            graph_files = [f.name for f in path_config.GRAPHS_DIR.glob('*.png')]
            
            logger.info("Code execution completed successfully")
            # 返回结果字典
            # status: 执行状态（success或失败）
            # output: 代码执行的标准输出内容
            # code_file: 执行的代码文件名
            # generated_files: 生成的图表文件名列表
            return {
                "status": "success",
                "output": result.stdout,
                "code_file": code_path.name,
                "generated_files": graph_files
            }

        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            # 捕获所有异常并抛出自定义异常
            raise CodeExecutionError(str(e))