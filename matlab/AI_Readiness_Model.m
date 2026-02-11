%% AI_READINESS_MODEL.m
% =========================================================================
% AI Readiness & ROI Simulator - MATLAB Implementation
% Multi-Criteria Decision Analysis (MCDA) with Weighted Sum Model
% =========================================================================
% Author: [Your Name]
% Date: January 2025
% Description: Parameterized decision model for AI investment prioritization
% =========================================================================

clear; clc; close all;

%% 1. MODEL PARAMETERS
% -------------------------------------------------------------------------
% These parameters are justified by industry research (see documentation)

% Dimension weights (must sum to 1.0)
params.w_readiness = 0.35;  % Gartner: 85% AI failures trace to readiness
params.w_roi = 0.45;        % McKinsey: ROI primary criterion for 67%
params.w_risk = 0.20;       % ISO 31000: Risk gated, residual weighted lower

% Gate thresholds (non-compensatory)
params.min_readiness_gate = 50;  % Forrester: <50 = <50% success rate
params.max_risk_gate = 70;       % 70th percentile risk tolerance

% Automation shift rates
params.shift_full = 0.70;     % IBM Watson: 65-80% containment
params.shift_partial = 0.40;  % McKinsey: 30-50% augmentation savings
params.shift_assist = 0.20;   % Gartner: 15-25% copilot productivity

% Financial parameters
params.adoption_rate = 0.80;
params.overhead_mult = 1.15;
params.base_impl_cost = 25000;
params.agent_cost_hr = 28;
params.target_payback = 12;  % months
params.target_roi = 2.0;     % ratio

%% 2. PROCESS STEPS DATA
% -------------------------------------------------------------------------
% 16 process steps derived from real customer support data (8,469 tickets)

process_steps = {
    'S01', 'Refund request',        'Billing',    576, 30, 'Assist';
    'S02', 'Software bug',          'Technical',  574, 35, 'Assist';
    'S03', 'Product compatibility', 'Product',    567, 15, 'Partial';
    'S04', 'Delivery problem',      'Logistics',  561, 20, 'Partial';
    'S05', 'Hardware issue',        'Technical',  547, 40, 'Assist';
    'S06', 'Battery life',          'Technical',  542, 18, 'Partial';
    'S07', 'Network problem',       'Technical',  539, 22, 'Partial';
    'S08', 'Installation support',  'Technical',  530, 20, 'Partial';
    'S09', 'Product setup',         'Technical',  529, 15, 'Full';
    'S10', 'Payment issue',         'Billing',    526, 25, 'Partial';
    'S11', 'Product recommendation','Sales',      517, 12, 'Full';
    'S12', 'Account access',        'Account',    509, 10, 'Full';
    'S13', 'Peripheral compat',     'Product',    496, 15, 'Partial';
    'S14', 'Data loss',             'Technical',  491, 45, 'Assist';
    'S15', 'Cancellation request',  'Billing',    487, 20, 'Assist';
    'S16', 'Display issue',         'Technical',  478, 25, 'Partial';
};

n_steps = size(process_steps, 1);

%% 3. SCORING MATRIX
% -------------------------------------------------------------------------
% Scores for each step (rows) against each metric (columns)
% Scale: 1-5 (1=poor, 5=excellent)
% Metrics: M01-M04 Readiness, M05-M08 Suitability, M09-M11 Risk

%           M01 M02 M03 M04 M05 M06 M07 M08 M09 M10 M11
scores = [
    4   4   4   4   3   3   4   4   4   4   3;   % S01 Refund
    4   3   3   4   3   3   4   3   3   3   3;   % S02 Software bug
    4   4   4   4   4   4   2   4   2   2   4;   % S03 Product compat
    4   4   4   4   4   3   3   4   3   3   3;   % S04 Delivery
    3   3   3   3   3   3   4   3   4   4   2;   % S05 Hardware
    4   4   4   3   4   4   2   4   2   2   4;   % S06 Battery
    4   3   4   3   4   3   3   4   2   3   4;   % S07 Network
    5   4   5   4   5   4   2   5   2   2   4;   % S08 Installation
    5   5   5   5   5   5   1   5   1   1   5;   % S09 Product setup
    4   4   4   4   4   3   3   4   5   4   2;   % S10 Payment
    5   4   5   4   5   4   2   5   2   2   4;   % S11 Recommendation
    5   5   5   5   5   4   2   4   3   4   3;   % S12 Account access
    4   4   4   3   4   4   2   4   2   2   4;   % S13 Peripheral
    3   3   3   3   2   2   5   3   4   5   1;   % S14 Data loss
    4   4   4   4   3   3   4   4   4   4   2;   % S15 Cancellation
    4   4   4   3   4   3   3   4   3   3   3;   % S16 Display
];

