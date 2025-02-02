
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

# Question 0: What is the distribution of Diabetes Pedigree Function across different outcome groups, and how does it relate to the number of pregnancies?
# Output: diabetes_pedigree_distribution.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"/home/bob/Projects/PedroReports/backend/response"
STATS_DIR = r"/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/stats"
GRAPHS_DIR = r"/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/graphs"

data_path = "/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/data/Healthcare-Diabetes.csv"

base_name = "diabetes_pedigree_distribution"
graph_file = os.path.join(GRAPHS_DIR, f"{base_name}.png")
stats_file = os.path.join(STATS_DIR, f"{base_name}_stats.json")


def calculate_stats(data):
    """Calculates basic descriptive statistics."""
    return {
        "mean": np.mean(data).round(4),
        "median": np.median(data).round(4),
        "mode": float(np.round(np.bincount(data.astype(int)).argmax(),4)) if len(data)>0 else None
    }


def create_visualization_and_stats(df):
    """Creates visualization and saves statistics."""

    #Preprocessing
    df = df.dropna()
    df = df.drop_duplicates()
    df = df.astype({"Pregnancies": int, "Glucose": int, "BloodPressure": int, "SkinThickness": int, "Insulin": int, "BMI": float, "DiabetesPedigreeFunction": float, "Age": int, "Outcome": int})
    
    #Handle Outliers (simple IQR method for demonstration.  More robust methods exist)
    for col in ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]


    #Visualization
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Outcome", y="DiabetesPedigreeFunction", hue="Pregnancies", data=df)
    plt.title("Distribution of Diabetes Pedigree Function across Outcome Groups")
    plt.xlabel("Outcome (0: No Diabetes, 1: Diabetes)")
    plt.ylabel("Diabetes Pedigree Function")
    plt.grid(True)
    plt.savefig(graph_file)
    plt.close()


    #Statistical Analysis
    stats = {
        "question": "What is the distribution of Diabetes Pedigree Function across different outcome groups, and how does it relate to the number of pregnancies?",
        "additional_metrics": {},
        "outcome_0": {
            "DiabetesPedigreeFunction": calculate_stats(df[df["Outcome"] == 0]["DiabetesPedigreeFunction"]),
            "Pregnancies": calculate_stats(df[df["Outcome"] == 0]["Pregnancies"])
        },
        "outcome_1": {
            "DiabetesPedigreeFunction": calculate_stats(df[df["Outcome"] == 1]["DiabetesPedigreeFunction"]),
            "Pregnancies": calculate_stats(df[df["Outcome"] == 1]["Pregnancies"])
        }
    }

    #Save Stats
    os.makedirs(STATS_DIR, exist_ok=True)
    os.makedirs(GRAPHS_DIR, exist_ok=True)
    with open(stats_file, "w") as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)


try:
    df = pd.read_csv(data_path)
    if df.empty:
        raise ValueError("Empty dataframe")
    create_visualization_and_stats(df)
    print(f"Visualization and stats saved to {GRAPHS_DIR} and {STATS_DIR}")

except FileNotFoundError:
    print(f"Error: File not found at {data_path}")
except pd.errors.EmptyDataError:
    print(f"Error: Data file is empty at {data_path}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# Question 1: How does Blood Glucose Level and BMI correlate with Diabetes Outcome, and what patterns emerge across different age groups?
# Output: diabetes_correlation_analysis.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"/home/bob/Projects/PedroReports/backend/response"
STATS_DIR = r"/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/stats"
GRAPHS_DIR = r"/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/graphs"

data_path = "/home/bob/Projects/PedroReports/backend/response/request_20250202_195442_394cc86a/data/Healthcare-Diabetes.csv"

base_name = "diabetes_correlation_analysis"
graph_file = os.path.join(GRAPHS_DIR, f"{base_name}.png")
stats_file = os.path.join(STATS_DIR, f"{base_name}_stats.json")


def save_stats(stats, filename):
    try:
        with open(filename, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except (IOError, OSError) as e:
        print(f"Error saving stats to {filename}: {e}")


def perform_analysis(df):
    # Data Preprocessing
    df = df.drop(columns=['Id'], errors='ignore')  # Drop irrelevant column
    df = df.dropna()  # Handle missing values (simple removal for this example)
    df = df.astype({'Pregnancies': int, 'Glucose': int, 'BloodPressure': int, 'SkinThickness': int, 'Insulin': int, 'BMI': float, 'DiabetesPedigreeFunction': float, 'Age': int, 'Outcome': int})
    df = df.drop_duplicates()

    # Outlier handling (simple IQR method for demonstration)
    for col in ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']:
        Q1 = np.percentile(df[col], 25)
        Q3 = np.percentile(df[col], 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]


    # Statistical Analysis using NumPy
    stats = {
        "question": "How does Blood Glucose Level and BMI correlate with Diabetes Outcome, and what patterns emerge across different age groups?",
        "additional_metrics": {},
        "columns": {
            "Glucose": {
                "mean": np.round(np.mean(df["Glucose"]), 4),
                "median": np.round(np.median(df["Glucose"]), 4),
                "mode": np.round(float(df["Glucose"].mode()[0]),4) if not df["Glucose"].mode().empty else None
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

    # Visualization
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.scatterplot(x="Glucose", y="BMI", hue="Outcome", data=df)
    plt.title("Glucose vs BMI by Outcome")
    plt.grid(True)
    plt.subplot(1, 2, 2)
    sns.boxplot(x="Outcome", y="Age", data=df)
    plt.title("Age Distribution by Outcome")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(graph_file)
    plt.close()

    return stats


try:
    df = pd.read_csv(data_path)
    if df.empty:
        raise ValueError("Empty dataframe")
    stats = perform_analysis(df)
    save_stats(stats, stats_file)
    print(f"Analysis complete. Stats saved to {stats_file}, graph saved to {graph_file}")

except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError, ValueError) as e:
    print(f"Error during analysis: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

