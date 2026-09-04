% ==============================================================================
% SIH Problem 26058: Master Simulation Script
% "Low-Power, Real-Time Adaptive Software-Defined Sonar Transmitter Payload for AUVs"
%
% File: run_simulation.m
% Description: Complete end-to-end MATLAB simulation, 23-point validation suite,
% 13 engineering validation plots, embedded memory analysis, and C header export.
% ==============================================================================

function run_simulation()
    clc;
    fprintf('==============================================================================\n');
    fprintf('  SIH PROBLEM 26058: AUV ADAPTIVE SONAR TRANSMITTER DIGITAL TWIN (MATLAB)\n');
    fprintf('  Target Platform: STM32G474 (170MHz Cortex-M4, Timer TRGO -> DMA -> DAC)\n');
    fprintf('==============================================================================\n');

    cfg = config_sonar();
    fprintf(cfg.disclaimer);

    % Output directories
    output_dir = fullfile(pwd, 'outputs_matlab');
    plots_dir = fullfile(output_dir, 'plots');
    headers_dir = fullfile(output_dir, 'headers');
    if ~exist(plots_dir, 'dir'), mkdir(plots_dir); end
    if ~exist(headers_dir, 'dir'), mkdir(headers_dir); end

    % --------------------------------------------------------------------------
    % Phase 1: Synthesize Waveforms for all 3 Profiles
    % --------------------------------------------------------------------------
    fprintf('\n[*] Phase 1: Synthesizing Adaptive LFM Chirp Waveforms (4.0 MSPS, 12-bit DAC)...\n');
    profiles = profile_definitions();
    waveforms = cell(length(profiles), 1);
    dac_arrays = cell(length(profiles), 1);
    q_metrics_all = cell(length(profiles), 1);

    for i = 1:length(profiles)
        p = profiles(i);
        [wf, ~] = generate_lfm_chirp(p.f_start_hz, p.f_end_hz, p.duration_s, cfg.Fs, 1.0);
        [dac_codes, q_m] = dac_quantize(wf.signal, cfg);
        waveforms{i} = wf;
        dac_arrays{i} = dac_codes;
        q_metrics_all{i} = q_m;

        mem_kb = (wf.Np * cfg.bytes_per_sample) / 1024.0;
        fprintf('  -> %-14s: %5.1f to %5.1f kHz | N = %d (%4.1f KB) | SQNR: %5.2f dB\n', ...
                p.name, p.f_start_hz/1e3, p.f_end_hz/1e3, wf.Np, mem_kb, q_m.sqnr_db);
    end

    % --------------------------------------------------------------------------
    % Phase 2: Embedded Memory Budget Analysis (STM32G474)
    % --------------------------------------------------------------------------
    fprintf('\n[*] Phase 2: Evaluating Embedded Memory Budget on %s...\n', cfg.target_mcu);
    bytes_per_lut = cfg.Np * cfg.bytes_per_sample;
    total_flash_luts = bytes_per_lut * cfg.num_profiles;
    sram_ping_buffer = bytes_per_lut; % Active ping DMA buffer

    sram_util_pct = (sram_ping_buffer / cfg.mcu_sram_bytes) * 100.0;
    flash_util_pct = (total_flash_luts / cfg.mcu_flash_bytes) * 100.0;

    fprintf('  --------------------------------------------------------------------------\n');
    fprintf('  Memory Segment          Allocated Size        MCU Capacity      Utilization\n');
    fprintf('  --------------------------------------------------------------------------\n');
    fprintf('  Single Ping DMA Buffer  %6d bytes (15.6 KB)  128 KB SRAM         %5.2f%%\n', ...
            sram_ping_buffer, sram_util_pct);
    fprintf('  Flash Storage (3 LUTs)  %6d bytes (46.9 KB)  512 KB Flash        %5.2f%%\n', ...
            total_flash_luts, flash_util_pct);
    fprintf('  --------------------------------------------------------------------------\n');

    % --------------------------------------------------------------------------
    % Phase 3: Power Model Evaluation
    % --------------------------------------------------------------------------
    fprintf('\n[*] Phase 3: Evaluating Duty-Cycle Power Model...\n');
    fprintf('  NOTE: Estimates for modeled transmitter payload alone against hypothetical 99 Wh pack.\n');
    fprintf('  --------------------------------------------------------------------------\n');
    fprintf('  Profile          Duration    PRI      Duty%%     Avg Power   Avg Current   TX-Only 99Wh\n');
    fprintf('  --------------------------------------------------------------------------\n');
    for i = 1:length(profiles)
        p = profiles(i);
        pm = power_model(p.duration_s, 1.0, cfg);
        fprintf('  %-16s %4.1f ms    %4.1f ms  %5.1f%%    %6.3f W     %6.1f mA       %6.1f hrs\n', ...
                p.name, pm.pulse_duration_ms, pm.pri_ms, pm.duty_cycle_pct, ...
                pm.average_power_w, pm.average_current_ma, pm.transmitter_alone_endurance_hours);
    end
    fprintf('  --------------------------------------------------------------------------\n');

    % --------------------------------------------------------------------------
    % Phase 4: Export Firmware-Ready Prototype C Headers
    % --------------------------------------------------------------------------
    fprintf('\n[*] Phase 4: Exporting Firmware-Ready Prototype C Headers...\n');
    export_c_headers(headers_dir);

    % --------------------------------------------------------------------------
    % Phase 5: Generating 13 Required Analysis Plots
    % --------------------------------------------------------------------------
    fprintf('\n[*] Phase 5: Generating 13 Required Engineering Validation Figures...\n');
    p_bal = profiles(2);
    wf_bal = waveforms{2};
    dac_bal = dac_arrays{2};
    qm_bal = q_metrics_all{2};
    n_fft = wf_bal.Np * 4;
    freqs_khz = (0:(n_fft/2)) * (cfg.Fs / n_fft) / 1e3;

    % Figure 1: Time-Domain Waveform for each profile (3 panels)
    fig1 = figure('Visible', 'off', 'Position', [100, 100, 1000, 800]);
    colors = {[0.85, 0.35, 0.0], [0.15, 0.50, 0.80], [0.15, 0.70, 0.35]};
    for i = 1:length(profiles)
        subplot(3, 1, i);
        plot(waveforms{i}.t * 1000, waveforms{i}.signal, 'Color', colors{i}, 'LineWidth', 0.9); hold on;
        plot(waveforms{i}.t * 1000, waveforms{i}.window, 'r--', 'LineWidth', 1.0);
        plot(waveforms{i}.t * 1000, -waveforms{i}.window, 'r--', 'LineWidth', 1.0);
        grid on; ylabel('Amplitude');
        title(sprintf('Profile %d: %s (%.0f - %.0f kHz, B = %.0f kHz)', ...
              profiles(i).id, profiles(i).name, profiles(i).f_start_hz/1e3, profiles(i).f_end_hz/1e3, profiles(i).bandwidth_hz/1e3));
    end
    xlabel('Time (ms)');
    saveas(fig1, fullfile(plots_dir, '01_time_domain_waveform.png'));
    close(fig1);
    fprintf('  [+] Plot 1 saved: 01_time_domain_waveform.png\n');

    % Figure 2: Zoomed Waveform Section (Stair-step DAC Quantization)
    fig2 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    mid_idx = round(wf_bal.Np / 2);
    zoom_idx = (mid_idx - 40):(mid_idx + 40);
    t_zoom_us = (wf_bal.t(zoom_idx) - wf_bal.t(zoom_idx(1))) * 1e6;
    plot(t_zoom_us, qm_bal.dac_ideal(zoom_idx), 'b-', 'LineWidth', 1.5); hold on;
    stairs(t_zoom_us, double(dac_bal(zoom_idx)), 'r-', 'LineWidth', 1.2);
    grid on; xlabel('Time (\mus)'); ylabel('12-bit DAC Code (0 - 4095)');
    title('Plot 2: Zoomed Waveform Detail (Ideal vs 12-bit Quantized DAC Output)');
    legend('Ideal Continuous Value', '12-bit Quantized Code', 'Location', 'northeast');
    saveas(fig2, fullfile(plots_dir, '02_zoomed_waveform_section.png'));
    close(fig2);
    fprintf('  [+] Plot 2 saved: 02_zoomed_waveform_section.png\n');

    % Figure 3: Instantaneous Frequency
    fig3 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    plot(wf_bal.t * 1000, wf_bal.inst_freq_hz / 1e3, 'b', 'LineWidth', 1.5); hold on;
    yline(p_bal.f_start_hz / 1e3, 'k--', 'f_{start} = 200 kHz');
    yline(p_bal.f_end_hz / 1e3, 'k--', 'f_{end} = 400 kHz');
    grid on; xlabel('Time (ms)'); ylabel('Frequency (kHz)');
    title('Plot 3: Instantaneous Frequency Trajectory (Linear Frequency Modulation)');
    saveas(fig3, fullfile(plots_dir, '03_instantaneous_frequency.png'));
    close(fig3);
    fprintf('  [+] Plot 3 saved: 03_instantaneous_frequency.png\n');

    % Figure 4: FFT Spectrum
    fig4 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    X_fft = fft(wf_bal.signal, n_fft);
    mag_db = 20 * log10(abs(X_fft(1:(n_fft/2 + 1))) / max(abs(X_fft)));
    plot(freqs_khz, mag_db, 'g', 'LineWidth', 1.2); hold on;
    xline(p_bal.f_start_hz / 1e3, 'r--', 'f_0 = 200 kHz');
    xline(p_bal.f_end_hz / 1e3, 'r--', 'f_1 = 400 kHz');
    xlim([0, 1000]); ylim([-65, 5]); grid on;
    xlabel('Frequency (kHz)'); ylabel('Normalized Magnitude (dB)');
    title('Plot 4: FFT Spectrum (Passband: 200 - 400 kHz, >50 dB Sidelobe Suppression)');
    saveas(fig4, fullfile(plots_dir, '04_fft_spectrum.png'));
    close(fig4);
    fprintf('  [+] Plot 4 saved: 04_fft_spectrum.png\n');

    % Figure 5: Spectrogram
    fig5 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    [S, F, T] = spectrogram(wf_bal.signal, hann(256), 192, 512, cfg.Fs);
    surf(T * 1000, F / 1e3, 20*log10(abs(S) + 1e-12), 'EdgeColor', 'none');
    axis xy; axis tight; view(0, 90); colormap('hot'); colorbar;
    ylim([0, 600]); caxis([-50, 0]);
    xlabel('Time (ms)'); ylabel('Frequency (kHz)');
    title('Plot 5: STFT Spectrogram (Linear Time-Frequency Energy Ridge)');
    saveas(fig5, fullfile(plots_dir, '05_spectrogram.png'));
    close(fig5);
    fprintf('  [+] Plot 5 saved: 05_spectrogram.png\n');

    % Figure 6: Quantization Error Time Series
    fig6 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    plot(wf_bal.t(1:1000) * 1000, qm_bal.quant_error_lsb(1:1000), 'Color', [0.85, 0.55, 0.1]); hold on;
    yline(0.5, 'r--', '+0.5 LSB Limit');
    yline(-0.5, 'r--', '-0.5 LSB Limit');
    ylim([-0.7, 0.7]); grid on;
    xlabel('Time (ms)'); ylabel('Quantization Error (LSB)');
    title(sprintf('Plot 6: 12-Bit DAC Quantization Error (Max = %.3f LSB, RMS = %.3f LSB)', ...
                  qm_bal.max_error_lsb, qm_bal.rms_error_lsb));
    saveas(fig6, fullfile(plots_dir, '06_dac_quantization_error.png'));
    close(fig6);
    fprintf('  [+] Plot 6 saved: 06_dac_quantization_error.png\n');

    % Figure 7: DAC Code Distribution Histogram
    fig7 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    histogram(double(dac_bal), 64, 'FaceColor', [0.2, 0.6, 0.8], 'EdgeColor', 'k');
    grid on; xlabel('12-bit DAC Integer Code'); ylabel('Sample Count');
    title(sprintf('Plot 7: DAC Output Code Distribution (Mean = %.1f, Midscale = %d)', ...
                  mean(double(dac_bal)), cfg.DAC_midscale));
    saveas(fig7, fullfile(plots_dir, '07_dac_code_histogram.png'));
    close(fig7);
    fprintf('  [+] Plot 7 saved: 07_dac_code_histogram.png\n');

    % Figure 8: Profile Comparison
    fig8 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    for i = 1:length(profiles)
        p = profiles(i);
        X = fft(waveforms{i}.signal, n_fft);
        m_db = 20 * log10(abs(X(1:(n_fft/2 + 1))) / max(abs(X)));
        plot(freqs_khz, m_db, 'Color', colors{i}, 'LineWidth', 1.5); hold on;
    end
    xlim([50, 600]); ylim([-60, 5]); grid on;
    xlabel('Frequency (kHz)'); ylabel('Normalized Magnitude (dB)');
    title('Plot 8: Transmission Profile Spectral Comparison (Low Freq vs Balanced vs High Freq)');
    legend('LOW\_FREQUENCY (100-220 kHz)', 'BALANCED (200-400 kHz)', 'HIGH\_FREQUENCY (350-500 kHz)', 'Location', 'northeast');
    saveas(fig8, fullfile(plots_dir, '08_profile_comparison.png'));
    close(fig8);
    fprintf('  [+] Plot 8 saved: 08_profile_comparison.png\n');

    % Dynamic Simulation Setup (150 Pings)
    num_pings = 150;
    t_axis = (0:(num_pings - 1)) * cfg.PRI_s;
    turb_traj = 15.0 + 75.0 ./ (1.0 + exp(-10.0 * (t_axis - 1.2))) - 45.0 ./ (1.0 + exp(-10.0 * (t_axis - 2.2)));
    rng(42);
    turb_traj = max(0, min(100, turb_traj + 3.0 * randn(1, num_pings)));

    Q_hist = zeros(num_pings, 1);
    cand_hist = zeros(num_pings, 1);
    active_hist = zeros(num_pings, 1);
    amp_hist = zeros(num_pings, 1);
    power_hist = zeros(num_pings, 1);

    ctrl_state = struct('active_profile_id', 2, 'pending_profile_id', 2, ...
                        'candidate_profile_id', 2, 'debounce_counter', 0, ...
                        'amplitude', 0.70, 'ping_index', 0, 'time_s', 0.0);

    for p_idx = 1:num_pings
        env = struct('depth_m', 50, 'temperature_c', 20, 'salinity_psu', 35, ...
                     'turbidity', turb_traj(p_idx), 'ambient_noise_db', 55.0);
        [Q_val, ~] = channel_model(env, cfg);
        [ctrl_state, dec_log] = adaptive_controller(Q_val, ctrl_state, cfg);
        pm = power_model(cfg.Tp_s, ctrl_state.amplitude, cfg);

        Q_hist(p_idx) = Q_val;
        cand_hist(p_idx) = dec_log.raw_candidate_id;
        active_hist(p_idx) = ctrl_state.active_profile_id;
        amp_hist(p_idx) = ctrl_state.amplitude;
        power_hist(p_idx) = pm.average_power_w;
    end

    % Figure 9: Channel Quality Timeline
    fig9 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    plot(t_axis, Q_hist, 'b-', 'LineWidth', 1.5); hold on;
    yline(cfg.thresh_bal_to_high, 'g--', 'Promote to High (0.75)');
    yline(cfg.thresh_high_to_bal, 'g:', 'Demote from High (0.65)');
    yline(cfg.thresh_low_to_bal, 'r:', 'Promote from Low (0.40)');
    yline(cfg.thresh_bal_to_low, 'r--', 'Demote to Low (0.30)');
    ylim([0, 1]); grid on; xlabel('Mission Time (seconds)'); ylabel('Quality Score Q');
    title('Plot 9: Predicted Channel Quality Score Timeline with Directional Thresholds');
    legend('Score Q', 'Location', 'southeast');
    saveas(fig9, fullfile(plots_dir, '09_channel_quality_timeline.png'));
    close(fig9);
    fprintf('  [+] Plot 9 saved: 09_channel_quality_timeline.png\n');

    % Figure 10: Candidate Profile Timeline
    fig10 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    stairs(t_axis, cand_hist, 'm-', 'LineWidth', 1.5);
    yticks([1, 2, 3]); yticklabels({'LOW\_FREQ', 'BALANCED', 'HIGH\_FREQ'});
    ylim([0.5, 3.5]); grid on; xlabel('Mission Time (seconds)'); ylabel('Candidate State');
    title('Plot 10: Raw Candidate Profile Timeline (Driven by Hysteresis Logic)');
    saveas(fig10, fullfile(plots_dir, '10_candidate_profile_timeline.png'));
    close(fig10);
    fprintf('  [+] Plot 10 saved: 10_candidate_profile_timeline.png\n');

    % Figure 11: Active Profile Timeline
    fig11 = figure('Visible', 'off', 'Position', [100, 100, 900, 450]);
    stairs(t_axis, active_hist, 'k-', 'LineWidth', 2.0);
    yticks([1, 2, 3]); yticklabels({'LOW\_FREQ', 'BALANCED', 'HIGH\_FREQ'});
    ylim([0.5, 3.5]); grid on; xlabel('Mission Time (seconds)'); ylabel('Active Profile');
    title('Plot 11: Committed Active Profile Timeline (Atomic Ping-Boundary Latching)');
    saveas(fig11, fullfile(plots_dir, '11_active_profile_timeline.png'));
    close(fig11);
    fprintf('  [+] Plot 11 saved: 11_active_profile_timeline.png\n');

    % Figure 12: Hysteresis / Debounce Demonstration Detail
    fig12 = figure('Visible', 'off', 'Position', [100, 100, 900, 600]);
    zoom_m = (t_axis >= 1.0) & (t_axis <= 1.8);
    subplot(2, 1, 1);
    plot(t_axis(zoom_m), Q_hist(zoom_m), 'b.-', 'LineWidth', 1.2); hold on;
    yline(0.40, 'r:', 'Low->Bal (0.40)'); yline(0.30, 'r--', 'Bal->Low (0.30)');
    ylabel('Quality Score Q'); grid on;
    title('Plot 12: Hysteresis & Debounce Filter Action during Sediment Plume Event');
    subplot(2, 1, 2);
    stairs(t_axis(zoom_m), cand_hist(zoom_m), 'm:', 'LineWidth', 1.2); hold on;
    stairs(t_axis(zoom_m), active_hist(zoom_m), 'k-', 'LineWidth', 2.0);
    yticks([1, 2, 3]); yticklabels({'LOW\_FREQ', 'BALANCED', 'HIGH\_FREQ'});
    ylabel('Profile State'); xlabel('Time (seconds)'); grid on;
    legend('Candidate Profile', 'Latched Active Profile', 'Location', 'southeast');
    saveas(fig12, fullfile(plots_dir, '12_hysteresis_debounce_demo.png'));
    close(fig12);
    fprintf('  [+] Plot 12 saved: 12_hysteresis_debounce_demo.png\n');

    % Figure 13: Estimated Power Summary & Pulse Duration Sensitivity Analysis
    fig13 = figure('Visible', 'off', 'Position', [100, 100, 1000, 450]);
    subplot(1, 2, 1);
    plot(t_axis, power_hist, 'r-', 'LineWidth', 1.5);
    ylim([0, 0.8]); grid on; xlabel('Mission Time (seconds)'); ylabel('Transmitter Average Power (W)');
    title('Transmitter Average Power across Dynamic Mission');

    subplot(1, 2, 2);
    durations_ms = [1.0, 2.0, 3.0];
    p_sens = zeros(3, 3);
    for d_idx = 1:3
        d_val = durations_ms(d_idx) / 1000.0;
        p_sens(d_idx, 1) = power_model(d_val, 1.00, cfg).average_power_w;
        p_sens(d_idx, 2) = power_model(d_val, 0.70, cfg).average_power_w;
        p_sens(d_idx, 3) = power_model(d_val, 0.40, cfg).average_power_w;
    end
    bar(durations_ms, p_sens);
    grid on; xlabel('Pulse Duration (ms) [PRI = 20 ms]'); ylabel('Average Power (W)');
    title('Sensitivity Analysis: Pulse Duration vs Power');
    legend('A = 1.0 (Low Freq)', 'A = 0.7 (Balanced)', 'A = 0.4 (High Freq)', 'Location', 'northwest');
    saveas(fig13, fullfile(plots_dir, '13_estimated_power_summary.png'));
    close(fig13);
    fprintf('  [+] Plot 13 saved: 13_estimated_power_summary.png\n');

    % --------------------------------------------------------------------------
    % Phase 6: Run 23-Point Automated Validation Suite
    % --------------------------------------------------------------------------
    fprintf('\n[*] Phase 6: Executing 23-Point Automated Validation Suite...\n');
    val_results = run_validation_suite();

    % Final report
    fprintf('==============================================================================\n');
    fprintf('  SIMULATION EXECUTION COMPLETE\n');
    fprintf('  • Status:               Algorithmically Credible, Physically Unverified\n');
    fprintf('  • Validation Suite:     %d / %d Tests Passed\n', val_results.tests_passed, val_results.total_tests);
    fprintf('  • Generated Plots:      %s (13 figures)\n', plots_dir);
    fprintf('  • Exported Headers:     %s (4 C headers)\n', headers_dir);
    fprintf('==============================================================================\n');
end
