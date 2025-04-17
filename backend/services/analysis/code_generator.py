import re
import os
import pandas as pd
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from .utils import load_schema
from core.config.settings import get_settings
from core.config.paths import path_config
from core.logging.logger import get_logger, log_execution
from domain.exceptions.custom import CodeGenerationError

logger = get_logger(__name__)

# 代码生成器：用于自动生成数据分析和可视化代码
class CodeGenerator:
    def __init__(self):
        # 获取全局配置
        settings = get_settings()
        # 响应目录路径
        self.response_dir = path_config.RESPONSE_DIR
        # 统计结果目录路径
        self.stats_dir = path_config.STATS_DIR
        # 图表目录路径
        self.graphs_dir = path_config.GRAPHS_DIR
        # 加载数据schema
        self.schema= load_schema()
        
        # 显式设置Google API密钥，供大模型调用
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
        
        # 初始化大模型（如Gemini）
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            convert_system_message_to_human=True,
            **settings.MODEL_SETTINGS
        )
        # 设置提示模板
        self._setup_prompt_template()
    
    def _setup_prompt_template(self):
        """Setup the code generation prompt template"""
        # 构建系统和用户提示，指导大模型如何生成代码
        self.code_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Generate data visualization and statistical analysis code using these imports:

import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"{self.response_dir}"
STATS_DIR = r"{self.stats_dir}"
GRAPHS_DIR = r"{self.graphs_dir}"

Please follow the correct JSON format for saving stats, as provided in template

Remember to:
1. I am Provding data_types of column, read that and perform appropriate analysis
2. Convert int32, int64, or float64 to Python's built-in int, which is JSON serializable
2. Use Numpy to Perform all Statistical Analysis
3. Always use this exact JSON structure and handle proper JSON serialization
4. Dont Perform unnecessary statistics analysis but keep only basic mean, meadian, mode for every column involved in questions 
5. Add relevant metrics to additional_metrics if needed
6. Format numbers appropriately (round to 4 decimal places)
7. Use os.path.join for file paths
8. Include proper error handling
9. Start Question numbering from 1

