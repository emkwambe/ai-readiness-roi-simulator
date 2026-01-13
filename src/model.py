"""
src/model.py - AI Readiness Scoring Engine
==========================================
Core computation logic for:
- Dimension scores (Readiness, Suitability, Risk)
- ROI calculations
- Priority scoring with gates

All formulas are documented and defensible for executive presentation.
"""

from __future__ import annotations
import numpy as np
import pandas as pd

# Score normalization constants
SCALE_MIN = 1
SCALE_MAX = 5


def normalize_score(score: pd.Series) -> pd.Series:
    """
    Normalize score from 1-5 scale to 0-1 scale.
    
    Formula: normalized = (score - 1) / (5 - 1)
    """
    return (score - SCALE_MIN) / (SCALE_MAX - SCALE_MIN)


def compute_dimension_score(
    step_scores: pd.DataFrame,
    metrics: pd.DataFrame,
    dimension: str
) -> pd.DataFrame:
    """
    Compute weighted score for a dimension (Readiness, Suitability).
    
    For "goodness" dimensions, higher raw scores = higher output.
    
    Formula: dimension_score = 100 × Σ(normalized_score × weight) / Σ(weight)
    
    Returns DataFrame with step_id and {dimension}_score_0_100
    """
    # Filter metrics for this dimension
    dim_metrics = metrics[metrics['dimension'] == dimension].copy()
    
    # Join scores with metric weights
    scored = step_scores.merge(dim_metrics[['metric_id', 'weight', 'direction']], 
                               on='metric_id', how='inner')
    
    # Normalize scores to 0-1
    scored['norm'] = normalize_score(scored['score'].astype(float)).clip(0, 1)
    
    # Handle direction: for HigherWorse, invert to represent "goodness"
    is_higher_worse = scored['direction'].str.lower() == 'higherworse'
    scored.loc[is_higher_worse, 'norm'] = 1 - scored.loc[is_higher_worse, 'norm']
    
    # Compute weighted average per step
    scored['weight'] = scored['weight'].astype(float)
    scored['weighted_score'] = scored['norm'] * scored['weight']
    
    agg = scored.groupby('step_id').agg({
        'weighted_score': 'sum',
        'weight': 'sum'
    }).reset_index()
    
    agg[f'{dimension.lower()}_score_0_100'] = 100.0 * agg['weighted_score'] / agg['weight'].clip(lower=1e-9)
    
    return agg[['step_id', f'{dimension.lower()}_score_0_100']]


