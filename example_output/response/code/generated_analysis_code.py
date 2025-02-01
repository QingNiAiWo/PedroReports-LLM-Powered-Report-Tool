
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

# Question 0: What is the distribution of BMI across different age groups, and how does it correlate with diabetes outcomes?
# Output: bmi_age_outcome_analysis.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"/home/bob/Projects/InsightFLow/backend/response"
STATS_DIR = r"/home/bob/Projects/InsightFLow/backend/response/request_20250201_225602_a54f8f07/stats"
GRAPHS_DIR = r"/home/bob/Projects/InsightFLow/backend/response/request_20250201_225602_a54f8f07/graphs"

data_path = "/home/bob/Projects/InsightFLow/backend/response/request_20250201_225602_a54f8f07/data/Healthcare-Diabetes.csv"

base_name = "bmi_age_outcome_analysis"
graph_file = os.path.join(GRAPHS_DIR, f"{base_name}.png")
stats_file = os.path.join(STATS_DIR, f"{base_name}_stats.json")


def perform_analysis(df):
    # Data Preprocessing
    df = df.drop(columns=['Id'], errors='ignore') #Drop Id column if exists
    df = df.dropna() #Handle missing values by dropping rows with NaN
    df = df.astype({'Pregnancies': int, 'Glucose': int, 'BloodPressure': int, 'SkinThickness': int, 'Insulin': int, 'BMI': float, 'DiabetesPedigreeFunction': float, 'Age': int, 'Outcome': int}) #Convert data types
    df = df.drop_duplicates() #Remove duplicates

    #Handle Outliers (simple IQR method for demonstration.  More robust methods exist)
    for col in ['BMI', 'Age', 'Glucose', 'BloodPressure']:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]


    # Question 1: Distribution of BMI across different age groups and correlation with diabetes outcomes
    #Statistical Analysis using numpy
    bmi_stats = {
        'mean': np.round(np.mean(df['BMI']),4),
        'median': np.round(np.median(df['BMI']),4),
        'mode': np.round(np.bincount(df['BMI'].astype(int)).argmax(),4) #Approximation for mode on floats
    }
    age_stats = {
        'mean': np.round(np.mean(df['Age']),4),
        'median': np.round(np.median(df['Age']),4),
        'mode': np.round(np.bincount(df['Age']).argmax(),4)
    }
    outcome_stats = {
        'mean': np.round(np.mean(df['Outcome']),4),
        'median': np.round(np.median(df['Outcome']),4),
        'mode': np.round(np.bincount(df['Outcome']).argmax(),4)
    }

    #Visualization
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='Age', y='BMI', hue='Outcome', data=df, palette='viridis')
    plt.title('BMI Distribution Across Age Groups and Diabetes Outcome')
    plt.xlabel('Age')
    plt.ylabel('BMI')
    plt.grid(True)
    plt.savefig(graph_file)
    plt.close()


    # JSON Structure for stats
    stats = {
        "question": "What is the distribution of BMI across different age groups, and how does it correlate with diabetes outcomes?",
        "additional_metrics": {
            "correlation_bmi_age": np.round(np.corrcoef(df['BMI'], df['Age'])[0, 1],4),
            "correlation_bmi_outcome": np.round(np.corrcoef(df['BMI'], df['Outcome'])[0, 1],4),
            "correlation_age_outcome": np.round(np.corrcoef(df['Age'], df['Outcome'])[0, 1],4)
        },
        "bmi_stats": bmi_stats,
        "age_stats": age_stats,
        "outcome_stats": outcome_stats
    }

    return stats


try:
    df = pd.read_csv(data_path)
    if df.empty:
        raise ValueError("Empty dataframe")
    stats = perform_analysis(df)
    with open(stats_file, 'w') as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    print(f"Analysis complete. Stats saved to {stats_file}, graph saved to {graph_file}")

