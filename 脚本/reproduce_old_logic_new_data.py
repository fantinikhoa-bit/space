
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Data with 2025 = 329
years = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025])
launches = np.array([74, 84, 78, 81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223, 329])

# Fixed Carrying Capacity from the old file
K_fixed = 2000

def logistic_model_fixed_K(t, A, r):
    t_norm = t - 2010
    return K_fixed / (1 + A * np.exp(-r * t_norm))

p0 = [20, 0.15]
bounds = ([0, 0], [1000, 2.0])

try:
    popt, _ = curve_fit(logistic_model_fixed_K, years, launches, p0=p0, bounds=bounds, maxfev=10000)
    A_fit, r_fit = popt
    val_2050 = logistic_model_fixed_K(2050, A_fit, r_fit)
    print(f"--- Prediction with Old Logic (K=2000) and New Data (329) ---")
    print(f"Prediction for 2050: {val_2050:.2f}")
    print(f"Growth Rate (r): {r_fit:.4f}")
    print(f"A: {A_fit:.4f}")
except Exception as e:
    print(f"Failed: {e}")
