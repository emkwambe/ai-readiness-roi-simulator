"""
src/io.py - Data loading and validation utilities
=================================================
Handles loading CSV files and validating required columns.
Designed to be migration-ready for future database backend.
"""

from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import List


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV file and return as DataFrame"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path)


def ensure_cols(df: pd.DataFrame, required: List[str], name: str) -> None:
    """Validate that DataFrame has required columns"""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def load_all_data(data_dir: Path) -> dict:
    """
    Load all configuration files from data directory.
    Returns dict with all DataFrames.
    """
    data = {}
    
    # Load each file with validation
    data['steps'] = load_csv(data_dir / "ProcessSteps.csv")
    ensure_cols(data['steps'], [
        'step_id', 'step_name', 'volume_share', 
        'avg_handle_time_min', 'automation_candidate'
    ], "ProcessSteps")
    
    data['metrics'] = load_csv(data_dir / "ScoringMetrics.csv")
    ensure_cols(data['metrics'], [
        'metric_id', 'dimension', 'metric_name', 
        'weight', 'direction'
    ], "ScoringMetrics")
    
    data['scores'] = load_csv(data_dir / "StepScores.csv")
    ensure_cols(data['scores'], [
        'step_id', 'metric_id', 'score'
    ], "StepScores")
    
    data['business_params'] = load_csv(data_dir / "BusinessParams.csv")
    ensure_cols(data['business_params'], [
        'scenario_id', 'ticket_volume_monthly', 
        'agent_cost_per_hour', 'implementation_budget'
    ], "BusinessParams")
    
    data['strategy_params'] = load_csv(data_dir / "StrategyParams.csv")
    ensure_cols(data['strategy_params'], [
        'scenario_id', 'w_readiness', 'w_roi', 'w_risk',
        'min_readiness_gate', 'max_risk_gate'
    ], "StrategyParams")
    
    return data


def get_scenario_params(data: dict, scenario_id: str) -> tuple:
    """
    Get business and strategy parameters for a specific scenario.
    Returns (business_params_row, strategy_params_row)
    """
    biz = data['business_params']
    strat = data['strategy_params']
    
    biz_row = biz[biz['scenario_id'] == scenario_id]
    if len(biz_row) == 0:
        raise ValueError(f"Scenario '{scenario_id}' not found in BusinessParams")
    biz_row = biz_row.iloc[0]
    
    strat_row = strat[strat['scenario_id'] == scenario_id]
    if len(strat_row) == 0:
        raise ValueError(f"Scenario '{scenario_id}' not found in StrategyParams")
    strat_row = strat_row.iloc[0]
    
    return biz_row, strat_row
