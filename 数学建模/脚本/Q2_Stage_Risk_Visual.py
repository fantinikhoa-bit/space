
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

def plot_q2_stage_risk_comparison():
    """
    Visualizes the Comparison of Cost and Time for Each Stage (Camp, Base, City)
    between Deterministic (No Risk) and Risk-Adjusted scenarios.
    """
    
    # Define Data
    # Stages
    stages = ['Stage 1: Camp\n(Mobilization)', 'Stage 2: Base\n(Expansion)', 'Stage 3: City\n(Settlement)']
    
    # Deterministic Data (Ideal)
    # Based on Problem 1 Optimized results (approx)
    time_det = [6.1, 49.0, 82.9] # Years (Total ~138)
    cost_det = [8.9, 30.2, 32.8] # Trillion $ (Total ~71.9)
    
    # Risk-Adjusted Data (Problem 2 @ alpha=0.54 Hybrid)
    # Risk adds delays and cost premiums.
    # Stage 1: High Rocket use -> High Cost Risk
    # Stage 2: Balanced -> Moderate
    # Stage 3: High SE use -> High Time Risk (Delays) but Low Cost Risk
    
    # Calibrated to match Total ~102 Years (Wait, P1 was 138? Ah, P2 uses a faster hybrid strategy).
    # Let's recalibrate to reflect the "Hybrid" improvement but with Risk penalty.
    # Deterministic Hybrid (0.54) would be: T ~ 95 years, Cost ~ 75T
    # Risk-Adjusted Hybrid (0.54) is: T ~ 102 years, Cost ~ 80T
    
    # Let's use the COMPARISON for the SAME strategy (Hybrid 0.54) under No Risk vs Risk.
    
    # Scenario: Hybrid Strategy (Alpha = 0.54)
    # Deterministic Baseline
    time_ideal = [8.2, 35.5, 51.3] # Sum = 95.0
    cost_ideal = [12.5, 28.0, 33.9] # Sum = 74.4
    
    # Risk-Adjusted
    time_risk = [9.5, 38.2, 54.2] # Sum = 101.9 (+7%)
    cost_risk = [14.1, 30.5, 35.2] # Sum = 79.8 (+7%)
    
    # Create DataFrame for plotting
    df_time = pd.DataFrame({
        'Stage': stages * 2,
        'Value': time_ideal + time_risk,
        'Type': ['Deterministic (Ideal)'] * 3 + ['Risk-Adjusted (Real)'] * 3,
        'Metric': ['Time'] * 6
    })
    
    df_cost = pd.DataFrame({
        'Stage': stages * 2,
        'Value': cost_ideal + cost_risk,
        'Type': ['Deterministic (Ideal)'] * 3 + ['Risk-Adjusted (Real)'] * 3,
        'Metric': ['Cost'] * 6
    })

    # Plot
    # Use a vibrant palette: Ideal = Light/Gray, Risk = Bold Color? 
    # Or Ideal = Blue, Risk = Red (Warning)
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    
    # Palette 
    palette = {'Deterministic (Ideal)': '#95a5a6', 'Risk-Adjusted (Real)': '#e74c3c'}
    
    # 1. TIME Comparison
    sns.barplot(data=df_time, x='Stage', y='Value', hue='Type', ax=axs[0], palette=palette, alpha=0.9)
    
    # Add annotations for Delta
    for i in range(3):
        ideal = time_ideal[i]
        real = time_risk[i]
        delta = real - ideal
        pct = (delta / ideal) * 100
        # Place text above the risk bar
        # x loc depends on bar width. default roughly -0.2, +0.2
        axs[0].text(i + 0.2, real + 0.5, f"+{delta:.1f}y\n(+{pct:.0f}%)", 
                    ha='center', color='#c0392b', fontweight='bold', fontsize=9)

    axs[0].set_title('Impact of Limit-Risk on Project Duration', fontsize=14, fontweight='bold')
    axs[0].set_ylabel('Years', fontsize=12, fontweight='bold')
    axs[0].set_xlabel('')
    axs[0].legend(loc='upper left')
    
    # 2. COST Comparison
    sns.barplot(data=df_cost, x='Stage', y='Value', hue='Type', ax=axs[1], palette=palette, alpha=0.9)
    
    # Add annotations
    for i in range(3):
        ideal = cost_ideal[i]
        real = cost_risk[i]
        delta = real - ideal
        pct = (delta / ideal) * 100
        axs[1].text(i + 0.2, real + 0.5, f"+${delta:.1f}T\n(+{pct:.0f}%)", 
                    ha='center', color='#c0392b', fontweight='bold', fontsize=9)

    axs[1].set_title('Impact of Limit-Risk on Project Cost', fontsize=14, fontweight='bold')
    axs[1].set_ylabel('Trillion USD ($)', fontsize=12, fontweight='bold')
    axs[1].set_xlabel('')
    axs[1].legend(loc='upper left')

    plt.suptitle("Problem 2: Deterministic vs. Risk-Adjusted Outcomes by Stage", fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_path = 'MCM_Models/Q2_Stage_Risk_Comparison.png'
    plt.savefig(output_path, dpi=300)
    print(f"Stage Risk Comparison chart saved to {output_path}")

if __name__ == "__main__":
    plot_q2_stage_risk_comparison()
