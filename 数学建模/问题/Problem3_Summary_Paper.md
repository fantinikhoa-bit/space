# Problem 3: Water Sustainment Analysis for a Fully Operational Colony

## 3.1 Problem Restatement & Assumption

The objective is to determine the additional cost and timeline required to supply water for a **100,000-person Moon Colony** for one full year. We focus on the **City Phase (Year 2050+)**, where the Space Elevator infrastructure is fully operational.

**Key Assumption:**
We assume the goal is **sustainment** (covering daily consumption and losses), not initial filling of reservoirs. Water is transported as **solid ice blocks** via the Space Elevator to minimize containment weight.

## 3.2 Methodology: Earth-to-Moon Demand Mapping

To estimate the water demand of a future lunar society, we explicitly reject static assumptions. Instead, we construct a **Predictive Mapping Model** that links Earth's usage trends to the Moon's operational requirements.

### 3.2.1 Phase 1: Earth Trend Prediction (Time Series Regression)
We trained a Linear Regression model on Earth's per capita water withdrawal data (2015-2024), which demonstrates a clear downward trend due to efficiency gains.
*   **Model Function**: $D_{Earth}(t) = -0.987t + C$
*   **2050 Forecast**: The model predicts Earth's efficiency will improve to **136.4 kg/person/day** by 2050.

### 3.2.2 Phase 2: The "Lunar Equivalence" Hypothesis
How does Earth's usage translate to the Moon? We introduce a **Living Standard Coefficient ($\gamma$)**:
$$ D_{Moon} = D_{Earth\_2050} \times \gamma $$
*   We adopt **$\gamma = 1.0$** (Parity Assumption).
*   **Rationale**: For a permanent city of 100,000 people to be psychologically sustainable, it must offer a **"Terrestrial Quality of Life"**. While personal hygiene may be stricter ($\gamma < 1$), the need for extensive **Biosphere Maintenance** (oxygen generation, humidity control, parkland irrigation) greatly increases per capita infrastructure consumtion ($\gamma > 1$). These factors balance out.
*   **Stress Test**: By using the higher "Earth-like" baseline ($136.4$) rather than a survival minimum ($<20$), we ensure our logistics model is robust enough to support a thriving, not just surviving, society.

### 3.2.3 Net Logistic Burden Model
The actual mass requiring transport from Earth is derived from the gap in the recycling system:
$$ M_{net} = P \times D_{2050} \times (1 - \eta) \times 365 \times (1 + \delta_{safety}) $$
Where:
*   $P = 100,000$ (Population)
*   $D_{2050} = 136.4$ kg/day (Base Demand)
*   $\eta$: Effective Recycling Rate (Variable parameter)
*   $\delta_{safety} = 0.10$ (10% Strategic Reserve buffer)

## 3.3 Quantitative Results

We evaluated the logistic burden under varying recycling efficiencies using the Space Elevator (SE) transport capacity ($Q_{SE} = 537,000$ tons/year) and unit cost ($525/kg).

### 3.3.1 Sensitivity Analysis Table

| Recycling Rate ($\eta$) | Net Annual Import (Million kg) | **Additional Cost ($ Billion)** | **Timeline Occupancy (Days)** | SE Capacity Load (%) | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **90%** | 553.1 | $290.4 | 376 days | **103.0%** | **FAILED**. Demand exceeds total supply capacity. |
| **95%** | 276.6 | $145.2 | 188 days | 51.5% | **Risky**. Consumes >50% of logistics. |
| **98%** | **110.6** | **$58.1** | **75 days** | **20.6%** | **OPTIMAL**. Feasible & Sustainable. |
| **99%** | 55.3 | $29.0 | 38 days | 10.3% | Ideal Goal. |

### 3.4 Findings & Discussion

1.  **The "98% Threshold"**:
    Our model reveals a critical tipping point. If the colony's water recycling rate falls below **98%**, the logistics required just to supply water would overwhelm the Space Elevator, crowding out food, equipment, and personnel transport. A 90% rate (current ISS standard) is mathematically impossible for a population of 100,000.

2.  **Logistic Cost & Timeline**:
    Under the recommended **98% recycling scenario**:
    *   **Additional Cost**: **$58.1 Billion** per year. While significant, this is an operational expense equivalent to ~0.05% of Global GDP in 2050, making it economically viable.
    *   **Timeline Impact**: The water transport will occupy **75 days (approx. 2.5 months)** of the Space Elevator's annual schedule. This leaves the remaining ~290 days available for other commercial and scientific payloads.

## 3.5 Conclusion for Problem 3

To ensure the water security of the Moon Colony:
1.  **Strict Technology Mandate**: The colony MUST implement ECLSS technologies capable of **$\ge 98\%$ recycling efficiency**.
2.  **Dedicated Logistics Window**: A **75-day dedicated window** each year must be allocated for "Ice Block" transport via the Space Elevator.
3.  **Budget Allocation**: An annual sustainment budget of **$58 Billion** is required solely for water logistics.
