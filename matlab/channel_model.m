% ==============================================================================
% File: channel_model.m
% Description: Simplified simulation-only acoustic channel model and explainable
% Channel Quality Score (Q) calculator for SIH Problem 26058.
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

    % Extract environmental parameters
    D = env_inputs.depth_m;         % Depth (m)
    T = env_inputs.temperature_c;   % Temperature (C)
    S = env_inputs.salinity_psu;     % Salinity (PSU)
    turb = env_inputs.turbidity;    % Turbidity (0 to 100 scale)
    noise_db = env_inputs.ambient_noise_db; % Ambient noise level (dB)

    % 1. Estimated Sound Speed via Mackenzie (1981) formula
    c = 1448.96 + 4.591*T - 0.05304*(T^2) + 0.0002374*(T^3) + ...
        1.340*(S - 35.0) + 0.0163*D + 0.0001675*(D^2) - ...
        0.01025*T*(S - 35.0) - 0.0000007139*T*(D^3);

    % 2. Estimated High-Frequency Chemical Absorption (Ainslie & McColm, 1998 simplified)
    % Evaluated at reference high band center (425 kHz) in dB/km
    f_ref_khz = 425.0; 
    % Boric acid contribution
    f1 = 0.78 * sqrt(S / 35.0) * exp(T / 26.0);
    A1 = 0.106 * exp((T - 20.0) / 27.0);
    % Magnesium sulfate contribution
    f2 = 42.0 * exp(T / 17.0);
    A2 = 0.52 * (1.0 + T / 43.0) * (S / 35.0);
    % Viscous pure water contribution
    A3 = 0.00049 * exp(-(T / 27.0) - (D / 17000.0));
    
    alpha_chem_db_km = (A1 * f1 * (f_ref_khz^2)) / (f1^2 + f_ref_khz^2) + ...
                       (A2 * f2 * (f_ref_khz^2)) / (f2^2 + f_ref_khz^2) + ...
                       A3 * (f_ref_khz^2);

    % 3. Simulated Turbidity Scattering Penalty
    % Rayleigh/Mie scattering scales with turbidity and frequency squared
    turb_norm = max(0.0, min(1.0, turb / 100.0));
    alpha_turb_db_km = 35.0 * turb_norm * ((f_ref_khz / 300.0)^2);

    total_alpha_db_km = alpha_chem_db_km + alpha_turb_db_km;

    % 4. Normalized Quality Component Penalties [0, 1]
    % Penalty 1: Turbidity particulate scattering (primary driver)
    p_turb = turb_norm;

    % Penalty 2: Acoustic attenuation (normalized against 150 dB/km threshold)
    p_attn = max(0.0, min(1.0, total_alpha_db_km / 160.0));

    % Penalty 3: Ambient acoustic noise (normalized between 40 dB calm and 80 dB severe)
    p_noise = max(0.0, min(1.0, (noise_db - 40.0) / 40.0));

    % 5. Deterministic, Explainable Channel Quality Score Q in [0.0, 1.0]
    % Weights: 50% Turbidity / Scattering, 25% Attenuation, 25% Ambient Noise
    w_turb = 0.50;
    w_attn = 0.25;
    w_noise = 0.25;
    total_penalty = w_turb * p_turb + w_attn * p_attn + w_noise * p_noise;

    Q = max(0.0, min(1.0, 1.0 - total_penalty));

    % 6. Compile simulation channel metadata
    channel_info = struct();
    channel_info.sound_speed_m_s = c;
    channel_info.chem_absorption_db_km = alpha_chem_db_km;
    channel_info.turb_scattering_db_km = alpha_turb_db_km;
    channel_info.total_attenuation_db_km = total_alpha_db_km;
    channel_info.turbidity_penalty = p_turb;
    channel_info.attenuation_penalty = p_attn;
    channel_info.noise_penalty = p_noise;
    channel_info.total_penalty = total_penalty;
    channel_info.Q = Q;
end
