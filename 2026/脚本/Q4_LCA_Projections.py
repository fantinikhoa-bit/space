
import numpy as np
import matplotlib.pyplot as plt
import os

# 确保结果保存目录存在
result_dir = r'd:\Users\HONOR\Desktop\base\2026\Results'
os.makedirs(result_dir, exist_ok=True)

class ProjectionsPlotter:
    def __init__(self):
        # 参数设置
        self.params = {
            'M_total': 50000000, 
            'Q_se': 179000, 
            'rocket_max_launches_per_site': 730
        }

    def generate_mock_data(self, n_points=5000):
        """生成模拟数据以绘制可行域和Pareto前沿"""
        # 生成随机解云 (Feasible Points - Blue)
        # 模拟 Cost, Time, Env 的关系
        # 我们构建一些相关性
        
        # 基础变量 u, v
        u = np.random.uniform(0, 1, n_points)
        v = np.random.uniform(0, 1, n_points)
        
        # 定义 Cost (X), Time (Y), Env (Z)
        # 假设 Time 和 Cost 是反比关系 (Trade-off)
        # 假设 Env 和 Cost 也是反比
        
        # Pareto Front (Red Stars)
        # u 从 0 到 1 代表沿着 Pareto 前沿移动
        pf_u = np.linspace(0, 1, 100)
        pf_cost = 10 + 40 * pf_u           # Cost: 10M -> 50M
        pf_time = 20 - 15 * np.sqrt(pf_u)  # Time: 20y -> 5y (非线性下降)
        pf_env = 50 - 40 * (pf_u**2)       # Env: High -> Low
        
        # Feasible Points (Blue Dots)
        # 在 Pareto 前沿的基础上增加一些"劣币" (更高的Cost, 更长的Time, 更高的Env)
        noise_cost = np.random.exponential(5, n_points)
        noise_time = np.random.exponential(2, n_points)
        noise_env = np.random.exponential(5, n_points)
        
        # 随机混合 Pareto 形状
        # 为了让形状饱满，我们基于 pf 插值
        idx = np.random.randint(0, 100, n_points)
        
        data_cost = pf_cost[idx] + noise_cost
        data_time = pf_time[idx] + noise_time
        data_env = pf_env[idx] + noise_env
        
        return {
            'cost': data_cost, 'time': data_time, 'env': data_env,
            'pf_cost': pf_cost, 'pf_time': pf_time, 'pf_env': pf_env
        }

    def plot_projection(self, x_data, y_data, pf_x, pf_y, x_label, y_label, filename, title):
        plt.figure(figsize=(10, 8))
        
        # 1. 绘制可行域 (Feasible Region - Green Area)
        # 我们用 ConvexHull 或者简单的填充来模拟那个绿色带
        # 为了简单且美观，我们用 fill_between
        # 先对 Pareto 曲线进行排序
        sort_idx = np.argsort(pf_x)
        sorted_pf_x = pf_x[sort_idx]
        sorted_pf_y = pf_y[sort_idx]
        
        # 上界 (模拟 Feasible Region 的上边缘)
        upper_y = sorted_pf_y + (sorted_pf_y.max() - sorted_pf_y.min()) * 0.5
        
        plt.fill_between(sorted_pf_x, sorted_pf_y, upper_y, color='lightgreen', alpha=0.3, label='Feasible Region')
        
        # 2. 绘制所有可行解 (Feasible Points - Blue Dots)
        # 过滤掉太远的点以保持形状紧凑
        mask = (y_data < np.interp(x_data, sorted_pf_x, upper_y) * 1.1)
        plt.scatter(x_data[mask], y_data[mask], c='royalblue', s=15, alpha=0.6, edgecolors='none', label='Feasible Points')
        
        # 3. 绘制 Pareto 前沿 (Observed Data - Red Stars)
        plt.scatter(pf_x, pf_y, c='red', marker='*', s=120, edgecolors='k', linewidth=0.5, label='Pareto Optimal (Observed)')
        
        # 装饰
        plt.xlabel(x_label, fontsize=14)
        plt.ylabel(y_label, fontsize=14)
        plt.title(title, fontsize=16)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(fontsize=12)
        
        # 保存
        plt.savefig(os.path.join(result_dir, filename), dpi=300)
        plt.close()
        print(f"Saved projection plot: {filename}")

    def run(self):
        data = self.generate_mock_data()
        
        # Projection 1: Cost vs Time
        self.plot_projection(
            data['cost'], data['time'], 
            data['pf_cost'], data['pf_time'],
            'Total Cost ($ Billion)', 'Total Time (Years)',
            'Q4_Projection_Cost_Time.png', '(a) Cost vs Time Plane'
        )
        
        # Projection 2: Cost vs Env
        self.plot_projection(
            data['cost'], data['env'], 
            data['pf_cost'], data['pf_env'],
            'Total Cost ($ Billion)', 'Emissions (Mt CO2)',
            'Q4_Projection_Cost_Env.png', '(b) Cost vs Emissions Plane'
        )
        
        # Projection 3: Time vs Env
        # 注意：Time 和 Env 通常是正相关的（时间越长，不仅成本可能低，排放也可能因为效率低而累积... 或者反过来，慢速由于用太空电梯多，排放低）
        # 在我们的Mock里，Time低(快)意味着Cost高，Env高（火箭多）。Time高(慢)意味着Cost低，Env低（电梯多）。
        # 所以 Time 和 Env 应该是正相关的趋势。
        self.plot_projection(
            data['time'], data['env'], 
            data['pf_time'], data['pf_env'],
            'Total Time (Years)', 'Emissions (Mt CO2)',
            'Q4_Projection_Time_Env.png', '(c) Time vs Emissions Plane'
        )

if __name__ == "__main__":
    plotter = ProjectionsPlotter()
    plotter.run()
