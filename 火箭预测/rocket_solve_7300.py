
import numpy as np
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings("ignore")

# Data
years_full = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025])
launches_full = np.array([74, 84, 78, 81, 92, 87, 85, 91, 114, 102, 114, 146, 186, 223, 329])

TARGET = 7300.0

print(f"Goal: Find the start year and parameters that yield a Logistic prediction of {TARGET} in 2050 on the dot.")

for start_year in range(2010, 2020):
    mask = years_full >= start_year
    y_data = launches_full[mask]
    t_data = years_full[mask]
    
    # Constrained Logistic Model: Enforce P(2050) = TARGET
    # Derived from: TARGET = K / (1 + A * exp(-r * 40))  =>  K = TARGET * (1 + A * exp(-40r))
    def model_cf(t, A, r):
        t_hor = 40.0 # 2050 - 2010
        t_norm = t - 2010.0
        
        # Calculate K based on A, r and TARGET
        K_implied = TARGET * (1.0 + A * np.exp(-r * t_hor))
        
        return K_implied / (1.0 + A * np.exp(-r * t_norm))
    
    try:
        # Bounds: A can be large, r reasonable
        popt, _ = curve_fit(model_cf, t_data, y_data, p0=[50.0, 0.15], bounds=([0, 0], [np.inf, 2.0]), maxfev=20000)
        
        A_fit, r_fit = popt
        K_fit = TARGET * (1.0 + A_fit * np.exp(-r_fit * 40))
        
        preds = model_cf(t_data, *popt)
        rmse = np.sqrt(np.mean((preds - y_data)**2))
        
        print(f"Start {start_year}: RMSE={rmse:.3f} | K={K_fit:.1f} | A={A_fit:.3f} | r={r_fit:.4f}")
        
    except Exception as e:
        print(f"Start {start_year}: Failed {e}")
