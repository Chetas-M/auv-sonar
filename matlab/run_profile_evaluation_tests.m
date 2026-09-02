% ==============================================================================
% File: run_profile_evaluation_tests.m
% Description: Automated 12-point unit test suite for Priority 1:
% Profile Performance Evaluation & Selection Logic (SIH Problem 26058).
% ==============================================================================

function results = run_profile_evaluation_tests()
    fprintf('\n==============================================================================\n');
    fprintf('  RUNNING PRIORITY 1 PROFILE EVALUATION TEST SUITE (12 Checks)\n');
    fprintf('==============================================================================\n');

    cfg = config_sonar();
    env_baseline = struct('depth_m', 50.0, 'temperature_c', 20.0, ...
                          'salinity_psu', 35.0, 'turbidity', 0.0, 'ambient_noise_db', 0.0);
    [metrics, dec] = evaluate_profile_performance(50.0, env_baseline, 'SURVEY', cfg);

    tests_passed = 0;
    total_tests = 12;

    % Test 1: All 3 profiles evaluate successfully
    t1 = (length(metrics) == 3);
    report_test(1, 'All 3 Profiles Evaluated Successfully', t1);
    tests_passed = tests_passed + t1;

    % Test 2: No NaN or Inf in any returned metric
    t2 = true;
    for i = 1:3
        m = metrics{i};
        if isnan(m.alpha_band_db_km) || isinf(m.alpha_band_db_km) || ...
           isnan(m.transmission_loss_db) || isinf(m.transmission_loss_db) || ...
           isnan(m.relative_margin_db) || isinf(m.relative_margin_db) || ...
           any(isnan(m.alpha_points_db_km)) || any(isinf(m.alpha_points_db_km))
            t2 = false;
        end
    end
    report_test(2, 'No NaN or Inf in Evaluated Acoustic Metrics', t2);
    tests_passed = tests_passed + t2;

    % Test 3: Positive finite attenuation across all bands
    t3 = true;
    for i = 1:3
        if metrics{i}.alpha_band_db_km <= 0 || any(metrics{i}.alpha_points_db_km <= 0)
            t3 = false;
        end
    end
    report_test(3, 'Positive Finite Attenuation Across All 5 Frequency Points', t3);
    tests_passed = tests_passed + t3;

    % Test 4: Monotonic Transmission Loss with range
    [m10, ~] = evaluate_profile_performance(10.0, env_baseline, 'SURVEY', cfg);
    [m50, ~] = evaluate_profile_performance(50.0, env_baseline, 'SURVEY', cfg);
    [m200, ~] = evaluate_profile_performance(200.0, env_baseline, 'SURVEY', cfg);
    t4 = true;
    for i = 1:3
        if ~(m10{i}.transmission_loss_db < m50{i}.transmission_loss_db && ...
             m50{i}.transmission_loss_db < m200{i}.transmission_loss_db)
            t4 = false;
        end
    end
    report_test(4, 'Monotonic Transmission Loss Increase with Range', t4);
    tests_passed = tests_passed + t4;

    % Test 5: Baseline attenuation ordering across frequency bands
    t5 = (metrics{1}.alpha_band_db_km < metrics{2}.alpha_band_db_km) && ...
         (metrics{2}.alpha_band_db_km < metrics{3}.alpha_band_db_km);
    report_test(5, 'Baseline Band Attenuation Ordering (HIGH > BALANCED > LOW)', t5);
    tests_passed = tests_passed + t5;

    % Test 6: Theoretical range resolution: BALANCED has the finest resolution
    t6 = (metrics{2}.range_resolution_mm < metrics{3}.range_resolution_mm) && ...
         (metrics{3}.range_resolution_mm < metrics{1}.range_resolution_mm) && ...
         (abs(metrics{2}.range_resolution_mm - 3.75) < 0.2);
    report_test(6, 'Range Resolution: BALANCED has Finest Resolution (3.75 mm)', t6);
    tests_passed = tests_passed + t6;

    % Test 7: Theoretical directivity metric: HIGH_FREQUENCY has highest directivity
    t7 = (metrics{3}.relative_directivity > metrics{2}.relative_directivity) && ...
         (metrics{2}.relative_directivity > metrics{1}.relative_directivity);
    report_test(7, 'Directivity: HIGH_FREQUENCY has Highest Directivity (1.417x)', t7);
    tests_passed = tests_passed + t7;

    % Test 8: Band confinement of 5 evaluation frequency points
    t8 = (abs(metrics{1}.f_points_khz(1) - 100.0) < 0.01) && (abs(metrics{1}.f_points_khz(end) - 220.0) < 0.01) && ...
         (abs(metrics{2}.f_points_khz(1) - 200.0) < 0.01) && (abs(metrics{2}.f_points_khz(end) - 400.0) < 0.01) && ...
         (abs(metrics{3}.f_points_khz(1) - 350.0) < 0.01) && (abs(metrics{3}.f_points_khz(end) - 500.0) < 0.01);
    report_test(8, 'Evaluation Frequency Points Strictly Confined to Chirp Bands', t8);
    tests_passed = tests_passed + t8;

    % Test 9: Fallback to LOW_FREQUENCY at long range (propagation limited)
    [m200_all, dec200] = evaluate_profile_performance(200.0, env_baseline, 'SURVEY', cfg);
    t9 = strcmp(dec200.candidate_name, 'LOW_FREQUENCY') && ...
         m200_all{1}.is_viable && ~m200_all{2}.is_viable && ~m200_all{3}.is_viable;
    report_test(9, 'Viability Fallback: LOW_FREQUENCY Selected at Long Range (200m)', t9);
    tests_passed = tests_passed + t9;

    % Test 10: Survey Mode selects BALANCED at short/medium range
    [~, dec_surv] = evaluate_profile_performance(25.0, env_baseline, 'SURVEY', cfg);
    t10 = strcmp(dec_surv.candidate_name, 'BALANCED') && (dec_surv.candidate_profile_id == 2);
    report_test(10, 'Survey Mode Selects BALANCED at Short Range (25m)', t10);
    tests_passed = tests_passed + t10;

    % Test 11: Directivity Mode selects HIGH_FREQUENCY at short/medium range
    [~, dec_dir] = evaluate_profile_performance(25.0, env_baseline, 'DIRECTIVITY', cfg);
    t11 = strcmp(dec_dir.candidate_name, 'HIGH_FREQUENCY') && (dec_dir.candidate_profile_id == 3);
    report_test(11, 'Directivity Mode Selects HIGH_FREQUENCY at Short Range (25m)', t11);
    tests_passed = tests_passed + t11;

    % Test 12: Determinism check: identical inputs yield identical outputs
    [m_a, d_a] = evaluate_profile_performance(50.0, env_baseline, 'SURVEY', cfg);
    [m_b, d_b] = evaluate_profile_performance(50.0, env_baseline, 'SURVEY', cfg);
    t12 = (d_a.candidate_profile_id == d_b.candidate_profile_id) && ...
          (d_a.profile_selection_confidence == d_b.profile_selection_confidence) && ...
          (m_a{1}.transmission_loss_db == m_b{1}.transmission_loss_db);
    report_test(12, 'Determinism Check: Identical Inputs Yield Bit-Exact Outputs', t12);
    tests_passed = tests_passed + t12;

    % Summary
    fprintf('------------------------------------------------------------------------------\n');
    fprintf('  PROFILE EVALUATION VALIDATION: %d / %d TESTS PASSED (%.1f%%)\n', ...
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
