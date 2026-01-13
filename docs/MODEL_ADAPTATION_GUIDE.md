# Model Adaptation Guide

## How to Apply This Framework to Any Business Context

This guide explains how to reuse the AI Readiness & ROI Simulator with different datasets, industries, and business problems. The model is designed to be **context-agnostic**—the mathematical structure stays the same, but parameters and data adapt to your situation.

---

## 1. Model Architecture: What's Fixed vs. Customizable

### 🔒 FIXED (Don't Change)

These are the mathematical foundations—changing them would break the model's validity:

| Component | Why It's Fixed |
|-----------|----------------|
| **Scoring formula** | `Score = 100 × Σ(norm × weight) / Σweight` is standard MCDA |
| **Normalization** | `(score - min) / (max - min)` is mathematically necessary |
| **Gate logic** | Non-compensatory thresholds are risk management best practice |
| **Priority formula** | Weighted sum with gates is well-validated |
| **Sensitivity analysis** | Monte Carlo + weight sensitivity are standard validation |

### 🔧 CUSTOMIZABLE (Must Adapt)

These change based on your specific context:

| Component | What to Customize | How to Customize |
|-----------|-------------------|------------------|
| **Process Steps** | The things you're evaluating | Replace with your workflow/products/projects |
| **Metrics** | What you measure | Add/remove based on your decision criteria |
| **Metric Weights** | Relative importance | Adjust based on domain research or expert input |
| **Dimension Weights** | Strategy emphasis | Adjust based on organizational priorities |
| **Gates** | Risk tolerance | Tighten (conservative) or loosen (aggressive) |
| **Business Params** | Economics | Your actual costs, volumes, budgets |
| **Scoring Assessments** | Raw scores | Your evaluation of each item against each metric |

---

## 2. Universal Applicability: Where This Model Works

### The Model Fits Any "Prioritization Under Uncertainty" Problem

```
IF you need to:
  - Evaluate multiple OPTIONS
  - Against multiple CRITERIA
  - With different STAKEHOLDER PRIORITIES
  - Under RESOURCE CONSTRAINTS
  - With some options being TOO RISKY

THEN this model applies.
```

### ✅ Excellent Fit (High Confidence)

| Domain | Use Case | Process Steps Would Be |
|--------|----------|----------------------|
| **IT/Operations** | AI/Automation prioritization | Workflows, processes, tasks |
| **IT/Operations** | Technical debt prioritization | Systems, codebases, integrations |
| **IT/Operations** | Vendor/tool selection | Software options, platforms |
| **Product** | Feature prioritization | Feature backlog items |
| **Product** | Market expansion | Geographic markets, segments |
| **Finance** | Investment portfolio | Investment opportunities |
| **Finance** | Cost reduction initiatives | Expense categories, departments |
| **HR** | Training program ROI | Training modules, skills |
| **Marketing** | Channel prioritization | Marketing channels, campaigns |
| **Supply Chain** | Supplier evaluation | Vendors, partners |
| **Healthcare** | Treatment protocol selection | Treatment options |
| **Real Estate** | Property/site selection | Locations, properties |
| **M&A** | Acquisition target scoring | Target companies |

### ⚠️ Moderate Fit (Needs Adaptation)

| Domain | Challenge | Adaptation Needed |
|--------|-----------|-------------------|
| **R&D** | High uncertainty | Add uncertainty dimension, wider confidence intervals |
| **Creative** | Subjective outcomes | Define measurable proxies for "quality" |
| **Regulatory** | Binary compliance | May need pass/fail gates rather than scores |

### ❌ Poor Fit (Use Different Model)

| Domain | Why Not | Better Alternative |
|--------|---------|-------------------|
| **Real-time decisions** | Too slow | Rule engines, ML classifiers |
| **Single criterion** | Overkill | Simple ranking |
| **No resource constraints** | No tradeoffs | Do everything |
| **Highly interdependent options** | Assumes independence | Network/graph models |

---

## 3. Step-by-Step Adaptation Process

