import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import pandas as pd

# 确保结果保存目录存在
result_dir = r'd:\Users\HONOR\Desktop\base\2026\Results'
os.makedirs(result_dir, exist_ok=True)

# 从CSV文件读取实际数据
csv_file = os.path.join(result_dir, 'Q4_LCA_Results.csv')
df = pd.read_csv(csv_file)

# 提取数据（注意：CSV中的成本单位可能是十亿，需要确认）
costs = df['Total_Cost'].values / 1e9  # 转换为十亿USD
times = df['Total_Time'].values
emissions = df['Total_Emissions'].values / 1e6  # 转换为Mt CO2

# 过滤掉无效数据
valid_mask = (costs > 0) & (times > 0) & (emissions > 0)
costs = costs[valid_mask]
times = times[valid_mask]
emissions = emissions[valid_mask]

# 计算帕累托最优解
def is_pareto_efficient(costs, times, emissions):
    """找出帕累托最优解"""
    n_points = len(costs)
    is_efficient = np.ones(n_points, dtype=bool)
    for i in range(n_points):
        if not is_efficient[i]:
            continue
        # 检查是否有其他点在所有目标上都更优或相等
        is_efficient[i] = not np.any(
            (costs <= costs[i]) & 
            (times <= times[i]) & 
            (emissions <= emissions[i]) &
            ((costs < costs[i]) | (times < times[i]) | (emissions < emissions[i]))
        )
    return is_efficient

# 应用帕累托筛选
pareto_mask = is_pareto_efficient(costs, times, emissions)
feasible_costs = costs
feasible_times = times
feasible_emissions = emissions

# 提取帕累托最优解
pareto_costs = costs[pareto_mask]
pareto_times = times[pareto_mask]
pareto_emissions = emissions[pareto_mask]

# 对帕累托点按成本排序，以便绘制连线
pareto_indices = np.argsort(pareto_costs)
pareto_costs = pareto_costs[pareto_indices]
pareto_times = pareto_times[pareto_indices]
pareto_emissions = pareto_emissions[pareto_indices]

# 创建3D图
fig = plt.figure(figsize=(15, 12))
ax = fig.add_subplot(111, projection='3d')

# 绘制可行区域内的点
scatter = ax.scatter(
    feasible_costs,
    feasible_times,
    feasible_emissions,
    c='b',
    alpha=0.3,
    s=20,
    label='Feasible Points'
)

# 绘制帕累托最优解
ax.scatter(
    pareto_costs,
    pareto_times,
    pareto_emissions,
    c='r',
    marker='*',
    s=150,
    label='Pareto Optimal (Observed)'
)

# 绘制帕累托前沿线
ax.plot(
    pareto_costs,
    pareto_times,
    pareto_emissions,
    'r-',
    linewidth=2,
    alpha=0.7
)

# 设置标签
ax.set_xlabel('Total Cost ($ Billion)', fontsize=12, labelpad=15)
ax.set_ylabel('Total Time (Years)', fontsize=12, labelpad=15)
ax.set_zlabel('Emissions (Mt CO2)', fontsize=12, labelpad=15)

# 设置标题
ax.set_title('3D Pareto Front: Cost vs Time vs Emissions', fontsize=14, pad=20)

# 添加图例
ax.legend(loc='upper right', fontsize=10)

# 设置视角
ax.view_init(elev=30, azim=45)  # 调整视角以获得最佳视图

# 添加网格
ax.grid(True, alpha=0.3)

# 保存图形
output_file = os.path.join(result_dir, 'Q4_3D_Pareto_Front.png')
plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches='tight')

# 显示图形
plt.show()

print(f"3D Pareto front plot saved to: {output_file}")
print(f"\nPlot details:")
print(f"- Feasible points: {len(feasible_costs)}")
print(f"- Pareto optimal points: {len(pareto_costs)}")
print(f"- View angle: Elevation=30°, Azimuth=45°")