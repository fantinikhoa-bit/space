
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import juno_sustainable_tourism as model  # Import your original model
import importlib

# --- Configuration ---
N_SAMPLES = 1000  # Number of Monte Carlo samples
PERTURBATION = 0.20  # +/- 20% variation in parameters

# Optimal Decision Variables (From your Paper/Results)
# Q_max, tau, f, gamma_e, gamma_i, L
OPTIMAL_GENE = [14517, 0.05, 44.91, 0.20, 0.10, 2]

# Parameters to test for sensitivity (Name in model : Label for plot)
PARAMS = {
    'AVG_SPEND_PER_HEAD': 'Avg Spend ($)',
    'COEFF_GLACIER': 'Glacier Coeff',
    'VISITOR_LOSS_COEFF': 'Demand Sensitivity',
    'SOCIAL_FACTOR_HOUSING': 'Housing Pressure',
    'BASELINE_DAILY_VISITORS': 'Baseline Demand'
}

# Values to capture
OUTPUTS = ['Net_Income', 'Glacier_Retreat', 'Social_Pressure', 
           'Net_Inc', 'Gov_Rev', 'Glacier', 'Carbon', 'Housing', 'Noise']

def run_sensitivity_analysis():
    print(f"Starting Sensitivity Analysis (Monte Carlo n={N_SAMPLES})...")
    
    # 1. Base Values Storage
    base_values = {}
    for param_name in PARAMS:
        base_values[param_name] = getattr(model, param_name)

    # 2. Generate Assumption Samples
    # We create a dictionary of arrays: {Param: [val1, val2...]}
    samples = {}
    np.random.seed(999)
    for param_name, current_val in base_values.items():
        # Uniform distribution around base value +/- 20%
        low = current_val * (1 - PERTURBATION)
        high = current_val * (1 + PERTURBATION)
        samples[param_name] = np.random.uniform(low, high, N_SAMPLES)
    
    # 3. Run Simulation Loop
    results = {out: [] for out in OUTPUTS}
    
    # Create an Individual with the optimal gene
    ind = model.Individual(OPTIMAL_GENE)
    
    for i in range(N_SAMPLES):
        # Apply temporary parameter values to the model module
        for param_name in PARAMS:
            setattr(model, param_name, samples[param_name][i])
            
        # Run calculation
        # Note: calculate_fitness returns (fitness, (E_net, glacier_net, Social_Index))
        try:
            _, objs = model.calculate_fitness(ind)
            E, G, S = objs
            
            # Recalculate granular metrics locally for detailed analysis
            # We need to replicate some minimal logic or extract properties if the model allows.
            # Since model.py returns limited objs, let's quickly re-derive the pieces we need
            # based on the computed flow in the model.
            
            # Unpack Gene
            Q_max, tau, f, gamma_e, gamma_i, L = ind.gene
            
            # --- Re-calc Demand ---
            added_cost = (model.AVG_SPEND_PER_HEAD * tau) + f
            loss_rate = model.VISITOR_LOSS_COEFF * added_cost * (1 + tau)
            actual_demand = model.BASELINE_DAILY_VISITORS * (1 - loss_rate)
            daily_visitors = min(Q_max, max(0, actual_demand))
            T_total = daily_visitors * model.SEASON_DAYS
            
            # --- Re-calc Econ Breakdown ---
            inc_direct = T_total * model.AVG_SPEND_PER_HEAD
            rev_tax = T_total * (model.AVG_SPEND_PER_HEAD * tau)
            rev_fee = T_total * f
            net_gov_rev = (rev_tax + rev_fee) * (1 - model.TAX_COLLECTION_COST)
            
            # --- Re-calc Env Breakdown ---
            budget_env = net_gov_rev * gamma_e
            mit_val = model.MITIGATION_ENV_COEFF * budget_env
            mit_factor_env = mit_val / (1 + mit_val) 
            
            imp_glacier = T_total * model.COEFF_GLACIER
            glacier_net = imp_glacier * (1 - mit_factor_env)
            
            imp_carbon = T_total * model.COEFF_CARBON
            carbon_net = imp_carbon * (1 - mit_factor_env)
            
            # --- Re-calc Social Breakdown ---
            alc_factor = model.ALCOHOL_FACTORS[L]
            p_crowd = daily_visitors / model.POPULATION
            p_housing = model.SOCIAL_FACTOR_HOUSING * p_crowd
            p_noise = p_crowd * alc_factor
            
            # Store Granular Results
            # Note: We append granular keys. The top level keys (Net_Income, etc) 
            # are also in OUTPUTS, so we must be careful not to double append if we use a loop or explicit calls.
            # My previous code block REPLACED the old append, so I should just ensure I append everything in OUTPUTS exactly once.
            
            # Let's map which value goes to which OUTPUT key
            val_map = {
                'Net_Income': E,
                'Glacier_Retreat': G,
                'Social_Pressure': S,
                'Net_Inc': E,
                'Gov_Rev': net_gov_rev,
                'Glacier': glacier_net,
                'Carbon': carbon_net,
                'Housing': p_housing,
                'Noise': p_noise
            }
            
            for key in OUTPUTS:
                results[key].append(val_map[key])
            
        except Exception as e:
            print(f"Error in simulation {i}: {e}")
            # Ensure we append SOMETHING so lengths match
            for key in OUTPUTS:
                results[key].append(0)



    # Restore Model Constants (Cleanup)
    for param_name, val in base_values.items():
        setattr(model, param_name, val)

    # 4. Data Consolidation
    df_params = pd.DataFrame(samples)
    df_out = pd.DataFrame(results)
    
    # Rename columns for plotting
    df_params.columns = [PARAMS[k] for k in PARAMS.keys()]
    
    # --- Analysis & Visualization ---
    
    # A. Robustness Distribution (Box/Violin Plots)
    # Normalize income to Millions
    df_out['Net_Income_M'] = df_out['Net_Income'] / 1e6
    
    plt.figure(figsize=(14, 5))
    
    # Income Distribution
    plt.subplot(1, 3, 1)
    sns.histplot(df_out['Net_Income_M'], kde=True, color='green')
    plt.axvline(320, color='r', linestyle='--', label='Baseline Ref ($320M)')
    plt.title('Distribution of Net Income')
    plt.xlabel('Net Income ($ Million)')
    
    # Glacier Distribution
    plt.subplot(1, 3, 2)
    sns.histplot(df_out['Glacier_Retreat'], kde=True, color='cyan')
    plt.axvline(0.5, color='r', linestyle='--', label='Safety Limit (0.5)')
    plt.title('Distribution of Glacier Regression')
    plt.xlabel('Soccer Fields / Year')
    
    # Social Distribution
    plt.subplot(1, 3, 3)
    sns.histplot(df_out['Social_Pressure'], kde=True, color='orange')
    plt.axvline(0.8, color='r', linestyle='--', label='Safety Limit (0.8)')
    plt.title('Distribution of Social Pressure')
    plt.xlabel('Social Stress Index')
    
    plt.tight_layout()
    plt.savefig('images/sa_robustness_dist.png')
    print("Saved images/sa_robustness_dist.png")

    # B. Sensitivity Indices (Correlation - Tornado Plot Concept)
    # We calculate Spearman Rank Correlation between Inputs and Outputs
    
    correlation_data = []
    
    # Targets to analyze against
    targets = [('Net_Income', 'Net Income'), 
               ('Glacier_Retreat', 'Glacier Impact'), 
               ('Social_Pressure', 'Social Stress')]
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for idx, (target_col, target_label) in enumerate(targets):
        corrs = []
        param_labels = df_params.columns
        import scipy.stats
        
        for p_col in df_params.columns:
            # Spearman correlation (robust to non-linear)
            coef, _ = scipy.stats.spearmanr(df_params[p_col], df_out[target_col])
            corrs.append(coef)
            
        # Plot Bar Chart (Tornado-ish)
        y_pos = np.arange(len(param_labels))
        colors = ['red' if x < 0 else 'blue' for x in corrs]
        
        ax = axes[idx]
        ax.barh(y_pos, corrs, align='center', color=colors, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(param_labels)
        ax.set_xlabel('Correlation Coefficient (Spearman)')
        ax.set_title(f'Sensitivity of {target_label}')
        ax.set_xlim(-1, 1)
        ax.grid(True, axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('images/sa_sensitivity_tornado.png')
    print("Saved images/sa_sensitivity_tornado.png")

    # C. Detailed Correlation Heatmap (Granular)
    # New Granular Outputs to Analyze
    granular_map = {
        'Net_Inc': 'Net Income',
        'Gov_Rev': 'Gov Revenue',
        'Glacier': 'Glacier Retreat',
        'Carbon': 'CO2 Emission',
        'Housing': 'Housing Stress',
        'Noise': 'Noise Level'
    }
    
    # Filter only the granular outputs we want to show
    chosen_outputs = list(granular_map.keys())
    
    # Combine Inputs and Granular Outputs
    df_combined_gran = pd.concat([df_params, df_out[chosen_outputs]], axis=1)
    
    # Calculate Spearman Correlation
    corr_matrix_gran = df_combined_gran.corr(method='spearman')
    
    # Focus: Inputs vs Granular Outputs
    focused_corr_gran = corr_matrix_gran.loc[df_params.columns, chosen_outputs]
    
    # Rename columns for display
    focused_corr_gran.columns = [granular_map[c] for c in focused_corr_gran.columns]

    plt.figure(figsize=(10, 8))
    # Using 'coolwarm' to match the user's reference exactly (Orange-Red vs Blue)
    # Removing linewidths to make it look like the solid blocks in the reference
    sns.heatmap(focused_corr_gran, annot=True, cmap='coolwarm', center=0, fmt=".2f", linewidths=0) 
    plt.title('Deep Dive: Correlation of Assumptions vs Key Sub-Metrics')
    plt.xlabel('Key Performance Indicators (Sub-metrics)')
    plt.ylabel('Model Assumptions (Input Parameters)')
    plt.tight_layout()
    plt.savefig('images/sa_correlation_heatmap_detailed.png')
    print("Saved images/sa_correlation_heatmap_detailed.png")
    
    print("\n=== Sensitivity Analysis Complete ===")
    print("Interpretation:")
    print("1. Robustness: Check the histograms.")
    print("2. Sensitivity: Check Tornado plots.")
    print("3. Correlation: Check Detailed Heatmap for specific impact pathways.")

if __name__ == "__main__":
    run_sensitivity_analysis()