### Phase 1: Define Your Decision Context (2-4 hours)

**Step 1.1: Identify What You're Prioritizing**

Ask: "What are the OPTIONS I need to rank?"

| Your Context | Options Are |
|--------------|-------------|
| AI readiness audit | Process steps / workflows |
| Feature prioritization | Product features |
| Vendor selection | Vendor options |
| Market expansion | Geographic markets |
| Investment decisions | Investment opportunities |

**Step 1.2: Identify Your Stakeholders' Priorities**

Ask: "What do decision-makers CARE about?"

Common priority dimensions (pick 3-5):
- Financial return (ROI, payback, NPV)
- Feasibility (readiness, capability, resources)
- Risk (compliance, reputation, operational)
- Strategic fit (alignment, synergy, timing)
- Customer impact (satisfaction, retention, growth)
- Competitive advantage (differentiation, moat)

**Step 1.3: Identify Your Constraints**

Ask: "What would make an option UNACCEPTABLE regardless of benefits?"

These become your GATES:
- Minimum feasibility threshold
- Maximum risk tolerance
- Budget ceiling
- Timeline requirements
- Regulatory requirements

---

### Phase 2: Design Your Scoring Framework (4-8 hours)

**Step 2.1: Define Dimensions**

Map stakeholder priorities to 3-5 scoring dimensions:

```
EXAMPLE: Feature Prioritization

Dimension 1: VALUE (40%)
  - Revenue potential
  - Customer demand
  - Competitive necessity

Dimension 2: FEASIBILITY (35%)
  - Technical complexity
  - Resource availability
  - Dependencies

Dimension 3: RISK (25%)
  - Technical risk
  - Market risk
  - Cannibalization risk
```

**Step 2.2: Define Metrics Within Each Dimension**

For each dimension, identify 3-5 measurable metrics:

```
EXAMPLE: VALUE Dimension

Metric 1: Revenue potential (weight: 0.40)
  Definition: Expected annual revenue if shipped
  Scale: 1 = <$100K, 5 = >$1M
  Direction: Higher is better

Metric 2: Customer demand (weight: 0.35)
  Definition: % of customers requesting feature
  Scale: 1 = <5%, 5 = >30%
  Direction: Higher is better

Metric 3: Competitive necessity (weight: 0.25)
  Definition: How many competitors have this?
  Scale: 1 = None, 5 = All major competitors
  Direction: Higher is worse (we're behind)
```

**Step 2.3: Justify Your Weights**

For each weight, document WHY:

| Weight | Justification Approach |
|--------|----------------------|
| **Equal weights** | "No strong prior; all criteria matter equally" |
| **Expert elicitation** | "Based on interviews with 5 product managers" |
| **Historical data** | "Regression on past project success rates" |
| **Industry research** | "McKinsey recommends 40% weight on X for this domain" |
| **Stakeholder vote** | "Leadership ranked priorities; converted to weights" |

---

### Phase 3: Prepare Your Data (4-8 hours)

**Step 3.1: Create ProcessSteps.csv**

List all options you're evaluating:

```csv
step_id,step_name,category,description,owner,volume_or_size,current_state
S01,Feature A,Core,User authentication redesign,Team Alpha,Large,In backlog
S02,Feature B,Growth,Referral program,Team Beta,Medium,Researching
...
```

**Step 3.2: Create ScoringMetrics.csv**

Define your measurement framework:

```csv
metric_id,dimension,metric_name,metric_definition,scale_min,scale_max,direction,weight
M01,Value,Revenue potential,Expected annual revenue if shipped,1,5,HigherBetter,0.40
M02,Value,Customer demand,Percent of customers requesting,1,5,HigherBetter,0.35
...
```

**Step 3.3: Create StepScores.csv**

Score each option against each metric:

```csv
step_id,metric_id,score,scored_by,scored_date,rationale
S01,M01,4,Product Manager,2025-01-15,Market research shows $500K-$1M potential
S01,M02,5,Product Manager,2025-01-15,Top requested feature (35% of feedback)
...
```

