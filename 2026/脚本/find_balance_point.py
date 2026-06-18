
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. 定义核心参数 ---
class Params:
    Total_Demand = 100_000_000  # 1亿吨
    
    # 太空电梯 (SE) - 成本低，必须拉满
    SE_Count = 3
    SE_Cap = 179_000        # 吨/年
    SE_Fixed = 150e9        # 1500亿美元
    SE_OpEx = 525_000       # 52.5万美元/吨
    
    # 传统火箭 (Rocket) - 成本高，用于加速
    R_Cap = 109_500         # 吨/年 (730次 * 150吨)
    R_Fixed = 3.25e6        # 325万美元 (相对于万亿级总成本几乎可忽略)
    R_OpEx = 1_012_500      # 101.25万美元/吨

# --- 2. 边际效应分析 (Marginal Analysis) ---
# 既然太空电梯运营成本远低于火箭 ($0.525M vs $1.0125M)，
# 任何理性的“最低成本”策略都必须优先跑满 3 个太空电梯。
# 所有的权衡（Balance）仅在于：为了赶时间，我们要增加多少个火箭基地？

results = []
prev_time = None
prev_cost = None

print(f"{'Rockets':<8} | {'Time(Y)':<10} | {'Cost(T$)':<10} | {'Saved(Y)':<10} | {'AddCost(T$)':<12} | {'Price($T/Year)':<15}")
print("-" * 80)

for r in range(11): # 0 到 10 个火箭
    # 总运力
    rate_se = Params.SE_Count * Params.SE_Cap
    rate_r = r * Params.R_Cap
    total_rate = rate_se + rate_r
    
    # 核心结果
    time = Params.Total_Demand / total_rate
    
    # 成本计算
    # 固定成本
    fixed = (Params.SE_Count * Params.SE_Fixed) + (r * Params.R_Fixed)
    # 运营成本 (加权平均)
    # 无论怎么组合，总量1亿吨里，谁运了多少比例，就花多少钱
    # 具体的：Cost_Op = Demand * (Rate_SE * Cost_SE + Rate_R * Cost_R) / Total_Rate
    # 其实可以简化为：总Cost = Time * (Rate_SE * Cost_SE_Total + Rate_R * Cost_R_Total) ??? 
    # 不，最准确的是按比例分摊总量。
    
    share_se = rate_se / total_rate
    share_r = rate_r / total_rate
    
    opex_total = Params.Total_Demand * (share_se * Params.SE_OpEx + share_r * Params.R_OpEx)
    total_cost = fixed + opex_total
    
    cost_trillion = total_cost / 1e12
    
    # 边际计算
    if prev_time is None:
        saved_years = 0
        added_cost = 0
        price_per_year = 0
    else:
        saved_years = prev_time - time
        added_cost = cost_trillion - prev_cost
        price_per_year = added_cost / saved_years if saved_years > 0 else 0
        
    results.append({
        "Rockets": r,
        "Time": time,
        "Cost_T": cost_trillion,
        "Saved_Years": saved_years,
        "Added_Cost_T": added_cost,
        "Price_Per_Year": price_per_year
    })
    
    print(f"{r:<8} | {time:<10.1f} | {cost_trillion:<10.2f} | {saved_years:<10.1f} | {added_cost:<12.2f} | {price_per_year:<15.2f}")
    
    prev_time = time
    prev_cost = cost_trillion

df = pd.DataFrame(results)

# --- 3. 寻找平衡点 (Elbow Method & TOPSIS) ---
# 方法 A: 肘部法则 (Elbow Point)
# 观察 Cost/Year Saved 的斜率变化，找出那个“再多花钱就不划算”的点。
# 通常是曲线曲率最大的地方。

# 方法 B: TOPSIS (标准化距离)
# 对 Cost 和 Time 进行标准化并评分
norm_cost = df["Cost_T"] / np.sqrt((df["Cost_T"]**2).sum())
norm_time = df["Time"] / np.sqrt((df["Time"]**2).sum())

# 理想解 (Ideal): Min Cost, Min Time
# 负理想 (Anti): Max Cost, Max Time
# 权重 0.5, 0.5
d_plus = np.sqrt((norm_cost - norm_cost.min())**2 + (norm_time - norm_time.min())**2)
d_minus = np.sqrt((norm_cost - norm_cost.max())**2 + (norm_time - norm_time.max())**2)
score = d_minus / (d_plus + d_minus)
df["TOPSIS_Score"] = score

best_idx = df["TOPSIS_Score"].idxmax()
best_r = df.loc[best_idx, "Rockets"]

print("\n" + "="*30)
print(f"推荐平衡点: {best_r} 个火箭基地")
print("="*30)

# --- 4. 可视化图表 ---
fig, ax1 = plt.subplots(figsize=(10, 6))

color = 'tab:blue'
ax1.set_xlabel('Number of Rocket Sites (with 3 Space Elevators)')
ax1.set_ylabel('Total Time (Years)', color=color)
ax1.plot(df['Rockets'], df['Time'], color=color, marker='o', linewidth=2, label='Time')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, axis='x', linestyle='--')

ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Total Cost (Trillion USD)', color=color)
ax2.plot(df['Rockets'], df['Cost_T'], color=color, marker='s', linewidth=2, linestyle='--', label='Cost')
ax2.tick_params(axis='y', labelcolor=color)

# 标注最佳点
plt.title(f'Finding the Balance Point: Time vs Cost Trade-off\nOptimal Balance: {best_r} Rockets', fontsize=14)
plt.axvline(x=best_r, color='green', linestyle=':', linewidth=2, label='Optimal Balance')

# 标注边际成本
# 在图上标出每增加一个火箭“买时间”的单价
for i in range(1, 11):
    cost_per_year = df.loc[i, "Price_Per_Year"]
    if i % 2 != 0: # 隔一个标一个防止重叠
        ax2.text(i, df.loc[i, "Cost_T"] + 2, f"${cost_per_year:.1f}T/Yr", ha='center', fontsize=8, color='darkred')

fig.tight_layout()
plt.savefig('balance_point_analysis.png')
print("图表已保存: balance_point_analysis.png")
