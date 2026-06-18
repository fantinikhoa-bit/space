
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
    SE_FIXED_COST_YEAR = 4.5e10    
    SE_UNIT_COST = 525.0           
    
    # Rocket Basic Params
    ROCKET_CAPACITY_PER_LAUNCH = 1.5e5  # kg
    ROCKET_LAUNCHES_PER_YEAR_MAX = 7300 # Total global max
    ROCKET_FIXED_COST_PER_LAUNCH = 3.25e6 # USD/launch
    ROCKET_UNIT_COST = 1012.5       # USD/kg
    
    # Simulation Params
    T_SIM = 200         # Runs per point (Reduced for speed in breakdown)
    T_MAX_YEARS = 250   # Cover worst case
    
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
            # Sample critical points: Min Cost, Min Time, Balanced (Median)
            # To get a good spread without running 1000s of sims
            if len(df) > 5:
                # Select min cost, min time, and 3 intermediate
                indices = np.linspace(0, len(df)-1, 5, dtype=int)
                strategies[i] = df.iloc[indices].copy()
            else:
                strategies[i] = df.copy()
        else:
            print(f"Warning: {file} not found. Using default linspace.")
            denom = Config.STAGES[i]
            alphas = np.linspace(0, 1, 5)
            strategies[i] = pd.DataFrame({'Alpha': alphas, 'q_SE': alphas*denom, 'Cost': 0, 'Time': 0})
            
    return strategies

def simulate_point_scenario(alpha, demand, cfg, active_risks):
    """
    active_risks: list of strings, e.g., ['R1', 'R3']
    """
    sim_results = {'Time': [], 'Cost': []}
    
    M_SE = alpha * demand
    M_R = (1 - alpha) * demand
    
    Q_SE_base_mo = (cfg.SE_CAPACITY_PER_YEAR / 12.0)
    K_R_base_mo = (cfg.ROCKET_LAUNCHES_PER_YEAR_MAX / 12.0)
    
    # Params based on active risks
    p1 = cfg.P1_ELEVATOR_FAIL_YEAR if 'R1' in active_risks else 0.0
    p2 = cfg.P2_DECAY_MONTH if 'R2' in active_risks else 0.0
    p3 = cfg.P3_EXPLOSION if 'R3' in active_risks else 0.0
    p4 = cfg.P4_FUEL_MONTH if 'R4' in active_risks else 0.0
    
    for _ in range(cfg.T_SIM):
        t_years = 0.0
        c_tot = 0.0
        
        se_moved = 0.0
        r_moved = 0.0
        
        cost_se_var = 0.0
        cost_r_var = 0.0
        cost_r_fixed = 0.0
        
        finished_year = False
        
        for year in range(1, cfg.T_MAX_YEARS + 1):
            # R1: Elevator Failure
            if np.random.rand() < p1:
                eff_yr_fac = (1.0 - cfg.D1_ELEVATOR_FAIL_IMPACT)
            else:
                eff_yr_fac = 1.0
                
            q_se_yr_capability = 0.0
            q_r_yr_capability = 0.0
            
            # Monthly Loop
            for m in range(12):
                # R2: Maintenance
                if np.random.rand() < p2:
                    decay_fac = (1.0 - cfg.D2_DECAY_IMPACT)
                else:
                    decay_fac = 1.0
                    
                q_se_mo = Q_SE_base_mo * eff_yr_fac * decay_fac
                
                # R4: Fuel Chain
                if np.random.rand() < p4:
                    fuel_fac = (1.0 - cfg.D4_FUEL_IMPACT)
                else:
                    fuel_fac = 1.0
                    
                launches_mo = K_R_base_mo * fuel_fac
                
                # R3: Explosion (Average Capacity Reduction)
                payload_eff = cfg.ROCKET_CAPACITY_PER_LAUNCH * (1.0 - p3)
                q_r_mo = launches_mo * payload_eff
                
                # Accumulate Capability
                q_se_yr_capability += q_se_mo
                q_r_yr_capability += q_r_mo
                
                # --- APPLY MOVEMENT ---
                needed_se = max(0, M_SE - se_moved)
                moved_se_now = min(needed_se, q_se_mo)
                se_moved += moved_se_now
                cost_se_var += moved_se_now * cfg.SE_UNIT_COST
                
                needed_r = max(0, M_R - r_moved)
                moved_r_now = min(needed_r, q_r_mo)
                r_moved += moved_r_now
                
                if moved_r_now > 0:
                    launches_used = moved_r_now / payload_eff
                    cost_r_fixed += launches_used * cfg.ROCKET_FIXED_COST_PER_LAUNCH
                    cost_r_var += moved_r_now * cfg.ROCKET_UNIT_COST
                    
                if se_moved >= M_SE - 1.0 and r_moved >= M_R - 1.0:
                    break 
            
            c_tot += cfg.SE_FIXED_COST_YEAR
            
            if se_moved >= M_SE - 1.0 and r_moved >= M_R - 1.0:
                 t_years = year
                 finished_year = True
                 break
        
        if not finished_year:
            t_years = cfg.T_MAX_YEARS
            
        c_tot += (cost_se_var + cost_r_var + cost_r_fixed)
        
        sim_results['Time'].append(t_years)
        sim_results['Cost'].append(c_tot)
        
    return sim_results

