
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def plot_pareto_multi_view():
    # Load data
    file_path = 'Q4_NSGA2_Pareto.csv'
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # Extract columns
    # We want to plot the objectives.
    time = df['Time']
    cost = df['Cost']
    emissions = df['Emissions']

    # Scale for better readability (optional)
    # Cost is in 10^13, let's scale to 10^12 (Trillions)
    cost_scaled = cost / 1e12
    cost_label = 'Cost ($ Trillion)'
    
    # Emissions is in 10^11, let's scale to 10^9 (Billion kg) or similar
    # 1e11 kg = 100 Billion kg ?
    emissions_scaled = emissions / 1e9
    emissions_label = 'Emissions ($10^9$ kg)'
    
    time_label = 'Time (Days)'

    # Create figure with 2x2 subplots
    fig = plt.figure(figsize=(16, 12))
    
    # Common scatter params
    scatter_kwargs = {'c': 'blue', 'alpha': 0.7, 'edgecolors': 'k', 's': 40}

    # 1. Top-Left: Cost vs Time
    ax1 = fig.add_subplot(221)
    ax1.scatter(time, cost_scaled, **scatter_kwargs)
    ax1.set_xlabel(time_label, fontsize=12)
    ax1.set_ylabel(cost_label, fontsize=12)
    ax1.set_title('Projection: Cost vs Time', fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # 2. Top-Right: Emissions vs Time
    ax2 = fig.add_subplot(222)
    ax2.scatter(time, emissions_scaled, **scatter_kwargs)
    ax2.set_xlabel(time_label, fontsize=12)
    ax2.set_ylabel(emissions_label, fontsize=12)
    ax2.set_title('Projection: Emissions vs Time', fontsize=14)
    ax2.grid(True, linestyle='--', alpha=0.6)

    # 3. Bottom-Left: Emissions vs Cost
    ax3 = fig.add_subplot(223)
    ax3.scatter(cost_scaled, emissions_scaled, **scatter_kwargs)
    ax3.set_xlabel(cost_label, fontsize=12)
    ax3.set_ylabel(emissions_label, fontsize=12)
    ax3.set_title('Projection: Emissions vs Cost', fontsize=14)
    ax3.grid(True, linestyle='--', alpha=0.6)

    # 4. Bottom-Right: 3D Plot
    ax4 = fig.add_subplot(224, projection='3d')
    sc = ax4.scatter(time, cost_scaled, emissions_scaled, c=emissions_scaled, cmap='viridis', s=50, alpha=0.9, edgecolors='w')
    
    ax4.set_xlabel(time_label, labelpad=10)
    ax4.set_ylabel(cost_label, labelpad=10)
    ax4.set_zlabel(emissions_label, labelpad=10)
    ax4.set_title('3D Pareto Front Surface', fontsize=14)
    
    # Add projections on walls for 3D plot
    xlim = ax4.get_xlim()
    ylim = ax4.get_ylim()
    zlim = ax4.get_zlim()
    
    ax4.scatter(time, cost_scaled, np.full_like(emissions_scaled, zlim[0]), c='gray', alpha=0.2, marker='.')
    ax4.scatter(time, np.full_like(cost_scaled, ylim[1]), emissions_scaled, c='gray', alpha=0.2, marker='.')
    ax4.scatter(np.full_like(time, xlim[0]), cost_scaled, emissions_scaled, c='gray', alpha=0.2, marker='.')

    # Colorbar for 3D plot
    cbar = plt.colorbar(sc, ax=ax4, shrink=0.6, pad=0.1)
    cbar.set_label(emissions_label)
    
    # Adjust view
    ax4.view_init(elev=30, azim=135)

    plt.suptitle('Pareto Optimization Results: Time vs Cost vs Emissions', fontsize=18)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    output_file = 'Pareto_Analysis_Combined.png'
    plt.savefig(output_file, dpi=300)
    print(f"Saved combined plot to {output_file}")

if __name__ == "__main__":
    plot_pareto_multi_view()