**Step 3.4: Create BusinessParams.csv**

Define your scenarios:

```csv
scenario_id,scenario_name,budget,timeline_months,team_capacity,strategic_priority
SCN_Q1,Q1 Planning,500000,3,20,Growth
SCN_CONS,Conservative,300000,6,15,Stability
```

---

### Phase 4: Calibrate and Validate (2-4 hours)

**Step 4.1: Run Baseline Model**

```bash
python run_model.py --scenario SCN_BASE
```

**Step 4.2: Sanity Check Results**

Ask domain experts:
- "Does the #1 priority make sense?"
- "Are the gated items appropriately excluded?"
- "Any surprises in the ranking?"

**Step 4.3: Run Sensitivity Analysis**

```bash
python src/sensitivity_analysis.py
```

Check:
- Are top 3 priorities stable across weight schemes?
- Do gates filter appropriately?
- Is the model robust to ±20% parameter uncertainty?

**Step 4.4: Iterate If Needed**

| Problem | Solution |
|---------|----------|
| Rankings don't match intuition | Review metric definitions or weights |
| Too many items gated | Loosen gates |
| Not enough differentiation | Add discriminating metrics |
| Results too sensitive | Consider equal weights (more robust) |

---

## 4. Industry-Specific Adaptation Examples

### Example A: SaaS Feature Prioritization

**Context:** B2B SaaS company with 50 features in backlog

**Dimensions:**
| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Customer Value | 0.40 | Revenue-driven company |
| Feasibility | 0.35 | Engineering constrained |
| Risk | 0.25 | Enterprise customers need stability |

**Metrics:**
```
CUSTOMER VALUE (40%)
├── ARR impact potential (0.35)
├── Churn reduction potential (0.30)
├── Expansion revenue potential (0.20)
└── Competitive necessity (0.15)

FEASIBILITY (35%)
├── Engineering complexity (0.30)
├── Dependencies resolved (0.25)
├── Team expertise (0.25)
└── Infrastructure readiness (0.20)

RISK (25%)
├── Technical risk (0.35)
├── Customer disruption risk (0.35)
└── Security/compliance risk (0.30)
```

