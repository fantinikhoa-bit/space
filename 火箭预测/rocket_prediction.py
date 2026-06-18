import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Data Preparation
# Global history + User 2025 data (329)
years = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025])
launches = np.array([74, 84, 78, 81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223, 329])

# Fixed Carrying Capacity as requested
K_fixed = 36500

# Define the Logistic Growth Model with fixed K
# P(t) = K_fixed / (1 + A * exp(-r * (t - t0)))
def logistic_model_fixed_K(t, A, r):
    t_norm = t - 2010
    return K_fixed / (1 + A * np.exp(-r * t_norm))

# Initial Guesses
# A: Determines starting point
# r: Growth rate
p0 = [20, 0.15]

# Bounds
# A > 0, r > 0
bounds = ([0, 0], [10000, 2.0])

try:
    popt, pcov = curve_fit(logistic_model_fixed_K, years, launches, p0=p0, bounds=bounds, maxfev=10000)
    A_fit, r_fit = popt
except Exception as e:
    print(f"Fitting failed: {e}")
    A_fit, r_fit = 0, 0

# Predictions
if A_fit > 0:
    future_years = np.arange(2010, 2051)
    predicted_launches = logistic_model_fixed_K(future_years, A_fit, r_fit)
    
    val_2050 = logistic_model_fixed_K(2050, A_fit, r_fit)
    
    print(f"Model Parameters:")
    print(f"Carrying Capacity (K): {K_fixed} (Fixed)")
    print(f"Growth Rate (r): {r_fit:.4f}")
    print(f"Parameter A: {A_fit:.4f}")
    print(f"Prediction for 2050: {val_2050:.2f}")

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.scatter(years, launches, color='red', label='Global History (2010-2025)')
    plt.plot(future_years, predicted_launches, color='blue', label=f'Logistic Fit (K={K_fixed})')
    
    plt.title(f'Logistic Prediction with K={K_fixed} (2050 Prediction: {val_2050:.0f})')
    plt.xlabel('Year')
    plt.ylabel('Annual Launches')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.savefig('rocket_launch_prediction_K20000.png')
    print("Plot saved to rocket_launch_prediction_K20000.png")
else:
    print("Could not fit the model.")
