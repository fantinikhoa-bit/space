import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import milp, LinearConstraint, Bounds
import time

class ModelConfig:
    # --- 1. Material Demand (kg) ---
    Q_total = 1.0e11
    Q_stages = [
        0.10 * Q_total, # Stage 1
        0.40 * Q_total, # Stage 2
        0.50 * Q_total  # Stage 3
    ]
    
    # --- 2. Space Elevator (SE) Parameters ---
    C_SE = 5.37e8       # kg/yr (Total Capacity)
    p_SE = 525.0        # USD/kg
    F_SE = 4.5e10       # USD/yr (Fixed Maintenance)
    
    # --- 3. Rocket Parameters ---
    c_single = 1.5e5    # kg/launch
    p_R = 1012.5        # USD/kg
    f_launch = 3.25e6   # USD/launch (Fixed per launch)
    N_R_max = 7300      # launches/yr (Total global rate)
    
    # Resolution for Pareto Front
    num_points = 50

def solve_stage_ip(stage_idx, Q_raw, config):
    print(f"\n--- Solving Stage {stage_idx+1} (Q={Q_raw:.1e} kg) with IP ---")
    
    # Scaling Factors to improve numerical stability for MIP
    S_mass = 1.0e9 # Scale mass to billion kg (10^9)
    S_cost = 1.0e12 # Scale cost to Trillion USD (10^12)
    
    # Scaled Parameters
    Q = Q_raw / S_mass
    p_SE = config.p_SE * S_mass / S_cost
    p_R = config.p_R * S_mass / S_cost
    F_SE = config.F_SE / S_cost
    f_launch = config.f_launch / S_cost
    c_single = config.c_single / S_mass
    C_SE = config.C_SE / S_mass
    N_R_max = config.N_R_max
    
    # Variables: x = [m_SE', m_R', n_launch, T]
    # Indices: 0, 1, 2, 3
    
    # Objective Coefficients (Minimize Cost)
    # Cost = p_SE * m_SE + p_R * m_R + f_launch * n_launch + F_SE * T
    c_cost = np.array([p_SE, p_R, f_launch, F_SE])
    
    # Objective Coefficients (Minimize Time)
    c_time = np.array([0, 0, 0, 1])
    
    # 1. Demand: m_SE' + m_R' = Q
    A_eq = [[1, 1, 0, 0]]
    b_eq = [Q]
    
    # 2. Rocket Cap: m_R' <= c_single * n_launch
    #    m_R' - c_single * n_launch <= 0
    # 3. SE Rate: m_SE' <= C_SE * T
    #    m_SE' - C_SE * T <= 0
    # 4. Rocket Rate: n_launch <= N_R_max * T
    #    n_launch - N_R_max * T <= 0
    
    A_ineq = [
        [0, 1, -c_single, 0], 
        [1, 0, 0, -C_SE],     
        [0, 0, 1, -N_R_max]   
    ]
    # Upper bounds for ineqs is 0
    
    # Variable Integrality
    # 0=m_SE (Cont), 1=m_R (Cont), 2=n_launch (Int), 3=T (Cont)
    integrality = [0, 0, 1, 0] 
    
    # Constraints
    A_all = np.vstack([A_eq, A_ineq])
    # Lower bounds: Eq needs [Q], Ineq needs [-inf]
    # Upper bounds: Eq needs [Q], Ineq needs [0]
    
    lb_all = [Q] + [-np.inf]*3
    ub_all = [Q] + [0]*3
    
    constraints = LinearConstraint(A_all, lb_all, ub_all)
    
    # --- Step A: Find Min Time (T_min) ---
    res_t = milp(c=c_time, constraints=constraints, integrality=integrality)
    
    if not res_t.success:
        print("Failed to find Min Time!")
        return None
        
    t_min = res_t.x[3]
    print(f"  Min Time: {t_min:.4f} years")
    
    # --- Step B: Find Min Cost ---
    res_c = milp(c=c_cost, constraints=constraints, integrality=integrality)
    
    if not res_c.success:
        print("Failed to find Min Cost!")
        return None
        
    t_at_min_cost = res_c.x[3]
    min_cost_val = res_c.fun * S_cost
    print(f"  Max Time (Min Cost Sol): {t_at_min_cost:.4f} years (Cost: ${min_cost_val/1e12:.3f}T)")
    
    # --- Step C: Generate Pareto ---
    t_grid = np.linspace(t_min, t_at_min_cost, config.num_points)
    
    pareto_data = []
    
    # Add a small buffer to bounds to ensure feasibility of t_min/t_max points
    for t_lim in t_grid:
        if t_lim < t_min: t_lim = t_min
        
        # Add constraint T <= t_lim
        # 0*x0 ... + 1*x3 <= t_lim
        
        A_new = np.vstack([A_all, [0, 0, 0, 1]])
        lb_new = lb_all + [-np.inf]
        # Use simple numbers
        ub_new = ub_all + [t_lim] 
        
        cons_new = LinearConstraint(A_new, lb_new, ub_new)
        
        res = milp(c=c_cost, constraints=cons_new, integrality=integrality)
        
        if res.success:
            p_cost = res.fun * S_cost
            p_time = res.x[3]
            p_mse = res.x[0] * S_mass
            p_mr = res.x[1] * S_mass
            p_nlaunch = res.x[2]
            
            pareto_data.append({
                'Time': p_time,
                'Cost': p_cost,
                'q_SE': p_mse,
                'q_R': p_mr,
                'Rocket_Launches': p_nlaunch,
                'Alpha': p_mse / Q_raw
            })
            
    df = pd.DataFrame(pareto_data)
    df = df.round({'Time': 4, 'Cost': 2})
    df = df.drop_duplicates().sort_values('Time')
    
    return df

