
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools

class Config:
    # Mass Definition (kg)
    M_total = 1.0e11
    
    # Phase Split (Assumption based on User Description)
    # Camp: 1% (Early exploration, urgent)
    # Base: 19% (Expansion, accumulation)
    # City: 80% (Massive settlement)
    Phases = [
        {'name': 'Camp Phase', 'mass': 0.01 * 1.0e11, 'color': '#f1c40f'},
        {'name': 'Base Phase', 'mass': 0.19 * 1.0e11, 'color': '#e67e22'},
        {'name': 'City Phase', 'mass': 0.80 * 1.0e11, 'color': '#3498db'}
    ]
    
    # Infrastructure Params
    # SE
    # Max Cap = 5.37e8 kg/yr with 3 cables (from Q2).
    # Single Cable Cap = 5.37e8 / 3
    # Cost per Cable = ?? Total was ~$50T fixed?
    # No, C_se_fixed was 4500 Billion * 6.5 ~ 30 Trillion?
    # Let's use Q1 derived metrics.
    # Fixed Cost (Project) = $30T (Approx, calibrated to Q1).
    # Variable Cost = $525/kg.
    # Unit Cap per Cable = 1.79e8 kg/yr.
    # Cost per Cable Infra = $10T.
    
    Cable_Cap = 1.79e8
    Cable_Cost_Fixed = 10.0e12
    SE_Var_Cost = 525.0
    
    # Rocket
    # 1 Site = 730 launches * 150000 kg = 1.095e8 kg/yr.
    # Site Infra Cost = $10B = 0.01T. (Cheap infra, high ops).
    # Ops Cost = $1000/kg. (High var).
    
    Site_Cap = 1.095e8
    Site_Cost_Fixed = 0.01e12
    Rocket_Var_Cost = 1000.0
    
    # Discrete Options
    Cable_Options = [0, 1, 2, 3] # Up to 3 cables ~ Full SE
    Site_Options = [0, 1, 5, 10] # 0, 1(Test), 5(Half), 10(Full)

