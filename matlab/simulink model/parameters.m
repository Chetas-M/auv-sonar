%% SIH 26058
% Adaptive Software-Defined Sonar Transmitter
% Main Project Parameters

clear;
clc;

%% =========================================================
% 1. SIMULATION / SAMPLING
% =========================================================

Fs = 2e6;              % Sampling frequency = 2 MHz
Ts = 1/Fs;             % Sampling period

SimTime = 0.1;         % Total simulation time = 100 ms


%% =========================================================
% 2. SONAR FREQUENCY
% =========================================================

Fmin = 100e3;          % Minimum sonar frequency = 100 kHz
Fmax = 500e3;          % Maximum sonar frequency = 500 kHz

Fc = 300e3;            % Centre frequency = 300 kHz
BW = 200e3;            % Bandwidth = 200 kHz

Fstart = 200e3;        % LFM start frequency
Fstop  = 400e3;        % LFM stop frequency


%% =========================================================
% 3. PULSE / TIMING
% =========================================================

Tp = 2e-3;             % Pulse duration = 2 ms
PRI = 20e-3;           % Pulse repetition interval = 20 ms

PRF = 1/PRI;           % Pulse repetition frequency
DutyCycle = Tp/PRI;    % Duty cycle


%% =========================================================
% 4. WAVEFORM TYPE
% =========================================================

waveformType = 3;

% 1 = LFM Chirp
% 2 = Geometric Sweep
% 3 = Phase-Coded Pulse


%% =========================================================
% 5. WINDOWING
% =========================================================

windowType = 2;

% 1 = Hamming
% 2 = Hann
% 3 = Blackman


%% =========================================================
% 6. LFM PARAMETERS
% =========================================================

LFM_fstart = 200e3;    % Start frequency
LFM_fstop  = 400e3;    % Stop frequency
LFM_T = 2e-3;          % Chirp duration


%% =========================================================
% 7. GEOMETRIC SWEEP
% =========================================================

Geo_fstart = 100e3;
Geo_fstop  = 500e3;
Geo_T = 2e-3;


%% =========================================================
% 8. PHASE-CODE PARAMETERS
% =========================================================

phaseCode = [1 1 -1 1 -1 -1 1];

chipDuration = 100e-6;


%% =========================================================
% 9. AMPLITUDE
% =========================================================

A = 1;                 % Normalized amplitude

Amin = 0.1;
Amax = 1.0;


%% =========================================================
% 10. DAC
% =========================================================

DAC_bits = 16;

DAC_levels = 2^DAC_bits;

DAC_Vref = 3.3;        % Simulation reference voltage


%% =========================================================
% 11. UNDERWATER ENVIRONMENT
% =========================================================

depth = 50;            % Depth in metres

temperature = 20;      % Water temperature in °C

salinity = 35;         % Salinity in PSU

turbidity = 100;       % Turbidity simulation input


%% =========================================================
% 12. NOISE
% =========================================================

noiseLevel = -20;      % Simulation noise parameter


%% =========================================================
% 13. UNDERWATER CHANNEL
% =========================================================

range = 5;            % Target range in metres

soundSpeed = 1500;     % Approximate sound speed in water (m/s)

channelGain = 1;

multipath = true;

numPaths = 3;


%% =========================================================
% 14. ADAPTIVE LIMITS
% =========================================================

Fc_min = 100e3;
Fc_max = 500e3;

BW_min = 50e3;
BW_max = 200e3;

Tp_min = 0.5e-3;
Tp_max = 5e-3;

A_min = 0.1;
A_max = 1.0;


%% =========================================================
% 15. ADAPTIVE THRESHOLDS
% =========================================================

depth_threshold = 100;

turbidity_threshold = 500;

noise_threshold = -10;


%% =========================================================
% 16. PERFORMANCE VARIABLES
% =========================================================

SNR = 0;

rangeResolution = 0;

pulseEnergy = 0;

peakPower = 0;

averagePower = 0;


%% =========================================================
% DISPLAY PARAMETERS
% =========================================================

fprintf('\n');
fprintf('============================================\n');
fprintf('       SIH 26058 SONAR PARAMETERS\n');
fprintf('============================================\n');

fprintf('Sampling Frequency : %.2f MHz\n', Fs/1e6);

fprintf('Frequency Range    : %.0f - %.0f kHz\n', ...
    Fmin/1e3, Fmax/1e3);

fprintf('Centre Frequency   : %.2f kHz\n', Fc/1e3);

fprintf('Bandwidth          : %.2f kHz\n', BW/1e3);

fprintf('Pulse Duration     : %.2f ms\n', Tp*1e3);

fprintf('PRI                : %.2f ms\n', PRI*1e3);

fprintf('PRF                : %.2f Hz\n', PRF);

fprintf('Duty Cycle         : %.2f %%\n', DutyCycle*100);

fprintf('DAC Resolution     : %d bits\n', DAC_bits);

fprintf('Water Temperature  : %.1f °C\n', temperature);

fprintf('Salinity           : %.1f PSU\n', salinity);

fprintf('Depth              : %.1f m\n', depth);

fprintf('Target Range       : %.1f m\n', range);

fprintf('============================================\n');