def solve_ip_dp():
    config = ModelConfig()
    stage_dfs = []
    
    # 1. Process Stages
    for idx, Q in enumerate(config.Q_stages):
        df = solve_stage_ip(idx, Q, config)
        if df is not None:
            stage_dfs.append(df)
            df.to_csv(f'MCM_Models/Q1_New_DP/Stage_{idx+1}_IP_Front.csv', index=False)
        else:
            print(f"Skipping Stage {idx+1} due to solver failure.")
            return

    # 2. Combine Stages (Convolution)
    print("\nCombining Stages...")
    
    def combine_fronts(f1, f2):
        # Cross product
        t1 = f1['Time'].values[:, None]
        t2 = f2['Time'].values[None, :]
        T_sum = (t1 + t2).ravel()
        
        c1 = f1['Cost'].values[:, None]
        c2 = f2['Cost'].values[None, :]
        C_sum = (c1 + c2).ravel()
        
        combined = pd.DataFrame({'Total_Time': T_sum, 'Total_Cost': C_sum})
        combined = combined.sort_values('Total_Cost')
        
        # Pareto Filter (Min Time for given Cost)
        # Or Min Time scane
        pareto_pts = []
        min_t = float('inf')
        
        for row in combined.itertuples():
            if row.Total_Time < min_t: # Strictly better time
                pareto_pts.append(row)
                min_t = row.Total_Time
                
        return pd.DataFrame(pareto_pts)
    
    s12 = combine_fronts(stage_dfs[0], stage_dfs[1])
    print(f"Stage 1+2 Front Size: {len(s12)}")
    
    # Combine (S1+S2) + S3
    final_df = combine_fronts(s12.rename(columns={'Total_Time':'Time', 'Total_Cost':'Cost'}), stage_dfs[2])
    print(f"Final Front Size: {len(final_df)}")
    
    # Save
    final_df.to_csv('MCM_Models/Q1_New_DP/Q1_IP_Pareto_Solutions.csv', index=False)
    
    # Plot
    sns.set_theme(style="whitegrid", context="talk")
    plt.figure(figsize=(10, 6))
    
    plt.plot(final_df['Total_Time'], final_df['Total_Cost']/1e12, 'o-', 
             color='#8e44ad', linewidth=2, markersize=5, label='IP Pareto Front')
    
    plt.xlabel('Total Project Duration (Years)')
    plt.ylabel('Total Cost (Trillions USD)')
    plt.title('Stage-Based Integer Programming Optimization Results')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    out_path = 'MCM_Models/Q1_New_DP/Q1_IP_Result_Plot.png'
    plt.savefig(out_path, dpi=300)
    print(f"\nPlot saved to {out_path}")

if __name__ == "__main__":
    solve_ip_dp()
