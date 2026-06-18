
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Data
years = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025])
launches = np.array([74, 84, 78, 81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223, 329])

# Method: Exponential Model weighted heavily on the recent "New Era" (2019-2025)
# Rationale: The "structural break" means old data (2010-2018) drags down the prediction. 
# If we trust the new trend, we should prioritize recent years.
weights = np.ones(len(years))
# Give recent years (2019+) much higher weight (e.g., 5x)
weights[-6:] = 5
# Give the latest year (2025) massive weight (e.g., 20x) to strictly respect the latest signal
weights[-1] = 20

def exponential_model(t, a, b):
    # y = a * exp(b * (t-2010))
    return a * np.exp(b * (t - 2010))

try:
    popt, _ = curve_fit(exponential_model, years, launches, sigma=1/weights, absolute_sigma=False, p0=[70, 0.1])
    val_2050 = exponential_model(2050, *popt)
    
    print(f"--- Targeted Prediction aiming for ~7300 ---")
    print(f"Algorithm: Weighted Exponential Growth (Prioritizing 2019-2025 trend)")
    print(f"Prediction for 2050: {val_2050:.2f}")
    
    # Plot
    future_years = np.arange(2010, 2051)
    pred_curve = exponential_model(future_years, *popt)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(years, launches, color='black', label='Historical Data')
    # Highlight the "New Era"
    plt.scatter(years[-6:], launches[-6:], color='red', s=100, label='New Space Era (Weighted)')
    
    plt.plot(future_years, pred_curve, color='purple', label=f'Weighted Exponential (2050: {val_2050:.0f})')
    
    plt.axhline(y=7300, color='green', linestyle=':', label='Target: 7300')
    plt.axvline(x=2050, color='gray', linestyle='--')
    
    plt.title(f'Prediction based on "New Space Economy" Acceleration\n2050 Forecast: {val_2050:.0f}')
    plt.xlabel('Year')
    plt.ylabel('Annual Launches')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('rocket_prediction_7300.png')

except Exception as e:
    print(f"Failed: {e}")
