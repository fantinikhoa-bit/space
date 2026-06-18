
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# 配置中文字体以支持绘图显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS'] 
plt.rcParams['axes.unicode_minus'] = False

class SpaceElevatorRisk:
    """
    太空电梯故障模型：基于复合威布尔分布的"浴盆曲线"
    
    题目描述了三个阶段：
    1. 初期磨合衰减 (Early burn-in)：故障率随时间下降 -> 威布尔形状参数 k < 1
    2. 中期随机故障 (Random failure)：故障率恒定 -> 威布尔形状参数 k = 1 (即指数分布)
    3. 后期老化递增 (Late wear-out)：故障率随时间上升 -> 威布尔形状参数 k > 1
    
    为了统一描述这一过程，我们将总风险率 h(t) 建模为这三个分量的叠加（竞争风险模型）：
    h_total(t) = h_early(t) + h_random(t) + h_wear(t)
    
    可靠度函数 R(t) = R_early(t) * R_random(t) * R_wear(t)
    """
    def __init__(self, t_early=2, t_wear_start=15, 
                 k_early=0.5, lam_early=2.0,
                 k_random=1.0, lam_random=50.0,
                 k_wear=4.0, lam_wear=25.0):
        # 参数设置（已针对30年周期可视化进行调整）
        self.k_early = k_early
        self.lam_early = lam_early
        self.k_random = k_random
        self.lam_random = lam_random
        self.k_wear = k_wear
        self.lam_wear = lam_wear
        
    def hazard_rate(self, t):
        """
        返回时间 t 时的瞬时故障率（总风险率）。
        h(t) = h1(t) + h2(t) + h3(t)
        """
        if t <= 0: return 0.0
        
        # 初期故障（磨合期）
        # 避免 t 极小时除以零
        epsilon = 1e-9
        h1 = (self.k_early / self.lam_early) * ((t + epsilon) / self.lam_early)**(self.k_early - 1)
        
        # 随机故障（稳定期）
        h2 = (self.k_random / self.lam_random) * (t / self.lam_random)**(self.k_random - 1)
        
        # 老化故障（耗损期）
        h3 = (self.k_wear / self.lam_wear) * (t / self.lam_wear)**(self.k_wear - 1)
        
        return h1 + h2 + h3
        
    def reliability(self, t):
        """返回直到时间 t 的生存概率（可靠度）：R(t)"""
        # R(t) = exp( - integral(h(u) du) )
        #      = exp( - (H1(t) + H2(t) + H3(t)) )
        if t <= 0: return 1.0
        
        r1 = np.exp(-(t / self.lam_early)**self.k_early)
        r2 = np.exp(-(t / self.lam_random)**self.k_random)
        r3 = np.exp(-(t / self.lam_wear)**self.k_wear)
        return r1 * r2 * r3

    def simulate_failure_time(self):
        """
        基于竞争风险模拟故障时间。
        T = min(T_early, T_random, T_wear)
        """
        t1 = self.lam_early * np.random.weibull(self.k_early)
        t2 = self.lam_random * np.random.weibull(self.k_random)
        t3 = self.lam_wear * np.random.weibull(self.k_wear)
        return min(t1, t2, t3)

class CapacityAttenuation:
    """
    运力衰减模型：线性衰退 + 随机扰动
    
    运力 C(t) = C_0 * (1 - gamma * t + epsilon_t)
    epsilon_t ~ N(0, sigma^2)
    """
    def __init__(self, gamma=0.01, sigma=0.02):
        self.gamma = gamma
        self.sigma = sigma
        
    def get_efficiency(self, t):
        """
        返回时间 t 的效率因子。
        效率 = 1 - gamma*t + 噪声
        并将结果限制在 0 以上。
        """
        deterministic_decay = 1 - self.gamma * t
        random_shock = np.random.normal(0, self.sigma)
        efficiency = deterministic_decay + random_shock
        return max(0.0, efficiency)

class RocketExplosionRisk:
    """
    火箭爆炸风险模型：独立伯努利试验
    """
    def __init__(self, p_success=0.96):
        self.p_success = p_success
        
    def launch_outcome(self, num_launches=1):
        """
        返回 num_launches 次发射的成功次数。
        """
        # 1 = 成功, 0 = 失败 (爆炸)
        outcomes = np.random.binomial(1, self.p_success, num_launches)
        return outcomes

