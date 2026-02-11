#!/usr/bin/env python3
"""
visualize_model.py - Comprehensive Visualization Suite
=======================================================

Professional visualizations for the AI Readiness & ROI Model
Generates publication-quality figures using matplotlib and plotly.

Run: python visualize_model.py
Output: Saves figures to outputs/figures/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

# Try to import plotly for interactive charts
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Note: Install plotly for interactive visualizations: pip install plotly")

from pathlib import Path
import sys

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.io import load_all_data, get_scenario_params
from src.model import (
    compute_dimension_score, compute_risk_score,
    compute_roi_fields, compute_roi_score, compute_priority_score
)

# Style configuration
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {
    'primary': '#2563eb',
    'secondary': '#7c3aed', 
    'success': '#16a34a',
    'warning': '#eab308',
    'danger': '#dc2626',
    'gray': '#6b7280'
}

def load_model_results(data_dir):
    """Load data and compute all scores"""
    data = load_all_data(data_dir)
    biz_params, strat_params = get_scenario_params(data, 'SCN_BASE')
    
    # Compute scores
    readiness = compute_dimension_score(data['scores'], data['metrics'], 'Readiness')
    suitability = compute_dimension_score(data['scores'], data['metrics'], 'Suitability')
    risk = compute_risk_score(data['scores'], data['metrics'])
    roi_df = compute_roi_fields(data['steps'], biz_params)
    roi_df['roi_score'] = compute_roi_score(roi_df['payback_months'], roi_df['roi_ratio'], 12, 2.0)
    
    # Merge all
    results = data['steps'][['step_id', 'step_name', 'process_area', 'automation_candidate']].copy()
    results = results.rename(columns={'process_area': 'category', 'automation_candidate': 'automation_type'})
    results = results.merge(readiness, on='step_id', how='left')
    results = results.merge(risk, on='step_id', how='left')
    results = results.merge(roi_df[['step_id', 'roi_score', 'annual_savings_est', 'payback_months']], on='step_id', how='left')
    results = results.merge(suitability, on='step_id', how='left')
    results = results.rename(columns={'suitability_score_0_100': 'suitability_score'})
    
    # Compute priority
    results['priority_score'] = compute_priority_score(
        results['readiness_score_0_100'].fillna(0),
        results['roi_score'].fillna(0),
        results['risk_score_0_100'].fillna(100),
        w_readiness=strat_params['w_readiness'],
        w_roi=strat_params['w_roi'],
        w_risk=strat_params['w_risk'],
        min_readiness_gate=strat_params['min_readiness_gate'],
        max_risk_gate=strat_params['max_risk_gate']
    )
    
    results['gated'] = results['priority_score'] == 0
    
    return results.sort_values('priority_score', ascending=False)


# =============================================================================
# MATPLOTLIB VISUALIZATIONS
# =============================================================================

def fig1_priority_matrix(results, save_path=None):
    """Bubble chart: Readiness vs ROI, size=savings, color=priority"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Separate gated and non-gated
    active = results[~results['gated']]
    gated = results[results['gated']]
    
    # Plot active items
    scatter = ax.scatter(
        active['readiness_score_0_100'],
        active['roi_score'],
        s=active['annual_savings_est'] / 200,
        c=active['priority_score'],
        cmap='RdYlGn',
        alpha=0.8,
        edgecolors='black',
        linewidths=1,
        vmin=0, vmax=100
    )
    
    # Plot gated items
    ax.scatter(
        gated['readiness_score_0_100'],
        gated['roi_score'],
        s=gated['annual_savings_est'] / 200,
        c='lightgray',
        alpha=0.5,
        edgecolors='red',
        linewidths=2,
        marker='X'
    )
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, label='Priority Score')
    
    # Gate lines
    ax.axvline(x=50, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Min Readiness Gate')
    ax.axhline(y=30, color='orange', linestyle='--', linewidth=1.5, alpha=0.7)
    
    # Labels for top 5
    for _, row in active.head(5).iterrows():
        ax.annotate(
            row['step_name'],
            (row['readiness_score_0_100'], row['roi_score']),
            xytext=(10, 10), textcoords='offset points',
            fontsize=9, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5)
        )
    
    ax.set_xlabel('Readiness Score', fontsize=12, fontweight='bold')
    ax.set_ylabel('ROI Score', fontsize=12, fontweight='bold')
    ax.set_title('AI Readiness Priority Matrix\nBubble Size = Annual Savings | Color = Priority Score', 
                 fontsize=14, fontweight='bold')
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 105)
    ax.legend(loc='lower right')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def fig2_dimension_heatmap(results, save_path=None):
    """Heatmap of dimension scores"""
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # Prepare data
    sorted_results = results.sort_values('priority_score', ascending=True)
    
    data_matrix = sorted_results[['readiness_score_0_100', 'suitability_score', 
                                   'risk_score_0_100', 'priority_score']].values
    
    # Custom colormap
    im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    
    # Labels
    ax.set_yticks(range(len(sorted_results)))
    ax.set_yticklabels(sorted_results['step_name'], fontsize=9)
    ax.set_xticks(range(4))
    ax.set_xticklabels(['Readiness', 'Suitability', 'Risk', 'Priority'], fontsize=10, fontweight='bold')
    
    # Add value annotations
    for i in range(len(sorted_results)):
        for j in range(4):
            val = data_matrix[i, j]
            color = 'white' if val < 50 else 'black'
            ax.text(j, i, f'{val:.0f}', ha='center', va='center', color=color, fontsize=8)
    
    plt.colorbar(im, ax=ax, label='Score (0-100)')
    ax.set_title('Dimension Scores Heatmap\n(Sorted by Priority)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def fig3_risk_readiness_quadrant(results, save_path=None):
    """Four-quadrant analysis with gate regions"""
    fig, ax = plt.subplots(figsize=(11, 9))
    
    # Gate thresholds
    min_ready = 50
    max_risk = 70
    
    # Shaded gate regions
    ax.fill_between([0, min_ready], [0, 0], [100, 100], alpha=0.1, color='red', label='Gated: Low Readiness')
    ax.fill_between([0, 100], [max_risk, max_risk], [100, 100], alpha=0.1, color='orange', label='Gated: High Risk')
    
    # Quadrant labels
    ax.text(75, 25, 'IDEAL\nHigh Ready / Low Risk', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='green', alpha=0.7)
    ax.text(25, 25, 'DEVELOP\nLow Ready / Low Risk', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='orange', alpha=0.7)
    ax.text(75, 85, 'CAUTION\nHigh Ready / High Risk', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='orange', alpha=0.7)
    ax.text(25, 85, 'AVOID\nLow Ready / High Risk', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='red', alpha=0.7)
    
    # Scatter plot
    colors = ['green' if not g else 'red' for g in results['gated']]
    sizes = results['annual_savings_est'] / 150
    
    scatter = ax.scatter(
        results['readiness_score_0_100'],
        results['risk_score_0_100'],
        s=sizes, c=colors, alpha=0.7, edgecolors='black', linewidths=1
    )
    
    # Label all points
    for _, row in results.iterrows():
        ax.annotate(
            row['step_name'][:15],
            (row['readiness_score_0_100'], row['risk_score_0_100']),
            xytext=(5, 5), textcoords='offset points', fontsize=7
        )
    
    # Gate lines
    ax.axvline(x=min_ready, color='red', linestyle='--', linewidth=2)
    ax.axhline(y=max_risk, color='orange', linestyle='--', linewidth=2)
    ax.axvline(x=50, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.axhline(y=50, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    
    ax.set_xlabel('Readiness Score →', fontsize=12, fontweight='bold')
    ax.set_ylabel('Risk Score →', fontsize=12, fontweight='bold')
    ax.set_title('Risk-Readiness Quadrant Analysis\nGreen = Prioritized | Red = Gated Out', 
                 fontsize=14, fontweight='bold')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def fig4_monte_carlo(results, n_sim=500, save_path=None):
    """Monte Carlo simulation of parameter uncertainty"""
    np.random.seed(42)
    
    # Parameter distributions (triangular: min, mode, max)
    def triangular(a, b, c, size=1):
        return np.array([np.random.triangular(a, b, c) for _ in range(size)])
    
    savings_results = []
    top1_results = []
    
    for _ in range(n_sim):
        # Sample weights
        w_r = triangular(0.25, 0.35, 0.45)[0]
        w_roi = triangular(0.35, 0.45, 0.55)[0]
        w_k = triangular(0.10, 0.20, 0.30)[0]
        
        # Normalize
        total = w_r + w_roi + w_k
        w_r, w_roi, w_k = w_r/total, w_roi/total, w_k/total
        
        # Compute priorities
        priority = compute_priority_score(
            results['readiness_score_0_100'].fillna(0),
            results['roi_score'].fillna(0),
            results['risk_score_0_100'].fillna(100),
            w_r, w_roi, w_k, 50, 70
        )
        
        # Track results
        total_savings = results.loc[priority > 0, 'annual_savings_est'].sum()
        savings_results.append(total_savings)
        
        top_idx = np.argmax(priority)
        top1_results.append(results.iloc[top_idx]['step_name'])
    
    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Savings distribution
    ax1 = axes[0]
    savings_k = np.array(savings_results) / 1000
    ax1.hist(savings_k, bins=30, color=COLORS['primary'], alpha=0.7, edgecolor='black')
    ax1.axvline(np.mean(savings_k), color='red', linewidth=2, label=f'Mean: ${np.mean(savings_k):.0f}K')
    ax1.axvline(np.percentile(savings_k, 5), color='red', linestyle='--', label=f'5th %ile: ${np.percentile(savings_k, 5):.0f}K')
    ax1.axvline(np.percentile(savings_k, 95), color='red', linestyle='--', label=f'95th %ile: ${np.percentile(savings_k, 95):.0f}K')
    ax1.set_xlabel('Annual Savings ($K)', fontsize=11)
    ax1.set_ylabel('Frequency', fontsize=11)
    ax1.set_title(f'Monte Carlo Savings Distribution (n={n_sim})', fontsize=12, fontweight='bold')
    ax1.legend()
    
    # Top 1 stability
    ax2 = axes[1]
    from collections import Counter
    top1_counts = Counter(top1_results)
    top5 = top1_counts.most_common(5)
    names = [x[0] for x in top5]
    counts = [x[1] for x in top5]
    percentages = [100 * c / n_sim for c in counts]
    
    bars = ax2.barh(range(len(names)), percentages, color=COLORS['success'], alpha=0.8)
    ax2.set_yticks(range(len(names)))
    ax2.set_yticklabels(names)
    ax2.set_xlabel('% of Simulations Ranked #1', fontsize=11)
    ax2.set_title('Top Priority Stability', fontsize=12, fontweight='bold')
    
    for i, (bar, pct) in enumerate(zip(bars, percentages)):
        ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                f'{pct:.1f}%', va='center', fontweight='bold')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def fig5_scenario_comparison(data_dir, save_path=None):
    """Compare all 4 scenarios"""
    data = load_all_data(data_dir)
    
    scenarios = ['SCN_BASE', 'SCN_COST', 'SCN_GROWTH', 'SCN_COMPLIANCE']
    scenario_names = ['Baseline', 'Cost Pressure', 'High Growth', 'Compliance']
    
    results_list = []
    
    for scn in scenarios:
        biz_params, strat_params = get_scenario_params(data, scn)
        
        readiness = compute_dimension_score(data['scores'], data['metrics'], 'Readiness')
        risk = compute_risk_score(data['scores'], data['metrics'])
        roi_df = compute_roi_fields(data['steps'], biz_params)
        roi_df['roi_score'] = compute_roi_score(roi_df['payback_months'], roi_df['roi_ratio'], 12, 2.0)
        
        merged = data['steps'][['step_id']].copy()
        merged = merged.merge(readiness, on='step_id', how='left')
        merged = merged.merge(risk, on='step_id', how='left')
        merged = merged.merge(roi_df[['step_id', 'roi_score', 'annual_savings_est']], on='step_id', how='left')
        
        priority = compute_priority_score(
            merged['readiness_score_0_100'].fillna(0),
            merged['roi_score'].fillna(0),
            merged['risk_score_0_100'].fillna(100),
            strat_params['w_readiness'],
            strat_params['w_roi'],
            strat_params['w_risk'],
            strat_params['min_readiness_gate'],
            strat_params['max_risk_gate']
        )
        
        prioritized = (priority > 0).sum()
        gated = (priority == 0).sum()
        total_savings = merged.loc[priority > 0, 'annual_savings_est'].sum()
        
        results_list.append({
            'scenario': scn,
            'prioritized': prioritized,
            'gated': gated,
            'savings': total_savings / 1000
        })
    
    df = pd.DataFrame(results_list)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Savings comparison
    ax1 = axes[0]
    bars = ax1.bar(scenario_names, df['savings'], color=[COLORS['primary'], COLORS['secondary'], 
                                                          COLORS['success'], COLORS['warning']])
    ax1.set_ylabel('Annual Savings ($K)', fontsize=11)
    ax1.set_title('Total Savings by Scenario', fontsize=12, fontweight='bold')
    for bar in bars:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                f'${bar.get_height():.0f}K', ha='center', fontweight='bold')
    
    # Prioritized vs Gated
    ax2 = axes[1]
    x = range(len(scenario_names))
    width = 0.35
    ax2.bar([i - width/2 for i in x], df['prioritized'], width, label='Prioritized', color=COLORS['success'])
    ax2.bar([i + width/2 for i in x], df['gated'], width, label='Gated Out', color=COLORS['danger'])
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenario_names)
    ax2.set_ylabel('Number of Process Steps', fontsize=11)
    ax2.set_title('Candidate Pool by Scenario', fontsize=12, fontweight='bold')
    ax2.legend()
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def fig6_weight_sensitivity(results, save_path=None):
    """Parallel coordinates showing ranking under different weight schemes"""
    weight_schemes = [
        ('Baseline', 0.35, 0.45, 0.20),
        ('ROI Heavy', 0.20, 0.60, 0.20),
        ('Risk Averse', 0.30, 0.30, 0.40),
        ('Readiness First', 0.50, 0.35, 0.15),
        ('Equal', 0.33, 0.34, 0.33),
    ]
    
    # Compute rankings for each scheme
    rankings = {}
    for name, w_r, w_roi, w_k in weight_schemes:
        priority = compute_priority_score(
            results['readiness_score_0_100'].fillna(0),
            results['roi_score'].fillna(0),
            results['risk_score_0_100'].fillna(100),
            w_r, w_roi, w_k, 50, 70
        )
        
        ranked_indices = np.argsort(priority)[::-1]  # Sort descending
        for rank, idx in enumerate(ranked_indices, 1):
            step_name = results.iloc[idx]['step_name']
            if step_name not in rankings:
                rankings[step_name] = {}
            rankings[step_name][name] = rank if priority[idx] > 0 else 99
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    scheme_names = [s[0] for s in weight_schemes]
    x = range(len(scheme_names))
    
    # Plot lines for each process
    for step_name, ranks in rankings.items():
        y = [ranks.get(s, 99) for s in scheme_names]
        
        # Color by average rank
        avg_rank = np.mean([r for r in y if r < 99])
        if avg_rank <= 3:
            color = COLORS['success']
            alpha = 0.9
            lw = 2.5
        elif avg_rank <= 8:
            color = COLORS['warning']
            alpha = 0.6
            lw = 1.5
        else:
            color = COLORS['gray']
            alpha = 0.3
            lw = 1
        
        ax.plot(x, y, marker='o', label=step_name if avg_rank <= 5 else '', 
                color=color, alpha=alpha, linewidth=lw)
    
    ax.set_xticks(x)
    ax.set_xticklabels(scheme_names, fontsize=10)
    ax.set_ylabel('Rank (1 = Best)', fontsize=11)
    ax.set_ylim(0, 16)
    ax.invert_yaxis()
    ax.set_title('Ranking Stability Across Weight Schemes\nGreen = Top 3 Avg | Yellow = Mid | Gray = Low', 
                 fontsize=12, fontweight='bold')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


