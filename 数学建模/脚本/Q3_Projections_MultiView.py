
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

def plot_q3_three_projections():
    # 1. Setup Model & Data
    file_path = 'MCM_Models/Q3_Water_Sustainment.csv'
    try:
        df = pd.read_csv(file_path)
    except:
        data = {'Recycle_Rate': [0.90, 0.95, 0.98, 0.99], 
                'Cost_Billion': [584.4, 292.2, 116.9, 58.4]}
        df = pd.DataFrame(data)

    # Grid for Surface Calculation
    x_grid = np.linspace(0.85, 0.999, 200) # Efficiency
    y_grid = np.linspace(0.8, 1.2, 100)    # Demand Scaling
    X, Y = np.meshgrid(x_grid, y_grid)
    
    # Physics Model with Volatility
    K_const = 5844 
    Z_ideal = K_const * (1 - X) * Y
    wave_y = np.sin(Y * 20) * 0.15 
    wave_x = np.cos(X * 30) * 0.10
    Z = Z_ideal * (1 + wave_y + wave_x)

    # 2. Create Figure with 3 Subplots
    fig = plt.figure(figsize=(18, 6))
    plt.suptitle("Problem 3: Multi-View Projections of Water Strategy Surface", fontsize=18, fontweight='bold', y=1.05)

    # --- View 1: Top-Down Projection (XY Plane) ---
    # Efficiency vs Demand (Color = Cost)
    ax1 = fig.add_subplot(131)
    contour = ax1.contourf(X*100, Y, Z, levels=20, cmap='rainbow', alpha=0.9)
    ax1.set_xlabel('Recycling Efficiency (%)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Demand Scaling Factor', fontsize=11, fontweight='bold')
    ax1.set_title('(1) Cost Heatmap\n(Efficiency vs Demand)', fontsize=14)
    # Overlay sim points
    ax1.scatter(df['Recycle_Rate']*100, [1.0]*len(df), color='white', s=100, edgecolor='black', label='Sim Points')
    ax1.axhline(1.0, color='white', linestyle='--', alpha=0.5)
    fig.colorbar(contour, ax=ax1, orientation='horizontal', label='Logistics Cost ($B)', pad=0.15)

    # --- View 2: Front Projection (XZ Plane) ---
    # Efficiency vs Cost (Density/Likelihood or just colored regions)
    # To project accurately, we need to map Z values.
    # But since it's a projection, simply coloring the area under the curve 
    # using the SAME colormap logic (Cost = Z) makes sense.
    
    ax2 = fig.add_subplot(132)
    
    # We plot the Z values as Y-coordinate, Efficiency as X.
    # To make it "Colorful" like a projection, we can use a scatter of the grid points
    # or a pcolormesh.
    
    # Let's use pcolormesh to show the "wall". 
    # But wait, XZ plane is Efficiency vs Cost. Z IS Cost.
    # So we are plotting Z against X.
    # To show the "Cloud" of possible costs, we can use fill_between but color it by Z value.
    
    # Scatter all grid points to simulate the "Side View" of the surface
    # Flatten arrays
    flat_x = X.flatten() * 100
    flat_z = Z.flatten()
    
    # Sort for better plotting order
    sort_idx = np.argsort(flat_z) # Plot low cost on top? No, high cost is red.
    
    sc2 = ax2.scatter(flat_x[sort_idx], flat_z[sort_idx], c=flat_z[sort_idx], cmap='rainbow', s=10, alpha=0.5, edgecolors='none')
    
    # Overlay Mean Trend
    z_mean = Z.mean(axis=0)
    ax2.plot(x_grid*100, z_mean, color='black', linewidth=2, linestyle='--', label='Mean Trend')
    
    ax2.set_xlabel('Recycling Efficiency (%)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Annual Logistics Cost ($ Billion)', fontsize=11, fontweight='bold')
    ax2.set_title('(2) Efficiency-Cost Projection\n(Side View)', fontsize=14)
    ax2.grid(True, linestyle='--', alpha=0.5)

    # --- View 3: Side Projection (YZ Plane) ---
    # Demand vs Cost
    ax3 = fig.add_subplot(133)
    
    flat_y = Y.flatten()
    
    # Scatter all grid points
    sc3 = ax3.scatter(flat_y, flat_z, c=flat_z, cmap='rainbow', s=10, alpha=0.5, edgecolors='none')
    
    # Overlay 98% line
    idx_98 = np.abs(x_grid - 0.98).argmin()
    z_98 = Z[:, idx_98]
    ax3.plot(y_grid, z_98, color='black', linewidth=3, linestyle='-', label='@ 98% Efficiency')
    
    ax3.set_xlabel('Demand Scaling Factor', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Annual Logistics Cost ($ Billion)', fontsize=11, fontweight='bold')
    ax3.set_title('(3) Demand-Cost Projection\n(Front View)', fontsize=14)
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend()

    plt.tight_layout()
    output_path = 'MCM_Models/Q3_Three_Views.png'
    plt.savefig(output_path, dpi=300)
    print(f"Three Views chart saved to {output_path}")

if __name__ == "__main__":
    plot_q3_three_projections()
