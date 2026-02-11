# A Parameterized Multi-Criteria Decision Model for Strategic AI Investment Prioritization

## Abstract

Organizations increasingly face the challenge of allocating limited resources across competing artificial intelligence (AI) initiatives. While AI promises transformative operational improvements, research indicates that 85% of AI projects fail to deliver expected value—primarily due to inadequate process readiness rather than technological limitations. This paper presents a parameterized Multi-Criteria Decision Analysis (MCDA) framework for systematically evaluating and prioritizing AI investments. The model employs weighted scoring across three dimensions—Readiness, Return on Investment (ROI), and Risk—with non-compensatory gates to filter unsuitable candidates. All parameters are justified through industry research and validated via sensitivity analysis, including Monte Carlo simulation. Applied to a real dataset of 8,469 customer support tickets across 16 process categories, the model demonstrates 100% ranking stability for top priorities across 500 simulated parameter variations. The framework is designed for portability across domains including feature prioritization, vendor selection, and technical debt management.

**Keywords:** Multi-Criteria Decision Analysis, AI Strategy, ROI Modeling, Weighted Scoring, Sensitivity Analysis, Operations Research

---

## 1. Introduction

### 1.1 Problem Context

The adoption of artificial intelligence in enterprise operations has accelerated dramatically, with global AI spending projected to exceed $500 billion annually by 2027 (IDC, 2023). However, this investment surge has not been matched by commensurate returns. McKinsey's Global AI Survey (2023) reports that only 22% of organizations have successfully scaled AI beyond pilot programs, while Gartner (2022) estimates that 85% of AI projects fail to transition to production.

A critical examination of these failures reveals a consistent pattern: organizations prioritize technological capability over operational readiness. The fundamental question—*which processes should be automated?*—is often answered through intuition, vendor influence, or executive mandate rather than systematic analysis. This approach leads to misallocated resources, failed implementations, and organizational skepticism toward AI initiatives.

### 1.2 Research Objective

This work addresses the prioritization problem through a quantitative decision framework that evaluates AI automation candidates across multiple criteria simultaneously. The model answers three essential questions:

1. **Readiness**: Is the process sufficiently mature for AI implementation?
2. **Return**: What financial value will automation deliver?
3. **Risk**: What operational, compliance, or reputational risks does automation introduce?

The framework produces a ranked priority list with actionable recommendations, enabling evidence-based resource allocation.

### 1.3 Contribution

This paper makes the following contributions:

- A fully parameterized MCDA implementation with documented formulas
- Research-backed justification for all model parameters
- Sensitivity analysis demonstrating model robustness
- Application to real-world customer support data
- Adaptation guidelines for cross-domain portability

---

## 2. Theoretical Foundation

### 2.1 Multi-Criteria Decision Analysis

Multi-Criteria Decision Analysis (MCDA) encompasses a family of methods for evaluating alternatives against multiple, often conflicting, objectives (Belton & Stewart, 2002). The approach is well-established in operations research, with applications spanning infrastructure planning, healthcare resource allocation, and environmental policy.

This implementation employs the Weighted Sum Model (WSM), one of the most widely used MCDA techniques. For a set of alternatives *A = {a₁, a₂, ..., aₙ}* evaluated against criteria *C = {c₁, c₂, ..., cₘ}*, the score for alternative *aᵢ* is computed as:

```
S(aᵢ) = Σⱼ wⱼ · vᵢⱼ
```

Where:
- *wⱼ* represents the weight assigned to criterion *cⱼ* (Σwⱼ = 1)
- *vᵢⱼ* represents the normalized score of alternative *aᵢ* on criterion *cⱼ*

### 2.2 Compensatory vs. Non-Compensatory Models

A key design decision in MCDA concerns whether high performance on one criterion can compensate for poor performance on another. Pure weighted sum models are fully compensatory—a sufficiently high ROI could theoretically offset unacceptable risk levels.

This framework incorporates non-compensatory **gates** that filter alternatives before scoring. Alternatives failing to meet minimum readiness thresholds or exceeding maximum risk tolerances are excluded regardless of other scores. This hybrid approach aligns with enterprise risk management principles (ISO 31000) and reflects the reality that certain deficiencies cannot be offset by other strengths.

### 2.3 Relationship to Other Parameterized Models

The mathematical structure employed here parallels parameterized models in other domains:

| Domain | Model | Parameters | Analogous Elements |
|--------|-------|------------|-------------------|
| Epidemiology | SIR/SEIR | β (transmission), γ (recovery) | Dimension weights |
| Finance | Credit Scoring | Factor weights, cutoff thresholds | Metric weights, gates |
| Economics | Cobb-Douglas | α, β (factor elasticities) | w_readiness, w_roi, w_risk |
| Options Pricing | Black-Scholes | σ (volatility), r (risk-free rate) | Risk parameters |

In each case, the model structure encodes domain knowledge through parameters that can be calibrated against empirical data or expert judgment.

---

## 3. Model Specification

### 3.1 Dimensional Structure

The model evaluates alternatives across three primary dimensions:

**Dimension 1: Readiness (R)**
Assesses whether prerequisite conditions for successful AI implementation exist. Comprised of four equally-weighted metrics:
- Data availability (M01)
- Data quality (M02)
- Process standardization (M03)
- Tool/integration readiness (M04)

**Dimension 2: Suitability (S)**
Evaluates the technical fit between the process and AI capabilities. Comprised of four metrics:
- Automation feasibility (M05, weight: 0.30)
- NLP/Pattern clarity (M06, weight: 0.25)
- Exception complexity (M07, weight: 0.20, inverted)
- Human-in-loop fit (M08, weight: 0.25)

