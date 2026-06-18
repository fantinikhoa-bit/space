import numpy as np
from scipy.integrate import odeint
import random
import matplotlib.pyplot as plt
import matplotlib

font={
    'family':'Microsoft YaHei',
    'weight':'bold',
}
matplotlib.rc("font",**font)#修改字体为中文，此处为模板，后续操作可以复制粘贴


# 基础参数设置
N = 10  # 种群内个体数目
N_chrom = 2  # 染色体节点数（变量个数）
iter = 10  # 迭代次数
mut = 0.1  # 突变概率，一般低于0.3
acr = 0.7  # 交叉概率，一般高于0.6
best = 1  # 一般不改
chrom_range = np.array([[0, 0], [100000, 1]])  # 每个节点的值的区间

chrom = np.zeros((N, N_chrom))  # 存放染色体的矩阵
fitness = np.zeros(N)  # 存放染色体的适应度
fitness_ave = np.zeros(iter)  # 存放每一代的平均适应度
fitness_best = np.zeros(iter)  # 存放每一代的最优适应度
chrom_best = np.zeros(N_chrom + 1)  # 存放当前代的最优染色体与适应度


def IfOut(c, range):  # 检查染色体是否越界
    if c < range[0] or c > range[1]:
        if abs(c - range[0]) < abs(c - range[1]):
            c_new = range[0]
        else:
            c_new = range[1]
    else:
        c_new = c
    return c_new

def MutChrom(chrom, mut, N, N_chrom, chrom_range, t, iter):
    for i in range(N):
        for j in range(N_chrom):
            mut_rand = random.random()  # 随机生成一个数，代表自然里的基因突变，然后用改值来决定是否产生突变。
            if mut_rand <= mut:  # mut代表突变概率，即产生突变的阈值，如果小于0.2的基因突变概率阈值才进行基因突变处理，否者不进行突变处理
                mut_pm = random.random()  # 增加还是减少
                mut_num = random.random() * (1 - t / iter) ** 2
                if mut_pm <= 0.5:
                    chrom[i, j] = chrom[i, j] * (1 - mut_num)
                else:
                    chrom[i, j] = chrom[i, j] * (1 + mut_num)
                chrom[i, j] = IfOut(chrom[i, j], chrom_range[:, j])  # 检验是否越界
    return chrom

# 初始化第一代并计算其适应度函数
def Initialize(N, N_chrom, chrom_range):
    chrom_new = np.zeros((N, N_chrom))
    for i in range(N_chrom):
        chrom_new[:, 0] = np.random.randint(chrom_range[0, 0], chrom_range[1, 0], N)
        chrom_new[:, 1] = chrom_range[0, 1] + (chrom_range[1, 1] - chrom_range[0, 1]) * np.random.rand(N)
    return chrom_new

def CalFitness(chrom, N, N_chrom):
    fitness = np.zeros(N)
    y0 = [0, 0, 0, 0]
    for i in range(N):
        T, Y = NewODE45(f_NewODE45, 0, 300, 10000, y0, chrom[i, 0], chrom[i,1])
        p = (np.abs(np.array(Y)[:, 1] - np.array(Y)[:, 3])) ** (2 + chrom[i, 1])
        pp = np.sum(p[6668:10001])
        fitness[i] = chrom[i, 0] * pp / (10001 - 6668)
    return fitness

def f_NewODE45(t, y, k, A):
    dy = np.zeros(4)
    dy[0] = y[1]
    dy[1] = (4890 * np.cos(2.2143 * t) - 1025 * 9.8 * np.pi * y[0] - 167.8395 * y[1] - 80000 * (y[0] - y[2]) - k * (
                (y[1] - y[3]) * np.abs(y[1] - y[3]) ** A)) / 6031.992
    dy[2] = y[3]
    dy[3] = (80000 * (y[0] - y[2]) + k * ((y[1] - y[3]) * np.abs(y[1] - y[3]) ** A)) / 2433
    return dy

