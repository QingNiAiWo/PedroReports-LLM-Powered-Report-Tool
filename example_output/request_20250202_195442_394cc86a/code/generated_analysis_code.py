import json  # 导入标准库json，用于数据的序列化和反序列化
import numpy as np  # 导入numpy库，用于数值计算和数组操作
import pandas as pd  # 导入pandas库，用于数据处理和分析

# 自定义JSON编码器，确保Numpy和Pandas类型能被正确序列化为JSON
class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        # 针对不同Numpy类型做类型转换，保证能被json序列化
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)  # 转为Python内置int
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)  # 转为Python内置float
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()  # 转为列表
        elif isinstance(obj, (pd.Series, pd.DataFrame)):
            return obj.to_dict()  # 转为字典
        return super().default(obj)  # 其他类型用父类默认方法

# ========== 第一组分析 ========== #
# Question 0: What is the distribution of Diabetes Pedigree Function across different outcome groups, and how does it relate to the number of pregnancies?
# Output: diabetes_pedigree_distribution.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns  # 导入所需的所有库
sns.set()  # 设置seaborn默认主题
plt.ioff()  # 关闭matplotlib的交互模式，防止阻塞

# 目录常量，指定输出文件保存位置
RESPONSE_DIR = r"/home/bob/Projects/PedroReports/backend/response"  # 响应主目录
STATS_DIR = r"/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/stats"  # 统计结果目录
GRAPHS_DIR = r"/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/graphs"  # 图表目录

data_path = "/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/data/Healthcare-Diabetes.csv"  # 数据文件路径

base_name = "diabetes_pedigree_distribution"  # 基础文件名
# 图表和统计结果的完整文件路径
graph_file = os.path.join(GRAPHS_DIR, f"{base_name}.png")  # 图表文件路径
stats_file = os.path.join(STATS_DIR, f"{base_name}_stats.json")  # 统计结果文件路径

# 计算基础统计量（均值、中位数、众数）
def calculate_stats(data):
    """Calculates basic descriptive statistics."""
    # data: 一维Series或数组
    return {
        "mean": np.mean(data).round(4),  # 均值，保留4位小数
        "median": np.median(data).round(4),  # 中位数
        "mode": float(np.round(np.bincount(data.astype(int)).argmax(),4)) if len(data)>0 else None  # 众数
    }

# 创建可视化并保存统计结果
# 该函数会对数据进行预处理、异常值处理、绘图和统计分析
# 并将结果保存为图片和JSON文件

