import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from mpl_toolkits.mplot3d import Axes3D

# 确保结果保存目录存在
result_dir = r'd:\Users\HONOR\Desktop\base\2026\Results'
os.makedirs(result_dir, exist_ok=True)

class LCAOptimizer:
    def __init__(self):
        # 模型参数（示例值）
        self.params = {
            # 运输参数
            'M_total': 100000000,  # 总物资量（吨）
            'Q_se': 179000,  # 太空电梯年运输能力（吨/年）
            'n': 10,  # 火箭发射场数量
            'T_se_cycle': 7,  # 太空电梯单次运输周期（天）
            'Q_r_max': 150,  # 火箭单次最大运力（吨）
            'Q_r_avg': 125,  # 火箭单次平均运力（吨）
            'rocket_max_launches_per_site': 730,  # 每年单座发射火箭的最高上线（次）
            'C_se_unit': 500,  # 太空电梯单位运输成本（美元/吨）
            'C_r_unit': 100,  # 火箭单位运输成本（美元/吨）
            'C_r_site': 40000000,  # 火箭发射场固定成本（美元）
            # 太空电梯运力衰减系数
            'se_capacity_decay': {
                'daily_base_decay': 0.00005,  # 日常运营基础日衰减率（0.005%/天，系绳/结构自然损耗）
                'extreme_weather_decay': 0.008,  # 极端天气单次额外衰减率（0.8%/次，风暴/陨石等影响）
                'extreme_weather_annual': 8,  # 年极端天气发生次数（次/年，合理工况假设）
                'max_decay_limit': 0.4,  # 最大衰减上限（运力不低于额定值60%）
                'maintenance_repair': 0.001  # 定期维护修复率（0.1%/月，抵消部分衰减）
            },
            # LCA参数（碳排放因子，单位：吨CO2/吨）
            'lca_factors': {
                # 原材料生产阶段
                'raw_material': {
                    'se_tether': 15.0,  # 太空电梯系绳材料
                    'rocket_fuel': 20.0,  # 火箭燃料
                    'se_structure': 8.0,  # 太空电梯结构材料
                    'rocket_structure': 12.0  # 火箭结构材料
                },
                # 系统建设阶段
                'construction': {
                    'se_earth_port': 50000,  # 太空电梯地球港建设
                    'rocket_site': 10000,  # 火箭发射场建设
                    'se_station': 100000  # 太空电梯空间站建设
                },
                # 运输运营阶段
                'operation': {
                    'se_electricity': 0.1,  # 太空电梯电力消耗
                    'rocket_launch': 30.0,  # 火箭发射
                    'se_maintenance': 0.5,  # 太空电梯维护
                    'rocket_maintenance': 2.0  # 火箭维护
                },
                # 废弃处置阶段
                'disposal': {
                    'se_equipment': 5.0,  # 太空电梯设备处置
                    'rocket_debris': 8.0  # 火箭残骸处置
                }
            },
            # 材料消耗
            'material_consumption': {
                'se_tether': 2000,  # 太空电梯系绳材料（吨）
                'rocket_fuel': 5000,  # 火箭燃料（吨）
                'se_structure': 5000,  # 太空电梯结构材料（吨）
                'rocket_structure': 3000  # 火箭结构材料（吨）
            }
        }
    
    def calculate_lca(self, x, y, z):
        """计算全生命周期碳排放"""
        # 原材料生产阶段碳排放
        E_raw = (
            self.params['material_consumption']['se_tether'] * self.params['lca_factors']['raw_material']['se_tether'] +
            self.params['material_consumption']['rocket_fuel'] * self.params['lca_factors']['raw_material']['rocket_fuel'] +
            self.params['material_consumption']['se_structure'] * self.params['lca_factors']['raw_material']['se_structure'] +
            self.params['material_consumption']['rocket_structure'] * self.params['lca_factors']['raw_material']['rocket_structure']
        )
        
        # 系统建设阶段碳排放
        E_construction = (
            self.params['lca_factors']['construction']['se_earth_port'] +
            sum(z[i] * self.params['lca_factors']['construction']['rocket_site'] for i in range(self.params['n'])) +
            self.params['lca_factors']['construction']['se_station']
        )
        
        # 运输运营阶段碳排放
        E_operation = (
            x * self.params['lca_factors']['operation']['se_electricity'] +
            y * self.params['lca_factors']['operation']['rocket_launch'] +
            x * self.params['lca_factors']['operation']['se_maintenance'] +
            y * self.params['lca_factors']['operation']['rocket_maintenance']
        )
        
        # 废弃处置阶段碳排放
        E_disposal = (
            self.params['lca_factors']['disposal']['se_equipment'] +
            (y / self.params['Q_r_avg']) * self.params['lca_factors']['disposal']['rocket_debris']  # 每发射一次的残骸处置
        )
        
        # 总碳排放
        E_total = E_raw + E_construction + E_operation + E_disposal
        
        return E_total
    
    def evaluate(self, individual):
        """评估个体适应度（三目标）"""
        x = individual[0]  # 太空电梯运输量
        y = individual[1]  # 火箭运输量
        z = individual[2:2+self.params['n']]  # 火箭发射场启用状态
        
        # 约束条件检查
        if x + y < self.params['M_total'] - 100:  # 允许小误差
            return [float('inf'), float('inf'), float('inf')]  # 未满足物资总量约束
        
        # 计算太空电梯运力衰减后的实际年运力
        decay_params = self.params['se_capacity_decay']
        daily_decay = decay_params['daily_base_decay'] * 365
        extreme_weather_decay = decay_params['extreme_weather_decay'] * decay_params['extreme_weather_annual']
        maintenance_repair = decay_params['maintenance_repair'] * 12
        total_decay = min(daily_decay + extreme_weather_decay - maintenance_repair, decay_params['max_decay_limit'])
        Q_se_actual = self.params['Q_se'] * (1 - total_decay)
        
        # 太空电梯运力约束（无时间限制，根据实际运力计算）
        if x < 0:
            return [float('inf'), float('inf'), float('inf')]  # 非负约束
        
        # 更新火箭运输能力约束，使用每年单座发射火箭的最高上线730次
        # 无时间限制，根据实际年运力计算
        rocket_annual_capacity = sum(z[i] * self.params['rocket_max_launches_per_site'] * self.params['Q_r_max'] 
                                 for i in range(self.params['n']))
        if y < 0:
            return [float('inf'), float('inf'), float('inf')]  # 非负约束
        
        # 目标函数1：最小化总成本
        C_total = (self.params['C_se_unit'] * x + 
                  self.params['C_r_unit'] * y + 
                  sum(z[i] * self.params['C_r_site'] for i in range(self.params['n'])))
        
        # 目标函数2：最小化总时间
        T_se = x / Q_se_actual
        # 更新火箭年运输能力计算，使用每年单座发射火箭的最高上线730次
        rocket_annual_capacity = sum(z[i] * self.params['rocket_max_launches_per_site'] * self.params['Q_r_avg'] 
                                 for i in range(self.params['n']))
        T_r = y / rocket_annual_capacity if rocket_annual_capacity > 0 else 0
        T_total = max(T_se, T_r)
        
        # 目标函数3：最小化环境影响（碳排放）
        E_total = self.calculate_lca(x, y, z)
        
        return [C_total, T_total, E_total]
    
    def generate_initial_population(self, size=100):
        """生成初始种群"""
        population = []
        for _ in range(size):
            # 随机生成太空电梯运输量（合理范围）
            x = np.random.uniform(0, self.params['M_total'])
            # 随机生成火箭运输量
            y = np.random.uniform(0, self.params['M_total'] - x)
            # 随机生成火箭发射场启用状态
            z = [np.random.randint(0, 2) for _ in range(self.params['n'])]
            population.append([x, y] + z)
        return population
    
    def run_nsga2(self, generations=100, population_size=100):
        """运行NSGA-Ⅱ算法"""
        # 初始化NSGA-Ⅱ
        nsga2 = NSGA2(
            fitness_function=self.evaluate,
            population_size=population_size,
            num_generations=generations,
            num_objectives=3,
            chromosome_length=2 + self.params['n'],  # x, y, z1, z2, ..., zn
            mutation_rate=0.1,
            crossover_rate=0.8
        )
        
        # 生成初始种群
        initial_population = self.generate_initial_population(population_size)
        
        # 运行算法
        pareto_front, pareto_solutions = nsga2.run(initial_population)
        
        return pareto_front, pareto_solutions
    
    def plot_3d_pareto(self, pareto_front, filename='Q4_LCA_3D_Pareto.png'):
        """绘制3D帕累托前沿"""
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # 绘制帕累托前沿
        scatter = ax.scatter(
            pareto_front[:, 0]/1e6,  # 成本（百万美元）
            pareto_front[:, 1],  # 时间（年）
            pareto_front[:, 2]/1e6,  # 碳排放（百万吨CO2）
            c=pareto_front[:, 0],  # 按成本着色
            cmap='viridis',
            alpha=0.7,
            s=50
        )
        
        # 添加颜色条
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label('Total Cost (Million USD)')
        
        # 设置标签
        ax.set_xlabel('Total Cost (Million USD)')
        ax.set_ylabel('Total Time (Years)')
        ax.set_zlabel('Total Emissions (Million tons CO2)')
        
        # 设置标题
        ax.set_title('3D Pareto Front: Cost vs Time vs Emissions')
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, filename))
        plt.show()
    
    def plot_pairwise(self, pareto_front, filename='Q4_LCA_Pairplot.png'):
        """绘制两两目标之间的关系图"""
        fig, axes = plt.subplots(3, 3, figsize=(15, 12))
        
        # 目标标签
        labels = ['Cost (Million USD)', 'Time (Years)', 'Emissions (Million tons CO2)']
        
        # 数据预处理
        data = [
            pareto_front[:, 0]/1e6,  # 成本（百万美元）
            pareto_front[:, 1],  # 时间（年）
            pareto_front[:, 2]/1e6  # 碳排放（百万吨CO2）
        ]
        
        # 绘制散点图
        for i in range(3):
            for j in range(3):
                if i == j:
                    # 对角线绘制直方图
                    axes[i, j].hist(data[i], bins=20, alpha=0.7)
                    axes[i, j].set_title(labels[i])
                else:
                    # 非对角线绘制散点图
                    scatter = axes[i, j].scatter(data[j], data[i], c=data[0], cmap='viridis', alpha=0.7)
                    axes[i, j].set_xlabel(labels[j])
                    axes[i, j].set_ylabel(labels[i])
        
        # 添加颜色条
        cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
        cbar = fig.colorbar(scatter, cax=cbar_ax)
        cbar.set_label('Cost (Million USD)')
        
        # 调整布局
        plt.tight_layout(rect=[0, 0, 0.9, 1])
        plt.savefig(os.path.join(result_dir, filename))
        plt.show()
    
    def save_results(self, pareto_front, pareto_solutions, filename='Q4_LCA_Results.csv'):
        """保存结果到CSV文件"""
        results = []
        for i, solution in enumerate(pareto_solutions):
            x = solution[0]
            y = solution[1]
            z = solution[2:2+self.params['n']]
            
            # 创建结果字典
            result = {
                'Rank': i+1,
                'Space_Elevator_Transport': x,
                'Rocket_Transport': y,
                'Total_Cost': pareto_front[i, 0],
                'Total_Time': pareto_front[i, 1],
                'Total_Emissions': pareto_front[i, 2]
            }
            
            # 添加发射场状态（最多显示前5个发射场）
            for j in range(min(5, self.params['n'])):
                result[f'Launch_Site_{j+1}'] = z[j]
            
            results.append(result)
        
        df = pd.DataFrame(results)
        df.to_csv(os.path.join(result_dir, filename), index=False)
        print(f"Results saved to {os.path.join(result_dir, filename)}")
    
    def generate_report(self, pareto_front):
        """生成LCA优化报告"""
        print("\n=== 全生命周期评估（LCA）优化报告 ===")
        
        # 计算平均值
        avg_cost = np.mean(pareto_front[:, 0])
        avg_time = np.mean(pareto_front[:, 1])
        avg_emissions = np.mean(pareto_front[:, 2])
        
        # 计算最优值
        min_cost = np.min(pareto_front[:, 0])
        min_time = np.min(pareto_front[:, 1])
        min_emissions = np.min(pareto_front[:, 2])
        
        print(f"\n1. 平均值")
        print(f"   - 总成本: ${avg_cost:,.2f}")
        print(f"   - 总时间: {avg_time:.2f} 年")
        print(f"   - 总碳排放: {avg_emissions:,.2f} 吨CO2")
        
        print(f"\n2. 最优值")
        print(f"   - 最低成本: ${min_cost:,.2f}")
        print(f"   - 最短时间: {min_time:.2f} 年")
        print(f"   - 最低碳排放: {min_emissions:,.2f} 吨CO2")
        
        print(f"\n3. 建议")
        print("   - 优先考虑太空电梯运输，以减少碳排放和成本")
        print("   - 合理规划火箭发射场数量，平衡成本和时间")
        print("   - 定期维护太空电梯，减少运力衰减")
        print("   - 优化火箭发射计划，提高发射效率")

