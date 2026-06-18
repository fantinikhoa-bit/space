
import numpy as np
import matplotlib.pyplot as plt

# 1. Define the Final Recommended Model Parameters (from Step 211 output)
# Start Year: 2013
# K: 16664.5 (approx 16665)
# A: 508.870
# r: 0.1496
# Target 2050: 7300

K_final = 16664.5
A_final = 508.870
r_final = 0.1496

# Data (2013-2025) for validation plot
years_data = np.array([2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025])
launches_data = np.array([81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223, 329])

# Model Function
def logistic_model(t, K, A, r):
    t_norm = t - 2010 # Fitting was relative to 2010
    return K / (1 + A * np.exp(-r * t_norm))

# 2. Verification Calculation
val_2050 = logistic_model(2050, K_final, A_final, r_final)
val_2025 = logistic_model(2025, K_final, A_final, r_final)

print(f"--- Final Verification ---")
print(f"Model Parameters: K={K_final:.1f}, A={A_final:.3f}, r={r_final:.4f}")
print(f"Prediction for 2050: {val_2050:.4f}")
print(f"  -> Target was 7300. Error: {abs(val_2050 - 7300):.4f}")
print(f"Fit check relative to 2025 Data (329): Model says {val_2025:.1f}")

if abs(val_2050 - 7300) < 1.0:
    print("VERIFICATION SUCCESS: The model hits 7300 accurately.")
else:
    print("VERIFICATION FAILED: Discrepancy detected.")

# 3. Generate Final Plot for Paper
future_years = np.arange(2010, 2051)
pred_curve = logistic_model(future_years, K_final, A_final, r_final)

plt.figure(figsize=(10, 6))

# Plot historical context (gray)
years_old = np.array([2010, 2011, 2012])
launches_old = np.array([74, 84, 78])
plt.scatter(years_old, launches_old, color='gray', alpha=0.5, label='Pre-2013 Data (Excluded)')

# Plot active data (blue)
plt.scatter(years_data, launches_data, color='blue', s=50, label='Model Data (2013-2025)')

# Plot Curve
plt.plot(future_years, pred_curve, color='green', linewidth=2, label=f'Logistic Prediction (2050={val_2050:.0f})')

# Annotations
plt.axvline(x=2050, color='red', linestyle='--', alpha=0.5)
plt.axhline(y=7300, color='red', linestyle='--', alpha=0.5)
plt.text(2035, 7500, f'2050 Limit: {val_2050:.0f}', color='red', fontweight='bold')
plt.text(2015, 14000, f'K (Capacity) = {K_final:.0f}', color='green')

plt.title('Global Rocket Launch Limit Prediction (2025-2050)')
plt.xlabel('Year')
plt.ylabel('Annual Launches')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('rocket_prediction_final_verified.png')
print("Verification plot saved to rocket_prediction_final_verified.png")