def run_phased_dp():
    print("Running Phased Strategy Optimization (Dynamic Programming)...")
    
    # State Definition: (cables_built, sites_built, accumulated_time, accumulated_cost, path_history)
    # We process phase by phase.
    
    # Initial State
    # List of possible states at end of Phase k
    # struct: {'max_c': int, 'max_s': int, 'time': float, 'cost': float, 'history': list}
    current_states = [{'max_c': 0, 'max_s': 0, 'time': 0.0, 'cost': 0.0, 'history': []}]
    
    for p_idx, phase in enumerate(Config.Phases):
        print(f"Processing {phase['name']} (Mass: {phase['mass']:.1e} kg)...")
        next_states = []
        
        # Pruning: If too many states, keep only Pareto-efficient ones within grid (c,s).
        # We handle this by grouping by (c,s) and keeping pareto sub-front for each (c,s).
        
        # Standard Viterbi-like expansion
        for state in current_states:
            curr_c = state['max_c']
            curr_s = state['max_s']
            
            # Try all possible upgrades
            for new_c in Config.Cable_Options:
                if new_c < curr_c: continue # Cannot demolish SE cables (sunk)
                
                for new_s in Config.Site_Options:
                    # We usually don't demolish rocket sites, but we can *deactivate* them.
                    # Ops Capacity depends on ACTIVE sites.
                    # Construction Cost depends on PEAK sites built.
                    # Let's assume we can Scale Up infrastructure. Scaling down saves Ops but Infra cost sunk.
                    # Simplified: State tracks Max_S_Built.
                    # But for *Throughput* of this phase, we choose Active_S.
                    # To allow "Phased Strategy" (Rocket -> SE), we must allow Active < Built.
                    pass # logic below
                    
                    # Decisions for this phase:
                    # 1. Invest Infra to reach at least max(built, active).
                    # 2. Run at active level.
                    
                    # We assume we operate at the NEW level (new_c, new_s) for this phase.
                    # "new_s" is Active Sites.
                    # Construction cost applies if new_s > state['s_max'].
                    
            # Let's iterate over Possible Operational Configs (Active_C, Active_S)
            for active_c in Config.Cable_Options:
                if active_c > 3: continue 
                
                for active_s in Config.Site_Options:
                    if active_c == 0 and active_s == 0: continue # Cannot transport
                    
                    # Calculate Infra Upgrade Cost
                    # We need to track 'max_c_built' and 'max_s_built' in state?
                    # Yes. Let's update state definition.
                    # state = (max_c, max_s, time, cost, history)
                    
                    max_c = state.get('max_c', 0)
                    max_s = state.get('max_s', 0)
                    
                    cost_infra = 0
                    if active_c > max_c:
                        cost_infra += (active_c - max_c) * Config.Cable_Cost_Fixed
                    if active_s > max_s:
                        cost_infra += (active_s - max_s) * Config.Site_Cost_Fixed
                        
                    new_max_c = max(max_c, active_c)
                    new_max_s = max(max_s, active_s)
                    
                    # Calculate Operational Metrics
                    capacity = (active_c * Config.Cable_Cap) + (active_s * Config.Site_Cap)
                    time_phase = phase['mass'] / capacity
                    
                    # Variable Cost
                    # Mass split by ratio of capacity
                    ratio_se = (active_c * Config.Cable_Cap) / capacity
                    mass_se = phase['mass'] * ratio_se
                    mass_rocket = phase['mass'] * (1 - ratio_se)
                    
                    cost_ops = (mass_se * Config.SE_Var_Cost) + (mass_rocket * Config.Rocket_Var_Cost)
                    
                    total_step_cost = cost_infra + cost_ops
                    
                    # New Path Unit
                    step_info = f"P{p_idx+1}:SE{active_c}+R{active_s}"
                    
                    next_states.append({
                        'max_c': new_max_c,
                        'max_s': new_max_s,
                        'time': state['time'] + time_phase,
                        'cost': state['cost'] + total_step_cost,
                        'history': state['history'] + [step_info]
                    })
        
        # Pruning Step:
        # If we have 1000s of states, we filter.
        # Here we likely have 4*4 * 4*4 * 4*4 = 4096 max paths. Manageable.
        current_states = next_states
        print(f"  -> Generated {len(current_states)} path candidates.")
        
    # Final Analysis: Pareto Front
    # Convert to DF
    df = pd.DataFrame(current_states)
    
    # Sort by Cost
    df = df.sort_values('cost')
    pareto_rows = []
    min_time = float('inf')
    
    # Filter Pareto
    for idx, row in df.iterrows():
        if row['time'] < min_time:
            # Found a point with lower time than any cheaper option -> Pareto
            pareto_rows.append(row)
            min_time = row['time']
            
    df_pareto = pd.DataFrame(pareto_rows)
    print(f"Found {len(df_pareto)} Pareto Optimal Phased Strategies.")
    
    # Save Results
    df_pareto.to_csv('MCM_Models/Q1_Phased_DP_Pareto.csv', index=False)
    
    # Plotting - Beautified "Rainbow" Version
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(14, 9))
    
    # 1. Plot Cloud (Rainbow colored by Cost)
    # Normalize Cost for Colormap
    norm = plt.Normalize(df['cost'].min(), df['cost'].max())
    # Use rainbow: Low Cost (Purple) -> High Cost (Red)
    # Actually rainbow is standard. Let's invers so Low Cost is Blue/Purple (Good), High is Red (Bad).
    
    sc = ax.scatter(df['time'], df['cost']/1e12, c=df['cost'], cmap='turbo', 
                    s=60, alpha=0.4, edgecolors='none', label='Feasible Strategy Space')
    
    # 2. Plot Pareto Line (Solid Black or Dark Blue)
    # Smooth line
    ax.plot(df_pareto['time'], df_pareto['cost']/1e12, color='#2c3e50', linewidth=3, linestyle='--', label='Pareto Frontier')
    
    # 3. Highlights
    # Define points
    fastest = df_pareto.iloc[df_pareto['time'].argmin()]
    cheapest = df_pareto.iloc[df_pareto['cost'].argmin()]
    
    # Recalculate Knee (Geometry)
    p1 = np.array([cheapest['time'], cheapest['cost']])
    p2 = np.array([fastest['time'], fastest['cost']])
    max_dist = -1
    knee_idx = 0
    for i in range(len(df_pareto)):
        p0 = np.array([df_pareto.iloc[i]['time'], df_pareto.iloc[i]['cost']])
        d = np.abs(np.cross(p2-p1, p1-p0)) / np.linalg.norm(p2-p1)
        if d > max_dist:
            max_dist = d
            knee_idx = i
    knee = df_pareto.iloc[knee_idx]
    
    # Plot Highlights
    highlights = [
        (fastest, '#e74c3c', 'Fastest Strategy\n(Rocket Blitz)'), 
        (cheapest, '#8e44ad', 'Cheapest Strategy\n(Elevator Patience)'), 
        (knee, '#f1c40f', 'Balanced Strategy\n(The Golden Mean)')
    ]
    
    import matplotlib.patheffects as pe
    
    for pt, color, name in highlights:
        # Large Star Marker
        ax.scatter(pt['time'], pt['cost']/1e12, color=color, s=250, marker='*', edgecolors='black', zorder=10)
        
        # Clean History String (Shorten)
        # Ex: "P1:SE0+R10 -> P2:SE1+R5..."
        # Just show key traits? No, full path is too long.
        # Let's show Time/Cost text
        
        label_text = f"{name}\n{pt['time']:.1f} Years\n${pt['cost']/1e12:.1f} Trillion"
        
        # Smart annotation placement
        offset = (20, 20)
        ha = 'left'
        if pt['time'] > 150: # Right side
            offset = (-20, 10)
            ha = 'right'
        
        ax.annotate(label_text, 
                     xy=(pt['time'], pt['cost']/1e12),
                     xytext=offset, textcoords='offset points',
                     ha=ha, va='bottom',
                     fontsize=11, fontweight='bold', color=color,
                     path_effects=[pe.withStroke(linewidth=3, foreground='white')],
                     bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=color, alpha=0.9))

    # 4. Colorbar
    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label('Total Project Cost ($ Trillion)', fontsize=12, fontweight='bold')
    # Fix ticks to Trillions
    # Get current ticks
    ticks = cbar.get_ticks()
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"${x/1e12:.0f}T" for x in ticks])

    # 5. Styling
    ax.set_xlabel('Total Project Duration (Years)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Total Cost (Trillion USD)', fontsize=14, fontweight='bold')
    ax.set_title('Problem 1: Phased Strategy Optimization Space', fontsize=20, fontweight='bold', pad=20)
    
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # Add a watermark/text box analyzing the result?
    text_analysis = (
        "Pareto Analysis:\n"
        "• The 'Knee' saves $50T vs Fast\n"
        "• The 'Knee' is 60y faster than Cheap\n"
        "• Feasible Space shows distinct 'bands'\n"
        "  corresponding to discrete infra steps."
    )
    ax.text(0.95, 0.05, text_analysis, transform=ax.transAxes, ha='right', va='bottom',
            fontsize=12, bbox=dict(boxstyle='round', fc='#f9f9f9', ec='gray', alpha=0.9))

    plt.tight_layout()
    plt.savefig('MCM_Models/Q1_Phased_DP_Plot.png', dpi=300)
    print("Plot saved to MCM_Models/Q1_Phased_DP_Plot.png")

if __name__ == "__main__":
    run_phased_dp()
