
import numpy as np
import random
import matplotlib.pyplot as plt
from copy import deepcopy

# --- Configuration & Constants ---
random.seed(2025)
np.random.seed(2025)

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

# --- 1. Nepal Annapurna Scenario Definition ---

# Demographics (Trekking Season)
# Peak season is short (Oct-Nov, Mar-Apr). Let's simulate a peak month.
BASELINE_MONTHLY_TREKKERS = 15000 
LOCAL_POPULATION = 50000 # In the circuit villages

# Economic Baseline (Lower spend than developed regions)
# But Trekkers stay longer (avg 10 days)
AVG_SPEND_PER_DAY = 40.0 
AVG_STAY_DAYS = 12
TOTAL_TRIP_SPEND = AVG_SPEND_PER_DAY * AVG_STAY_DAYS # ~$480 per trip

# Base Risks (The "Pain Points")
BASE_ACCIDENT_RATE = 0.005 # 0.5% serious incident rate (High!)
BASE_WASTE_KG = 1.5 # kg waste per person per day
BASE_LOCAL_RETENTION = 0.30 # Only 30% of money stays in villages

# Decision Variables (Your 5 New Variables)
# 1. Batches_Daily: Timeslots for entry (1-10) -> spreads flow
# 2. Deposit_Fee: Trash deposit ($20 - $200)
# 3. Rescue_Density: Stations per 10km (0.1 - 2.0)
# 4. Train_Inv: % of permit fee for guide training (0.1 - 0.5)
# 5. Insure_Cover: % Mandatory Insurance Coverage (0.0 - 1.0)

RANGES = {
    'Batches_Daily': (1, 12),      # Entry Batches per day
    'Deposit_Fee': (20.0, 200.0),  # Waste Deposit ($)
    'Rescue_Density': (0.1, 2.0),  # Stations / 10km
    'Train_Inv': (0.10, 0.50),     # % Inv in Guide Training
    'Insure_Cover': (0.0, 1.0)     # Standardized Insurance Reach
}

IND_NAMES = ['Batches_Daily', 'Deposit_Fee', 'Rescue_Density', 'Train_Inv', 'Insure_Cover']
IND_TYPES = [int, float, float, float, float]

class Individual:
    def __init__(self, gene=None):
        if gene is None:
            self.gene = self._random_gene()
        else:
            self.gene = gene
        self.fitness = None
        self.objs = None 

    def _random_gene(self):
        gene = []
        for name, dtype in zip(IND_NAMES, IND_TYPES):
            low, high = RANGES[name]
            if dtype == int:
                val = random.randint(low, high)
            else:
                val = random.uniform(low, high)
            gene.append(val)
        return gene

    def clone(self):
        ind = Individual(deepcopy(self.gene))
        ind.fitness = self.fitness
        ind.objs = deepcopy(self.objs)
        return ind

def calculate_fitness(ind):
    # Unpack Gene
    Batches, Deposit, Rescue, Train, Insure = ind.gene
    
    # Static Params
    PERMIT_FEE = 50.0 # Standard ACAP permit fee
    
    # --- 1. Safety & Risk (The "Survival" Metric) ---
    # Accident rate reduces with Rescue Density and Insurance (better prep)
    # Risk Model: Base / (1 + Rescue) / (1 + Insure*0.5)
    # Rescue Density 1.0 means rate halved.
    risk_factor = BASE_ACCIDENT_RATE / (1 + Rescue * 2.0) / (1 + Insure * 0.5)
    
    # Cost of Safety: Rescue stations are expensive relative to local income
    # Cost = Rescue * $500 per trekker unit equivalent (conceptual)
    cost_safety = Rescue * 20.0 # Per trekker
    
    # --- 2. Environment (The "Trash" Metric) ---
    # Waste Recovery Rate depends on Deposit Fee
    # Logic: If deposit is $0, recover 20%. If $100, recover 95%.
    # Sigmoid-like response
    recovery_rate = 0.2 + 0.75 * (Deposit / (Deposit + 40.0))
    recovery_rate = min(0.99, recovery_rate)
    
    total_waste = BASELINE_MONTHLY_TREKKERS * AVG_STAY_DAYS * BASE_WASTE_KG
    uncollected_waste = total_waste * (1 - recovery_rate)
    
    # --- 3. Local Economy (The "Benefit" Metric) ---
    # Demand Adjustment: 
    # High safety (Insure) ATTRACTS people. High Deposit REPELS slightly.
    # Batches spreads flow but too many batches (strict timing) might annoy free trekkers.
    
    demand_mod = 1.0 
    if Deposit > 100: demand_mod -= 0.05
    if Batches > 8: demand_mod -= 0.02 # Too rigid
    if risk_factor < 0.001: demand_mod += 0.10 # "Safe destination" branding
    
    actual_trekkers = BASELINE_MONTHLY_TREKKERS * demand_mod
    
    # Total Revenue Generated
    total_spend = actual_trekkers * TOTAL_TRIP_SPEND
    total_permit = actual_trekkers * PERMIT_FEE
    
    # Local Retention Rate (The Key Goal)
    # Base 30% + Effect of Training (Local guides get hired more)
    # Training Investment directly correlates to locals running businesses
    local_retention = BASE_LOCAL_RETENTION + (Train * 0.6) # Max adds 30% -> 60% total
    
    final_local_income = total_spend * local_retention
    
    # Available Budget for Training
    budget_training = total_permit * Train
    
    # --- 4. Experience / Flow ---
    # Congestion: Total / Batches.
    # More batches = Less congestion per timeslot = Better experience
    congestion_score = (actual_trekkers / 30) / Batches # Simply inversed
    
    # --- Fitness Aggregate ---
    # Goals: Max Local Income, Min Risk, Min Waste
    # Weights: Risk is paramount (Safety First).
    
    norm_Income = final_local_income / 3e6 # ~$3M target
    norm_Risk = risk_factor / BASE_ACCIDENT_RATE # Should be < 1
    norm_Waste = uncollected_waste / 200000 # kg
    
    # Fitness Function
    # High Income, Low Risk, Low Waste
    val = (0.4 * norm_Income) - (0.4 * norm_Risk) - (0.2 * norm_Waste)
    
    # Penalties
    penalties = 0
    # Safety Floor: If risk is still above 0.3%, UNACCEPTABLE
    if risk_factor > 0.003: penalties += (risk_factor - 0.003) * 1000
    # Training Floor: Must invest at least 20% if we want retention
    if Train < 0.2: penalties += (0.2 - Train) * 2
    
    return val - penalties, (final_local_income, risk_factor, recovery_rate, local_retention)

