
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time

class ModelConfig:
    # --- 1. Material Demand (kg) ---
    # User Table: Total 100,000,000 Tons = 1.0e11 kg
    Q_total = 1.0e11
    
    # User Table: Split 10% (Camp), 40% (Base), 50% (City)
    Q_stages = [
        0.10 * Q_total, # Stage 1: 1.0e10
        0.40 * Q_total, # Stage 2: 4.0e10
        0.50 * Q_total  # Stage 3: 5.0e10
    ]
    
    # --- 2. Space Elevator (SE) Parameters ---
    # Capacity: 179,000 tons/year per unit. 3 Units.
    # Total Cap = 1.79e5 * 1000 * 3 = 5.37e8 kg/yr
    C_SE = 5.37e8 
    
    # Unit Cost: 450-600 USD/kg -> Mean 525
    p_SE = 525.0 
    
    # Fixed Cost (Maintenance/Ops):
    # Table lists Construction Cost: 1200-1800 Billion/unit. Total ~4500B.
    # Formula uses F_SE * T (Time). This implies F_SE is Annual Fixed Cost.
    # Typically 1% of CapEx. 1% of $4.5T = $45B/yr = 4.5e10.
    F_SE = 4.5e10 
    
    # --- 3. Rocket Parameters ---
    # Single Launch Cap: 150 tons = 1.5e5 kg
    c_single = 1.5e5 
    
    # Unit Cost: 90-112.5 Wan USD / Ton
    # 1 Wan = 10,000. 100 Wan = 1M.
    # 90-112.5 * 10000 = 900,000 - 1,125,000 USD / Ton.
    # USD/kg = 900 - 1125. Mean = 1012.5.
    p_R = 1012.5 
    
    # Fixed Launch Cost: "Launch Site Enable Cost" ???
    # Table: 250-400 Wan USD = $2.5M - $4M. Mean $3.25M.
    # This might be `f_launch` (per launch fixed) or Site Setup.
    # Context "Start Cost" usually means Setup.
    # But Formula `Cost = q*p + N * f_launch`.
    # Usually Launch Vehicle Fixed Cost is high.
    # If this is Site Setup, it's tiny.
    # Let's assume `f_launch` is the per-launch fixed operations cost. 
    # $3.25M is reasonable for Ground Ops.
    f_launch = 3.25e6
    
    # Constraints
    # 730 launches/year/site * 10 sites = 7300
    N_R_max = 7300
    
    # Reduce resolution for speed
    resolution = 200 

def calculate_stage_pareto(stage_idx, Q_j, config):
    print(f"Calculating Pareto Front for Stage {stage_idx+1} (Q={Q_j:.1e} kg)...")
    
    results = []
    
    # Use config resolution
    steps = config.resolution
    qs_se_values = np.linspace(0, Q_j, steps)
    
    # Vectorized Calculation
    q_SE = qs_se_values
    q_R = Q_j - q_SE
    
    # Time
    t_SE = np.where(q_SE > 0, q_SE / config.C_SE, 0.0)
    
    n_launch = np.ceil(q_R / config.c_single)
    t_R = np.where(q_R > 0, n_launch / config.N_R_max, 0.0)
    
    T_j = np.maximum(t_SE, t_R)
    
    # Cost
    # Only active maintenance for time used? Or full duration? 
    # Use t_SE for maintenance cost duration as per formula logic
    current_t_SE = t_SE 
    
    c_SE = q_SE * config.p_SE + config.F_SE * current_t_SE
    c_R = q_R * config.p_R + n_launch * config.f_launch
    C_j = c_SE + c_R
    
    df = pd.DataFrame({
        'q_SE': q_SE,
        'q_R': q_R,
        'Time': T_j,
        'Cost': C_j,
        'Alpha': q_SE/Q_j,
        'Rocket_Launches': n_launch
    })
    
    # Pareto Filter
    df = df.sort_values('Cost')
    
    # Vectorized Pareto Filter (Cummin)
    # If Cost is sorted, Time must be strictly decreasing to be Pareto
    # We want min Time for a given Cost.
    # Since sorted by Cost ascending, the first Time encountered that is lower than all previous is Pareto.
    
    # Calculate cumulative min of Time
    min_time_so_far = df['Time'].cummin()
    
    # Keep rows where Time < min_time_of_previous_rows (strictly better)
    # Actually, cummin includes self. We need shift.
    # But simpler: mask = time < everything_before
    # Iterate is safer for strictly Pareto
    
    pareto_points = []
    min_t = float('inf')
    for row in df.itertuples():
        if row.Time < min_t:
            pareto_points.append(row)
            min_t = row.Time
    
    return pd.DataFrame(pareto_points)

