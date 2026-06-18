# Problem 2: Risk Assessment Model & Quantitative Analysis

## 1. Modeling Framework

To quantify the impact of uncertainties on the stability of the logistics system, we developed a **Hybrid Monte Carlo Simulation Model**. This model integrates **Discrete Event Simulation (DES)** with stochastic process generation to evaluate the robustness of the optimal strategies derived in Problem 1 under four distinct risk categories.

### 1.1 Stochastic Risk Definitions

We modeled four core risk factors ($R_1, R_2, R_3, R_4$) based on their specific statistical characteristics:

#### **R1: Space Elevator System Failure (Bernoulli Process)**
*   **Definition**: A catastrophic annual failure event (e.g., cable snap or anchor instability) that significantly reduces capacity for a prolonged period.
*   **Model**: We model this as a Bernoulli trial per year with probability $P_{R1} = 0.02$.
*   **Impact Function**:
    $$ \eta_{SE}^{year}(t) = \begin{cases} 1.0 & \text{if } X_{R1} > 0.02 \\ 0.5 & \text{if } X_{R1} \le 0.02 \end{cases} $$
    Where $\eta$ is the capacity efficiency factor. A failure results in a **50% reduction** in annual throughput due to major repairs.

#### **R2: Maintenance Delays (Poisson-like Periodic Process)**
*   **Definition**: Routine maintenance overruns or minor technical glitches occurring on a monthly basis.
*   **Model**: Modeled as a monthly random event with $P_{R2}^{month} = 0.03$.
*   **Impact**: A **10% transient reduction** ($D_{R2}=0.1$) in monthly capacity, simulating operational slowdowns.

#### **R3: Rocket Launch Failure (Binomial Process)**
*   **Definition**: The catastrophic loss of a rocket vehicle and its payload during launch.
*   **Model**: For a planned batch of $N$ launches, the number of successful launches follows a Binomial distribution $S \sim B(N, 1-P_{R3})$, where $P_{R3} = 0.05$.
*   **Impact**:
    *   **Capacity Loss**: Direct loss of payload mass $M_{lost}$.
    *   **Cost Penalty**: Economic loss including the vehicle cost and payload replacement cost. The cost multiplier is derived as $C_{real} \approx C_{nominal} \times \frac{1}{1-P_{R3}}$.

#### **R4: Fuel Supply Chain Disruption (Monthly Random Shocks)**
*   **Definition**: Interruption in the generation or transport of Hydrogen/Methane fuel for rockets.
*   **Model**: Monthly probability $P_{R4} = 0.05$.
*   **Impact**: A **40% reduction** ($D_{R4}=0.4$) in rocket launch frequency for the affected month.

---

## 2. Simulation Algorithm

We implemented a **Time-Stepped Stochastic Simulation** engine (Python) to stress-test the strategies.

### **Algorithm Logic:**
1.  **Initialization**: Load the optimal Transport Ratio ($\alpha$) and Infrastructure Configuration from Problem 1 for a specific stage (Camp, Base, or City).
2.  **Monte Carlo Loop** ($N=500$ iterations):
    *   **Time Progression**: Step through time $t$ in 1-month increments.
    *   **Event Generation**: At each step, generate random variables for $R_1, R_2, R_3, R_4$.
    *   **Capacity Integration**:
        $$ Q_{SE}(t) = Q_{SE}^{base} \times \eta_{R1}(yr) \times \eta_{R2}(mo) $$
        $$ Q_{Rocket}(t) = Q_{Rocket}^{base} \times \eta_{R4}(mo) \times (1 - P_{R3}) $$
    *   **Accumulation**: Update total mass delivered $M(t)$. Check if Target Mass is reached.
    *   **Cost Accumulation**: Update costs, including penalties for $R_3$ (Loss Replacement).
3.  **Statistical Aggregation**: Compute Mean ($\mu$) and Standard Deviation ($\sigma$) for Time and Cost.

---

## 3. Quantitative Results & Sensitivity Analysis

We performed a comprehensive sensitivity breakdown, analyzing the impact of each risk factor individually across the three development phases.

### 3.1 Stage-by-Stage Risk Impact

The table below summarizes the simulation results, highlighting the **"Time Delay"** caused by risks compared to the deterministic baseline.

| Development Phase | Dominant Strategy | Delay Impact | Cost Premium | **Primary Risk Driver** |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1 (Camp)** | Rocket-Heavy ($\alpha \approx 0.3$) | **+0.9 Years** (+14.7%) | **+$1.2 Trillion** (+13.5%) | **R3 (Rocket Failure)**: High launch frequency amplifies explosion costs. |
| **Stage 2 (Base)** | Mixed ($\alpha \approx 0.5$) | +1.1 Years (+2.4%) | +$0.8 Trillion (+2.7%) | **Mixed**: Balanced exposure to both SE jams and launch failures. |
| **Stage 3 (City)** | Elevator-Heavy ($\alpha \approx 1.0$) | +1.4 Years (+1.9%) | **+$0.3 Trillion** (+0.9%) | **R1 (Elevator Failure)**: Capacity drops cause delays, but financial impact is low. |

All costs include the "Risk Premium" (e.g., replacement payloads, insurance, idle labor). Note that while Stage 3 has the longest absolute delay, Stage 1 suffers the highest relative cost surge due to the expensive nature of rocket replacements.

### 3.2 Key Findings

#### **Finding 1: The "Fragility of Speed" in Stage 1**
The **Camp Phase** is the most vulnerable to risk.
*   **Cause**: This phase relies heavily on rockets to meet urgent timelines.
*   **Mechanism**: A rocket explosion (R3) is a "Hard Stop" event. It instantly destroys 150 tons of cargo and effectively wastes the time slot of that launch.
*   **Data**: R3 alone contributes to ~0.8 years of the total delay in Stage 1.
*   **Implication**: Strategies dominating the Camp Phase must account for a **15% time buffer** to accommodate launch failures.

#### **Finding 2: The "Resilience of Scale" in Stage 3**
The **City Phase** shows remarkable robustness.
*   **Cause**: The Space Elevator's capacity ($537,000$ tons/year) is massive.
*   **Mechanism**: Even with a catastrophic failure (R1) reducing capacity by 50%, the remaining throughput is still far superior to any rocket fleet. The system absorbs the shock.
*   **Data**: Delay is less than 2%, despite R1 being a "Major" failure event.

#### **Finding 3: Mixed Strategy robustness in Stage 2**
The **Base Phase** benefits from **Portfolio Diversification**.
*   When Rocket fuel supply is disrupted (R4), the Space Elevator continues operation.
*   When the Space Elevator is under maintenance (R2), Rockets continue launching.
*   This mutual compensation leads to the lowest Cost Standard Deviation relative to the total project scale.

## 4. Conclusion for Risk Assessment

The Monte Carlo analysis reveals that **Risk is not uniformly distributed**.
1.  **Early Risk is Explosive**: The project is most likely to face critical delays in the first decade due to rocket reliability issues.
2.  **Late Risk is Manageable**: Once the Space Elevator infrastructure is mature, the system becomes highly stable.

**Recommendation**: We propose a **"Risk-Buffer Strategy"** for Stage 1, allocating an additional **10% budget** specifically for backup launches, whereas Stage 3 requires minimal risk contingency.
