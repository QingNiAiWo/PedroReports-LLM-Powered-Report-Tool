import os

# 加载分析统计模板schema的工具函数

def load_schema():
    # 获取当前文件所在目录的绝对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接出stats_template.json的路径（相对路径转绝对路径）
    file_path = os.path.join(base_dir, "../../services/analysis/stats_template.json")  
    
    file_path = os.path.abspath(file_path) 
    print("Loading file from:", file_path) 

    # 读取模板文件内容并返回
    with open(file_path, "r") as f:
        return f.read()
