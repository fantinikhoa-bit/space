
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import copy

# --- Configuration ---
class Config:
    M_total = 1.0e11
    STAGES = {
        'Camp': 0.10 * M_total,
        'Base': 0.40 * M_total,
        'City': 0.50 * M_total
    }
    
    Q_se = 5.37e8 
    C_se_unit = 525.0
    C_r_unit = 1012.5
    C_r_site = 1.0e10
    
    Q_r_launch = 1.5e5
    T_r_cycle = 0.5
    Num_Launch_Sites = 10
    
    # Emissions (kg CO2)
    E_site_const = 5.0e7
    E_trans_se_CO2 = 0.1 
    E_trans_r_CO2 = 3.62 
    E_strat_factor = 2.0 

# --- Evaluation Function ---
def evaluate_individual(alphas):
    """
    alphas: list of [alpha_camp, alpha_base, alpha_city]
    Returns: (Time, Cost, Emissions)
    """
    total_time = 0
    total_cost = 0
    total_env = 0
    
    # Fixed Costs (One-time)
    total_cost += 10 * Config.C_r_site # Sites
    total_cost += 4.5e10 # SE Project Fixed
    total_env += 10 * Config.E_site_const
    
    stage_names = ['Camp', 'Base', 'City']
    
    for i, stage in enumerate(stage_names):
        mass = Config.STAGES[stage]
        alpha = alphas[i]
        
        # 1. Mass Split
        m_se = mass * alpha
        m_rocket = mass * (1 - alpha)
        
        # 2. Time
        t_se = m_se / Config.Q_se if m_se > 0 else 0
        
        launches_yr = Config.Num_Launch_Sites * (365.0 / Config.T_r_cycle)
        q_rocket_annual = launches_yr * Config.Q_r_launch
        t_rocket = m_rocket / q_rocket_annual if m_rocket > 0 else 0
        
        t_stage = max(t_se, t_rocket)
        total_time += t_stage
        
        # 3. Cost
        c_var = (m_se * Config.C_se_unit) + (m_rocket * Config.C_r_unit)
        total_cost += c_var
        
        # 4. Env
        e_se = m_se * Config.E_trans_se_CO2
        e_rocket = m_rocket * Config.E_trans_r_CO2 * Config.E_strat_factor
        total_env += (e_se + e_rocket)
        
    return [total_time, total_cost, total_env]

# --- NSGA-II Implementation (Custom for reliability) ---
class NSGA2_Solver:
    def __init__(self, pop_size=100, generations=50):
        self.pop_size = pop_size
        self.generations = generations
        self.population = [] # List of {'genes': [a1, a2, a3], 'objs': [t, c, e], 'rank': 0, 'dist': 0}
        
    def initialize(self):
        for _ in range(self.pop_size):
            # Random alphas
            genes = [random.random() for _ in range(3)]
            objs = evaluate_individual(genes)
            self.population.append({'genes': genes, 'objs': objs})
        self.non_dominated_sort(self.population)

    def dominates(self, p1, p2):
        # Min Time, Min Cost, Min Env
        # True if p1 dominates p2
        o1 = p1['objs']
        o2 = p2['objs']
        and_condition = True
        or_condition = False
        for i in range(3):
            if o1[i] > o2[i]:
                and_condition = False
            if o1[i] < o2[i]:
                or_condition = True
        return and_condition and or_condition
        
    def non_dominated_sort(self, pop):
        fronts = [[]]
        for p in pop:
            p['domination_count'] = 0
            p['dominated_set'] = []
            for q in pop:
                if self.dominates(p, q):
                    p['dominated_set'].append(q)
                elif self.dominates(q, p):
                    p['domination_count'] += 1
            if p['domination_count'] == 0:
                p['rank'] = 0
                fronts[0].append(p)
        
        i = 0
        while len(fronts[i]) > 0:
            next_front = []
            for p in fronts[i]:
                for q in p['dominated_set']:
                    q['domination_count'] -= 1
                    if q['domination_count'] == 0:
                        q['rank'] = i + 1
                        next_front.append(q)
            i += 1
            fronts.append(next_front)
            
        return fronts[:-1] # Last one is empty
        
    def crowding_distance(self, front):
        l = len(front)
        if l == 0: return
        
        for p in front:
            p['dist'] = 0
        
        for m in range(3): # 3 Objectives
            front.sort(key=lambda x: x['objs'][m])
            front[0]['dist'] = float('inf')
            front[-1]['dist'] = float('inf')
            
            r_range = front[-1]['objs'][m] - front[0]['objs'][m]
            if r_range == 0: continue
            
            for i in range(1, l-1):
                front[i]['dist'] += (front[i+1]['objs'][m] - front[i-1]['objs'][m]) / r_range

    def run(self):
        self.initialize()
        
        for g in range(self.generations):
            # 1. Check Ranks (Safety)
            if 'rank' not in self.population[0]:
                 self.non_dominated_sort(self.population)

            # 1. Offspring
            offspring = []
            while len(offspring) < self.pop_size:
                # Tournament
                p1 = random.choice(self.population)
                p2 = random.choice(self.population)
                # Ensure rank exists
                r1 = p1.get('rank', 999)
                r2 = p2.get('rank', 999)
                parent1 = p1 if r1 < r2 else p2
                
                p3 = random.choice(self.population)
                p4 = random.choice(self.population)
                r3 = p3.get('rank', 999)
                r4 = p4.get('rank', 999)
                parent2 = p3 if r3 < r4 else p4
                
                # Crossover
                child_genes = []
                for i in range(3):
                    beta = random.random()
                    c_gene = beta * parent1['genes'][i] + (1-beta) * parent2['genes'][i]
                    # Mutation
                    if random.random() < 0.1:
                        c_gene += np.random.normal(0, 0.1)
                        c_gene = np.clip(c_gene, 0, 1)
                    child_genes.append(c_gene)
                
                offspring.append({'genes': child_genes, 'objs': evaluate_individual(child_genes)})
            
            # 2. Merge
            combined = self.population + offspring
            
            # 3. Sort
            fronts = self.non_dominated_sort(combined)
            
            # 4. Select next gen
            new_pop = []
            for front in fronts:
                self.crowding_distance(front)
                # Sort by Rank (implicit) then Distance (desc)
                front.sort(key=lambda x: x['dist'], reverse=True)
                
                if len(new_pop) + len(front) <= self.pop_size:
                    new_pop.extend(front)
                else:
                    remain = self.pop_size - len(new_pop)
                    new_pop.extend(front[:remain])
                    break
            
            self.population = new_pop
            if g % 10 == 0:
                print(f"Generation {g}: Best Front Size {len(fronts[0])}")
        
        return self.non_dominated_sort(self.population)[0]