# =============================================================================
# PLOTLY INTERACTIVE VISUALIZATIONS
# =============================================================================

def plotly_priority_matrix(results, save_path=None):
    """Interactive bubble chart with hover details"""
    if not PLOTLY_AVAILABLE:
        print("Plotly not available")
        return None
    
    fig = px.scatter(
        results,
        x='readiness_score_0_100',
        y='roi_score',
        size='annual_savings_est',
        color='priority_score',
        hover_name='step_name',
        hover_data={
            'readiness_score_0_100': ':.1f',
            'roi_score': ':.1f',
            'risk_score_0_100': ':.1f',
            'annual_savings_est': ':$,.0f',
            'priority_score': ':.1f'
        },
        color_continuous_scale='RdYlGn',
        range_color=[0, 100],
        title='AI Readiness Priority Matrix (Interactive)',
        labels={
            'readiness_score_0_100': 'Readiness Score',
            'roi_score': 'ROI Score',
            'priority_score': 'Priority'
        }
    )
    
    # Add gate lines
    fig.add_vline(x=50, line_dash='dash', line_color='red', annotation_text='Min Readiness Gate')
    
    fig.update_layout(
        xaxis_range=[0, 105],
        yaxis_range=[0, 105],
        height=600,
        width=900
    )
    
    if save_path:
        fig.write_html(save_path)
    
    return fig


