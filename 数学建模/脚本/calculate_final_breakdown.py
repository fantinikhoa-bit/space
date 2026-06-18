
import numpy as np
import pandas as pd

# 参数配置 (与 NSGA-II 保持一致)
class Config:
    M_total = 1.0e11
    # 阶段定义
    STAGES = {
        'Camp': {'mass': 0.10 * M_total, 'alpha': 0.3290},
        'Base': {'mass': 0.40 * M_total, 'alpha': 0.6577},
        'City': {'mass': 0.50 * M_total, 'alpha': 0.8905}
    }
    
    # 基础参数
    Q_se = 5.37e8  # SE年运力
    Q_r_launch = 1.5e5 # 火箭单次运力
    T_r_cycle = 0.5    # 发射周期(天)
    Num_Launch_Sites = 10 
    
    # 成本参数
    C_se_unit = 525.0
    C_r_unit = 1012.5
    C_r_site = 1.0e10
    C_se_fixed_project = 4.5e10
    
    # 环境参数 (kg CO2)
    # 修正环境参数单位为 "kg" 以便计算，最后转 Million Tons
    E_site_const = 5.0e7
    E_trans_se_CO2 = 0.1 
    E_trans_r_CO2 = 3.62 
    E_strat_factor = 2.0 

def calc_detailed_metrics():
    print("--- 最终推荐方案详细指标计算 ---")
    
    total_time_sum = 0
    total_cost_sum = 0
    total_env_sum = 0
    
    # 固定成本/排放 (一次性)
    fixed_cost_sites = 10 * Config.C_r_site
    fixed_cost_se = Config.C_se_fixed_project
    fixed_env_sites = 10 * Config.E_site_const
    
    # 将固定部分平摊到总计中，不分摊到阶段(避免歧义)
    total_cost_sum += (fixed_cost_sites + fixed_cost_se)
    total_env_sum += fixed_env_sites
    
    results = []
    
    for name, params in Config.STAGES.items():
        mass = params['mass']
        alpha = params['alpha']
        
        # 1. 质量分配
        m_se = mass * alpha
        m_rocket = mass * (1 - alpha)
        
        # 2. 时间计算 (并行)
        t_se = m_se / Config.Q_se
        
        # 火箭年运力: 10个基地 * (365/0.5)次 * 1.5e5 kg
        q_rocket_annual = 10 * (365.0 / 0.5) * 1.5e5
        t_rocket = m_rocket / q_rocket_annual
        
        # 阶段时间取决于较慢者
        t_stage = max(t_se, t_rocket)
        
        # 3. 变量成本
        c_var = (m_se * Config.C_se_unit) + (m_rocket * Config.C_r_unit)
        
        # 4. 变量排放
        e_se = m_se * Config.E_trans_se_CO2
        e_se = m_se * 0.1 # 直接用值避免嵌套错误
        
        # 火箭排放: 质量 * 3.62 * 2.0 (平流层因子)
        e_rocket = m_rocket * 3.62 * 2.0
        
        e_stage = e_se + e_rocket
        
        # 汇总
        total_time_sum += t_stage
        total_cost_sum += c_var
        total_env_sum += e_stage
        
        results.append({
            'Stage': name,
            'Alpha': alpha,
            'Mass_Total (Mt)': mass / 1e9,
            'Mass_SE (Mt)': m_se / 1e9,
            'Mass_Rocket (Mt)': m_rocket / 1e9,
            'Time (Years)': t_stage,
            'Cost_Var ($T)': c_var / 1e12,
            'Emissions (Mt CO2)': e_stage / 1e9
        })
        
    print(f"\n{'阶段':<10} | {'Alpha':<6} | {'时间(年)':<10} | {'成本($T)':<10} | {'排放(Mt)':<10}")
    print("-" * 60)
    for r in results:
        print(f"{r['Stage']:<10} | {r['Alpha']:<6.2f} | {r['Time (Years)']:<10.2f} | {r['Cost_Var ($T)']:<10.2f} | {r['Emissions (Mt CO2)']:<10.2f}")
        
    print("-" * 60)
    print(f"{'总计 (含固定)':<10} | {'-':<6} | {total_time_sum:<10.2f} | {total_cost_sum/1e12:<10.2f} | {total_env_sum/1e9:<10.2f}")
    
    # 导出 CSV
    pd.DataFrame(results).to_csv('MCM_Models/Final_Optimal_Breakdown.csv', index=False)
    print("\n结果已保存至 MCM_Models/Final_Optimal_Breakdown.csv")

if __name__ == "__main__":
    calc_detailed_metrics()
