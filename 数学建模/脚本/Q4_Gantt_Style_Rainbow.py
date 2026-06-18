
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import matplotlib.patheffects as pe

def plot_q4_gantt_style_rainbow_arrow():
    """
    Generates a stylized Gantt Chart with a RAINBOW color scheme and ARROW-shaped bars.
    """
    
    # --- Data Setup ---
    tasks = [
        # Phase 1: The Sprint (Red/Warm)
        ("Phase 1: Mars Camp", 2050, 11, 0),
        ("  - Rocket Fleet Deployment", 2050, 11, 1),
        ("  - Initial Habitat Construction", 2052, 8, 1),
        
        # Phase 2: The Transition (Green/Nature)
        ("Phase 2: Mars Base", 2061, 56, 2),
        ("  - Space Elevator Const.", 2061, 15, 3),
        ("  - Industrial Expansion", 2065, 40, 3),
        ("  - Logistics Transition (Hybrid)", 2070, 47, 3),
        
        # Phase 3: The City (Purple/Future)
        ("Phase 3: Mars City", 2117, 75, 4),
        ("  - Mega-Structure Assembly", 2117, 60, 5),
        ("  - Population Boom (to 1M)", 2120, 72, 5),
        ("  - Eco-System Stabilization", 2140, 52, 5),
        
        # Summary
        ("Total Project Timeline", 2050, 142, 6),
    ]
    
    # Reverse order for plotting (Top-down)
    tasks = tasks[::-1]
    
    n_tasks = len(tasks)
    start_year_global = 2050
    end_year_global = 2200
    total_years = end_year_global - start_year_global
    
    # --- Color Palette (Rainbow / Vibrant) ---
    colors = [
        '#e74c3c', # 0: Phase 1 Main (Red)
        '#f39c12', # 1: Phase 1 Sub (Orange)
        '#27ae60', # 2: Phase 2 Main (Green)
        '#2ecc71', # 3: Phase 2 Sub (Light Green)
        '#8e44ad', # 4: Phase 3 Main (Purple)
        '#9b59b6', # 5: Phase 3 Sub (Violet)
        '#34495e', # 6: Total (Dark Slate)
    ]
    
    # --- Plot Setup ---
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(start_year_global - 30, end_year_global + 5)
    ax.set_ylim(0, n_tasks + 2)
    
    # --- Header Bar ---
    header_height = 1.0
    header_y = n_tasks + 0.5
    
    # Create a gradient header
    gradient_colors = plt.cm.rainbow(np.linspace(0, 1, 100))
    step = total_years / 100
    for i in range(100):
        c = gradient_colors[i]
        rect = patches.Rectangle((start_year_global + i*step, header_y), step, header_height, 
                                 facecolor=c, edgecolor='none', zorder=1)
        ax.add_patch(rect)
    
    # Header Grid & Labels
    decades = np.arange(2050, 2200, 20)
    for d in decades:
        ax.axvline(d, ymin=(header_y)/ (n_tasks+2), ymax=(header_y+1)/(n_tasks+2), color='white', linewidth=0.5)
        ax.axvline(d, ymin=0, ymax=(header_y)/(n_tasks+2), color='#ebedef', linestyle='-', linewidth=1, zorder=0)
        ax.text(d + 10, header_y + 0.5, f"{d}s", color='white', ha='center', va='center', fontweight='bold', fontsize=11, 
                path_effects=[pe.withStroke(linewidth=2, foreground='black')])

    # --- Drawing Tasks ---
    row_height = 0.6
    head_length = 3.0 # Years for the arrow head
    
    for i, (name, start, duration, color_idx) in enumerate(tasks):
        y_pos = i + 1
        
        # 1. Task Name Background
        name_bg = patches.FancyBboxPatch((start_year_global - 45, y_pos - 0.3), 40, 0.6,
                                       boxstyle="round,pad=0.1", 
                                       ec="none", fc='#ecf0f1', zorder=2)
        ax.add_patch(name_bg)
        
        # Text
        display_name = name
        weight = 'bold' if color_idx % 2 == 0 else 'normal'
        t_col = colors[color_idx] if weight == 'bold' else '#2c3e50'
        
        ax.text(start_year_global - 25, y_pos, display_name, ha='center', va='center', 
                fontsize=10, fontweight=weight, color=t_col)
        
        # 2. Task Arrow (Polygon)
        bar_color = colors[color_idx]
        end = start + duration
        
        # Define Polygon Points for Arrow shape
        # (Start, Bottom), (End-Head, Bottom), (End, Middle), (End-Head, Top), (Start, Top)
        
        y_bottom = y_pos - row_height/2
        y_top = y_pos + row_height/2
        
        # Ensure arrow head isn't longer than duration
        curr_head = min(head_length, duration)
        
        poly_points = [
            (start, y_bottom),                  # Bottom Left
            (end - curr_head, y_bottom),        # Bottom Right (before head)
            (end, y_pos),                       # Tip
            (end - curr_head, y_top),           # Top Right (before head)
            (start, y_top)                      # Top Left
        ]
        
        arrow = patches.Polygon(poly_points, closed=True, facecolor=bar_color, edgecolor='none', alpha=0.9, zorder=3)
        ax.add_patch(arrow)
        
        # 3. Label
        label_text = f"{start} - {end}"
        ax.text(end + 2, y_pos, label_text, ha='left', va='center', fontsize=9, color='#7f8c8d')

    # --- Final Touches ---
    ax.set_yticks([])
    ax.set_xticks([])
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    ax.text(start_year_global, n_tasks + 2.5, "Problem 4: Strategic Deployment Roadmap (Rainbow Arrows)", 
            fontsize=16, fontweight='bold', color='#2c3e50', ha='left')
            
    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Gantt_Style_Rainbow.png'
    plt.savefig(output_path, dpi=300)
    print(f"Rainbow Arrow Gantt chart saved to {output_path}")

if __name__ == "__main__":
    plot_q4_gantt_style_rainbow_arrow()