except FileNotFoundError:
    print(f"Error: File not found at {data_path}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# Question 1: Analyze the relationship between Glucose levels and Insulin, and their combined impact on diabetes outcome.
# Output: glucose_insulin_diabetes.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"/home/bob/Projects/InsightFLow/backend/response"
STATS_DIR = r"/home/bob/Projects/InsightFLow/backend/response/request_20250201_225602_a54f8f07/stats"
GRAPHS_DIR = r"/home/bob/Projects/InsightFLow/backend/response/request_20250201_225602_a54f8f07/graphs"

data_path = "/home/bob/Projects/InsightFLow/backend/response/request_20250201_225602_a54f8f07/data/Healthcare-Diabetes.csv"

base_name = "glucose_insulin_diabetes"
graph_file = os.path.join(GRAPHS_DIR, f"{base_name}.png")
stats_file = os.path.join(STATS_DIR, f"{base_name}_stats.json")


def analyze_and_visualize(data_path, graph_file, stats_file):
    try:
        df = pd.read_csv(data_path)
        if df.empty:
            raise ValueError("Empty dataframe")

        # Data Preprocessing
        df = df[['Glucose', 'Insulin', 'Outcome']]  # Select relevant columns
        df.dropna(inplace=True) #Handle missing values by dropping rows with NaN
        df = df[~df.duplicated()] #Remove duplicates

        #Convert to appropriate data types.  Assume int for Outcome.
        df['Glucose'] = df['Glucose'].astype(int)
        df['Insulin'] = df['Insulin'].astype(int)
        df['Outcome'] = df['Outcome'].astype(int)


        # Statistical Analysis using NumPy
        glucose_stats = {
            'mean': np.mean(df['Glucose']).round(4),
            'median': np.median(df['Glucose']).round(4),
            'mode': np.round(np.bincount(df['Glucose']).argmax(),4)
        }
        insulin_stats = {
            'mean': np.mean(df['Insulin']).round(4),
            'median': np.median(df['Insulin']).round(4),
            'mode': np.round(np.bincount(df['Insulin']).argmax(),4)
        }
        outcome_stats = {
            'mean': np.mean(df['Outcome']).round(4),
            'median': np.median(df['Outcome']).round(4),
            'mode': np.round(np.bincount(df['Outcome']).argmax(),4)
        }

        #Visualization
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='Glucose', y='Insulin', hue='Outcome', data=df, palette='viridis')
        plt.title('Glucose vs. Insulin Levels and Diabetes Outcome')
        plt.xlabel('Glucose Level')
        plt.ylabel('Insulin Level')
        plt.grid(True)
        plt.legend(title='Diabetes Outcome (0: No, 1: Yes)')
        plt.savefig(graph_file)
        plt.close()


        # JSON Structure for Stats
        stats = {
            "question": "Analyze the relationship between Glucose levels and Insulin, and their combined impact on diabetes outcome.",
            "glucose_stats": glucose_stats,
            "insulin_stats": insulin_stats,
            "outcome_stats": outcome_stats,
            "additional_metrics": {} # Add more metrics if needed
        }

        #Save Stats to JSON
        with open(stats_file, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)

    except FileNotFoundError:
        print(f"Error: File not found at {data_path}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


analyze_and_visualize(data_path, graph_file, stats_file)

# Question 2: How does DiabetesPedigreeFunction (genetic influence) vary across age groups, and is there a significant correlation with diabetes outcomes?
# Output: diabetes_pedigree_analysis.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"/home/bob/Projects/InsightFLow/backend/response"
STATS_DIR = r"/home/bob/Projects/InsightFLow/backend/response/request_20250201_225602_a54f8f07/stats"
GRAPHS_DIR = r"/home/bob/Projects/InsightFLow/backend/response/request_20250201_225602_a54f8f07/graphs"

data_path = "/home/bob/Projects/InsightFLow/backend/response/request_20250201_225602_a54f8f07/data/Healthcare-Diabetes.csv"

base_name = "diabetes_pedigree_analysis"
graph_file = os.path.join(GRAPHS_DIR, f"{base_name}.png")
stats_file = os.path.join(STATS_DIR, f"{base_name}_stats.json")


def analyze_and_visualize(data_path):
    try:
        df = pd.read_csv(data_path)
        if df.empty:
            raise ValueError("Empty dataframe")

        # Data Preprocessing
        df = df[['Age', 'DiabetesPedigreeFunction', 'Outcome']]  #Selecting relevant columns
        df.dropna(inplace=True) #Handling missing values by dropping rows with NaN
        df = df.astype({'Age': int, 'DiabetesPedigreeFunction': float, 'Outcome': int}) #Type conversion
        df.drop_duplicates(inplace=True) #Removing duplicates

        #Statistical Analysis using numpy
        age_stats = {
            'mean': np.round(np.mean(df['Age']),4),
            'median': np.round(np.median(df['Age']),4),
            'mode': np.round(np.bincount(df['Age']).argmax(),4)
        }
        dp_stats = {
            'mean': np.round(np.mean(df['DiabetesPedigreeFunction']),4),
            'median': np.round(np.median(df['DiabetesPedigreeFunction']),4),
            'mode': np.round(stats.mode(df['DiabetesPedigreeFunction'])[0][0],4)
        }
        outcome_stats = {
            'mean': np.round(np.mean(df['Outcome']),4),
            'median': np.round(np.median(df['Outcome']),4),
            'mode': np.round(np.bincount(df['Outcome']).argmax(),4)
        }
        correlation = np.round(np.corrcoef(df['DiabetesPedigreeFunction'], df['Outcome'])[0,1],4)


        #Visualization
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='Age', y='DiabetesPedigreeFunction', hue='Outcome', data=df, palette='viridis')
        plt.title('Diabetes Pedigree Function vs. Age, Colored by Outcome')
        plt.xlabel('Age')
        plt.ylabel('Diabetes Pedigree Function')
        plt.grid(True)
        plt.savefig(graph_file)
        plt.close()


        #JSON Structure for stats
        stats_data = {
            "question": "How does DiabetesPedigreeFunction (genetic influence) vary across age groups, and is there a significant correlation with diabetes outcomes?",
            "additional_metrics": {
                "correlation_dp_outcome": correlation
            },
            "age_stats": age_stats,
            "diabetes_pedigree_stats": dp_stats,
            "outcome_stats": outcome_stats
        }

        #Save stats to JSON
        with open(stats_file, 'w') as f:
            json.dump(stats_data, f, cls=NumpyJSONEncoder, indent=4)

    except FileNotFoundError:
        print(f"Error: File not found at {data_path}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

from scipy import stats #importing scipy for mode calculation
analyze_and_visualize(data_path)

