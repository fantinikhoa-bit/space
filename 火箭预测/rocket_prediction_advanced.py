
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from statsmodels.tsa.arima.model import ARIMA
import warnings

warnings.filterwarnings("ignore")

# Data
years = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025])
launches = np.array([74, 84, 78, 81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223, 329])

# Fill missing year 2024 for time series models
years_full = np.arange(2010, 2026)
launches_series = pd.Series(index=years, data=launches)
# Reindex and interpolate for 2024
launches_full = launches_series.reindex(years_full).interpolate(method='linear')

future_years = np.arange(2010, 2051)
forecast_horizon = 2050 - 2025

# --- Method 1: Bass Diffusion Model ---
# Often used for product/technology adoption forecasting.
# f(t) = (p + q * (N(t-1)/M)) * (M - N(t-1))
# Here we fit Cumulative Launches first, then derive annual.
cumulative_launches = np.cumsum(launches)

def bass_cumulative(t, M, p, q):
    t_start = 0 
    # Bass Cumulative Function
    # N(t) = M * (1 - exp(-(p+q)t)) / (1 + (q/p)*exp(-(p+q)t))
    num = 1 - np.exp(-(p+q)*(t - t_start))
    den = 1 + (q/p)*np.exp(-(p+q)*(t - t_start))
    return M * (num / den)

# Initial guess: M=Total Potential Market (Limit), p=Innovation rate, q=Imitation rate
try:
    # Estimate cumulative data
    cum_launches_data = np.cumsum(launches_full)
    # Time steps 1, 2, ...
    t_steps = np.arange(1, len(cum_launches_data) + 1)
    
    p0_bass = [50000, 0.001, 0.1]
    bounds_bass = ([cum_launches_data.max(), 0, 0], [1000000, 1.0, 1.0])
    
    popt_bass, _ = curve_fit(bass_cumulative, t_steps, cum_launches_data, p0=p0_bass, bounds=bounds_bass, maxfev=10000)
    M_bass, p_bass, q_bass = popt_bass
    
    # Predict
    total_steps = len(future_years)
    t_future = np.arange(1, total_steps + 1)
    pred_cum_bass = bass_cumulative(t_future, M_bass, p_bass, q_bass)
    # Annual launches is the difference of cumulative
    pred_annual_bass = np.diff(pred_cum_bass, prepend=0)
    # Adjust first point to match actual scale roughly for plotting
    pred_annual_bass[0] = launches[0] 
    
    val_2050_bass = pred_annual_bass[-1]
except Exception as e:
    print(f"Bass Model failed: {e}")
    val_2050_bass = 0
    pred_annual_bass = np.zeros(len(future_years))


# --- Method 2: ARIMA (Time Series) ---
# AutoRegressive Integrated Moving Average
try:
    # Fit ARIMA on the full interpolated dataset
    # Order (p,d,q) needs tuning, usually (1,1,1) or (2,2,0) for trending growth
    # We use valid simple heuristics here or auto-fit if using pmdarima (not available)
    # Let's try ARIMA(1,2,0) which handles quadratic-like trends well
    arima_model = ARIMA(launches_full, order=(1, 2, 0)) 
    arima_res = arima_model.fit()
    
    # Forecast
    arima_forecast_obj = arima_res.get_forecast(steps=forecast_horizon)
    arima_pred = arima_forecast_obj.predicted_mean
    
    # Stitch history + forecast
    pred_arima_full = np.concatenate([launches_full, arima_pred])
    val_2050_arima = pred_arima_full[-1]

    # Get Confidence Intervals
    conf_int = arima_forecast_obj.conf_int(alpha=0.05)
    lower_series = conf_int.iloc[:, 0]
    upper_series = conf_int.iloc[:, 1]
except Exception as e:
    print(f"ARIMA failed: {e}")
    val_2050_arima = 0
    pred_arima_full = np.zeros(len(future_years))

# Print Results
print("--- Advanced Prediction Comparison for 2050 ---")
if val_2050_bass > 0:
    print(f"1. Bass Diffusion Model (Tech Adoption): {val_2050_bass:.2f}")
    print(f"   (Parameters: Potenital Total={M_bass:.0f}, p={p_bass:.4f}, q={q_bass:.4f})")
if val_2050_arima > 0:
    print(f"2. ARIMA(1,2,0) Time Series: {val_2050_arima:.2f}")

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(years, launches, color='black', label='Historical Data', zorder=5)

if val_2050_bass > 0:
    plt.plot(future_years, pred_annual_bass, label=f'Bass Diffusion (2050: {val_2050_bass:.0f})', color='purple', linestyle='-')

if val_2050_arima > 0:
    plt.plot(future_years, pred_arima_full, label=f'ARIMA(1,2,0) (2050: {val_2050_arima:.0f})', color='green', linestyle='--')
    # Fill confidence interval for ARIMA
    # plt.fill_between(np.arange(2026, 2051), lower_series, upper_series, color='green', alpha=0.1)

plt.title('Advanced Rocket Launch Prediction Models')
plt.xlabel('Year')
plt.ylabel('Annual Launches')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('rocket_prediction_advanced.png')
print("Comparison plot saved to rocket_prediction_advanced.png")
