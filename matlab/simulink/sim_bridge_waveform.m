% ==============================================================================
% SIH Problem 26058: AUV Sonar Transmitter Digital Twin
%
% File: sim_bridge_waveform.m
% Description: Simulink bridge function for Continuous LFM Chirp Synthesizer.
% Directly references profile definitions and generates phase-continuous chirp.
% ==============================================================================

function [x_ideal, inst_freq_khz, window_envelope] = sim_bridge_waveform(prof_id, amp, t_sec)
    p_id = double(prof_id(1));
    a_val = double(amp(1));
    t_val = double(t_sec(1));

    Tp = 0.002;
    if t_val < 0.0 || t_val > Tp
        x_ideal = 0.0;
        inst_freq_khz = 0.0;
        window_envelope = 0.0;
        return;
    end

    % Canonical profiles: 1: 100-220 kHz, 2: 200-400 kHz, 3: 350-500 kHz
    f0 = 200.0e3;
    f1 = 400.0e3;
    if p_id == 1
        f0 = 100.0e3;
        f1 = 220.0e3;
    elseif p_id == 3
        f0 = 350.0e3;
        f1 = 500.0e3;
    end

    k = (f1 - f0) / Tp;
    phi = 2.0 * pi * (f0 * t_val + 0.5 * k * (t_val ^ 2));
    carrier = cos(phi);
    w = 0.5 * (1.0 - cos(2.0 * pi * t_val / Tp));

    x_ideal = a_val * carrier * w;
    inst_freq_khz = (f0 + k * t_val) / 1000.0;
    window_envelope = a_val * w;
end
