
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

result_dir = r'd:\Users\HONOR\Desktop\base\2026\Results'
os.makedirs(result_dir, exist_ok=True)

def plot_3d_tube_schematic():
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. 生成平滑的主轨迹曲线 (Pareto Trajectory)
    t = np.linspace(0, 1, 100)
    # x: Cost (Incr), y: Time (Decr), z: Env (Decr)
    x = 10 + 40 * t
    y = 20 - 15 * np.power(t, 0.6) # Non-linear
    z = 50 - 40 * np.power(t, 1.2)
    
    # 2. 绘制"管道" (Feasible Region Tube)
    # 我们围绕主曲线生成一些散点云，形成一个"管道"感
    theta = np.linspace(0, 2*np.pi, 20)
    w_t, w_theta = np.meshgrid(t, theta)
    
    # 半径随位置变化，中间胖两头瘦
    r = 2.0 * np.sin(np.pi * w_t) + 1.0
    
    # 管道坐标
    # 简化的管道生成：直接在主轨迹周围加正态分布云
    # 用 wireframe 模拟更像示意图
    # 这里我们用半透明散点云+线框来模拟那个"绿通"
    
    # 3. 绘制主曲线 (红色连线 + 星号)
    ax.plot(x, y, z, color='red', linewidth=3, label='Optimized Trajectory')
    ax.scatter(x[::5], y[::5], z[::5], color='red', s=100, marker='*', depthshade=False)

    # 4. 绘制"可行域云" (Feasible Cloud) - 灰色/绿色半透明
    # 在主轨迹"上方" (更高Cost/Time/Env) 生成点
    n_cloud = 2000
    cloud_t = np.random.uniform(0, 1, n_cloud)
    cloud_x = 10 + 40 * cloud_t + np.random.exponential(5, n_cloud)
    cloud_y = 20 - 15 * np.power(cloud_t, 0.6) + np.random.exponential(2, n_cloud) 
    cloud_z = 50 - 40 * np.power(cloud_t, 1.2) + np.random.exponential(5, n_cloud)
    
    # 只保留靠近轨迹的，形成"Tube"感
    dist = np.sqrt((cloud_x - np.interp(cloud_t, t, x))**2 + 
                   (cloud_y - np.interp(cloud_t, t, y))**2 + 
                   (cloud_z - np.interp(cloud_t, t, z))**2)
    mask = dist < 12 # 半径阈值
    
    ax.scatter(cloud_x[mask], cloud_y[mask], cloud_z[mask], 
               c='lightgreen', alpha=0.1, s=20, marker='o', label='Feasible Region')
    
    # 5. 绘制投影虚线框 (Schematic Box)
    # 画出从曲线到墙壁的投影线，增强立体感
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    zlim = ax.get_zlim()
    
    bottom_z = zlim[0]
    back_y = ylim[1]
    left_x = xlim[0] # 或根据视角调整
    
    # 取几个关键点画虚线
    key_indices = [10, 30, 50, 70, 90]
    for i in key_indices:
        cx, cy, cz = x[i], y[i], z[i]
        # Drop lines to floor (Z-min)
        ax.plot([cx, cx], [cy, cy], [cz, bottom_z], 'k--', alpha=0.3, linewidth=1)
        # Drop lines to back wall (Y-max)
        ax.plot([cx, cx], [cy, back_y], [cz, cz], 'k--', alpha=0.3, linewidth=1)
        # Drop lines to side wall (X-min)
        ax.plot([cx, left_x], [cy, cy], [cz, cz], 'k--', alpha=0.3, linewidth=1)

    # 装饰
    ax.set_xlabel('Cost', fontsize=12)
    ax.set_ylabel('Time', fontsize=12)
    ax.set_zlabel('Environment', fontsize=12)
    ax.set_title('3D Trajectory Schematic (Figure 3 Style)', fontsize=15)
    
    # 调整视角
    ax.view_init(elev=20, azim=-45)
    
    save_path = os.path.join(result_dir, 'Q4_LCA_3D_Schematic_Tube.png')
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")

if __name__ == "__main__":
    plot_3d_tube_schematic()
