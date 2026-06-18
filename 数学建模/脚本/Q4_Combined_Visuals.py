
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# --- Global Style ---
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 14,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'axes.titleweight': 'bold',
    'legend.fontsize': 12,
    'grid.alpha': 0.3,
    'figure.dpi': 300, 
    'axes.spines.top': False,
    'axes.spines.right': False,
})

def plot_combined_analysis():
    """
    Combines Feasibility Analysis (Table 7) and Sensitivity Analysis (Table 8)
    into a single 1x2 figure.
    """
    print("Generating Combined Analysis Plot...")
    
    # Create Figure with GridSpec
    fig = plt.figure(figsize=(20, 9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 1], wspace=0.25)
    
    ax1 = fig.add_subplot(gs[0, 0])
    ax_tornado = fig.add_subplot(gs[0, 1])

    # ==========================================
    # LEFT PANEL: Feasibility Analysis (Table 7)
    # ==========================================
    scenarios = ['Baseline\nScenario', 'High-Demand\nScenario', 'Low-Efficiency\nScenario', 'Critical Point\nScenario']
    load_rates = [41.0, 59.8, 102.6, 100.3] # %
    import_mass = [220.4, 321.2, 551.1, 539.3] # Million tons
    feasibility = ['Feasible', 'Feasible', 'Infeasible', 'Critical']
    
    colors = []
    for f in feasibility:
        if f == 'Feasible':
            colors.append('#2ECC71') # Green
        elif f == 'Critical':
            colors.append('#F39C12') # Orange
        else:
            colors.append('#E74C3C') # Red

    # Bar Plot for Load Rate
    bars = ax1.bar(scenarios, load_rates, color=colors, alpha=0.8, width=0.6, label='SE Load Rate')
    
    # Threshold Line
    ax1.axhline(y=100, color='#C0392B', linestyle='--', linewidth=2, zorder=10)
    ax1.text(3.5, 102, 'Max Capacity (100%)', color='#C0392B', va='bottom', ha='right', fontweight='bold', fontsize=12)

    # Secondary Axis for Import Mass
    ax2 = ax1.twinx()
    ax2.plot(scenarios, import_mass, color='#3498DB', marker='o', linestyle='-', linewidth=3, markersize=10, label='Import Mass')
    ax2.set_ylabel('Import Mass (Million Tons)', fontsize=14, color='#34495E')
    ax2.spines['right'].set_visible(True)
    ax2.set_ylim(0, 650)
    
    # Formatting Ax1
    ax1.set_ylabel('Space Elevator Load Rate (%)', fontsize=14, color='#2C3E50')
    ax1.set_ylim(0, 120)
    ax1.set_title('(A) Feasibility Threshold Analysis', loc='left', pad=15)
    
    # Add values on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height}%',
                ha='center', va='bottom', fontweight='bold', color='black', fontsize=11)

    # Custom Legend for Left Panel
    legend_patches = [
        mpatches.Patch(color='#2ECC71', label='Feasible'),
        mpatches.Patch(color='#F39C12', label='Critical'),
        mpatches.Patch(color='#E74C3C', label='Infeasible'),
        plt.Line2D([0], [0], color='#3498DB', marker='o', linewidth=3, label='Import Mass')
    ]
    ax1.legend(handles=legend_patches, loc='upper left', frameon=True, facecolor='white', framealpha=0.9)

    # ==========================================
    # RIGHT PANEL: Sensitivity Analysis (Table 8)
    # ==========================================
    params = [
        r'$D_{Moon}$ (Demand)',
        r'$\delta$ (Depreciation)',
        r'$C_{SE}$ (Unit Cost)',
        r'$Q_{SE}$ (Capacity)'
    ]
    impact_f1 = [20, 5, 10, 0] # Impact on Cost
    
    # Invert for plotting
    y_pos = np.arange(len(params))
    
    # Tornado/Horizontal Bar
    bars_t = ax_tornado.barh(y_pos, impact_f1, color='#8E44AD', alpha=0.8, height=0.6)
    
    # Labels
    ax_tornado.set_yticks(y_pos)
    ax_tornado.set_yticklabels(params, fontsize=13)
    ax_tornado.set_xlabel('Impact on Total Cost ($f_1$) [%]', fontweight='bold')
    ax_tornado.set_title('(B) Parameter Sensitivity (Cost Driver)', loc='left', pad=15)
    ax_tornado.set_xlim(0, 25)
    
    # Add value labels
    for i, width in enumerate(impact_f1):
        if width > 0:
            ax_tornado.text(width + 0.5, i, f'±{width}%', va='center', fontweight='bold', color='#8E44AD', fontsize=12)
        else:
            ax_tornado.text(width + 0.5, i, 'Negligible', va='center', fontstyle='italic', color='gray', fontsize=11)

    # Insights Text Box in right panel
    desc = (
        "Key Insight:\n"
        "Water Demand ($D_{Moon}$) is the\n"
        "dominant cost driver (±20%).\n"
        "Capacity has minimal cost impact\n"
        "assuming feasibility conditions met."
    )
    ax_tornado.text(0.95, 0.05, desc, transform=ax_tornado.transAxes, 
                   fontsize=12, verticalalignment='bottom', horizontalalignment='right',
                   bbox=dict(facecolor='#ECF0F1', alpha=0.6, boxstyle='round,pad=0.5'))

    # Final Layout
    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Combined_Analysis.png'
    plt.savefig(output_path)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    plot_combined_analysis()
