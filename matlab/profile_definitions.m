% ==============================================================================
% File: profile_definitions.m
% Description: Defines the 3 locked transmission profiles for SIH Problem 26058.
% Profiles are strictly named LOW_FREQUENCY, BALANCED, and HIGH_FREQUENCY.
% ==============================================================================

function profiles = profile_definitions()
    % Profile 1: LOW_FREQUENCY / DEGRADED CHANNEL
    p1 = struct();
    p1.id = 1;
    p1.name = 'LOW_FREQUENCY';
    p1.full_name = 'Profile 1: Low Frequency / Degraded Channel';
    p1.f_start_hz = 100.0e3;        % 100 kHz
    p1.f_end_hz = 220.0e3;          % 220 kHz
    p1.f_center_hz = 160.0e3;       % 160 kHz
    p1.bandwidth_hz = 120.0e3;      % 120 kHz
    p1.duration_s = 0.002;          % 2.0 ms
    p1.lut_name = 'CHIRP_LOW_FREQUENCY_LUT';
    p1.header_file = 'chirp_low_frequency.h';
    p1.purpose = 'Lower-frequency profile designed for degraded or particulate-scattering channel scenarios.';

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
    p2.purpose = 'Default operating profile. Features largest bandwidth (200 kHz) and therefore best idealized bandwidth-based range resolution (3.75 mm).';

    % Profile 3: HIGH_FREQUENCY / HIGH-BAND CHANNEL
    p3 = struct();
    p3.id = 3;
    p3.name = 'HIGH_FREQUENCY';
    p3.full_name = 'Profile 3: High Frequency Channel';
    p3.f_start_hz = 350.0e3;        % 350 kHz
    p3.f_end_hz = 500.0e3;          % 500 kHz
    p3.f_center_hz = 425.0e3;       % 425 kHz
    p3.bandwidth_hz = 150.0e3;      % 150 kHz
    p3.duration_s = 0.002;          % 2.0 ms
    p3.lut_name = 'CHIRP_HIGH_FREQUENCY_LUT';
    p3.header_file = 'chirp_high_frequency.h';
    p3.purpose = 'Higher-frequency operating-band simulation profile providing narrow acoustic beam directivity for a given physical transducer aperture.';

    profiles = [p1, p2, p3];
end
