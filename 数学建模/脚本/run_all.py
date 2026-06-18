
import os
import subprocess
import sys

def run_script(script_path, base_dir):
    print(f"==========================================")
    print(f"Running {os.path.basename(script_path)}...")
    print(f"==========================================")
    try:
        # Run using the same python executable
        result = subprocess.run([sys.executable, script_path], cwd=base_dir)
        if result.returncode != 0:
            print(f"Error running {os.path.basename(script_path)}")
    except Exception as e:
        print(f"Failed to run {script_path}: {e}")

if __name__ == "__main__":
    # Get the directory where this run_all.py resides (MCM_Models)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (base)
    base_dir = os.path.dirname(current_dir)
    
    # Define the sequence of Phase-Based Models
    scripts = [
        # 1. Base DP Optimization (Camp, Base, City)
        "Q1_New_DP/solve_dp.py", 
        
        # 2. Risk Analysis (Sensitivity & Breakdown)
        "Q1_New_DP/solve_risk_per_stage.py",
        "Q1_New_DP/solve_risk_sensitivity_breakdown.py",
        
        # 3. Environmental Impact (Phased LCA)
        "Q4_Phased_Strategy_LCA.py"
    ]
    
    for script_rel_path in scripts:
        # Construct full path to the script
        script_path = os.path.join(current_dir, script_rel_path)
        run_script(script_path, base_dir)
    
    print("\nAll Phased Strategy models executed successfully.")