def create_visualization_and_stats(df):
    """Creates visualization and saves statistics."""

    # 数据预处理：去除缺失值和重复值，类型转换
    df = df.dropna()  # 删除所有包含缺失值的行
    df = df.drop_duplicates()  # 删除重复行
    # 明确指定每一列的数据类型，保证后续分析和绘图不会报错
    df = df.astype({"Pregnancies": int, "Glucose": int, "BloodPressure": int, "SkinThickness": int, "Insulin": int, "BMI": float, "DiabetesPedigreeFunction": float, "Age": int, "Outcome": int})
    
    # 异常值处理：用IQR方法剔除极端值，防止极端值影响统计和可视化
    for col in ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']:
        Q1 = df[col].quantile(0.25)  # 第一四分位数
        Q3 = df[col].quantile(0.75)  # 第三四分位数
        IQR = Q3 - Q1  # 四分位距
        lower_bound = Q1 - 1.5 * IQR  # 下界
        upper_bound = Q3 + 1.5 * IQR  # 上界
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]  # 只保留正常范围内的数据

    # 绘制箱线图，展示不同Outcome组的DiabetesPedigreeFunction分布，并用怀孕次数分色
    plt.figure(figsize=(10, 6))  # 设置画布大小
    sns.boxplot(x="Outcome", y="DiabetesPedigreeFunction", hue="Pregnancies", data=df)  # 箱线图
    plt.title("Distribution of Diabetes Pedigree Function across Outcome Groups")  # 标题
    plt.xlabel("Outcome (0: No Diabetes, 1: Diabetes)")  # x轴标签
    plt.ylabel("Diabetes Pedigree Function")  # y轴标签
    plt.grid(True)  # 显示网格
    plt.savefig(graph_file)  # 保存图片到指定路径
    plt.close()  # 关闭画布，释放内存

    # 统计分析：分别统计Outcome=0和1组的DPF和怀孕次数
    stats = {
        "question": "What is the distribution of Diabetes Pedigree Function across different outcome groups, and how does it relate to the number of pregnancies?",  # 问题描述
        "additional_metrics": {},  # 可扩展的附加指标
        "outcome_0": {
            "DiabetesPedigreeFunction": calculate_stats(df[df["Outcome"] == 0]["DiabetesPedigreeFunction"]),  # Outcome=0组的DPF统计
            "Pregnancies": calculate_stats(df[df["Outcome"] == 0]["Pregnancies"])  # Outcome=0组的怀孕次数统计
        },
        "outcome_1": {
            "DiabetesPedigreeFunction": calculate_stats(df[df["Outcome"] == 1]["DiabetesPedigreeFunction"]),  # Outcome=1组的DPF统计
            "Pregnancies": calculate_stats(df[df["Outcome"] == 1]["Pregnancies"])  # Outcome=1组的怀孕次数统计
        }
    }

    # 保存统计结果到JSON文件
    os.makedirs(STATS_DIR, exist_ok=True)  # 确保统计目录存在
    os.makedirs(GRAPHS_DIR, exist_ok=True)  # 确保图表目录存在
    with open(stats_file, "w") as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)  # 用自定义encoder保存为JSON

# 主流程：读取数据，调用分析和可视化函数，异常处理
try:
    df = pd.read_csv(data_path)  # 读取CSV数据为DataFrame
    if df.empty:
        raise ValueError("Empty dataframe")  # 如果数据为空，抛出异常
    create_visualization_and_stats(df)  # 调用分析和可视化函数
    print(f"Visualization and stats saved to {GRAPHS_DIR} and {STATS_DIR}")  # 打印成功信息

except FileNotFoundError:
    print(f"Error: File not found at {data_path}")  # 文件未找到异常
except pd.errors.EmptyDataError:
    print(f"Error: Data file is empty at {data_path}")  # 文件内容为空异常
except ValueError as e:
    print(f"Error: {e}")  # 其他值错误
except Exception as e:
    print(f"An unexpected error occurred: {e}")  # 其他未知异常

# ========== 第二组分析 ========== #
# Question 1: How does Blood Glucose Level and BMI correlate with Diabetes Outcome, and what patterns emerge across different age groups?
# Output: diabetes_correlation_analysis.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns  # 再次导入所有库（自动生成代码常见）
sns.set()  # 设置seaborn默认主题
plt.ioff()  # 关闭matplotlib的交互模式

RESPONSE_DIR = r"/home/bob/Projects/PedroReports/backend/response"  # 响应主目录
STATS_DIR = r"/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/stats"  # 统计结果目录
GRAPHS_DIR = r"/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/graphs"  # 图表目录

data_path = "/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/data/Healthcare-Diabetes.csv"  # 数据文件路径

base_name = "diabetes_correlation_analysis"  # 基础文件名
graph_file = os.path.join(GRAPHS_DIR, f"{base_name}.png")  # 图表文件路径
stats_file = os.path.join(STATS_DIR, f"{base_name}_stats.json")  # 统计结果文件路径

# 保存统计结果到文件

def save_stats(stats, filename):
    try:
        with open(filename, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)  # 用自定义encoder保存为JSON
    except (IOError, OSError) as e:
        print(f"Error saving stats to {filename}: {e}")  # 文件写入异常

# 进行数据分析和可视化

