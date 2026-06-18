
import numpy as np
from scipy.optimize import curve_fit

# Data with 329 (Assuming maybe user gave this earlier?)
years = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025])
launches = np.array([74, 84, 78, 81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223, 329])

# 1. Exponential
def exponential_model(t, a, b):
    return a * np.exp(b * (t - 2010))

try:
    popt_exp, _ = curve_fit(exponential_model, years, launches, p0=[70, 0.1])
    val_2050_exp = exponential_model(2050, *popt_exp)
    print(f"Exponential with 329: {val_2050_exp:.2f}")
except:
    pass

# 2. Logistic Auto K (Wide bounds)
def logistic_model(t, K, A, r):
    t_norm = t - 2010
    return K / (1 + A * np.exp(-r * t_norm))

try:
    bounds = ([300, 0, 0], [100000, 1000, 2.0])
    popt, _ = curve_fit(logistic_model, years, launches, bounds=bounds, maxfev=10000)
    val_2050 = logistic_model(2050, *popt)
    # Also 2045, 2040 in case user remembers those?
    print(f"Logistic (Auto K, Wide Bounds) with 329: {val_2050:.2f}")
    print(f"Parameters: K={popt[0]:.2f}")
except:
    pass
