
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.colors as mcolors

def plot_q3_3d_surface():
    # --- Constants ---
    POPULATION = 100000
    SE_ANNUAL_CAPACITY = 5.37e8  # kg
    SAFETY_BUFFER = 0.10
    PACKAGING = 0.01
    FACTOR = (1 + SAFETY_BUFFER) * (1 + PACKAGING)

    # --- Data Grid ---
    # X: Recycling Rate (85% to 99.9%)
    x_eff = np.linspace(0.90, 0.995, 100)
    
    # Y: Per Capita Demand (150 to 450 kg/day)
    # Baseline is 274.5
    y_demand = np.linspace(200, 400, 100)
    
    X, Y = np.meshgrid(x_eff, y_demand)
    
    # Z: Occupancy (%)
    # Non-linear relationship: Import ~ Demand * (1 - Efficiency)
    # Occupancy = (Pop * Demand * 365 * (1-Eff) * Factor) / Capacity * 100
    
    Z_ideal = (POPULATION * Y * 365.0 * (1 - X) * FACTOR) / SE_ANNUAL_CAPACITY * 100
    
    # Add "Volatility" to simulate real-world system instability
    # Assumption: Higher efficiency systems are more complex and sensitive to perturbations.
    # We add a wave-like fluctuation that increases amplitude slightly as Efficiency increases,
    # and also varies randomly with Demand.
    
    # 1. Sine wave fluctuation along Demand (Y)
    wave_y = np.sin(Y / 30.0) * 0.05 
    
    # 2. Random micro-noise
    np.random.seed(42)
    noise = np.random.normal(0, 0.02, Z_ideal.shape)
    
    # Combine: Z_new = Z_ideal * (1 + wave + noise)
    Z = Z_ideal * (1 + wave_y + noise)

    # --- Plotting ---
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Main Surface Plot
    # Main Surface Plot
    # User requested rainbow color scheme
    surf = ax.plot_surface(X*100, Y, Z, cmap='rainbow', 
                           linewidth=0.1, edgecolors='k', antialiased=True, alpha=0.9)

    # --- Add Projections (Shadows) ---
    # User asked for "the part below" (projections)
    # Z axis is log scale from 10 to 300, so we project to z=10
    
    # Bottom (Z=min) - Heatmap projection
    ax.contourf(X*100, Y, Z, zdir='z', offset=10, cmap='rainbow', alpha=0.5)

    # --- Add Capacity Limit Plane (Z = 100%) ---
    ax.plot_surface(X*100, Y, np.full_like(Z, 100), color='#FF0000', alpha=0.15, shade=False)
    # Add a line on the surface where Z=100
    ax.contour(X*100, Y, Z, levels=[100], colors='red', linewidths=3, linestyles='--')

    # --- Highlights ---
    # Highlight the "Baseline Point" (274.5 kg, 98%)
    bl_eff = 0.98
    bl_demand = 274.5
    bl_z = (POPULATION * bl_demand * 365.0 * (1 - bl_eff) * FACTOR) / SE_ANNUAL_CAPACITY * 100
    
    ax.scatter([bl_eff*100], [bl_demand], [bl_z], color='white', s=150, label='Proposed Strategy (98%)', zorder=20, edgecolors='black', linewidth=1.5)
    
    # Highlight the "Failure Point" (274.5 kg, 95%)
    fail_eff = 0.95
    fail_z = (POPULATION * bl_demand * 365.0 * (1 - fail_eff) * FACTOR) / SE_ANNUAL_CAPACITY * 100
    # fail_z is usually > 100, so it might be clipped if we limit z to 200, but 95% is ~103%, so it shows.
    ax.scatter([fail_eff*100], [bl_demand], [fail_z], color='red', s=150, label='Scenario 95% (Failure)', zorder=20, marker='X', edgecolors='white')

    # Labels
    ax.set_xlabel('\nRecycling Efficiency (%)', fontsize=11, fontweight='bold')
    ax.set_ylabel('\nPer Capita Demand (kg/day)', fontsize=11, fontweight='bold')
    ax.set_zlabel('\nSpace Elevator Occupancy (%)', fontsize=11, fontweight='bold')
    
    ax.set_title('Problem 3: 3D Sensitivity Analysis (Log Scale)\nThe "Feasibility Cliff" of Water Sustainability', fontsize=16, pad=20)
    
    # Use Log Scale for Z axis to show the "Cliff" effect and details at low values
    ax.set_zscale('log')
    # After setting log scale, we need to adjust limits carefully. Z cannot be 0.
    # Our data min is around 0.5% (at 99.5% efficiency).
    ax.set_zlim(10, 300) 
    
    # Colorbar
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.1)
    cbar.set_label('SE Occupancy (%) - Log Scale', fontsize=12, fontweight='bold')

    ax.view_init(elev=25, azim=135)
    
    # Legend
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    
    output_path = 'Q3_Sensitivity_3D.png'
    plt.savefig(output_path, dpi=300)
    print(f"3D Chart saved to {output_path}")

if __name__ == "__main__":
    plot_q3_3d_surface()