File naming:
- You MUST include the base_name variable and set it to a descriptive name for your analysis
- One graph (.png) and one stats (_stats.json) file per question
- Use descriptive names: <metric>_<analysis_type>
- Define filenames at start:
  base_name = "metric_analysis"
  graph_file = os.path.join(GRAPHS_DIR,base_name.png")
  stats_file = os.path.join(STATS_DIR, base_name_stats.json")

Remember to add the Question in the returned stats JSON file  
  
Data preprocessing:
- Drop irrelevant columns
- Handle missing values
- Convert data types
- Remove duplicates
- Handle outliers

Visualization:
- Use appropriate plot types
- Include title, labels, legend, and grid
- Enhance readability

Validation:
- Check data format and sufficiency
- Verify figure creation and readability
- Validate file paths and permissions

Input handling:
df = pd.read_csv(data_path)
if df.empty:
    raise ValueError("Empty dataframe")

Remember to close plots and clear memory when done."""),
            ("human", """Create visualization code for:
            Columns: {columns}
            Data: {head_data}
            Task: {question}
            Path: {data_path}
            """)
        ])
        # 组合提示模板和大模型，形成链式调用
        self.chain = self.code_prompt | self.llm

    @log_execution
    def remove_code_block_formatting(self, code: str) -> str:
        """Clean code formatting"""
        # 清理大模型返回的代码块格式，只保留纯代码
        try:
            # 去除markdown代码块标记
            cleaned = re.sub(r'```python\s*|\s*```', '', code)
            # 兼容特殊格式（如exec("""...""")）
            if match := re.search(r'exec\("""(.*?)"""\)', cleaned, re.DOTALL):
                return match.group(1).strip()
            return cleaned
        except Exception as e:
            # 捕获异常并抛出自定义异常
            raise CodeGenerationError(str(e))

    @log_execution
    def generate_code_for_question(self, question: str, columns: List[str], head_data: pd.DataFrame, data_path: str,d_types, schema) -> tuple[str, str]:
        """Generate code with schema example"""
        # 针对单个分析问题，生成数据分析和可视化代码
        try:   
            # 调用大模型生成代码
            response = self.chain.invoke({
                "columns": columns,
                "head_data": head_data,
                "question": question,
                "data_path": data_path,
                "data_type": d_types,
                "schema": schema
            })
            
            # 清理代码格式
            base_code = self.remove_code_block_formatting(response.content)
            
            # 用正则提取base_name变量，确定图表文件名
            filename_match = re.search(r'base_name\s*=\s*["\']([^"\']+)["\']', base_code)
            if not filename_match:
                # 如果未找到，抛出异常
                raise CodeGenerationError("Could not find base_name in generated code")
            
            filename = f"{filename_match.group(1)}.png"
            
            # 保证统计JSON中包含问题内容，替换json.dump的写法
            stats_save_pattern = r'json\.dump\((.*?),\s*f,\s*default=convert_to_serializable,\s*indent=4\)'
            modified_code = re.sub(
                stats_save_pattern,
                rf'json.dump({{\n    "question": """{question}""",\n    "analysis": \1}}, f, default=convert_to_serializable, indent=4)',
                base_code
            )
            
            # 返回生成的代码和图表文件名
            return modified_code, filename
        except Exception as e:
            # 捕获异常并抛出自定义异常
            raise CodeGenerationError(f"Failed to generate code: {str(e)}")
    

    @log_execution
    def save_generated_code(self, code: str) -> str:
        """Save generated code to file"""
        # 保存生成的分析代码到文件
        try:
            # 目标代码文件路径
            code_path = path_config.CODE_DIR / "generated_analysis_code.py"
            # 写入文件
            with open(code_path, 'w') as f:
                f.write(code)
            # 返回文件路径
            return str(code_path)
        except Exception as e:
            # 捕获异常并抛出自定义异常
            raise CodeGenerationError(f"Failed to save code: {str(e)}")

    @log_execution
    def generate(self, provided_questions: List[str] = None) -> Dict[str, Any]:
        """Main generation method"""
        # 主入口：根据用户提供的问题批量生成分析代码
        try:
            # 检查环境变量中是否有数据文件路径
            # 数据文件路径由前端上传数据后，后端设置到环境变量DATA_FILE_PATH中
            if not os.environ.get("DATA_FILE_PATH"):
                raise ValueError("No data file path provided")

            # 获取数据文件路径（如 /g:/Documents/PedroReports-LLM-Powered-Report-Tool/backend/user_uploads/diabetes.csv）
            data_path = os.environ["DATA_FILE_PATH"]
            # 读取数据文件，生成DataFrame对象
            df = pd.read_csv(data_path) 
            # 获取所有列名，便于后续生成代码时参考
            columns = df.columns.tolist()
            # 获取前5行数据样例，便于大模型理解数据结构
            head_data = df.head()
            # 获取每列数据类型，转为字符串，便于大模型判断分析方法
            d_types = df.dtypes.apply(lambda x: str(x)).to_dict()
            # 获取schema（预定义的数据结构约束）
            schema= self.schema
            
            generated_code = ""  # 用于存放所有生成的代码
            filenames = []        # 用于存放所有生成的图表文件名
            
            # 遍历每个分析问题，逐一生成代码和图表文件名
            for i, question in enumerate(provided_questions or []):
                code, filename = self.generate_code_for_question(
                    question, columns, head_data, data_path, d_types, schema
                )
                # 拼接注释、代码和文件名，便于后续追溯
                generated_code += f"# Question {i}: {question}\n# Output: {filename}\n{code}\n\n"
                filenames.append(filename)
                
            # 保存所有生成的代码到本地文件，供后续自动执行
            code_path = self.save_generated_code(generated_code)
        
            # 返回结果字典，供后续执行和报告生成使用
            # code: 所有自动生成的分析和可视化Python代码（字符串形式），包含每个问题的代码段
            # filenames: 一个列表，包含每个问题生成的图表文件名（如 ['glucose_analysis.png', ...]）
            # code_path: 生成的完整Python代码文件的路径（如 backend/services/analysis/generated_analysis_code.py）
            # status: 字符串，标记本次代码生成是否成功（一般为 'success'）
            return {
                "code": generated_code,      # 所有问题的完整Python代码
                "filenames": filenames,      # 每个问题生成的图表文件名
                "code_path": code_path,      # 代码文件的保存路径
                "status": "success"          # 状态标记
            }
        except Exception as e:
            # 记录错误日志并抛出自定义异常
            logger.error(f"Code generation failed: {str(e)}")
            raise CodeGenerationError(str(e))