
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

def plot_q3_pareto_surface_final():
    # 1. Load User Data (The "Spine" of the surface)
    file_path = 'MCM_Models/Q3_Water_Sustainment.csv'
    try:
        df = pd.read_csv(file_path)
    except:
        # Fallback if file missing
        data = {'Recycle_Rate': [0.90, 0.95, 0.98, 0.99], 
                'Cost_Billion': [584.4, 292.2, 116.9, 58.4],
                'Occupancy_Pct': [207.3, 103.6, 41.5, 20.7]}
        df = pd.DataFrame(data)

    # 2. Define Grid for Surface
    # X axis: Efficiency (from 0.85 to 0.995) to cover user data range
    x_grid = np.linspace(0.85, 0.999, 100)
    
    # Y axis: Capacity Variation / User Demand Scaling (0.8 to 1.2 x Baseline)
    # This creates the "Surface" width
    y_grid = np.linspace(0.8, 1.2, 50)
    
    X, Y = np.meshgrid(x_grid, y_grid)
    
    # 3. Calculate Z (Cost) based on physics model
    # Cost ~ (1 - Efficiency) * Demand_Factor
    # We use the user's 90% data point to calibrate the constant "K"
    # Cost_90 = K * (1 - 0.90) * 1.0 => 584.4 = K * 0.1 => K = 5844
    K_const = 5844 
    
    Z_ideal = K_const * (1 - X) * Y
    
    # 3.5 Add "Volatility" / Noise as requested by user
    # Add a sine wave perturbation along the Demand axis (Y) to show sensitivity
    # Increased amplitude significantly to make it visible
    wave_y = np.sin(Y * 20) * 0.15 
    
    # Add a sine wave along Efficiency (X) to show non-linear tech risks
    wave_x = np.cos(X * 30) * 0.10
    
    # Combine
    Z = Z_ideal * (1 + wave_y + wave_x)
    
    # 4. Plotting
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Surface Plot (Rainbow)
    surf = ax.plot_surface(X*100, Y, Z, cmap='rainbow', 
                           linewidth=0, edgecolors='k', alpha=0.8)
                           
    # --- Add Projections on Walls (Shadows) ---
    # Get approximate data limits for placement
    z_floor = 0 
    x_wall = 85 # Min X
    y_wall = 1.25 # Max Y (Back wall)
    
    # 1. Bottom Projection (XY Plane) -> Efficiency vs Demand Map
    ax.contourf(X*100, Y, Z, zdir='z', offset=z_floor, cmap='rainbow', alpha=0.4)
    
    # 2. Back Wall Projection (XZ Plane) -> Efficiency vs Cost Profile
    ax.contourf(X*100, Y, Z, zdir='y', offset=y_wall, cmap='rainbow', alpha=0.3)
    
    # 3. Side Wall Projection (YZ Plane) -> Demand vs Cost Profile
    ax.contourf(X*100, Y, Z, zdir='x', offset=x_wall, cmap='rainbow', alpha=0.3)
    
    # Set explicit limits to ensure projections are visible and not clipped
    ax.set_xlim(85, 100)
    ax.set_ylim(0.8, 1.25)
    ax.set_zlim(0, Z.max())
    
    # 5. Highlight User's Data on the Surface
    # User data corresponds to Y = 1.0 (Baseline)
    user_x = df['Recycle_Rate'] * 100
    user_y = np.ones(len(user_x)) * 1.0 # Baseline line
    user_z = df['Cost_Billion']
    
    # Draw the "Trajectory Line"
    ax.plot(user_x, user_y, user_z, color='white', linewidth=4, zorder=10, label='Your Data Trace')
    
    # Draw the specific Points
    ax.scatter(user_x, user_y, user_z, color='white', s=200, edgecolor='black', zorder=11)
    
    # Annotate points
    for i, row in df.iterrows():
        label = f"{row['Recycle_Rate']*100:.0f}%"
        ax.text(row['Recycle_Rate']*100, 1.0, row['Cost_Billion'] + 20, label, 
                color='black', fontsize=10, fontweight='bold', ha='center')

    # 6. Add Threshold Plane (Budget/Capacity Limit)
    # E.g. $200B Budget
    # Z_limit = 200
    # ax.plot_surface(X*100, Y, np.full_like(Z, Z_limit), color='red', alpha=0.2)

    # Decoration
    ax.set_xlabel('\nRecycling Efficiency (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('\nDemand Scaling Factor (0.8x - 1.2x)', fontsize=12, fontweight='bold')
    ax.set_zlabel('\nLogistics Cost ($ Billion)', fontsize=12, fontweight='bold')
    
    ax.set_title('Problem 3: Pareto Solution Surface\n(Extending your data with Demand Uncertainty)', fontsize=16, pad=20)
    
    # Set proper view
    ax.view_init(elev=30, azim=135)
    
    # Colorbar
    cbar = plt.colorbar(surf, ax=ax, shrink=0.5, pad=0.1)
    cbar.set_label('Logistics Cost ($ Billion)', fontsize=12)

    plt.tight_layout()
    output_path = 'MCM_Models/Q3_Pareto_Surface_Final.png'
    plt.savefig(output_path, dpi=300)
    print(f"Surface chart saved to {output_path}")

if __name__ == "__main__":
    plot_q3_pareto_surface_final()
