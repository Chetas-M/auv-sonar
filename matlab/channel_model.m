% ==============================================================================
% File: channel_model.m
% Description: Simplified predictive simulation acoustic channel model and
% explainable Channel Quality Score (Q) calculator for SIH Problem 26058.
%
% IMPORTANT DISCLAIMER:
% This is a simulation model used to evaluate and justify the transmitter
% adaptation policy. It does NOT claim that the transmitter hardware measures
% real acoustic echoes, real SNR, or oceanographic properties.
% ==============================================================================

function [Q, channel_info] = channel_model(env_inputs, cfg)
    if nargin < 2
        cfg = config_sonar();
    end

    % 1. Input range validation and extraction
    D = max(0.0, min(1000.0, env_inputs.depth_m));         % Depth clamped [0, 1000] m
    T = max(-2.0, min(40.0, env_inputs.temperature_c));    % Temperature clamped [-2, 40] C
    S = max(0.0, min(45.0, env_inputs.salinity_psu));       % Salinity clamped [0, 45] PSU
    turb = max(0.0, min(100.0, env_inputs.turbidity));      % Turbidity clamped [0, 100]
    noise_db = max(30.0, min(100.0, env_inputs.ambient_noise_db)); % Ambient noise [30, 100] dB

    % 2. Estimated Sound Speed via Mackenzie (1981) 9-term formula
    c = 1448.96 + 4.591*T - 0.05304*(T^2) + 0.0002374*(T^3) + ...
        1.340*(S - 35.0) + 0.0163*D + 0.0001675*(D^2) - ...
        0.01025*T*(S - 35.0) - 0.0000007139*T*(D^3);

    % 3. Estimated High-Frequency Chemical Absorption (Ainslie & McColm, 1998)
    % Evaluated at reference frequency (425 kHz) in dB/km
    f_ref_khz = 425.0; 
    % Boric acid relaxation
    f1 = 0.78 * sqrt(S / 35.0) * exp(T / 26.0);
    A1 = 0.106 * exp((T - 20.0) / 27.0);
    % Magnesium sulfate relaxation
    f2 = 42.0 * exp(T / 17.0);
    A2 = 0.52 * (1.0 + T / 43.0) * (S / 35.0);
    % Pure water viscous absorption
    A3 = 0.00049 * exp(-(T / 27.0) - (D / 17000.0));
    
    alpha_chem_db_km = (A1 * f1 * (f_ref_khz^2)) / (f1^2 + f_ref_khz^2) + ...
                       (A2 * f2 * (f_ref_khz^2)) / (f2^2 + f_ref_khz^2) + ...
                       A3 * (f_ref_khz^2);

    % 4. Simulated Turbidity Scattering Penalty (Rayleigh/Mie approximation ~ f^2)
    turb_norm = turb / 100.0;
    alpha_turb_db_km = 35.0 * turb_norm * ((f_ref_khz / 300.0)^2);
    total_alpha_db_km = alpha_chem_db_km + alpha_turb_db_km;

    % 5. Normalized Component Penalties [0.0, 1.0]
    % Penalty 1: Turbidity particulate scattering
    Q_environment = 1.0 - turb_norm;

    % Penalty 2: Acoustic attenuation (normalized against 160 dB/km threshold)
    norm_attn = max(0.0, min(1.0, total_alpha_db_km / 160.0));
    Q_attenuation = 1.0 - norm_attn;

    % Penalty 3: Ambient acoustic noise (normalized between 40 dB calm and 80 dB noisy)
    norm_noise = max(0.0, min(1.0, (noise_db - 40.0) / 40.0));
    Q_noise = 1.0 - norm_noise;

    % 6. Deterministic, Explainable Channel Quality Score Q in [0.0, 1.0]
    % Combined using central configuration weights
    w_env = cfg.w_environment;
    w_attn = cfg.w_attenuation;
    w_noise = cfg.w_noise;

    Q_raw = (w_env * Q_environment) + (w_attn * Q_attenuation) + (w_noise * Q_noise);
    Q = max(0.0, min(1.0, Q_raw));

    % 7. Channel Metadata
    channel_info = struct();
    channel_info.sound_speed_m_s = c;
    channel_info.chem_absorption_db_km = alpha_chem_db_km;
    channel_info.turb_scattering_db_km = alpha_turb_db_km;
    channel_info.total_attenuation_db_km = total_alpha_db_km;
    channel_info.Q_environment = Q_environment;
    channel_info.Q_attenuation = Q_attenuation;
    channel_info.Q_noise = Q_noise;
    channel_info.Q = Q;
end
