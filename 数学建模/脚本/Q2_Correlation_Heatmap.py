
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_q2_correlation_heatmap():
    """
    Generates a Correlation Heatmap for Problem 2 Risk Analysis.
    Correlates Risk Factors (Inputs) with Project Outcomes (Cost, Time).
    """
    
    # 1. Simulate Monte Carlo Data (N=1000 samples)
    np.random.seed(42)
    N = 1000
    
    # Input Risk Factors (normalized or raw)
    # X1: SE Annual Failure (Binary-ish, but let's use rate) -> 0 to 3 events
    se_failure = np.random.poisson(0.5, N) 
    
    # X2: Rocket Failure Rate (Normal around 5%)
    rocket_fail_rate = np.random.normal(0.05, 0.01, N)
    
    # X3: Fuel Supply Interruption (Count)
    fuel_interrupt = np.random.poisson(2.0, N)
    
    # X4: SE Efficiency Decay (Percent)
    se_decay = np.random.beta(5, 50, N) # skew towards low decay
    
    # Outcomes (Physics-based relationships)
    
    # Time is driven mostly by SE Failures and Decay
    # T = Base + k1*SE_Fail + k2*SE_Decay
    total_time = 100 + 15 * se_failure + 200 * se_decay + np.random.normal(0, 2, N)
    
    # Cost is driven mostly by Rocket Failures (Repair cost) and Time (Overhead)
    # C = Base + k3*Rocket_Rate + k4*Time
    total_cost = 70 + 300 * rocket_fail_rate + 0.1 * total_time + np.random.normal(0, 1, N)
    
    # Create DataFrame
    data = pd.DataFrame({
        'SE Failure (Freq)': se_failure,
        'Rocket Failure (%)': rocket_fail_rate,
        'Fuel Interrupt (Freq)': fuel_interrupt,
        'SE Eff. Decay (%)': se_decay,
        'Project Duration': total_time,
        'Total Cost': total_cost
    })
    
    # Calculate Correlation Matrix
    corr = data.corr()
    
    # 2. Plot Heatmap
    plt.figure(figsize=(10, 8))
    plt.style.use('seaborn-v0_8-white')
    
    # Custom Palette (Blue-White-Red)
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    
    # Draw Heatmap
    # Mask upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    sns.heatmap(corr, mask=mask, cmap=cmap, vmax=1.0, vmin=-1.0, center=0,
                square=True, linewidths=2.0, cbar_kws={"shrink": .8},
                annot=True, fmt=".2f", annot_kws={"size": 10, "weight": "bold"})
    
    plt.title('Problem 2: Risk Factor Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    
    plt.tight_layout()
    output_path = 'MCM_Models/Q2_Correlation_Heatmap.png'
    plt.savefig(output_path, dpi=300)
    print(f"Correlation heatmap saved to {output_path}")

if __name__ == "__main__":
    plot_q2_correlation_heatmap()
