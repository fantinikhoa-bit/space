
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Configuration (Must Match User Image) ---
class Config:
    # Demand Stages (kg)
    Q_total = 1.0e11
    # Consistent with Q1
    STAGES = {
        1: 0.10 * Q_total,
        2: 0.40 * Q_total,
        3: 0.50 * Q_total
    }
    
    # Space Elevator (SE) Basic Params
    SE_CAPACITY_PER_YEAR = 5.37e8  # kg/yr (Total 3 units)
    # Fixed Cost: From User Image "Total 3 units ~ 4500B" -> Yearly Maint?
    # Q1 Used F_SE = 4.5e10. We stick to this.
    SE_FIXED_COST_YEAR = 4.5e10    
    SE_UNIT_COST = 525.0           
    
    # Rocket Basic Params
    ROCKET_CAPACITY_PER_LAUNCH = 1.5e5  # kg
    ROCKET_LAUNCHES_PER_YEAR_MAX = 7300 # Total global max
    ROCKET_FIXED_COST_PER_LAUNCH = 3.25e6 # USD/launch
    ROCKET_UNIT_COST = 1012.5       # USD/kg
    
    # Simulation Params
    T_SIM = 500         # Runs per point (enough for distribution)
    T_MAX_YEARS = 200    # Cover worst case
    
    # --- Risk Parameters (User Image) ---
    # R1: Elevator Failure (Annual)
    P1_ELEVATOR_FAIL_YEAR = 0.02
    D1_ELEVATOR_FAIL_IMPACT = 0.5
    
    # R2: Capacity Decay (Monthly)
    P2_DECAY_MONTH = 0.03
    D2_DECAY_IMPACT = 0.10
    
    # R3: Rocket Explosion (Per Launch)
    P3_EXPLOSION = 0.05
    
    # R4: Fuel Chain Interruption (Monthly)
    P4_FUEL_MONTH = 0.05
    D4_FUEL_IMPACT = 0.4

def load_q1_strategies():
    strategies = {}
    for i in [1, 2, 3]:
        file = f'MCM_Models/Q1_New_DP/Stage_{i}_Front.csv'
        if os.path.exists(file):
            df = pd.read_csv(file)
            # We want to test the discrete points on the Pareto front
            # To save time, sample the front (e.g., 20 points)
            if len(df) > 20:
                indices = np.linspace(0, len(df)-1, 20, dtype=int)
                strategies[i] = df.iloc[indices].copy()
            else:
                strategies[i] = df.copy()
        else:
            print(f"Warning: {file} not found. Using default linspace.")
            # Fallback
            denom = Config.STAGES[i]
            alphas = np.linspace(0, 1, 11)
            strategies[i] = pd.DataFrame({'Alpha': alphas, 'q_SE': alphas*denom, 'Cost': 0, 'Time': 0})
            
    return strategies

def simulate_point(alpha, demand, cfg):
    # Same logic as before but optimized for single point call
    sim_results = {'Time': [], 'Cost': []}
    
    M_SE = alpha * demand
    M_R = (1 - alpha) * demand
    
    # Pre-calc constants
    Q_SE_base_mo = (cfg.SE_CAPACITY_PER_YEAR / 12.0)
    K_R_base_mo = (cfg.ROCKET_LAUNCHES_PER_YEAR_MAX / 12.0)
    
    for _ in range(cfg.T_SIM):
        t_years = 0.0
        c_tot = 0.0
        
        se_moved = 0.0
        r_moved = 0.0
        
        # State
        decay_fac = 1.0
        
        cost_se_var = 0.0
        cost_r_var = 0.0
        cost_r_fixed = 0.0
        
        finished_year = False
        
        for year in range(1, cfg.T_MAX_YEARS + 1):
            # R1
            if np.random.rand() < cfg.P1_ELEVATOR_FAIL_YEAR:
                eff_yr_fac = (1.0 - cfg.D1_ELEVATOR_FAIL_IMPACT)
            else:
                eff_yr_fac = 1.0
                
            q_se_yr_capability = 0.0
            q_r_yr_capability = 0.0
            
            # Monthly Loop
            for m in range(12):
                # R2: Transient Maintenance Delay (Affects THIS month only)
                if np.random.rand() < cfg.P2_DECAY_MONTH:
                    decay_fac = (1.0 - cfg.D2_DECAY_IMPACT)
                else:
                    decay_fac = 1.0
                    
                q_se_mo = Q_SE_base_mo * eff_yr_fac * decay_fac
                
                # R4
                if np.random.rand() < cfg.P4_FUEL_MONTH:
                    fuel_fac = (1.0 - cfg.D4_FUEL_IMPACT)
                else:
                    fuel_fac = 1.0
                    
                launches_mo = K_R_base_mo * fuel_fac
                
                # R3 - Capacity
                # Expected payload per launch = Cap * (1-P3)
                # Or simulation? Let's use expectation for speed/stability as variance is high freq
                payload_eff = cfg.ROCKET_CAPACITY_PER_LAUNCH * (1.0 - cfg.P3_EXPLOSION)
                q_r_mo = launches_mo * payload_eff
                
                # Accumulate Capability (Capacity)
                q_se_yr_capability += q_se_mo
                q_r_yr_capability += q_r_mo
                
                # --- APPLY MOVEMENT ---
                # Check SE need
                needed_se = max(0, M_SE - se_moved)
                moved_se_now = min(needed_se, q_se_mo)
                se_moved += moved_se_now
                cost_se_var += moved_se_now * cfg.SE_UNIT_COST
                
                # Check Rocket need
                needed_r = max(0, M_R - r_moved)
                moved_r_now = min(needed_r, q_r_mo)
                r_moved += moved_r_now
                
                # Cost Rocket
                # Launches Used? 
                # delivered = launches * cap * (1-p3)
                # launches = delivered / (cap * (1-p3))
                if moved_r_now > 0:
                    launches_used = moved_r_now / payload_eff
                    cost_r_fixed += launches_used * cfg.ROCKET_FIXED_COST_PER_LAUNCH
                    cost_r_var += moved_r_now * cfg.ROCKET_UNIT_COST
                    
                if se_moved >= M_SE - 1.0 and r_moved >= M_R - 1.0:
                    break # Month loop break
            
            # End Year Costs
            c_tot += cfg.SE_FIXED_COST_YEAR
            
            if se_moved >= M_SE - 1.0 and r_moved >= M_R - 1.0:
                 # Fraction? Just use year index for integer constraint or simple
                 t_years = year
                 finished_year = True
                 break
        
        if not finished_year:
            t_years = cfg.T_MAX_YEARS
            
        c_tot += (cost_se_var + cost_r_var + cost_r_fixed)
        
        sim_results['Time'].append(t_years)
        sim_results['Cost'].append(c_tot)
        
    return sim_results

