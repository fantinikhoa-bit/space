
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import os

# Ensure results directory exists
result_dir = r'd:\Users\HONOR\Desktop\base\2026\Results'
csv_path = os.path.join(result_dir, 'Q4_LCA_Results.csv')
os.makedirs(result_dir, exist_ok=True)

class Combined3DPlotter:
    def __init__(self):
        self.data_path = csv_path

    def load_data(self):
        """Load real data from CSV"""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"CSV file not found at {self.data_path}")
            
        df = pd.read_csv(self.data_path)
        return df

    def plot_3d_combined(self, df):
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Extract data
        # Scale the data for better visualization labels
        
        # Cost: Original is ~1e14 (100 Trillion). Convert to Trillion USD (1e12)
        # Or maybe 100 Billion? Let's check magnitude. 
        # 1e14 is 100 Trillion. That's a lot. 
        # Let's scale by 1e12 (Trillion)
        cost_scale = 1e12
        cost_unit = "Trillion USD"
        costs = df['Total_Cost'] / cost_scale
        
        # Time: Years
        times = df['Total_Time']
        
        # Emissions: Original ~7e8 (700 Million). Convert to Million Tonnes (Mt)
        emission_scale = 1e6
        emission_unit = "Mt CO2"
        emissions = df['Total_Emissions'] / emission_scale
        
        # Plot Pareto Front (Red Stars) since CSV typically contains the optimal set
        # We can use color to represent one of the dimensions (e.g., Cost) for better depth perception
        scatter = ax.scatter(costs, times, emissions, 
                           c=costs, cmap='viridis', 
                           marker='*', s=200, 
                           edgecolors='k', linewidth=0.5, 
                           label='Pareto Optimal Solutions',
                           depthshade=True)

        # Connect points to visualize the front structure (optional, but helps if points are sparse)
        # Sort by Cost to make a cleaner line
        sort_idx = np.argsort(costs)
        ax.plot(costs[sort_idx], times[sort_idx], emissions[sort_idx], 
                c='gray', linestyle='--', linewidth=1, alpha=0.5)

        # Labels and Title
        ax.set_xlabel(f'Total Cost ({cost_unit})', fontsize=11, labelpad=10)
        ax.set_ylabel('Total Time (Years)', fontsize=11, labelpad=10)
        ax.set_zlabel(f'Emissions ({emission_unit})', fontsize=11, labelpad=10)
        ax.set_title('3D Pareto Front Visualization\n(Based on Optimized Solution Data)', fontsize=14, pad=20)
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax, pad=0.1, shrink=0.6)
        cbar.set_label(f'Total Cost ({cost_unit})')
        
        # Customize Grid and Pane
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        
        # View angle
        ax.view_init(elev=20, azim=135)
        
        # Save
        filename = 'Q4_Projection_Combined_3D_Real.png'
        save_path = os.path.join(result_dir, filename)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved real data 3D plot to: {save_path}")
        plt.close()

if __name__ == "__main__":
    plotter = Combined3DPlotter()
    try:
        df = plotter.load_data()
        print(f"Loaded {len(df)} data points from CSV.")
        plotter.plot_3d_combined(df)
    except Exception as e:
        print(f"Error: {e}")
