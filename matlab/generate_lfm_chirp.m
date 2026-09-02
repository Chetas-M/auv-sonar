% ==============================================================================
% File: generate_lfm_chirp.m
% Description: Synthesizes continuous-phase LFM chirp with Hann windowing.
% Validates that sample count, endpoints, and values contain no NaN or Inf.
% ==============================================================================

function [wf, diagnostics] = generate_lfm_chirp(f_start_hz, f_end_hz, duration_s, Fs, amplitude)
    if nargin < 5
        amplitude = 1.0;
    end
    if nargin < 4
        Fs = 4.0e6;
    end

    % 1. Sample count & discrete time vector
    Np = round(duration_s * Fs);
    n = (0:(Np - 1))';          % Column vector of discrete indices n = 0, ..., N-1
    t = n / Fs;                 % Time in seconds [0, Tp - Ts]

    % 2. LFM chirp parameters
    k = (f_end_hz - f_start_hz) / duration_s; % Chirp rate (Hz/s)

    % 3. Analytical phase integration
    % phi(t) = 2*pi * integral_0^t (f_0 + k*tau) dtau = 2*pi * (f_0*t + 0.5*k*t^2)
    phi = 2.0 * pi * (f_start_hz .* t + 0.5 * k .* (t .^ 2));

    % Raw continuous-phase carrier sinusoid
    raw_carrier = cos(phi);

    % 4. Hann window implementation (standard definition)
    % w[n] = 0.5 * (1 - cos(2*pi*n / (N - 1)))
    w = 0.5 * (1.0 - cos(2.0 * pi * n / (Np - 1)));

    % 5. Windowed and amplitude-scaled ideal signal
    x_windowed = amplitude * raw_carrier .* w;

    % Validation checks
    assert(~any(isnan(x_windowed)), 'Generated waveform contains NaN values');
    assert(~any(isinf(x_windowed)), 'Generated waveform contains Inf values');
    assert(length(x_windowed) == Np, 'Generated waveform length mismatch');

    % 6. Diagnostics & Verification metrics
    diagnostics = struct();
    diagnostics.Np = Np;
    diagnostics.duration_s = duration_s;
    diagnostics.k_hz_s = k;
    diagnostics.window_endpoint_start = w(1);
    diagnostics.window_endpoint_end = w(end);
    diagnostics.peak_amplitude = max(abs(x_windowed));
    diagnostics.has_nan = any(isnan(x_windowed));
    diagnostics.has_inf = any(isinf(x_windowed));

    % Estimate numerical instantaneous frequency via phase diff
    dphi = diff(phi);
    inst_freq_hz = dphi / (2.0 * pi * (1.0 / Fs));
    diagnostics.inst_freq_start = inst_freq_hz(1);
    diagnostics.inst_freq_end = inst_freq_hz(end);

    % Store in output structure
    wf = struct();
    wf.t = t;
    wf.raw_carrier = raw_carrier;
    wf.window = w;
    wf.signal = x_windowed;
    wf.f_start_hz = f_start_hz;
    wf.f_end_hz = f_end_hz;
    wf.duration_s = duration_s;
    wf.Fs = Fs;
    wf.amplitude = amplitude;
    wf.Np = Np;
    wf.phi = phi;
    wf.chirp_slope_hz_s = k;
    wf.inst_freq_hz = [inst_freq_hz; inst_freq_hz(end)]; % Pad last sample to match length
end