def NewODE45(f, a, b, N, y0, k, A):
    h = (b - a) / N
    x = a
    y = y0
    x_vals = [x]
    y_vals = [y]

    for i in range(N):
        k1 = f(x, y, k, A)
        k2 = f(x + h / 2, y + k1 * h / 2, k, A)
        k3 = f(x + h / 2, y + k2 * h / 2, k, A)
        k4 = f(x + h, y + k3 * h, k, A)
        y_next = y + (k1 + 2 * k2 + 2 * k3 + k4) * h / 6

        x = x + h
        y = y_next
        x_vals.append(x)
        y_vals.append(y)

    return x_vals, y_vals

# 交叉处理
def AcrChrom(chrom, acr, N, N_chrom):
    for i in range(N):
        acr_rand = random.random()  # 生成一个代表该个体是否产生交叉的概率大小，用于判别是否进行交叉处理
        if acr_rand < acr:  # 如果该个体的交叉概率值大于产生交叉处理的阈值，则对该个体的染色体（两条，因为此案例中有两个自变量）进行交叉处理
            acr_chrom = random.randint(0, N - 1)  # 要交叉的染色体
            acr_node = random.randint(0, N_chrom - 1)  # 要交叉的节点
            # 交叉开始
            temp = chrom[i, acr_node]
            chrom[i, acr_node] = chrom[acr_chrom, acr_node]
            chrom[acr_chrom, acr_node] = temp
    return chrom

# 平均适应度计算
def CalAveFitness(fitness):
    N = len(fitness)
    fitness_ave = sum(fitness) / N
    return fitness_ave

# 寻找最优染色体
def FindBest(chrom, fitness, N_chrom):
    maxNum = max(fitness)
    maxCorr = np.argmax(fitness)
    chrom_best = np.zeros(N_chrom + 1)
    chrom_best[0:N_chrom] = chrom[maxCorr, :]
    chrom_best[-1] = maxNum
    return chrom_best

# 替换最差个体
def ReplaceWorse(chrom, chrom_best, fitness):
    max_num = max(fitness)
    min_num = min(fitness)
    limit = (max_num - min_num) * 0.2 + min_num

    replace_corr = fitness < limit
    replace_num = np.sum(replace_corr)
    chrom[replace_corr, :] = np.ones((replace_num, 1)) * chrom_best[0:N_chrom]
    fitness[replace_corr] = np.ones(replace_num) * chrom_best[-1]
    return chrom, fitness

# 初始化第一代
chrom = Initialize(N, N_chrom, chrom_range)
fitness = CalFitness(chrom, N, N_chrom)
chrom_best = FindBest(chrom, fitness, N_chrom)
fitness_best[0] = chrom_best[-1]
fitness_ave[0] = CalAveFitness(fitness)

# 生成以下各代，迭代次数为最高迭代次数
for t in range(1, iter):
    chrom = MutChrom(chrom, mut, N, N_chrom, chrom_range, t, iter)
    chrom = AcrChrom(chrom, acr, N, N_chrom)
    fitness = CalFitness(chrom, N, N_chrom)
    chrom_best_temp = FindBest(chrom, fitness, N_chrom)
    if chrom_best_temp[-1] > chrom_best[-1]:
        chrom_best = chrom_best_temp
    chrom, fitness = ReplaceWorse(chrom, chrom_best, fitness)
    fitness_best[t] = chrom_best[-1]
    fitness_ave[t] = CalAveFitness(fitness)

# 绘图
plt.figure(1)
plt.plot(range(1, iter+1), fitness_ave, 'r', range(1, iter+1), fitness_best, 'b')
plt.grid(True)
plt.legend(['平均适应度', '最优适应度'])
plt.show()

# 输出结果
print('最优染色体为', chrom_best[0:N_chrom])
print('最优适应度为', chrom_best[-1])
