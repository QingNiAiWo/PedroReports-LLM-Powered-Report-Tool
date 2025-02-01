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

class CodeExecutor:
    def __init__(self):
        self.code_fixer = CodeFixer()
    
    @log_execution
    def cleanup_previous_files(self):
        """Clean up any previous output files"""
        try:
            # Clean up graphs directory
            for file in os.listdir(path_config.GRAPHS_DIR):
                if file.endswith('.png'):
                    (path_config.GRAPHS_DIR / file).unlink()
                    
            # Clean up stats directory
            for file in os.listdir(path_config.STATS_DIR):
                if file.endswith('_stats.json'):
                    (path_config.STATS_DIR / file).unlink()
                    
            logger.info("Successfully cleaned up previous files")
        except Exception as e:
            logger.error(f"Failed to cleanup files: {str(e)}")
            raise FileOperationError(str(e))
    
    def _verify_outputs(self) -> bool:
        """Verify that output files were generated"""
        graph_files = list(path_config.GRAPHS_DIR.glob('*.png'))
        stats_files = list(path_config.STATS_DIR.glob('*_stats.json'))
        
        if not graph_files or not stats_files:
            logger.error(f"Graphs directory contents: {list(path_config.GRAPHS_DIR.iterdir())}")
            logger.error(f"Stats directory contents: {list(path_config.STATS_DIR.iterdir())}")
            return False
        return True
    
    @log_execution
    def execute_code(self) -> Dict[str, Any]:
        """Execute the generated code with error handling and retries"""
        try:
            code_path = path_config.CODE_DIR / "generated_analysis_code.py"
            
            if not code_path.exists():
                raise CodeExecutionError(f"Code file not found: {code_path}")
            
            # Clean up any previous output files
            self.cleanup_previous_files()
            
            # Preprocess the code to handle numpy types
            try:
                process_generated_code(str(code_path))
                logger.info("Successfully preprocessed generated code")
            except Exception as e:
                logger.error(f"Failed to preprocess code: {str(e)}")
                raise CodeExecutionError(f"Code preprocessing failed: {str(e)}")
            
            # Set up environment variables
            env = os.environ.copy()
            env['PYTHONPATH'] = str(path_config.BASE_DIR)
            
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"Executing code from: {code_path}")
            
            try:
                # Execute the preprocessed code
                result = subprocess.run(
                    [sys.executable, str(code_path)],
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=str(path_config.BASE_DIR)
                )
                
                # Log the output
                if result.stdout:
                    logger.info(f"Code output: {result.stdout}")
                if result.stderr:
                    logger.error(f"Code errors: {result.stderr}")
                
                # If execution failed, try to fix the code
                if result.returncode != 0:
                    logger.warning("Initial execution failed. Attempting to fix code...")
                    fix_result = self.code_fixer.fix_code()
                    
                    if fix_result["status"] != "success":
                        raise CodeExecutionError("Code fixing failed")
                    
                    result.returncode = 0
                    result.stdout = fix_result["output"]
                    result.stderr = ""
            
            except Exception as e:
                raise CodeExecutionError(f"Code execution failed: {str(e)}")
            
            # Wait a moment for file system
            time.sleep(1)
            
            # Verify outputs
            if not self._verify_outputs():
                raise CodeExecutionError("No output files were generated")
            
            # Get list of generated files
            graph_files = [f.name for f in path_config.GRAPHS_DIR.glob('*.png')]
            
            logger.info("Code execution completed successfully")
            return {
                "status": "success",
                "output": result.stdout,
                "code_file": code_path.name,
                "generated_files": graph_files
            }

        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            raise CodeExecutionError(str(e))