
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

def plot_q2_phased_comparison_rainbow():
    """
    Visualizes the Phased Comparison (Time & Cost) for Deterministic vs Risk-Adjusted scenarios.
    Style: Vibrant/Rainbow as requested.
    """
    
    # Data
    stages = ['Camp', 'Base', 'City']
    
    # Time (Years)
    time_det = [8.2, 35.5, 51.3]
    time_risk = [9.5, 38.2, 54.2]
    
    # Cost (Trillion $)
    cost_det = [12.5, 28.0, 33.9]
    cost_risk = [14.1, 30.5, 35.2]
    
    # Setup Figure
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    plt.suptitle("Problem 2: Phased Risk Impact Analysis", fontsize=18, fontweight='bold', y=1.05)
    
    bar_width = 0.35
    index = np.arange(len(stages))
    
    # --- Plot 1: Time Comparison ---
    # Colors: Deterministic (Blue/Cool), Risk (Red/Hot/Rainbow?)
    # Let's use Gradient colors for the bars
    
    # Time Bars
    rects1 = axs[0].bar(index, time_det, bar_width, label='Deterministic (Ideal)', 
                        color='#3498db', alpha=0.8, edgecolor='black', linewidth=1)
    
    rects2 = axs[0].bar(index + bar_width, time_risk, bar_width, label='Risk-Adjusted (Real)', 
                        color='#e74c3c', alpha=0.9, edgecolor='black', linewidth=1, hatch='//')
    
    # Annotations
    for i, (t_d, t_r) in enumerate(zip(time_det, time_risk)):
        diff = t_r - t_d
        # Draw arrow or line?
        axs[0].annotate(f'+{diff:.1f}y', 
                        xy=(index[i] + bar_width, t_r), 
                        xytext=(0, 5), textcoords='offset points',
                        ha='center', fontweight='bold', color='#c0392b')
    
    axs[0].set_xlabel('Development Stage', fontsize=12, fontweight='bold')
    axs[0].set_ylabel('Duration (Years)', fontsize=12, fontweight='bold')
    axs[0].set_title('Phase Duration: Ideal vs Risk', fontsize=14)
    axs[0].set_xticks(index + bar_width / 2)
    axs[0].set_xticklabels(stages, fontsize=11)
    axs[0].legend(loc='upper left')
    axs[0].grid(axis='y', linestyle='--', alpha=0.3)

    # --- Plot 2: Cost Comparison ---
    # Cost Bars
    rects3 = axs[1].bar(index, cost_det, bar_width, label='Deterministic (Ideal)', 
                        color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1)
    
    rects4 = axs[1].bar(index + bar_width, cost_risk, bar_width, label='Risk-Adjusted (Real)', 
                        color='#9b59b6', alpha=0.9, edgecolor='black', linewidth=1, hatch='//')

    # Annotations
    for i, (c_d, c_r) in enumerate(zip(cost_det, cost_risk)):
        diff = c_r - c_d
        pct = (diff/c_d)*100
        axs[1].annotate(f'+${diff:.1f}T\n(+{pct:.0f}%)', 
                        xy=(index[i] + bar_width, c_r), 
                        xytext=(0, 5), textcoords='offset points',
                        ha='center', fontweight='bold', color='#8e44ad')

    axs[1].set_xlabel('Development Stage', fontsize=12, fontweight='bold')
    axs[1].set_ylabel('Cost ($ Trillion)', fontsize=12, fontweight='bold')
    axs[1].set_title('Phase Cost: Ideal vs Risk', fontsize=14)
    axs[1].set_xticks(index + bar_width / 2)
    axs[1].set_xticklabels(stages, fontsize=11)
    axs[1].legend(loc='upper left')
    axs[1].grid(axis='y', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    output_path = 'MCM_Models/Q2_Phased_Risk_Comparison.png'
    plt.savefig(output_path, dpi=300)
    print(f"Comparison chart saved to {output_path}")

if __name__ == "__main__":
    plot_q2_phased_comparison_rainbow()