def main():
    print("Running NSGA-II for (Time, Cost, Environment) Optimization...")
    print("Variables: [Alpha_Camp, Alpha_Base, Alpha_City]")
    
    solver = NSGA2_Solver(pop_size=200, generations=50)
    pareto_front = solver.run()
    
    # Extract Results
    data = []
    for p in pareto_front:
        data.append({
            'Alpha_Camp': p['genes'][0],
            'Alpha_Base': p['genes'][1],
            'Alpha_City': p['genes'][2],
            'Time': p['objs'][0],
            'Cost': p['objs'][1],
            'Emissions': p['objs'][2]
        })
        
    df = pd.DataFrame(data)
    
    # Save
    df.to_csv('MCM_Models/Q4_NSGA2_Pareto.csv', index=False)
    print(f"\nPareto Front (size {len(df)}) saved.")
    
    # Find Interesting Solutions
    # 1. Min Env
    min_env = df.loc[df['Emissions'].idxmin()]
    # 2. Min Cost
    min_cost = df.loc[df['Cost'].idxmin()]
    # 3. Min Time
    min_time = df.loc[df['Time'].idxmin()]
    # 4. Balanced (Knee) - Simple Normalize distance
    norm_df = (df[['Time','Cost','Emissions']] - df[['Time','Cost','Emissions']].min()) / (df[['Time','Cost','Emissions']].max() - df[['Time','Cost','Emissions']].min())
    norm_df['dist'] = norm_df['Time']**2 + norm_df['Cost']**2 + norm_df['Emissions']**2
    knee = df.loc[norm_df['dist'].idxmin()]
    
    print("\n--- Key Solutions on Pareto Front ---")
    
    def print_sol(name, row):
        print(f"\n[{name}]")
        print(f"  Strategy: Camp={row['Alpha_Camp']:.2f}, Base={row['Alpha_Base']:.2f}, City={row['Alpha_City']:.2f}")
        print(f"  Result:   Time={row['Time']:.1f}y, Cost=${row['Cost']/1e12:.1f}T, Env={row['Emissions']/1e9:.2f}MT")
        
    print_sol("Minimum Emissions (Greenest)", min_env)
    print_sol("Minimum Cost (Cheapest)", min_cost)
    print_sol("Minimum Time (Fastest)", min_time)
    print_sol("Balanced Compromise (Recommended)", knee)
    
    # Plotting
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    xs = df['Time']
    ys = df['Cost'] / 1e12
    zs = df['Emissions'] / 1e9 # Million Tons
    
    img = ax.scatter(xs, ys, zs, c=zs, cmap='viridis', s=50, alpha=0.8)
    
    ax.set_xlabel('Time (Years)')
    ax.set_ylabel('Cost (Trillion $)')
    ax.set_zlabel('Emissions (Million Tons CO2)')
    ax.set_title('NSGA-II Pareto Front: Time-Cost-Environment')
    
    cbar = fig.colorbar(img, ax=ax, shrink=0.5, aspect=10)
    cbar.set_label('Emissions')
    
    # Highlight points
    ax.scatter([knee['Time']], [knee['Cost']/1e12], [knee['Emissions']/1e9], color='red', s=100, label='Balanced')
    
    plt.savefig('MCM_Models/Q4_NSGA2_3D_Plot.png', dpi=300)
    print("3D Plot saved.")

if __name__ == "__main__":
    main()
