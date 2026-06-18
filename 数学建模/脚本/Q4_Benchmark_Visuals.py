
import matplotlib.pyplot as plt
import numpy as np
from math import pi

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

def plot_benchmark_comparison_bars():
    """
    Visualizes Table 11 using a 3-panel bar chart to handle different units.
    Comparison of Time, Cost, and Emissions.
    """
    print("Generating Benchmark Bar Comparison...")
    
    scenarios = ['Pure Rocket', 'Pure Space Elevator', 'Phased Strategy']
    colors = ['#E74C3C', '#3498DB', '#27AE60'] # Red, Blue, Green
    
    # Data
    time_data = [91.3, 186.2, 141.5]     # Years
    cost_data = [100.0, 52.5, 64.3]      # Trillion USD
    emissions_data = [724.0, 10.0, 181.9] # Million Tons CO2e
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Helper to plot each metric
    def plot_metric(ax, data, title, unit, y_limit):
        bars = ax.bar(scenarios, data, color=colors, alpha=0.85, width=0.6, edgecolor='black', linewidth=0.5)
        ax.set_title(title)
        ax.set_ylabel(unit)
        ax.set_ylim(0, y_limit)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        # Add values
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (y_limit * 0.02),
                    f'{height}', ha='center', va='bottom', fontweight='bold', fontsize=11)
            
        # Highlight the "Winner" or Characteristics
        # Rocket: Fastest
        if title == "Total Time":
             ax.text(0, data[0]/2, "Fastest", ha='center', color='white', fontweight='bold')
             ax.text(1, data[1]/2, "Slowest", ha='center', color='white', fontweight='bold')
             ax.text(2, data[2]/2, "Balanced", ha='center', color='white', fontweight='bold')
             
        # Cost
        if title == "Total Cost":
             ax.text(0, data[0]/2, "Highest", ha='center', color='white', fontweight='bold')
             ax.text(1, data[1]/2, "Lowest", ha='center', color='white', fontweight='bold')
             ax.text(2, data[2]/2, "Optimal", ha='center', color='white', fontweight='bold')

        # Emissions
        if title == "Total Emissions":
             ax.text(0, data[0]/2, "Catastrophic", ha='center', color='white', fontweight='bold', fontsize=9)
             ax.text(1, data[1] + 10, "Clean", ha='center', color='#3498DB', fontweight='bold')
             ax.text(2, data[2] + 10, "Controllable", ha='center', color='#27AE60', fontweight='bold')

    plot_metric(axes[0], time_data, "Time comparison", "Years", 220)
    plot_metric(axes[1], cost_data, "Cost comparison", "Trillion USD ($T)", 120)
    plot_metric(axes[2], emissions_data, "Emissions comparison", "Million Tons CO2e", 800)

    plt.suptitle('Table 11: Benchmark Scenario Comparison Matrix\n(Trade-off Analysis)', fontsize=18, fontweight='bold', y=1.05)
    plt.tight_layout()
    
    output_path = 'MCM_Models/Q4_Benchmark_Bars.png'
    plt.savefig(output_path, bbox_inches='tight')
    print(f"Saved {output_path}")


def plot_benchmark_radar():
    """
    Normalizes the data and plots a Radar Chart to show the 'Shape' of each strategy.
    """
    print("Generating Benchmark Radar Chart...")
    
    # Categories
    categories = ['Time (Years)', 'Cost ($T)', 'Emissions (Mt)']
    N = len(categories)
    
    # Raw Data
    # We normalize each metric to [0, 1] relative to the max in that category for visualization
    # Note: For all these metrics, LOWER IS BETTER. 
    # So we might want to invert axis or just plot as 'Magnitude of Impact' (Outer = High Cost/Time/Emit)
    
    # Let's plot "Magnitude" (Outer = Higher Value). 
    # So "Small Area" = Better.
    
    raw_rocket = [91.3, 100.0, 724.0]
    raw_se = [186.2, 52.5, 10.0]
    raw_phased = [141.5, 64.3, 181.9]
    
    # Max values for normalization
    max_vals = [200.0, 110.0, 800.0] # Slightly above max for padding
    
    def normalize(data):
        return [d / m for d, m in zip(data, max_vals)]
    
    values_rocket = normalize(raw_rocket)
    values_se = normalize(raw_se)
    values_phased = normalize(raw_phased)
    
    # Loop back for radar closure
    values_rocket += values_rocket[:1]
    values_se += values_se[:1]
    values_phased += values_phased[:1]
    
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Draw one axe per variable + labels
    plt.xticks(angles[:-1], categories, color='black', size=12, weight='bold')
    
    # Draw ylabels (scales) ? No, confusing with normalized data. Let's hide radial labels.
    ax.set_yticklabels([])
    
    # Plot Rocket
    ax.plot(angles, values_rocket, linewidth=2, linestyle='dotted', color='#E74C3C', label='Pure Rocket (Fast but Dirty)')
    ax.fill(angles, values_rocket, '#E74C3C', alpha=0.1)
    
    # Plot SE
    ax.plot(angles, values_se, linewidth=2, linestyle='dashed', color='#3498DB', label='Pure Space Elevator (Clean but Slow)')
    ax.fill(angles, values_se, '#3498DB', alpha=0.1)
    
    # Plot Phased
    ax.plot(angles, values_phased, linewidth=3, linestyle='solid', color='#27AE60', label='Phased Strategy (The Golden Mean)')
    ax.fill(angles, values_phased, '#27AE60', alpha=0.25)
    
    # Add Title
    plt.title("Scenario Footprint Comparison\n(Smaller Area = Better/More Efficient)", size=15, color='#2C3E50', y=1.1, weight='bold')
    
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15))
    
    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Benchmark_Radar.png'
    plt.savefig(output_path)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    plot_benchmark_comparison_bars()
    plot_benchmark_radar()