%% 4. METRIC DEFINITIONS
% -------------------------------------------------------------------------
% Weights within each dimension

% Readiness metrics (M01-M04) - equal weights
readiness_weights = [0.25, 0.25, 0.25, 0.25];
readiness_direction = [1, 1, 1, 1];  % 1 = higher is better

% Suitability metrics (M05-M08)
suitability_weights = [0.30, 0.25, 0.20, 0.25];
suitability_direction = [1, 1, -1, 1];  % M07 inverted (higher = worse)

% Risk metrics (M09-M11)
risk_weights = [0.35, 0.35, 0.30];
risk_direction = [-1, -1, 1];  % M09, M10 higher = worse; M11 higher = better

%% 5. COMPUTE DIMENSION SCORES
% -------------------------------------------------------------------------

% Normalize scores to 0-1
scores_norm = (scores - 1) / (5 - 1);

% Readiness Score (0-100)
readiness_raw = scores_norm(:, 1:4);
readiness_scores = zeros(n_steps, 1);
for i = 1:n_steps
    weighted_sum = 0;
    for j = 1:4
        if readiness_direction(j) == 1
            weighted_sum = weighted_sum + readiness_weights(j) * readiness_raw(i,j);
        else
            weighted_sum = weighted_sum + readiness_weights(j) * (1 - readiness_raw(i,j));
        end
    end
    readiness_scores(i) = 100 * weighted_sum;
end

% Suitability Score (0-100) - for reference, not used in priority
suitability_raw = scores_norm(:, 5:8);
suitability_scores = zeros(n_steps, 1);
for i = 1:n_steps
    weighted_sum = 0;
    for j = 1:4
        if suitability_direction(j) == 1
            weighted_sum = weighted_sum + suitability_weights(j) * suitability_raw(i,j);
        else
            weighted_sum = weighted_sum + suitability_weights(j) * (1 - suitability_raw(i,j));
        end
    end
    suitability_scores(i) = 100 * weighted_sum;
end

% Risk Score (0-100) - higher = more risky
risk_raw = scores_norm(:, 9:11);
risk_scores = zeros(n_steps, 1);
for i = 1:n_steps
    weighted_sum = 0;
    for j = 1:3
        if risk_direction(j) == -1  % Higher input = higher risk
            weighted_sum = weighted_sum + risk_weights(j) * risk_raw(i,j);
        else  % Higher input = lower risk (invert)
            weighted_sum = weighted_sum + risk_weights(j) * (1 - risk_raw(i,j));
        end
    end
    risk_scores(i) = 100 * weighted_sum;
end

%% 6. COMPUTE ROI SCORES
% -------------------------------------------------------------------------

roi_scores = zeros(n_steps, 1);
annual_savings = zeros(n_steps, 1);
payback_months = zeros(n_steps, 1);

