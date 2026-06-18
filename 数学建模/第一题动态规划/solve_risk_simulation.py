
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# --- Configuration & Constants ---
class Config:
    # Demand Stages (kg)
    Q_total = 1.0e11
    STAGES = {
        1: 0.10 * Q_total,
        2: 0.40 * Q_total,
        3: 0.50 * Q_total
    }
    
    # Space Elevator (SE) Basic Params
    SE_CAPACITY_PER_YEAR = 5.37e8  # kg/yr (Base Capacity)
    SE_FIXED_COST_YEAR = 4.5e10    # USD/yr
    SE_UNIT_COST = 525.0           # USD/kg
    
    # Rocket Basic Params
    ROCKET_CAPACITY_PER_LAUNCH = 1.5e5  # kg
    ROCKET_LAUNCHES_PER_YEAR_MAX = 7300 # Total global max
    ROCKET_FIXED_COST_PER_LAUNCH = 3.25e6 # USD/launch
    ROCKET_UNIT_COST = 1012.5       # USD/kg (Maybe fuel/ops)
    
    # Simulation Params
    T_SIM = 1000        # Number of Monte Carlo runs
    T_MAX_YEARS = 200    # Max allowed years to simulate (Stage 3 needs ~93 years for all-SE)
    ALPHA_STEPS = 51    # Resolution for alpha [0...1]

    # --- Risk Parameters (Calibrated from User Data) ---
    # R1: Elevator Failure (Annual)
    P1_ELEVATOR_FAIL_YEAR = 0.02  # Probability/year (Table: 0.02)
    D1_ELEVATOR_FAIL_IMPACT = 0.5 # Capacity loss ratio if fail (Table: 0.5)
    
    # R2: Capacity Decay (Maintenance Delay - Monthly)
    P2_DECAY_MONTH = 0.03         # Probability/month (Table: 0.03)
    D2_DECAY_IMPACT = 0.10        # Monthly capacity reduction (Table: 10%)
    
    # R3: Rocket Explosion (Per Launch)
    P3_EXPLOSION = 0.05           # Probability per launch (Table: 0.05)
    
    # R4: Fuel Chain Interruption (Monthly)
    P4_FUEL_MONTH = 0.05          # Probability/month (Table: 0.05)
    D4_FUEL_IMPACT = 0.4          # Launch count reduction ratio (Table: 40%)

