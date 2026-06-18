import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# 确保结果保存目录存在
result_dir = 'd:\\Users\\HONOR\\Desktop\\base\\2026\\Results'
os.makedirs(result_dir, exist_ok=True)

class WaterSupplyOptimizer:
    def __init__(self):
        # 模型参数（示例值）
        self.params = {
            # 月球殖民地用水需求（吨/年）
            'water_demands': {
                'drink': 100,  # 生活饮用水
                'prod': 300,   # 生产用水
                'eco': 200     # 生态用水
            },
            # 水资源循环利用率
            'recycle_rate': {
                'drink': 0.3,  # 生活饮用水回收率
                'prod': 0.6,   # 生产用水回收率
                'eco': 0.8     # 生态用水回收率
            },
            # 运输成本参数
            'transport_costs': {
                'ice_unit': 15000,  # 冰块单位运输成本（美元/吨）
                'compress_unit': 8000,  # 压缩水单位运输成本（美元/吨）
                'equip_cost': 5000000   # 压缩设备固定成本（美元）
            },
            # 运输能力参数
            'transport_capacity': {
                'se_water': 200,  # 太空电梯水资源专项运力（吨/年）
                'r_water': 100    # 火箭水资源运力（吨/年）
            },
            # 密度参数
            'density': {
                'water': 1.0,     # 液态水密度（吨/立方米）
                'ice': 0.92,      # 冰密度（吨/立方米）
                'compressed': 1.2  # 压缩水密度（吨/立方米）
            },
            # 损耗率
            'loss_rate': {
                'ice': 0.05,      # 冰块运输损耗率（5%）
                'compressed': 0.02  # 压缩水运输损耗率（2%）
            }
        }
    
    def water_balance(self):
        """水量平衡计算"""
        W_drink = self.params['water_demands']['drink']
        W_prod = self.params['water_demands']['prod']
        W_eco = self.params['water_demands']['eco']
        
        # 再生水量
        W_recycle = (W_drink * self.params['recycle_rate']['drink'] +
                     W_prod * self.params['recycle_rate']['prod'] +
                     W_eco * self.params['recycle_rate']['eco'])
        
        # 需从地球运输的新鲜水量
        W_raw = (W_drink + W_prod + W_eco) - W_recycle
        
        return W_raw, W_drink, W_prod, W_eco, W_recycle
    
    def calculate_ice_strategy(self):
        """计算冰块运输策略"""
        W_raw, W_drink, W_prod, W_eco, W_recycle = self.water_balance()
        
        # 冰块运输：仅用于生活饮用水
        W_ice = W_drink
        # 压缩水运输：用于生产和生态用水
        W_compress = W_prod + W_eco
        
        # 考虑运输损耗
        W_ice_sent = W_ice / (1 - self.params['loss_rate']['ice'])
        W_compress_sent = W_compress / (1 - self.params['loss_rate']['compressed'])
        
        # 运输成本
        C_ice = W_ice_sent * self.params['transport_costs']['ice_unit']
        C_compress = W_compress_sent * self.params['transport_costs']['compress_unit']
        C_equip = self.params['transport_costs']['equip_cost']
        C_total = C_ice + C_compress + C_equip
        
        # 运输时间
        W_annual = W_ice_sent + W_compress_sent
        T_water = W_annual / self.params['transport_capacity']['se_water']
        
        # 体积计算
        vol_ice = W_ice_sent / self.params['density']['ice']
        vol_compress = W_compress_sent / self.params['density']['compressed']
        vol_total = vol_ice + vol_compress
        
        return {
            'strategy': 'Ice + Compressed Water',
            'W_raw': W_raw,
            'W_ice': W_ice,
            'W_compress': W_compress,
            'W_ice_sent': W_ice_sent,
            'W_compress_sent': W_compress_sent,
            'C_ice': C_ice,
            'C_compress': C_compress,
            'C_equip': C_equip,
            'C_total': C_total,
            'T_water': T_water,
            'vol_ice': vol_ice,
            'vol_compress': vol_compress,
            'vol_total': vol_total,
            'recycle_rate': (W_recycle / (W_drink + W_prod + W_eco)) * 100
        }
    
    def calculate_baseline_strategy(self):
        """计算基准策略（全部液态水运输）"""
        W_raw, W_drink, W_prod, W_eco, W_recycle = self.water_balance()
        
        # 全部液态水运输
        W_total = W_raw
        
        # 运输成本（假设液态水单位运输成本为10000美元/吨）
        C_total = W_total * 10000
        
        # 运输时间
        T_water = W_total / self.params['transport_capacity']['se_water']
        
        # 体积计算
        vol_total = W_total / self.params['density']['water']
        
        return {
            'strategy': 'Baseline (Liquid Water)',
            'W_raw': W_raw,
            'C_total': C_total,
            'T_water': T_water,
            'vol_total': vol_total,
            'recycle_rate': (W_recycle / (W_drink + W_prod + W_eco)) * 100
        }
    
    def sensitivity_analysis(self):
        """敏感性分析"""
        # 分析不同循环利用率对结果的影响
        recycle_rates = np.linspace(0.1, 0.9, 9)
        results = []
        
        for rate in recycle_rates:
            # 临时修改循环利用率
            original_rates = self.params['recycle_rate'].copy()
            self.params['recycle_rate'] = {
                'drink': rate * 0.5,  # 生活饮用水回收率较低
                'prod': rate * 0.8,   # 生产用水回收率中等
                'eco': rate * 0.9     # 生态用水回收率较高
            }
            
            # 计算冰块策略
            ice_strategy = self.calculate_ice_strategy()
            
            # 恢复原始参数
            self.params['recycle_rate'] = original_rates
            
            results.append({
                'recycle_rate': rate,
                'W_raw': ice_strategy['W_raw'],
                'C_total': ice_strategy['C_total'],
                'T_water': ice_strategy['T_water'],
                'vol_total': ice_strategy['vol_total']
            })
        
        return pd.DataFrame(results)
    
    def plot_water_strategy(self):
        """绘制水资源策略对比图"""
        # 计算两种策略
        ice_strategy = self.calculate_ice_strategy()
        baseline_strategy = self.calculate_baseline_strategy()
        
        # 策略对比数据
        strategies = ['Baseline', 'Ice + Compressed']
        costs = [baseline_strategy['C_total']/1e6, ice_strategy['C_total']/1e6]
        times = [baseline_strategy['T_water'], ice_strategy['T_water']]
        volumes = [baseline_strategy['vol_total'], ice_strategy['vol_total']]
        
        # 成本对比图
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        bars = plt.bar(strategies, costs, color=['blue', 'green'])
        plt.title('Total Cost Comparison')
        plt.ylabel('Cost (Million USD)')
        plt.grid(True, alpha=0.3)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}',
                     ha='center', va='bottom')
        
        # 时间对比图
        plt.subplot(2, 2, 2)
        bars = plt.bar(strategies, times, color=['blue', 'green'])
        plt.title('Transport Time Comparison')
        plt.ylabel('Time (Years)')
        plt.grid(True, alpha=0.3)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}',
                     ha='center', va='bottom')
        
        # 体积对比图
        plt.subplot(2, 2, 3)
        bars = plt.bar(strategies, volumes, color=['blue', 'green'])
        plt.title('Transport Volume Comparison')
        plt.ylabel('Volume (Cubic Meters)')
        plt.grid(True, alpha=0.3)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}',
                     ha='center', va='bottom')
        
        # 水资源分配饼图
        plt.subplot(2, 2, 4)
        labels = ['Fresh Water', 'Recycled Water']
        sizes = [ice_strategy['W_raw'], 
                 (ice_strategy['W_raw'] / (1 - ice_strategy['recycle_rate']/100)) - ice_strategy['W_raw']]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('Water Source Distribution')
        plt.axis('equal')
        
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, 'Q3_Water_Strategy_Comparison.png'))
        plt.show()
        
        # 冰块策略详细分析
        plt.figure(figsize=(10, 6))
        categories = ['Ice Transport', 'Compressed Transport', 'Equipment']
        values = [ice_strategy['C_ice']/1e6, ice_strategy['C_compress']/1e6, ice_strategy['C_equip']/1e6]
        bars = plt.bar(categories, values, color=['cyan', 'lightgreen', 'orange'])
        plt.title('Ice + Compressed Strategy Cost Breakdown')
        plt.ylabel('Cost (Million USD)')
        plt.grid(True, alpha=0.3)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}',
                     ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, 'Q3_Water_Ice_Strategy_Breakdown.png'))
        plt.show()
    
    def plot_sensitivity(self, sensitivity_df):
        """绘制敏感性分析结果"""
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.plot(sensitivity_df['recycle_rate'], sensitivity_df['W_raw'], 'o-', color='blue')
        plt.title('Water Demand vs Recycle Rate')
        plt.xlabel('Recycle Rate')
        plt.ylabel('Fresh Water Demand (Tons/Year)')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 2, 2)
        plt.plot(sensitivity_df['recycle_rate'], sensitivity_df['C_total']/1e6, 'o-', color='green')
        plt.title('Total Cost vs Recycle Rate')
        plt.xlabel('Recycle Rate')
        plt.ylabel('Cost (Million USD)')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 2, 3)
        plt.plot(sensitivity_df['recycle_rate'], sensitivity_df['T_water'], 'o-', color='orange')
        plt.title('Transport Time vs Recycle Rate')
        plt.xlabel('Recycle Rate')
        plt.ylabel('Time (Years)')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 2, 4)
        plt.plot(sensitivity_df['recycle_rate'], sensitivity_df['vol_total'], 'o-', color='purple')
        plt.title('Transport Volume vs Recycle Rate')
        plt.xlabel('Recycle Rate')
        plt.ylabel('Volume (Cubic Meters)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(result_dir, 'Q3_Water_Sensitivity.png'))
        plt.show()
    
    def save_results(self, ice_strategy, baseline_strategy, sensitivity_df):
        """保存结果"""
        # 策略对比结果
        strategy_results = pd.DataFrame([
            {
                'Strategy': 'Baseline',
                'Fresh_Water_Demand': baseline_strategy['W_raw'],
                'Total_Cost': baseline_strategy['C_total'],
                'Transport_Time': baseline_strategy['T_water'],
                'Transport_Volume': baseline_strategy['vol_total'],
                'Recycle_Rate': baseline_strategy['recycle_rate']
            },
            {
                'Strategy': 'Ice + Compressed',
                'Fresh_Water_Demand': ice_strategy['W_raw'],
                'Total_Cost': ice_strategy['C_total'],
                'Transport_Time': ice_strategy['T_water'],
                'Transport_Volume': ice_strategy['vol_total'],
                'Recycle_Rate': ice_strategy['recycle_rate']
            }
        ])
        
        strategy_results.to_csv(os.path.join(result_dir, 'Q3_Water_Strategy_Results.csv'), index=False)
        sensitivity_df.to_csv(os.path.join(result_dir, 'Q3_Water_Sensitivity.csv'), index=False)
        
        print("Results saved successfully!")
    
    def generate_report(self):
        """生成水资源策略报告"""
        ice_strategy = self.calculate_ice_strategy()
        baseline_strategy = self.calculate_baseline_strategy()
        
        print("=== 水资源供应与运输优化报告 ===")
        print("\n1. 基准策略（液态水运输）")
        print(f"   - 新鲜水需求量: {baseline_strategy['W_raw']:.2f} 吨/年")
        print(f"   - 总运输成本: ${baseline_strategy['C_total']:.2f}")
        print(f"   - 运输时间: {baseline_strategy['T_water']:.2f} 年")
        print(f"   - 运输体积: {baseline_strategy['vol_total']:.2f} 立方米")
        
        print("\n2. 冰块+压缩水策略")
        print(f"   - 新鲜水需求量: {ice_strategy['W_raw']:.2f} 吨/年")
        print(f"   - 总运输成本: ${ice_strategy['C_total']:.2f}")
        print(f"   - 运输时间: {ice_strategy['T_water']:.2f} 年")
        print(f"   - 运输体积: {ice_strategy['vol_total']:.2f} 立方米")
        print(f"   - 成本构成: 冰块运输 ${ice_strategy['C_ice']:.2f}, 压缩水运输 ${ice_strategy['C_compress']:.2f}, 设备 ${ice_strategy['C_equip']:.2f}")
        
        print("\n3. 策略对比")
        cost_diff = (ice_strategy['C_total'] - baseline_strategy['C_total']) / baseline_strategy['C_total'] * 100
        time_diff = (ice_strategy['T_water'] - baseline_strategy['T_water']) / baseline_strategy['T_water'] * 100
        vol_diff = (ice_strategy['vol_total'] - baseline_strategy['vol_total']) / baseline_strategy['vol_total'] * 100
        
        print(f"   - 成本变化: {cost_diff:.2f}%")
        print(f"   - 时间变化: {time_diff:.2f}%")
        print(f"   - 体积变化: {vol_diff:.2f}%")
        
        print("\n4. 优势分析")
        print("   - 冰块运输: 损耗率低，适合生活饮用水，可利用低温环境")
        print("   - 压缩水运输: 密度高，运输效率高，适合生产和生态用水")
        print("   - 分质供水: 根据不同用水需求选择合适的运输方式，降低总成本")
        
        print("\n5. 建议")
        print("   - 优先采用冰块+压缩水策略，特别是对于大规模月球殖民地")
        print("   - 提高水资源循环利用率，减少新鲜水运输需求")
        print("   - 开发月球本地水资源（如冰矿开采），进一步降低地球运输依赖")

if __name__ == "__main__":
    print("Running 2026 MCM Problem B: Question 3 - Water Supply Optimization")
    print("="*60)
    
    # 初始化优化器
    optimizer = WaterSupplyOptimizer()
    
    # 计算策略
    ice_strategy = optimizer.calculate_ice_strategy()
    baseline_strategy = optimizer.calculate_baseline_strategy()
    
    # 敏感性分析
    sensitivity_df = optimizer.sensitivity_analysis()
    
    # 绘制结果
    print("Generating water strategy plots...")
    optimizer.plot_water_strategy()
    optimizer.plot_sensitivity(sensitivity_df)
    
    # 保存结果
    optimizer.save_results(ice_strategy, baseline_strategy, sensitivity_df)
    
    # 生成报告
    optimizer.generate_report()
    
    print("="*60)
    print("Question 3 water supply optimization completed successfully!")
    print(f"Results saved in {result_dir}")