for i = 1:n_steps
    volume = process_steps{i, 4};
    aht_min = process_steps{i, 5};
    auto_type = process_steps{i, 6};
    
    % Get shift rate based on automation type
    switch auto_type
        case 'Full'
            shift_rate = params.shift_full;
        case 'Partial'
            shift_rate = params.shift_partial;
        case 'Assist'
            shift_rate = params.shift_assist;
    end
    
    % Monthly calculations
    monthly_volume = volume;  % Already monthly
    aht_hours = aht_min / 60;
    monthly_manual_cost = monthly_volume * aht_hours * params.agent_cost_hr * params.overhead_mult;
    monthly_savings = monthly_manual_cost * shift_rate * params.adoption_rate;
    
    annual_savings(i) = monthly_savings * 12;
    impl_cost = params.base_impl_cost * (1 + 0.5 * (volume/500 - 1));  % Scale with volume
    
    if monthly_savings > 0
        payback_months(i) = impl_cost / monthly_savings;
    else
        payback_months(i) = 999;
    end
    
    roi_ratio = annual_savings(i) / impl_cost;
    
    % ROI Score: 60% payback + 40% ratio
    payback_score = min(1, params.target_payback / payback_months(i)) * 100;
    ratio_score = min(1, roi_ratio / params.target_roi) * 100;
    roi_scores(i) = 0.6 * payback_score + 0.4 * ratio_score;
end

%% 7. COMPUTE PRIORITY SCORES WITH GATES
% -------------------------------------------------------------------------

priority_scores = zeros(n_steps, 1);
gated = zeros(n_steps, 1);  % 1 = gated out

for i = 1:n_steps
    % Check gates
    if readiness_scores(i) < params.min_readiness_gate
        gated(i) = 1;  % Failed readiness gate
    elseif risk_scores(i) > params.max_risk_gate
        gated(i) = 2;  % Failed risk gate
    end
    
    if gated(i) == 0
        safety = 100 - risk_scores(i);
        priority_scores(i) = params.w_readiness * readiness_scores(i) + ...
                             params.w_roi * roi_scores(i) + ...
                             params.w_risk * safety;
    else
        priority_scores(i) = 0;
    end
end

%% 8. DISPLAY RESULTS
% -------------------------------------------------------------------------

fprintf('\n');
fprintf('═══════════════════════════════════════════════════════════════════\n');
fprintf('           AI READINESS & ROI SIMULATOR - MATLAB RESULTS\n');
fprintf('═══════════════════════════════════════════════════════════════════\n\n');

fprintf('Model Parameters:\n');
fprintf('  Weights: Readiness=%.2f, ROI=%.2f, Risk=%.2f\n', ...
    params.w_readiness, params.w_roi, params.w_risk);
fprintf('  Gates: Min Readiness=%d, Max Risk=%d\n\n', ...
    params.min_readiness_gate, params.max_risk_gate);

% Sort by priority
[sorted_priority, sort_idx] = sort(priority_scores, 'descend');

fprintf('RANKED PRIORITIES:\n');
fprintf('───────────────────────────────────────────────────────────────────\n');
fprintf('%-3s %-22s %8s %8s %8s %10s %8s\n', ...
    'Rk', 'Process Step', 'Priority', 'Ready', 'Risk', 'Savings', 'Payback');
fprintf('───────────────────────────────────────────────────────────────────\n');

for rank = 1:n_steps
    i = sort_idx(rank);
    step_name = process_steps{i, 2};
    
    if gated(i) == 0
        fprintf('%2d. %-22s %8.1f %8.1f %8.1f %10s %6.1f mo\n', ...
            rank, step_name, priority_scores(i), readiness_scores(i), ...
            risk_scores(i), sprintf('$%,.0f', annual_savings(i)), payback_months(i));
    else
        if gated(i) == 1
            gate_reason = 'LOW READY';
        else
            gate_reason = 'HIGH RISK';
        end
        fprintf('%2d. %-22s %8s %8.1f %8.1f %10s %8s\n', ...
            rank, step_name, 'GATED', readiness_scores(i), ...
            risk_scores(i), sprintf('$%,.0f', annual_savings(i)), gate_reason);
    end
end

% Financial Summary
prioritized_idx = find(gated == 0);
total_savings = sum(annual_savings(prioritized_idx));
total_impl = sum(params.base_impl_cost * ones(length(prioritized_idx), 1));

fprintf('\n───────────────────────────────────────────────────────────────────\n');
fprintf('FINANCIAL SUMMARY (Prioritized Items Only):\n');
fprintf('  Total Annual Savings: $%,.0f\n', total_savings);
fprintf('  Items Prioritized: %d of %d\n', length(prioritized_idx), n_steps);
fprintf('  Items Gated Out: %d\n', sum(gated > 0));
fprintf('═══════════════════════════════════════════════════════════════════\n\n');

