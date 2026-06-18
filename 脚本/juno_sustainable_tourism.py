import numpy as np

# --- Default Parameters ---
AVG_SPEND_PER_HEAD = 410.0
COEFF_GLACIER = 4.01413e-9
VISITOR_LOSS_COEFF = 0.0022285
SOCIAL_FACTOR_HOUSING = 0.10856
BASELINE_DAILY_VISITORS = 15000.0

SEASON_DAYS = 180
TAX_COLLECTION_COST = 0.062029
MITIGATION_ENV_COEFF = 8.32956e-9
COEFF_CARBON = 0.02
POPULATION = 100000.0
ALCOHOL_FACTORS = [0.05, 0.07, 0.085053, 0.10]

class Individual:
    def __init__(self, gene):
        self.gene = gene
        self.fitness = None
        self.objs = None

def calculate_fitness(ind):
    Q_max, tau, f, gamma_e, gamma_i, L = ind.gene
    
    # --- Demand ---
    added_cost = (AVG_SPEND_PER_HEAD * tau) + f
    loss_rate = VISITOR_LOSS_COEFF * added_cost * (1 + tau)
    actual_demand = BASELINE_DAILY_VISITORS * (1 - loss_rate)
    daily_visitors = min(Q_max, max(0, actual_demand))
    T_total = daily_visitors * SEASON_DAYS
    
    # --- Economy ---
    inc_direct = T_total * AVG_SPEND_PER_HEAD
    rev_tax = T_total * (AVG_SPEND_PER_HEAD * tau)
    rev_fee = T_total * f
    net_gov_rev = (rev_tax + rev_fee) * (1 - TAX_COLLECTION_COST)
    
    # --- Environment ---
    budget_env = net_gov_rev * gamma_e
    mit_val = MITIGATION_ENV_COEFF * budget_env
    mit_factor_env = mit_val / (1 + mit_val) 
    
    glacier_net = T_total * COEFF_GLACIER * (1 - mit_factor_env)
    
    # --- Social ---
    alc_factor = ALCOHOL_FACTORS[L]
    p_crowd = daily_visitors / POPULATION
    p_housing = SOCIAL_FACTOR_HOUSING * p_crowd
    p_noise = p_crowd * alc_factor
    
    # Combine economic, environmental and social indices
    E_net = inc_direct + net_gov_rev * (1 - gamma_e - gamma_i)
    Social_Index = p_housing + p_noise
    
    # Fitness Function
    # High Income, Low Glacier Retreat, Low Social Pressure
    norm_E = E_net / 1e9
    norm_G = glacier_net / 0.01
    norm_S = Social_Index / 0.02
    
    fitness = norm_E - norm_G - norm_S
    
    return fitness, (E_net, glacier_net, Social_Index)
