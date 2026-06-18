
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import numpy as np

def plot_q4_gantt_style():
    """
    Generates a Gantt Chart mimicking the 'Powerpoint Template' style requested.
    - Clean Blue Theme
    - Rounded Bars
    - Left Task Column
    - Top Time Header
    """
    
    # --- Data Setup ---
    # Tasks: Name, Start Year, Duration, Color Level (0-3 for blue intensity)
    tasks = [
        # Phase 1
        ("Phase 1: Mars Camp", 2030, 11, 2),
        ("  - Rocket Fleet Deployment", 2030, 11, 1),
        ("  - Initial Habitat Construction", 2032, 8, 1),
        
        # Phase 2
        ("Phase 2: Mars Base", 2041, 56, 2),
        ("  - Space Elevator Const.", 2041, 15, 1),
        ("  - Industrial Expansion", 2045, 40, 1),
        ("  - Logistics Transition (Hybrid)", 2050, 47, 1),
        
        # Phase 3
        ("Phase 3: Mars City", 2097, 75, 2),
        ("  - Mega-Structure Assembly", 2097, 60, 1),
        ("  - Population Boom (to 1M)", 2100, 72, 1),
        ("  - Eco-System Stabilization", 2120, 52, 1),
        
        # Summary
        ("Total Project Timeline", 2030, 142, 3),
    ]
    
    # Reverse order for plotting (Top-down)
    tasks = tasks[::-1]
    
    n_tasks = len(tasks)
    start_year_global = 2030
    end_year_global = 2180
    total_years = end_year_global - start_year_global
    
    # --- Plot Setup ---
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Colors (Blues)
    # Dark Blue, Medium Blue, Light Blue, Very Light Blue
    colors = ['#d6eaf8', '#85c1e9', '#3498db', '#1a5276'] # 0, 1, 2, 3
    
    # Limits
    ax.set_xlim(start_year_global - 30, end_year_global + 5) # Extra space on left for labels
    ax.set_ylim(0, n_tasks + 2)
    
    # --- Drawing UI Elements ---
    
    # 1. Background Types
    # Draw alternating row backgrounds? No, let's keep it clean white like the template.
    
    # 2. Header Bar (Top)
    header_height = 1.0
    header_y = n_tasks + 0.5
    # Dark Blue Header
    header_rect = patches.Rectangle((start_year_global, header_y), total_years, header_height, 
                                    facecolor='#154360', edgecolor='none', zorder=1)
    ax.add_patch(header_rect)
    
    # Header Grid & Labels (Decades)
    decades = np.arange(2030, 2180, 20)
    for d in decades:
        # Vertical Separator in Header
        ax.axvline(d, ymin=(header_y)/ (n_tasks+2), ymax=(header_y+1)/(n_tasks+2), color='white', linewidth=0.5)
        # Vertical Grid Line in Body
        ax.axvline(d, ymin=0, ymax=(header_y)/(n_tasks+2), color='#ebedef', linestyle='-', linewidth=1, zorder=0)
        
        # Label
        ax.text(d + 10, header_y + 0.5, f"{d}s", color='white', ha='center', va='center', fontweight='bold', fontsize=11)

    # --- Drawing Tasks ---
    
    row_height = 0.6
    
    for i, (name, start, duration, color_idx) in enumerate(tasks):
        y_pos = i + 1
        
        # 1. Task Name (Left Column)
        # Background for name? Maybe light gray pill
        name_bg = patches.FancyBboxPatch((start_year_global - 45, y_pos - 0.3), 40, 0.6,
                                       boxstyle="round,pad=0.1", 
                                       ec="none", fc='#ebedef', zorder=2)
        ax.add_patch(name_bg)
        
        # Text
        # Indent subtasks?
        display_name = name
        weight = 'bold' if color_idx >= 2 else 'normal'
        ax.text(start_year_global - 25, y_pos, display_name, ha='center', va='center', fontsize=10, fontweight=weight, color='#2c3e50')
        
        # 2. Task Bar
        bar_color = colors[color_idx]
        
        # Rounded Bar (FancyBboxPatch)
        # x, y, width, height. Note: FancyBbox puts x,y at center or corner depending. 
        # Using Rectangle coordinates approx.
        bar = patches.FancyBboxPatch((start, y_pos - row_height/2), duration, row_height,
                                   boxstyle="round,pad=0.02,rounding_size=0.2", 
                                   ec="none", fc=bar_color, alpha=0.9, zorder=3)
        ax.add_patch(bar)
        
        # 3. Label Next to Bar (Date Range)
        end_date = start + duration
        label_text = f"{start} - {end_date}"
        ax.text(end_date + 2, y_pos, label_text, ha='left', va='center', fontsize=9, color='#7f8c8d')

    # --- Final Touches ---
    ax.set_yticks([])
    ax.set_xticks([])
    
    # Frame off
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    # Title
    ax.text(start_year_global, n_tasks + 2.5, "Problem 4: Strategic Deployment Roadmap", 
            fontsize=16, fontweight='bold', color='#2c3e50', ha='left')
            
    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Gantt_Style_Blue.png'
    plt.savefig(output_path, dpi=300)
    print(f"Styled Gantt chart saved to {output_path}")

if __name__ == "__main__":
    plot_q4_gantt_style()
