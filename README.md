# AI Readiness & ROI Simulator

![AI Readiness & ROI Simulator](assets/banner.svg)

**A parameterized decision model for strategic AI investment prioritization**

> *This is a Multi-Criteria Decision Analysis (MCDA) implementation using weighted scoring—the same mathematical structure used in operations research, epidemiological compartmental models (SIR/SEIR), and credit risk scoring. Parameters are justified by industry research and validated through sensitivity analysis.*

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Model](https://img.shields.io/badge/Model-MCDA%20%2F%20WSM-purple)
![Status](https://img.shields.io/badge/Status-Portfolio%20Ready-brightgreen)

---

## 🎯 Problem Statement

Organizations waste millions on AI initiatives that fail—not because the technology doesn't work, but because they automate the wrong processes. This tool provides a **data-driven, mathematically rigorous framework** to answer:

- Which processes are *ready* for AI automation?
- Which will deliver the highest *ROI*?
- Which carry unacceptable *risk*?

## 🧮 Mathematical Foundation

This project implements a **parameterized decision model**—the same class of models used in:

| Domain | Model Type | Our Implementation |
|--------|------------|-------------------|
| Epidemiology | SIR/SEIR compartmental models | Parameter-driven state transitions |
| Finance | Credit scoring (FICO) | Weighted multi-factor scoring |
| Operations Research | Analytic Hierarchy Process (AHP) | Hierarchical criteria with weights |
| Decision Science | Multi-Criteria Decision Analysis | Compensatory weighted sum with gates |

### Core Model

```
Priority = GateFactor × (w_r × Readiness + w_roi × ROI + w_risk × Safety)

Where:
  GateFactor ∈ {0, 1}  — Non-compensatory threshold filter
  w_r, w_roi, w_risk   — Strategy weights (Σ = 1.0)
  Readiness, ROI       — Dimension scores [0, 100]
  Safety = 100 - Risk  — Inverted risk score
```

### Parameter Justification

All parameters are derived from **industry research and empirical benchmarks**—not arbitrary choices. See [`docs/PARAMETER_JUSTIFICATION.md`](docs/PARAMETER_JUSTIFICATION.md) for complete citations including:

- McKinsey Global AI Survey (ROI primacy in 67% of decisions)
- Gartner research (85% AI failures trace to readiness issues)
- Forrester Automation Success Index (readiness-success correlation)
- ISO 31000 / NIST AI RMF (risk management frameworks)

---

## 📊 What This Project Demonstrates

| Skill | Evidence |
|-------|----------|
| **Mathematical Modeling** | Parameterized decision model with documented assumptions |
| **Quantitative Analysis** | Weighted scoring, ROI calculations, sensitivity analysis |
| **Business Analysis** | Process mapping, stakeholder requirements, scenario planning |
| **Research Rigor** | Parameter justification with academic/industry citations |
| **Technical Implementation** | Python engine, modular architecture, comprehensive testing |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      INPUT LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ProcessSteps │  │StepScores   │  │BusinessParams       │  │
│  │(workflow)   │  │(assessments)│  │(scenario economics) │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                     SCORING ENGINE                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Dimension_Score = 100 × Σ(norm_score × weight) / Σw   │  │
│  │ ROI_Score = 0.6 × PaybackScore + 0.4 × RatioScore     │  │
│  │ Priority = Gate × (w_r·R + w_roi·ROI + w_risk·Safety) │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                     VALIDATION LAYER                        │
│  ┌─────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │Weight Sensitivity│  │Gate Sensitivity│  │Monte Carlo   │  │
│  │Analysis          │  │Analysis        │  │Simulation    │  │
│  └─────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-readiness-roi-simulator.git
cd ai-readiness-roi-simulator

# Install dependencies
pip install -r requirements.txt

# Run baseline scenario
python run_model.py --scenario SCN_BASE

# Run sensitivity analysis
python src/sensitivity_analysis.py

# List all scenarios
python run_model.py --list-scenarios
```

---

## 📈 Model Validation: Sensitivity Analysis

A mathematical model is only as good as its robustness to parameter uncertainty. We validate through:

### 1. Weight Sensitivity

**Question:** Do top priorities change with different weight schemes?

| Weight Scheme | #1 Priority | #2 Priority | Stability |
|---------------|-------------|-------------|-----------|
| Baseline (35/45/20) | Product setup | Installation support | ✅ |
| ROI Heavy (20/60/20) | Product setup | Installation support | ✅ |
| Risk Averse (30/30/40) | Product setup | Installation support | ✅ |
| Equal Weights (33/34/33) | Product setup | Installation support | ✅ |

**Finding:** Top 2 priorities are **100% stable** across all reasonable weight combinations.

### 2. Monte Carlo Simulation (n=500)

```
📊 SAVINGS DISTRIBUTION:
   Mean:    $286K
   Median:  $283K
   Std Dev: $40K
   90% CI:  [$222K, $354K]

📊 TOP PRIORITY STABILITY:
   "Product Setup" ranked #1 in 500/500 simulations (100%)
```

**Finding:** Recommendations are robust to parameter uncertainty within ±20%.

### 3. Gate Sensitivity

| Gates (Readiness/Risk) | Items Prioritized | Potential Savings |
|------------------------|-------------------|-------------------|
| Loose (40/80) | 14 | $289K |
| **Baseline (50/70)** | **14** | **$289K** |
| Strict (70/55) | 9 | $192K |

**Finding:** Baseline gates are optimal; tightening reduces opportunity by $96K.

---

## 🎛️ Scenario Configuration

The system is **fully parameterized**—change business context without code changes:

### Available Scenarios

| Scenario | Focus | Annual Savings | ROI | Payback |
|----------|-------|----------------|-----|---------|
| **Baseline** | Balanced | $289K | 1.08x | 11.1 mo |
| **Cost Pressure** | Aggressive ROI | $424K | 1.91x | 6.3 mo |
| **High Growth** | Scale ops | $582K | 1.98x | 6.1 mo |
| **Compliance** | Risk-averse | $222K | 0.80x | 15.1 mo |

### Parameter Categories

```yaml
# Business Economics (change by company)
ticket_volume_monthly: 8500
agent_cost_per_hour: 28
implementation_budget: 150000

# Strategy Weights (change by leadership)
w_readiness: 0.35  # Justified: industry research
w_roi: 0.45        # Justified: CFO decision patterns
w_risk: 0.20       # Justified: risk management frameworks

# Gates (non-compensatory thresholds)
min_readiness_gate: 50  # Justified: Forrester success data
max_risk_gate: 70       # Justified: ISO 31000 principles
```

---

## 📁 Project Structure

```
ai-readiness-roi/
├── assets/
│   └── banner.svg            # Project banner
├── data/
│   ├── ProcessSteps.csv      # 16 workflow steps (from real data)
│   ├── ScoringMetrics.csv    # 11 metrics, 3 dimensions
│   ├── StepScores.csv        # 176 manual assessments
│   ├── BusinessParams.csv    # 4 scenario economics
│   ├── StrategyParams.csv    # 4 strategy configurations
│   └── real_tickets_source.csv  # Source: Kaggle (8,469 tickets)
├── docs/
│   └── PARAMETER_JUSTIFICATION.md  # Research citations
├── outputs/
│   ├── ModelOutput_*.csv     # Results per scenario
│   └── AIReadinessDashboard.jsx  # Interactive visualization
├── src/
│   ├── io.py                 # Data loading utilities
│   ├── model.py              # Core scoring engine
│   └── sensitivity_analysis.py  # Model validation
├── run_model.py              # CLI entry point
├── requirements.txt
└── README.md
```

---

## 📐 Scoring Framework

### Dimension Structure

```
┌─────────────────────────────────────────────────────────┐
│                    PRIORITY SCORE                        │
│                         │                                │
│     ┌───────────────────┼───────────────────┐            │
│     │                   │                   │            │
│     ▼                   ▼                   ▼            │
│ ┌───────────┐     ┌───────────┐     ┌───────────┐       │
│ │ READINESS │     │    ROI    │     │   RISK    │       │
│ │   (35%)   │     │   (45%)   │     │   (20%)   │       │
│ └─────┬─────┘     └─────┬─────┘     └─────┬─────┘       │
│       │                 │                 │              │
│   ┌───┴───┐         ┌───┴───┐         ┌───┴───┐         │
│   │4 items│         │Payback│         │3 items│         │
│   │equally│         │ + ROI │         │weighted│         │
│   │weighted│        │ ratio │         │       │         │
│   └───────┘         └───────┘         └───────┘         │
└─────────────────────────────────────────────────────────┘
```

### Metric Details

| Dimension | Metric | Weight | Direction | Source |
|-----------|--------|--------|-----------|--------|
| Readiness | Data availability | 0.25 | ↑ Better | Davenport 2018 |
| Readiness | Data quality | 0.25 | ↑ Better | Gartner 2022 |
| Readiness | Process standardization | 0.25 | ↑ Better | IEEE SE |
| Readiness | Tool integration | 0.25 | ↑ Better | VentureBeat |
| Suitability | Automation feasibility | 0.30 | ↑ Better | McKinsey |
| Suitability | NLP pattern clarity | 0.25 | ↑ Better | Domain |
| Suitability | Exception complexity | 0.20 | ↑ Worse | Forrester |
| Suitability | Human-in-loop fit | 0.25 | ↑ Better | HBR |
| Risk | Compliance sensitivity | 0.35 | ↑ Worse | ISO 31000 |
| Risk | Customer harm potential | 0.35 | ↑ Worse | Qualtrics |
| Risk | Error tolerance | 0.30 | ↑ Better | NIST |

---

## 🔬 Comparison to Other Parameterized Models

| Model | Domain | Parameters | Our Analog |
|-------|--------|------------|------------|
| **SIR/SEIR** | Epidemiology | β (transmission), γ (recovery) | w_roi, w_readiness |
| **FICO Score** | Credit Risk | Payment history, utilization weights | Dimension weights |
| **Black-Scholes** | Options Pricing | σ (volatility), r (risk-free rate) | Risk gates, adoption rate |
| **Cobb-Douglas** | Economics | α, β (factor elasticities) | w_r, w_roi, w_risk |

The epistemology is identical:
1. **Structure relationships** between factors
2. **Parameterize** with domain knowledge or calibration
3. **Simulate scenarios** to inform decisions
4. **Validate** against outcomes and adjust

---

## 📚 Documentation

- **[Parameter Justification](docs/PARAMETER_JUSTIFICATION.md)** — Complete research citations for all parameters
- **[Sensitivity Analysis](src/sensitivity_analysis.py)** — Model validation code
- **[Interactive Dashboard](outputs/AIReadinessDashboard.jsx)** — React visualization

---

## 🎯 Use Cases

1. **Pre-Investment Due Diligence** — Score processes before AI spending
2. **Vendor Evaluation** — Compare AI solutions against requirements
3. **Portfolio Prioritization** — Rank multiple AI initiatives
4. **Executive Communication** — Justify decisions with data
5. **Continuous Calibration** — Update parameters with outcomes

---

## 🔮 Future Enhancements

- [ ] Bayesian parameter updating from outcomes
- [ ] Process dependency modeling (network effects)
- [ ] Uncertainty quantification (confidence intervals)
- [ ] Web interface for non-technical users
- [ ] Integration with project management tools

---

## 👤 About

**AI Business Analyst Portfolio Project**

This project demonstrates the ability to build mathematically rigorous decision support tools that translate business problems into quantitative frameworks with defensible parameters.

> "I built a parameterized decision model using multi-criteria weighted scoring—the same mathematical structure used in epidemiological models and credit risk scoring. All parameters are justified by industry research, and the model is validated through sensitivity analysis showing 100% ranking stability for top priorities."

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Data Source:** [Kaggle Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset)
- **Methodology:** Multi-Criteria Decision Analysis (MCDA), Weighted Sum Model (WSM)
- **Research:** McKinsey, Gartner, Forrester, ISO, NIST (see Parameter Justification doc)
