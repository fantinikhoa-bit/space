import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# 确保结果保存目录存在
result_dir = 'd:\\Users\\HONOR\\Desktop\\base\\2026\\Results'
os.makedirs(result_dir, exist_ok=True)

class MoonTransportOptimizer:
    def __init__(self):
        # 模型参数（使用新数据）
        self.params = {
            'M_total': 100000000,  # 月球殖民地建设所需总物资量（吨）
            'Q_se': 179000,  # 太空电梯年运输能力（吨/年）
            'n': 10,  # 火箭发射场总数
            'T_se_cycle': 7,  # 太空电梯单次运输周期（天）
            'Q_r_max': 150,  # 火箭单次最大运力（吨）
            'Q_r_avg': 150,  # 火箭单次平均运力（吨）
            'rocket_max_launches_per_site': 730,  # 每年单座发射火箭的最高上线（次）
            'C_se_unit': 500000,  # 太空电梯单位运输成本（美元/吨），450-600美元/公斤 = 450000-600000美元/吨
            'C_r_unit': 1000000,  # 火箭单位运输成本（美元/吨），90~112.5万美元/吨
            'C_r_site': 3000000,  # 火箭发射场启用固定成本（美元），250万-400万美元
            # 太空电梯运力衰减系数
            'se_capacity_decay': {
                'daily_base_decay': 0.00005,  # 日常运营基础日衰减率（0.005%/天，系绳/结构自然损耗）
                'extreme_weather_decay': 0.008,  # 极端天气单次额外衰减率（0.8%/次，风暴/陨石等影响）
                'extreme_weather_annual': 8,  # 年极端天气发生次数（次/年，合理工况假设）
                'max_decay_limit': 0.4,  # 最大衰减上限（运力不低于额定值60%）
                'maintenance_repair': 0.001  # 定期维护修复率（0.1%/月，抵消部分衰减）
            }
        }
    
    def evaluate(self, individual):
        """评估个体适应度"""
        x = individual[0]  # 太空电梯运输量
        y = individual[1]  # 火箭运输量
        z = individual[2:2+self.params['n']]  # 火箭发射场启用状态
        
        # 自动调整y的值，确保x + y = M_total
        y = self.params['M_total'] - x
        
        # 非负约束
        if x < 0 or y < 0:
            return [float('inf'), float('inf')]  # 非负约束
        
        # 计算太空电梯运力衰减后的实际年运力
        decay_params = self.params['se_capacity_decay']
        daily_decay = decay_params['daily_base_decay'] * 365
        extreme_weather_decay = decay_params['extreme_weather_decay'] * decay_params['extreme_weather_annual']
        maintenance_repair = decay_params['maintenance_repair'] * 12
        total_decay = min(daily_decay + extreme_weather_decay - maintenance_repair, decay_params['max_decay_limit'])
        Q_se_actual = self.params['Q_se'] * (1 - total_decay)
        
        # 太空电梯运力约束（无时间限制，根据实际运力计算）
        if x < 0:
            return [float('inf'), float('inf')]  # 非负约束
        
        # 更新火箭运输能力约束，使用每年单座发射火箭的最高上线730次
        # 无时间限制，根据实际年运力计算
        rocket_annual_capacity = sum(z[i] * self.params['rocket_max_launches_per_site'] * self.params['Q_r_max'] 
                                 for i in range(self.params['n']))
        if y < 0:
            return [float('inf'), float('inf')]  # 非负约束
        
        if x < 0 or y < 0:
            return [float('inf'), float('inf')]  # 非负约束
        
        # 计算太空电梯运力衰减后的实际年运力
        decay_params = self.params['se_capacity_decay']
        # 计算一年的总衰减率
        daily_decay = decay_params['daily_base_decay'] * 365
        extreme_weather_decay = decay_params['extreme_weather_decay'] * decay_params['extreme_weather_annual']
        maintenance_repair = decay_params['maintenance_repair'] * 12
        total_decay = min(daily_decay + extreme_weather_decay - maintenance_repair, decay_params['max_decay_limit'])
        # 实际年运力
        Q_se_actual = self.params['Q_se'] * (1 - total_decay)
        
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
        
        return [C_total, T_total]
    
    def generate_initial_population(self, size=100):
        """生成初始种群"""
        population = []
        for _ in range(size):
            # 随机生成太空电梯运输量（合理范围）
            x = np.random.uniform(0, self.params['M_total'])
            # 确保x + y = M_total
            y = self.params['M_total'] - x
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
            num_objectives=2,
            chromosome_length=2 + self.params['n'],  # x, y, z1, z2, z3
            mutation_rate=0.1,
            crossover_rate=0.8
        )
        
        # 生成初始种群
        initial_population = self.generate_initial_population(population_size)
        
        # 运行算法
        pareto_front, pareto_solutions = nsga2.run(initial_population)
        
        return pareto_front, pareto_solutions
    
    def topsis(self, pareto_front):
        """TOPSIS排序"""
        # 标准化决策矩阵
        normalized_matrix = np.zeros_like(pareto_front)
        for i in range(pareto_front.shape[1]):
            norm = np.linalg.norm(pareto_front[:, i])
            if norm > 0:
                normalized_matrix[:, i] = pareto_front[:, i] / norm
        
        # 确定正理想解和负理想解（最小化问题）
        positive_ideal = np.min(normalized_matrix, axis=0)
        negative_ideal = np.max(normalized_matrix, axis=0)
        
        # 计算到正理想解和负理想解的距离
        distance_positive = np.sqrt(np.sum((normalized_matrix - positive_ideal)**2, axis=1))
        distance_negative = np.sqrt(np.sum((normalized_matrix - negative_ideal)**2, axis=1))
        
        # 计算贴近度
        closeness = distance_negative / (distance_positive + distance_negative)
        
        # 排序
        sorted_indices = np.argsort(closeness)[::-1]  # 从大到小排序
        
        return closeness, sorted_indices
    
    def plot_pareto_front(self, pareto_front, filename='Q1_Pareto_Front.png'):
        """绘制帕累托前沿"""
        plt.figure(figsize=(10, 6))
        plt.scatter(pareto_front[:, 0]/1e6, pareto_front[:, 1], c='blue', alpha=0.7, label='Pareto Optimal Solutions')
        plt.title('Pareto Front: Cost vs Time')
        plt.xlabel('Total Cost (Million USD)')
        plt.ylabel('Total Time (Years)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, filename))
        plt.show()
    
    def plot_topsis_ranking(self, pareto_front, closeness, sorted_indices, filename='Q1_TOPSIS_Ranking.png'):
        """绘制TOPSIS排序结果"""
        plt.figure(figsize=(12, 6))
        
        # 绘制成本和时间的排序
        plt.subplot(1, 2, 1)
        plt.bar(range(len(sorted_indices)), pareto_front[sorted_indices, 0]/1e6, color='green', alpha=0.7)
        plt.title('TOPSIS Ranking: Total Cost')
        plt.xlabel('Ranking')
        plt.ylabel('Total Cost (Million USD)')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        plt.bar(range(len(sorted_indices)), pareto_front[sorted_indices, 1], color='orange', alpha=0.7)
        plt.title('TOPSIS Ranking: Total Time')
        plt.xlabel('Ranking')
        plt.ylabel('Total Time (Years)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, filename))
        plt.show()
    
    def save_results(self, pareto_front, pareto_solutions, closeness, sorted_indices, filename='Q1_Results.csv'):
        """保存结果到CSV文件"""
        results = []
        for i, idx in enumerate(sorted_indices):
            solution = pareto_solutions[idx]
            x = solution[0]
            y = solution[1]
            z = solution[2:2+self.params['n']]
            
            # 创建结果字典
            result = {
                'Rank': i+1,
                'Closeness': closeness[idx],
                'Space_Elevator_Transport': x,
                'Rocket_Transport': y,
                'Total_Cost': pareto_front[idx, 0],
                'Total_Time': pareto_front[idx, 1]
            }
            
            # 添加发射场状态（最多显示前5个发射场）
            for j in range(min(5, len(z))):
                result[f'Launch_Site_{j+1}'] = z[j]
            
            results.append(result)
        
        df = pd.DataFrame(results)
        df.to_csv(os.path.join(result_dir, filename), index=False)
        print(f"Results saved to {os.path.join(result_dir, filename)}")

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
                    if obj_max - obj_min > 0:
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
    print("Running 2026 MCM Problem B: Question 1 - Dual Objective Optimization")
    print("="*60)
    
    # 初始化优化器
    optimizer = MoonTransportOptimizer()
    
    # 运行NSGA-Ⅱ算法
    print("Running NSGA-Ⅱ algorithm...")
    pareto_front, pareto_solutions = optimizer.run_nsga2(generations=50, population_size=100)
    
    print(f"Found {len(pareto_front)} Pareto optimal solutions")
    
    # 运行TOPSIS排序
    print("Running TOPSIS ranking...")
    closeness, sorted_indices = optimizer.topsis(pareto_front)
    
    # 绘制结果
    print("Generating plots...")
    optimizer.plot_pareto_front(pareto_front)
    optimizer.plot_topsis_ranking(pareto_front, closeness, sorted_indices)
    
    # 保存结果
    optimizer.save_results(pareto_front, pareto_solutions, closeness, sorted_indices)
    
    print("="*60)
    print("Question 1 optimization completed successfully!")
    print(f"Results saved in {result_dir}")