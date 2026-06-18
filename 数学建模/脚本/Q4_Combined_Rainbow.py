
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

# --- Global Style ---
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 12,
    'axes.labelsize': 13,
    'axes.titlesize': 15,
    'axes.titleweight': 'bold',
    'legend.fontsize': 11,
    'grid.alpha': 0.3,
    'figure.dpi': 300, 
    'axes.spines.top': False,
    'axes.spines.right': False,
})

def plot_combined_rainbow():
    """
    Combines Decomposition (Donuts) and Configuration (Bars) into a single
    'Rainbow' themed poster-style visualization.
    """
    print("Generating Combined Rainbow Plot...")
    
    # Define Rainbow Palette for Phases (Camp -> Base -> City)
    # Red/Orange -> Green/Teal -> Blue/Purple
    phase_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1'] # Modern "Rainbow" (Coral, Teal, Sky)
    # Let's go for a more standard vibrant rainbow transition
    # Phase 1: Warmer (Orange/Red)
    # Phase 2: Middle (Green/Lime)
    # Phase 3: Cooler (Blue/Violet)
    phase_colors = ['#FF9F43', '#2ECC71', '#54A0FF'] 
    
    phases = ['Stage 1\nCamp', 'Stage 2\nBase', 'Stage 3\nCity']

    # Create layout
    fig = plt.figure(figsize=(16, 12)) 
    gs = gridspec.GridSpec(2, 3, height_ratios=[1, 1], hspace=0.3, wspace=0.3)
    
    # ==========================================
    # TOP ROW: Performance Decomposition (Donuts)
    # ==========================================
    time_data = [11.2, 55.9, 74.5]
    cost_data = [7.2, 25.9, 31.1]
    emissions_data = [29.6, 75.4, 76.4]
    
    donut_data = [
        (time_data, "Time Distribution", "Years", 141.5),
        (cost_data, "Cost Distribution", "$T", 64.3),
        (emissions_data, "Emissions Distribution", "Mt", 181.9)
    ]
    
    for i, (data, title, unit, total) in enumerate(donut_data):
        ax = fig.add_subplot(gs[0, i])
        
        wedges, texts, autotexts = ax.pie(data, labels=phases, autopct='%1.0f%%', 
                                          startangle=140, colors=phase_colors, pctdistance=0.82, 
                                          wedgeprops=dict(width=0.35, edgecolor='white', linewidth=2),
                                          textprops=dict(color="#333333"))
        
        # Center Text
        ax.text(0, 0, f"{total}\n{unit}", ha='center', va='center', fontweight='bold', fontsize=16, color='#2C3E50')
        ax.set_title(title, fontsize=14, pad=10)
        
        # Clarify labels
        for t in texts:
            t.set_fontsize(9)
        for at in autotexts:
            at.set_color('white')
            at.set_fontweight('bold')

    # ==========================================
    # BOTTOM ROW: Configuration (Combined Bar)
    # ==========================================
    # Spanning all columns
    ax_bar = fig.add_subplot(gs[1, :])
    
    mass_se = [6.0, 30.0, 40.0]        
    mass_rocket = [4.0, 10.0, 10.0]    
    alpha_vals = [0.60, 0.75, 0.80]    
    
    x = np.arange(len(phases))
    width = 0.5
    
    # Draw Bars
    # SE Mass = Phase Color (Rainbow)
    # Rocket Mass = Grey (To contrast "Dirty")
    
    p1 = ax_bar.bar(x, mass_se, width, label='Space Elevator (Clean)', color=phase_colors, alpha=0.9, edgecolor='white', linewidth=1)
    p2 = ax_bar.bar(x, mass_rocket, width, bottom=mass_se, label='Rocket (Heavy)', color='#5F27CD', alpha=0.8, hatch='//', edgecolor='white')

    # Add Values
    for i in range(len(phases)):
        ax_bar.text(x[i], mass_se[i]/2, f"{mass_se[i]}", ha='center', va='center', color='white', fontweight='bold', fontsize=12)
        ax_bar.text(x[i], mass_se[i] + mass_rocket[i]/2, f"{mass_rocket[i]}", ha='center', va='center', color='white', fontweight='bold', fontsize=12)

    # Line Plot for Alpha
    ax_alpha = ax_bar.twinx()
    # Use a gradient line or just a solid contrasting line? Let's use a solid dark line.
    ax_alpha.plot(x, alpha_vals, color='#EE5A24', marker='o', markersize=12, linewidth=4, linestyle='-', label=r'Optimal $\alpha_{SE}$', markeredgecolor='white', markeredgewidth=2)
    
    # Customizing axes
    ax_bar.set_ylabel('Visualized Mass Transport (Million Tons)', fontsize=14)
    ax_bar.set_title('Strategy Configuration: Rainbow Transition to Sustainability', pad=20, fontsize=16)
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(phases, fontsize=13)
    ax_bar.set_ylim(0, 60)
    
    ax_alpha.set_ylabel(r'Space Elevator Ratio ($\alpha_{SE}$)', fontsize=14, color='#EE5A24')
    ax_alpha.set_ylim(0.4, 1.0)
    ax_alpha.tick_params(axis='y', labelcolor='#EE5A24')
    ax_alpha.spines['right'].set_color('#EE5A24')
    ax_alpha.spines['right'].set_linewidth(2)

    # Add Alpha Labels
    for i, alpha in enumerate(alpha_vals):
        ax_alpha.text(x[i], alpha + 0.04, f"$\\alpha={alpha}$", ha='center', va='bottom', fontweight='bold', color='#EE5A24', 
                 bbox=dict(facecolor='white', alpha=0.9, edgecolor='#EE5A24', boxstyle='round,pad=0.3'))

    # Legends
    # We need a legend that explains the Bars (SE vs Rocket) and the Line
    # Create custom handles for the rainbow bars is tricky, so let's just use a generic proxy
    from matplotlib.lines import Line2D
    import matplotlib.patches as mpatches
    
    legend_elements = [
        mpatches.Patch(facecolor='gray', label='Space Elevator (Colored by Phase)'),
        mpatches.Patch(facecolor='#5F27CD', hatch='//', alpha=0.8, label='Rocket Transport'),
        Line2D([0], [0], color='#EE5A24', linewidth=3, marker='o', label=r'SE Usage Ratio ($\alpha$)')
    ]
    ax_bar.legend(handles=legend_elements, loc='upper left', fontsize=12, framealpha=0.9)

    plt.suptitle("Problem 4: Optimal Strategy & Performance Decomposition", fontsize=20, fontweight='bold', y=0.96)
    
    output_path = 'MCM_Models/Q4_Combined_Rainbow.png'
    plt.savefig(output_path, bbox_inches='tight')
    print(f"Saved {output_path}")

if __name__ == "__main__":
    plot_combined_rainbow()
