% ==============================================================================
% File: evaluate_profile_performance.m
% Description: Evaluates frequency-dependent acoustic propagation, transmission
% loss, theoretical range resolution, and relative theoretical directivity for
% sonar transmission profiles.
%
% Implements Priority 1 of SIH Problem 26058: Profile Performance Evaluation &
% Physical Justification of Adaptive Profile Selection.
%
% IMPORTANT DISCLAIMER:
% Transmission loss is a simplified relative one-way propagation model for profile
% comparison. It does NOT claim to model physical two-way echo reflection, target
% strength, ocean-acoustic multipath, bottom bounce, or measured transducer beam patterns.
% ==============================================================================

function [all_metrics, decision] = evaluate_profile_performance(range_m, env_inputs, mission_objective, cfg)
    if nargin < 4 || isempty(cfg)
        cfg = config_sonar();
    end
    if nargin < 3 || isempty(mission_objective)
        mission_objective = 'SURVEY'; % Default: 'SURVEY' (resolution), 'DIRECTIVITY', or 'PENETRATION'
    end
    if nargin < 2 || isempty(env_inputs)
        env_inputs = struct('depth_m', 50.0, 'temperature_c', 20.0, ...
                            'salinity_psu', 35.0, 'turbidity', 0.0, 'noise_penalty_db', 0.0);
    end
    if nargin < 1 || isempty(range_m)
        range_m = 50.0;
    end

    % 1. Extract and clamp environmental parameters
    D = max(0.0, min(1000.0, env_inputs.depth_m));
    T = max(-2.0, min(40.0, env_inputs.temperature_c));
    S = max(0.0, min(45.0, env_inputs.salinity_psu));
    turb = max(0.0, min(100.0, env_inputs.turbidity));

    % Extract noise penalty (support both noise_penalty_db and legacy ambient_noise_db)
    if isfield(env_inputs, 'noise_penalty_db')
        noise_penalty = env_inputs.noise_penalty_db;
    elseif isfield(env_inputs, 'ambient_noise_db')
        noise_penalty = env_inputs.ambient_noise_db;
    else
        noise_penalty = 0.0;
    end

    % 2. Sound Speed via Mackenzie (1981) formula
    c = 1448.96 + 4.591*T - 0.05304*(T^2) + 0.0002374*(T^3) + ...
        1.340*(S - 35.0) + 0.0163*D + 0.0001675*(D^2) - ...
        0.01025*T*(S - 35.0) - 0.0000007139*T*(D^3);

    % Viability threshold (relative margin floor in dB)
    % [SIMULATION ASSUMPTION] A profile is viable if relative margin >= -65.0 dB
    % Note: This is a simulation policy parameter used to demonstrate adaptive switching;
    % it is not derived from or calibrated against a physical receiver or hydrophone noise floor.
    if isfield(cfg, 'viability_threshold_db')
        viability_threshold_db = cfg.viability_threshold_db;
    else
        viability_threshold_db = -65.0;
    end

    profiles = profile_definitions();
    num_profiles = length(profiles);
    all_metrics = cell(num_profiles, 1);

    % 3. Evaluate each profile independently across 5 frequency points
    for p_idx = 1:num_profiles
        p = profiles(p_idx);
        
        % 5 evenly spaced frequency points across active chirp band
        f_pts_hz = linspace(p.f_start_hz, p.f_end_hz, 5);
        f_pts_khz = f_pts_hz / 1000.0;
        alpha_pts_db_km = zeros(1, 5);

        for i = 1:5
            f_k = f_pts_khz(i);
            % Ainslie & McColm (1998) chemical relaxation absorption (dB/km)
            % Includes hydrostatic pressure reduction factor P2 = exp(-D_km / 6) = exp(-D / 6000.0)
            f1 = 0.78 * sqrt(S / 35.0) * exp(T / 26.0);
            A1 = 0.106 * exp((T - 20.0) / 27.0);
            f2 = 42.0 * exp(T / 17.0);
            A2 = 0.52 * (1.0 + T / 43.0) * (S / 35.0);
            P2 = exp(-D / 6000.0);
            A3 = 0.00049 * exp(-(T / 27.0) - (D / 17000.0));
            
            alpha_chem = (A1 * f1 * (f_k^2)) / (f1^2 + f_k^2) + ...
                         (A2 * P2 * f2 * (f_k^2)) / (f2^2 + f_k^2) + ...
                         A3 * (f_k^2);

            % Optional scenario sensitivity heuristic for turbidity scattering
            % [UNVALIDATED HEURISTIC]: Rayleigh-type f^2 scattering approximation
            if turb > 0
                alpha_turb = 35.0 * (turb / 100.0) * ((f_k / 300.0)^2);
            else
                alpha_turb = 0.0;
            end

            alpha_pts_db_km(i) = alpha_chem + alpha_turb;
        end

        % Band-averaged attenuation (dB/km)
        alpha_band_db_km = mean(alpha_pts_db_km);

        % Simplified relative transmission loss (1-way spherical spreading + absorption)
        % TL(R) = 20*log10(R) + alpha*(R/1000)
        r_eff = max(1.0, range_m);
        tl_db = 20.0 * log10(r_eff) + alpha_band_db_km * (r_eff / 1000.0);

        % Normalized relative propagation margin (dB)
        % Transmit reference is 0 dB; noise penalty subtracts from margin
        rel_margin_db = -tl_db - noise_penalty;

        % Viability determination
        is_viable = (rel_margin_db >= viability_threshold_db);

        % Idealized bandwidth-based theoretical range resolution: Delta_R = c / (2B)
        delta_r_m = c / (2.0 * p.bandwidth_hz);
        delta_r_mm = delta_r_m * 1000.0;

        % Relative theoretical directivity proxy: Dir_rel = fc / 300 kHz
        % [RELATIVE THEORETICAL METRIC - assumes fixed physical aperture diameter D]
        dir_rel = p.f_center_hz / 300.0e3;

        % Package structured profile evaluation
        m = struct();
        m.profile_id = p.id;
        m.name = p.name;
        m.f_start_hz = p.f_start_hz;
        m.f_end_hz = p.f_end_hz;
        m.f_center_hz = p.f_center_hz;
        m.bandwidth_hz = p.bandwidth_hz;
        m.f_points_khz = f_pts_khz;
        m.alpha_points_db_km = alpha_pts_db_km;
        m.alpha_band_db_km = alpha_band_db_km;
        m.transmission_loss_db = tl_db;
        m.relative_margin_db = rel_margin_db;
        m.is_viable = is_viable;
        m.viability_threshold_db = viability_threshold_db;
        m.range_resolution_mm = delta_r_mm;
        m.relative_directivity = dir_rel;
        m.sound_speed_m_s = c;
        m.range_m = range_m;
        m.assumptions = { ...
            'Five-point discrete frequency approximation across chirp band', ...
            'Ainslie-McColm (1998) chemical relaxation absorption model', ...
            'Simplified spherical spreading one-way transmission loss 20*log10(R) + alpha*R', ...
            'Normalized relative source level (0 dB reference, no absolute acoustic SPL claimed)', ...
            '[SIMULATION ASSUMPTION] Relative viability threshold = -65 dB (policy parameter, not physical detection limit)', ...
            'Theoretical range resolution assumes matched-filter pulse compression c/(2B)', ...
            'Theoretical directivity metric is a frequency proxy (fc/300kHz) under fixed aperture assumption', ...
            'Turbidity scattering is an unvalidated sensitivity heuristic when turb > 0' ...
        };

        all_metrics{p_idx} = m;
    end

    % Convert cell array to struct array for easy indexing
    metrics_arr = [all_metrics{1}, all_metrics{2}, all_metrics{3}];

    % 4. Multi-Tier Decision Hierarchy: Viability Filter + Mission Objective
    p1_viable = metrics_arr(1).is_viable;
    p2_viable = metrics_arr(2).is_viable;
    p3_viable = metrics_arr(3).is_viable;

    candidate_id = 1; % Default fail-safe: LOW_FREQUENCY (lowest attenuation)
    selection_rationale = '';

    switch upper(mission_objective)
        case 'DIRECTIVITY'
            if p3_viable
                candidate_id = 3;
                selection_rationale = 'HIGH_FREQUENCY selected: propagation is viable and directivity objective is active (narrowest theoretical beam).';
            elseif p2_viable
                candidate_id = 2;
                selection_rationale = 'BALANCED selected: HIGH_FREQUENCY falls below simulation viability threshold; BALANCED provides next best directivity.';
            else
                candidate_id = 1;
                selection_rationale = 'LOW_FREQUENCY fallback: higher-frequency profiles fall below viability threshold; LOW experiences lower modeled attenuation.';
            end

        case 'PENETRATION'
            candidate_id = 1;
            selection_rationale = 'LOW_FREQUENCY selected: penetration objective prioritizes lowest frequency-dependent attenuation.';

        otherwise % 'SURVEY' (Default)
            if p2_viable
                candidate_id = 2;
                selection_rationale = 'BALANCED selected: propagation is viable and BALANCED delivers superior range resolution (3.75 mm limit).';
            elseif p1_viable
                candidate_id = 1;
                selection_rationale = 'LOW_FREQUENCY fallback: BALANCED falls below simulation viability threshold at this range.';
            else
                candidate_id = 1;
                selection_rationale = 'LOW_FREQUENCY fallback: all profiles propagation-limited; selecting profile with lowest modeled transmission loss.';
            end
    end

    % 5. Dual Confidence Metrics
    cand_metric = metrics_arr(candidate_id);
    margin_above_viability = cand_metric.relative_margin_db - viability_threshold_db;

    % Viability confidence: how comfortably viable is the candidate above the threshold
    % C_v = clip((Margin - Margin_threshold) / 15.0, 0.0, 1.0)
    viability_confidence = max(0.0, min(1.0, margin_above_viability / 15.0));

    % Mission selection confidence: utility difference among viable candidates under active mission mode
    % In Survey Mode, utility is normalized sweep bandwidth: U = B / 200 kHz
    % In Directivity Mode, utility is normalized directivity: U = fc / 425 kHz
    viable_indices = find([p1_viable, p2_viable, p3_viable]);
    num_viable = length(viable_indices);

    if num_viable == 0
        selection_confidence = 0.50;
    elseif num_viable == 1
        selection_confidence = 1.00;
    else
        if strcmpi(mission_objective, 'DIRECTIVITY')
            utility_map = [160.0 / 425.0, 300.0 / 425.0, 1.00];
        else
            utility_map = [120.0 / 200.0, 1.00, 150.0 / 200.0];
        end

        winner_u = utility_map(candidate_id);
        other_viable = viable_indices(viable_indices ~= candidate_id);
        if ~isempty(other_viable)
            second_u = max(utility_map(other_viable));
            delta_u = winner_u - second_u;
            selection_confidence = max(0.0, min(1.0, delta_u / 0.25));
        else
            selection_confidence = 1.00;
        end
    end

    % Decision summary output
    decision = struct();
    decision.candidate_profile_id = candidate_id;
    decision.candidate_name = metrics_arr(candidate_id).name;
    decision.mission_objective = mission_objective;
    decision.selection_rationale = selection_rationale;
    decision.viability_confidence = viability_confidence;
    decision.selection_confidence = selection_confidence;
    decision.profile_selection_confidence = viability_confidence; % Canonical preserved
    decision.margin_above_viability_db = margin_above_viability;
    decision.all_viable = [p1_viable, p2_viable, p3_viable];
    decision.range_m = range_m;
end
