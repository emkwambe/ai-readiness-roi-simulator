import React, { useState, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ScatterChart, Scatter, Cell, Legend, LineChart, Line, PieChart, Pie, CartesianGrid } from 'recharts';

// Real model output data derived from analysis
const scenarioData = {
  SCN_BASE: {
    name: "Baseline",
    description: "Balanced approach - standard operations",
    params: { volume: 8500, agentCost: 28, budget: 150000 },
    weights: { readiness: 0.35, roi: 0.45, risk: 0.20 },
    gates: { minReadiness: 50, maxRisk: 70 },
    summary: { totalSavings: 288651, totalCost: 266200, roi: 1.08, payback: 11.1, prioritized: 14, gated: 2 }
  },
  SCN_COST: {
    name: "Cost Pressure",
    description: "Aggressive ROI focus - higher labor costs",
    params: { volume: 8500, agentCost: 35, budget: 100000 },
    weights: { readiness: 0.25, roi: 0.60, risk: 0.15 },
    gates: { minReadiness: 40, maxRisk: 75 },
    summary: { totalSavings: 423563, totalCost: 222080, roi: 1.91, payback: 6.3, prioritized: 14, gated: 2 }
  },
  SCN_GROWTH: {
    name: "High Growth",
    description: "Scaling operations - 15K tickets/month",
    params: { volume: 15000, agentCost: 28, budget: 250000 },
    weights: { readiness: 0.40, roi: 0.40, risk: 0.20 },
    gates: { minReadiness: 55, maxRisk: 65 },
    summary: { totalSavings: 582384, totalCost: 294000, roi: 1.98, payback: 6.1, prioritized: 13, gated: 3 }
  },
  SCN_COMPLIANCE: {
    name: "Compliance Heavy",
    description: "Risk-averse - regulated environment",
    params: { volume: 8500, agentCost: 32, budget: 150000 },
    weights: { readiness: 0.30, roi: 0.35, risk: 0.35 },
    gates: { minReadiness: 60, maxRisk: 55 },
    summary: { totalSavings: 221601, totalCost: 278180, roi: 0.80, payback: 15.1, prioritized: 11, gated: 5 }
  }
};

const stepResults = [
  { id: "S09", name: "Product setup", area: "Technical", readiness: 100, risk: 0, roi: 95, priority: 93, savings: 28509, payback: 10.0, candidate: "Full", recommendation: "PRIORITY 1 - Full automation" },
  { id: "S08", name: "Installation support", area: "Technical", readiness: 94, risk: 9, roi: 89, priority: 89, savings: 22071, payback: 10.3, candidate: "Partial", recommendation: "PRIORITY 1 - Full automation" },
  { id: "S11", name: "Product recommendation", area: "Sales", readiness: 94, risk: 9, roi: 76, priority: 85, savings: 22439, payback: 12.7, candidate: "Full", recommendation: "PRIORITY 1 - Full automation" },
  { id: "S06", name: "Battery life", area: "Technical", readiness: 75, risk: 9, roi: 86, priority: 81, savings: 20179, payback: 11.2, candidate: "Partial", recommendation: "PRIORITY 1 - Partial automation" },
  { id: "S16", name: "Display issue", area: "Technical", readiness: 75, risk: 25, roi: 91, priority: 80, savings: 24524, payback: 9.2, candidate: "Partial", recommendation: "PRIORITY 1 - Partial automation" },
  { id: "S07", name: "Network problem", area: "Technical", readiness: 69, risk: 18, roi: 90, priority: 78, savings: 22407, payback: 10.1, candidate: "Partial", recommendation: "PRIORITY 2 - AI-assisted" },
  { id: "S12", name: "Account access", area: "Account", readiness: 100, risk: 42, roi: 76, priority: 77, savings: 18428, payback: 12.8, candidate: "Full", recommendation: "PRIORITY 1 - Human-in-loop" },
  { id: "S04", name: "Delivery problem", area: "Logistics", readiness: 75, risk: 34, roi: 85, priority: 75, savings: 21149, payback: 10.7, candidate: "Partial", recommendation: "PRIORITY 2 - AI-assisted" },
  { id: "S03", name: "Product compatibility", area: "Product", readiness: 75, risk: 9, roi: 86, priority: 79, savings: 21943, payback: 10.3, candidate: "Partial", recommendation: "PRIORITY 1 - Partial automation" },
  { id: "S13", name: "Peripheral compatibility", area: "Product", readiness: 75, risk: 9, roi: 77, priority: 76, savings: 19544, payback: 11.6, candidate: "Partial", recommendation: "PRIORITY 1 - Partial automation" },
  { id: "S01", name: "Refund request", area: "Billing", readiness: 75, risk: 67, roi: 85, priority: 66, savings: 21549, payback: 10.9, candidate: "Assist", recommendation: "PRIORITY 2 - Careful review" },
  { id: "S02", name: "Software bug", area: "Technical", readiness: 56, risk: 34, roi: 83, priority: 65, savings: 21943, payback: 10.7, candidate: "Assist", recommendation: "PRIORITY 3 - Assist mode" },
  { id: "S05", name: "Hardware issue", area: "Technical", readiness: 50, risk: 50, roi: 79, priority: 55, savings: 17079, payback: 11.0, candidate: "Assist", recommendation: "PRIORITY 3 - Assist mode" },
  { id: "S15", name: "Cancellation request", area: "Billing", readiness: 75, risk: 59, roi: 80, priority: 62, savings: 15887, payback: 11.3, candidate: "Assist", recommendation: "PRIORITY 2 - Retention focus" },
  { id: "S10", name: "Payment issue", area: "Billing", readiness: 75, risk: 75, roi: 82, priority: 0, savings: 20569, payback: 11.0, candidate: "Partial", recommendation: "GATED - High risk" },
  { id: "S14", name: "Data loss", area: "Technical", readiness: 50, risk: 92, roi: 60, priority: 0, savings: 10679, payback: 19.1, candidate: "Assist", recommendation: "GATED - Keep human" }
];

