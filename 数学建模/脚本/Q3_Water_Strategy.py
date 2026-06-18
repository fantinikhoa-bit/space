
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- 参数配置 ---
class Config:
    # 状态：2050+ City Phase
    Population = 100000
    
    # 需求参数 (基准: 空间站/生态圈数据)
    # 人均日用水: 基于 First-Principles Urban Metabolism Model (Bio + Ind + Muni)
    Water_Per_Capita_Day = 274.5 
    
    # 循环效率
    # 设定两个档次对比
    Recycle_Scenarios = [0.90, 0.95, 0.98, 0.99]
    
    # 太空电梯参数 (唯一运输方式)
    SE_Annual_Capacity = 5.37e8 # 53.7万吨 (从Q1/Q2继承)
    SE_Unit_Cost = 525.0        # $/kg
    
    # 冰砖包装系数
    Ice_Packaging = 0.01 
    
    # 战略储备系数 (Safety Stock)
    # 题目说 "ensure ... sufficient"，通常意味着需要 Safety Buffer
    Safety_Buffer = 0.10 # 额外多运10%防备意外

def solve_city_water():
    print("--- Problem 3: 100k Colony Water Sustainment Analysis ---")
    
    results = []
    
    print(f"\nColony Population: {Config.Population}")
    print(f"Per Capita Usage:  {Config.Water_Per_Capita_Day} kg/day")
    print(f"SE Annual Capacity: {Config.SE_Annual_Capacity/1e6:.2f} Million kg")
    
    print(f"\n{'Recycle Rate':<15} | {'Net Import(Mt)':<15} | {'Cost ($B)':<12} | {'Time (Days)':<12} | {'Capacity Occu.':<15}")
    print("-" * 80)
    
    for eff in Config.Recycle_Scenarios:
        # 1. 基础需求
        daily_gross = Config.Population * Config.Water_Per_Capita_Day
        annual_gross = daily_gross * 365.0
        
        # 2. 净补给 (Net Import)
        # 损耗率 = 1 - eff
        annual_net = annual_gross * (1 - eff)
        
        # 3. 加上包装和安全储备
        # 实际运输量 = 净需求 * (1 + Buffer) * (1 + Pack)
        # 题目问 "Timeline needed"，即运送这些水需要占用的时间
        transport_mass = annual_net * (1 + Config.Safety_Buffer) * (1 + Config.Ice_Packaging)
        
        # 4. 计算指标
        cost = transport_mass * Config.SE_Unit_Cost
        
        # 占用时间 (年)
        time_years = transport_mass / Config.SE_Annual_Capacity
        time_days = time_years * 365.0
        
        # 运力占用率
        occupancy = time_years * 100.0
        
        results.append({
            'Recycle_Rate': eff,
            'Net_Import_Mt': transport_mass / 1e6, # Million kg
            'Cost_Billion': cost / 1e9,
            'Time_Days': time_days,
            'Occupancy_Pct': occupancy
        })
        
        print(f"{eff*100:<14.0f}% | {transport_mass/1e6:<15.2f} | {cost/1e9:<12.2f} | {time_days:<12.1f} | {occupancy:<14.2f}%")
        
    # --- 敏感性绘图 ---
    df = pd.DataFrame(results)
    plot_recycling_sensitivity(df)
    
    # 输出结论
    print("\n--- Key Findings ---")
    best_case = df.iloc[-1] # 99%
    worst_case = df.iloc[0] # 90%
    
    print(f"1. At 90% recycling, water Logistics consumes {worst_case['Occupancy_Pct']:.1f}% of total SE capacity.")
    print(f"   (This is dangerous, crowding out other supplies)")
    print(f"2. At 99% recycling, water consumes only {best_case['Occupancy_Pct']:.1f}% of SE capacity.")
    print(f"   (This is sustainable)")
    
    # Save
    df.to_csv('MCM_Models/Q3_Water_Sustainment.csv', index=False)

def plot_recycling_sensitivity(df):
    plt.figure(figsize=(10, 6))
    
    # 双轴图
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    
    # Bar plot for Cost
    sns.barplot(data=df, x='Recycle_Rate', y='Cost_Billion', ax=ax1, palette='Blues_d', alpha=0.6)
    ax1.set_ylabel('Annual Cost (Billion $)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    # Line plot for Occupancy
    sns.lineplot(data=df, x=df.index, y='Occupancy_Pct', ax=ax2, color='red', marker='o', linewidth=2)
    ax2.set_ylabel('SE Capacity Occupancy (%)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    plt.title('Impact of Water Recycling Efficiency on Logistics Load')
    ax1.set_xlabel('Recycle Rate')
    
    # Fix x-axis labels (Seaborn barplot 0,1,2,3 index issue)
    # ax1.set_xticklabels([f"{x*100:.0f}%" for x in df['Recycle_Rate']])
    
    plt.tight_layout()
    plt.savefig('MCM_Models/Q3_Recycle_Sensitivity.png', dpi=300)
    print("Plot saved to MCM_Models/Q3_Recycle_Sensitivity.png")

if __name__ == "__main__":
    solve_city_water()
