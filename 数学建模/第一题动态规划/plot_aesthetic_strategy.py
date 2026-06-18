
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import FancyArrowPatch

# Set high-quality style
plt.style.use('dark_background')
# Define a custom futurist palette
colors = {
    'bg': '#0f111a',
    'grid': '#2a2d3e',
    'text': '#e0e0e0',
    'p1': '#00f2ff', # Cyan (Tech/Speed)
    'p2': '#ff00ff', # Magenta (Balance)
    'p3': '#ffd700', # Gold (Economy)
    'point_select': '#ffffff',
    'pareto_line': '#444444'
}

def load_and_select(stage_num, file_path, w_time, w_cost):
    df = pd.read_csv(file_path)
    # Ensure sorted by Time
    df = df.sort_values('Time')
    
    # Normalize
    t = df['Time'].values
    c = df['Cost'].values
    
    t_min, t_max = t.min(), t.max()
    c_min, c_max = c.min(), c.max()
    
    # Avoid zero div
    t_range = t_max - t_min if (t_max - t_min) > 0 else 1.0
    c_range = c_max - c_min if (c_max - c_min) > 0 else 1.0
    
    # Calculate Score (Minimization)
    # Score = w_t * norm_t + w_c * norm_c
    t_norm = (t - t_min) / t_range
    c_norm = (c - c_min) / c_range
    
    scores = w_time * t_norm + w_cost * c_norm
    best_idx = np.argmin(scores)
    
    return df, df.iloc[best_idx], (t_norm, c_norm)

def plot_aesthetic():
    fig, axes = plt.subplots(1, 3, figsize=(20, 7), facecolor=colors['bg'])
    
    configs = [
        {
            'stage': 1, 'file': 'MCM_Models/Q1_New_DP/Stage_1_IP_Front.csv',
            'wt': 0.7, 'wc': 0.3,
            'color': colors['p1'],
            'title': 'Phase I: The Camp',
            'subtitle': 'Strategy: Velocity First (0.7/0.3)',
            'icon': '' 
        },
        {
            'stage': 2, 'file': 'MCM_Models/Q1_New_DP/Stage_2_IP_Front.csv',
            'wt': 0.5, 'wc': 0.5,
            'color': colors['p2'],
            'title': 'Phase II: The Base',
            'subtitle': 'Strategy: Golden Balance (0.5/0.5)',
            'icon': ''
        },
        {
            'stage': 3, 'file': 'MCM_Models/Q1_New_DP/Stage_3_IP_Front.csv',
            'wt': 0.2, 'wc': 0.8,
            'color': colors['p3'],
            'title': 'Phase III: The City',
            'subtitle': 'Strategy: Cost Efficiency (0.2/0.8)',
            'icon': ''
        }
    ]
    
    for i, cfg in enumerate(configs):
        ax = axes[i]
        try:
            df, best_pt, _ = load_and_select(cfg['stage'], cfg['file'], cfg['wt'], cfg['wc'])
        except Exception as e:
            print(f"Error loading {cfg['file']}: {e}")
            continue

        # Data arrays
        X = df['Time'].values
        Y = df['Cost'].values / 1e12 # Trillions
        
        # 1. Plot the fill under the curve (Glow effect)
        ax.fill_between(X, Y, Y.max(), color=cfg['color'], alpha=0.1)
        ax.fill_between(X, Y, Y.max(), color=cfg['color'], alpha=0.05)
        
        # 2. Plot the Line
        ax.plot(X, Y, color=cfg['color'], linewidth=3, alpha=0.9, 
                solid_capstyle='round', label='Pareto Frontier')
        
        # 3. Plot the Selected Point
        bx, by = best_pt['Time'], best_pt['Cost']/1e12
        ax.scatter([bx], [by], color='white', s=150, zorder=10, edgecolors=cfg['color'], linewidth=3)
        ax.scatter([bx], [by], color=cfg['color'], s=300, zorder=9, alpha=0.4) # Glow ring
        
        # Annotation for the point
        ax.annotate(
            f"{bx:.1f} yr\n${by:.1f}T",
            xy=(bx, by), xytext=(20, 40),
            textcoords='offset points', ha='left', va='bottom',
            color='white', fontsize=12, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='white', connectionstyle='arc3,rad=0.2')
        )
        
        # 4. Styling
        ax.set_facecolor(colors['bg'])
        ax.grid(True, color=colors['grid'], linestyle='--', linewidth=0.8, alpha=0.5)
        for spine in ax.spines.values():
            spine.set_edgecolor(colors['grid'])
            spine.set_linewidth(1.5)
            
        ax.set_xlabel('Duration (Years)', color=colors['text'], fontsize=12, weight='bold')
        ax.set_ylabel('Total Cost (Trillions USD)', color=colors['text'], fontsize=12, weight='bold')
        
        # Title with Icon
        ax.set_title(f"{cfg['title']}\n{cfg['subtitle']}", 
                     color=cfg['color'], fontsize=16, pad=20,loc='left', fontweight='bold')
        
        # Add Weight Vectors (Conceptual)
        # origin in axis coordinates
        # Draw a small compass showing the weight pull
        # Using inset or just an arrow in the corner
        
        # Let's add a "Scan Line" text
        ax.text(0.95, 0.05, f"Optimized Selection", 
                transform=ax.transAxes, ha='right', color=cfg['color'], alpha=0.6, fontsize=10)

    # Global Title
    fig.suptitle("OPTIMAL STRATEGY SELECTION ACROSS DEVELOPMENT PHASES\nRisk-Utility Lifecycle Analysis", 
                 color='white', fontsize=24, fontweight='bold', y=1.05)
    
    plt.tight_layout()
    plt.savefig('MCM_Models/Q1_New_DP/Beautiful_Strategy_Evolution.png', 
                dpi=300, bbox_inches='tight', facecolor=colors['bg'])
    print("Plot saved to MCM_Models/Q1_New_DP/Beautiful_Strategy_Evolution.png")

if __name__ == "__main__":
    plot_aesthetic()
