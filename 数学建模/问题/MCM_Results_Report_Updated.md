
# 2026 MCM Problem B: Result Analysis and Report (Updated Data)

## 5. Result Analysis (Phase 2 - Updated Parameters)

### 5.1 Dual-Objective Optimization: Cost vs Time
Using the updated extraction from the data, we re-ran the Epsilon-Constraint optimization with TOPSIS Ranking. 
*   **Key Parameter Changes**: Total Material Mass ($M_{total}$) updated to **100,000,000,000 kg (100 Million Tons)**. Space Elevator Capacity increased to 537,000 tons/year. Rocket costs set to ~$1,000/kg.
*   **Weights**: Cost ($0.3$), Time ($0.7$).
*   **Results**: Due to the high priority on **Time**, the optimal solutions favor a **Hybrid Strategy** (Max Rockets + Space Elevator).

**Table 1: Top 5 Solutions Ranking (TOPSIS)**

| Rank | Space Elevator (kg) | Rocket Sites | Total Cost ($) | Total Time (years) | TOPSIS Score | Scenario |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 33.3 Billion | 10 | 84,198 Billion | 61.9 | 0.833 | Hybrid (Heavy Rocket) |
| 2 | 32.9 Billion | 10 | 84,370 Billion | 61.3 | 0.833 | Hybrid (Heavy Rocket) |
| 3 | 33.6 Billion | 10 | 84,026 Billion | 62.6 | 0.833 | Hybrid (Heavy Rocket) |
| 4 | 33.9 Billion | 10 | 83,854 Billion | 63.3 | 0.833 | Hybrid (Heavy Rocket) |
| 5 | 34.3 Billion | 10 | 83,682 Billion | 64.0 | 0.832 | Hybrid (Heavy Rocket) |

**Detailed Interpretation:**
The dual-objective optimization outcomes highlight a fundamental conflict between economic efficiency and temporal feasibility. 
*   **The Cost of Time**: Relying solely on the Space Elevator yields the lowest possible cost ($52.5 Trillion), but the limited throughput extends the project timeline to **186 years**—spanning over two centuries. This duration is practical only for a multi-generational non-urgent expansion, not for establishing a functional colony in the near future.
*   **Hybrid Necessity**: By introducing a massive fleet of Rockets (10 launch sites operating continuously), the timeline is compressed to **~62 years**, effectively saving 124 years. This falls within a single human lifetime, making the colony viable for the current generation. However, this acceleration comes at a premium of nearly **$32 Trillion**.
*   **Decision Rationale**: The TOPSIS analysis, with a heavy weight on Time ($W_{Time}=0.7$), definitively selects the Hybrid approach. It quantifies that the value of completing the colony 1.2 centuries earlier outweighs the massive financial overhead.

### 5.2 Reliability Sensitivity Analysis
We performed Latin Hypercube Sampling (LHS) to stress-test the system against reliability variables.

**Table 2: Standardized Sensitivity Coefficients**

| Factor | Symbol | Sensitivity (Cost) | Sensitivity (Time) |
| :--- | :--- | :--- | :--- |
| SE Capacity Decay | $\gamma$ | 0.03 | **-5.83** |
| Rocket Fluctuation | $\delta$ | **-5.08** | -0.03 |
| SE Failure Rate | $\alpha$ | 0.00 | 0.47 |
| Rocket Failure Rate | $\beta$ | 0.56 | 0.00 |

**Risk Analysis:**
*   **Critical Failure Point (Time)**: The analysis identifies the Space Elevator's capacity decay rate ($\gamma$) as the single most critical risk factor (Sensitivity -5.83). Unlike rockets where failures are discrete events, any degradation in the SE cable or climber efficiency acts as a systemic bottleneck that compounds over decades. A 10% loss in SE efficiency could extend the project by over 20 years. **Rigorous maintenance of the SE cable is the paramount operational requirement.**
*   **Budget Volatility**: Cost risks are overwhelmingly driven by Rocket Cost Fluctuation ($\delta$, -5.08). Given the sheer volume of launches in the Hybrid scenario, even minor increases in propellant prices or launch site fees propagate into Trillion-dollar budget overruns. Long-term fixed-price contracts for rocket operations are essential to stabilize the financial model.

### 5.3 Water Resource Transport Strategy
*   **Demand**: 2.92 Million Tons/Year. **Recycle Rate**: 97%.
*   **Net Transport Need**: ~87,600 Tons/Year.
*   **Strategy**: Integrated Transport (Ice blocks via SE).

**Comparison & Feasibility:**
*   **Logistical Optimization**: Water presents a unique challenge: it is high-mass but low-value. Using rockets to transport water at ~$1,000/kg is economically inefficient. Our optimized strategy utilizes the Space Elevator for 100% of the water transport. By shipping water as solid ice blocks, we maximize packing density and utilize the 'fill' capacity of the elevator.
*   **Economic Impact**: This approach costs **$43.5 Billion** annually, exactly half the cost of rocket transport (**$87.6 Billion**). This 50% saving represents a massive absolute reduction in operational expenditure.
*   **Capacity utilization**: Despite the heavy absolute mass, water transport occupies less than **16%** of the elevator's annual logistic bandwidth, leaving ample capacity for high-value structural materials and equipment.

### 5.4 Life Cycle Assessment (LCA) Optimization
*   **Baseline (Pure SE)**: 10 tons CO2 (Near Zero). Cost **$52.5 Trillion**.
*   **Rocket Heavy**: > 360 Billion kg CO2. Cost **> $100 Trillion**.
*   **Factor**: ~30 Million.

**Environmental Imperative:**
From an environmental perspective, the distinction is absolute. A rocket-heavy reliance for the full 100 Million Tons would release over **360 Billion kg (0.36 Gigatons)** of CO2 into the upper atmosphere, contributing significantly to radiative forcing. The Space Elevator, once constructed, operates with near-zero marginal emissions. The Life Cycle Assessment (LCA) demonstrates that the Space Elevator prevents an ecological disaster, reducing the project's carbon footprint by a factor of **30 million**. It is the only sustainable path for planetary-scale logistics.

![LCA 3D Plot](Q4_LCA_NSGA2.png)
