
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

def plot_feasibility_threshold_analysis():
    """
    Visualizes Table 7: Feasibility Threshold Analysis Under Different Scenarios
    Focuses on Space Elevator Load Rate and Import Volume.
    """
    print("Generating Feasibility Threshold Plot (Table 7)...")
    
    # Data from Table 7
    scenarios = ['Baseline\nScenario', 'High-Demand\nScenario', 'Low-Efficiency\nScenario', 'Critical Point\nScenario']
    load_rates = [41.0, 59.8, 102.6, 100.3] # %
    import_mass = [220.4, 321.2, 551.1, 539.3] # Million tons
    feasibility = ['Feasible', 'Feasible', 'Infeasible', 'Critical']
    
    # Colors based on feasibility
    colors = []
    for f in feasibility:
        if f == 'Feasible':
            colors.append('#2ECC71') # Green
        elif f == 'Critical':
            colors.append('#F39C12') # Orange
        else:
            colors.append('#E74C3C') # Red

    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Bar Plot for Load Rate
    bars = ax1.bar(scenarios, load_rates, color=colors, alpha=0.8, width=0.6, label='SE Load Rate')
    
    # Threshold Line
    ax1.axhline(y=100, color='#C0392B', linestyle='--', linewidth=2, zorder=10)
    ax1.text(3.6, 102, 'Feasibility Threshold (100%)', color='#C0392B', va='bottom', ha='right', fontweight='bold')

    # Formatting Ax1
    ax1.set_ylabel('Space Elevator Load Rate (%)', fontsize=14, color='#2C3E50')
    ax1.set_ylim(0, 120)
    ax1.set_title('Feasibility Analysis: Load Rate & Import Demands', pad=20)
    
    # Add values on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height}%',
                ha='center', va='bottom', fontweight='bold', color='black')

    # Secondary Axis for Import Mass (Optional, but Table 7 has it)
    # Let's verify if we want to plot Import Mass. It correlates heavily with Load Rate. 
    # Maybe just a line plot on twinx?
    ax2 = ax1.twinx()
    ax2.plot(scenarios, import_mass, color='#3498DB', marker='o', linestyle='-', linewidth=2, markersize=8, label='Import Mass')
    ax2.set_ylabel('Import Mass (Million Tons)', fontsize=14, color='#34495E')
    ax2.spines['right'].set_visible(True)
    ax2.set_ylim(0, 600)
    
    # Add values for mass
    for i, mass in enumerate(import_mass):
        ax2.text(i, mass - 30, f'{mass} Mt', ha='center', va='top', color='#2980B9', fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    # Custom Legend
    legend_patches = [
        mpatches.Patch(color='#2ECC71', label='Feasible (<100%)'),
        mpatches.Patch(color='#F39C12', label='Critical (~100%)'),
        mpatches.Patch(color='#E74C3C', label='Infeasible (>100%)'),
        plt.Line2D([0], [0], color='#3498DB', marker='o', label='Import Mass')
    ]
    ax1.legend(handles=legend_patches, loc='upper left')

    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Feasibility_Analysis.png'
    plt.savefig(output_path)
    print(f"Saved {output_path}")


def plot_sensitivity_tornado():
    """
    Visualizes Table 8: Parameter Sensitivity Analysis Results
    """
    print("Generating Parameter Sensitivity Plot (Table 8)...")
    
    # Data from Table 8
    # Parameter names
    params = [
        r'$D_{Moon}$ (Demand)',
        r'$\delta$ (Depreciation)',
        r'$C_{SE}$ (Unit Cost)',
        r'$Q_{SE}$ (Capacity)'
    ]
    
    # Impact on f1 (Cost) in %
    # Table values: +/- 20, +/- 5, +/- 10, None (0)
    impact_f1 = [20, 5, 10, 0]
    
    # We can plot this as a horizontal bar chart
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Invert order for top-down plotting
    y_pos = np.arange(len(params))
    
    bars = ax.barh(y_pos, impact_f1, color='#8E44AD', alpha=0.8, height=0.6)
    
    # Labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels(params)
    ax.set_xlabel('Impact on Total Cost ($f_1$) [%]', fontweight='bold')
    ax.set_title('Parameter Sensitivity Analysis', pad=20)
    ax.set_xlim(0, 25)
    
    # Add value labels
    for i, width in enumerate(impact_f1):
        if width > 0:
            ax.text(width + 0.5, i, f'±{width}%', va='center', fontweight='bold', color='#8E44AD')
        else:
            ax.text(width + 0.5, i, 'Negligible', va='center', fontstyle='italic', color='gray')

    # Annotate "Drivers"
    # Highlight that Demand is the main driver
    ax.text(20, 0, 'Primary Cost Driver', ha='right', va='center', color='white', fontweight='bold', fontsize=10)
    
    # Add a text description box for context
    desc = (
        "Sensitivity Notes:\n"
        "• Water Demand ($D_{Moon}$) has the highest impact on cost.\n"
        "• Capacity ($Q_{SE}$) changes do not affect cost significantly\n"
        "  as long as feasibility is maintained."
    )
    plt.figtext(0.7, 0.2, desc, fontsize=11, bbox=dict(facecolor='#ECF0F1', alpha=0.5, boxstyle='round,pad=0.5'))

    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Sensitivity_Tornado.png'
    plt.savefig(output_path)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    plot_feasibility_threshold_analysis()
    plot_sensitivity_tornado()
