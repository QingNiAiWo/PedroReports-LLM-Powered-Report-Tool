def add_type_conversion_handling(code: str) -> str:
    """Add type conversion handling to generated code before execution."""
    # 定义类型转换工具代码，确保Numpy和Pandas类型能被JSON序列化
    type_conversion_code = '''
import json
import numpy as np
import pandas as pd

class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, (pd.Series, pd.DataFrame)):
            return obj.to_dict()
        return super().default(obj)

'''
    
    # 移除原代码中已存在的相关import，避免重复
    code_lines = code.split('\n')
    filtered_lines = []
    skip_imports = {'import json', 'import numpy as np', 'import pandas as pd'}
    
    for line in code_lines:
        if not any(imp in line for imp in skip_imports):
            filtered_lines.append(line)
    
    code = '\n'.join(filtered_lines)
    
    # 在代码开头插入类型转换工具代码
    code = type_conversion_code + code
    
    # 替换json.dump调用，强制使用自定义encoder
    import re
    json_dump_pattern = r'json\.dump\((.*?),\s*(.*?)(?:,\s*(?:default=[\w\._]+,\s*)?indent\s*=\s*(\d+))?\)'
    
    def replace_json_dump(match):
        obj, file_obj = match.group(1), match.group(2)
        indent = match.group(3) or '4'
        return f'json.dump({obj}, {file_obj}, cls=NumpyJSONEncoder, indent={indent})'
    
    code = re.sub(json_dump_pattern, replace_json_dump, code)
    
    return code

def process_generated_code(code_path: str) -> str:
    """Process the generated code file to add type conversion handling"""
    # 处理生成的代码文件，插入类型转换支持
    try:
        # 读取原始代码
        with open(code_path, 'r') as f:
            original_code = f.read()
        
        # 添加类型转换处理
        modified_code = add_type_conversion_handling(original_code)
        
        # 写回修改后的代码
        with open(code_path, 'w') as f:
            f.write(modified_code)
            
        return code_path
    except Exception as e:
        # 捕获异常并抛出运行时错误
        raise RuntimeError(f"Failed to process generated code: {str(e)}")