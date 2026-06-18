import os
import subprocess
import time

# 脚本路径
scripts = [
    "Q1_DualObjective_TOPSIS.py",
    "Q2_Sensitivity_LHS.py",
    "Q3_Water_Strategy.py",
    "Q4_LCA_NSGA2.py"
]

# 运行每个脚本
for script in scripts:
    print(f"\n=== 运行 {script} ===")
    try:
        result = subprocess.run(
            ["python", script],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            check=True
        )
        print("运行成功!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"运行失败: {e}")
        print(e.stdout)
        print(e.stderr)
    except Exception as e:
        print(f"发生错误: {e}")
    time.sleep(2)  # 等待2秒，确保脚本完全运行完毕

print("\n=== 所有脚本运行完成 ===")