
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
        # 模型参数（与Q4_LCA_NSGA2_fixed.py一致）
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
    
    def generate_initial_population(self, size=100):
        """Generate initial population"""
        population = []
        for _ in range(size):
            # Random transport amounts
            x = np.random.uniform(0, self.params['M_total'])
            y = np.random.uniform(0, self.params['M_total'] - x)
            # Random site activation
            z = [np.random.randint(0, 2) for _ in range(self.params['n'])]
            population.append([x, y] + z)
        return population
    
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
        total_decay = min(daily_decay, decay_params['max_decay_limit'])
        Q_se_actual = self.params['Q_se'] * (1 - total_decay)
        
        # 约束检查
        if x < 0: return [float('inf'), float('inf'), float('inf')]
        if y < 0: return [float('inf'), float('inf'), float('inf')]
        
        # 目标函数1：最小化总成本
        C_total = (self.params['C_se_unit'] * x + 
                  self.params['C_r_unit'] * y + 
                  sum(z[i] * self.params['C_r_site'] for i in range(self.params['n'])))
        
        # 目标函数2：最小化总时间
        T_se = x / Q_se_actual
        rocket_annual_capacity = sum(z[i] * self.params['rocket_max_launches_per_site'] * self.params['Q_r_avg'] 
                                 for i in range(self.params['n']))
        T_r = y / rocket_annual_capacity if rocket_annual_capacity > 0 else 0
        T_total = max(T_se, T_r)
        
        # 目标函数3：最小化环境影响（碳排放）
        E_total = self.calculate_lca(x, y, z)
        
        return [C_total, T_total, E_total]

class NSGA2:
    """简化版NSGA-Ⅱ"""
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
            fitness_values = np.array([self.fitness_function(ind) for ind in population])
            fronts = self.non_dominated_sorting(fitness_values)
            crowding_distances = self.crowding_distance(fitness_values, fronts)
            
            new_population = []
            for front in fronts:
                if len(new_population) + len(front) <= self.population_size:
                    new_population.extend([population[i] for i in front])
                else:
                    front_sorted = sorted(front, key=lambda i: crowding_distances[i], reverse=True)
                    remaining = self.population_size - len(new_population)
                    new_population.extend([population[i] for i in front_sorted[:remaining]])
                    break
            
            offspring = []
            while len(offspring) < self.population_size:
                parent1 = self.tournament_selection(new_population, fitness_values)
                parent2 = self.tournament_selection(new_population, fitness_values)
                if np.random.random() < self.crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                offspring.extend([child1, child2])
            population = offspring[:self.population_size]
        
        fitness_values = np.array([self.fitness_function(ind) for ind in population])
        fronts = self.non_dominated_sorting(fitness_values)
        pareto_indices = fronts[0]
        pareto_front = fitness_values[pareto_indices]
        return pareto_front

    def non_dominated_sorting(self, fitness_values):
        n = len(fitness_values)
        dominated = [[] for _ in range(n)]
        count = [0] * n
        for i in range(n):
            for j in range(n):
                if i != j:
                    if all(fitness_values[i][k] <= fitness_values[j][k] for k in range(self.num_objectives)) and \
                       any(fitness_values[i][k] < fitness_values[j][k] for k in range(self.num_objectives)):
                        dominated[i].append(j)
                        count[j] += 1
        fronts = []
        current_front = [i for i in range(n) if count[i] == 0]
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
        n = len(fitness_values)
        crowding_distances = [0] * n
        for front in fronts:
            if len(front) == 1:
                crowding_distances[front[0]] = float('inf')
                continue
            for obj in range(self.num_objectives):
                sorted_indices = sorted(front, key=lambda i: fitness_values[i][obj])
                crowding_distances[sorted_indices[0]] = float('inf')
                crowding_distances[sorted_indices[-1]] = float('inf')
                if len(sorted_indices) > 2:
                    obj_min = fitness_values[sorted_indices[0]][obj]
                    obj_max = fitness_values[sorted_indices[-1]][obj]
                    if obj_max - obj_min > 1e-10:
                        for i in range(1, len(sorted_indices)-1):
                            crowding_distances[sorted_indices[i]] += \
                                (fitness_values[sorted_indices[i+1]][obj] - fitness_values[sorted_indices[i-1]][obj]) / \
                                (obj_max - obj_min)
        return crowding_distances
    
    def tournament_selection(self, population, fitness_values):
        k = 3
        selected = np.random.choice(len(population), k, replace=False)
        best = selected[0]
        for i in selected[1:]:
            if all(fitness_values[i][j] <= fitness_values[best][j] for j in range(self.num_objectives)) and \
               any(fitness_values[i][j] < fitness_values[best][j] for j in range(self.num_objectives)):
                best = i
        return population[best]
    
    def crossover(self, parent1, parent2):
        point = np.random.randint(1, len(parent1)-1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    
    def mutate(self, chromosome):
        for i in range(len(chromosome)):
            if np.random.random() < 0.1:
                if i < 2:
                    chromosome[i] = np.random.uniform(0, 1000000) # Reset amount
                else:
                    chromosome[i] = 1 - chromosome[i]
        return chromosome

# 模拟不同时期（营地、基地、城市）的参数
# 假设不同时期物资总量不同
periods = {
    'Camp': {'M_total': 5000000}, # 500万吨
    'Base': {'M_total': 30000000}, # 3000万吨
    'City': {'M_total': 65000000}  # 6500万吨
}

optimizer = LCAOptimizer()

for phase, settings in periods.items():
    print(f"Generating plot for {phase} phase...")
    optimizer.params['M_total'] = settings['M_total']
    
    # Run optimization
    nsga2 = NSGA2(
        fitness_function=optimizer.evaluate,
        population_size=50,
        num_generations=30,
        num_objectives=3,
        chromosome_length=12
    )
    pop = optimizer.generate_initial_population(50)
    pareto_front = nsga2.run(pop)
    
    # Plot separately
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(
        pareto_front[:, 0]/1e6,  # Cost
        pareto_front[:, 1],      # Time
        pareto_front[:, 2]/1e6,  # Emissions
        c=pareto_front[:, 0], cmap='viridis', s=50
    )
    ax.set_xlabel('Cost ($M)')
    ax.set_ylabel('Time (Years)')
    ax.set_zlabel('Emissions (Mt CO2)')
    ax.set_title(f'Pareto Front - {phase} Phase')
    fig.colorbar(scatter, label='Cost ($M)')
    
    result_path = os.path.join(result_dir, f'Q4_LCA_3D_Pareto_{phase}.png')
    plt.savefig(result_path)
    plt.close()
    print(f"Saved {result_path}")
