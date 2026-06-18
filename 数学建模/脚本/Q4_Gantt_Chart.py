
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def plot_q4_gantt_chart():
    """
    Generates a high-quality Gantt Chart for the Problem 4 Phased Transition Strategy.
    Shows the timeline of Stages (Camp, Base, City) and the operational modes of SE/Rockets.
    """
    
    # Define Timelines (Based on Optimization Results)
    # Start Year: 2030 (Assumption)
    start_year = 2030
    
    # Durations (Years)
    d1 = 11.2  # Camp
    d2 = 55.9  # Base
    d3 = 74.5  # City
    
    # End Years
    e1 = start_year + d1
    e2 = e1 + d2
    e3 = e2 + d3
    
    # Milestones
    milestones = [
        (start_year, 'Program Start'),
        (e1, 'Stage 1 Complete\n(Camp Established)'),
        (e2, 'Stage 2 Complete\n(Base Operational)'),
        (e3, 'Stage 3 Complete\n(City Inhabited)')
    ]
    
    # Setup Figure
    fig, ax = plt.subplots(figsize=(14, 7))
    plt.title('Problem 4: Optimization-Based Phased Deployment Schedule (2030 - 2171)', fontsize=16, fontweight='bold', pad=20)
    
    # --- Draw Stages as Colored Blocks ---
    # Y position: 3
    
    # Stage 1: Camp (Rocket Heavy)
    ax.broken_barh([(start_year, d1)], (3, 0.8), facecolors='#e74c3c', edgecolor='black', alpha=0.9)
    ax.text(start_year + d1/2, 3.4, 'Stage 1: Mars Camp\n(Rocket Sprint)', ha='center', va='center', color='white', fontweight='bold', fontsize=10)
    
    # Stage 2: Base (Green Shift)
    ax.broken_barh([(e1, d2)], (3, 0.8), facecolors='#f1c40f', edgecolor='black', alpha=0.9)
    ax.text(e1 + d2/2, 3.4, 'Stage 2: Mars Base\n(Transition)', ha='center', va='center', color='black', fontweight='bold', fontsize=10)
    
    # Stage 3: City (Sustainable)
    ax.broken_barh([(e2, d3)], (3, 0.8), facecolors='#2ecc71', edgecolor='black', alpha=0.9)
    ax.text(e2 + d3/2, 3.4, 'Stage 3: Mars City\n(Sustainable Scale)', ha='center', va='center', color='white', fontweight='bold', fontsize=10)
    
    # --- Draw Logistics Intensity (Rocket vs SE) ---
    # Draw bars representing usage intensity? Or just text annotations?
    # Let's draw "Activity Streams" below.
    
    # Space Elevator Stream (Y: 1.5)
    # Alpha increases: 0.6 -> 0.75 -> 0.80
    ax.broken_barh([(start_year, d1)], (1.5, 0.6), facecolors='#3498db', alpha=0.6) # 0.6
    ax.broken_barh([(e1, d2)], (1.5, 0.6), facecolors='#3498db', alpha=0.75)  # 0.75
    ax.broken_barh([(e2, d3)], (1.5, 0.6), facecolors='#3498db', alpha=0.9)   # 0.80 (Most intense)
    ax.text(start_year - 5, 1.8, 'Space Elevator\nUtilization', ha='right', va='center', fontweight='bold', color='#2980b9')
    
    # Add Alpha Labels
    ax.text(start_year + d1/2, 1.8, '60%', ha='center', color='white', fontweight='bold')
    ax.text(e1 + d2/2, 1.8, '75%', ha='center', color='white', fontweight='bold')
    ax.text(e2 + d3/2, 1.8, '80%', ha='center', color='white', fontweight='bold')

    # Rocket Stream (Y: 0.5)
    # Alpha decreases: 0.4 -> 0.25 -> 0.20
    ax.broken_barh([(start_year, d1)], (0.5, 0.6), facecolors='#e67e22', alpha=0.9) # 0.4 (High)
    ax.broken_barh([(e1, d2)], (0.5, 0.6), facecolors='#e67e22', alpha=0.5)  # 0.25
    ax.broken_barh([(e2, d3)], (0.5, 0.6), facecolors='#e67e22', alpha=0.3)  # 0.20 (Low)
    ax.text(start_year - 5, 0.8, 'Heavy Rocket\nUtilization', ha='right', va='center', fontweight='bold', color='#d35400')

    # Add Share Labels
    ax.text(start_year + d1/2, 0.8, '40%', ha='center', color='white', fontweight='bold')
    ax.text(e1 + d2/2, 0.8, '25%', ha='center', color='black', fontweight='bold')
    ax.text(e2 + d3/2, 0.8, '20%', ha='center', color='black', fontweight='bold')

    # --- Formatting ---
    ax.set_ylim(0, 5)
    ax.set_xlim(start_year - 10, e3 + 10)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_yticks([]) # Hide Y ticks
    
    # Add Milestone Lines
    for date, label in milestones:
        ax.axvline(date, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax.text(date, 4.2, f"{label}\n({date:.0f})", ha='center', fontsize=9, rotation=0)

    # Add Grid for decades
    ticks = np.arange(2030, 2180, 10)
    ax.set_xticks(ticks)
    ax.grid(axis='x', linestyle=':', alpha=0.5)
    
    # Legend manually
    # legend_patches = [
    #     mpatches.Patch(color='#e74c3c', label='High Emission Phase'),
    #     mpatches.Patch(color='#2ecc71', label='Low Emission Phase')
    # ]
    # ax.legend(handles=legend_patches, loc='upper right')

    plt.tight_layout()
    output_path = 'MCM_Models/Q4_Phased_Gantt_Chart.png'
    plt.savefig(output_path, dpi=300)
    print(f"Gantt chart saved to {output_path}")

if __name__ == "__main__":
    plot_q4_gantt_chart()
