
import numpy as np
import pandas as pd

class Config:
    # Mass Definition (kg)
    M_total = 1.0e11
    
    # Phase Split
    Phases = [
        {'name': 'Camp Phase', 'mass': 0.10 * 1.0e11, 'weights': {'time': 0.7, 'cost': 0.3}},
        {'name': 'Base Phase', 'mass': 0.40 * 1.0e11, 'weights': {'time': 0.5, 'cost': 0.5}},
        {'name': 'City Phase', 'mass': 0.50 * 1.0e11, 'weights': {'time': 0.2, 'cost': 0.8}}
    ]
    
    # Infrastructure Params
    # SE
    Cable_Cap = 1.79e8  # kg/yr per cable
    Cable_Cost_Fixed = 10.0e12 # $10T per cable
    SE_Var_Cost = 525.0 # $/kg
    
    # Rocket
    Site_Cap = 1.095e8 # kg/yr per site (100% utilization)
    Site_Cost_Fixed = 0.01e12 # $10B per site
    Rocket_Var_Cost = 1000.0 # $/kg
    
    # Discrete Options
    Cable_Options = [0, 1, 2, 3] 
    Site_Options = [0, 1, 5, 10]

def calculate_weighted_strategy():
    print("Calculating Optimal Strategy based on User Weights...")
    print("Weights: Camp(T:0.9, C:0.1) -> Base(T:0.2, C:0.8) -> City(T:0.5, C:0.5)")
    
    # Initial State
    current_max_c = 0
    current_max_s = 0
    
    total_time = 0
    total_cost = 0
    path_history = []
    
    # Metrics to track
    phase_details = []

    for phase in Config.Phases:
        print(f"\nProcessing {phase['name']}...")
        candidates = []
        
        # 1. Generate all feasible options for this phase
        for active_c in Config.Cable_Options:
            if active_c > 3: continue
            
            for active_s in Config.Site_Options:
                if active_c == 0 and active_s == 0: continue # Invalid
                
                # Check feasibility (Can't use more cables than 3, logical bound is Config)
                # But we can use FEWER active cables than built (though inefficient often).
                # However, for Infra Cost, we must pay if we build NEW ones.
                
                # Infra Cost
                # We need to build up to max(current_max, active)
                needed_c = max(current_max_c, active_c)
                needed_s = max(current_max_s, active_s)
                
                cost_infra = 0
                if needed_c > current_max_c:
                    cost_infra += (needed_c - current_max_c) * Config.Cable_Cost_Fixed
                if needed_s > current_max_s:
                    cost_infra += (needed_s - current_max_s) * Config.Site_Cost_Fixed
                
                # Operational Metrics
                capacity_se = active_c * Config.Cable_Cap
                capacity_rocket = active_s * Config.Site_Cap
                total_capacity = capacity_se + capacity_rocket
                
                time_phase = phase['mass'] / total_capacity
                
                # Variable Cost
                ratio_se = capacity_se / total_capacity
                mass_se = phase['mass'] * ratio_se
                mass_rocket = phase['mass'] * (1 - ratio_se)
                
                cost_ops = (mass_se * Config.SE_Var_Cost) + (mass_rocket * Config.Rocket_Var_Cost)
                
                total_phase_cost = cost_infra + cost_ops
                
                candidates.append({
                    'active_c': active_c,
                    'active_s': active_s,
                    'new_max_c': needed_c,
                    'new_max_s': needed_s,
                    'time': time_phase,
                    'cost': total_phase_cost,
                    'cost_infra': cost_infra,
                    'cost_ops': cost_ops,
                    'mass_se': mass_se, 
                    'mass_rocket': mass_rocket
                })
        
        # 2. Normalize and Score
        # Extract lists for vector calc
        times = np.array([c['time'] for c in candidates])
        costs = np.array([c['cost'] for c in candidates])
        
        # Avoid div by zero if all same (unlikely)
        t_range = times.max() - times.min()
        c_range = costs.max() - costs.min()
        
        if t_range == 0: t_range = 1e-9
        if c_range == 0: c_range = 1e-9
        
        print(f"  Range: Time [{times.min():.2f}, {times.max():.2f}], Cost [${costs.min()/1e12:.2f}T, ${costs.max()/1e12:.2f}T]")
        
        best_score = float('inf')
        best_candidate = None
        
        w_t = phase['weights']['time']
        w_c = phase['weights']['cost']
        
        for i, cand in enumerate(candidates):
            # Normalize [0, 1]
            t_norm = (cand['time'] - times.min()) / t_range
            c_norm = (cand['cost'] - costs.min()) / c_range
            
            score = (w_t * t_norm) + (w_c * c_norm)
            
            cand['score'] = score
            cand['t_norm'] = t_norm
            cand['c_norm'] = c_norm
            
            if score < best_score:
                best_score = score
                best_candidate = cand
        
        # 3. Select Best
        sel = best_candidate
        print(f"  Selected: SE:{sel['active_c']} + Rocket:{sel['active_s']}")
        print(f"  Metrics: Time={sel['time']:.2f} yr, Cost=${sel['cost']/1e12:.2f}T (Score: {best_score:.4f})")
        
        # Update System State
        current_max_c = sel['new_max_c']
        current_max_s = sel['new_max_s']
        
        total_time += sel['time']
        total_cost += sel['cost']
        
        phase_details.append({
            'Stage': phase['name'],
            'Strategy': f"SE:{sel['active_c']} / R:{sel['active_s']}",
            'Time_Yr': sel['time'],
            'Cost_Trillion': sel['cost'] / 1e12,
            'SE_Share_%': (sel['mass_se'] / phase['mass']) * 100,
            'Rocket_Share_%': (sel['mass_rocket'] / phase['mass']) * 100,
            'Rocket_Launches': sel['mass_rocket'] / 150000 
        })
        
    # Final Output
    print("\n" + "="*80)
    print("FINAL WEIGHTED OPTIMIZATION RESULTS")
    print("="*80)
    
    df_res = pd.DataFrame(phase_details)
    print(df_res.to_string(index=False, formatters={
        'Time_Yr': '{:.2f}'.format,
        'Cost_Trillion': '{:.2f}'.format,
        'SE_Share_%': '{:.1f}%'.format,
        'Rocket_Share_%': '{:.1f}%'.format,
        'Rocket_Launches': '{:.0f}'.format
    }))
    
    print("-" * 80)
    print(f"Total Duration: {total_time:.2f} Years")
    print(f"Total Cost:     ${total_cost/1e12:.2f} Trillion")
    print("-" * 80)
    
    # Save
    df_res.to_csv('MCM_Models/Q1_New_DP/Weighted_Strategy_Result.csv', index=False)
    print("Saved to MCM_Models/Q1_New_DP/Weighted_Strategy_Result.csv")

if __name__ == "__main__":
    calculate_weighted_strategy()
