
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib import cm
import matplotlib.colors as mcolors

# Set style for better aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['axes.titlesize'] = 18
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12

def plot_q3_pareto_tradeoff():
    # Load data
    try:
        df = pd.read_csv('MCM_Models/Q3_Water_Sustainment.csv')
    except FileNotFoundError:
        # Fallback data if file not found
        data = {
            'Recycle_Rate': [0.90, 0.95, 0.98, 0.99],
            'Cost_Billion': [584.40, 292.20, 116.88, 58.44],
            'Occupancy_Pct': [207.29, 103.64, 41.46, 20.73]
        }
        df = pd.DataFrame(data)

    # Convert Rate to Percent for plotting
    df['Recycle_Pct'] = df['Recycle_Rate'] * 100
    
    # Create figure with higher resolution
    fig, ax1 = plt.subplots(figsize=(12, 8), dpi=100)

    # --- Plot 1: The Trade-off Curve (Recycle Rate vs Cost) ---
    # We treat "Recycling Deficiency" (1-Rate) as the driver, but plotting Rate on X is clearer for readers.
    
    # Use a smooth interpolation for the line to show the trend
    x_smooth = np.linspace(df['Recycle_Pct'].min(), df['Recycle_Pct'].max(), 100)
    # Fit a curve: Cost is proportional to (1 - Rate)
    # y = k * (1 - x/100)
    # Let's just use the actual points for the "Pareto" look
    
    # Create a custom color gradient for the line
    colors = ['#3498DB', '#2980B9', '#1F618D', '#154360']
    cmap = mcolors.LinearSegmentedColormap.from_list('custom_blue', colors, N=256)
    
    # Plot the trade-off curve with enhanced styling
    sns.lineplot(data=df, x='Recycle_Pct', y='Cost_Billion', ax=ax1, 
                 marker='o', markersize=14, linewidth=4, color='#2E86C1', 
                 label='Logistics Cost', alpha=0.9)
    
    # Add gradient fill under the curve
    x = df['Recycle_Pct']
    y = df['Cost_Billion']
    ax1.fill_between(x, y, y.min(), color='#2E86C1', alpha=0.1)

    # Fill area to show "Feasibility"
    # Threshold: Where Occupancy < 100%?
    # From data: 95% is 103% (Fail), 98% is 41% (Pass).
    # Interpolating: 100% occupancy happens roughly at 95.5%
    
    # Add a vertical span for "Infeasible Zone" with better styling
    ax1.axvspan(90, 95.4, color='#E74C3C', alpha=0.2, label='Infeasible Zone (>100% SE Capacity)')
    ax1.axvspan(95.4, 99.5, color='#2ECC71', alpha=0.2, label='Feasible Zone (Sustainable)')
    
    # Add border lines for the zones
    ax1.axvline(x=95.4, color='#34495E', linestyle='--', linewidth=2, label='Feasibility Threshold')

    # Labels with enhanced styling
    ax1.set_title('Problem 3: Technology-Cost Trade-off Analysis\n(The "Pareto Frontier" of Water Sustainability)', 
                  fontsize=18, pad=25, fontweight='bold', color='#2C3E50')
    ax1.set_xlabel('Water Recycling Efficiency (%)', fontsize=14, fontweight='bold', labelpad=15)
    ax1.set_ylabel('Annual Logistics Cost ($ Billion)', fontsize=14, fontweight='bold', color='#2E86C1', labelpad=15)
    ax1.tick_params(axis='y', labelcolor='#2E86C1')
    
    # --- Plot 2: Secondary Axis for Occupancy ---
    ax2 = ax1.twinx()
    
    # Annotate points
    for i, row in df.iterrows():
        ax1.annotate(f"${row['Cost_Billion']:.1f}B", 
                     (row['Recycle_Pct'], row['Cost_Billion']),
                     textcoords="offset points", xytext=(0,12), ha='center', 
                     fontsize=11, weight='bold', color='#2E86C1',
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.8))
        
        # Add occupancy percentage annotations
        ax2.annotate(f"{row['Occupancy_Pct']:.1f}%", 
                     (row['Recycle_Pct'], row['Occupancy_Pct']),
                     textcoords="offset points", xytext=(0,-15), ha='center', 
                     fontsize=10, weight='bold', color='#E67E22',
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.8))
    # Plot occupancy with enhanced styling
    sns.lineplot(data=df, x='Recycle_Pct', y='Occupancy_Pct', ax=ax2, 
                 marker='s', markersize=12, linewidth=3, linestyle='--', 
                 color='#E67E22', label='SE Capacity Occupancy', alpha=0.9)
    
    ax2.set_ylabel('Space Elevator Capacity Occupancy (%)', fontsize=12, fontweight='bold', color='#E67E22')
    ax2.tick_params(axis='y', labelcolor='#E67E22')
    
    # Add a horizontal line for 100% Capacity with better styling
    ax2.axhline(100, color='#C0392B', linestyle=':', linewidth=3, label='100% Capacity Limit')
    ax2.text(91, 103, 'CRITICAL LIMIT (100%)', color='#C0392B', fontweight='bold', 
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.8))

    # Legend
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    
    # Combine legends (handling the span patch correctly)
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', frameon=True, prop={'size': 10})

    # Enhanced grid
    ax1.grid(True, linestyle='--', alpha=0.4, color='#BDC3C7')
    ax2.grid(True, linestyle='--', alpha=0.4, color='#BDC3C7')
    
    # Layout
    plt.tight_layout()
    
    # Save with higher resolution
    output_path = 'MCM_Models/Q3_Pareto_Tradeoff.png'
    plt.savefig(output_path, dpi=400, bbox_inches='tight')
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    print("Generating enhanced Pareto frontier plot for water resource optimization...")
    plot_q3_pareto_tradeoff()
    print("Plot generation completed! The enhanced chart has been saved.")