**Dimension 3: Risk (K)**
Quantifies potential negative consequences of automation. Comprised of three metrics:
- Compliance/privacy sensitivity (M09, weight: 0.35)
- Customer harm potential (M10, weight: 0.35)
- Model error tolerance (M11, weight: 0.30, inverted)

### 3.2 Scoring Normalization

Raw scores are collected on a 1-5 Likert scale and normalized to [0, 1]:

```
v_norm = (score - scale_min) / (scale_max - scale_min) = (score - 1) / (5 - 1)
```

For metrics where higher values indicate worse outcomes (e.g., exception complexity), the normalized score is inverted when computing dimension scores but preserved when computing risk.

### 3.3 Dimension Score Computation

For each dimension *d* containing metrics *M_d*:

```
Score_d = 100 × Σ(w_m · v_m_adj) / Σ(w_m)
```

Where *v_m_adj* applies direction adjustment:
- HigherBetter: v_m_adj = v_m
- HigherWorse: v_m_adj = 1 - v_m

### 3.4 ROI Computation

Financial return is modeled through cost displacement:

```
Monthly Manual Cost = V × H × C × O
```

Where:
- V = Monthly ticket/task volume
- H = Average handle time (hours)
- C = Fully-loaded agent cost per hour
- O = Overhead multiplier

```
Monthly Savings = Manual Cost × α × φ
```

Where:
- α = Automation shift rate (Full: 0.70, Partial: 0.40, Assist: 0.20)
- φ = Adoption rate (default: 0.80)

```
Payback Period = Implementation Cost / Monthly Savings
ROI Ratio = Annual Savings / Implementation Cost
```

### 3.5 Priority Score with Gates

The final priority score applies strategy weights and non-compensatory gates:

```
Priority = G × (w_R · R + w_ROI · ROI + w_K · (100 - K))
```

Where the gate function G is defined as:

```
G = 1  if R ≥ R_min AND K ≤ K_max
G = 0  otherwise
```

---

## 4. Parameter Justification

### 4.1 Dimension Weights

| Parameter | Value | Justification |
|-----------|-------|---------------|
| w_readiness | 0.35 | Gartner (2022): 85% of AI failures trace to readiness issues |
| w_roi | 0.45 | McKinsey (2023): ROI is primary criterion for 67% of AI decisions |
| w_risk | 0.20 | ISO 31000: Risk is gated, residual risk weighted lower |

### 4.2 Gate Thresholds

| Parameter | Value | Justification |
|-----------|-------|---------------|
| min_readiness | 50 | Forrester (2022): <50 readiness correlates with <50% success rate |
| max_risk | 70 | Enterprise risk management: 70th percentile separates manageable from unacceptable |

### 4.3 Automation Shift Rates

| Type | Rate | Justification |
|------|------|---------------|
| Full Automation | 0.70 | IBM Watson studies: 65-80% containment typical |
| Partial Automation | 0.40 | McKinsey: Augmentation saves 30-50% |
| AI Assist | 0.20 | Gartner: Copilots improve productivity 15-25% |

---

## 5. Results

### 5.1 Baseline Scenario Rankings

| Rank | Process Step | Priority | Readiness | Risk | Annual Savings |
|------|--------------|----------|-----------|------|----------------|
| 1 | Product setup | 93 | 100 | 0 | $28,509 |
| 2 | Installation support | 89 | 94 | 9 | $22,071 |
| 3 | Product recommendation | 85 | 94 | 9 | $22,439 |
| 4 | Battery life | 81 | 75 | 9 | $20,179 |
| 5 | Display issue | 80 | 75 | 25 | $24,524 |

### 5.2 Financial Summary

| Metric | Value |
|--------|-------|
| Total Annual Savings | $288,651 |
| Total Implementation Cost | $266,200 |
| Portfolio ROI Ratio | 1.08x |
| Aggregate Payback Period | 11.1 months |

### 5.3 Scenario Comparison

| Scenario | Items Prioritized | Items Gated | Annual Savings | Payback |
|----------|-------------------|-------------|----------------|---------|
| Baseline | 14 | 2 | $288,651 | 11.1 mo |
| Cost Pressure | 14 | 2 | $423,563 | 6.3 mo |
| High Growth | 13 | 3 | $582,384 | 6.1 mo |
| Compliance Heavy | 11 | 5 | $221,601 | 15.1 mo |

---

## 6. Sensitivity Analysis

### 6.1 Monte Carlo Simulation (n=500)

| Metric | Value |
|--------|-------|
| Mean Annual Savings | $286,000 |
| Standard Deviation | $40,000 |
| 90% Confidence Interval | [$222K, $354K] |
| "Product Setup" Ranked #1 | 500/500 (100%) |

### 6.2 Weight Sensitivity

Top two priorities remained stable across all seven tested weight combinations, demonstrating robust recommendations.

---

## 7. Conclusion

This paper presented a parameterized MCDA framework for AI investment prioritization. Applied to real customer support data, the framework identified robust automation candidates validated through sensitivity analysis. The mathematical structure is portable to any multi-criteria prioritization problem.

---

## References

Belton, V., & Stewart, T. (2002). *Multiple Criteria Decision Analysis*. Springer.
Gartner. (2022). *Predicts 2023: AI Requires New Approaches*.
McKinsey & Company. (2023). *The State of AI in 2023*.
ISO. (2018). *ISO 31000:2018 Risk Management Guidelines*.
NIST. (2023). *AI Risk Management Framework*.
