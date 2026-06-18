import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def plot_pareto_3d_no_projections():
    # Load data
    file_path = 'Q4_NSGA2_Pareto.csv'
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # Extract columns
    x = df['Time']
    y = df['Cost']
    z = df['Emissions']

    # Create figure
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Main 3D Data
    sc = ax.scatter(x, y, z, c=z, cmap='viridis', s=50, alpha=0.9, edgecolors='w', label='Pareto Optimal Points')

    # Labels
    ax.set_xlabel('Time (Days)', fontsize=12, labelpad=10)
    ax.set_ylabel('Cost ($)', fontsize=12, labelpad=10)
    ax.set_zlabel('Emissions (kg CO2)', fontsize=12, labelpad=10)
    ax.set_title('3D Pareto Front\n(Time vs Cost vs Emissions)', fontsize=16)

    # Colorbar
    cbar = plt.colorbar(sc, ax=ax, shrink=0.6, pad=0.1)
    cbar.set_label('Emissions', fontsize=12)

    # View angle
    ax.view_init(elev=25, azim=135)

    # Grid aesthetics
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Save to multiple locations to ensure the user sees the update
    filenames = ['Pareto_3D.png', 'Pareto_3D_Projection.png', 'Q4_NSGA2_3D_Plot.png']
    plt.tight_layout()
    for f in filenames:
        plt.savefig(f, dpi=300)
        print(f"Saved plot to {f}")

if __name__ == "__main__":
    plot_pareto_3d_no_projections()