def perform_analysis(df):
    # 数据预处理：去除无关列、缺失值、类型转换、去重
    df = df.drop(columns=['Id'], errors='ignore')  # 删除无关列Id
    df = df.dropna()  # 删除缺失值
    df = df.astype({'Pregnancies': int, 'Glucose': int, 'BloodPressure': int, 'SkinThickness': int, 'Insulin': int, 'BMI': float, 'DiabetesPedigreeFunction': float, 'Age': int, 'Outcome': int})  # 类型转换
    df = df.drop_duplicates()  # 删除重复行

    # 异常值处理（IQR方法）
    for col in ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']:
        Q1 = np.percentile(df[col], 25)  # 第一四分位数
        Q3 = np.percentile(df[col], 75)  # 第三四分位数
        IQR = Q3 - Q1  # 四分位距
        lower_bound = Q1 - 1.5 * IQR  # 下界
        upper_bound = Q3 + 1.5 * IQR  # 上界
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]  # 只保留正常范围内的数据

    # 统计分析：分别统计各列的均值、中位数、众数
    stats = {
        "question": "How does Blood Glucose Level and BMI correlate with Diabetes Outcome, and what patterns emerge across different age groups?",  # 问题描述
        "additional_metrics": {},  # 可扩展的附加指标
        "columns": {
            "Glucose": {
                "mean": np.round(np.mean(df["Glucose"]), 4),  # 均值
                "median": np.round(np.median(df["Glucose"]), 4),  # 中位数
                "mode": np.round(float(df["Glucose"].mode()[0]),4) if not df["Glucose"].mode().empty else None  # 众数
            },
            "BMI": {
                "mean": np.round(np.mean(df["BMI"]), 4),
                "median": np.round(np.median(df["BMI"]), 4),
                "mode": np.round(float(df["BMI"].mode()[0]),4) if not df["BMI"].mode().empty else None
            },
            "Age": {
                "mean": np.round(np.mean(df["Age"]), 4),
                "median": np.round(np.median(df["Age"]), 4),
                "mode": np.round(float(df["Age"].mode()[0]),4) if not df["Age"].mode().empty else None
            },
            "Outcome": {
                "mean": np.round(np.mean(df["Outcome"]), 4),
                "median": np.round(np.median(df["Outcome"]), 4),
                "mode": np.round(float(df["Outcome"].mode()[0]),4) if not df["Outcome"].mode().empty else None
            }
        }
    }

    # 可视化：绘制两个子图（散点图和箱线图）
    plt.figure(figsize=(12, 6))  # 设置画布大小
    plt.subplot(1, 2, 1)  # 第一个子图
    sns.scatterplot(x="Glucose", y="BMI", hue="Outcome", data=df)  # 散点图，颜色区分Outcome
    plt.title("Glucose vs BMI by Outcome")  # 标题
    plt.grid(True)  # 显示网格
    plt.subplot(1, 2, 2)  # 第二个子图
    sns.boxplot(x="Outcome", y="Age", data=df)  # 箱线图
    plt.title("Age Distribution by Outcome")  # 标题
    plt.grid(True)  # 显示网格
    plt.tight_layout()  # 自动调整子图间距
    plt.savefig(graph_file)  # 保存图片
    plt.close()  # 关闭画布

    return stats

# 主流程：读取数据，调用分析和可视化函数，异常处理
try:
    df = pd.read_csv(data_path)  # 读取CSV数据为DataFrame
    if df.empty:
        raise ValueError("Empty dataframe")  # 如果数据为空，抛出异常
    stats = perform_analysis(df)  # 调用分析和可视化函数
    save_stats(stats, stats_file)  # 保存统计结果
    print(f"Analysis complete. Stats saved to {stats_file}, graph saved to {graph_file}")  # 打印成功信息

except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError, ValueError) as e:
    print(f"Error during analysis: {e}")  # 处理常见异常，输出错误信息
except Exception as e:
    print(f"An unexpected error occurred: {e}")  # 处理其他未知异常

