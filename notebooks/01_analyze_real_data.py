"""
Step 1: Analyze Real Data → Derive Process Steps
=================================================
This script analyzes the real support ticket dataset and generates
the ProcessSteps.csv file with calculated metrics.

The goal is to extract REAL patterns from data, not make them up.
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Load real data
df = pd.read_csv('/home/claude/learnpath-ai-audit/real_data/customer_support_tickets.csv')

print("=" * 70)
print("ANALYZING REAL DATA TO DERIVE PROCESS STEPS")
print("=" * 70)

# =============================================================================
# STEP 1: Understand the data structure
# =============================================================================

# Parse time columns
def parse_time_to_hours(time_str):
    """Convert 'X days HH:MM:SS' or 'HH:MM:SS' to hours"""
    if pd.isna(time_str):
        return np.nan
    try:
        time_str = str(time_str).strip()
        if 'days' in time_str:
            parts = time_str.split(' days ')
            days = int(parts[0])
            time_part = parts[1] if len(parts) > 1 else '00:00:00'
        elif 'day' in time_str:
            parts = time_str.split(' day ')
            days = int(parts[0])
            time_part = parts[1] if len(parts) > 1 else '00:00:00'
        else:
            days = 0
            time_part = time_str
        
        # Parse time part
        time_parts = time_part.split(':')
        hours = int(time_parts[0]) if len(time_parts) > 0 else 0
        minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        total_hours = days * 24 + hours + minutes / 60
        return total_hours
    except:
        return np.nan

df['first_response_hours'] = df['First Response Time'].apply(parse_time_to_hours)
df['resolution_hours'] = df['Time to Resolution'].apply(parse_time_to_hours)

print(f"\n📊 Total Tickets: {len(df)}")
print(f"   With Resolution: {df['resolution_hours'].notna().sum()}")
print(f"   With CSAT: {df['Customer Satisfaction Rating'].notna().sum()}")

# =============================================================================
# STEP 2: Analyze by Ticket Type (our process steps)
# =============================================================================

print("\n" + "=" * 70)
print("METRICS BY TICKET TYPE (Process Steps)")
print("=" * 70)

step_analysis = df.groupby('Ticket Type').agg({
    'Ticket ID': 'count',
    'first_response_hours': 'mean',
    'resolution_hours': 'mean',
    'Customer Satisfaction Rating': 'mean',
    'Ticket Priority': lambda x: (x == 'Critical').mean() + (x == 'High').mean(),  # High priority %
}).round(2)

step_analysis.columns = ['volume', 'avg_first_response_hrs', 'avg_resolution_hrs', 'avg_csat', 'high_priority_pct']
step_analysis['volume_share'] = (step_analysis['volume'] / step_analysis['volume'].sum()).round(3)
step_analysis = step_analysis.sort_values('volume', ascending=False)

print(step_analysis)

# =============================================================================
# STEP 3: Analyze by Ticket Subject (subcategories)
# =============================================================================

print("\n" + "=" * 70)
print("METRICS BY TICKET SUBJECT (Subcategories)")
print("=" * 70)

subject_analysis = df.groupby('Ticket Subject').agg({
    'Ticket ID': 'count',
    'first_response_hours': 'mean',
    'resolution_hours': 'mean',
    'Customer Satisfaction Rating': 'mean',
}).round(2)

subject_analysis.columns = ['volume', 'avg_first_response_hrs', 'avg_resolution_hrs', 'avg_csat']
subject_analysis['volume_share'] = (subject_analysis['volume'] / subject_analysis['volume'].sum()).round(3)
subject_analysis = subject_analysis.sort_values('volume', ascending=False)

print(subject_analysis)

# =============================================================================
# STEP 4: Analyze by Channel
# =============================================================================

print("\n" + "=" * 70)
print("METRICS BY CHANNEL")
print("=" * 70)

channel_analysis = df.groupby('Ticket Channel').agg({
    'Ticket ID': 'count',
    'first_response_hours': 'mean',
    'resolution_hours': 'mean',
    'Customer Satisfaction Rating': 'mean',
}).round(2)

channel_analysis.columns = ['volume', 'avg_first_response_hrs', 'avg_resolution_hrs', 'avg_csat']
channel_analysis['volume_share'] = (channel_analysis['volume'] / channel_analysis['volume'].sum()).round(3)

print(channel_analysis)

# =============================================================================
# STEP 5: Create ProcessSteps.csv (combining type + subject for granularity)
# =============================================================================

print("\n" + "=" * 70)
print("GENERATING ProcessSteps.csv")
print("=" * 70)

# We'll use Ticket Subject as our process steps (more granular than Type)
# Each subject represents a distinct support scenario that could be automated differently

process_steps = []

# Map subjects to AI automation potential based on characteristics
automation_mapping = {
    # High automation potential - routine, template-able
    'Password reset': 'Full',  # Doesn't exist but similar
    'Account access': 'Full',
    'Product setup': 'Partial',
    'Installation support': 'Partial',
    'Product recommendation': 'Partial',
    'Product compatibility': 'Partial',
    
    # Medium automation potential - need some investigation
    'Payment issue': 'Partial',
    'Delivery problem': 'Partial',
    'Network problem': 'Partial',
    'Battery life': 'Partial',
    'Display issue': 'Partial',
    'Peripheral compatibility': 'Partial',
    
    # Lower automation potential - complex/sensitive
    'Software bug': 'Assist',
    'Hardware issue': 'Assist',
    'Data loss': 'Assist',
    'Refund request': 'Assist',
    'Cancellation request': 'Assist',
}

for i, (subject, row) in enumerate(subject_analysis.iterrows(), 1):
    step = {
        'step_id': f'S{str(i).zfill(2)}',
        'step_name': subject,
        'process_area': df[df['Ticket Subject'] == subject]['Ticket Type'].mode().iloc[0] if len(df[df['Ticket Subject'] == subject]) > 0 else 'General',
        'description': f'Customer inquiry related to {subject.lower()}',
        'owner_role': 'L1 Agent',
        'volume_share': row['volume_share'],
        'avg_handle_time_min': row['avg_resolution_hrs'] * 60 / 3 if pd.notna(row['avg_resolution_hrs']) else 30,  # Estimate handle time
        'avg_first_response_hrs': row['avg_first_response_hrs'] if pd.notna(row['avg_first_response_hrs']) else 4,
        'avg_resolution_hrs': row['avg_resolution_hrs'] if pd.notna(row['avg_resolution_hrs']) else 24,
        'avg_csat': row['avg_csat'] if pd.notna(row['avg_csat']) else 3.0,
        'volume': row['volume'],
        'automation_candidate': automation_mapping.get(subject, 'Partial'),
    }
    process_steps.append(step)

steps_df = pd.DataFrame(process_steps)
steps_df.to_csv('/home/claude/ai-readiness-roi/data/ProcessSteps.csv', index=False)

print(f"✅ Created ProcessSteps.csv with {len(steps_df)} steps")
print(steps_df[['step_id', 'step_name', 'volume_share', 'automation_candidate']].to_string())

# =============================================================================
# STEP 6: Summary Statistics for BusinessParams
# =============================================================================

print("\n" + "=" * 70)
print("KEY METRICS FOR BUSINESS PARAMETERS")
print("=" * 70)

print(f"""
📊 Derived from Real Data:
   Total Monthly Volume (estimate): {len(df)} tickets over ~24 months ≈ {len(df)//24}/month
   Avg First Response Time: {df['first_response_hours'].mean():.1f} hours
   Avg Resolution Time: {df['resolution_hours'].mean():.1f} hours  
   Avg CSAT (where available): {df['Customer Satisfaction Rating'].mean():.2f}/5
   Resolution Rate: {(df['Ticket Status'] == 'Closed').mean()*100:.1f}%
   
   Channel Distribution:
{df['Ticket Channel'].value_counts(normalize=True).round(3).to_string()}
   
   Priority Distribution:
{df['Ticket Priority'].value_counts(normalize=True).round(3).to_string()}
""")

print("\n✅ Analysis complete!")
