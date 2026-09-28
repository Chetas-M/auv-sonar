%% =========================================================
% SIH 26058
% SNR-AWARE ADAPTIVE CONTROLLER
%
% Inputs:
%   Depth
%   Turbidity
%   Noise Level
%   Estimated SNR
%
% Outputs:
%   Waveform
%   Centre Frequency
%   Bandwidth
%   Pulse Duration
%   Amplitude
% =========================================================

clear;
clc;
close all;

%% =========================================================
% 1. LOAD PROJECT PARAMETERS
% =========================================================

parameters;

%% =========================================================
% 2. ENVIRONMENT INPUTS
% =========================================================

currentDepth = depth;
currentTurbidity = turbidity;
currentNoise = noiseLevel;

% SNR input obtained from simulation/receiver
estimatedSNR = -22;

%% =========================================================
% 3. INITIAL PARAMETERS
% =========================================================

adaptiveFc = Fc;
adaptiveBW = BW;
adaptiveTp = Tp;
adaptiveAmplitude = A;
adaptiveWaveform = 1;

adaptationReason = 'Normal operating condition';

%% =========================================================
% 4. SNR-AWARE ADAPTATION
% =========================================================

if estimatedSNR < -25

    % ------------------------------------------------------
    % VERY LOW SNR
    % ------------------------------------------------------

    adaptiveFc = 300e3;
    adaptiveBW = 200e3;
    adaptiveTp = 4e-3;
    adaptiveAmplitude = 1.0;
    adaptiveWaveform = 3;

    adaptationReason = ...
        'Very low SNR - robust phase-coded waveform';

elseif estimatedSNR < -20

    % ------------------------------------------------------
    % LOW SNR
    % ------------------------------------------------------

    adaptiveFc = 300e3;
    adaptiveBW = 200e3;
    adaptiveTp = 3e-3;
    adaptiveAmplitude = 1.0;
    adaptiveWaveform = 1;

    adaptationReason = ...
        'Low SNR - increased pulse duration';

elseif currentTurbidity > turbidity_threshold

    % ------------------------------------------------------
    % HIGH TURBIDITY
    % ------------------------------------------------------

    adaptiveFc = 200e3;
    adaptiveBW = 100e3;
    adaptiveTp = 3e-3;
    adaptiveAmplitude = 0.8;
    adaptiveWaveform = 1;

    adaptationReason = ...
        'High turbidity';

elseif currentNoise > noise_threshold

    % ------------------------------------------------------
    % HIGH NOISE
    % ------------------------------------------------------

    adaptiveFc = 300e3;
    adaptiveBW = 200e3;
    adaptiveTp = 2e-3;
    adaptiveAmplitude = 1.0;
    adaptiveWaveform = 3;

    adaptationReason = ...
        'High environmental noise';

elseif currentDepth > depth_threshold

    % ------------------------------------------------------
    % DEEP WATER
    % ------------------------------------------------------

    adaptiveFc = 250e3;
    adaptiveBW = 150e3;
    adaptiveTp = 3e-3;
    adaptiveAmplitude = 1.0;
    adaptiveWaveform = 2;

    adaptationReason = ...
        'Deep-water condition';

else

    % ------------------------------------------------------
    % NORMAL
    % ------------------------------------------------------

    adaptiveFc = Fc;
    adaptiveBW = BW;
    adaptiveTp = Tp;
    adaptiveAmplitude = A;
    adaptiveWaveform = 1;

    adaptationReason = ...
        'Normal operating condition';

end

%% =========================================================
% 5. APPLY SAFETY LIMITS
% =========================================================

adaptiveFc = ...
    max(Fc_min,min(Fc_max,adaptiveFc));

adaptiveBW = ...
    max(BW_min,min(BW_max,adaptiveBW));

adaptiveTp = ...
    max(Tp_min,min(Tp_max,adaptiveTp));

adaptiveAmplitude = ...
    max(A_min,min(A_max,adaptiveAmplitude));

%% =========================================================
% 6. WAVEFORM NAME
% =========================================================

switch adaptiveWaveform

    case 1
        waveformName = 'LFM Chirp';

    case 2
        waveformName = 'Geometric Sweep';

    case 3
        waveformName = 'Phase-Coded Pulse';

end

%% =========================================================
% 7. DISPLAY INPUTS
% =========================================================

fprintf('\n');
fprintf('====================================================\n');
fprintf('       SIH 26058 - SNR ADAPTIVE CONTROLLER\n');
fprintf('====================================================\n');

fprintf('\nENVIRONMENT / RECEIVER INPUTS\n');
fprintf('----------------------------------------------------\n');

fprintf('Depth          : %.2f m\n',currentDepth);
fprintf('Turbidity      : %.2f\n',currentTurbidity);
fprintf('Noise Level    : %.2f dB\n',currentNoise);
fprintf('Estimated SNR  : %.2f dB\n',estimatedSNR);

%% =========================================================
% 8. DISPLAY DECISION
% =========================================================

fprintf('\nADAPTIVE DECISION\n');
fprintf('----------------------------------------------------\n');

fprintf('Reason         : %s\n',adaptationReason);

%% =========================================================
% 9. DISPLAY OUTPUTS
% =========================================================

fprintf('\nADAPTIVE TRANSMITTER OUTPUT\n');
fprintf('----------------------------------------------------\n');

fprintf('Waveform         : %s\n',waveformName);
fprintf('Centre Frequency : %.2f kHz\n',adaptiveFc/1e3);
fprintf('Bandwidth        : %.2f kHz\n',adaptiveBW/1e3);
fprintf('Pulse Duration   : %.2f ms\n',adaptiveTp*1e3);
fprintf('Amplitude        : %.2f\n',adaptiveAmplitude);

fprintf('====================================================\n');

%% =========================================================
% 10. BEFORE / AFTER COMPARISON
% =========================================================

figure;

before = [
    Fc/1e3
    BW/1e3
    Tp*1e3
    A
    ];

after = [
    adaptiveFc/1e3
    adaptiveBW/1e3
    adaptiveTp*1e3
    adaptiveAmplitude
    ];

bar([before after]);

set(gca,'XTickLabel',{
    'Centre Frequency'
    'Bandwidth'
    'Pulse Duration'
    'Amplitude'
    });

ylabel('Value');

legend('Before Adaptation','After Adaptation');

title('SIH 26058 - SNR Adaptive Parameter Selection');

grid on;

%% =========================================================
% 11. COMPLETE
% =========================================================

fprintf('\n');
fprintf('SNR ADAPTIVE CONTROLLER TEST COMPLETE\n');
fprintf('====================================================\n');