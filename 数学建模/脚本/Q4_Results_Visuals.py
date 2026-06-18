
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

# --- Global Style Config ---
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 12,
    'axes.labelsize': 13,
    'axes.titlesize': 15,
    'axes.titleweight': 'bold',
    'legend.fontsize': 11,
    'figure.titlesize': 16,
    'grid.alpha': 0.3,
    'figure.dpi': 300,
})

def plot_kpi_comparison():
    """
    Visualizes the Key Performance Indicators table from the Q4 Report.
    Comparing Baseline (Pure Rocket) vs Optimal Phased Strategy.
    """
    print("Generating KPI Comparison Plot...")

    # Data from Problem4_Summary_Paper_Final.md
    metrics = ['Total Time\n(Years)', 'Total Cost\n($ Trillion)', 'Total Emissions\n(Mt CO2)']
    
    # Baseline (Pure Rocket) - Reconstructed from report deltas
    # Time: Phased is 141.5 (+55% of X) -> X = 141.5/1.55 = 91.3
    # Cost: Phased is 64.3 (-36% of X) -> X = 64.3 / (1-0.36) = 100.5
    # Emissions: Report explicitly states Pure Rocket is 724 Mt
    baseline_values = [91.3, 100.5, 724.0] 
    
    # Phased Strategy (Optimal)
    phased_values = [141.5, 64.3, 181.9]

    # Plot Setup
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(metrics))
    width = 0.35

    # Bars
    bars1 = ax.bar(x - width/2, baseline_values, width, label='Baseline (Pure Rocket)', color='#E74C3C', alpha=0.9, edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, phased_values, width, label='Optimal Phased Strategy', color='#2ECC71', alpha=0.9, edgecolor='black', linewidth=0.5)

    # Styling
    ax.set_ylabel('Value (Units differ by metric)')
    ax.set_title('Problem 4 Results: Performance Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Annotate bars with values
    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, fontweight='bold')

    autolabel(bars1)
    autolabel(bars2)

    # Annotate "Better/Worse"
    # Time
    ax.text(x[0], max(baseline_values[0], phased_values[0]) + 15, '+55% Slower\n(Trade-off)', ha='center', color='#C0392B', fontsize=9)
    # Cost
    ax.text(x[1], max(baseline_values[1], phased_values[1]) + 15, '-36% Cheaper', ha='center', color='#27AE60', fontsize=9, fontweight='bold')
    # Emissions
    ax.text(x[2], max(baseline_values[2], phased_values[2]) + 15, '-75% Cleaner!', ha='center', color='#27AE60', fontsize=9, fontweight='bold')

    # Adjust Y limit to fit annotations
    ax.set_ylim(0, 800)

    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Results_KPI_Comparison.png'
    plt.savefig(output_path)
    print(f"Saved {output_path}")


def plot_strategy_evolution():
    """
    Visualizes the Strategy Evolution table (Alpha values per stage).
    """
    print("Generating Strategy Evolution Plot...")
    
    # Data
    stages_labels = ['Stage 1\nCamp', 'Stage 2\nBase', 'Stage 3\nCity']
    stages_x = [1, 2, 3]
    alphas = [0.60, 0.75, 0.80]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Line and Scatter
    ax.plot(stages_x, alphas, color='#2980B9', linewidth=3, zorder=1)
    ax.scatter(stages_x, alphas, color='#2980B9', s=150, zorder=2, edgecolor='white', linewidth=2)
    
    # Fill under
    ax.fill_between(stages_x, alphas, 0, color='#2980B9', alpha=0.1)
    
    # Labels
    ax.set_xticks(stages_x)
    ax.set_xticklabels(stages_labels)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('Space Elevator Usage Ratio ($\\alpha_{SE}$)')
    ax.set_title('Strategy Evolution: The Shift to Sustainability')
    
    # Annotate contexts (Rationale)
    rationales = [
        "Agile Hybrid\n(Speed Focus)",
        "Green Shift\n(Scale Focus)",
        "Sustainable Scale\n(Eco Focus)"
    ]
    
    for i, txt in enumerate(rationales):
        ax.annotate(txt, (stages_x[i], alphas[i]), xytext=(0, 20), textcoords='offset points', ha='center', 
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#2980B9", alpha=0.9))

    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Results_Strategy_Evolution.png'
    plt.savefig(output_path)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    plot_kpi_comparison()
    plot_strategy_evolution()
