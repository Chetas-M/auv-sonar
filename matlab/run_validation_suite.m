% ==============================================================================
% File: run_validation_suite.m
% Description: Automated 15-point engineering validation test suite for
% SIH Problem 26058. Verifies DSP math, DAC quantization, hysteresis,
% debounce, power model, and firmware C header round-trip integrity.
% ==============================================================================

function results = run_validation_suite()
    fprintf('\n==============================================================================\n');
    fprintf('  RUNNING 15-POINT AUTOMATED VALIDATION SUITE (SIH Problem 26058)\n');
    fprintf('==============================================================================\n');

    cfg = config_sonar();
    profiles = profile_definitions();
    p_bal = profiles(2); % Balanced profile (200-400 kHz, 2 ms)
    [wf, diag] = generate_lfm_chirp(p_bal.f_start_hz, p_bal.f_end_hz, p_bal.duration_s, cfg.Fs, 1.0);
    [dac_codes, q_metrics] = dac_quantize(wf.signal, cfg);

    tests_passed = 0;
    total_tests = 15;

    % Test 1: Sample Count
    t1_pass = (wf.Np == 8000) && (length(wf.signal) == 8000) && (length(dac_codes) == 8000);
    report_test(1, 'Correct Sample Count (8000 samples @ 4 MSPS, 2 ms)', t1_pass);
    tests_passed = tests_passed + t1_pass;

    % Test 2: Pulse Duration
    t2_pass = abs(wf.t(end) - (cfg.Tp_s - cfg.Ts)) < 1e-9;
    report_test(2, 'Correct Pulse Duration (2.0 ms exact time base)', t2_pass);
    tests_passed = tests_passed + t2_pass;

    % Test 3: DAC Code Range (0 <= code <= 4095)
    t3_pass = all(dac_codes >= cfg.DAC_min_code) && all(dac_codes <= cfg.DAC_max_code) && ...
              ~q_metrics.has_overflow && ~q_metrics.has_underflow;
    report_test(3, 'DAC Code Dynamic Range (0 <= code <= 4095, no clipping)', t3_pass);
    tests_passed = tests_passed + t3_pass;

    % Test 4: Midscale Correctness (at zero signal, code is 2048)
    [wf_zero, ~] = generate_lfm_chirp(p_bal.f_start_hz, p_bal.f_end_hz, p_bal.duration_s, cfg.Fs, 0.0);
    [dac_zero, ~] = dac_quantize(wf_zero.signal, cfg);
    t4_pass = all(dac_zero == cfg.DAC_midscale);
    report_test(4, 'DAC Midscale Correctness (Code = 2048 at zero AC amplitude)', t4_pass);
    tests_passed = tests_passed + t4_pass;

    % Test 5: Hann Window Endpoints (tapers to zero)
    t5_pass = (wf.window(1) < 1e-6) && (wf.window(end) < 1e-6);
    report_test(5, 'Hann Window Endpoints (Starts and ends at 0.0 to suppress transients)', t5_pass);
    tests_passed = tests_passed + t5_pass;

    % Test 6: LFM Instantaneous Frequency Slope (df/dt = k = 100 MHz/s)
    mid_idx = round(0.20 * wf.Np) : round(0.80 * wf.Np);
    poly_fit = polyfit(wf.t(mid_idx), wf.inst_freq_hz(mid_idx), 1);
    k_empirical = poly_fit(1);
    k_theoretical = (p_bal.f_end_hz - p_bal.f_start_hz) / p_bal.duration_s;
    slope_err_pct = abs((k_empirical - k_theoretical) / k_theoretical) * 100.0;
    t6_pass = (slope_err_pct < 0.1);
    report_test(6, sprintf('LFM Instantaneous Frequency Slope (Error = %.4f%% < 0.1%%)', slope_err_pct), t6_pass);
    tests_passed = tests_passed + t6_pass;

    % Test 7: Start Frequency Correctness
    f_start_est = poly_fit(2);
    f_start_err_pct = abs((f_start_est - p_bal.f_start_hz) / p_bal.f_start_hz) * 100.0;
    t7_pass = (f_start_err_pct < 0.1);
    report_test(7, sprintf('Start Frequency Correctness (f_0 = %.1f kHz, Error = %.4f%%)', f_start_est/1e3, f_start_err_pct), t7_pass);
    tests_passed = tests_passed + t7_pass;

    % Test 8: End Frequency Correctness
    f_end_est = f_start_est + k_empirical * p_bal.duration_s;
    f_end_err_pct = abs((f_end_est - p_bal.f_end_hz) / p_bal.f_end_hz) * 100.0;
    t8_pass = (f_end_err_pct < 0.1);
    report_test(8, sprintf('End Frequency Correctness (f_1 = %.1f kHz, Error = %.4f%%)', f_end_est/1e3, f_end_err_pct), t8_pass);
    tests_passed = tests_passed + t8_pass;

    % Test 9: FFT In-Band Energy Concentration (>99.0%)
    n_fft = wf.Np * 4;
    fft_v = fft(wf.signal, n_fft);
    psd = abs(fft_v(1:(n_fft/2 + 1))) .^ 2;
    freqs = (0:(n_fft/2))' * (cfg.Fs / n_fft);
    in_band_mask = (freqs >= (p_bal.f_start_hz - 5000)) & (freqs <= (p_bal.f_end_hz + 5000));
    in_band_ratio = sum(psd(in_band_mask)) / sum(psd);
    t9_pass = (in_band_ratio >= 0.990);
    report_test(9, sprintf('FFT Spectral Energy Concentration (In-band = %.4f%% >= 99.0%%)', in_band_ratio * 100.0), t9_pass);
    tests_passed = tests_passed + t9_pass;

    % Test 10: Hysteresis Stability (Suppression of Deadband Fluctuations)
    state_init = struct('active_profile_id', 2, 'candidate_profile_id', 2, ...
                        'debounce_counter', 0, 'amplitude', 0.7, 'ping_index', 0, 'time_s', 0.0);
    % In BALANCED: Q fluctuates between 0.66 and 0.72 (inside deadband [0.65, 0.75])
    [s_h1, ~] = adaptive_controller(0.72, state_init, cfg);
    [s_h2, ~] = adaptive_controller(0.66, s_h1, cfg);
    t10_pass = (s_h1.active_profile_id == 2) && (s_h2.active_profile_id == 2);
    report_test(10, 'Hysteresis Deadband Stability (No profile switching within deadband)', t10_pass);
    tests_passed = tests_passed + t10_pass;

    % Test 11: Debounce Persistence (Requires N = 2 consecutive cycles)
    % Single spike to Q = 0.85 (Clear candidate)
    [s_d1, ~] = adaptive_controller(0.85, state_init, cfg);
    % Should still be BALANCED because it only lasted 1 cycle
    check_not_yet = (s_d1.active_profile_id == 2) && (s_d1.candidate_profile_id == 3);
    % Second consecutive cycle at Q = 0.85
    [s_d2, ~] = adaptive_controller(0.85, s_d1, cfg);
    % Now committed to CLEAR
    t11_pass = check_not_yet && (s_d2.active_profile_id == 3);
    report_test(11, 'Debounce Persistence (Requires N=2 consecutive cycles before commit)', t11_pass);
    tests_passed = tests_passed + t11_pass;

    % Test 12: Profile Switching Only at Ping Boundaries
    % Verify that time increments strictly by PRI (0.020 s) and state is latched atomically
    t12_pass = (s_d2.time_s == 2 * cfg.PRI_s) && (s_d2.ping_index == 2);
    report_test(12, 'Atomic Ping-Boundary Latching (State changes commit strictly at PRI)', t12_pass);
    tests_passed = tests_passed + t12_pass;

    % Test 13: Power Calculation Accuracy
    % At 2 ms / 20 ms, D = 10%. Active = 5W, Idle = 0.045W -> P_avg = 5*0.1 + 0.045*0.9 = 0.5405 W
    p_met = power_model(0.002, 1.0, cfg);
    expected_p = (5.0 * 0.10) + (0.045 * 0.90);
    t13_pass = abs(p_met.average_power_w - expected_p) < 1e-4;
    report_test(13, sprintf('Power Model Analytical Accuracy (P_avg = %.4f W)', p_met.average_power_w), t13_pass);
    tests_passed = tests_passed + t13_pass;

    % Test 14: C Header Export Integrity
    test_export_dir = fullfile(pwd, 'outputs_matlab', 'headers_test');
    if ~exist(test_export_dir, 'dir')
        mkdir(test_export_dir);
    end
    export_c_headers(test_export_dir);
    test_header_path = fullfile(test_export_dir, 'chirp_balanced.h');
    t14_pass = exist(test_header_path, 'file') == 2;
    report_test(14, 'C Header Export Integrity (Valid header files and macros generated)', t14_pass);
    tests_passed = tests_passed + t14_pass;

    % Test 15: Bit-Exact Waveform Round-Trip Validation
    % Read back C header and compare parsed uint16 samples against MATLAB array
    fid = fopen(test_header_path, 'r');
    content = fread(fid, '*char')';
    fclose(fid);
    tokens = regexp(content, '0x([0-9A-Fa-f]{4})', 'tokens');
    parsed_samples = zeros(length(tokens), 1, 'uint16');
    for idx = 1:length(tokens)
        parsed_samples(idx) = uint16(hex2dec(tokens{idx}{1}));
    end
    t15_pass = (length(parsed_samples) == length(dac_codes)) && all(parsed_samples == dac_codes);
    report_test(15, sprintf('Bit-Exact Waveform Round-Trip (All %d samples matched bit-for-bit)', length(parsed_samples)), t15_pass);
    tests_passed = tests_passed + t15_pass;

    % Clean up test export directory
    delete(fullfile(test_export_dir, '*'));
    rmdir(test_export_dir);

    % Summary
    fprintf('------------------------------------------------------------------------------\n');
    fprintf('  VALIDATION SUMMARY: %d / %d TESTS PASSED (%.1f%%)\n', ...
            tests_passed, total_tests, (tests_passed / total_tests) * 100.0);
    fprintf('==============================================================================\n\n');

    results = struct('tests_passed', tests_passed, 'total_tests', total_tests, 'all_passed', tests_passed == total_tests);
end

function report_test(num, name, passed)
    if passed
        status = '[PASSED]';
    else
        status = '[FAILED]';
    end
    fprintf('  Check %02d: %-60s %s\n', num, name, status);
end
