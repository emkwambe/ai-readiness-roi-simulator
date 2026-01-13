#!/usr/bin/env python3
"""
run_model.py - AI Readiness & ROI Scoring Engine
================================================

Usage:
    python run_model.py --scenario SCN_BASE
    python run_model.py --scenario SCN_COST --company ACME_CORP
    python run_model.py --list-scenarios

This script:
1. Loads all configuration data (ProcessSteps, Metrics, Scores, Params)
2. Computes dimension scores (Readiness, Suitability, Risk)
3. Computes ROI metrics (Savings, Payback, ROI Ratio)
4. Calculates Priority Score with configurable weights and gates
5. Outputs ranked recommendations to CSV

The system is parameterized: change BusinessParams or StrategyParams
to run different scenarios without code changes.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.io import load_all_data, get_scenario_params
from src.model import (
    compute_dimension_score,
    compute_risk_score,
    compute_roi_fields,
    compute_roi_score,
    compute_priority_score,
    generate_recommendation
)


DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "outputs"
OUT_DIR.mkdir(exist_ok=True)


def list_scenarios(data: dict) -> None:
    """Print available scenarios"""
    print("\n📋 Available Scenarios:")
    print("-" * 60)
    
    biz = data['business_params']
    strat = data['strategy_params']
    
    for _, row in biz.iterrows():
        sid = row['scenario_id']
        srow = strat[strat['scenario_id'] == sid].iloc[0] if sid in strat['scenario_id'].values else None
        
        print(f"\n  {sid}: {row.get('scenario_name', 'Unnamed')}")
        print(f"    Volume: {row['ticket_volume_monthly']:,.0f} tickets/month")
        print(f"    Agent Cost: ${row['agent_cost_per_hour']}/hour")
        print(f"    Budget: ${row['implementation_budget']:,.0f}")
        if srow is not None:
            print(f"    Weights: Readiness={srow['w_readiness']}, ROI={srow['w_roi']}, Risk={srow['w_risk']}")
            print(f"    Strategy: {srow.get('roi_preference', 'Balanced')}")


def run_scenario(data: dict, scenario_id: str, company_id: str) -> pd.DataFrame:
    """
    Run the scoring model for a specific scenario.
    Returns the final output DataFrame.
    """
    print(f"\n{'='*60}")
    print(f"🚀 Running Scenario: {scenario_id}")
    print(f"{'='*60}")
    
    # Get scenario parameters
    biz_params, strat_params = get_scenario_params(data, scenario_id)
    
    print(f"\n📊 Business Parameters:")
    print(f"   Ticket Volume: {biz_params['ticket_volume_monthly']:,.0f}/month")
    print(f"   Agent Cost: ${biz_params['agent_cost_per_hour']}/hour")
    print(f"   Implementation Budget: ${biz_params['implementation_budget']:,.0f}")
    
    print(f"\n🎯 Strategy Parameters:")
    print(f"   Weights: Readiness={strat_params['w_readiness']}, ROI={strat_params['w_roi']}, Risk={strat_params['w_risk']}")
    print(f"   Gates: Min Readiness={strat_params['min_readiness_gate']}, Max Risk={strat_params['max_risk_gate']}")
    
    # Compute dimension scores
    print(f"\n⚙️  Computing scores...")
    
    readiness_df = compute_dimension_score(
        data['scores'], data['metrics'], 'Readiness'
    )
    
    suitability_df = compute_dimension_score(
        data['scores'], data['metrics'], 'Suitability'
    )
    
    risk_df = compute_risk_score(
        data['scores'], data['metrics']
    )
    
    # Compute ROI fields
    roi_df = compute_roi_fields(data['steps'], biz_params)
    
    roi_df['roi_score_0_100'] = compute_roi_score(
        roi_df['payback_months'],
        roi_df['roi_ratio'],
        target_payback_months=float(strat_params.get('target_payback_months', 12)),
        target_roi_ratio=float(strat_params.get('target_roi_ratio', 2.0))
    )
    
    # Merge all scores
    out = data['steps'][['step_id', 'step_name', 'process_area', 'automation_candidate', 'volume_share']].copy()
    out = out.merge(readiness_df, on='step_id', how='left')
    out = out.merge(suitability_df, on='step_id', how='left')
    out = out.merge(risk_df, on='step_id', how='left')
    out = out.merge(roi_df, on='step_id', how='left')
    
    # Fill NaN scores with defaults
    out['readiness_score_0_100'] = out['readiness_score_0_100'].fillna(0)
    out['suitability_score_0_100'] = out['suitability_score_0_100'].fillna(0)
    out['risk_score_0_100'] = out['risk_score_0_100'].fillna(100)
    out['roi_score_0_100'] = out['roi_score_0_100'].fillna(0)
    
    # Compute Priority Score
    out['priority_score_0_100'] = compute_priority_score(
        readiness=out['readiness_score_0_100'],
        roi=out['roi_score_0_100'],
        risk=out['risk_score_0_100'],
        w_readiness=float(strat_params['w_readiness']),
        w_roi=float(strat_params['w_roi']),
        w_risk=float(strat_params['w_risk']),
        min_readiness_gate=float(strat_params['min_readiness_gate']),
        max_risk_gate=float(strat_params['max_risk_gate'])
    )
    
    # Generate recommendations
    out['recommendation'] = out.apply(generate_recommendation, axis=1)
    
    # Add metadata
    out['scenario_id'] = scenario_id
    out['company_id'] = company_id
    
    # Sort by priority
    out = out.sort_values('priority_score_0_100', ascending=False)
    
    # Round numeric columns for readability
    numeric_cols = [
        'readiness_score_0_100', 'suitability_score_0_100', 'risk_score_0_100',
        'roi_score_0_100', 'priority_score_0_100', 'monthly_savings_est',
        'annual_savings_est', 'implementation_cost_est', 'payback_months', 'roi_ratio'
    ]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = out[col].round(2)
    
    return out


def print_summary(df: pd.DataFrame) -> None:
    """Print a summary of results"""
    print(f"\n{'='*60}")
    print("📊 RESULTS SUMMARY")
    print(f"{'='*60}")
    
    # Top priorities
    print("\n🔥 TOP 5 AUTOMATION PRIORITIES:")
    print("-" * 60)
    top5 = df.head(5)
    for _, row in top5.iterrows():
        print(f"  {row['step_name']}")
        print(f"    Priority: {row['priority_score_0_100']:.0f} | Readiness: {row['readiness_score_0_100']:.0f} | Risk: {row['risk_score_0_100']:.0f}")
        print(f"    Annual Savings: ${row['annual_savings_est']:,.0f} | Payback: {row['payback_months']:.1f} mo")
        print(f"    → {row['recommendation']}")
        print()
    
    # Items gated out
    gated = df[df['priority_score_0_100'] == 0]
    if len(gated) > 0:
        print(f"\n⚠️  GATED OUT ({len(gated)} items):")
        print("-" * 60)
        for _, row in gated.iterrows():
            print(f"  {row['step_name']}: {row['recommendation']}")
    
    # Totals
    priority_items = df[df['priority_score_0_100'] > 0]
    total_savings = priority_items['annual_savings_est'].sum()
    total_impl = priority_items['implementation_cost_est'].sum()
    
    print(f"\n💰 FINANCIAL SUMMARY (Priority Items Only):")
    print("-" * 60)
    print(f"  Total Annual Savings Potential: ${total_savings:,.0f}")
    print(f"  Total Implementation Cost: ${total_impl:,.0f}")
    if total_impl > 0:
        print(f"  Overall ROI Ratio: {total_savings/total_impl:.2f}x")
        print(f"  Aggregate Payback: {total_impl/(total_savings/12):.1f} months")


def main():
    parser = argparse.ArgumentParser(
        description="AI Readiness & ROI Scoring Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_model.py --scenario SCN_BASE
  python run_model.py --scenario SCN_COST --company ACME_CORP
  python run_model.py --list-scenarios
        """
    )
    parser.add_argument("--scenario", help="Scenario ID to run (e.g., SCN_BASE)")
    parser.add_argument("--company", default="DEMO_CO", help="Company ID for output")
    parser.add_argument("--list-scenarios", action="store_true", help="List available scenarios")
    parser.add_argument("--all", action="store_true", help="Run all scenarios")
    
    args = parser.parse_args()
    
    # Load all data
    print("📁 Loading data...")
    data = load_all_data(DATA_DIR)
    print(f"   ✅ Loaded {len(data['steps'])} process steps")
    print(f"   ✅ Loaded {len(data['metrics'])} scoring metrics")
    print(f"   ✅ Loaded {len(data['scores'])} step scores")
    print(f"   ✅ Loaded {len(data['business_params'])} scenarios")
    
    if args.list_scenarios:
        list_scenarios(data)
        return
    
    if args.all:
        # Run all scenarios
        for scenario_id in data['business_params']['scenario_id'].unique():
            result = run_scenario(data, scenario_id, args.company)
            print_summary(result)
            
            # Save output
            out_path = OUT_DIR / f"ModelOutput_{scenario_id}.csv"
            result.to_csv(out_path, index=False)
            print(f"\n✅ Saved: {out_path}")
    
    elif args.scenario:
        result = run_scenario(data, args.scenario, args.company)
        print_summary(result)
        
        # Save output
        out_path = OUT_DIR / f"ModelOutput_{args.scenario}.csv"
        result.to_csv(out_path, index=False)
        print(f"\n✅ Saved: {out_path}")
    
    else:
        parser.print_help()
        print("\n⚠️  Please specify --scenario or --list-scenarios")


if __name__ == "__main__":
    main()