def simulate_risk_scenario(alpha, stage_demand, cfg):
    """
    Simulates the transport process for a given allocation alpha.
    Returns (Expected_Time, Expected_Cost, STD_Time, STD_Cost).
    """
    
    # Required Transport Amounts
    M_SE = alpha * stage_demand
    M_R = (1 - alpha) * stage_demand
    
    sim_times = []
    sim_costs = []
    
    # Constants
    months_per_year = 12
    
    for _ in range(cfg.T_SIM):
        
        # --- Random Process Generation per Month/Year ---
        # We assume we simulate year by year until done
        
        # State trackers
        se_moved = 0.0
        r_moved = 0.0
        
        current_time_years = 0.0
        
        # Cost Accumulators
        cost_se = 0.0
        cost_r = 0.0
        
        # SE Specific State
        current_decay_factor = 1.0 # Starts at 100% efficiency
        
        # Simulation Loop (Time Steps: Monthly probably better for granularity, but model defines Annual & Monthly)
        for year in range(1, cfg.T_MAX_YEARS + 1):
            
            # 1. R1: Elevator Annual Failure
            # X1 ~ Bernoulli(P1)
            is_elevator_fail = np.random.rand() < cfg.P1_ELEVATOR_FAIL_YEAR
            delta_1_factor = (1.0 - cfg.D1_ELEVATOR_FAIL_IMPACT) if is_elevator_fail else 1.0
            
            # Base Annual Capacity considering R1
            Q_SE_base_year = cfg.SE_CAPACITY_PER_YEAR * delta_1_factor
            
            # Distribute into months for R2 calculation
            Q_SE_base_month = Q_SE_base_year / 12.0
            
            year_se_capacity = 0.0
            year_r_capacity = 0.0
            
            # Rockets per month base
            K_R_month_base = cfg.ROCKET_LAUNCHES_PER_YEAR_MAX / 12.0
            
            for month in range(1, 13):
                # --- Space Elevator R2: Decay ---
                # X2 ~ Bernoulli(P2)
                if np.random.rand() < cfg.P2_DECAY_MONTH:
                    # Decay accumulates! "Product of (1 - delta2)"
                    current_decay_factor *= (1.0 - cfg.D2_DECAY_IMPACT)
                
                # Effective SE Monthly Capacity
                q_se_mo = Q_SE_base_month * current_decay_factor
                year_se_capacity += q_se_mo
                
                # --- Rocket R4: Fuel Chain ---
                # X4 ~ Bernoulli(P4)
                is_fuel_fail = np.random.rand() < cfg.P4_FUEL_MONTH
                fuel_factor = (1.0 - cfg.D4_FUEL_IMPACT) if is_fuel_fail else 1.0
                
                K_R_mo_eff = K_R_month_base * fuel_factor
                
                # --- Rocket R3: Explosion (Expected Value Approach vs Simulation) ---
                # Text says: "Q_R_eff = Q_unit * K_eff * (1 - p3)" in formula 3.3.2.
                # Since we are doing Monte Carlo for the *macro* variables, we can arguably 
                # use expected loss for the micro (launch) variables if N is large. 
                # But let's stick to the spirit. 
                # If N ~ 600/month, variance is low. Using expectation (1-P3) is fine and faster.
                # However, for Cost, explosions matter (replacement cost).
                
                # Capacity Contribution
                q_r_mo = cfg.ROCKET_CAPACITY_PER_LAUNCH * K_R_mo_eff * (1.0 - cfg.P3_EXPLOSION)
                year_r_capacity += q_r_mo
                
                # Increment Costs
                # SE Cost: Fixed based on TIME (handled at end) + Unit Cost (handled by mass)
                # But wait, SE Fixed cost is Annual.
                
                # Rocket Cost:
                # We pay for ALL launches, even failed ones?
                # Text 3.3.3: C_R = (1-alpha)M * UnitCost * 1/(1-p3)
                # This implies we launch enough to get the job done.
                # Here we are simulation "Capacity per year".
                # Let's count launches.
                
                num_launches_attempted = K_R_mo_eff # This is "Effective Planned"? 
                # Actually R4 reduces "Planning". So we don't pay for cancelled launches due to fuel?
                # Usually interruption means "cannot launch", so no cost. Use K_R_mo_eff.
                
                # Cost for these launches
                # Each launch costs: Fixed + (Mass * Unit)?
                # Config has F_launch and p_R (unit).
                # Cost_Mo = Launches * F_launch + ValidMass * p_R?
                # Or is p_R per kg of payload attempted?
                
                # Let's use the user's simplified Cost Function in 3.3.3 as a guide for structure,
                # but applied to the realized timeline.
                # Actually, 3.3.3 Formula is for the *Objectives*, derived analytically.
                # Here we want to measure them from simulation.
                
                # Let's track Mass Moved.
                if se_moved < M_SE:
                    can_move = min(q_se_mo, M_SE - se_moved)
                    se_moved += can_move
                    # SE Variable Cost
                    cost_se += can_move * cfg.SE_UNIT_COST
                
                if r_moved < M_R:
                    can_move = min(q_r_mo, M_R - r_moved)
                    r_moved += can_move
                    
                    # Estimate launches used for this 'can_move'
                    # effective_capacity_per_launch = capacity * (1-p3)
                    # launches_needed = can_move / (capacity * (1-p3))
                    # This accounts for replacement launches?
                    if q_r_mo > 0:
                        fraction_used = can_move / q_r_mo
                        launches_used = K_R_mo_eff * fraction_used
                    else:
                        launches_used = 0
                        
                    # Cost of Rockets
                    # Fixed Launch Cost per launch
                    cost_r += launches_used * cfg.ROCKET_FIXED_COST_PER_LAUNCH
                    # Variable Cost per kg
                    cost_r += can_move * cfg.ROCKET_UNIT_COST 
                    
                    # Note: We need to account for explosions in cost explicitly?
                    # The formula 3.3.3 multiplies by 1/(1-p3).
                    # My logic above: launches_used derived from 'can_move' vs 'q_r_mo' (which includes 1-p3)
                    # already scales up launches.
                    # e.g. if I need 95kg, and capacity is 100*(0.95)=95.
                    # I use 100% of available launches (1 launch).
                    # So I pay for 1 launch to move 0.95*Cap.
                    # Correct.
            
            cost_se += cfg.SE_FIXED_COST_YEAR # Annual fixed cost
            
            # Check completion
            se_done = se_moved >= M_SE - 1.0 # tolerance
            r_done = r_moved >= M_R - 1.0
            
            if se_done and r_done:
                # We finished in this year.
                # To be improved: calculate exact fractional year? 
                # For now, integer years is safe or just 'year'.
                current_time_years = year
                break
        
        else:
            # Did not finish in T_MAX
            current_time_years = cfg.T_MAX_YEARS
            
        sim_times.append(current_time_years)
        
        # Add Fixed Costs associated with SE Construction? 
        # Text 3.3.3: C_SE = C_fixed + ...
        # Assume C_SE_fixed is a one-time project cost or annual?
        # "F_SE = 4.5e10 USD/yr (Fixed Maintenance)" in config.
        # "C_SE_fixed" usually means Construction.
        # The prompt code has F_SE (Maintenance).
        # We'll stick to summing annual maintenance.
        
        sim_costs.append(cost_se + cost_r)

    return np.mean(sim_times), np.mean(sim_costs), np.std(sim_times), np.std(sim_costs)

def run_solver():
    print("Initializing Risk-Based Monte Carlo Simulation...")
    cfg = Config()
    
    results = []
    
    # Iterate Stages
    for stage_id, demand in cfg.STAGES.items():
        print(f"\nProcessing Stage {stage_id} (Demand: {demand:.2e} kg)...")
        
        alphas = np.linspace(0, 1, cfg.ALPHA_STEPS)
        
        for alpha in alphas:
            t_mean, c_mean, t_std, c_std = simulate_risk_scenario(alpha, demand, cfg)
            
            results.append({
                'Stage': stage_id,
                'Alpha': alpha,
                'Time_Mean': t_mean,
                'Cost_Mean': c_mean,
                'Time_Std': t_std,
                'Cost_Std': c_std
            })
            
    df = pd.DataFrame(results)
    
    # Save Raw Results
    df.to_csv('MCM_Models/Q1_New_DP/risk_simulation_raw.csv', index=False)
    print("Simulation Complete. Results saved.")
    
    # Identify Pareto Front per Stage
    # (Simple sort and filter)
    # ... (Visualization logic to be added later)

if __name__ == "__main__":
    run_solver()
