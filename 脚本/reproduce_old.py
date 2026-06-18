
import numpy as np
from scipy.optimize import curve_fit

# Data from Jan 30 (2025 = 165)
years = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025])
launches = np.array([74, 84, 78, 81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223, 165]) # Note 165 here

# Logistic Model
def logistic_model(t, K, A, r):
    t_norm = t - 2010
    return K / (1 + A * np.exp(-r * t_norm))

# Bounds
bounds = ([0, 0, 0], [10000, 1000, 2.0])
p0 = [500, 20, 0.15]

try:
    popt, _ = curve_fit(logistic_model, years, launches, p0=p0, bounds=bounds, maxfev=10000)
    K_fit, A_fit, r_fit = popt
    val_2050 = logistic_model(2050, *popt)
    print(f"Prediction for 2050 (with 2025=165): {val_2050:.2f}")
    print(f"Parameters: K={K_fit:.2f}, r={r_fit:.4f}")
except Exception as e:
    print(f"Fitting failed: {e}")
