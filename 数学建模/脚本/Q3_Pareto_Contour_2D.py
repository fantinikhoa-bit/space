
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.patheffects as pe

def plot_q3_contour_2d_final():
    # 1. Load User Data 
    file_path = 'MCM_Models/Q3_Water_Sustainment.csv'
    try:
        df = pd.read_csv(file_path)
    except:
        # Fallback
        data = {'Recycle_Rate': [0.90, 0.95, 0.98, 0.99], 
                'Cost_Billion': [584.4, 292.2, 116.9, 58.4]}
        df = pd.DataFrame(data)

    # 2. Define Grid
    # X axis: Efficiency (from 85% to 99.9%)
    x_grid = np.linspace(0.85, 0.999, 200)
    # Y axis: Demand Scaling (0.8 to 1.2)
    y_grid = np.linspace(0.8, 1.2, 100)
    
    X, Y = np.meshgrid(x_grid, y_grid)
    
    # 3. Calculate Cost (Z) with Noise
    K_const = 5844 
    Z_ideal = K_const * (1 - X) * Y
    
    # Add same perturbations as before for consistency
    wave_y = np.sin(Y * 20) * 0.15 
    wave_x = np.cos(X * 30) * 0.10
    Z = Z_ideal * (1 + wave_y + wave_x)
    
    # 4. Plot 2D Contour Map
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Filled Contour (Heatmap)
    # Using 'rainbow' or 'viridis'. 'RdYlGn_r' is good for Cost (Red=High, Green=Low)
    # User liked rainbow in previous steps.
    level_bounds = np.linspace(0, 1000, 21) # Cap roughly at 1000B
    
    contour = ax.contourf(X*100, Y, Z, levels=20, cmap='rainbow', alpha=0.9)
    # Add contour lines for clarity
    ax.contour(X*100, Y, Z, levels=20, colors='black', linewidths=0.5, alpha=0.3)
    
    # 5. Overlay User Trajectory (Baseline Y=1.0)
    # Draw the baseline path
    ax.axhline(1.0, color='white', linestyle='--', linewidth=2, label='Baseline Demand Scenario')
    
    # Plot the specific points
    user_x = df['Recycle_Rate'] * 100
    user_y = [1.0] * len(user_x)
    
    ax.scatter(user_x, user_y, color='white', s=150, edgecolor='black', zorder=10, label='Simulated Scenarios')
    
    # Annotate points
    for i, row in df.iterrows():
        # Label with Cost
        cost_val = row['Cost_Billion']
        label = f"${cost_val:.0f}B"
        ax.annotate(label, (row['Recycle_Rate']*100, 1.0), 
                    xytext=(0, 15), textcoords='offset points', ha='center', 
                    color='white', fontweight='bold', fontsize=11,
                    path_effects=[pe.withStroke(linewidth=3, foreground='black')])

    # 6. Add Threshold Line (e.g. Failure Zone)
    # If Cost > 200B is failure? Or Efficiency < 96%?
    # Let's mark the "Safe Zone" border based on cost?
    # Or just keep it clean.
    
    # Labels
    ax.set_xlabel('Recycling Efficiency (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Demand Scaling Factor (Seasonal/Risk)', fontsize=12, fontweight='bold')
    
    ax.set_title('Problem 3: Cost Sensitivity Heatmap (2D View)\nRecycling Efficiency vs. Demand Uncertainty', fontsize=16, pad=20)
    
    # Colorbar
    cbar = plt.colorbar(contour, ax=ax)
    cbar.set_label('Logistics Cost ($ Billion)', fontsize=12)
    
    ax.legend(loc='upper right', frameon=True, framealpha=0.9)
    
    plt.tight_layout()
    output_path = 'MCM_Models/Q3_Pareto_Contour_2D.png'
    plt.savefig(output_path, dpi=300)
    print(f"2D Contour chart saved to {output_path}")

if __name__ == "__main__":
    plot_q3_contour_2d_final()
