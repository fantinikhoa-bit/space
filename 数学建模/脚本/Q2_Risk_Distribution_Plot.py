
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import weibull_min, binom, poisson
import matplotlib.cm as cm

def plot_q2_risk_distributions():
    # Set style
    plt.style.use('default') 
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial', 'DejaVu Sans'] 
    plt.rcParams['axes.unicode_minus'] = False 

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Problem 2: Stochastic Models of Risk Factors', fontsize=16, fontweight='bold', y=0.96)

    # Define axes for clarity
    ax1 = axs[0, 0]
    ax2 = axs[0, 1]
    ax3 = axs[1, 0]
    ax4 = axs[1, 1]

    # --- 1. Space Elevator: Bathtub Curve (Weibull Mixture) ---
    t = np.linspace(0, 30, 200)
    # Bathtub = Early Failure (Decreasing) + Random Failure (Constant) + Wear-out (Increasing)
    h_early = 0.5 * (t + 0.1)**(-0.5) 
    h_random = 0.02 
    h_wear = 0.00005 * (t)**2.5
    h_total = h_early * 0.2 + h_random + h_wear * 5.0 
    
    # Use Red/Orange for Failure (Vibrant)
    ax1.plot(t, h_total, color='#FF4500', linewidth=3, label='Failure Rate $\lambda(t)$')
    ax1.fill_between(t, 0, h_total, color='#FF4500', alpha=0.1)
    
    ax1.set_title('Space Elevator: Bathtub Failure Rate', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Time (Years)')
    ax1.set_ylabel('Failure Rate (Events/Year)')
    ax1.grid(True, alpha=0.3)
    ax1.text(1, 0.8, 'Early Failure\n(Burn-in)', color='#FF4500', fontsize=9, fontweight='bold')
    ax1.text(25, 0.4, 'Wear-out\n(Aging)', color='#FF4500', fontsize=9, fontweight='bold')

    # --- 2. Capacity Decay: Stochastic Process ---
    years = np.linspace(0, 30, 60) # half-year steps
    efficiency_det = np.exp(-0.03 * years)
    np.random.seed(42)
    noise = np.random.normal(0, 0.03, len(years))
    efficiency_stoch = np.clip(efficiency_det + noise, 0, 1.0)
    
    # Use Cool color (Purple/Blue)
    ax2.plot(years, efficiency_stoch, 'o-', color='#9b59b6', markersize=5, linewidth=1, label='Simulated Efficiency')
    ax2.plot(years, efficiency_det, '--', color='#2c3e50', linewidth=2, label='Deterministic Trend')
    
    ax2.set_title('Transport Capacity Decay Model', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Time (Years)')
    ax2.set_ylabel('Efficiency Factor')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # --- 3. Rocket Launch Success: Binomial Distribution ---
    n = 100 
    p = 0.95 
    x_vals = np.arange(85, 101)
    probs = binom.pmf(x_vals, n, p)
    
    # Use Rainbow colors
    norm = plt.Normalize(x_vals.min(), x_vals.max())
    colors = plt.cm.rainbow(norm(x_vals))
    
    bars = ax3.bar(x_vals, probs, color=colors, alpha=0.9, edgecolor='black')
    ax3.set_title(f'Rocket Launch Success (Batch of {n})', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Number of Successful Launches')
    ax3.set_ylabel('Probability')
    ax3.grid(True, axis='y', alpha=0.3)
    ax3.axvline(n*p, color='red', linestyle='--', label=f'Exp. Value = {n*p}')
    ax3.legend()

    # --- 4. Fuel Chain Interruption: Poisson Process (Gantt) ---
    interruption_times = []
    current_t = 0
    while current_t < 5:
        dt = np.random.exponential(1.0/0.8) 
        current_t += dt
        if current_t < 5:
            interruption_times.append(current_t)
            
    ax4.axhline(0, color='gray', linewidth=2)
    ax4.set_ylim(-1, 1)
    ax4.set_yticks([]) 
    
    duration = 0.15 
    for i, t_event in enumerate(interruption_times):
        # Pick diverse colors from HSV
        c = cm.hsv(i / len(interruption_times))
        rect = plt.Rectangle((t_event, -0.2), duration, 0.4, facecolor=c, edgecolor='black')
        ax4.add_patch(rect)
        ax4.text(t_event, 0.5, 'Event', ha='left', fontsize=8, rotation=45, color=c, fontweight='bold')
        
    ax4.set_title('Fuel Chain Interruption (Poisson Process)', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Time (Years)')
    ax4.set_xlim(0, 5)
    ax4.grid(True, axis='x', alpha=0.3)

    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    output_path = 'MCM_Models/Q2_Risk_Distributions.png'
    plt.savefig(output_path, dpi=300)
    print(f"Distribution chart saved to {output_path}")

if __name__ == "__main__":
    plot_q2_risk_distributions()
