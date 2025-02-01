# services/analysis/code_fixer.py
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from core.config.settings import get_settings
from core.config.paths import path_config
from core.logging.logger import get_logger, log_execution
from domain.exceptions.custom import CodeExecutionError, CodeGenerationError

logger = get_logger(__name__)

class CodeFixer:
    def __init__(self):
        settings = get_settings()
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL_NAME,
            convert_system_message_to_human=True,
            **settings.MODEL_SETTINGS
        )
        self._setup_prompt()
    
    def _setup_prompt(self):
        """Set up the code fixing prompt"""
        self.fix_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a Python code correction expert. Fix the code based on the error message.
            Use these EXACT paths for saving files:
            Graphs: {path_config.GRAPHS_DIR}
            Stats: {path_config.STATS_DIR}
            
            Rules:
            1. Return ONLY the corrected code
            2. Preserve all original imports and path configurations
            3. Keep the original structure and comments
            4. Fix ALL potential issues
            5. Handle edge cases and add error handling
            6. DO NOT include ```python``` markers
            7. Use os.path.join for ALL file paths
            8. Add error handling around file operations
            9. Ensure plt.savefig uses the full path with os.path.join
            10. Ensure JSON stats are saved with full path using os.path.join
            """),
            ("human", """Original code:
            {code}
            
            Error message:
            {error}
            
            Expected output files:
            {expected_files}
            
            Please provide the corrected code.""")
        ])
        self.chain = self.fix_prompt | self.llm

    def _clean_code_formatting(self, code: str) -> str:
        """Clean formatting from generated code"""
        try:
            cleaned = re.sub(r'```python\s*|\s*```', '', code)
            if match := re.search(r'exec\("""(.*?)"""\)', cleaned, re.DOTALL):
                return match.group(1).strip()
            return cleaned
        except Exception as e:
            raise CodeGenerationError(str(e))

    def _get_expected_files(self, code: str) -> List[Dict[str, str]]:
        """Extract expected output files from code"""
        expected_files = []
        for line in code.split('\n'):
            if line.startswith('# Output:'):
                filename = line.split('Output:')[1].strip()
                expected_files.append({
                    'graph': str(path_config.GRAPHS_DIR / filename),
                    'stats': str(path_config.STATS_DIR / f"{Path(filename).stem}_stats.json")
                })
        return expected_files

    def _verify_files(self, expected_files: List[Dict[str, str]]) -> tuple[bool, List[str]]:
        """Verify that all expected files exist"""
        missing_files = []
        for file_pair in expected_files:
            if not os.path.exists(file_pair['graph']):
                missing_files.append(file_pair['graph'])
            if not os.path.exists(file_pair['stats']):
                missing_files.append(file_pair['stats'])
        return len(missing_files) == 0, missing_files

    def _cleanup_partial_files(self):
        """Clean up any partially generated files"""
        try:
            for file in path_config.GRAPHS_DIR.glob('*.png'):
                file.unlink()
            
            for file in path_config.STATS_DIR.glob('*_stats.json'):
                file.unlink()
            
            logger.info("Cleaned up partial execution files")
        except Exception as e:
            logger.error(f"Error cleaning up files: {str(e)}")

    @log_execution
    def fix_code(self, code_path: Path = None, error_msg: str = None, max_attempts: int = 3) -> Dict[str, Any]:
        """Fix code with retries"""
        if code_path is None:
            code_path = path_config.CODE_DIR / "generated_analysis_code.py"

        attempt = 0
        while attempt < max_attempts:
            try:
                with open(code_path, 'r') as f:
                    code = f.read()
                
                expected_files = self._get_expected_files(code)
                
                if attempt > 0:
                    self._cleanup_partial_files()
                
                # Generate fix
                response = self.chain.invoke({
                    "code": code,
                    "error": error_msg or "Code execution failed",
                    "expected_files": expected_files
                })
                
                fixed_code = self._clean_code_formatting(response.content)
                
                with open(code_path, 'w') as f:
                    f.write(fixed_code)
                
                logger.info(f"Applied fix attempt {attempt + 1}")
                return {"status": "success", "output": "Code fixed successfully"}
                
            except Exception as e:
                attempt += 1
                if attempt == max_attempts:
                    raise CodeExecutionError(f"Failed to fix code after {max_attempts} attempts: {str(e)}")
                logger.warning(f"Fix attempt {attempt} failed: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff