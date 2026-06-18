
import matplotlib.pyplot as plt
import numpy as np

# --- Global Style ---
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 12,
    'axes.labelsize': 13,
    'axes.titlesize': 15,
    'axes.titleweight': 'bold',
    'legend.fontsize': 11,
    'grid.alpha': 0.3,
    'figure.dpi': 300, 
    'axes.spines.top': False,
    'axes.spines.right': False,
})

def plot_performance_decomposition():
    """
    Visualizes Table 9: Performance Decomposition of the Optimal Three-Phase Strategy.
    Uses discrete stacked bars/pie charts to show contribution of each phase.
    """
    print("Generating Performance Decomposition Plot...")
    
    # Data
    phases = ['Stage 1\n(Camp)', 'Stage 2\n(Base)', 'Stage 3\n(City)']
    time_data = [11.2, 55.9, 74.5]
    cost_data = [7.2, 25.9, 31.1]
    emissions_data = [29.6, 75.4, 76.4]
    
    colors = ['#A9CCE3', '#5499C7', '#2471A3'] # Blues for Phases
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))

    # Function to create donut charts for decomposition
    def create_donut(ax, data, title, unit, total_val):
        wedges, texts, autotexts = ax.pie(data, labels=phases, autopct='%1.1f%%', 
                                          startangle=140, colors=colors, pctdistance=0.85, 
                                          wedgeprops=dict(width=0.3, edgecolor='white'))
        
        # Center Text (Total)
        ax.text(0, 0, f"{total_val}\n{unit}", ha='center', va='center', fontweight='bold', fontsize=14, color='#34495E')
        
        ax.set_title(title, pad=20)
        
        # Style percentages
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

    # Plot 1: Time
    create_donut(axes[0], time_data, "Time Decomposition", "Years", 141.5)
    
    # Plot 2: Cost
    create_donut(axes[1], cost_data, "Cost Decomposition", "$ Trillion", 64.3)
    
    # Plot 3: Emissions
    create_donut(axes[2], emissions_data, "Emissions Decomposition", "Mt CO2", 181.9)
    
    # Add a main title
    plt.suptitle('Table 9: Comparison of Phase Contributions to Global Impact', fontsize=18, fontweight='bold', y=1.05)
    
    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Performance_Decomposition.png'
    plt.savefig(output_path, bbox_inches='tight')
    print(f"Saved {output_path}")

def plot_configuration_parameters():
    """
    Visualizes Table 10: Configuration Parameters of the Optimal Strategy.
    Combines Mass Allocation (Stacked Bar) and Alpha (Line).
    """
    print("Generating Configuration Parameters Plot...")
    
    phases = ['Phase 1\nCamp', 'Phase 2\nBase', 'Phase 3\nCity']
    
    # Data
    mass_se = [6.0, 30.0, 40.0]        # Million Tons
    mass_rocket = [4.0, 10.0, 10.0]    # Million Tons
    alpha_vals = [0.60, 0.75, 0.80]    # Ratio
    
    x = np.arange(len(phases))
    width = 0.5
    
    fig, ax1 = plt.subplots(figsize=(10, 7))
    
    # Stacked Bars (Mass Allocation)
    p1 = ax1.bar(x, mass_se, width, label='Space Elevator Mass', color='#2ECC71', alpha=0.9, edgecolor='white')
    p2 = ax1.bar(x, mass_rocket, width, bottom=mass_se, label='Rocket Mass', color='#E74C3C', alpha=0.9, edgecolor='white')
    
    ax1.set_ylabel('Visualized Mass Transport (Million Tons)', fontsize=13)
    ax1.set_title('Table 10: Optimal Strategy Configuration & Mass Split', pad=20)
    ax1.set_xticks(x)
    ax1.set_xticklabels(phases, fontsize=12)
    ax1.set_ylim(0, 60) # 50 + buffer
    
    # Add values to bars
    for i in range(len(phases)):
        # SE Mass label
        ax1.text(x[i], mass_se[i]/2, f"{mass_se[i]}Mt\n(SE)", ha='center', va='center', color='white', fontweight='bold')
        # Rocket Mass label
        ax1.text(x[i], mass_se[i] + mass_rocket[i]/2, f"{mass_rocket[i]}Mt\n(Rkt)", ha='center', va='center', color='white', fontweight='bold')
    
    # Second Axis for Alpha
    ax2 = ax1.twinx()
    ax2.plot(x, alpha_vals, color='#2C3E50', marker='D', markersize=10, linewidth=3, linestyle='--', label=r'Optimal $\alpha_{SE}$')
    ax2.set_ylabel(r'Space Elevator Ratio ($\alpha_{SE}$)', fontsize=13, color='#2C3E50')
    ax2.set_ylim(0.4, 1.0)
    ax2.spines['right'].set_visible(True)
    
    # Add Alpha Labels
    for i, alpha in enumerate(alpha_vals):
        ax2.text(x[i], alpha + 0.03, f"$\\alpha={alpha}$", ha='center', va='bottom', fontweight='bold', color='#2C3E50', 
                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='#2C3E50', boxstyle='round,pad=0.2'))
    
    # Combined Legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left', framealpha=0.9)
    
    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Strategy_Configuration.png'
    plt.savefig(output_path)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    plot_performance_decomposition()
    plot_configuration_parameters()