def plotly_radar_comparison(results, save_path=None):
    """Radar chart comparing top 5 processes"""
    if not PLOTLY_AVAILABLE:
        print("Plotly not available")
        return None
    
    top5 = results.head(5)
    
    categories = ['Readiness', 'Suitability', 'Safety (100-Risk)', 'ROI', 'Priority']
    
    fig = go.Figure()
    
    colors = ['#2563eb', '#7c3aed', '#16a34a', '#eab308', '#dc2626']
    
    for i, (_, row) in enumerate(top5.iterrows()):
        values = [
            row['readiness_score_0_100'],
            row['suitability_score'],
            100 - row['risk_score_0_100'],
            row['roi_score'],
            row['priority_score']
        ]
        values.append(values[0])  # Close the polygon
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            name=row['step_name'],
            line=dict(color=colors[i], width=2),
            fill='toself',
            opacity=0.3
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title='Top 5 Priorities - Dimension Comparison',
        height=600,
        width=700
    )
    
    if save_path:
        fig.write_html(save_path)
    
    return fig


def plotly_sunburst(results, save_path=None):
    """Sunburst chart showing category > process > priority"""
    if not PLOTLY_AVAILABLE:
        print("Plotly not available")
        return None
    
    # Prepare data
    data = []
    for _, row in results.iterrows():
        data.append({
            'id': row['step_name'],
            'parent': row['category'],
            'value': row['annual_savings_est'],
            'priority': row['priority_score']
        })
    
    # Add category totals
    for cat in results['category'].unique():
        cat_data = results[results['category'] == cat]
        data.append({
            'id': cat,
            'parent': '',
            'value': cat_data['annual_savings_est'].sum(),
            'priority': cat_data['priority_score'].mean()
        })
    
    df = pd.DataFrame(data)
    
    fig = px.sunburst(
        df,
        ids='id',
        parents='parent',
        values='value',
        color='priority',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100],
        title='Savings by Category and Process (Priority-Colored)'
    )
    
    fig.update_layout(height=600, width=700)
    
    if save_path:
        fig.write_html(save_path)
    
    return fig


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def generate_all_visualizations(data_dir, output_dir):
    """Generate all visualizations and save to output directory"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading model results...")
    results = load_model_results(data_dir)
    
    print("\nGenerating Matplotlib visualizations...")
    
    print("  1. Priority Matrix...")
    fig1_priority_matrix(results, output_dir / 'fig1_priority_matrix.png')
    
    print("  2. Dimension Heatmap...")
    fig2_dimension_heatmap(results, output_dir / 'fig2_dimension_heatmap.png')
    
    print("  3. Risk-Readiness Quadrant...")
    fig3_risk_readiness_quadrant(results, output_dir / 'fig3_risk_readiness_quadrant.png')
    
    print("  4. Monte Carlo Simulation...")
    fig4_monte_carlo(results, n_sim=500, save_path=output_dir / 'fig4_monte_carlo.png')
    
    print("  5. Scenario Comparison...")
    fig5_scenario_comparison(data_dir, output_dir / 'fig5_scenario_comparison.png')
    
    print("  6. Weight Sensitivity...")
    fig6_weight_sensitivity(results, output_dir / 'fig6_weight_sensitivity.png')
    
    if PLOTLY_AVAILABLE:
        print("\nGenerating Plotly interactive visualizations...")
        
        print("  7. Interactive Priority Matrix...")
        plotly_priority_matrix(results, output_dir / 'fig7_interactive_matrix.html')
        
        print("  8. Radar Comparison...")
        plotly_radar_comparison(results, output_dir / 'fig8_radar_comparison.html')
        
        print("  9. Sunburst Chart...")
        plotly_sunburst(results, output_dir / 'fig9_sunburst.html')
    
    print(f"\n✅ All visualizations saved to: {output_dir}")
    print(f"   - 6 PNG files (matplotlib)")
    if PLOTLY_AVAILABLE:
        print(f"   - 3 HTML files (plotly interactive)")
    
    return results


if __name__ == "__main__":
    DATA_DIR = PROJECT_ROOT / "data"
    OUTPUT_DIR = PROJECT_ROOT / "outputs" / "figures"
    
    results = generate_all_visualizations(DATA_DIR, OUTPUT_DIR)
    
    # Show figures
    plt.show()
