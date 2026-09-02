% ==============================================================================
% SIH Problem 26058: Low-Power, Real-Time Adaptive Software-Defined Sonar
% Transmitter Payload for Autonomous Underwater Vehicles (AUVs)
%
% File: config_sonar.m
% Description: Master configuration defining Single Source of Truth parameters.
% Every parameter is explicitly classified by engineering category:
%   - [FIXED]         Fixed Implementation Parameter (locked hardware specs)
%   - [ADAPTIVE]      Adaptive Runtime Parameter (dynamically selected by controller)
%   - [ENVIRONMENT]   Environmental Input (simulation scenario variables)
%   - [ASSUMPTION]    Simulation Assumption (unmeasured model parameters)
%   - [DERIVED]       Derived Value (analytically computed from other parameters)
% ==============================================================================

function cfg = config_sonar()
    cfg = struct();

    % --------------------------------------------------------------------------
    % [FIXED] Single Source of Truth: Locked Implementation Parameters (v1)
    % --------------------------------------------------------------------------
    cfg.Fs = 4.0e6;                 % [FIXED] DAC sampling frequency: 4.0 MHz
    cfg.Ts = 1.0 / cfg.Fs;          % [FIXED] Sampling period: 250 ns
    cfg.DAC_bits = 12;              % [FIXED] DAC resolution: 12-bit unsigned
    cfg.DAC_min_code = 0;           % [FIXED] Minimum integer DAC code
    cfg.DAC_max_code = 4095;        % [FIXED] Maximum integer DAC code (2^12 - 1)
    cfg.DAC_midscale = 2048;        % [FIXED] Midscale code (1.65V bias for AC-coupled TX)
    cfg.DAC_vref = 3.3;             % [FIXED] STM32 analog reference rail (Volts)
    cfg.target_mcu = 'STM32G474';   % [FIXED] Target MCU: 170MHz Cortex-M4F
    cfg.mcu_sram_bytes = 128 * 1024;% [FIXED] Total SRAM on STM32G474 (128 KB)
    cfg.mcu_flash_bytes = 512 * 1024;% [FIXED] Total Flash on STM32G474 (512 KB)
    cfg.bytes_per_sample = 2;       % [FIXED] uint16_t storage: 2 bytes per sample

    cfg.waveform_type = 'LFM_CHIRP';% [FIXED] Waveform family locked to LFM chirp
    cfg.window_type = 'HANN';       % [FIXED] Spectral window locked to Hann
    cfg.PRI_s = 0.020;              % [FIXED] Pulse Repetition Interval: 20.0 ms (50 Hz)
    cfg.Tp_s = 0.002;               % [FIXED] Nominal pulse duration: 2.0 ms
    cfg.num_profiles = 3;           % [FIXED] Exactly 3 discrete transmission profiles

    % --------------------------------------------------------------------------
    % [DERIVED] Basic Timing & Sample Counts
    % --------------------------------------------------------------------------
    cfg.Np = round(cfg.Fs * cfg.Tp_s); % [DERIVED] Sample count: 4e6 * 0.002 = 8000 samples
    cfg.duty_cycle = cfg.Tp_s / cfg.PRI_s; % [DERIVED] Default duty cycle: 10.0%
    cfg.nyquist_hz = cfg.Fs / 2.0;  % [DERIVED] Nyquist frequency: 2.0 MHz
    cfg.lut_bytes_per_profile = cfg.Np * cfg.bytes_per_sample; % [DERIVED] 16,000 bytes

    % --------------------------------------------------------------------------
    % [ADAPTIVE] Runtime Controller Parameters (Adaptive Decisions)
    % --------------------------------------------------------------------------
    cfg.hysteresis_band = 0.10;     % [ADAPTIVE] 10% deadband around decision thresholds
    cfg.debounce_count = 2;         % [ADAPTIVE] N = 2 consecutive cycles required to commit
    cfg.amp_poor = 1.00;            % [ADAPTIVE] Amplitude factor for poor channel (0 dB)
    cfg.amp_moderate = 0.70;        % [ADAPTIVE] Amplitude factor for moderate channel (-3.1 dB)
    cfg.amp_good = 0.40;            % [ADAPTIVE] Amplitude factor for good channel (-7.96 dB)

    % Channel Quality Score (Q) Thresholds:
    %   Poor channel     (Q < 0.35):               Profile 1 (MUDDY)
    %   Moderate channel (0.35 <= Q < 0.70):       Profile 2 (BALANCED)
    %   Good channel     (Q >= 0.70):              Profile 3 (CLEAR)
    cfg.thresh_poor_to_mod = 0.35;
    cfg.thresh_mod_to_good = 0.70;

    % --------------------------------------------------------------------------
    % [ENVIRONMENT] Simulation Scenario Inputs (Default Baseline)
    % --------------------------------------------------------------------------
    cfg.env_depth_m = 50.0;         % [ENVIRONMENT] Operating depth in meters
    cfg.env_temperature_c = 20.0;   % [ENVIRONMENT] Water temperature in Celsius
    cfg.env_salinity_psu = 35.0;    % [ENVIRONMENT] Salinity in Practical Salinity Units
    cfg.env_turbidity_ntu = 100.0;  % [ENVIRONMENT] Turbidity scale (0: clear, 100: high sediment)
    cfg.env_ambient_noise_db = 55.0;% [ENVIRONMENT] Ambient acoustic noise (dB re 1 uPa / sqrt(Hz))

    % --------------------------------------------------------------------------
    % [ASSUMPTION] Simplified Transmitter Payload Power Model Assumptions
    % NOTE: Unmeasured simulation estimates for transmitter payload load alone.
    % --------------------------------------------------------------------------
    cfg.P_active_w = 5.0;           % [ASSUMPTION] Active transmit power (PA + DAC + MCU active)
    cfg.P_idle_w = 0.045;           % [ASSUMPTION] Idle power between pings (PA shut down, MCU sleep)
    cfg.V_battery_v = 12.0;         % [ASSUMPTION] Primary subsea battery rail (12.0 V)
    cfg.battery_capacity_wh = 99.0; % [ASSUMPTION] Hypothetical 99 Wh pack (payload load alone)

    % --------------------------------------------------------------------------
    % Standard Engineering Scope Disclaimer
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
