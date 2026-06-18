
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def verify_q3_sensitivity():
    print("--- Problem 3: Sensitivity Validation ---")
    
    # 1. 变量范围
    # 回收率 (X轴): 从 90% 到 99.5%, 步长 0.5%
    recycle_rates = np.linspace(0.90, 0.995, 20)
    
    # 人均日需求 (Y轴): 从 200 kg 到 400 kg, 步长 20 kg
    # 基准是 274.5 kg
    demands = np.linspace(200, 400, 11)
    
    # 常量
    POPULATION = 100000
    SE_CAPACITY = 5.37e8 # 5.37亿 kg/年
    SAFETY_BUFFER = 0.10
    
    # 结果矩阵
    results = [] # 格式: [Demand, Rate, Load]
    
    for d in demands:
        for r in recycle_rates:
            # 计算年净补给量 Import
            # Import = Pop * Demand * (1-Rate) * 365 * (1+Buffer)
            yearly_import = POPULATION * d * (1 - r) * 365 * (1 + SAFETY_BUFFER)
            
            # 计算负荷率 Load = Import / Capacity
            load_pct = (yearly_import / SE_CAPACITY) * 100.0
            
            results.append({
                'Demand (kg/day)': round(d, 1),
                'Recycle Rate (%)': round(r * 100, 1),
                'SE Load (%)': load_pct
            })
            
    df = pd.DataFrame(results)
    
    # 2. 绘制热力图
    # Pivot for heatmap
    pivot_table = df.pivot(index='Demand (kg/day)', columns='Recycle Rate (%)', values='SE Load (%)')
    # 反转Y轴，让大的在上
    pivot_table = pivot_table.sort_index(ascending=False)
    
    plt.figure(figsize=(12, 8))
    
    # 绘制 Heatmap
    # 颜色映射: 绿色(安全) -> 黄色(警告) -> 红色(崩溃)
    # 关键阈值: 100% (崩溃线)
    sns.heatmap(pivot_table, annot=True, fmt=".0f", cmap="RdYlGn_r", 
                vmin=0, vmax=120, cbar_kws={'label': 'Space Elevator Load (%)'})
    
    plt.title('Validation: SE Load Sensitivity to Demand & Recycling Rate')
    plt.xlabel('Recycling Efficiency (%)')
    plt.ylabel('Per Capita Base Demand (kg/day)')
    
    # 保存到桌面
    output_path = 'd:/Users/HONOR/Desktop/Q3_Sensitivity_Heatmap_Validation.png'
    plt.savefig(output_path, dpi=300)
    print(f"Sensitivity Heatmap saved to {output_path}")
    
    # 显示图像
    plt.show()
    
    # 3. 验证结论
    # 检查在基准 Demand=275 附近，红线在哪里
    baseline_row = df[ np.isclose(df['Demand (kg/day)'], 280, atol=10) ]
    print("\n--- Validation at Baseline Demand (~280 kg) ---")
    print(baseline_row.to_string(index=False))
    
    # 检查是否存在 "Feasibility Cliff"
    print("\n--- Critical Threshold Analysis ---")
    print("Finding the Recycle Rate where Load drops below 100% for various demands...")
    for d in [200, 274.5, 400]:
        # 插值查找
        # 简单遍历
        subset = df[ np.isclose(df['Demand (kg/day)'], d, atol=20) ]
        if not subset.empty:
            safe_configs = subset[subset['SE Load (%)'] <= 100]
            if not safe_configs.empty:
                cutoff = safe_configs.iloc[0]['Recycle Rate (%)']
                print(f"  At Demand {d:.1f} kg: Minimum Recycle Rate = {cutoff}%")
            else:
                print(f"  At Demand {d:.1f} kg: System ALWAYS fails in range [90-99.5%]")

if __name__ == "__main__":
    verify_q3_sensitivity()