class NSGA2:
    """简化版NSGA-Ⅱ算法"""
    def __init__(self, fitness_function, population_size, num_generations, num_objectives, chromosome_length, mutation_rate=0.1, crossover_rate=0.8):
        self.fitness_function = fitness_function
        self.population_size = population_size
        self.num_generations = num_generations
        self.num_objectives = num_objectives
        self.chromosome_length = chromosome_length
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
    
    def run(self, initial_population):
        population = initial_population
        
        for generation in range(self.num_generations):
            # 计算适应度
            fitness_values = np.array([self.fitness_function(ind) for ind in population])
            
            # 非支配排序
            fronts = self.non_dominated_sorting(fitness_values)
            
            # 拥挤度计算
            crowding_distances = self.crowding_distance(fitness_values, fronts)
            
            # 选择下一代
            new_population = []
            for front in fronts:
                if len(new_population) + len(front) <= self.population_size:
                    new_population.extend([population[i] for i in front])
                else:
                    # 对当前前沿按拥挤度排序并选择
                    front_sorted = sorted(front, key=lambda i: crowding_distances[i], reverse=True)
                    remaining = self.population_size - len(new_population)
                    new_population.extend([population[i] for i in front_sorted[:remaining]])
                    break
            
            # 交叉和变异
            offspring = []
            while len(offspring) < self.population_size:
                # 选择父母
                parent1 = self.tournament_selection(new_population, fitness_values)
                parent2 = self.tournament_selection(new_population, fitness_values)
                
                # 交叉
                if np.random.random() < self.crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # 变异
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                offspring.extend([child1, child2])
            
            population = offspring[:self.population_size]
        
        # 最终种群的非支配前沿
        fitness_values = np.array([self.fitness_function(ind) for ind in population])
        fronts = self.non_dominated_sorting(fitness_values)
        pareto_indices = fronts[0]
        pareto_front = fitness_values[pareto_indices]
        pareto_solutions = [population[i] for i in pareto_indices]
        
        return pareto_front, pareto_solutions
    
    def non_dominated_sorting(self, fitness_values):
        """非支配排序"""
        n = len(fitness_values)
        dominated = [[] for _ in range(n)]
        rank = [0] * n
        count = [0] * n
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    if all(fitness_values[i][k] <= fitness_values[j][k] for k in range(self.num_objectives)) and \
                       any(fitness_values[i][k] < fitness_values[j][k] for k in range(self.num_objectives)):
                        dominated[i].append(j)
                        count[j] += 1
        
        fronts = []
        current_front = []
        for i in range(n):
            if count[i] == 0:
                current_front.append(i)
        
        while current_front:
            next_front = []
            for i in current_front:
                for j in dominated[i]:
                    count[j] -= 1
                    if count[j] == 0:
                        next_front.append(j)
            fronts.append(current_front)
            current_front = next_front
        
        return fronts
    
    def crowding_distance(self, fitness_values, fronts):
        """计算拥挤度"""
        n = len(fitness_values)
        crowding_distances = [0] * n
        
        for front in fronts:
            if len(front) == 1:
                crowding_distances[front[0]] = float('inf')
                continue
            
            for obj in range(self.num_objectives):
                # 按当前目标排序
                sorted_indices = sorted(front, key=lambda i: fitness_values[i][obj])
                
                # 边界点拥挤度设为无穷大
                crowding_distances[sorted_indices[0]] = float('inf')
                crowding_distances[sorted_indices[-1]] = float('inf')
                
                # 计算中间点拥挤度
                if len(sorted_indices) > 2:
                    obj_min = fitness_values[sorted_indices[0]][obj]
                    obj_max = fitness_values[sorted_indices[-1]][obj]
                    if obj_max - obj_min > 1e-10:  # 使用小值避免除零错误
                        for i in range(1, len(sorted_indices)-1):
                            crowding_distances[sorted_indices[i]] += \
                                (fitness_values[sorted_indices[i+1]][obj] - fitness_values[sorted_indices[i-1]][obj]) / \
                                (obj_max - obj_min)
        
        return crowding_distances
    
    def tournament_selection(self, population, fitness_values):
        """锦标赛选择"""
        k = 3
        selected = np.random.choice(len(population), k, replace=False)
        best = selected[0]
        for i in selected[1:]:
            if all(fitness_values[i][j] <= fitness_values[best][j] for j in range(self.num_objectives)) and \
               any(fitness_values[i][j] < fitness_values[best][j] for j in range(self.num_objectives)):
                best = i
        return population[best]
    
    def crossover(self, parent1, parent2):
        """单点交叉"""
        point = np.random.randint(1, len(parent1)-1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    
    def mutate(self, chromosome):
        """变异"""
        for i in range(len(chromosome)):
            if np.random.random() < self.mutation_rate:
                if i < 2:  # x和y是连续变量
                    chromosome[i] = np.random.uniform(0, 10000)  # 随机值
                else:  # z是离散变量
                    chromosome[i] = 1 - chromosome[i]  # 翻转
        return chromosome

if __name__ == "__main__":
    print("Running 2026 MCM Problem B: Question 4 - LCA and Multi-Objective Optimization")
    print("="*60)
    
    # 初始化优化器
    optimizer = LCAOptimizer()
    
    # 运行NSGA-Ⅱ算法
    print("Running NSGA-Ⅱ algorithm for 3-objective optimization...")
    pareto_front, pareto_solutions = optimizer.run_nsga2(generations=50, population_size=100)
    
    print(f"Found {len(pareto_front)} Pareto optimal solutions")
    
    # 绘制结果
    print("Generating LCA optimization plots...")
    optimizer.plot_3d_pareto(pareto_front)
    optimizer.plot_pairwise(pareto_front)
    
    # 保存结果
    optimizer.save_results(pareto_front, pareto_solutions)
    
    # 生成报告
    optimizer.generate_report(pareto_front)
    
    print("="*60)
    print("Question 4 LCA optimization completed successfully!")
    print(f"Results saved in {result_dir}")