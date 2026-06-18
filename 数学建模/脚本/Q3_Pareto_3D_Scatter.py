
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm

def plot_q3_pareto_3d_final():
    """
    Generates a 3D Scatter Plot for Problem 3 Pareto data.
    Since Problem 3 data (from CSV) is technically 2D (Rate vs Cost), 
    we will extend it to 3D by adding 'Safety Buffer' as the 3rd dimension 
    or just plotting (Rate, Cost, Occupancy) as the 3 axes.
    
    Let's use:
    X: Recycling Rate (%)
    Y: Cost ($B)
    Z: Occupancy (%)
    
    This visualizes the complete state space.
    """
    
    # Load user data
    file_path = 'MCM_Models/Q3_Water_Sustainment.csv'
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Prepare Data
    x = df['Recycle_Rate'] * 100  # Efficiency %
    y = df['Cost_Billion']        # Cost $B
    z = df['Occupancy_Pct']       # Occupancy %

    # Create figure
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. Plot the actual data points
    # Use color based on Z (Occupancy) - High Occ = Red, Low Occ = Green
    # We use a reversed colormap so Red is high Z
    sc = ax.scatter(x, y, z, c=z, cmap='RdYlGn_r', s=200, edgecolors='k', depthshade=False, alpha=1.0)
    
    # 2. Add "Drop lines" to the floor (Projection)
    z_min = 0 # Visual floor
    for xi, yi, zi in zip(x, y, z):
        ax.plot([xi, xi], [yi, yi], [z_min, zi], 'k--', alpha=0.3)
        
    # 3. Add a curve connecting them (interpolation)
    # Sort by X
    sorted_indices = np.argsort(x)
    ax.plot(x[sorted_indices], y[sorted_indices], z[sorted_indices], 
            color='gray', linewidth=2, alpha=0.6, label='Trend Line')

    # 4. Add the "Limit Plane" at Z = 100%
    # Create a meshgrid for the plane
    xx, yy = np.meshgrid(np.linspace(x.min()-1, x.max()+1, 10),
                         np.linspace(y.min()-10, y.max()+10, 10))
    zz = np.full_like(xx, 100)
    
    plane = ax.plot_surface(xx, yy, zz, color='red', alpha=0.15, shade=False)
    
    # Add text annotation for the limit
    ax.text(x.min(), y.max(), 105, "Operational Limit (100% Occupancy)", color='red', fontsize=10, fontweight='bold')

    # Labels
    ax.set_xlabel('\nRecycling Efficiency (%)', fontsize=11, fontweight='bold')
    ax.set_ylabel('\nLogistics Cost ($ Billion)', fontsize=11, fontweight='bold')
    ax.set_zlabel('\nSE Occupancy (%)', fontsize=11, fontweight='bold')
    
    ax.set_title('Problem 3: 3D Pareto Analysis\n(Efficiency vs Cost vs Capacity)', fontsize=16, pad=20)
    
    # Labels for points
    for xi, yi, zi in zip(x, y, z):
        label = f"{xi:.0f}%"
        ax.text(xi, yi, zi + 10, label, ha='center', fontsize=9, fontweight='bold')

    # Colorbar
    cbar = plt.colorbar(sc, ax=ax, shrink=0.5, pad=0.1)
    cbar.set_label('Capacity Occupancy (%)', fontsize=11)
    
    # View Angle
    ax.view_init(elev=20, azim=135)
    
    plt.tight_layout()
    output_path = 'MCM_Models/Q3_Pareto_3D_Scatter.png'
    plt.savefig(output_path, dpi=300)
    print(f"3D Scatter saved to {output_path}")

if __name__ == "__main__":
    plot_q3_pareto_3d_final()
