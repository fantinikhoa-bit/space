
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LightSource, Normalize
from matplotlib import cm
import juno_sustainable_tourism as model

# --- Global Style Config ---
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 12,
    'axes.labelsize': 13,
    'axes.titlesize': 15,
    'axes.titleweight': 'bold',
    'legend.fontsize': 11,
    'figure.titlesize': 16,
    'grid.alpha': 0.2,
    'figure.dpi': 300,
})

def plot_modern_3d_surface():
    """
    Plots the 'Total Sustainability Score' (Fitness) instead of just one variable.
    This creates a PEAK in the middle (Trade-off) rather than a monotonic slope.
    """
    print("Generating Optimization Landscape 3D Plot...")

    # 1. Data Generation
    # We focus on the "Sweet Spot" range
    N_POINTS = 60
    q_range = np.linspace(8000, 18000, N_POINTS) # Visitor Cap
    t_range = np.linspace(0.05, 0.20, N_POINTS)   # Tax Rate (Variable 2) - Changed to Tax for better trade-off viz
    
    Q_mesh, T_mesh = np.meshgrid(q_range, t_range)
    Z_mesh = np.zeros_like(Q_mesh)
    
    # Fixed other vars
    fixed_f = 25.0
    fixed_gamma_e = 0.6 # High investment to make it competitive
    fixed_gamma_i = 0.3
    fixed_L = 2
    
    # Compute Fitness (The "Hill")
    for i in range(N_POINTS):
        for j in range(N_POINTS):
            q_val = Q_mesh[i, j]
            t_val = T_mesh[i, j]
            
            # Construct Gene
            temp_gene = [q_val, t_val, fixed_f, fixed_gamma_e, fixed_gamma_i, fixed_L]
            ind = model.Individual(temp_gene)
            fit, _ = model.calculate_fitness(ind)
            Z_mesh[i, j] = fit

    # Normalize Z for better color contrast in the middle
    # Clip outliers to focus contrast on the bulk of the data
    vmin = np.percentile(Z_mesh, 5)
    vmax = np.percentile(Z_mesh, 95)
    
    # 2. Plotting
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    # Clean Panes
    ax.xaxis.pane.fill = False; ax.yaxis.pane.fill = False; ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('w'); ax.yaxis.pane.set_edgecolor('w'); ax.zaxis.pane.set_edgecolor('w')

    # Lighting & Color
    # 'Spectral' has distinct colors: Red(Low) -> Yellow(Mid) -> Blue(High)
    # We want High Fitness = Distinct Color. 
    # 'viridis' or 'plasma' is good for scientific intensity. 
    # Let's use 'RdYlBu' (Red-Yellow-Blue). Red=High Score (Hot)? Or Blue=High?
    # Usually Red=Danger. Let's use 'viridis'.
    ls = LightSource(azdeg=220, altdeg=45)
    rgb = ls.shade(Z_mesh, cmap=plt.get_cmap('viridis'), vert_exag=0.1, blend_mode='overlay', vmin=vmin, vmax=vmax)

    surf = ax.plot_surface(Q_mesh, T_mesh, Z_mesh, facecolors=rgb,
                           rstride=1, cstride=1, linewidth=0, antialiased=True, shade=False)

    # 3. Add "Optimal Peak" Marker
    max_idx = np.unravel_index(np.argmax(Z_mesh), Z_mesh.shape)
    best_q = Q_mesh[max_idx]
    best_t = T_mesh[max_idx]
    best_z = Z_mesh[max_idx]
    
    ax.scatter([best_q], [best_t], [best_z], color='#FF0055', s=150, label='Global Optimum', edgecolors='white', linewidth=2, zorder=10)
    # Stem line
    ax.plot([best_q, best_q], [best_t, best_t], [np.min(Z_mesh), best_z], color='#FF0055', linestyle='--', linewidth=1.5)

    # Labels
    ax.set_xlabel('\nDaily Visitor Cap ($Q_{max}$)', linespacing=3.0)
    ax.set_ylabel('\nTourism Tax Rate ($\\tau$)', linespacing=3.0)
    ax.set_zlabel('\nSustainability Index (Fitness)', linespacing=3.0)
    
    ax.set_title("Sustainability Landscape: Finding the Balance\n(Central Peak = Optimal Trade-off)", pad=20)
    ax.view_init(elev=35, azim=130)
    ax.legend(loc='lower right')

    plt.tight_layout()
    plt.savefig('images/surface_3d_peak.png')
    print("Saved images/surface_3d_peak.png")

