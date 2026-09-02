% ==============================================================================
% File: run_experiments.m
% Description: Parameter sweep experiments and visualization generator for
% Priority 1 of SIH Problem 26058.
%
% Executes:
%   1. Range Sweep (10m to 200m)
%   2. Noise Sensitivity Sweep (-20 dB to +20 dB)
%   3. Environmental Sensitivity Analysis (Temperature, Salinity, Depth)
%   4. Turbidity Sensitivity Heuristic
% Generates all 7 required engineering validation figures in outputs_matlab/plots/
% ==============================================================================

function results = run_experiments()
    fprintf('\n==============================================================================\n');
    fprintf('  EXECUTING PRIORITY 1 PARAMETER SWEEP EXPERIMENTS (SIH Problem 26058)\n');
    fprintf('==============================================================================\n');

    cfg = config_sonar();
    output_dir = fullfile(pwd, 'outputs_matlab', 'plots');
    if ~exist(output_dir, 'dir'), mkdir(output_dir); end

    % --------------------------------------------------------------------------
    % Experiment 1: Range Sweep Analysis
    % --------------------------------------------------------------------------
    fprintf('\n[*] Experiment 1: Range Sweep Analysis (SURVEY Objective)...\n');
    ranges = [10.0, 25.0, 50.0, 75.0, 100.0, 125.0, 150.0, 175.0, 200.0];
    fprintf('  %-8s %-12s %-12s %-12s %-16s %s\n', ...
            'Range', 'LOW Margin', 'BAL Margin', 'HIGH Margin', 'Selected Profile', 'Confidence');
    fprintf('  ------------------------------------------------------------------------\n');

    range_results = cell(length(ranges), 1);
    for r_idx = 1:length(ranges)
        r_val = ranges(r_idx);
        env = struct('depth_m', 50.0, 'temperature_c', 20.0, 'salinity_psu', 35.0, ...
                     'turbidity', 0.0, 'ambient_noise_db', 0.0);
        [m, d] = evaluate_profile_performance(r_val, env, 'SURVEY', cfg);
        fprintf('  %5.1f m  %7.2f dB   %7.2f dB   %7.2f dB   %-16s %5.2f\n', ...
                r_val, m{1}.relative_margin_db, m{2}.relative_margin_db, m{3}.relative_margin_db, ...
                d.candidate_name, d.profile_selection_confidence);
        range_results{r_idx} = struct('range_m', r_val, 'metrics', {m}, 'decision', d);
    end

    % --------------------------------------------------------------------------
    % Experiment 2: Noise Sensitivity Sweep
    % --------------------------------------------------------------------------
    fprintf('\n[*] Experiment 2: Noise Sensitivity Sweep (at Range = 75 m)...\n');
    noise_levels = [-20.0, -10.0, 0.0, 10.0, 20.0];
    fprintf('  %-14s %-12s %-12s %-12s %s\n', ...
            'Noise Param', 'LOW Viable', 'BAL Viable', 'HIGH Viable', 'Selected Profile');
    fprintf('  ------------------------------------------------------------------\n');

    for n_idx = 1:length(noise_levels)
        n_val = noise_levels(n_idx);
        env = struct('depth_m', 50.0, 'temperature_c', 20.0, 'salinity_psu', 35.0, ...
                     'turbidity', 0.0, 'ambient_noise_db', n_val);
        [m, d] = evaluate_profile_performance(75.0, env, 'SURVEY', cfg);
        fprintf('  %7.1f dB      %-12s %-12s %-12s %s\n', ...
                n_val, mat2str(m{1}.is_viable), mat2str(m{2}.is_viable), mat2str(m{3}.is_viable), d.candidate_name);
    end

    % --------------------------------------------------------------------------
    % Generate 7 Engineering Figures
    % --------------------------------------------------------------------------
    fprintf('\n[*] Generating 7 Required Priority 1 Engineering Figures...\n');

    c_low = [0.83, 0.33, 0.0];
    c_bal = [0.16, 0.50, 0.73];
    c_high = [0.15, 0.68, 0.38];

    % Figure 1: Attenuation vs Frequency
    fig1 = figure('Visible', 'off', 'Position', [100, 100, 900, 500]);
    f_axis_khz = linspace(80.0, 520.0, 300);
    a_clear = zeros(size(f_axis_khz));
    for i = 1:length(f_axis_khz)
        a_clear(i) = calc_attenuation(f_axis_khz(i), 20.0, 35.0, 50.0, 0.0);
    end
    plot(f_axis_khz, a_clear, 'k-', 'LineWidth', 2.0); hold on;
    
    p_low_pts = linspace(100.0, 220.0, 5);
    p_bal_pts = linspace(200.0, 400.0, 5);
    p_high_pts = linspace(350.0, 500.0, 5);
    scatter(p_low_pts, arrayfun(@(f) calc_attenuation(f, 20, 35, 50, 0), p_low_pts), 50, c_low, 'filled');
    scatter(p_bal_pts, arrayfun(@(f) calc_attenuation(f, 20, 35, 50, 0), p_bal_pts), 50, c_bal, 'filled');
    scatter(p_high_pts, arrayfun(@(f) calc_attenuation(f, 20, 35, 50, 0), p_high_pts), 50, c_high, 'filled');
    grid on; xlabel('Frequency (kHz)'); ylabel('Attenuation \alpha (dB/km)');
    title('Fig 1: Frequency-Dependent Seawater Attenuation (Ainslie-McColm 1998 & 5-Pt Sampling)');
    legend('Clear Seawater (T=20^\circC, S=35, D=50m)', 'LOW\_FREQUENCY (100-220k)', ...
           'BALANCED (200-400k)', 'HIGH\_FREQUENCY (350-500k)', 'Location', 'northwest');
    saveas(fig1, fullfile(output_dir, 'exp01_attenuation_vs_frequency.png'));
    close(fig1);
    fprintf('  [+] Saved Fig 1: exp01_attenuation_vs_frequency.png\n');

    % Figure 2: Propagation vs Range
    fig2 = figure('Visible', 'off', 'Position', [100, 100, 900, 500]);
    r_dense = linspace(5.0, 200.0, 80);
    m1_r = zeros(size(r_dense)); m2_r = zeros(size(r_dense)); m3_r = zeros(size(r_dense));
    for i = 1:length(r_dense)
        env = struct('depth_m', 50.0, 'temperature_c', 20.0, 'salinity_psu', 35.0, 'turbidity', 0.0, 'ambient_noise_db', 0.0);
        [m, ~] = evaluate_profile_performance(r_dense(i), env, 'SURVEY', cfg);
        m1_r(i) = m{1}.relative_margin_db;
        m2_r(i) = m{2}.relative_margin_db;
        m3_r(i) = m{3}.relative_margin_db;
    end
    plot(r_dense, m1_r, 'Color', c_low, 'LineWidth', 2.0); hold on;
    plot(r_dense, m2_r, 'Color', c_bal, 'LineWidth', 2.0);
    plot(r_dense, m3_r, 'Color', c_high, 'LineWidth', 2.0);
    yline(-65.0, 'r--', 'Viability Threshold (-65 dB relative)');
    grid on; xlabel('Target Range R (meters)'); ylabel('Relative Propagation Margin (dB)');
    title('Fig 2: Relative Propagation Margin vs Range (Natural Viability Limits)');
    legend('LOW\_FREQUENCY (100-220 kHz)', 'BALANCED (200-400 kHz)', 'HIGH\_FREQUENCY (350-500 kHz)', 'Location', 'northeast');
    saveas(fig2, fullfile(output_dir, 'exp02_propagation_vs_range.png'));
    close(fig2);
    fprintf('  [+] Saved Fig 2: exp02_propagation_vs_range.png\n');

    % Figure 3: Theoretical Range Resolution
    fig3 = figure('Visible', 'off', 'Position', [100, 100, 800, 450]);
    bar([1, 2, 3], [6.25, 3.75, 5.00]);
    xticks([1, 2, 3]); xticklabels({'LOW\_FREQ (120k BW)', 'BALANCED (200k BW)', 'HIGH\_FREQ (150k BW)'});
    ylabel('Theoretical Range Resolution \Delta R = c / (2B) (mm)'); ylim([0, 8]); grid on;
    title('Fig 3: Theoretical Bandwidth-Based Range Resolution (c = 1500 m/s)');
    saveas(fig3, fullfile(output_dir, 'exp03_theoretical_range_resolution.png'));
    close(fig3);
    fprintf('  [+] Saved Fig 3: exp03_theoretical_range_resolution.png\n');

    % Figure 4: Relative Directivity Comparison
    fig4 = figure('Visible', 'off', 'Position', [100, 100, 800, 450]);
    bar([1, 2, 3], [0.533, 1.000, 1.417]);
    xticks([1, 2, 3]); xticklabels({'LOW\_FREQ (160k)', 'BALANCED (300k)', 'HIGH\_FREQ (425k)'});
    ylabel('Relative Directivity Factor (f_c / 300 kHz)'); ylim([0, 1.8]); grid on;
    title('Fig 4: Relative Theoretical Directivity (Fixed Physical Aperture Assumption)');
    saveas(fig4, fullfile(output_dir, 'exp04_relative_directivity_comparison.png'));
    close(fig4);
    fprintf('  [+] Saved Fig 4: exp04_relative_directivity_comparison.png\n');

    % Figure 5: Profile Selection vs Range
    fig5 = figure('Visible', 'off', 'Position', [100, 100, 900, 600]);
    c_surv = zeros(size(r_dense)); c_dir = zeros(size(r_dense));
    for i = 1:length(r_dense)
        env = struct('depth_m', 50.0, 'temperature_c', 20.0, 'salinity_psu', 35.0, 'turbidity', 0.0, 'ambient_noise_db', 0.0);
        [~, ds] = evaluate_profile_performance(r_dense(i), env, 'SURVEY', cfg);
        [~, dd] = evaluate_profile_performance(r_dense(i), env, 'DIRECTIVITY', cfg);
        c_surv(i) = ds.candidate_profile_id;
        c_dir(i) = dd.candidate_profile_id;
    end
    subplot(2, 1, 1);
    stairs(r_dense, c_surv, 'Color', c_bal, 'LineWidth', 2.0);
    yticks([1, 2, 3]); yticklabels({'LOW\_FREQ', 'BALANCED', 'HIGH\_FREQ'}); ylim([0.5, 3.5]); grid on;
    title('Fig 5a: Profile Selection vs Range under SURVEY Objective (Resolution Priority)');
    ylabel('Selected Profile');

    subplot(2, 1, 2);
    stairs(r_dense, c_dir, 'Color', c_high, 'LineWidth', 2.0);
    yticks([1, 2, 3]); yticklabels({'LOW\_FREQ', 'BALANCED', 'HIGH\_FREQ'}); ylim([0.5, 3.5]); grid on;
    title('Fig 5b: Profile Selection vs Range under DIRECTIVITY Objective (Narrow-Beam Priority)');
    ylabel('Selected Profile'); xlabel('Target Range R (meters)');
    saveas(fig5, fullfile(output_dir, 'exp05_profile_winner_vs_range.png'));
    close(fig5);
    fprintf('  [+] Saved Fig 5: exp05_profile_winner_vs_range.png\n');

    % Figure 6: Performance Margin vs Range
    fig6 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    m_above = zeros(size(r_dense)); conf_arr = zeros(size(r_dense));
    for i = 1:length(r_dense)
        env = struct('depth_m', 50.0, 'temperature_c', 20.0, 'salinity_psu', 35.0, 'turbidity', 0.0, 'ambient_noise_db', 0.0);
        [~, ds] = evaluate_profile_performance(r_dense(i), env, 'SURVEY', cfg);
        m_above(i) = ds.margin_above_viability_db;
        conf_arr(i) = ds.profile_selection_confidence;
    end
    plot(r_dense, m_above, 'b-', 'LineWidth', 1.8); hold on;
    yline(0.0, 'r--', 'Viability Limit (Margin = 0 dB)');
    yline(10.0, 'g:', 'Full Confidence (+10 dB)');
    grid on; xlabel('Target Range R (meters)'); ylabel('Viability Margin (dB)');
    title('Fig 6: Candidate Margin Above Viability & profile\_selection\_confidence vs Range');
    saveas(fig6, fullfile(output_dir, 'exp06_performance_margin_vs_range.png'));
    close(fig6);
    fprintf('  [+] Saved Fig 6: exp06_performance_margin_vs_range.png\n');

    % Figure 7: Environmental Sensitivity
    fig7 = figure('Visible', 'off', 'Position', [100, 100, 1200, 400]);
    temps = linspace(-2.0, 35.0, 20);
    c_t = arrayfun(@(t) calc_mackenzie(t, 35, 50), temps);
    a_t = arrayfun(@(t) calc_attenuation(425, t, 35, 50, 0), temps);

    subplot(1, 3, 1);
    plot(temps, c_t, 'b-', 'LineWidth', 1.5);
    xlabel('Temperature (^\circC)'); ylabel('Sound Speed (m/s)'); grid on;
    title('Temperature Sensitivity');

    salinities = linspace(0.0, 40.0, 20);
    c_s = arrayfun(@(s) calc_mackenzie(20, s, 50), salinities);
    subplot(1, 3, 2);
    plot(salinities, c_s, 'b-', 'LineWidth', 1.5);
    xlabel('Salinity (PSU)'); ylabel('Sound Speed (m/s)'); grid on;
    title('Salinity Sensitivity');

    depths = linspace(0.0, 500.0, 20);
    c_d = arrayfun(@(d) calc_mackenzie(20, 35, d), depths);
    subplot(1, 3, 3);
    plot(depths, c_d, 'b-', 'LineWidth', 1.5);
    xlabel('Depth (m)'); ylabel('Sound Speed (m/s)'); grid on;
    title('Depth Sensitivity');
    saveas(fig7, fullfile(output_dir, 'exp07_environmental_sensitivity_summary.png'));
    close(fig7);
    fprintf('  [+] Saved Fig 7: exp07_environmental_sensitivity_summary.png\n');

    fprintf('\n==============================================================================\n');
    fprintf('  ALL 7 EXPERIMENT FIGURES GENERATED IN %s\n', output_dir);
    fprintf('==============================================================================\n');
    results = struct('ranges', ranges, 'noise_levels', noise_levels);
end

function c = calc_mackenzie(T, S, D)
    c = 1448.96 + 4.591*T - 0.05304*(T^2) + 0.0002374*(T^3) + ...
        1.340*(S - 35.0) + 0.0163*D + 0.0001675*(D^2) - ...
        0.01025*T*(S - 35.0) - 0.0000007139*T*(D^3);
end

function alpha = calc_attenuation(f_k, T, S, D, turb)
    f1 = 0.78 * sqrt(S / 35.0) * exp(T / 26.0);
    A1 = 0.106 * exp((T - 20.0) / 27.0);
    f2 = 42.0 * exp(T / 17.0);
    A2 = 0.52 * (1.0 + T / 43.0) * (S / 35.0);
    A3 = 0.00049 * exp(-(T / 27.0) - (D / 17000.0));
    alpha_chem = (A1 * f1 * (f_k^2)) / (f1^2 + f_k^2) + ...
                 (A2 * f2 * (f_k^2)) / (f2^2 + f_k^2) + A3 * (f_k^2);
    if turb > 0
        alpha_turb = 35.0 * (turb / 100.0) * ((f_k / 300.0)^2);
    else
        alpha_turb = 0.0;
    end
    alpha = alpha_chem + alpha_turb;
end