def compute_risk_score(
    step_scores: pd.DataFrame,
    metrics: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute Risk score where HIGHER = MORE RISK (worse).
    
    For risk metrics:
    - HigherWorse: keep as-is (high score = high risk)
    - HigherBetter: invert (high score = low risk, so 1-norm = high risk)
    
    Returns DataFrame with step_id and risk_score_0_100
    """
    # Filter metrics for Risk dimension
    risk_metrics = metrics[metrics['dimension'] == 'Risk'].copy()
    
    # Join scores with metric weights
    scored = step_scores.merge(risk_metrics[['metric_id', 'weight', 'direction']], 
                               on='metric_id', how='inner')
    
    # Normalize to 0-1
    scored['norm'] = normalize_score(scored['score'].astype(float)).clip(0, 1)
    
    # For Risk, we want higher output = worse
    # HigherWorse metrics: keep norm as-is (high input = high risk output)
    # HigherBetter metrics: invert (high input = low risk, so 1-norm = high risk)
    is_higher_better = scored['direction'].str.lower() == 'higherbetter'
    scored.loc[is_higher_better, 'norm'] = 1 - scored.loc[is_higher_better, 'norm']
    
    # Compute weighted average
    scored['weight'] = scored['weight'].astype(float)
    scored['weighted_score'] = scored['norm'] * scored['weight']
    
    agg = scored.groupby('step_id').agg({
        'weighted_score': 'sum',
        'weight': 'sum'
    }).reset_index()
    
    agg['risk_score_0_100'] = 100.0 * agg['weighted_score'] / agg['weight'].clip(lower=1e-9)
    
    return agg[['step_id', 'risk_score_0_100']]


def compute_roi_fields(
    steps: pd.DataFrame,
    biz_params: pd.Series,
    automation_rates: dict = None
) -> pd.DataFrame:
    """
    Compute ROI-related fields for each step.
    
    Calculations:
    - Monthly manual cost = volume × AHT × cost_per_hour × overhead
    - Monthly savings = manual_cost × automation_shift_rate × adoption_rate
    - Payback months = implementation_cost / monthly_savings
    - ROI ratio = annual_savings / implementation_cost
    
    Returns DataFrame with ROI fields per step_id
    """
    df = steps.copy()
    
    # Extract business parameters
    ticket_volume = float(biz_params['ticket_volume_monthly'])
    cost_per_hour = float(biz_params['agent_cost_per_hour'])
    overhead = float(biz_params.get('overhead_multiplier', 1.15))
    peak = float(biz_params.get('peak_multiplier', 1.0))
    base_impl_cost = float(biz_params.get('base_implementation_cost', 25000))
    adoption_rate = float(biz_params.get('automation_adoption_rate', 0.80))
    
    # Calculate monthly volume per step
    df['monthly_volume'] = ticket_volume * df['volume_share'].astype(float) * peak
    
    # Convert handle time to hours
    df['aht_hours'] = df['avg_handle_time_min'].astype(float) / 60.0
    
    # Monthly manual cost
    df['monthly_manual_cost'] = (
        df['monthly_volume'] * df['aht_hours'] * cost_per_hour * overhead
    )
    
    # Automation shift rates based on candidate type
    if automation_rates is None:
        automation_rates = {
            'Full': 0.70,      # 70% of work can shift to AI
            'Partial': 0.40,  # 40% shift
            'Assist': 0.20    # 20% shift (AI helps, human does most)
        }
    
    df['base_shift_rate'] = df['automation_candidate'].map(automation_rates).fillna(0.30)
    df['effective_shift_rate'] = (df['base_shift_rate'] * adoption_rate).clip(0, 1)
    
    # Monthly savings estimate
    df['monthly_savings_est'] = df['monthly_manual_cost'] * df['effective_shift_rate']
    df['annual_savings_est'] = df['monthly_savings_est'] * 12.0
    
    # Implementation cost estimate (proportional to complexity)
    # Higher shift rate = more complex implementation
    df['implementation_cost_est'] = base_impl_cost * (0.5 + 0.8 * df['effective_shift_rate'])
    
    # Payback and ROI
    df['payback_months'] = np.where(
        df['monthly_savings_est'] > 0,
        df['implementation_cost_est'] / df['monthly_savings_est'],
        np.inf
    )
    
    df['roi_ratio'] = np.where(
        df['implementation_cost_est'] > 0,
        df['annual_savings_est'] / df['implementation_cost_est'],
        0.0
    )
    
    return df[[
        'step_id', 
        'monthly_volume',
        'monthly_manual_cost',
        'monthly_savings_est',
        'annual_savings_est',
        'implementation_cost_est',
        'payback_months',
        'roi_ratio'
    ]]


def compute_roi_score(
    payback_months: pd.Series,
    roi_ratio: pd.Series,
    target_payback_months: float = 12.0,
    target_roi_ratio: float = 2.0
) -> pd.Series:
    """
    Compute ROI score (0-100) based on payback and ROI ratio.
    
    Formula:
    - PaybackScore = 100 × min(1, target_payback / actual_payback)
    - ROIRatioScore = 100 × min(1, actual_ratio / target_ratio)
    - ROI_score = 0.6 × PaybackScore + 0.4 × ROIRatioScore
    """
    # Payback score: faster payback = higher score
    payback_score = 100.0 * np.clip(
        target_payback_months / payback_months.replace(0, np.nan), 
        0, 1
    )
    payback_score = payback_score.fillna(0)
    
    # ROI ratio score: higher ratio = higher score
    roi_ratio_score = 100.0 * np.clip(
        roi_ratio / target_roi_ratio, 
        0, 1
    )
    roi_ratio_score = roi_ratio_score.fillna(0)
    
    # Weighted combination
    return 0.6 * payback_score + 0.4 * roi_ratio_score


def compute_priority_score(
    readiness: pd.Series,
    roi: pd.Series,
    risk: pd.Series,
    w_readiness: float,
    w_roi: float,
    w_risk: float,
    min_readiness_gate: float,
    max_risk_gate: float
) -> pd.Series:
    """
    Compute final Priority Score with gates.
    
    Gates: If readiness < min_gate OR risk > max_gate, score = 0
    
    Formula:
    Priority = GateFactor × (w_r × Readiness + w_roi × ROI + w_risk × (100 - Risk))
    
    Note: (100 - Risk) converts risk to "safety" so higher is better
    """
    # Apply gates
    gate_passed = (readiness >= min_readiness_gate) & (risk <= max_risk_gate)
    
    # Base score calculation
    # Convert risk to "safety" by subtracting from 100
    safety = 100.0 - risk
    
    base_score = (
        w_readiness * readiness + 
        w_roi * roi + 
        w_risk * safety
    )
    
    # Apply gate: zero out items that don't pass
    return np.where(gate_passed, base_score, 0.0)


def generate_recommendation(row: pd.Series) -> str:
    """
    Generate a text recommendation based on scores.
    """
    priority = row.get('priority_score_0_100', 0)
    readiness = row.get('readiness_score_0_100', 0)
    risk = row.get('risk_score_0_100', 0)
    roi = row.get('roi_score_0_100', 0)
    
    if priority == 0:
        if readiness < 50:
            return "NOT READY - Improve data/process standardization first"
        else:
            return "HIGH RISK - Keep human-operated, monitor for changes"
    
    if priority >= 70:
        if risk < 40:
            return "PRIORITY 1 - Strong candidate for full automation"
        else:
            return "PRIORITY 1 - Implement with human-in-loop safeguards"
    elif priority >= 50:
        return "PRIORITY 2 - Good candidate for AI-assisted workflow"
    elif priority >= 30:
        return "PRIORITY 3 - Consider for Phase 2 implementation"
    else:
        return "LOW PRIORITY - Defer or keep manual"
