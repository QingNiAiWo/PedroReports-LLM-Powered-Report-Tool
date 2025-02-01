import os

def load_schema():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "../../services/analysis/stats_template.json")  
    
    file_path = os.path.abspath(file_path) 
    print("Loading file from:", file_path) 

    with open(file_path, "r") as f:
        return f.read()
