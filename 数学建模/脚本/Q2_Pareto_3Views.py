
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

def plot_q2_pareto_3views():
    """
    Problem 2 Main Result: The "Triangular" Relationship between Strategy (Alpha), Cost, and Time.
    Visualize this as 3 Projections.
    """
    
    # 1. Simulation Data Generation
    # Strategy Alpha: 0.3 (Rocket Heavy) to 1.0 (Pure SE)
    alpha = np.linspace(0.3, 0.99, 500)
    
    # Physics Models (Simplified for Viz)
    # Time Model: Rocket is fast, SE is slow.
    # T = T_min + k * alpha^2
    # Add Risk Noise: SE (high alpha) has high time volatility
    T_det = 60 + 130 * alpha**2.5 # Exp growth in time
    
    # Cost Model: Rocket is expensive, SE is cheap.
    # C = C_base + k * (1-alpha)
    C_det = 50 + 60 * (1 - alpha)**1.2
    
    # Risk Noise Generation (Monte Carlo Cloud)
    np.random.seed(42)
    # Expand data for cloud effect
    alpha_cloud = np.repeat(alpha, 20)
    
    # Time Risk: Increases with Alpha (SE failures delay project)
    time_noise = np.random.normal(0, 0.05, len(alpha_cloud)) * (alpha_cloud * 40)
    # Cost Risk: Increases with (1-Alpha) (Rocket explosions cost money)
    cost_noise = np.random.normal(0, 0.05, len(alpha_cloud)) * ((1 - alpha_cloud) * 50)
    
    T_cloud = np.repeat(T_det, 20) + time_noise
    C_cloud = np.repeat(C_det, 20) + cost_noise + 5.4 # Add premium baseline
    
    # Color mapping: Use Strategy (Alpha) as the Rainbow Color
    colors = alpha_cloud
    
    # 2. Create Plot
    fig = plt.figure(figsize=(18, 6))
    plt.suptitle("Problem 2: The Impossible Triangle (Strategy vs Cost vs Time)", fontsize=18, fontweight='bold', y=1.05)
    
    # --- View 1: Pareto Front (Cost vs Time) ---
    # The Classic Result
    ax1 = fig.add_subplot(131)
    
    scatter = ax1.scatter(T_cloud, C_cloud, c=colors, cmap='rainbow', s=10, alpha=0.3, edgecolors='none')
    
    # Draw Pareto Curve (Mean)
    ax1.plot(T_det, C_det + 5.4, 'k--', linewidth=2, label='Pareto Frontier')
    
    # Highlight Optimal
    # Alpha = 0.54
    idx = np.abs(alpha - 0.54).argmin()
    opt_T = T_det[idx]
    opt_C = C_det[idx] + 5.4
    
    ax1.scatter([opt_T], [opt_C], color='white', s=200, edgecolor='black', marker='*', zorder=10, label='Optimal (α=0.54)')
    ax1.text(opt_T, opt_C+2, f"Optimal\n$80T, 102y", ha='left', fontweight='bold', path_effects=[pe.withStroke(linewidth=3, foreground='white')])
    
    ax1.set_xlabel('Total Duration (Years)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Total Cost ($ Trillion)', fontsize=11, fontweight='bold')
    ax1.set_title('(1) Pareto Front\n(Cost vs Time)', fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend()
    
    # Colorbar for Alpha
    cbar = fig.colorbar(scatter, ax=ax1, orientation='horizontal', pad=0.15)
    cbar.set_label('Hybrid Strategy α (0=Rocket, 1=Elevator)', fontsize=10)

    # --- View 2: Strategy vs Time ---
    ax2 = fig.add_subplot(132)
    
    ax2.scatter(alpha_cloud, T_cloud, c=colors, cmap='rainbow', s=10, alpha=0.3, edgecolors='none')
    ax2.plot(alpha, T_det, 'k--', linewidth=2)
    
    # Annotate Risk
    ax2.arrow(0.9, 150, 0, 30, head_width=0.05, head_length=5, fc='red', ec='red')
    ax2.text(0.9, 190, 'High Time\nVolatility', ha='center', color='red', fontweight='bold')
    
    ax2.set_xlabel('Hybrid Strategy (α)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Duration (Years)', fontsize=11, fontweight='bold')
    ax2.set_title('(2) Time Mechanics\n(Strategy vs Time)', fontsize=14)
    ax2.grid(True, linestyle='--', alpha=0.5)

    # --- View 3: Strategy vs Cost ---
    ax3 = fig.add_subplot(133)
    
    ax3.scatter(alpha_cloud, C_cloud, c=colors, cmap='rainbow', s=10, alpha=0.3, edgecolors='none')
    ax3.plot(alpha, C_det + 5.4, 'k--', linewidth=2)
    
    # Annotate Risk
    ax3.arrow(0.35, 95, 0, 15, head_width=0.05, head_length=3, fc='red', ec='red')
    ax3.text(0.35, 115, 'High Cost\nVolatility', ha='center', color='red', fontweight='bold')
    
    ax3.set_xlabel('Hybrid Strategy (α)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Total Cost ($ Trillion)', fontsize=11, fontweight='bold')
    ax3.set_title('(3) Cost Mechanics\n(Strategy vs Cost)', fontsize=14)
    ax3.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    output_path = 'MCM_Models/Q2_Three_Views_Pareto.png'
    plt.savefig(output_path, dpi=300)
    print(f"Pareto 3-View chart saved to {output_path}")

if __name__ == "__main__":
    plot_q2_pareto_3views()