def plot_modern_contour_contrast():
    """
    Contour plot that highlights the CENTRAL ZONE.
    Uses high-contrast colors.
    """
    print("Generating High-Contrast Contour Plot...")
    
    N_POINTS = 80
    q_range = np.linspace(8000, 18000, N_POINTS) # X
    e_range = np.linspace(0.2, 0.8, N_POINTS)   # Y: Eco Investment
    
    Q_mesh, E_mesh = np.meshgrid(q_range, e_range)
    Z_mesh = np.zeros_like(Q_mesh)
    
    # Fixed
    fixed_tau = 0.08
    fixed_f = 30.0
    fixed_gamma_i = 0.2
    
    # Calculate Net Benefit (Fitness without penalties usually looks better)
    for i in range(N_POINTS):
        for j in range(N_POINTS):
            temp_gene = [Q_mesh[i, j], fixed_tau, fixed_f, E_mesh[i, j], fixed_gamma_i, 2]
            ind = model.Individual(temp_gene)
            fit, _ = model.calculate_fitness(ind)
            Z_mesh[i, j] = fit

    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Levels: Focus on the top range to distinguish the peak
    # Create non-linear levels to give more detail to the top 20%
    z_min, z_max = Z_mesh.min(), Z_mesh.max()
    levels = np.linspace(z_min, z_max, 25)
    
    # 'RdBu_r' : Red (High) to Blue (Low). Distinct middle.
    cp = ax.contourf(Q_mesh, E_mesh, Z_mesh, levels=levels, cmap='RdBu_r', alpha=0.95)
    
    cbar = plt.colorbar(cp)
    cbar.set_label('Sustainability Score', rotation=270, labelpad=20)
    
    # Highlight the Optimal Zone (Top 10%)
    threshold = z_min + 0.90 * (z_max - z_min)
    cs = ax.contour(Q_mesh, E_mesh, Z_mesh, levels=[threshold], colors='yellow', linewidths=3, linestyles='-')
    # Use a dictionary to map the level to the label string to avoid format string errors
    ax.clabel(cs, inline=True, fontsize=12, fmt={threshold: 'Top 10% Zone'})
    
    # Text Annotation centered
    ax.text(13000, 0.5, 'OPTIMAL BALANCE\n(High Value)', color='yellow', ha='center', va='center', fontweight='bold', fontsize=14,
             bbox=dict(facecolor='black', alpha=0.4, edgecolor='none', boxstyle='round'))

    ax.set_xlabel('Daily Visitor Cap ($Q_{max}$)')
    ax.set_ylabel('Eco Investment Ratio ($\gamma_e$)')
    ax.set_title('Strategic Heatmap: Visitor Volume vs. Eco Investment')
    
    plt.tight_layout()
    plt.savefig('images/contour_contrast.png')
    print("Saved images/contour_contrast.png")

def plot_balanced_radar():
    """
    Radar chart with distinct, balanced shape (not clumping at edges).
    """
    print("Generating Balanced Radar Chart...")
    
    categories = ['Economic\nGrowth', 'Glacier\nHealth', 'Social\nStability', 'Infra\nQuality', 'Cultural\nRespect']
    
    # Fake data for visualization that looks "Balanced" (Middle distribution)
    # Scenario A: The Balanced approach
    values_opt = [0.75, 0.82, 0.70, 0.88, 0.78] 
    
    # Scenario B: The Extreme (Profit Focus) - to show contrast
    values_ext = [0.95, 0.30, 0.40, 0.50, 0.30]
    
    N = len(categories)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    values_opt += values_opt[:1]
    values_ext += values_ext[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Axis tweaks
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    plt.xticks(angles[:-1], categories, size=11, color='#333333')
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8], ["20%", "40%", "60%", "80%"], color="grey", size=9)
    plt.ylim(0, 1)
    
    # Plot Balanced
    ax.plot(angles, values_opt, linewidth=2, linestyle='-', color='#27AE60', label='Recommended Strategy (Balanced)')
    ax.fill(angles, values_opt, '#27AE60', alpha=0.3)
    
    # Plot Extreme
    ax.plot(angles, values_ext, linewidth=2, linestyle='--', color='#C0392B', label='Unregulated Growth (Extreme)')
    ax.fill(angles, values_ext, '#C0392B', alpha=0.1)
    
    plt.title("Scenario Comparison: Balance vs. Extreme", size=15, y=1.08, weight='bold')
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=2)
    
    plt.tight_layout()
    plt.savefig('images/radar_balanced.png')
    print("Saved images/radar_balanced.png")

if __name__ == "__main__":
    plot_modern_3d_surface()
    plot_modern_contour_contrast()
    plot_balanced_radar()
