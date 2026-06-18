
# 2026 MCM Problem B: Result Analysis and Report (Mathematical Optimization)

## 5. Result Analysis: The Knee Point Solution

### 5.1 Methodology: Epsilon-Constraint Optimization
Instead of fixing the project duration arbitrarily, we employed a generic **Multi-Objective Integer Programming** framework:
*   **Objectives**: Minimize Cost ($Z_1$) and Minimize Time ($Z_2$).
*   **Constraints**: Total Material ($M_{total} = 10^9$ kg), Annual Capacity Limits ($Q_{SE}, Q_{Rocket}$).

We solved this using the **$\epsilon$-Constraint Method**: by fixing the project duration $T$ (ranging from the theoretical minimum of ~1.3 years to ~2.0 years) and minimizing Cost for each $T$. This generated the Pareto Front shown in Figure 1.

### 5.2 The "Knee Point" (Optimal Solution)
The optimal trade-off is identified at the **"Knee Point"** of the Pareto curve—the point where the marginal cost to further reduce time increases sharply.

**Optimal Solution Specifications:**
*   **Total Duration**: **679 Days** (approx. 1.86 Years).
*   **Total Cost**: **$525.35 Billion**.
*   **Transport Strategy**:
    *   **Space Elevator**: 99.9% of load (999 Million kg).
    *   **Rockets**: 0.1% of load (1 Million kg) via **1 Launch Site**.
    *   *Note*: Activation of 1 rocket site balances the very last bit of capacity needed to meet this specific deadline without waiting for the SE's next cycle. Although purely SE is cheaper, this specific "Knee" point suggests a tiny hybrid component is analytically part of the mathematical front, though practically indistinguishable from Pure SE.

**Why this is optimal**:
As seen in the data, reducing time below 600 days requires a massive exponential increase in cost (blue curve shoots up), involving 8+ rocket sites and costing over $640 Billion. The Knee Point represents the sweet spot where we achieve the lowest cost ($525B) without an unnecessarily long delay.

![Pareto Front and Knee Point](Q1_DualObj_Pareto_TOPSIS.png)

### 5.3 Sensitivity & Risks
*   **Time Criticality**: The project duration is highly sensitive to the Space Elevator's capacity decay. Maintaining SE efficiency is paramount.
*   **Cost Stability**: The recommended solution minimizes exposure to Rocket failure risks, making the budget highly predictable.

### 5.4 Recommendation
We recommend the **Knee Point Strategy**:
1.  **Primary**: Rely on Space Elevator for >99% of logistics.
2.  **Secondary**: Maintain **1 Rocket Launch Site** as a strategic buffer to ensure schedule adherence and handle emergency deviations, but do not rely on it for bulk transport.
3.  **Budget**: Allocate **$525 Billion** for transport logistics.
4.  **Timeline**: Plan for a **1.9-Year** transport phase.
