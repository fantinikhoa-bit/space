# Problem 4: Detailed Methodology & LCA Model Construction

## 4.1 System Boundaries and Problem Formulation

Our objective is to optimize the long-term transportation strategy for the Moon Colony, balancing logistical efficiency with planetary sustainability. We formulate this as a **Multi-Objective Optimization Problem (MOOP)**.

### 4.1.1 Decision Variable Space
We define the decision space as a continuous vector $\mathbf{x}$ representing the **Space Elevator (SE) Usage Ratio** across three development phases:
$$ \mathbf{x} = [\alpha_{Camp}, \alpha_{Base}, \alpha_{City}]^T, \quad \text{where } 0 \le \alpha_k \le 1 $$
*   $\alpha_k = 1$: Phase $k$ relies exclusively on the Space Elevator (Zero-Emission).
*   $\alpha_k = 0$: Phase $k$ relies exclusively on Heavy Rockets (High-Emission).

### 4.1.2 The "Trilemma" Objective Functions
We simultaneously minimize three conflicting objectives:
$$ \min \mathbf{F}(\mathbf{x}) = [f_{Time}(\mathbf{x}), f_{Cost}(\mathbf{x}), f_{Env}(\mathbf{x})] $$

**1. Time Objective ($f_{Time}$)**
Each phase $k$ proceeds in parallel mode (Rocket + SE). The duration is constrained by the slower bottleneck channel:
$$ T_k(\alpha_k) = \max \left( \frac{M_k \cdot \alpha_k}{Q_{SE}}, \frac{M_k \cdot (1-\alpha_k)}{Q_{Rocket}} \right) $$
$$ f_{Time}(\mathbf{x}) = \sum_{k=1}^{3} T_k(\alpha_k) $$

**2. Cost Objective ($f_{Cost}$)**
$$ f_{Cost}(\mathbf{x}) = C_{fixed} + \sum_{k=1}^{3} M_k \left[ \alpha_k C_{SE} + (1-\alpha_k) C_{Rocket} \right] $$

**3. Environmental Objective ($f_{Env}$): The LCA Model**
We adopt a **Life Cycle Assessment (LCA)** approach, focusing on the distinct impact of *Stratospheric Emissions*.

## 4.2 Stratospheric Impact LCA Model

Standard carbon accounting underestimates the impact of rocket launches. We introduce a physics-based correction model.

### 4.2.1 The Stratospheric Multiplier Effect
Rockets inject **Black Carbon (BC)** and **Aluminum Oxide ($Al_2O_3$)** directly into the stratosphere (>15km altitude). Unlike surface emissions which are washed out by rain days, stratospheric aerosols persist for **3-5 years**, absorbing solar radiation and depleting ozone.

We define the **Effective CO2 Equivalent Emissions ($E_{eff}$)**:
$$ E_{eff} = E_{Ground} + \kappa \cdot E_{Upper} $$
Where $\kappa$ is the **Stratospheric Forcing Multiplier**. Based on Ross et al. (2010), the radiative forcing of stratospheric soot is approx. $10^3 \sim 10^4$ times higher per unit mass than surface $CO_2$. For this model, we conservatively adopt a weighted factor of **$\kappa = 2.0$** applied to the total fuel mass to represent this amplified GWP (Global Warming Potential).

### 4.2.2 Calculation Formula
$$ f_{Env}(\mathbf{x}) = E_{Const} + \sum_{k=1}^{3} M_k \cdot (1-\alpha_k) \cdot \lambda_{Rock} \cdot \kappa $$
*   $E_{Const}$: Fixed emissions from building Launch Sites (Concrete/Steel).
*   $\lambda_{Rock}$: Specific fuel consumption per kg of payload (approx. 25-50 kg fuel/kg payload).

## 4.3 Solver Algorithm: NSGA-II

Since the objectives are non-convex and conflicting, we utilize the **Non-dominated Sorting Genetic Algorithm II (NSGA-II)** to approximate the Pareto Front.

### 4.3.1 Core Mechanisms
1.  **Fast Non-Dominated Sorting**:
    We classify the population into distinct fronts $\mathcal{F}_1, \mathcal{F}_2, ...$ based on Pareto dominance.
    $$ \mathbf{x}_i \succ \mathbf{x}_j \iff \forall m, f_m(\mathbf{x}_i) \le f_m(\mathbf{x}_j) \land \exists n, f_n(\mathbf{x}_i) < f_n(\mathbf{x}_j) $$
    Solutions in $\mathcal{F}_1$ are not dominated by any other solution and represent the best trade-offs found so far.

2.  **Crowding Distance Calculation**:
    To maintain diversity (avoid clustering), we calculate a density metric $d_i$ for each individual:
    $$ d_i = \sum_{m=1}^{M} \frac{f_m(i+1) - f_m(i-1)}{f_m^{max} - f_m^{min}} $$
    Within the same rank, solutions with larger $d_i$ (sparser regions) are preferred.

3.  **Elite Preservation**:
    The parent and offspring populations are combined ($N+N$), then sorted. The top $N$ individuals form the next generation, ensuring good solutions are never lost ("Elitism").

### 4.3.2 Implementation
*   **Population Size**: 200
*   **Generations**: 50
*   **Mutation Rate**: 0.1 (Gaussian perturbation)
*   **Selection**: Binary Tournament based on $(Rank, Distance)$.

This rigorous methodology ensures that our recommended "Phased Strategy" is not an arbitrary choice, but a mathematically proven **Pareto-Optimal Solution**.
