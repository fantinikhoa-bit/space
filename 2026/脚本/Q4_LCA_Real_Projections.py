
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys

# Ensure we can import the optimizer model
sys.path.append(r'd:\Users\HONOR\Desktop\base\2026')
from Q4_LCA_NSGA2 import LCAOptimizer

# Output directory
result_dir = r'd:\Users\HONOR\Desktop\base\2026\Results'
os.makedirs(result_dir, exist_ok=True)

class RealProjectionsPlotter:
    def __init__(self):
        self.optimizer = LCAOptimizer()
        self.csv_path = os.path.join(result_dir, 'Q4_LCA_Results.csv')
        
    def load_pareto_data(self):
        """Load the optimized Pareto front solutions from CSV"""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found at {self.csv_path}")
        return pd.read_csv(self.csv_path)

    def generate_feasible_cloud(self, n_samples=5000):
        """Run Monte Carlo simulation using the REAL model to get the Feasible Region"""
        print(f"Generating {n_samples} Monte Carlo samples from the real model...")
        costs = []
        times = []
        emissions = []
        
        # Use the generator logic from LCAOptimizer to create random valid inputs
        # The optimizer has generate_initial_population, let's use that logic or similar
        
        for _ in range(n_samples):
            # Random inputs
            # M_total is fixed in params
            M_total = self.optimizer.params['M_total']
            
            # Random Split
            x = np.random.uniform(0, M_total) # Space Elevator
            y = M_total - x                   # Rocket
            
            # Random Sites (Binary)
            z = [np.random.randint(0, 2) for _ in range(self.optimizer.params['n'])]
            
            individual = [x, y] + z
            
            # Evaluate using the REAL fitness function
            res = self.optimizer.evaluate(individual)
            
            # Res contains [Cost, Time, Emission]
            # Check for infinity (constraint violations)
            if res[0] != float('inf'):
                costs.append(res[0])
                times.append(res[1])
                emissions.append(res[2])
                
        return np.array(costs), np.array(times), np.array(emissions)

    def plot_projection(self, pareto_x, pareto_y, 
                       x_label, y_label, filename, title, 
                       x_scale=1.0, y_scale=1.0):
        
        plt.figure(figsize=(10, 8))
        
        # 2. Pareto Front (Real Optimization Results)
        # Sort points for a smooth line connecting them (optional but looks better)
        sort_idx = np.argsort(pareto_x)
        sorted_x = pareto_x[sort_idx] / x_scale
        sorted_y = pareto_y[sort_idx] / y_scale
        
        # Plot Line
        plt.plot(sorted_x, sorted_y, c='red', linestyle='--', linewidth=1.5, alpha=0.7)
        
        # Plot Points
        plt.scatter(sorted_x, sorted_y, 
                   c='red', marker='*', s=200, edgecolors='k', linewidth=0.5, label='Optimal Strategies (NSGA-II)')
        
        # Labels
        plt.xlabel(x_label, fontsize=14)
        plt.ylabel(y_label, fontsize=14)
        plt.title(title, fontsize=16)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(fontsize=12)
        
        # Save
        save_path = os.path.join(result_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved real data plot (no cloud): {save_path}")

    def run(self):
        # 1. Load Real Pareto Data
        df = self.load_pareto_data()
        pf_cost = df['Total_Cost'].values
        pf_time = df['Total_Time'].values
        pf_env = df['Total_Emissions'].values
        
        # Scaling Factors for display (e.g. Cost to Trillions, Env to Mt)
        cost_scale = 1e12 # Trillions
        cost_lbl = "Total Cost (Trillion USD)"
        
        time_scale = 1.0
        time_lbl = "Total Time (Years)"
        
        env_scale = 1e6 # Million Tons
        env_lbl = "Emissions (Mt CO2)"
        
        # 3. Plot 
        
        # (a) Cost vs Time
        self.plot_projection(
            pf_cost, pf_time,
            cost_lbl, time_lbl,
            'Q4_Projection_Cost_Time_Real.png', '(a) Cost vs Time (Real Model)'
            , cost_scale, time_scale
        )
        
        # (b) Cost vs Env
        self.plot_projection(
            pf_cost, pf_env,
            cost_lbl, env_lbl,
            'Q4_Projection_Cost_Env_Real.png', '(b) Cost vs Emissions (Real Model)'
            , cost_scale, env_scale
        )
        
        # (c) Time vs Env
        self.plot_projection(
            pf_time, pf_env,
            time_lbl, env_lbl,
            'Q4_Projection_Time_Env_Real.png', '(c) Time vs Emissions (Real Model)'
            , time_scale, env_scale
        )

if __name__ == "__main__":
    plotter = RealProjectionsPlotter()
    plotter.run()
