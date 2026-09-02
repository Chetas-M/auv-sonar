% ==============================================================================
% File: profile_definitions.m
% Description: Defines the 3 locked transmission profiles for SIH Problem 26058.
% ==============================================================================

function profiles = profile_definitions()
    % Profile 1: MUDDY / DEGRADED CHANNEL
    p1 = struct();
    p1.id = 1;
    p1.name = 'MUDDY';
    p1.full_name = 'Profile 1: Muddy / Degraded Channel';
    p1.f_start_hz = 100.0e3;        % 100 kHz
    p1.f_end_hz = 220.0e3;          % 220 kHz
    p1.f_center_hz = 160.0e3;       % 160 kHz
    p1.bandwidth_hz = 120.0e3;      % 120 kHz
    p1.duration_s = 0.002;          % 2.0 ms
    p1.lut_name = 'CHIRP_MUDDY_LUT';
    p1.header_file = 'chirp_muddy.h';
    p1.purpose = 'Lower-frequency profile to mitigate particulate acoustic scattering in turbid water.';

    % Profile 2: BALANCED / DEFAULT CHANNEL
    p2 = struct();
    p2.id = 2;
    p2.name = 'BALANCED';
    p2.full_name = 'Profile 2: Balanced / Default Channel';
    p2.f_start_hz = 200.0e3;        % 200 kHz
    p2.f_end_hz = 400.0e3;          % 400 kHz
    p2.f_center_hz = 300.0e3;       % 300 kHz
    p2.bandwidth_hz = 200.0e3;      % 200 kHz
    p2.duration_s = 0.002;          % 2.0 ms
    p2.lut_name = 'CHIRP_BALANCED_LUT';
    p2.header_file = 'chirp_balanced.h';
    p2.purpose = 'Default nominal operating profile balancing penetration range and spatial resolution.';

    % Profile 3: CLEAR / HIGH-RESOLUTION CHANNEL
    p3 = struct();
    p3.id = 3;
    p3.name = 'CLEAR';
    p3.full_name = 'Profile 3: Clear / High-Resolution Channel';
    p3.f_start_hz = 350.0e3;        % 350 kHz
    p3.f_end_hz = 500.0e3;          % 500 kHz
    p3.f_center_hz = 425.0e3;       % 425 kHz
    p3.bandwidth_hz = 150.0e3;      % 150 kHz
    p3.duration_s = 0.002;          % 2.0 ms
    p3.lut_name = 'CHIRP_CLEAR_LUT';
    p3.header_file = 'chirp_clear.h';
    p3.purpose = 'High-frequency profile delivering fine spatial range resolution in clear, low-attenuation water.';

    profiles = [p1, p2, p3];
end