**Gates:**
- min_feasibility = 40 (don't commit to infeasible features)
- max_risk = 70 (enterprise customers need stability)

**Data Source:**
- Customer feedback surveys
- Sales team input on competitive gaps
- Engineering estimates
- Security review scores

---

### Example B: Marketing Channel Prioritization

**Context:** E-commerce company allocating $2M marketing budget

**Dimensions:**
| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| ROI Potential | 0.50 | Performance marketing focus |
| Scalability | 0.30 | Need to grow 3x |
| Brand Safety | 0.20 | Reputation matters |

**Metrics:**
```
ROI POTENTIAL (50%)
├── Historical ROAS (0.40)
├── CAC efficiency (0.35)
└── Attribution confidence (0.25)

SCALABILITY (30%)
├── Audience size remaining (0.40)
├── Bid inflation trend (0.30)
└── Creative refresh capacity (0.30)

BRAND SAFETY (20%)
├── Platform brand safety score (0.40)
├── Audience quality (0.35)
└── Fraud risk (0.25)
```

**Gates:**
- min_roi = 50 (don't invest in unprofitable channels)
- max_brand_risk = 60 (protect brand reputation)

**Data Source:**
- Analytics platform data
- Attribution modeling
- Brand lift studies
- Third-party brand safety audits

---

### Example C: Technical Debt Prioritization

**Context:** Engineering team with 100+ tech debt items

**Dimensions:**
| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Business Impact | 0.35 | Must show value to stakeholders |
| Technical Urgency | 0.40 | Prevent cascading failures |
| Effort Efficiency | 0.25 | Limited engineering time |

**Metrics:**
```
BUSINESS IMPACT (35%)
├── Customer-facing incidents/month (0.40)
├── Developer productivity loss (0.35)
└── Revenue at risk (0.25)

TECHNICAL URGENCY (40%)
├── Failure probability (0.35)
├── Blast radius if fails (0.30)
├── Dependency on deprecated tech (0.20)
└── Security vulnerability score (0.15)

EFFORT EFFICIENCY (25%)
├── Estimated person-weeks (0.40) [inverted]
├── Team familiarity (0.30)
└── Parallelizable work (0.30)
```

**Gates:**
- min_urgency = 30 (focus on urgent items first)
- max_effort = 80 (avoid massive multi-quarter projects)

**Data Source:**
- Incident tracking system
- Developer surveys
- Static analysis tools
- Security scanners

---

### Example D: Vendor Selection

**Context:** Selecting CRM vendor from 8 options

**Dimensions:**
| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Capability Fit | 0.40 | Must meet requirements |
| Total Cost | 0.30 | Budget constrained |
| Risk | 0.30 | Mission-critical system |

**Metrics:**
```
CAPABILITY FIT (40%)
├── Feature requirement coverage (0.40)
├── Integration capabilities (0.30)
├── Customization flexibility (0.30)

TOTAL COST (30%)
├── 3-year TCO (0.50)
├── Implementation cost (0.30)
└── Training/change management (0.20)

RISK (30%)
├── Vendor stability (0.35)
├── Data portability (0.25)
├── Security certifications (0.25)
└── Reference customer satisfaction (0.15)
```

**Gates:**
- min_capability = 60 (must meet core requirements)
- max_risk = 65 (mission-critical system)

**Data Source:**
- RFP responses
- Vendor demos
- Reference calls
- Analyst reports (Gartner, Forrester)

---

## 5. Data Requirements Checklist

### Minimum Viable Dataset

| File | Minimum Rows | Required Columns |
|------|--------------|------------------|
| ProcessSteps.csv | 5+ options | step_id, step_name, category |
| ScoringMetrics.csv | 6+ metrics | metric_id, dimension, weight, direction |
| StepScores.csv | steps × metrics | step_id, metric_id, score |
| BusinessParams.csv | 1+ scenarios | scenario_id, key economics |
| StrategyParams.csv | 1+ scenarios | scenario_id, weights, gates |

### Data Quality Requirements

| Requirement | Why It Matters | How to Check |
|-------------|----------------|--------------|
| **Complete scoring** | Missing scores break calculations | No nulls in StepScores |
| **Consistent scales** | Scores must be comparable | All scores 1-5 (or your scale) |
| **Weight normalization** | Must sum to 1.0 per dimension | Sum(weights) = 1.0 |
| **Reasonable variation** | All 5s or all 1s = no differentiation | Std dev > 0.5 per metric |
| **Expert consensus** | Single-scorer bias | Multiple scorers, average |

### Red Flags in Your Data

| Red Flag | Problem | Solution |
|----------|---------|----------|
| All scores are 4 or 5 | Scoring inflation | Recalibrate, force distribution |
| One item dominates | Metric may be biased | Check metric weights |
| No items pass gates | Gates too strict | Loosen thresholds |
| All items pass gates | Gates too loose | Tighten thresholds |
| Rankings change wildly | High sensitivity | Use equal weights |

---

## 6. Common Adaptation Mistakes

### ❌ Mistake 1: Too Many Metrics

**Problem:** 30 metrics = scoring fatigue, noise dominates signal

**Solution:** 8-15 metrics is optimal. Ask: "Would this metric CHANGE my decision?"

### ❌ Mistake 2: Correlated Metrics

**Problem:** "Revenue" and "Profit" are correlated → double-counting

**Solution:** Pick one or combine into single metric

### ❌ Mistake 3: Unmeasurable Metrics

**Problem:** "Strategic alignment" with no clear definition

**Solution:** Define observable proxy: "Mentioned in CEO's top 3 priorities? Y/N"

### ❌ Mistake 4: Ignoring Stakeholder Buy-in

**Problem:** Model says X, leadership wants Y

**Solution:** Involve stakeholders in weight selection; sensitivity analysis shows their weights' impact

### ❌ Mistake 5: Skipping Validation

**Problem:** Model may have errors or bias

**Solution:** Always run sensitivity analysis; check face validity with experts

---

## 7. Quick Start Template

For rapid deployment, copy and modify these files:

### ProcessSteps_TEMPLATE.csv
```csv
step_id,step_name,category,description,owner
S01,[Your Option 1],[Category],[Description],[Owner]
S02,[Your Option 2],[Category],[Description],[Owner]
S03,[Your Option 3],[Category],[Description],[Owner]
```

### ScoringMetrics_TEMPLATE.csv
```csv
metric_id,dimension,metric_name,metric_definition,scale_min,scale_max,direction,weight
M01,Value,[Metric 1],[Definition],1,5,HigherBetter,0.35
M02,Value,[Metric 2],[Definition],1,5,HigherBetter,0.35
M03,Value,[Metric 3],[Definition],1,5,HigherWorse,0.30
M04,Feasibility,[Metric 4],[Definition],1,5,HigherBetter,0.50
M05,Feasibility,[Metric 5],[Definition],1,5,HigherBetter,0.50
M06,Risk,[Metric 6],[Definition],1,5,HigherWorse,0.50
M07,Risk,[Metric 7],[Definition],1,5,HigherBetter,0.50
```

### BusinessParams_TEMPLATE.csv
```csv
scenario_id,scenario_name,budget,timeline_months,key_constraint
SCN_BASE,Baseline,100000,12,None
SCN_AGGR,Aggressive,150000,6,Speed
SCN_CONS,Conservative,75000,18,Budget
```

### StrategyParams_TEMPLATE.csv
```csv
scenario_id,w_value,w_feasibility,w_risk,min_feasibility_gate,max_risk_gate
SCN_BASE,0.40,0.35,0.25,50,70
SCN_AGGR,0.50,0.30,0.20,40,75
SCN_CONS,0.30,0.40,0.30,60,60
```

---

## 8. Calibration Over Time

### The Feedback Loop

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌──────────┐  │
│  │ Run Model   │────▶│ Implement   │────▶│ Measure  │  │
│  │ Get Rankings│     │ Top Items   │     │ Outcomes │  │
│  └─────────────┘     └─────────────┘     └────┬─────┘  │
│         ▲                                      │        │
│         │                                      │        │
│         │            ┌─────────────┐           │        │
│         └────────────│ Calibrate   │◀──────────┘        │
│                      │ Parameters  │                    │
│                      └─────────────┘                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### What to Track

| Predicted | Actual | Calibration Action |
|-----------|--------|-------------------|
| High priority, High outcome | ✅ Model working | No change |
| High priority, Low outcome | ⚠️ False positive | Increase risk weight or add metrics |
| Low priority, High outcome | ⚠️ False negative | Review feasibility scoring |
| Low priority, Low outcome | ✅ Model working | No change |

### When to Recalibrate

| Trigger | Action |
|---------|--------|
| 3+ false positives | Review metrics and weights |
| New strategic priorities | Adjust dimension weights |
| Significant cost changes | Update business params |
| New risk factors emerge | Add risk metrics |
| Annual planning cycle | Full model review |

---

## Summary: The 80/20 of Adaptation

**If you remember nothing else:**

1. **Keep the math** — Weighted scoring + gates works universally
2. **Change the metrics** — Define what matters in YOUR context
3. **Justify weights** — Document WHY each weight was chosen
4. **Validate always** — Run sensitivity analysis before trusting results
5. **Iterate with outcomes** — Calibrate parameters based on real results

**Time Investment by Phase:**

| Phase | Hours | Output |
|-------|-------|--------|
| Define context | 2-4 | Clear problem statement |
| Design framework | 4-8 | Metrics and weights |
| Prepare data | 4-8 | Populated CSV files |
| Calibrate & validate | 2-4 | Validated model |
| **Total** | **12-24** | **Production-ready model** |

---

*This guide is part of the AI Readiness & ROI Simulator project.*
*See README.md for model documentation and PARAMETER_JUSTIFICATION.md for research citations.*
