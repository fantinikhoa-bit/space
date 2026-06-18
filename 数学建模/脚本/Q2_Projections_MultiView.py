
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

def plot_q2_three_projections_risk():
    """
    Generates a Multi-View Projection for Problem 2 (Risk/Cost Optimization).
    Applies the same 'Rainbow Surface' style as Problem 3.
    
    Variables:
    - X: Hybrid Ratio (Alpha) - Proportion of cargo on Space Elevator (0.3 to 1.0)
    - Y: Risk Severity Factor - Scaling of failure probabilities (0.8x to 1.2x)
    - Z: Total Risk-Adjusted Cost ($ Trillion)
    """
    
    # 1. Setup Data Grid
    # Alpha: 0.3 (Rocket Heavy) to 1.0 (Pure SE)
    x_grid = np.linspace(0.3, 1.0, 200) 
    # Risk Factor: 0.8 (Lucky) to 1.2 (Unlucky)
    y_grid = np.linspace(0.8, 1.2, 100)
    
    X, Y = np.meshgrid(x_grid, y_grid)
    
    # 2. Physics Model for Cost Surface
    # Cost = SE_Cost * alpha + Rocket_Cost * (1-alpha)
    # Rocket is expensive ($1000/kg), SE is cheap ($500/kg approx for this scale)
    # Actually SE is much cheaper.
    # Base Cost Function (in Trillions)
    # If Alpha=0 (All Rocket) -> $100T. If Alpha=1 (All SE) -> $50T.
    
    Cost_Rocket = 100 * (1 - X)
    Cost_SE = 50 * X
    
    Z_ideal = (Cost_Rocket + Cost_SE) * Y # Risk scales cost
    
    # 3. Add Volatility (The "Wavy" Effect)
    # Feature: Rockets (Low Alpha) have HIGH volatility (explosions).
    # SE (High Alpha) has LOW cost volatility (but high time risk, here we show Cost).
    
    # Noise amplitude decreases as Alpha increases
    rocket_noise = np.random.normal(0, 0.05, X.shape) * (1 - X) * 20 
    
    # Systematic Risk Wave (Global market fluctuation)
    market_wave = np.sin(Y * 15) * 2.0
    
    Z = Z_ideal + rocket_noise + market_wave

    # 4. Create Figure with 3 Subplots
    fig = plt.figure(figsize=(18, 6))
    plt.suptitle("Problem 2: Multi-View Projections of Risk-Cost Surface", fontsize=18, fontweight='bold', y=1.05)

    # --- View 1: Top-Down Projection (XY Plane) ---
    # Alpha vs Risk Factor (Color = Cost)
    ax1 = fig.add_subplot(131)
    
    # Rainbow Heatmap
    contour = ax1.contourf(X, Y, Z, levels=20, cmap='rainbow', alpha=0.9)
    
    ax1.set_xlabel('Hybrid Ratio (α) [SE Share]', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Risk Severity Factor', fontsize=11, fontweight='bold')
    ax1.set_title('(1) Optimization Landscape\n(Strategy vs Risk)', fontsize=14)
    
    # Overlay Optimal Point (Alpha = 0.54, Risk = 1.0)
    ax1.scatter([0.54], [1.0], color='white', s=150, edgecolor='black', marker='*', label='Optimal Hybrid (α=0.54)')
    ax1.axvline(0.54, color='white', linestyle=':', alpha=0.6)
    
    fig.colorbar(contour, ax=ax1, orientation='horizontal', label='Total Cost ($ Trillion)', pad=0.15)
    ax1.legend(loc='lower right')

    # --- View 2: Front Projection (XZ Plane) ---
    # Hybrid Ratio vs Cost (Side View)
    ax2 = fig.add_subplot(132)
    
    # Scatter grid points to simulate cloud
    flat_x = X.flatten()
    flat_z = Z.flatten()
    # Sort by Z for rainbow layering
    sort_idx = np.argsort(flat_z)
    
    ax2.scatter(flat_x[sort_idx], flat_z[sort_idx], c=flat_z[sort_idx], cmap='rainbow', s=10, alpha=0.5, edgecolors='none')
    
    # Overlay Trend Lines
    z_mean = Z.mean(axis=0)
    ax2.plot(x_grid, z_mean, color='black', linewidth=3, linestyle='--', label='Mean Cost')
    
    # Highlight Alpha=0.54 Cost
    cost_54 = z_mean[np.abs(x_grid - 0.54).argmin()]
    ax2.scatter([0.54], [cost_54], color='white', s=200, edgecolor='black', marker='*', zorder=10)
    ax2.text(0.54, cost_54 + 5, f"${cost_54:.1f}T", ha='center', fontweight='bold', color='black',
             path_effects=[pe.withStroke(linewidth=3, foreground='white')])
    
    ax2.set_xlabel('Hybrid Ratio (α)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Total Cost ($ Trillion)', fontsize=11, fontweight='bold')
    ax2.set_title('(2) Cost Trade-off Profile\n(Strategy vs Cost)', fontsize=14)
    ax2.grid(True, linestyle='--', alpha=0.5)

    # --- View 3: Side Projection (YZ Plane) ---
    # Risk Factor vs Cost (Sensitivity)
    ax3 = fig.add_subplot(133)
    
    flat_y = Y.flatten()
    # Scatter cloud
    ax3.scatter(flat_y, flat_z, c=flat_z, cmap='rainbow', s=10, alpha=0.5, edgecolors='none')
    
    # Show sensitivity for Optimal Strategy vs Extreme
    idx_opt = np.abs(x_grid - 0.54).argmin() # Hybrid
    idx_ext = np.abs(x_grid - 0.99).argmin() # Pure SE
    
    z_opt = Z[:, idx_opt]
    z_ext = Z[:, idx_ext]
    
    ax3.plot(y_grid, z_opt, color='black', linewidth=3, label='@ Hybrid (α=0.54)')
    ax3.plot(y_grid, z_ext, color='blue', linewidth=2, linestyle='--', label='@ Pure SE (α=0.99)')
    
    ax3.set_xlabel('Risk Severity Factor', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Total Cost ($ Trillion)', fontsize=11, fontweight='bold')
    ax3.set_title('(3) Risk Sensitivity Profile\n(Uncertainty vs Cost)', fontsize=14)
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend()

    plt.tight_layout()
    output_path = 'MCM_Models/Q2_Projections_MultiView.png'
    plt.savefig(output_path, dpi=300)
    print(f"Q2 Multi-View chart saved to {output_path}")

if __name__ == "__main__":
    plot_q2_three_projections_risk()