def run_risk_breakdown():
    print("Loading Strategies...")
    strats = load_q1_strategies()
    cfg = Config()
    
    # Scenarios to test
    # Baseline: No risk
    # Individual: Each risk alone
    # Full: All risks
    scenarios = {
        'Baseline': [],
        'R1_Elevator': ['R1'],
        'R2_Maint': ['R2'],
        'R3_Rocket': ['R3'],
        'R4_Fuel': ['R4'],
        'All_Risks': ['R1', 'R2', 'R3', 'R4']
    }
    
    all_results = []
    
    for stage_id, df_strat in strats.items():
        print(f"\n--- Processing Stage {stage_id} Breakdowns ---")
        demand = Config.STAGES[stage_id]
        
        # Only process a middle strategy (Balanced) to simplify the "Breakdown" view?
        # Or average across the sampled strategies?
        # Let's take the "Median Alpha" strategy as representative for the breakdown chart
        # Middle row of the sampled 5
        mid_idx = len(df_strat) // 2
        # Actually, let's take the one closest to Alpha=0.5 if it exists, or just the middle
        # But wait, df_strat is already sampled to 5 points.
        # Let's do ALL 5 points, then we can aggregate or pick one for plotting.
        
        for idx, row in df_strat.iterrows():
            alpha = row['Alpha']
            # print(f"  > Strategy Alpha: {alpha:.2f}")
            
            for scen_name, risks in scenarios.items():
                res = simulate_point_scenario(alpha, demand, cfg, risks)
                
                t_mean = np.mean(res['Time'])
                c_mean = np.mean(res['Cost'])
                
                all_results.append({
                    'Stage': stage_id,
                    'Alpha': alpha,
                    'Scenario': scen_name,
                    'Time_Mean': t_mean,
                    'Cost_Mean': c_mean
                })
    
    df_res = pd.DataFrame(all_results)
    df_res.to_csv('MCM_Models/Q1_New_DP/Risk_Breakdown_Detailed.csv', index=False)
    print("Detailed breakdown saved.")
    
    # --- Visualization ---
    # We want to show the "Added Impact" of each risk
    # 1. Select one representative Alpha per stage (e.g. nearest to 0.5 or 0.6)
    #    OR Average the impact across strategies? (Risk impact depends heavily on Alpha though)
    #    Let's pick the strategy with Alpha closest to 0.6 (Balanced-ish)
    
    plot_risk_impact_bar(df_res)

def plot_risk_impact_bar(df):
    # Filter for a representative strategy per stage
    # Let's pick the Alpha closest to 0.5 for each stage
    
    target_alpha = 0.5
    filtered_rows = []
    
    for stage in df['Stage'].unique():
        stage_df = df[df['Stage'] == stage]
        unique_alphas = stage_df['Alpha'].unique()
        # Find closest
        best_alpha = unique_alphas[np.argmin(np.abs(unique_alphas - target_alpha))]
        
        # Get rows for this alpha
        subset = stage_df[stage_df['Alpha'] == best_alpha].copy()
        filtered_rows.append(subset)
        
    plot_df = pd.concat(filtered_rows)
    
    # Calculate Deltas relative to Baseline
    # Pivot to get Baseline values accessible
    pivoted = plot_df.pivot(index=['Stage', 'Alpha'], columns='Scenario', values=['Time_Mean', 'Cost_Mean'])
    
    # Prepare data for plotting
    # We want bars for: R1, R2, R3, R4, All
    # y-axis: % Increase or Absolute Increase
    
    # Let's do Absolute Increase for robustness
    
    stages = plot_df['Stage'].unique()
    scenarios_to_plot = ['R1_Elevator', 'R2_Maint', 'R3_Rocket', 'R4_Fuel', 'All_Risks']
    
    fig, axes = plt.subplots(2, 1, figsize=(10, 12))
    
    # Plot Time Impact
    ax1 = axes[0]
    bar_width = 0.15
    x = np.arange(len(stages))
    
    for i, scen in enumerate(scenarios_to_plot):
        deltas = []
        for stage in stages:
            # Extract baseline and scen value
            # access pivot structure: pivoted.loc[(stage, alpha), ('Time_Mean', scen)]
            # Find the alpha used for this stage
            alpha = plot_df[plot_df['Stage']==stage]['Alpha'].iloc[0]
            base = pivoted.loc[(stage, alpha), ('Time_Mean', 'Baseline')]
            val = pivoted.loc[(stage, alpha), ('Time_Mean', scen)]
            deltas.append(val - base)
        
        ax1.bar(x + i*bar_width, deltas, width=bar_width, label=scen)
        
    ax1.set_xticks(x + bar_width * 2)
    ax1.set_xticklabels([f'Stage {s}' for s in stages])
    ax1.set_ylabel('Additional Time (Years)')
    ax1.set_title('Risk Impact on Time (vs Baseline)')
    ax1.legend()
    
    # Plot Cost Impact
    ax2 = axes[1]
    
    for i, scen in enumerate(scenarios_to_plot):
        deltas = []
        for stage in stages:
            alpha = plot_df[plot_df['Stage']==stage]['Alpha'].iloc[0]
            base = pivoted.loc[(stage, alpha), ('Cost_Mean', 'Baseline')]
            val = pivoted.loc[(stage, alpha), ('Cost_Mean', scen)]
            deltas.append(val - base)
        
        ax2.bar(x + i*bar_width, [d/1e9 for d in deltas], width=bar_width, label=scen) # Billions
        
    ax2.set_xticks(x + bar_width * 2)
    ax2.set_xticklabels([f'Stage {s}' for s in stages])
    ax2.set_ylabel('Additional Cost (Billion USD)')
    ax2.set_title('Risk Impact on Cost (vs Baseline)')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('MCM_Models/Q1_New_DP/Risk_Breakdown_Chart.png', dpi=300)
    print("Breakdown chart saved.")

if __name__ == "__main__":
    run_risk_breakdown()
