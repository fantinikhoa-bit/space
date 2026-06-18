
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Data 2010-2025 (329)
years = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025])
launches = np.array([74, 84, 78, 81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223, 329])

# Logistic Model: P(t) = K / (1 + A * exp(-r * (t - t0)))
def logistic_model(t, K, A, r):
    t_norm = t - 2010
    return K / (1 + A * np.exp(-r * t_norm))

# We let the optimizer find the BEST K without arbitrary limits (just physical > max_launches)
# Bounds: K must be at least 330, but can go very high. r usually 0..1.
bounds = ([330, 0, 0], [100000, 5000, 1.0])
p0 = [5000, 50, 0.15]

try:
    popt, pcov = curve_fit(logistic_model, years, launches, p0=p0, bounds=bounds, maxfev=20000)
    K_best, A_best, r_best = popt
    
    # Predict 2050
    val_2050 = logistic_model(2050, *popt)
    
    # Calculate Inflection Point (Time when launches = K/2)
    # K/2 = K / (1 + A * exp(-r * t_norm)) => 2 = 1 + A*... => 1 = A*exp(...) => ln(1/A) = -r*t_norm
    # t_norm = ln(A) / r
    t_inflection_norm = np.log(A_best) / r_best
    t_inflection_year = 2010 + t_inflection_norm
    
    print(f"--- Best Fit 'Logical' (Logistic) Prediction ---")
    print(f"Prediction for 2050: {val_2050:.2f}")
    print(f"Optimal Carrying Capacity (K): {K_best:.2f}")
    print(f"Inflection Point Year: {t_inflection_year:.1f}")
    print(f"Explanation: The data suggests we are still early in the curve, reaching {K_best/2:.0f} launches around {t_inflection_year:.0f}.")
    
    # Plot
    future_years = np.arange(2010, 2051)
    pred_curve = logistic_model(future_years, *popt)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(years, launches, color='red', label='Data (2025=329)')
    plt.plot(future_years, pred_curve, color='blue', label=f'Best Logistic Fit (K={K_best:.0f})')
    plt.axvline(x=t_inflection_year, color='green', linestyle=':', label=f'Inflection {t_inflection_year:.0f}')
    plt.axvline(x=2050, color='gray', linestyle='--')
    plt.title(f'Most "Logical" Prediction utilizing Data Trends\n2050 Forecast: {val_2050:.0f} Launches')
    plt.xlabel('Year')
    plt.ylabel('Launches')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('rocket_prediction_logical_best.png')
    
except Exception as e:
    print(f"Optimization failed: {e}")
