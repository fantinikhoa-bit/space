
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import FuncFormatter

def plot_q3_pareto_final():
    # Load user data
    file_path = 'MCM_Models/Q3_Water_Sustainment.csv'
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Prepare Data
    # X: Recycling Efficiency (%) -> We usually plot "1 - Efficiency" (Waste Rate) for Pareto to minimize both X and Y?
    # Or just Efficiency on X (Maximize) and Cost on Y (Minimize).
    # Let's use Efficiency (Maximize) vs Cost (Minimize).
    
    df['Efficiency_Pct'] = df['Recycle_Rate'] * 100
    df['Cost_B'] = df['Cost_Billion']
    
    # Setup Plot
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Define Palette (Red to Green)
    # 90% -> Red (Bad)
    # 99% -> Green (Good)
    points = ax.scatter(df['Efficiency_Pct'], df['Cost_B'], 
                        c=df['Efficiency_Pct'], cmap='RdYlGn', s=200, edgecolor='black', zorder=10)
    
    # Connect points to show the "Front"
    ax.plot(df['Efficiency_Pct'], df['Cost_B'], linestyle='--', color='gray', alpha=0.7, zorder=5)

    # Add Labels
    for i, row in df.iterrows():
        label = f"{row['Efficiency_Pct']:.0f}%\n${row['Cost_B']:.1f}B"
        
        # Adjust label position
        xytext = (0, 15)
        if i == 0: xytext = (10, -20) # 90%
        
        ax.annotate(label, (row['Efficiency_Pct'], row['Cost_B']), 
                    xytext=xytext, textcoords='offset points', 
                    ha='center', fontsize=11, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9))

    # Add Regions
    # Failure Zone (>100% Occupancy)
    # From csv: 95% is 103% Occ. 98% is 41%.
    # Interpolating: Limit is around 95.3%
    limit_eff = 95.3
    
    # Shade Failure Zone
    ax.axvspan(90, limit_eff, color='#e74c3c', alpha=0.15, label='Infeasible (>100% SE Occupancy)')
    ax.axvspan(limit_eff, 100, color='#2ecc71', alpha=0.15, label='Feasible (Sustainable)')

    # Add vertical line for limit
    ax.axvline(limit_eff, color='#c0392b', linestyle=':', linewidth=2)
    ax.text(limit_eff, df['Cost_B'].max()*0.9, ' SYSTEM LIMIT\n (Occupancy > 100%)', 
            color='#c0392b', ha='left', fontweight='bold')

    # Axes Labels and Title
    ax.set_xlabel('Recycling Efficiency (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Annual Logistics Cost ($ Billion)', fontsize=12, fontweight='bold')
    ax.set_title('Problem 3: Pareto Frontier of Water Strategy\n(Efficiency vs. Logistics Cost)', fontsize=16, pad=20)
    
    # Invert X axis? No, standard is distinct.
    # But usually Pareto front is convex towards origin (Min, Min).
    # Here X is Max, Y is Min. That's fine.
    
    ax.legend(loc='upper right', frameon=True)
    
    plt.tight_layout()
    output_path = 'MCM_Models/Q3_Pareto_Front_Final.png'
    plt.savefig(output_path, dpi=300)
    print(f"Pareto chart saved to {output_path}")

if __name__ == "__main__":
    plot_q3_pareto_final()