%% 9. VISUALIZATIONS
% =========================================================================

%% Figure 1: Priority Matrix (Readiness vs ROI)
figure('Name', 'Priority Matrix', 'Position', [100 100 900 700]);

% Bubble chart
scatter(readiness_scores, roi_scores, annual_savings/500, priority_scores, 'filled', 'MarkerEdgeColor', 'k');
colormap(jet);
colorbar('Label', 'Priority Score');
caxis([0 100]);

xlabel('Readiness Score', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('ROI Score', 'FontSize', 12, 'FontWeight', 'bold');
title('AI Readiness Priority Matrix', 'FontSize', 14, 'FontWeight', 'bold');
subtitle('Bubble size = Annual Savings | Color = Priority Score');

% Add gate lines
hold on;
xline(params.min_readiness_gate, '--r', 'LineWidth', 1.5, 'Label', 'Min Readiness Gate');
grid on;

% Label top 5
top5_idx = sort_idx(1:5);
for k = 1:5
    i = top5_idx(k);
    text(readiness_scores(i)+2, roi_scores(i), process_steps{i,2}, 'FontSize', 8);
end

%% Figure 2: Dimension Scores Heatmap
figure('Name', 'Dimension Scores', 'Position', [100 100 800 600]);

% Prepare data for heatmap
heatmap_data = [readiness_scores, suitability_scores, risk_scores, priority_scores];
step_names = process_steps(:, 2);

% Sort by priority for display
[~, heat_sort] = sort(priority_scores, 'descend');
heatmap_sorted = heatmap_data(heat_sort, :);
names_sorted = step_names(heat_sort);

imagesc(heatmap_sorted);
colormap(parula);
colorbar;
caxis([0 100]);

set(gca, 'YTick', 1:n_steps, 'YTickLabel', names_sorted);
set(gca, 'XTick', 1:4, 'XTickLabel', {'Readiness', 'Suitability', 'Risk', 'Priority'});
title('Dimension Scores by Process Step (Sorted by Priority)', 'FontSize', 14);

% Add value annotations
for i = 1:n_steps
    for j = 1:4
        val = heatmap_sorted(i, j);
        if val > 50
            txt_color = 'k';
        else
            txt_color = 'w';
        end
        text(j, i, sprintf('%.0f', val), 'HorizontalAlignment', 'center', ...
            'Color', txt_color, 'FontSize', 8);
    end
end

%% Figure 3: Sensitivity Analysis - Weight Variation
figure('Name', 'Weight Sensitivity', 'Position', [100 100 1000 400]);

% Test different weight combinations
weight_schemes = {
    'Baseline',       0.35, 0.45, 0.20;
    'ROI Heavy',      0.20, 0.60, 0.20;
    'Risk Averse',    0.30, 0.30, 0.40;
    'Readiness First',0.50, 0.35, 0.15;
    'Equal',          0.33, 0.34, 0.33;
};

n_schemes = size(weight_schemes, 1);
rankings = zeros(n_steps, n_schemes);

for s = 1:n_schemes
    w_r = weight_schemes{s, 2};
    w_roi = weight_schemes{s, 3};
    w_k = weight_schemes{s, 4};
    
    temp_priority = zeros(n_steps, 1);
    for i = 1:n_steps
        if gated(i) == 0
            safety = 100 - risk_scores(i);
            temp_priority(i) = w_r * readiness_scores(i) + w_roi * roi_scores(i) + w_k * safety;
        end
    end
    
    [~, temp_sort] = sort(temp_priority, 'descend');
    for rank = 1:n_steps
        rankings(temp_sort(rank), s) = rank;
    end
end

% Plot ranking stability for top items
subplot(1, 2, 1);
top_items = sort_idx(1:8);
bar(rankings(top_items, :)');
set(gca, 'XTickLabel', weight_schemes(:, 1));
ylabel('Rank (1 = Best)');
title('Ranking Stability Across Weight Schemes');
legend(process_steps(top_items, 2), 'Location', 'eastoutside');
set(gca, 'YDir', 'reverse');
ylim([0 10]);
grid on;

% Rank variance
subplot(1, 2, 2);
rank_variance = var(rankings, 0, 2);
[sorted_var, var_idx] = sort(rank_variance);
barh(sorted_var(1:10));
set(gca, 'YTickLabel', process_steps(var_idx(1:10), 2));
xlabel('Ranking Variance');
title('Most Stable Rankings (Low Variance = Stable)');
grid on;

%% Figure 4: Monte Carlo Simulation
figure('Name', 'Monte Carlo Simulation', 'Position', [100 100 1000 400]);

n_simulations = 1000;
mc_savings = zeros(n_simulations, 1);
mc_top1 = cell(n_simulations, 1);

rng(42);  % For reproducibility

for sim = 1:n_simulations
    % Sample parameters from triangular distributions
    w_r = triangular_sample(0.25, 0.35, 0.45);
    w_roi = triangular_sample(0.35, 0.45, 0.55);
    w_k = triangular_sample(0.10, 0.20, 0.30);
    
    % Normalize weights
    w_total = w_r + w_roi + w_k;
    w_r = w_r / w_total;
    w_roi = w_roi / w_total;
    w_k = w_k / w_total;
    
    % Compute priorities
    temp_priority = zeros(n_steps, 1);
    for i = 1:n_steps
        if gated(i) == 0
            safety = 100 - risk_scores(i);
            temp_priority(i) = w_r * readiness_scores(i) + w_roi * roi_scores(i) + w_k * safety;
        end
    end
    
    [~, temp_sort] = sort(temp_priority, 'descend');
    mc_top1{sim} = process_steps{temp_sort(1), 2};
    
    % Sum savings for prioritized items
    mc_savings(sim) = sum(annual_savings(temp_priority > 0));
end

% Plot savings distribution
subplot(1, 2, 1);
histogram(mc_savings/1000, 30, 'FaceColor', [0.2 0.4 0.8]);
xlabel('Annual Savings ($K)');
ylabel('Frequency');
title(sprintf('Monte Carlo Savings Distribution (n=%d)', n_simulations));
xline(mean(mc_savings)/1000, 'r-', 'LineWidth', 2, 'Label', sprintf('Mean: $%.0fK', mean(mc_savings)/1000));
xline(prctile(mc_savings, 5)/1000, 'r--', 'Label', '5th %ile');
xline(prctile(mc_savings, 95)/1000, 'r--', 'Label', '95th %ile');
grid on;

% Count top 1 occurrences
subplot(1, 2, 2);
[unique_top1, ~, ic] = unique(mc_top1);
top1_counts = accumarray(ic, 1);
[sorted_counts, count_idx] = sort(top1_counts, 'descend');
bar(sorted_counts(1:min(5, length(sorted_counts))));
set(gca, 'XTickLabel', unique_top1(count_idx(1:min(5, length(sorted_counts)))));
ylabel('Count');
title('Top Priority Stability');
for k = 1:min(5, length(sorted_counts))
    text(k, sorted_counts(k)+20, sprintf('%.1f%%', 100*sorted_counts(k)/n_simulations), ...
        'HorizontalAlignment', 'center');
end
grid on;

%% Figure 5: Scenario Comparison
figure('Name', 'Scenario Comparison', 'Position', [100 100 1000 500]);

scenarios = {
    'Baseline',       0.35, 0.45, 0.20, 50, 70;
    'Cost Pressure',  0.25, 0.60, 0.15, 40, 75;
    'High Growth',    0.40, 0.40, 0.20, 55, 65;
    'Compliance',     0.30, 0.35, 0.35, 60, 55;
};

n_scenarios = size(scenarios, 1);
scenario_results = zeros(n_scenarios, 4);  % savings, prioritized, gated, avg_priority

for s = 1:n_scenarios
    w_r = scenarios{s, 2};
    w_roi = scenarios{s, 3};
    w_k = scenarios{s, 4};
    min_r = scenarios{s, 5};
    max_k = scenarios{s, 6};
    
    temp_priority = zeros(n_steps, 1);
    temp_gated = zeros(n_steps, 1);
    
    for i = 1:n_steps
        if readiness_scores(i) < min_r
            temp_gated(i) = 1;
        elseif risk_scores(i) > max_k
            temp_gated(i) = 1;
        else
            safety = 100 - risk_scores(i);
            temp_priority(i) = w_r * readiness_scores(i) + w_roi * roi_scores(i) + w_k * safety;
        end
    end
    
    prioritized = temp_gated == 0;
    scenario_results(s, 1) = sum(annual_savings(prioritized)) / 1000;
    scenario_results(s, 2) = sum(prioritized);
    scenario_results(s, 3) = sum(~prioritized);
    scenario_results(s, 4) = mean(temp_priority(prioritized));
end

subplot(1, 2, 1);
bar(scenario_results(:, 1));
set(gca, 'XTickLabel', scenarios(:, 1));
ylabel('Annual Savings ($K)');
title('Total Savings by Scenario');
grid on;

subplot(1, 2, 2);
bar([scenario_results(:, 2), scenario_results(:, 3)], 'stacked');
set(gca, 'XTickLabel', scenarios(:, 1));
ylabel('Number of Process Steps');
legend('Prioritized', 'Gated Out', 'Location', 'northeast');
title('Candidate Pool by Scenario');
grid on;

%% Figure 6: Risk vs Readiness Quadrant
figure('Name', 'Risk-Readiness Quadrant', 'Position', [100 100 800 600]);

scatter(readiness_scores, risk_scores, 150, priority_scores, 'filled', 'MarkerEdgeColor', 'k');
colormap(jet);
colorbar('Label', 'Priority Score');
caxis([0 100]);

% Add quadrant lines
xline(50, '--k', 'LineWidth', 1);
yline(50, '--k', 'LineWidth', 1);

% Label quadrants
text(75, 25, 'HIGH READY / LOW RISK', 'FontSize', 10, 'FontWeight', 'bold', ...
    'HorizontalAlignment', 'center', 'Color', [0 0.5 0]);
text(25, 25, 'LOW READY / LOW RISK', 'FontSize', 10, 'FontWeight', 'bold', ...
    'HorizontalAlignment', 'center', 'Color', [0.8 0.6 0]);
text(75, 75, 'HIGH READY / HIGH RISK', 'FontSize', 10, 'FontWeight', 'bold', ...
    'HorizontalAlignment', 'center', 'Color', [0.8 0.6 0]);
text(25, 75, 'LOW READY / HIGH RISK', 'FontSize', 10, 'FontWeight', 'bold', ...
    'HorizontalAlignment', 'center', 'Color', [0.8 0 0]);

% Add gate regions
patch([0 params.min_readiness_gate params.min_readiness_gate 0], ...
      [0 0 100 100], 'r', 'FaceAlpha', 0.1, 'EdgeColor', 'none');
patch([0 100 100 0], ...
      [params.max_risk_gate params.max_risk_gate 100 100], 'r', 'FaceAlpha', 0.1, 'EdgeColor', 'none');

xlabel('Readiness Score', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('Risk Score', 'FontSize', 12, 'FontWeight', 'bold');
title('Risk-Readiness Quadrant Analysis', 'FontSize', 14, 'FontWeight', 'bold');
subtitle('Shaded regions = Gated out by thresholds');

% Label all points
for i = 1:n_steps
    text(readiness_scores(i)+1, risk_scores(i)+1, process_steps{i, 2}, 'FontSize', 7);
end

xlim([0 105]);
ylim([0 105]);
grid on;

fprintf('Visualizations complete. %d figures generated.\n', 6);

%% HELPER FUNCTION
function x = triangular_sample(a, b, c)
    % Sample from triangular distribution (a=min, b=mode, c=max)
    u = rand();
    fc = (b - a) / (c - a);
    if u < fc
        x = a + sqrt(u * (c - a) * (b - a));
    else
        x = c - sqrt((1 - u) * (c - a) * (c - b));
    end
end