def run_nepal_ga():
    POP_SIZE = 50
    GENS = 50
    pop = [Individual() for _ in range(POP_SIZE)]
    history = []
    
    print("Starting Nepal Annapurna Optimization...")
    print("Focus: Safety, Waste Mgmt, Local Empowerment")
    
    for gen in range(GENS):
        for ind in pop:
            ind.fitness, ind.objs = calculate_fitness(ind)
        
        pop.sort(key=lambda x: x.fitness, reverse=True)
        best = pop[0]
        history.append(best.fitness)
        
        if gen % 10 == 0:
            Inc, Risk, Recov, Retent = best.objs
            print(f"Gen {gen}: LocalInc=${Inc/1e6:.2f}M | Risk={Risk*100:.2f}% | TrashRec={Recov*100:.1f}% | LocalKeep={Retent*100:.1f}%")
            
        next_gen = pop[:4]
        while len(next_gen) < POP_SIZE:
            p1 = random.choice(pop[:15])
            p2 = random.choice(pop[:15])
            c_gene = []
            for i in range(len(p1.gene)):
                if random.random() < 0.5: c_gene.append(p1.gene[i])
                else: c_gene.append(p2.gene[i])
            child = Individual(c_gene)
            if random.random() < 0.2:
                idx = random.randint(0, 4)
                low, high = RANGES[IND_NAMES[idx]]
                if isinstance(child.gene[idx], int):
                    child.gene[idx] = random.randint(low, high)
                else:
                    child.gene[idx] = random.uniform(low, high)
            next_gen.append(child)
        pop = next_gen
        
    best = pop[0]
    Inc, Risk, Recov, Retent = best.objs
    
    print("\n=== Optimal Himalaya Strategy ===")
    print(f"Entry Batches/Day: {best.gene[0]} (Flow Control)")
    print(f"Trash Deposit: ${best.gene[1]:.2f} (Incentive)")
    print(f"Rescue Stations/10km: {best.gene[2]:.2f} (Safety Infrastr)")
    print(f"Guide Training Inv: {best.gene[3]*100:.1f}% (Local Skills)")
    print(f"Insurance Coverage: {best.gene[4]*100:.1f}% (Risk Transfer)")
    print("-" * 30)
    print("KPI Achievement:")
    print(f"  - Local Retained Income: ${Inc/1e6:.2f}M (Target: Maximize)")
    print(f"  - Accident Rate: {Risk*100:.3f}% (Baseline {BASE_ACCIDENT_RATE*100}%)")
    print(f"  - Trash Recovery: {Recov*100:.1f}%")
    print(f"  - Local Benefit Ratio: {Retent*100:.1f}% (Baseline 30%)")
    
    # Visualization: Bar Chart of Improvement
    metrics = ['Safety Level', 'Trash Recovery', 'Local Income %']
    # Safety Level = 1 / (Risk/Base) -> Higher is better
    safe_imp = (BASE_ACCIDENT_RATE / Risk) 
    waste_imp = Recov / 0.2 # Base 20%
    inc_imp = Retent / 0.3 # Base 30%
    
    vals = [safe_imp, waste_imp, inc_imp]
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(metrics, vals, color=['#d32f2f', '#4caf50', '#ff9800'])
    plt.axhline(1.0, color='gray', linestyle='--', label='Baseline')
    plt.title('Annapurna Circuit: Improvement vs Baseline (Factor x)', fontsize=14)
    plt.ylabel('Improvement Factor (1.0 = Baseline)')
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, height,
                 f'{height:.1f}x', ha='center', va='bottom', fontsize=12, weight='bold')
                 
    plt.tight_layout()
    plt.savefig('images/nepal_strategy_improvement.png')
    print("Saved images/nepal_strategy_improvement.png")

if __name__ == "__main__":
    run_nepal_ga()
