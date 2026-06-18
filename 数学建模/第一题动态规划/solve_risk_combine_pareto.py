
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_combine():
    print("Loading Risk Simulation Data...")
    df = pd.read_csv('MCM_Models/Q1_New_DP/risk_simulation_raw.csv')
    
    # Separate Stages
    s1 = df[df['Stage'] == 1].reset_index(drop=True)
    s2 = df[df['Stage'] == 2].reset_index(drop=True)
    s3 = df[df['Stage'] == 3].reset_index(drop=True)
    
    print(f"Stage Points: S1={len(s1)}, S2={len(s2)}, S3={len(s3)}")
    
    # 3-Stage Cross Product (Brute Force 50^3 is fast enough)
    # We use numpy broadcasting for speed
    
    # Extract Vectors
    # Stage 1
    t1 = s1['Time_Mean'].values[:, None, None] # Shape (N, 1, 1)
    c1 = s1['Cost_Mean'].values[:, None, None]
    ts1 = s1['Time_Std'].values[:, None, None]
    cs1 = s1['Cost_Std'].values[:, None, None]
    
    # Stage 2
    t2 = s2['Time_Mean'].values[None, :, None] # Shape (1, N, 1)
    c2 = s2['Cost_Mean'].values[None, :, None]
    ts2 = s2['Time_Std'].values[None, :, None]
    cs2 = s2['Cost_Std'].values[None, :, None]
    
    # Stage 3
    t3 = s3['Time_Mean'].values[None, None, :] # Shape (1, 1, N)
    c3 = s3['Cost_Mean'].values[None, None, :]
    ts3 = s3['Time_Std'].values[None, None, :]
    cs3 = s3['Cost_Std'].values[None, None, :]
    
    # Combine (Sequential)
    # Means add
    T_total = t1 + t2 + t3
    C_total = c1 + c2 + c3
    
    # Stds add in quadrature (assuming independence)
    TS_total = np.sqrt(ts1**2 + ts2**2 + ts3**2)
    CS_total = np.sqrt(cs1**2 + cs2**2 + cs3**2)
    
    # Flatten
    flat_len = T_total.size
    data = {
        'Total_Time_Mean': T_total.ravel(),
        'Total_Cost_Mean': C_total.ravel(),
        'Total_Time_Std': TS_total.ravel(),
        'Total_Cost_Std': CS_total.ravel()
    }
    
    df_combined = pd.DataFrame(data)
    print(f"Total Combinations: {len(df_combined)}")
    
    # Sort and Filter Pareto (Mean vs Mean)
    df_combined = df_combined.sort_values('Total_Cost_Mean')
    
    # Pareto Filter
    pareto_points = []
    min_t = float('inf')
    
    # Iterate
    # Since sorted by Cost Ascending, we need strictly decreasing Time
    for row in df_combined.itertuples():
        if row.Total_Time_Mean < min_t:
            pareto_points.append(row)
            min_t = row.Total_Time_Mean
            
    df_pareto = pd.DataFrame(pareto_points)
    print(f"Risk-Adjusted Pareto Front Size: {len(df_pareto)}")
    
    return df_pareto

def plot_comparison(risk_df):
    # Load Deterministic
    try:
        det_df = pd.read_csv('MCM_Models/Q1_New_DP/Q1_DP_Pareto_Solutions.csv')
        has_det = True
    except:
        print("Could not load Q1_DP_Pareto_Solutions.csv")
        has_det = False
        
    sns.set_theme(style="whitegrid", context="talk")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 1. Deterministic Curve
    if has_det:
        plt.plot(det_df['Total_Time'], det_df['Total_Cost']/1e12, 
                 '--', color='gray', linewidth=2, label='Deterministic Baseline (Q1)')
                 
    # 2. Risk Curve (Mean)
    plt.plot(risk_df['Total_Time_Mean'], risk_df['Total_Cost_Mean']/1e12, 
             '-', color='#e74c3c', linewidth=3, label='Risk-Adjusted Expected Value')
             
    # 3. Risk Area (+/- 1 StdDev for Time and Cost)
    # We can perform a fill_between logic.
    # Since it's a parametric curve, fill_betweenx might be tricky or just filled polygon.
    # Simple approach: Fill vertical (Cost uncertainty)
    
    low_cost = (risk_df['Total_Cost_Mean'] - risk_df['Total_Cost_Std'])/1e12
    high_cost = (risk_df['Total_Cost_Mean'] + risk_df['Total_Cost_Std'])/1e12
    
    plt.fill_between(risk_df['Total_Time_Mean'], low_cost, high_cost, 
                     color='#e74c3c', alpha=0.2, label='Cost Risk (±1 Std)')
                     
    # Also Time Risk? Horizontal error bars are messy on a curve.
    # We can just mention it in title or legend.
    
    plt.xlabel('Total Project Duration (Years)', fontsize=14)
    plt.ylabel('Total Cost (Trillions USD)', fontsize=14)
    plt.title('Impact of Risks on Optimal Strategy (Q1 vs Risk Model)', fontsize=18, fontweight='bold')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig('MCM_Models/Q1_New_DP/Risk_vs_Deterministic_Comparison.png', dpi=300)
    print("Plot saved to MCM_Models/Q1_New_DP/Risk_vs_Deterministic_Comparison.png")
    
    # Save Data
    risk_df.to_csv('MCM_Models/Q1_New_DP/Risk_Corrected_Pareto.csv', index=False)

if __name__ == "__main__":
    df_pareto = load_and_combine()
    plot_comparison(df_pareto)
