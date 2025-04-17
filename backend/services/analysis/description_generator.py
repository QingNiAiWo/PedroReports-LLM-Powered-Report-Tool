import json
import re
import time
import io
import os
from typing import Dict, Optional, List
from PIL import Image
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAI
from langchain.schema.messages import HumanMessage
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from core.config.settings import get_settings
from core.config.paths import path_config
from core.logging.logger import get_logger, log_execution
from domain.exceptions.custom import DataProcessingError

logger = get_logger(__name__)

# DescriptionGenerator类：自动化图表解读生成器，结合图像和统计数据，生成专业分析解读
class DescriptionGenerator:
    def __init__(self, batch_size: int = 1, min_delay: float = 3.0):
        # 构造函数，初始化生成器，设置批量处理参数和API密钥
        try:
            settings = get_settings()  # 获取全局配置（如API密钥、模型名等）
            
            # 显式设置Google API密钥，供大模型调用
            os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
            
            # 初始化大模型（如Gemini），用于后续AI分析
            self.llm = GoogleGenerativeAI(
                model=settings.GEMINI_MODEL_NAME,
                google_api_key=settings.GOOGLE_API_KEY, 
                **settings.MODEL_SETTINGS
            )
            # 设置批处理参数和分析模板
            self._setup_parameters(batch_size, min_delay)
            self._setup_analysis_template()
            
            logger.info("DescriptionGenerator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DescriptionGenerator: {str(e)}")
            # 初始化失败时抛出自定义异常
            raise DataProcessingError(str(e))
    
    def _setup_parameters(self, batch_size: int, min_delay: float):
        """Set up processing parameters"""
        # 设置批量处理相关参数
        self.batch_size = batch_size  # 每批处理的图表数量
        self.min_delay = min_delay    # 每次API调用之间的最小延迟（秒）
        self.last_api_call = 0        # 上一次API调用的时间戳
        
        # 图像优化参数，控制图片大小和质量，避免API超限
        self.max_image_size = (500, 500)  # 图片最大宽高（像素）
        self.image_quality = 50           # 图片初始压缩质量（0-100）
        self.max_image_size_kb = 100      # 图片最大体积（KB）
    
    def _setup_analysis_template(self):
        """Set up the analysis template"""
        # 设定大模型分析时的统一模板，要求输出结构化JSON，便于后续自动解析
        self.analysis_template = """Analyze this visualization and statistical data to provide a comprehensive professional analysis. Consider ALL aspects of the data:

1. All the Statistics Related to features involved in graph are provided in the prompt.
2. Try to answer the analysis question asked, with the help of provided statistics and visually analyzing graph.
3. Use the statistical data provided to support your analysis.
4. Analyze the provided data as if you are a Professional Data Scientist, try to cover all aspects.        

Format your response in the following JSON structure:

{
    "sections": [
        {
            "title": "Clear and Professional Title based on Analysis",
            "heading": "Analysis Overview",
            "content": "Comprehensive answer incorporating statistical findings",
            "data_points": [
                {
                    "metric": "Statistical measure name",
                    "value": "Numerical or categorical result",
                    "significance": "Business and statistical importance"
                }
            ]
        },
        {
            "heading": "Statistical Evidence",
            "content": "Detailed statistical interpretation",
            "calculations": [
                {
                    "name": "Statistical measure",
                    "value": "Calculated result",
                    "interpretation": "Clear explanation of meaning"
                }
            ]
        },
        {
            "heading": "Conclusions and Recommendations",
            "content": "Overall conclusions from analysis",
            "key_conclusions": [
                {
                    "finding": "Key insight",
                    "impact": "Business/analytical impact",
                    "recommendation": "Actionable suggestion"
                }
            ],
            "limitations": [
                "Analysis limitations or caveats"
            ],
            "next_steps": [
                "Recommended actions"
            ]
        }
    ]
}"""
    
    def _optimize_image(self, image_data: bytes) -> bytes:
        """Optimize image for processing"""
        # 图像优化，压缩图片以便大模型处理，避免超出API限制
        try:
            image = Image.open(io.BytesIO(image_data))  # 从二进制数据读取图片
            
            # 如果图片有透明通道（RGBA），转为白底RGB
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            
            width, height = image.size
            # 如果图片尺寸超限，缩放到最大尺寸
            if width > self.max_image_size[0] or height > self.max_image_size[1]:
                image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
            
            quality = self.image_quality
            # 循环降低图片质量，直到体积小于最大限制
            while quality >= 40:
                output_buffer = io.BytesIO()
                image.save(output_buffer, 
                         format='JPEG', 
                         quality=quality, 
                         optimize=True)
                size_kb = len(output_buffer.getvalue()) / 1024
                
                if size_kb <= self.max_image_size_kb:
                    break
                    
                quality -= 5
            
            optimized_data = output_buffer.getvalue()  # 得到优化后的图片二进制数据
            logger.info(f"Image optimized from {len(image_data)/1024:.1f}KB to {len(optimized_data)/1024:.1f}KB")
            
            return optimized_data
        except Exception as e:
            logger.error(f"Image optimization failed: {str(e)}")
            # 优化失败时返回原始图片数据，保证流程不中断
            return image_data

    def _clean_json_string(self, text: str) -> Optional[str]:
        """Clean and validate JSON string"""
        # 清理和校验大模型返回的JSON字符串，保证能被json.loads解析
        try:
            # 用正则提取第一个大括号包裹的内容
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group(0)
                # 去除换行，避免格式问题
                json_str = json_str.replace('\n', ' ')
                # 修正部分格式问题
                json_str = re.sub(r'(\w)"(\w)', r'\1"\2', json_str)
                json_str = re.sub(r',\s*}', '}', json_str)
                return json_str
            return None
        except Exception as e:
            logger.error(f"Failed to clean JSON string: {str(e)}")
            raise DataProcessingError(str(e))

    def _rate_limit_api_call(self):
        """Implement rate limiting for API calls"""
        # 控制API调用频率，防止超限或被封禁
        current_time = time.time()  # 当前时间戳
        time_since_last_call = current_time - self.last_api_call  # 距离上次调用的间隔
        
        if time_since_last_call < self.min_delay:
            sleep_time = self.min_delay - time_since_last_call
            time.sleep(sleep_time)  # 如果间隔太短则等待
        
        self.last_api_call = time.time()  # 更新上次调用时间

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        retry=retry_if_exception_type((Exception,))
    )
    def _make_api_call(self, message: HumanMessage) -> str:
        """Make API call with retry logic"""
        # 调用大模型API，自动重试机制，防止偶发性网络或服务错误
        self._rate_limit_api_call()  # 先做频率控制
        try:
            return self.llm.invoke([message])  # 实际调用大模型API
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            # 如果遇到超时等问题，适当增加延迟
            if "deadline" in str(e).lower():
                self.min_delay += 1
            raise

    def _load_stats_data(self, stats_path: Path) -> Dict:
        """Load and validate stats data from file"""
        # 加载并校验统计数据（json文件），返回字典
        try:
            with open(stats_path, 'r') as f:
                stats_data = json.load(f)
            
            # 校验结构，必须是字典
            if not isinstance(stats_data, dict):
                raise DataProcessingError("Invalid stats data format")
            
            return stats_data
        except Exception as e:
            logger.error(f"Failed to load stats data from {stats_path}: {str(e)}")
            raise DataProcessingError(f"Failed to load stats data: {str(e)}")

    @log_execution
    def _process_single_graph(self, graph_path: Path, stats_path: Path) -> Dict:
        """Process a single graph with error handling"""
        # 处理单个图表，生成AI解读，返回结构化结果
        try:
            # 读取并优化图片，准备传给大模型
            with open(graph_path, "rb") as img_file:
                image_data = img_file.read()
            optimized_image_data = self._optimize_image(image_data)
            
            # 读取并校验统计数据，准备传给大模型
            stats_data = self._load_stats_data(stats_path)
            
            # 构建大模型输入prompt，包含统计数据和分析模板
            prompt = f"""Statistical Data:
    {json.dumps(stats_data, indent=2)}

    {self.analysis_template}"""

            # 构造消息，包含文本和图片，传递给大模型
            message = HumanMessage(content=[
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image",
                    "image_data": optimized_image_data
                }
            ])

            # 调用大模型并处理返回，得到AI分析结果
            response = self._make_api_call(message)
            cleaned_json = self._clean_json_string(response)
            
            if not cleaned_json:
                # 如果AI返回内容无法解析为JSON，抛出异常
                raise DataProcessingError("Failed to generate valid analysis")
                
            output_data = {
                "graph_name": graph_path.name,  # 图表文件名
                "question": stats_data.get('question', 'Analyze the visualization'),  # 分析问题
                "stats_file": stats_path.name,  # 统计数据文件名
                "sections": json.loads(cleaned_json).get("sections", [])  # 结构化分析内容
            }
            
            # 保存分析结果到json文件，便于后续报告生成
            json_path = path_config.DESCRIPTION_DIR / f"{graph_path.stem}.json"
            with open(json_path, "w", encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Generated description for {graph_path}")
            # 返回本次分析的所有关键信息
            return {
                "graph_path": str(graph_path),   # 图表路径
                "stats_path": str(stats_path),   # 统计数据路径
                "json_path": str(json_path),     # 生成的解读json路径
                "content": output_data           # 结构化分析内容
            }
                
        except Exception as e:
            logger.error(f"Failed to process graph {graph_path}: {str(e)}")
            # 发生异常时返回错误信息和图表路径
            return {"error": str(e), "graph_path": str(graph_path)}

    @log_execution
    def generate_description(self, graph_paths: List[str]) -> List[Dict]:
        """Generate descriptions for multiple graphs"""
        # 批量处理多个图表，生成AI解读，返回所有成功的结果
        try:
            results = []  # 用于收集所有结果
            # 分批处理，支持大批量任务，防止API超限
            for i in range(0, len(graph_paths), self.batch_size):
                batch = graph_paths[i:i + self.batch_size]  # 当前批次的图表路径
                batch_results = []
                
                for graph_path in batch:
                    graph_path = Path(graph_path)
                    graph_base = graph_path.stem
                    
                    # 查找匹配的统计文件，通常以图表名为前缀
                    analysis_prefix = '_'.join(graph_base.split('_')[:-1])
                    matching_stats = list(path_config.STATS_DIR.glob(
                        f"{analysis_prefix}*_stats.json"
                    ))
                    
                    if not matching_stats:
                        logger.error(f"No matching stats file found for graph {graph_path.name}")
                        continue
                    
                    # 按创建时间排序，取最新的统计文件，保证分析和图表一一对应
                    stats_path = sorted(
                        matching_stats,
                        key=lambda x: x.stat().st_ctime
                    )[-1]
                    
                    # 处理单个图表，生成AI解读
                    result = self._process_single_graph(graph_path, stats_path)
                    batch_results.append(result)
                    time.sleep(self.min_delay)  # 控制API调用频率
                
                results.extend(batch_results)
                
                # 批次间延迟，进一步防止API限流
                if i + self.batch_size < len(graph_paths):
                    logger.info("Adding delay between batches")
                    time.sleep(self.min_delay * 2)
            
            # 过滤出成功和失败的结果，便于后续处理
            successful_results = [r for r in results if 'error' not in r]
            errors = [r for r in results if 'error' in r]
            
            # 记录所有失败的任务，便于排查
            for error in errors:
                logger.error(f"Failed to process {error['graph_path']}: {error['error']}")
            
            logger.info(f"Successfully processed {len(successful_results)} out of {len(graph_paths)} graphs")
            # 返回所有成功的结构化分析结果
            return successful_results
                
        except Exception as e:
            logger.error(f"Failed to generate descriptions: {str(e)}")
            raise DataProcessingError(str(e))

# 入口函数：批量生成所有图表的AI解读

def generate_descriptions() -> List[Dict]:
    """Main function to generate descriptions"""
    # 该函数为整个流程的入口，自动处理所有图表，生成AI解读
    try:
        logger.info("Starting graph analysis...")
        generator = DescriptionGenerator(batch_size=1, min_delay=3.0)  # 实例化生成器
        
        # 获取所有图表文件路径，通常为png图片
        graph_paths = list(path_config.GRAPHS_DIR.glob('*.png'))
        
        if not graph_paths:
            logger.error("No graphs found for analysis")
            return []
        
        # 批量生成所有图表的AI解读
        results = generator.generate_description([str(p) for p in graph_paths])
        logger.info(f"Completed processing {len(results)} graphs successfully")
        return results
        
    except Exception as e:
        logger.error(f"Failed to generate descriptions: {str(e)}")
        raise DataProcessingError(str(e))