import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.stats import pearsonr

# 确保结果保存目录存在
result_dir = 'd:\\Users\\HONOR\\Desktop\\base\\2026\\Results'
os.makedirs(result_dir, exist_ok=True)

class ReliabilitySensitivityAnalyzer:
    def __init__(self):
        # 模型参数（使用新数据）
        self.params = {
            'M_total': 100000000,  # 总物资量（吨）
            'Q_se': 179000,  # 太空电梯年运输能力（吨/年）
            'n': 10,  # 火箭发射场数量
            'T_se_cycle': 7,  # 太空电梯单次运输周期（天）
            'Q_r_max': 150,  # 火箭单次最大运力（吨）
            'Q_r_avg': 150,  # 火箭单次平均运力（吨）           
            'rocket_max_launches_per_site': 730,  # 每年单座发射火箭的最高上线（次）
            'C_se_unit': 500000,  # 太空电梯单位运输成本（美元/吨），450-600美元/公斤 = 450000-600000美元/吨
            'C_r_unit': 1000000,  # 火箭单位运输成本（美元/吨），90~112.5万美元/吨
            'C_r_site': 3000000,  # 火箭发射场固定成本（美元），250万-400万美元
            # 不确定性因素的分布范围
            'uncertainty_factors': {
                'alpha': [0.0004, 0.0006],  # 太空电梯故障率（0.05%）
                'gamma': [0.80, 1.00],  # 太空电梯运力衰减系数（80%-100%）
                'beta': [0.014, 0.016],  # 火箭发射失败率（1.50%）
                'delta': [0.70, 1.00],  # 火箭运力波动系数（70%-100%）
            }
        }
        # 基础运输方案（参考值）
        self.base_solution = {
            'x': 70000000,  # 太空电梯运输量（吨）
            'y': 30000000,  # 火箭运输量（吨）
            'z': [1, 1, 0]  # 火箭发射场启用状态
        }
    
    def latin_hypercube_sampling(self, n_samples=100):
        """拉丁超立方抽样"""
        factors = list(self.params['uncertainty_factors'].keys())
        n_factors = len(factors)
        
        # 初始化样本矩阵
        samples = np.zeros((n_samples, n_factors))
        
        for i, factor in enumerate(factors):
            low, high = self.params['uncertainty_factors'][factor]
            # 将区间等分为n_samples个子区间
            intervals = np.linspace(low, high, n_samples + 1)
            # 在每个子区间内随机抽样
            for j in range(n_samples):
                samples[j, i] = np.random.uniform(intervals[j], intervals[j+1])
            # 打乱顺序以确保空间填充
            np.random.shuffle(samples[:, i])
        
        return factors, samples
    
    def calculate_transport_metrics(self, sample, factors):
        """计算运输时间和成本"""
        # 解析不确定性因素
        alpha = sample[factors.index('alpha')]  # 太空电梯故障率
        gamma = sample[factors.index('gamma')]  # 太空电梯运力衰减系数
        beta = sample[factors.index('beta')]  # 火箭发射失败率
        delta = sample[factors.index('delta')]  # 火箭运力波动系数
        
        x = self.base_solution['x']
        y = self.base_solution['y']
        z = self.base_solution['z']
        
        # 计算太空电梯运力衰减后的实际年运力
        decay_params = {
            'daily_base_decay': 0.00005,  # 日常运营基础日衰减率（0.005%/天，系绳/结构自然损耗）
            'extreme_weather_decay': 0.008,  # 极端天气单次额外衰减率（0.8%/次，风暴/陨石等影响）
            'extreme_weather_annual': 8,  # 年极端天气发生次数（次/年，合理工况假设）
            'max_decay_limit': 0.4,  # 最大衰减上限（运力不低于额定值60%）
            'maintenance_repair': 0.001  # 定期维护修复率（0.1%/月，抵消部分衰减）
        }
        daily_decay = decay_params['daily_base_decay'] * 365
        extreme_weather_decay = decay_params['extreme_weather_decay'] * decay_params['extreme_weather_annual']
        maintenance_repair = decay_params['maintenance_repair'] * 12
        total_decay = min(daily_decay + extreme_weather_decay - maintenance_repair, decay_params['max_decay_limit'])
        
        # 修正后运输时间
        T_se = x / (self.params['Q_se'] * (1 - total_decay) * gamma)
        # 更新火箭年运输能力计算，使用每年单座发射火箭的最高上线7300次
        rocket_annual_capacity = sum(z[i] * self.params['rocket_max_launches_per_site'] * self.params['Q_r_avg'] * delta 
                                 for i in range(len(z)))
        T_r = y / rocket_annual_capacity if rocket_annual_capacity > 0 else 0
        T_total = max(T_se, T_r) / (1 - alpha)  # 考虑太空电梯故障率
        
        # 修正后运输成本
        C_se = self.params['C_se_unit'] * x / gamma  # 考虑运力衰减
        C_r = self.params['C_r_unit'] * y / delta / (1 - beta)  # 考虑发射失败率
        C_sites = sum(z[i] * self.params['C_r_site'] for i in range(len(z)))
        C_total = C_se + C_r + C_sites
        
        return T_total, C_total
    
    def run_sensitivity_analysis(self, n_samples=100):
        """运行敏感性分析"""
        # 生成拉丁超立方样本
        factors, samples = self.latin_hypercube_sampling(n_samples)
        
        # 计算基础方案的时间和成本
        base_sample = [0.05, 1.0, 0.05, 1.0]  # 基础值
        base_T, base_C = self.calculate_transport_metrics(base_sample, factors)
        
        # 计算每个样本的时间和成本
        results = []
        for i, sample in enumerate(samples):
            T, C = self.calculate_transport_metrics(sample, factors)
            # 计算变化率
            T_change = (T - base_T) / base_T * 100
            C_change = (C - base_C) / base_C * 100
            results.append([i] + list(sample) + [T, C, T_change, C_change])
        
        # 构建结果DataFrame
        columns = ['Sample'] + factors + ['Transport_Time', 'Total_Cost', 'Time_Change', 'Cost_Change']
        df = pd.DataFrame(results, columns=columns)
        
        # 计算敏感性系数
        sensitivity_coeffs = []
        correlation_coeffs = []
        
        for factor in factors:
            # 计算皮尔逊相关系数
            corr_time, _ = pearsonr(df[factor], df['Time_Change'])
            corr_cost, _ = pearsonr(df[factor], df['Cost_Change'])
            correlation_coeffs.append([factor, corr_time, corr_cost])
            
            # 计算标准化敏感性系数
            mean_factor = df[factor].mean()
            mean_time = df['Transport_Time'].mean()
            mean_cost = df['Total_Cost'].mean()
            
            # 简单线性回归斜率作为敏感性指标
            slope_time = np.polyfit(df[factor], df['Transport_Time'], 1)[0]
            slope_cost = np.polyfit(df[factor], df['Total_Cost'], 1)[0]
            
            S_time = slope_time * mean_factor / mean_time
            S_cost = slope_cost * mean_factor / mean_cost
            sensitivity_coeffs.append([factor, S_time, S_cost])
        
        # 构建敏感性系数DataFrame
        coeff_columns = ['Factor', 'Time_Sensitivity', 'Cost_Sensitivity']
        coeff_df = pd.DataFrame(sensitivity_coeffs, columns=coeff_columns)
        
        corr_columns = ['Factor', 'Time_Correlation', 'Cost_Correlation']
        corr_df = pd.DataFrame(correlation_coeffs, columns=corr_columns)
        
        return df, coeff_df, corr_df, factors, base_T, base_C
    
    def plot_sensitivity_analysis(self, df, coeff_df, corr_df, factors):
        """绘制敏感性分析结果"""
        # 1. 敏感性系数条形图
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        x = np.arange(len(factors))
        width = 0.35
        plt.bar(x - width/2, coeff_df['Time_Sensitivity'], width, label='Time Sensitivity', color='blue')
        plt.bar(x + width/2, coeff_df['Cost_Sensitivity'], width, label='Cost Sensitivity', color='green')
        plt.xlabel('Uncertainty Factors')
        plt.ylabel('Sensitivity Coefficient')
        plt.title('Sensitivity Coefficients')
        plt.xticks(x, factors)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        plt.bar(x - width/2, corr_df['Time_Correlation'], width, label='Time Correlation', color='orange')
        plt.bar(x + width/2, corr_df['Cost_Correlation'], width, label='Cost Correlation', color='purple')
        plt.xlabel('Uncertainty Factors')
        plt.ylabel('Correlation Coefficient')
        plt.title('Correlation Coefficients')
        plt.xticks(x, factors)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, 'Q2_Sensitivity_Coefficients.png'))
        plt.show()
        
        # 2. 因素与输出的散点图
        plt.figure(figsize=(16, 12))
        for i, factor in enumerate(factors):
            plt.subplot(2, 2, i+1)
            plt.scatter(df[factor], df['Time_Change'], alpha=0.5, label='Time Change (%)')
            plt.scatter(df[factor], df['Cost_Change'], alpha=0.5, label='Cost Change (%)')
            plt.xlabel(factor)
            plt.ylabel('Change (%)')
            plt.title(f'{factor} vs Output Changes')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, 'Q2_Sensitivity_Scatter.png'))
        plt.show()
        
        # 3. 敏感性龙卷风图
        plt.figure(figsize=(10, 6))
        
        # 按时间敏感性排序
        sorted_df = coeff_df.sort_values('Time_Sensitivity', key=abs, ascending=True)
        x = np.arange(len(sorted_df))
        plt.barh(x, sorted_df['Time_Sensitivity'], color='blue', alpha=0.7)
        plt.yticks(x, sorted_df['Factor'])
        plt.xlabel('Time Sensitivity Coefficient')
        plt.title('Tornado Diagram: Time Sensitivity')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, 'Q2_Sensitivity_Tornado_Time.png'))
        plt.show()
        
        plt.figure(figsize=(10, 6))
        # 按成本敏感性排序
        sorted_df = coeff_df.sort_values('Cost_Sensitivity', key=abs, ascending=True)
        x = np.arange(len(sorted_df))
        plt.barh(x, sorted_df['Cost_Sensitivity'], color='green', alpha=0.7)
        plt.yticks(x, sorted_df['Factor'])
        plt.xlabel('Cost Sensitivity Coefficient')
        plt.title('Tornado Diagram: Cost Sensitivity')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, 'Q2_Sensitivity_Tornado_Cost.png'))
        plt.show()
    
    def save_results(self, df, coeff_df, corr_df):
        """保存结果到CSV文件"""
        df.to_csv(os.path.join(result_dir, 'Q2_Sensitivity_Results.csv'), index=False)
        coeff_df.to_csv(os.path.join(result_dir, 'Q2_Sensitivity_Coefficients.csv'), index=False)
        corr_df.to_csv(os.path.join(result_dir, 'Q2_Sensitivity_Correlations.csv'), index=False)
        print("Results saved successfully!")
    
    def generate_report(self, coeff_df):
        """生成敏感性分析报告"""
        print("=== 敏感性分析报告 ===")
        print("\n1. 关键不确定性因素识别")
        
        # 识别对时间影响最大的因素
        time_sensitive = coeff_df.sort_values('Time_Sensitivity', key=abs, ascending=False).iloc[0]['Factor']
        # 识别对成本影响最大的因素
        cost_sensitive = coeff_df.sort_values('Cost_Sensitivity', key=abs, ascending=False).iloc[0]['Factor']
        
        print(f"\n- 对运输时间影响最大的因素: {time_sensitive}")
        print(f"- 对运输成本影响最大的因素: {cost_sensitive}")
        
        print("\n2. 敏感性系数详情")
        print(coeff_df.to_string(index=False))
        
        print("\n3. 风险缓解建议")
        print("- 针对太空电梯故障率(alpha): 提高系统冗余度，增加定期维护频率")
        print("- 针对太空电梯运力衰减(gamma): 优化系绳材料，定期检测并更换受损部分")
        print("- 针对火箭发射失败率(beta): 改进发射前检测系统，提高火箭可靠性")
        print("- 针对火箭运力波动(delta): 优化火箭设计，减少载重波动")

if __name__ == "__main__":
    print("Running 2026 MCM Problem B: Question 2 - Reliability Sensitivity Analysis")
    print("="*60)
    
    # 初始化分析器
    analyzer = ReliabilitySensitivityAnalyzer()
    
    # 运行敏感性分析
    print("Running Latin Hypercube Sampling...")
    df, coeff_df, corr_df, factors, base_T, base_C = analyzer.run_sensitivity_analysis(n_samples=100)
    
    print(f"Base Transport Time: {base_T:.2f} years")
    print(f"Base Total Cost: ${base_C:.2f}")
    print(f"Generated {len(df)} samples for analysis")
    
    # 绘制结果
    print("Generating sensitivity analysis plots...")
    analyzer.plot_sensitivity_analysis(df, coeff_df, corr_df, factors)
    
    # 保存结果
    analyzer.save_results(df, coeff_df, corr_df)
    
    # 生成报告
    analyzer.generate_report(coeff_df)
    
    print("="*60)
    print("Question 2 sensitivity analysis completed successfully!")
    print(f"Results saved in {result_dir}")