def run_stage_analysis():
    print("Loading Deterministic Pareto Fronts...")
    strats = load_q1_strategies()
    cfg = Config()
    
    all_results = []
    
    for stage_id, df_strat in strats.items():
        print(f"\n--- Analyzing Stage {stage_id} ---")
        demand = Config.STAGES[stage_id]
        
        # Analyze each strategy point
        for idx, row in df_strat.iterrows():
            alpha = row['Alpha']
            det_time = row['Time']
            det_cost = row['Cost']
            
            # Run Sim
            sim_res = simulate_point(alpha, demand, cfg)
            
            t_mean = np.mean(sim_res['Time'])
            c_mean = np.mean(sim_res['Cost'])
            t_std = np.std(sim_res['Time'])
            c_std = np.std(sim_res['Cost'])
            
            all_results.append({
                'Stage': stage_id,
                'Alpha': alpha,
                'Det_Time': det_time,
                'Det_Cost': det_cost,
                'Risk_Time_Mean': t_mean,
                'Risk_Cost_Mean': c_mean,
                'Risk_Time_Std': t_std,
                'Risk_Cost_Std': c_std
            })
            
            if idx % 5 == 0:
                print(f"   Alpha {alpha:.2%}: Det_T={det_time:.1f} -> Risk_T={t_mean:.1f} (+/- {t_std:.1f})")
                
    results_df = pd.DataFrame(all_results)
    results_df.to_csv('MCM_Models/Q1_New_DP/Risk_Sensitivity_Per_Stage.csv', index=False)
    
    # --- Plotting ---
    plot_stage_comparisons(results_df)

def plot_stage_comparisons(df):
    stages = df['Stage'].unique()
    sns.set_theme(style="whitegrid")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for i, stage in enumerate(stages):
        ax = axes[i]
        subset = df[df['Stage'] == stage]
        
        # Plot Deterministic Line
        ax.plot(subset['Det_Time'], subset['Det_Cost']/1e12, 'b--', label='Deterministic (Q1)', alpha=0.7)
        
        # Plot Risk Mean
        ax.plot(subset['Risk_Time_Mean'], subset['Risk_Cost_Mean']/1e12, 'ro-', label='Risk Expected Value')
        
        # Error Bars (Fill between)
        # Sort by Time for fill calculation
        subset_sorted = subset.sort_values('Risk_Time_Mean')
        ax.fill_between(subset_sorted['Risk_Time_Mean'], 
                        (subset_sorted['Risk_Cost_Mean'] - subset_sorted['Risk_Cost_Std'])/1e12,
                        (subset_sorted['Risk_Cost_Mean'] + subset_sorted['Risk_Cost_Std'])/1e12,
                        color='red', alpha=0.15)
        
        ax.set_title(f'Stage {int(stage)} Risk Impact')
        ax.set_xlabel('Time (Years)')
        ax.set_ylabel('Cost (Trillion USD)')
        if i == 0:
            ax.legend()
            
    plt.tight_layout()
    plt.savefig('MCM_Models/Q1_New_DP/Stages_Risk_Comparison.png', dpi=300)
    print("Comparison Plot Saved.")

if __name__ == "__main__":
    run_stage_analysis()