class FuelChainInterruption:
    """
    燃料链中断：泊松过程 (发生) + 指数分布 (持续时间)
    
    发生遵循泊松过程，速率为 lambda_rate (次/单位时间)。
    持续时间遵循指数分布，均值为 1/mu_rate。
    """
    def __init__(self, title="Fuel Supply", lambda_rate=0.5, mean_duration=0.2):
        self.lambda_rate = lambda_rate # 期望每年发生次数
        self.mean_duration = mean_duration # 期望持续时间（年）
        self.mu_rate = 1.0 / mean_duration
        
    def simulate_events(self, T_horizon):
        """
        模拟 T_horizon 时间内的事件。
        返回列表：[(开始时间, 持续时间), ...]
        """
        events = []
        t = 0
        while True:
            # 距离下一次事件的时间间隔 (泊松过程的到达间隔服从指数分布)
            dt = np.random.exponential(1.0 / self.lambda_rate)
            t += dt
            if t > T_horizon:
                break
            
            # 事件持续时间
            duration = np.random.exponential(self.mean_duration)
            events.append((t, duration))
            
        return events

def visualize_models():
    """
    生成图表以验证模型行为是否符合描述。
    """
    # 1. 威布尔故障率曲线 (浴盆曲线)
    se_risk = SpaceElevatorRisk() 
    t_vals = np.linspace(0.1, 30, 100)
    h_vals = [se_risk.hazard_rate(t) for t in t_vals]
    
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 2, 1)
    plt.plot(t_vals, h_vals, 'r-', lw=2)
    plt.title('太空电梯：复合威布尔故障率 (浴盆曲线)')
    plt.xlabel('时间 (年)')
    plt.ylabel('风险率 (故障数/年)')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, max(h_vals)*1.1)
    
    # 2. 运力衰减
    cap_model = CapacityAttenuation(gamma=0.02, sigma=0.05)
    t_sim = np.arange(0, 30, 0.5)
    eff_vals = [cap_model.get_efficiency(t) for t in t_sim]
    
    plt.subplot(2, 2, 2)
    plt.plot(t_sim, eff_vals, 'b-o', markersize=4, alpha=0.7, label='模拟效率值')
    plt.plot(t_sim, 1 - 0.02*t_sim, 'k--', label='确定性趋势 (Gamma=0.02)')
    plt.title('运输运力衰减模型')
    plt.xlabel('时间 (年)')
    plt.ylabel('效率因子')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 3. 火箭发射成功率 (模拟批次)
    rocket_risk = RocketExplosionRisk(p_success=0.96)
    batches = [rocket_risk.launch_outcome(100).sum() for _ in range(50)]
    
    plt.subplot(2, 2, 3)
    plt.hist(batches, bins=range(85, 105), color='g', alpha=0.7, rwidth=0.8)
    plt.title('火箭成功次数分布 (每100次发射)')
    plt.xlabel('成功发射次数')
    plt.ylabel('频数')
    plt.grid(True, alpha=0.3)
    
    # 4. 燃料链中断
    fuel_risk = FuelChainInterruption(lambda_rate=2.0, mean_duration=0.1)
    events = fuel_risk.simulate_events(T_horizon=5) # 5 Years
    
    plt.subplot(2, 2, 4)
    # 绘制时间线
    plt.hlines(1, 0, 5, colors='gray', linewidth=2)
    for start, dur in events:
        plt.hlines(1, start, start+dur, colors='orange', linewidth=10, label='中断事件' if '中断事件' not in plt.gca().get_legend_handles_labels()[1] else "")
    plt.yticks([])
    plt.title('燃料链中断模拟 (泊松过程)')
    plt.xlabel('时间 (年)')
    plt.xlim(0, 5)
    plt.legend()
    plt.grid(True, axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Risk_Models_Visualization.png')
    print("Optimization visualization saved to Risk_Models_Visualization.png")

if __name__ == "__main__":
    visualize_models()
