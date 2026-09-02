% ==============================================================================
% SIH Problem 26058: Low-Power, Real-Time Adaptive Software-Defined Sonar
% Transmitter Payload for Autonomous Underwater Vehicles (AUVs)
%
% File: config_sonar.m
% Description: Single Source of Truth Master Configuration Module.
% Every parameter is strictly classified into one of five categories:
%   - [FIXED]         Fixed Implementation Parameter (locked hardware specs)
%   - [ADAPTIVE]      Adaptive Runtime Parameter (dynamically selected by controller)
%   - [ENVIRONMENT]   Environmental Scenario Input (simulation scenario variables)
%   - [ASSUMPTION]    Simulation Assumption (unmeasured model parameters)
%   - [DERIVED]       Derived Value (analytically computed from other parameters)
% ==============================================================================

function cfg = config_sonar()
    cfg = struct();

    % --------------------------------------------------------------------------
    % 1. [FIXED] SYSTEM PARAMETERS (Locked Implementation Constraints for v1)
    % --------------------------------------------------------------------------
    cfg.Fs = 4.0e6;                 % [FIXED] DAC sampling frequency: 4.0 MHz (4.0 MSPS)
    cfg.Ts = 1.0 / cfg.Fs;          % [FIXED] Sampling period: 250 ns
    cfg.DAC_bits = 12;              % [FIXED] DAC resolution: 12-bit unsigned
    cfg.DAC_min_code = 0;           % [FIXED] Minimum integer DAC code
    cfg.DAC_max_code = 4095;        % [FIXED] Maximum integer DAC code (2^12 - 1)
    cfg.DAC_midscale = 2048;        % [FIXED] Nominal midpoint code (1.65V bias for AC output)
    cfg.DAC_vref = 3.3;             % [FIXED] STM32 analog reference rail (Volts)
    cfg.target_mcu = 'STM32G474';   % [FIXED] Target MCU: 170MHz ARM Cortex-M4F
    cfg.mcu_sram_bytes = 128 * 1024;% [FIXED] Total SRAM on STM32G474 (128 KB)
    cfg.mcu_flash_bytes = 512 * 1024;% [FIXED] Total Flash on STM32G474 (512 KB)
    cfg.bytes_per_sample = 2;       % [FIXED] uint16_t storage: 2 bytes per sample

    cfg.waveform_type = 'LFM_CHIRP';% [FIXED] Waveform family: LFM chirp only
    cfg.window_type = 'HANN';       % [FIXED] Spectral window: Hann window only
    cfg.PRI_s = 0.020;              % [FIXED] Pulse Repetition Interval: 20.0 ms (50 Hz ping rate)
    cfg.Tp_s = 0.002;               % [FIXED] Nominal pulse duration: 2.0 ms (fixed for v1)
    cfg.num_profiles = 3;           % [FIXED] Exactly 3 predefined transmission profiles

    % --------------------------------------------------------------------------
    % 2. [DERIVED] TIMING & MEMORY METRICS
    % --------------------------------------------------------------------------
    cfg.Np = round(cfg.Fs * cfg.Tp_s); % [DERIVED] Sample count: 4e6 * 0.002 = 8000 samples
    cfg.duty_cycle = cfg.Tp_s / cfg.PRI_s; % [DERIVED] Nominal duty cycle: 10.0%
    cfg.nyquist_hz = cfg.Fs / 2.0;  % [DERIVED] Nyquist frequency: 2.0 MHz
    cfg.lut_bytes_per_profile = cfg.Np * cfg.bytes_per_sample; % [DERIVED] 16,000 bytes (15.625 KB)
    cfg.total_lut_flash_bytes = cfg.lut_bytes_per_profile * cfg.num_profiles; % [DERIVED] 48,000 bytes

    % --------------------------------------------------------------------------
    % 3. [ADAPTIVE] CONTROLLER & HYSTERESIS PARAMETERS
    % --------------------------------------------------------------------------
    % Channel Quality Score (Q) Weights:
    % Q = w_env * Q_env + w_attn * Q_attn + w_noise * Q_noise
    cfg.w_environment = 0.50;       % [ADAPTIVE] Weight for particulate/scattering penalty (50%)
    cfg.w_attenuation = 0.25;       % [ADAPTIVE] Weight for seawater absorption penalty (25%)
    cfg.w_noise = 0.25;             % [ADAPTIVE] Weight for ambient acoustic noise penalty (25%)

    % Directional Hysteresis Thresholds:
    % Prevents chattering/oscillation at state boundaries.
    cfg.thresh_low_to_bal = 0.40;   % [ADAPTIVE] To rise from LOW_FREQUENCY to BALANCED: Q > 0.40
    cfg.thresh_bal_to_low = 0.30;   % [ADAPTIVE] To drop from BALANCED to LOW_FREQUENCY: Q <= 0.30
    cfg.thresh_bal_to_high = 0.75;  % [ADAPTIVE] To rise from BALANCED to HIGH_FREQUENCY: Q >= 0.75
    cfg.thresh_high_to_bal = 0.65;  % [ADAPTIVE] To drop from HIGH_FREQUENCY to BALANCED: Q < 0.65

    cfg.debounce_count = 2;         % [ADAPTIVE] N = 2 consecutive cycles required to commit candidate

    % Normalized Digital Amplitude Scaling (0 < A <= 1):
    cfg.amp_low = 1.00;             % [ADAPTIVE] LOW_FREQUENCY: maximum acoustic energy (0 dB)
    cfg.amp_balanced = 0.70;        % [ADAPTIVE] BALANCED: default moderate power (-3.1 dB)
    cfg.amp_high = 0.40;            % [ADAPTIVE] HIGH_FREQUENCY: power conservation / clipping limit (-7.96 dB)

    % --------------------------------------------------------------------------
    % 4. [ENVIRONMENT] ENVIRONMENTAL SCENARIO INPUTS (Simulation Variables)
    % --------------------------------------------------------------------------
    cfg.env_depth_m = 50.0;         % [ENVIRONMENT] Operating depth in meters
    cfg.env_temperature_c = 20.0;   % [ENVIRONMENT] Water temperature in Celsius
    cfg.env_salinity_psu = 35.0;    % [ENVIRONMENT] Practical salinity in PSU
    cfg.env_turbidity_ntu = 100.0;  % [ENVIRONMENT] Turbidity scale (0: clear, 100: severe sediment)
    cfg.env_ambient_noise_db = 55.0;% [ENVIRONMENT] Ambient acoustic noise (dB re 1 uPa / sqrt(Hz))

    % --------------------------------------------------------------------------
    % 5. [ASSUMPTION] TRANSMITTER PAYLOAD POWER MODEL ASSUMPTIONS
    % NOTE: Modeled simulation estimates for transmitter payload alone against 99 Wh pack.
    % --------------------------------------------------------------------------
    cfg.P_active_w = 5.0;           % [ASSUMPTION] Active transmit power (PA + DAC + MCU active)
    cfg.P_idle_w = 0.045;           % [ASSUMPTION] Idle power between pings (PA shut down, MCU sleep)
    cfg.P_elec_overhead_w = 0.30;   % [ASSUMPTION] Constant digital/analog electronic overhead
    cfg.V_battery_v = 12.0;         % [ASSUMPTION] Primary subsea battery rail (12.0 V)
    cfg.battery_capacity_wh = 99.0; % [ASSUMPTION] Hypothetical 99 Wh pack (transmitter payload load)
    cfg.viability_threshold_db = -65.0; % [ASSUMPTION] Relative propagation viability threshold (policy parameter, not physical detection limit)

    % --------------------------------------------------------------------------
    % Honest Engineering Scope Disclaimer
    % --------------------------------------------------------------------------
    cfg.disclaimer = [ ...
        '================================================================================\n' ...
        'SIMULATION STATUS: algorithmically credible, physically unverified.\n' ...
        'This simulation validates waveform generation, adaptation logic, quantization,\n' ...
        'DMA buffer sizing, and estimated duty-cycle power. It does NOT validate transducer\n' ...
        'impedance, acoustic propagation, real environmental sensing, analog settling,\n' ...
        'amplifier stability, or actual current draw.\n' ...
        '================================================================================\n'];
end