def solve_dp():
    config = ModelConfig()
    
    stage_fronts = []
    
    # 1. Calc Stages
    for idx, Q in enumerate(config.Q_stages):
        front = calculate_stage_pareto(idx, Q, config)
        stage_fronts.append(front)
        
        # Analyze Stage Extremes
        min_time_row = front.loc[front['Time'].idxmin()]
        min_cost_row = front.loc[front['Cost'].idxmin()]
        
        # Save Stage Front
        front.to_csv(f'MCM_Models/Q1_New_DP/Stage_{idx+1}_Front.csv', index=False)
        
        print(f"  -> Stage {idx+1} Analysis:")
        print(f"     Min Time Strategy: {min_time_row['Time']:.2f} Years, Cost: ${min_time_row['Cost']/1e12:.3f}T, Alpha: {min_time_row['Alpha']:.2%}")
        print(f"     Min Cost Strategy: {min_time_row['Time']:.2f} Years (Cost-Focused: ${min_cost_row['Cost']/1e12:.3f}T, T={min_cost_row['Time']:.2f}), Alpha: {min_cost_row['Alpha']:.2%}")
        print(f"     Front Size: {len(front)}")
        
        # Analyze Stage Knee Point (Optimal Trade-off)
        t = front['Time'].values
        c = front['Cost'].values
        
        # Normalize
        norm_t = (t - t.min()) / (t.max() - t.min()) if t.max() > t.min() else t*0
        norm_c = (c - c.min()) / (c.max() - c.min()) if c.max() > c.min() else c*0
        
        dist = np.sqrt(norm_t**2 + norm_c**2)
        knee_idx = dist.argmin()
        knee = front.iloc[knee_idx]
        
        # Calculate Detailed Logistics
        se_mass = knee['q_SE']
        rocket_mass = knee['q_R']
        launches = np.ceil(rocket_mass / config.c_single)
        
        print(f"     [Optimal Knee Point]:")
        print(f"       Time: {knee['Time']:.2f} Yr, Cost: ${knee['Cost']/1e12:.2f}T, SE Ratio: {knee['Alpha']:.1%}")
        print(f"       Logistics: SE Mass = {se_mass:.2e} kg, Rocket Mass = {rocket_mass:.2e} kg")
        print(f"       Rocket Activity: {int(launches):,} Total Launches ({launches/knee['Time']:.0f}/yr)")

    # 2. DP Combine
    # Stage 1 + Stage 2
    # Instead of full cross product, we can sample?
    # Or just do it. 200x200 = 40,000. Very fast.
    
    print("Combining S1 + S2...")
    f1 = stage_fronts[0]
    f2 = stage_fronts[1]
    
    # Cross join using broadcasting or meshgrid
    # Time: T1 + T2
    # Cost: C1 + C2
    
    t1 = f1['Time'].values[:, None] # (N, 1)
    t2 = f2['Time'].values[None, :] # (1, M)
    T_12 = t1 + t2 # (N, M)
    
    c1 = f1['Cost'].values[:, None]
    c2 = f2['Cost'].values[None, :]
    C_12 = c1 + c2
    
    # Flatten
    T_flat = T_12.ravel()
    C_flat = C_12.ravel()
    
    # Filter Pareto (S1+S2)
    df_12 = pd.DataFrame({'Total_Time': T_flat, 'Total_Cost': C_flat})
    df_12 = df_12.sort_values('Total_Cost')
    
    # Fast filtering
    pareto_mask = []
    min_t = float('inf')
    times = df_12['Total_Time'].values
    
    # Numba would be faster but raw python loop on 40k is fine
    keep_indices = []
    for i in range(len(times)):
        if times[i] < min_t:
            keep_indices.append(i)
            min_t = times[i]
            
    df_12_pareto = df_12.iloc[keep_indices]
    print(f"  -> Combined 1+2 Front Size: {len(df_12_pareto)}")
    
    # 3. Combine with S3
    print("Combining (S1+S2) + S3...")
    f3 = stage_fronts[2]
    
    t12 = df_12_pareto['Total_Time'].values[:, None]
    t3 = f3['Time'].values[None, :]
    T_final = t12 + t3
    
    c12 = df_12_pareto['Total_Cost'].values[:, None]
    c3 = f3['Cost'].values[None, :]
    C_final = c12 + c3
    
    T_flat_final = T_final.ravel()
    C_flat_final = C_final.ravel()
    
    df_final = pd.DataFrame({'Total_Time': T_flat_final, 'Total_Cost': C_flat_final})
    df_final = df_final.sort_values('Total_Cost')
    
    keep_indices_final = []
    min_t = float('inf')
    times_f = df_final['Total_Time'].values
    
    for i in range(len(times_f)):
        if times_f[i] < min_t:
            keep_indices_final.append(i)
            min_t = times_f[i]
            
    final_df = df_final.iloc[keep_indices_final]
    print(f"  -> Final Front Size: {len(final_df)}")
    
    # Save
    final_df.to_csv('MCM_Models/Q1_New_DP/Q1_DP_Pareto_Solutions.csv', index=False)
    
    # Plot
    sns.set_theme(style="whitegrid", context="talk")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Points
    plt.plot(final_df['Total_Time'], final_df['Total_Cost']/1e12, 'o-', color='#3498db', linewidth=2, markersize=4, label='Pareto Front')
    
    plt.xlabel('Total Project Duration (Years)', fontsize=12)
    plt.ylabel('Total Cost (Trillions USD)', fontsize=12)
    plt.title('Stage-Based DP Optimization Results (Q1)', fontsize=16, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig('MCM_Models/Q1_New_DP/Q1_DP_Result_Plot.png', dpi=300)
    print("Plot saved to MCM_Models/Q1_New_DP/Q1_DP_Result_Plot.png")

if __name__ == "__main__":
    solve_dp()
