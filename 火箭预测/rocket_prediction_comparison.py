
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Data
years = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025])
launches = np.array([74, 84, 78, 81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223, 329])
future_years = np.arange(2010, 2051)

# 1. Exponential Model: y = a * exp(b * (t - t0))
def exponential_model(t, a, b):
    return a * np.exp(b * (t - 2010))

popt_exp, _ = curve_fit(exponential_model, years, launches, p0=[70, 0.1])
pred_exp = exponential_model(future_years, *popt_exp)
val_2050_exp = exponential_model(2050, *popt_exp)

# 2. Quadratic Model (Polynomial): y = a*t^2 + b*t + c
z = np.polyfit(years - 2010, launches, 2)
p = np.poly1d(z)
pred_poly = p(future_years - 2010)
val_2050_poly = p(2050 - 2010)

# 3. Grey System Model GM(1,1)
def gm11(x, predict_len):
    n = len(x)
    x1 = np.cumsum(x)
    z1 = (x1[:n-1] + x1[1:]) / 2.0
    z1 = z1.reshape((n-1, 1))
    B = np.append(-z1, np.ones((n-1, 1)), axis=1)
    Y = x[1:].reshape((n-1, 1))
    
    # Estimate parameters [a, b]
    a, b = np.dot(np.dot(np.linalg.inv(np.dot(B.T, B)), B.T), Y)
    a = a[0]
    b = b[0]
    
    # Prediction function
    result = np.zeros(predict_len)
    result[0] = x[0]
    for i in range(1, predict_len):
        result[i] = (x[0] - b/a) * np.exp(-a * (i)) * (1 - np.exp(a))
        
    return result

# GM(1,1) prediction needs continuous time steps, so we fill missing 2024 with interpolation for the input
years_filled = np.arange(2010, 2026)
launches_filled = np.interp(years_filled, years, launches)

# Forecast up to 2050 (which is index 40 from 2010)
pred_gm = gm11(launches_filled, len(future_years))
val_2050_gm = pred_gm[-1]

# Print Results
print("--- Prediction Comparison for 2050 ---")
print(f"1. Exponential Model: {val_2050_exp:.2f}")
print(f"2. Quadratic Polynomial: {val_2050_poly:.2f}")
print(f"3. Grey Model GM(1,1): {val_2050_gm:.2f}")

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(years, launches, color='black', label='Historical Data', zorder=5)
plt.plot(future_years, pred_exp, label=f'Exponential (2050: {val_2050_exp:.0f})', linestyle='--')
plt.plot(future_years, pred_poly, label=f'Polynomial deg=2 (2050: {val_2050_poly:.0f})', linestyle='-.')
plt.plot(future_years, pred_gm, label=f'Grey Model GM(1,1) (2050: {val_2050_gm:.0f})', linestyle=':')

plt.title('Comparison of Rocket Launch Prediction Models')
plt.xlabel('Year')
plt.ylabel('Annual Launches')
plt.legend()
plt.grid(True, alpha=0.3)
plt.ylim(0, max(val_2050_exp, val_2050_poly, val_2050_gm) * 1.1)
plt.savefig('rocket_prediction_comparison.png')
print("Comparison plot saved to rocket_prediction_comparison.png")
