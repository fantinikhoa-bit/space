
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Historical Data 2010-2023 (Ignoring the 2025=165 outlier for a moment, or checking if it was used)
years_trend = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023])
launches_trend = np.array([74, 84, 78, 81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223])

# 1. Exponential Model on 2010-2023
def exponential_model(t, a, b):
    return a * np.exp(b * (t - 2010))

try:
    popt_exp, _ = curve_fit(exponential_model, years_trend, launches_trend, p0=[70, 0.1])
    val_2050_exp = exponential_model(2050, *popt_exp)
    print(f"Prediction using Exponential Model on 2010-2023 data: {val_2050_exp:.2f}")
except:
    pass

# 2. Logistic with High K (e.g. inferred from 2010-2023 trend)
def logistic_model(t, K, A, r):
    t_norm = t - 2010
    return K / (1 + A * np.exp(-r * t_norm))

try:
    # Bounds with high K allowed
    bounds = ([300, 0, 0], [50000, 1000, 2.0])
    popt_log, _ = curve_fit(logistic_model, years_trend, launches_trend, bounds=bounds)
    val_2050_log = logistic_model(2050, *popt_log)
    print(f"Prediction using Logistic Model (Auto K) on 2010-2023 data: {val_2050_log:.2f}")
    print(f"  Best fit K: {popt_log[0]:.2f}")
except:
    pass
