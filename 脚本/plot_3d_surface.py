
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import juno_sustainable_tourism as model

def plot_beautiful_surface():
    print("Generating High-Resolution 3D Surface Plot...")
    
    # 1. Define Grid Range (X and Y axes)
    # X: Daily Visitors (Q_max) - The scale/size of tourism
    # Y: Environmental Fee (f) or Tax (tau)? Let's use Tax Rate (tau) as it's a major lever.
    # actually, looking at the user image, the axes are labeled "negative of economic index".
    # Let's try to map:
    # X axis: Tourism Scale (Q_max: 8000 to 18000)
    # Y axis: Mitigation Effort (Eco Investment %: gamma_e: 0.2 to 0.8)
    
    N_POINTS = 50
    q_range = np.linspace(8000, 18000, N_POINTS)
    g_range = np.linspace(0.2, 0.8, N_POINTS)
    
    Q_mesh, G_mesh = np.meshgrid(q_range, g_range)
    Z_mesh = np.zeros_like(Q_mesh)
    
    # Fixed optimums for other vars
    # tau=0.05, f=45, gamma_i=0.1, L=2
    fixed_tau = 0.05
    fixed_f = 45.0
    fixed_gamma_i = 0.1
    fixed_L = 2
    
    # 2. Calculate Z for every point on the grid
    # We want Z to look like a trade-off surface.
    # Let's verify what Z is. If we want a Pareto front look, Z usually is 'Objective 2' given 'Objective 1'
    # Let's make Z = Environmental Impact (Glacier Retreat)
    # Or Z = Net Income?
    # User image: Z is "environmental index". X/Y are "negative of economic" and "community".
    # Let's simplify: 
    # X = Net Income (We will compute this)
    # Y = Social Pressure (We will compute this)
    # Z = Environmental Impact
    
    # Actually, generating a surface directly from variables is easier and safer.
    # Let's Plot:
    # X: Visitors (Economic Driver)
    # Y: Eco Investment (Mitigation Driver)
    # Z: Net Environmental Impact (Glacier Result)
    
    for i in range(N_POINTS):
        for j in range(N_POINTS):
            q_val = Q_mesh[i, j]
            gamma_val = G_mesh[i, j]
            
            # Construct a temporary individual
            # gene: [Q_max, tau, f, gamma_e, gamma_i, L]
            temp_gene = [q_val, fixed_tau, fixed_f, gamma_val, fixed_gamma_i, fixed_L]
            ind = model.Individual(temp_gene)
            
            # Run model
            # calculate_fitness returns: fit, (E_net, glacier_net, Social_Index)
            _, objs = model.calculate_fitness(ind)
            E, G, S = objs
            
            Z_mesh[i, j] = G # Glacier Retreat
    
    # 3. Plotting
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create the surface plot
    # cmap='viridis' is good, 'plasma' or 'coolwarm' als good.
    # The user reference has a yellow-green-blue Map (likely 'viridis_r' or similar)
    surf = ax.plot_surface(Q_mesh, G_mesh, Z_mesh, cmap='viridis', 
                           edgecolor='none', alpha=0.9, antialiased=True)
    
    # Customize axes
    ax.set_xlabel('Daily Visitor Cap ($Q_{max}$)', fontsize=12, labelpad=10)
    ax.set_ylabel('Eco Investment Ratio ($\gamma_e$)', fontsize=12, labelpad=10)
    ax.set_zlabel('Glacier Retreat (Index)', fontsize=12, labelpad=10)
    
    ax.set_title('Environmental Impact Surface\n(Trade-off: Economy vs Protection)', fontsize=14)
    
    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=10, pad=0.1)
    
    # Adjust view angle for best "3D" look
    ax.view_init(elev=30, azim=135)
    
    plt.tight_layout()
    plt.savefig('images/ga_solution_space_surface.png', dpi=300)
    print("Saved images/ga_solution_space_surface.png")
    
    # --- Part 2: 2D Contour Plot (Safety Zone) ---
    plt.figure(figsize=(10, 8))
    
    # Filled contour
    # Levels: automatic or custom. Let's use custom to highlight the 0.5 threshold
    levels = np.linspace(Z_mesh.min(), Z_mesh.max(), 20)
    cp = plt.contourf(Q_mesh, G_mesh, Z_mesh, levels=levels, cmap='viridis')
    plt.colorbar(cp, label='Glacier Retreat Index')
    
    # Add the Critical Safety Line (Index = 0.5)
    # We plot a specific contour line at 0.5
    cs = plt.contour(Q_mesh, G_mesh, Z_mesh, levels=[0.5], colors='red', linewidths=3, linestyles='--')
    plt.clabel(cs, inline=1, fontsize=12, fmt='Safety Limit (0.5)')
    
    plt.xlabel('Daily Visitor Cap ($Q_{max}$)', fontsize=12)
    plt.ylabel('Eco Investment Ratio ($\gamma_e$)', fontsize=12)
    plt.title('Decision Boundary: The "Safe Operating Space"', fontsize=14)
    
    # Annotate regions
    # Find a safe point (low Q, high gamma)
    plt.text(10000, 0.7, 'SAFE ZONE\n(Sustainable)', color='white', fontsize=14, weight='bold', ha='center')
    # Find a danger point (high Q, low gamma)
    plt.text(16000, 0.3, 'DANGER ZONE\n(Over-tourism)', color='red', fontsize=14, weight='bold', ha='center')
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('images/ga_solution_space_contour.png', dpi=300)
    print("Saved images/ga_solution_space_contour.png")

if __name__ == "__main__":
    plot_beautiful_surface()
