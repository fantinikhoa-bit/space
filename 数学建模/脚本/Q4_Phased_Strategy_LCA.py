
import numpy as np
import pandas as pd
import sys
import os

# Define Config relative to the user's "Camp, Base, City" structure
class Config:
    M_total = 1.0e11
    STAGES = {
        'Camp': 0.10 * M_total, # 1e10 kg
        'Base': 0.40 * M_total, # 4e10 kg
        'City': 0.50 * M_total  # 5e10 kg
    }
    
    Q_se = 5.37e8 
    C_se_unit = 525.0
    C_r_unit = 1012.5
    C_r_site = 1.0e10
    
    Q_r_launch = 1.5e5
    T_r_cycle = 0.5
    Num_Launch_Sites = 10
    
    # Environment Params
    # Construction Emissions
    E_site_const = 5.0e8 # 500,000 tons? No, 500,000 kg CO2 from older script? 
    # Let's say 500 tons CO2 per site construction. (Low estimate)
    # Actually concrete is heavy. Let's use 50,000 tons = 5e7 kg.
    E_site_const = 5.0e7
    
    # Operation Emissions (kg CO2 / kg Payload)
    E_trans_se_CO2 = 0.1 # Very low
    E_trans_r_CO2 = 3.62 # Kerosene/Methane burning
    
    # Stratospheric Impact Factor (Multiplier)
    # Rockets release soot in stratosphere, multiplier effect
    E_strat_factor = 2.0 

def calculate_stage_metrics(stage_name, mass_demand, alpha):
    """
    alpha: Fraction of mass via Space Elevator (0.0 to 1.0)
    """
    # 1. Mass Split
    m_se = mass_demand * alpha
    m_rocket = mass_demand * (1 - alpha)
    
    # 2. Time Calculation
    # SE Time
    t_se = m_se / Config.Q_se if m_se > 0 else 0
    
    # Rocket Time
    # Throughput
    launches_yr = Config.Num_Launch_Sites * (365.0 / Config.T_r_cycle)
    q_rocket_annual = launches_yr * Config.Q_r_launch
    t_rocket = m_rocket / q_rocket_annual if m_rocket > 0 else 0
    
    # Stage Time (Parallel)
    t_stage = max(t_se, t_rocket)
    
    # 3. Cost Calculation
    c_se = m_se * Config.C_se_unit
    c_rocket = m_rocket * Config.C_r_unit
    # Fixed costs? Sites built in Stage 1, SE built in Stage 1?
    # Let's assume Fixed Costs distributed or One-off.
    # We'll add discrete Fixed costs in main loop.
    c_var = c_se + c_rocket
    
    # 4. Environment Calculation
    # SE Emissions
    e_se = m_se * Config.E_trans_se_CO2
    
    # Rocket Emissions (with stratospheric factor)
    e_rocket = m_rocket * Config.E_trans_r_CO2 * Config.E_strat_factor
    
    return {
        'Stage': stage_name,
        'Mass': mass_demand,
        'Alpha': alpha,
        'Time': t_stage,
        'Cost_Var': c_var,
        'Emissions': e_se + e_rocket
    }

def run_phased_lca():
    print("--- Problem 4: Three-Stage Environmental Impact Assessment ---")
    
    # Define Our Recommended Strategies for each Stage
    # Based on Q1/Q2 Optimization:
    # 1. Camp: Speed prioritized -> Use Hybrid/Rocket (Alpha low) -> e.g., 0.3
    # 2. Base: Balanced -> Hybrid (Alpha med) -> e.g., 0.6
    # 3. City: Cost/Env prioritized -> SE (Alpha high) -> e.g., 1.0
    
    strategies = [
        {'name': 'Camp', 'mass': Config.STAGES['Camp'], 'alpha': 0.30},
        {'name': 'Base', 'mass': Config.STAGES['Base'], 'alpha': 0.60},
        {'name': 'City', 'mass': Config.STAGES['City'], 'alpha': 1.00}
    ]
    
    total_time = 0
    total_cost = 0
    total_emissions = 0
    
    stage_results = []
    
    # Fixed Costs (One time)
    # 10 Sites built at start
    cost_sites = Config.Num_Launch_Sites * Config.C_r_site
    # SE built at start
    cost_se_fixed = 4.5e10 * 3 # 3 Cables? Or just project cost. Using Q1 4.5e10 number.
    
    # Construction Emissions
    emit_const = Config.Num_Launch_Sites * Config.E_site_const
    
    total_cost += (cost_sites + cost_se_fixed)
    total_emissions += emit_const
    
    print(f"\n{'Stage':<10} | {'Alpha (SE%)':<12} | {'Time (Yr)':<10} | {'Cost ($T)':<10} | {'Emissions (MT)':<15}")
    print("-" * 70)
    
    for s in strategies:
        res = calculate_stage_metrics(s['name'], s['mass'], s['alpha'])
        
        # Add Fixed cost per year for SE maintenance?
        # Let's keep it simple: Variable + Deployment Fixed.
        
        total_time += res['Time']
        total_cost += res['Cost_Var']
        total_emissions += res['Emissions']
        
        # Print Row
        # Emissions in Million Tons (CO2) -> kg / 1e9
        e_mt = res['Emissions'] / 1e9
        c_t = res['Cost_Var'] / 1e12
        print(f"{s['name']:<10} | {s['alpha']:<12.2f} | {res['Time']:<10.2f} | {c_t:<10.2f} | {e_mt:<15.2f}")
        
        stage_results.append(res)
        
    print("-" * 70)
    print(f"{'TOTAL':<10} | {'-':<12} | {total_time:<10.2f} | {total_cost/1e12:<10.2f} | {total_emissions/1e9:<15.2f}")
    
    # --- Comparison with Non-Phased Scenarios ---
    # Pure Rocket (Alpha=0 all stages)
    # Pure SE (Alpha=1 all stages)
    
    print("\n--- Strategy Comparison ---")
    
    # Calc Pure Rocket
    e_rocket = Config.M_total * Config.E_trans_r_CO2 * Config.E_strat_factor
    # Calc Pure SE
    e_se = Config.M_total * Config.E_trans_se_CO2
    
    print(f"Pure Rocket Impact: {e_rocket/1e9:.2f} Million Tons CO2")
    print(f"Pure SE Impact:     {e_se/1e9:.2f} Million Tons CO2")
    print(f"Phased Strategy:    {total_emissions/1e9:.2f} Million Tons CO2")
    
    reduction = (e_rocket - total_emissions) / e_rocket
    print(f"\n>> Environmental Optimization: Reduced emissions by {reduction:.1%} compared to Pure Rocket.")
    
    # Save Results
    df_res = pd.DataFrame(stage_results)
    df_res.to_csv('MCM_Models/Q4_Phased_Detailed_LCA.csv', index=False)
    print("\nDetailed Stage Analysis saved to MCM_Models/Q4_Phased_Detailed_LCA.csv")

if __name__ == "__main__":
    run_phased_lca()