const COLORS = {
  primary: '#1e40af',
  secondary: '#3b82f6',
  success: '#059669',
  warning: '#d97706',
  danger: '#dc2626',
  muted: '#6b7280',
  light: '#f3f4f6',
  accent: '#8b5cf6'
};

const formatCurrency = (value) => `$${(value / 1000).toFixed(0)}K`;
const formatPercent = (value) => `${value}%`;

export default function AIReadinessDashboard() {
  const [activeScenario, setActiveScenario] = useState('SCN_BASE');
  const [activeTab, setActiveTab] = useState('overview');
  
  const scenario = scenarioData[activeScenario];
  
  const priorityMatrixData = useMemo(() => 
    stepResults.map(s => ({
      ...s,
      x: s.readiness,
      y: s.roi,
      z: s.savings / 1000,
      color: s.priority > 70 ? COLORS.success : s.priority > 40 ? COLORS.warning : COLORS.danger
    })), []);

  const scenarioComparison = Object.entries(scenarioData).map(([id, s]) => ({
    scenario: s.name,
    savings: s.summary.totalSavings / 1000,
    roi: s.summary.roi,
    payback: s.summary.payback,
    prioritized: s.summary.prioritized
  }));

  const riskDistribution = [
    { name: 'Low Risk (0-30)', value: stepResults.filter(s => s.risk <= 30).length, color: COLORS.success },
    { name: 'Medium Risk (31-60)', value: stepResults.filter(s => s.risk > 30 && s.risk <= 60).length, color: COLORS.warning },
    { name: 'High Risk (61+)', value: stepResults.filter(s => s.risk > 60).length, color: COLORS.danger }
  ];

  const automationBreakdown = [
    { name: 'Full Automation', value: stepResults.filter(s => s.candidate === 'Full').length, color: COLORS.primary },
    { name: 'Partial Automation', value: stepResults.filter(s => s.candidate === 'Partial').length, color: COLORS.secondary },
    { name: 'AI Assist', value: stepResults.filter(s => s.candidate === 'Assist').length, color: COLORS.accent }
  ];

  return (
    <div style={{ 
      fontFamily: "'IBM Plex Sans', -apple-system, sans-serif",
      background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
      minHeight: '100vh',
      padding: '24px'
    }}>
      {/* Header */}
      <div style={{ 
        background: 'white',
        borderRadius: '12px',
        padding: '24px 32px',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        borderLeft: `4px solid ${COLORS.primary}`
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ 
              fontSize: '28px', 
              fontWeight: '600', 
              color: '#1e293b',
              margin: 0,
              letterSpacing: '-0.5px'
            }}>
              AI Readiness & ROI Simulator
            </h1>
            <p style={{ color: COLORS.muted, margin: '8px 0 0', fontSize: '14px' }}>
              Strategic prioritization of AI investments • Customer Support Operations
            </p>
          </div>
          <div style={{ 
            background: COLORS.light, 
            padding: '8px 16px', 
            borderRadius: '8px',
            fontSize: '13px',
            color: COLORS.muted
          }}>
            Data: 8,469 real support tickets • 16 process steps analyzed
          </div>
        </div>
      </div>

      {/* Scenario Selector */}
      <div style={{ 
        display: 'flex', 
        gap: '12px', 
        marginBottom: '24px',
        flexWrap: 'wrap'
      }}>
        {Object.entries(scenarioData).map(([id, s]) => (
          <button
            key={id}
            onClick={() => setActiveScenario(id)}
            style={{
              padding: '12px 20px',
              borderRadius: '8px',
              border: activeScenario === id ? `2px solid ${COLORS.primary}` : '2px solid #e2e8f0',
              background: activeScenario === id ? COLORS.primary : 'white',
              color: activeScenario === id ? 'white' : '#475569',
              cursor: 'pointer',
              fontWeight: '500',
              fontSize: '14px',
              transition: 'all 0.2s'
            }}
          >
            <div>{s.name}</div>
            <div style={{ 
              fontSize: '11px', 
              opacity: 0.8,
              marginTop: '4px'
            }}>
              {s.description.split(' - ')[1] || s.description}
            </div>
          </button>
        ))}
      </div>

      {/* KPI Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        {[
          { label: 'Annual Savings', value: formatCurrency(scenario.summary.totalSavings), sublabel: 'Potential', color: COLORS.success },
          { label: 'Implementation Cost', value: formatCurrency(scenario.summary.totalCost), sublabel: 'Estimated', color: COLORS.primary },
          { label: 'ROI Ratio', value: `${scenario.summary.roi.toFixed(2)}x`, sublabel: 'First Year', color: scenario.summary.roi >= 1 ? COLORS.success : COLORS.warning },
          { label: 'Payback Period', value: `${scenario.summary.payback} mo`, sublabel: 'Break-even', color: scenario.summary.payback <= 12 ? COLORS.success : COLORS.warning },
          { label: 'Steps Prioritized', value: scenario.summary.prioritized, sublabel: 'of 16 total', color: COLORS.secondary },
          { label: 'Steps Gated Out', value: scenario.summary.gated, sublabel: 'High risk', color: COLORS.danger }
        ].map((kpi, i) => (
          <div key={i} style={{
            background: 'white',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.08)'
          }}>
            <div style={{ fontSize: '12px', color: COLORS.muted, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              {kpi.label}
            </div>
            <div style={{ fontSize: '28px', fontWeight: '700', color: kpi.color, margin: '8px 0 4px' }}>
              {kpi.value}
            </div>
            <div style={{ fontSize: '12px', color: COLORS.muted }}>
              {kpi.sublabel}
            </div>
          </div>
        ))}
      </div>

      {/* Tab Navigation */}
      <div style={{ 
        display: 'flex', 
        gap: '4px',
        marginBottom: '24px',
        background: 'white',
        padding: '4px',
        borderRadius: '10px',
        width: 'fit-content'
      }}>
        {['overview', 'matrix', 'comparison', 'details'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '10px 20px',
              borderRadius: '6px',
              border: 'none',
              background: activeTab === tab ? COLORS.primary : 'transparent',
              color: activeTab === tab ? 'white' : COLORS.muted,
              cursor: 'pointer',
              fontWeight: '500',
              fontSize: '14px',
              textTransform: 'capitalize'
            }}
          >
            {tab === 'matrix' ? 'Priority Matrix' : tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
        
        {activeTab === 'overview' && (
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
            <div>
              <h3 style={{ margin: '0 0 16px', color: '#1e293b', fontSize: '16px' }}>Top Automation Priorities</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stepResults.filter(s => s.priority > 0).slice(0, 8)} layout="vertical">
                  <XAxis type="number" domain={[0, 100]} tickFormatter={v => `${v}`} />
                  <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 12 }} />
                  <Tooltip 
                    formatter={(v, name) => [v, name === 'priority' ? 'Priority Score' : name]}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}
                  />
                  <Bar dataKey="priority" fill={COLORS.primary} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div>
              <h3 style={{ margin: '0 0 16px', color: '#1e293b', fontSize: '16px' }}>Risk Distribution</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={riskDistribution}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={70}
                    paddingAngle={2}
                  >
                    {riskDistribution.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" height={36} />
                </PieChart>
              </ResponsiveContainer>
              
              <h3 style={{ margin: '24px 0 16px', color: '#1e293b', fontSize: '16px' }}>Automation Type</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={automationBreakdown}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={70}
                    paddingAngle={2}
                  >
                    {automationBreakdown.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" height={36} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === 'matrix' && (
          <div>
            <h3 style={{ margin: '0 0 8px', color: '#1e293b', fontSize: '16px' }}>Priority Matrix: Readiness vs ROI Potential</h3>
            <p style={{ color: COLORS.muted, fontSize: '13px', margin: '0 0 24px' }}>
              Bubble size = Annual savings potential • Color = Priority score (green = high, red = gated)
            </p>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="x" 
                  name="Readiness" 
                  domain={[0, 100]} 
                  label={{ value: 'AI Readiness Score', position: 'bottom', offset: 20 }}
                />
                <YAxis 
                  dataKey="y" 
                  name="ROI Score" 
                  domain={[0, 100]}
                  label={{ value: 'ROI Score', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ payload }) => {
                    if (!payload || !payload[0]) return null;
                    const d = payload[0].payload;
                    return (
                      <div style={{ 
                        background: 'white', 
                        padding: '12px', 
                        borderRadius: '8px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                        fontSize: '13px'
                      }}>
                        <div style={{ fontWeight: '600', marginBottom: '8px' }}>{d.name}</div>
                        <div>Readiness: {d.readiness}</div>
                        <div>ROI Score: {d.roi}</div>
                        <div>Risk: {d.risk}</div>
                        <div>Annual Savings: ${d.savings.toLocaleString()}</div>
                        <div style={{ marginTop: '8px', color: d.color }}>{d.recommendation}</div>
                      </div>
                    );
                  }}
                />
                <Scatter data={priorityMatrixData}>
                  {priorityMatrixData.map((entry, i) => (
                    <Cell 
                      key={i} 
                      fill={entry.color}
                      fillOpacity={0.7}
                      r={Math.sqrt(entry.z) * 2 + 8}
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
            <div style={{ display: 'flex', gap: '24px', justifyContent: 'center', marginTop: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: 12, height: 12, borderRadius: '50%', background: COLORS.success }} />
                <span style={{ fontSize: '13px', color: COLORS.muted }}>Priority 1 (Score &gt; 70)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: 12, height: 12, borderRadius: '50%', background: COLORS.warning }} />
                <span style={{ fontSize: '13px', color: COLORS.muted }}>Priority 2-3 (Score 40-70)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: 12, height: 12, borderRadius: '50%', background: COLORS.danger }} />
                <span style={{ fontSize: '13px', color: COLORS.muted }}>Gated Out (Score = 0)</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'comparison' && (
          <div>
            <h3 style={{ margin: '0 0 24px', color: '#1e293b', fontSize: '16px' }}>Scenario Comparison</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
              <div>
                <h4 style={{ fontSize: '14px', color: COLORS.muted, margin: '0 0 12px' }}>Annual Savings by Scenario ($K)</h4>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={scenarioComparison}>
                    <XAxis dataKey="scenario" tick={{ fontSize: 12 }} />
                    <YAxis tickFormatter={v => `$${v}K`} />
                    <Tooltip formatter={v => [`$${v}K`, 'Savings']} />
                    <Bar dataKey="savings" fill={COLORS.success} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div>
                <h4 style={{ fontSize: '14px', color: COLORS.muted, margin: '0 0 12px' }}>ROI Ratio by Scenario</h4>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={scenarioComparison}>
                    <XAxis dataKey="scenario" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 2.5]} />
                    <Tooltip formatter={v => [`${v}x`, 'ROI']} />
                    <Bar dataKey="roi" fill={COLORS.primary} radius={[4, 4, 0, 0]}>
                      {scenarioComparison.map((entry, i) => (
                        <Cell key={i} fill={entry.roi >= 1 ? COLORS.success : COLORS.warning} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div style={{ marginTop: '32px', overflowX: 'auto' }}>
              <h4 style={{ fontSize: '14px', color: COLORS.muted, margin: '0 0 12px' }}>Scenario Parameters</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                    <th style={{ textAlign: 'left', padding: '12px', color: COLORS.muted }}>Scenario</th>
                    <th style={{ textAlign: 'right', padding: '12px', color: COLORS.muted }}>Volume/mo</th>
                    <th style={{ textAlign: 'right', padding: '12px', color: COLORS.muted }}>Agent $/hr</th>
                    <th style={{ textAlign: 'right', padding: '12px', color: COLORS.muted }}>W.Readiness</th>
                    <th style={{ textAlign: 'right', padding: '12px', color: COLORS.muted }}>W.ROI</th>
                    <th style={{ textAlign: 'right', padding: '12px', color: COLORS.muted }}>W.Risk</th>
                    <th style={{ textAlign: 'right', padding: '12px', color: COLORS.muted }}>Risk Gate</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(scenarioData).map(([id, s]) => (
                    <tr key={id} style={{ 
                      borderBottom: '1px solid #e2e8f0',
                      background: id === activeScenario ? '#f0f9ff' : 'transparent'
                    }}>
                      <td style={{ padding: '12px', fontWeight: '500' }}>{s.name}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>{s.params.volume.toLocaleString()}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>${s.params.agentCost}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>{(s.weights.readiness * 100).toFixed(0)}%</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>{(s.weights.roi * 100).toFixed(0)}%</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>{(s.weights.risk * 100).toFixed(0)}%</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>≤{s.gates.maxRisk}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'details' && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#1e293b', fontSize: '16px' }}>Process Step Details</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                    <th style={{ textAlign: 'left', padding: '12px', color: COLORS.muted }}>Step</th>
                    <th style={{ textAlign: 'left', padding: '12px', color: COLORS.muted }}>Area</th>
                    <th style={{ textAlign: 'center', padding: '12px', color: COLORS.muted }}>Readiness</th>
                    <th style={{ textAlign: 'center', padding: '12px', color: COLORS.muted }}>Risk</th>
                    <th style={{ textAlign: 'center', padding: '12px', color: COLORS.muted }}>ROI</th>
                    <th style={{ textAlign: 'center', padding: '12px', color: COLORS.muted }}>Priority</th>
                    <th style={{ textAlign: 'right', padding: '12px', color: COLORS.muted }}>Savings</th>
                    <th style={{ textAlign: 'right', padding: '12px', color: COLORS.muted }}>Payback</th>
                    <th style={{ textAlign: 'left', padding: '12px', color: COLORS.muted }}>Type</th>
                  </tr>
                </thead>
                <tbody>
                  {stepResults.map((step, i) => (
                    <tr key={step.id} style={{ 
                      borderBottom: '1px solid #e2e8f0',
                      background: step.priority === 0 ? '#fef2f2' : i % 2 === 0 ? 'white' : '#f8fafc'
                    }}>
                      <td style={{ padding: '12px', fontWeight: '500' }}>{step.name}</td>
                      <td style={{ padding: '12px' }}>{step.area}</td>
                      <td style={{ textAlign: 'center', padding: '12px' }}>
                        <span style={{ 
                          background: step.readiness >= 75 ? '#dcfce7' : step.readiness >= 50 ? '#fef9c3' : '#fee2e2',
                          color: step.readiness >= 75 ? COLORS.success : step.readiness >= 50 ? COLORS.warning : COLORS.danger,
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: '600'
                        }}>{step.readiness}</span>
                      </td>
                      <td style={{ textAlign: 'center', padding: '12px' }}>
                        <span style={{ 
                          background: step.risk <= 30 ? '#dcfce7' : step.risk <= 60 ? '#fef9c3' : '#fee2e2',
                          color: step.risk <= 30 ? COLORS.success : step.risk <= 60 ? COLORS.warning : COLORS.danger,
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: '600'
                        }}>{step.risk}</span>
                      </td>
                      <td style={{ textAlign: 'center', padding: '12px' }}>{step.roi}</td>
                      <td style={{ textAlign: 'center', padding: '12px' }}>
                        <span style={{ 
                          background: step.priority > 70 ? COLORS.success : step.priority > 40 ? COLORS.warning : COLORS.danger,
                          color: 'white',
                          padding: '4px 10px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: '600'
                        }}>{step.priority}</span>
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px', fontWeight: '500' }}>
                        ${step.savings.toLocaleString()}
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>{step.payback} mo</td>
                      <td style={{ padding: '12px' }}>
                        <span style={{
                          background: step.candidate === 'Full' ? '#dbeafe' : step.candidate === 'Partial' ? '#e0e7ff' : '#fae8ff',
                          color: step.candidate === 'Full' ? COLORS.primary : step.candidate === 'Partial' ? COLORS.accent : '#a855f7',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '11px',
                          fontWeight: '500'
                        }}>{step.candidate}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{ 
        marginTop: '24px', 
        padding: '16px 24px',
        background: 'white',
        borderRadius: '12px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '13px',
        color: COLORS.muted
      }}>
        <div>
          <strong>Methodology:</strong> Weighted scoring (Readiness + Suitability + Risk) with configurable gates and ROI calculation
        </div>
        <div>
          AI Business Analyst Portfolio Project • Data-driven AI investment prioritization
        </div>
      </div>
    </div>
  );
}
