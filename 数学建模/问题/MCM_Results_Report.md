
# 2026 MCM Problem B: Result Analysis and Report

## 5. Result Analysis

### 5.1 Dual-Objective Optimization: Cost vs Time
Using the NSGA-II algorithm, we solved the dual-objective optimization problem to minimize both total cost ($C_{total}$) and total transmission time ($T_{total}$). The resulting Pareto front (Figure 1) allows decision-makers to weigh the trade-offs between rapid deployment and budget constraints. We applied the TOPSIS method (Weights: Cost=0.6, Time=0.4) to rank the non-dominated solutions.

**Table 1: Top 5 Solutions Ranking (TOPSIS)**

| Rank | Space Elevator (kg) | Rocket Sites | Total Cost ($) | Total Time (days) | TOPSIS Score | Scenario |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 1,000,000 | 0 | 200,000,000 | 20.0 | 0.637 | Pure Elevator |
| 2 | 1,000,000 | 0 | 200,000,000 | 20.0 | 0.637 | Pure Elevator |
| 3 | 982,657 | 1 | 383,248,651 | 19.7 | 0.632 | Hybrid |
| 4 | 999,068 | 1 | 304,471,243 | 20.0 | 0.632 | Pure Elevator |
| 5 | 974,054 | 1 | 424,539,120 | 19.5 | 0.632 | Hybrid |

*Interpretation:* The analysis overwhelmingly favors the **Pure Space Elevator** strategy ("Pure Elevator") as the most cost-effective solution. While activating 1 rocket site (Hybrid) can marginally reduce time (from 20 days to ~19.5 days), it nearly doubles the cost. Given the weights ($W_C=0.6, W_T=0.4$), the cost penalty of rockets outweighs the time benefit.

![Pareto Front](Q1_DualObj_Pareto_TOPSIS.png)

### 5.2 Reliability Sensitivity Analysis
We performed a reliability sensitivity analysis using Latin Hypercube Sampling (LHS) with $N=200$ samples. The baseline scenario was "Pure Elevator" (or high-elevator hybrid). The impact of key reliability parameters on system cost and time was quantified using standardized sensitivity coefficients.

**Table 2: Standardized Sensitivity Coefficients**

| Factor | Symbol | Sensitivity (Cost) | Sensitivity (Time) | Conclusion |
| :--- | :--- | :--- | :--- | :--- |
| SE Failure Rate | $\alpha$ | ~0.00 | **0.46** | Moderate Impact on Time |
| SE Capacity Decay | $\gamma$ | ~0.04 | **-5.77** | **Critical Impact on Time** |
| Rocket Failure Rate | $\beta$ | **0.57** | ~0.00 | Moderate Impact on Cost |
| Rocket Fluctuation | $\delta$ | **-5.17** | ~0.00 | **Critical Impact on Cost** |

*Interpretation:*
1.  **Time Sensitivity**: The system's time efficiency is extremely sensitive to the Space Elevator's capacity decay coefficient ($\gamma$, coeff: -5.77). Maintaining the nominal capacity of the SE is the single most critical factor for meeting schedule targets.
2.  **Cost Sensitivity**: Cost is heavily influenced by Rocket Fluctuation ($\delta$, coeff: -5.17). This indicates that if rockets are used (even sparingly), their effective capacity per launch dictates the budget. However, since the optimal strategy is predominantly SE-based, the global cost risk is manageable if rockets are avoided.

![Sensitivity Coefficients](Q2_Sensitivity_Bar.png)

### 5.3 Water Resource Transport Strategy
We evaluated an innovative "Ice + Compressed Water" transport strategy against a traditional all-rocket approach.
*   **Recycle Rate Assumed**: 80% ($\eta = 0.8$)
*   **Strategy**: Drinking water (fresh) transported as Ice via SE; Production/Eco water transported as compressed liquid.

**Comparison Metrics:**
*   **Total Water to Transport**: 34,000 kg (post-recycling)
*   **Optimized Strategy Cost**: **$55.82 Million**
*   **Traditional Rocket Cost**: **$170.00 Million**
*   **Savings**: **$114.18 Million (67.1%)**
*   **Transport Time**: ~1.7 Years (within the 10-year window).

The strategy significantly reduces logistics costs by leveraging the SE's lower unit cost for the bulk of water transport, making the colony sustainable.

![Water Strength](Q3_Water_Strategy_Sensitivity.png)

### 5.4 Life Cycle Assessment (LCA) Optimization
Including environmental impact ($E_{CO2}$), we solved a 3-objective optimization problem.

**Pareto Front Statistics (Sample of N=100):**
*   **Low Impact Solution**: Cost $\approx$ \$200M, Time = 20 days, CO2 $\approx$ 110,000 kg (Pure SE).
*   **High Speed Solution**: Cost $\approx$ \$4.5B, Time $\approx$ 3.75 days, CO2 $\approx$ 40,000,000 kg (Rocket Heavy).

*Trade-off*: Reducing time below 10 days requires massive rocket usage, which increases Carbon Footprint by orders of magnitude (from $10^5$ kg to $10^7$ kg). The environmentally friendly choice aligns with the economically optimal choice (Space Elevator), reinforcing the SE recommendation.

![LCA 3D Plot](Q4_LCA_NSGA2.png)
