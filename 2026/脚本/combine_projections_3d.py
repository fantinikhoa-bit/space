import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

# 确保结果保存目录存在
result_dir = r'd:\Users\HONOR\Desktop\base\2026\Results'
os.makedirs(result_dir, exist_ok=True)

class CombineProjections3D:
    def __init__(self):
        pass

    def generate_mock_data(self, n_points=5000):
        """生成模拟数据以绘制可行域和Pareto前沿"""
        # 基础变量
        u = np.random.uniform(0, 1, n_points)
        v = np.random.uniform(0, 1, n_points)
        
        # Pareto Front (Red Stars)
        pf_u = np.linspace(0, 1, 100)
        pf_cost = 10 + 40 * pf_u           # Cost: 10M -> 50M
        pf_time = 20 - 15 * np.sqrt(pf_u)  # Time: 20y -> 5y (非线性下降)
        pf_env = 50 - 40 * (pf_u**2)       # Env: High -> Low
        
        # Feasible Points (Blue Dots)
        noise_cost = np.random.exponential(5, n_points)
        noise_time = np.random.exponential(2, n_points)
        noise_env = np.random.exponential(5, n_points)
        
        idx = np.random.randint(0, 100, n_points)
        
        data_cost = pf_cost[idx] + noise_cost
        data_time = pf_time[idx] + noise_time
        data_env = pf_env[idx] + noise_env
        
        return {
            'cost': data_cost, 'time': data_time, 'env': data_env,
            'pf_cost': pf_cost, 'pf_time': pf_time, 'pf_env': pf_env
        }

    def create_3d_plot(self):
        """创建3D图，组合三个投影"""
        data = self.generate_mock_data()
        
        # 提取数据
        feasible_costs = data['cost']
        feasible_times = data['time']
        feasible_emissions = data['env']
        
        pareto_costs = data['pf_cost']
        pareto_times = data['pf_time']
        pareto_emissions = data['pf_env']
        
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
        ax.set_title('3D Projection: Cost vs Time vs Emissions', fontsize=14, pad=20)
        
        # 添加图例
        ax.legend(loc='upper right', fontsize=10)
        
        # 设置视角
        ax.view_init(elev=30, azim=45)  # 调整视角以获得最佳视图
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        # 保存图形
        output_file = os.path.join(result_dir, 'Q4_Projection_Combined_3D.png')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        
        # 显示图形
        plt.show()
        
        print(f"3D combined projection plot saved to: {output_file}")
        print(f"\nPlot details:")
        print(f"- Feasible points: {len(feasible_costs)}")
        print(f"- Pareto optimal points: {len(pareto_costs)}")
        print(f"- View angle: Elevation=30°, Azimuth=45°")

if __name__ == "__main__":
    combiner = CombineProjections3D()
    combiner.create_3d_plot()