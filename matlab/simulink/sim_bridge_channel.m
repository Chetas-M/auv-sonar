% ==============================================================================
% SIH Problem 26058: AUV Sonar Transmitter Digital Twin
%
% File: sim_bridge_channel.m
% Description: Simulink bridge function for Channel & Propagation Evaluation.
% Directly references and invokes channel_model.m and evaluate_profile_performance.m.
% ==============================================================================

function [Q, cand_id, viability_conf, p1_viable, p2_viable, p3_viable] = ...
    sim_bridge_channel(turb, depth, temp, sal, noise, range, mode)

    % Extract scalar values safely
    turb_val = double(turb(1));
    depth_val = double(depth(1));
    temp_val = double(temp(1));
    sal_val = double(sal(1));
    noise_val = double(noise(1));
    range_val = double(range(1));
    mode_val = double(mode(1));

    % 1. Evaluate Channel Quality Score Q via channel_model.m
    env = struct('depth_m', depth_val, 'temperature_c', temp_val, ...
                 'salinity_psu', sal_val, 'turbidity', turb_val, ...
                 'ambient_noise_db', noise_val);
    Q = double(channel_model(env));

    % 2. Map mission mode numeric code to objective string
    % 1: SURVEY (Default), 2: DIRECTIVITY, 3: PENETRATION
    mode_str = 'SURVEY';
    if mode_val == 2
        mode_str = 'DIRECTIVITY';
    elseif mode_val == 3
        mode_str = 'PENETRATION';
    end

    % 3. Evaluate Profile Performance via evaluate_profile_performance.m
    [~, dec] = evaluate_profile_performance(range_val, env, mode_str);

    cand_id = double(dec.candidate_profile_id);
    viability_conf = double(dec.viability_confidence);
    p1_viable = double(dec.all_viable(1));
    p2_viable = double(dec.all_viable(2));
    p3_viable = double(dec.all_viable(3));
end
