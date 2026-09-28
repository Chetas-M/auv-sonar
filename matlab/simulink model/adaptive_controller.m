%% =========================================================
% SIH 26058
% ADAPTIVE SOFTWARE-DEFINED SONAR TRANSMITTER
%
% ADAPTIVE CONTROLLER
%
% Inputs:
%   Depth
%   Turbidity
%   Noise
%
% Outputs:
%   Waveform Type
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

%% =========================================================
% 3. INITIAL VALUES
% =========================================================

adaptiveFc = Fc;
adaptiveBW = BW;
adaptiveTp = Tp;
adaptiveAmplitude = A;
adaptiveWaveform = 1;

%% =========================================================
% 4. ADAPTIVE DECISION LOGIC
% =========================================================

% ----------------------------------------------------------
% HIGH TURBIDITY
% ----------------------------------------------------------

if currentTurbidity > turbidity_threshold

    % Use lower frequency to improve robustness
    adaptiveFc = 200e3;

    % Reduce bandwidth
    adaptiveBW = 100e3;

    % Use longer pulse
    adaptiveTp = 3e-3;

    % Reduce transmitted amplitude slightly
    adaptiveAmplitude = 0.8;

    % LFM is preferred
    adaptiveWaveform = 1;

% ----------------------------------------------------------
% HIGH NOISE
% ----------------------------------------------------------

elseif currentNoise > noise_threshold

    % Use wider bandwidth for better processing gain
    adaptiveFc = 300e3;

    adaptiveBW = 200e3;

    adaptiveTp = 2e-3;

    adaptiveAmplitude = 1.0;

    % Phase-coded waveform
    adaptiveWaveform = 3;

% ----------------------------------------------------------
% DEEP WATER
% ----------------------------------------------------------

elseif currentDepth > depth_threshold

    % Lower centre frequency
    adaptiveFc = 250e3;

    adaptiveBW = 150e3;

    adaptiveTp = 3e-3;

    adaptiveAmplitude = 1.0;

    % Geometric sweep
    adaptiveWaveform = 2;

% ----------------------------------------------------------
% NORMAL CONDITIONS
% ----------------------------------------------------------

else

    adaptiveFc = Fc;

    adaptiveBW = BW;

    adaptiveTp = Tp;

    adaptiveAmplitude = A;

    % LFM
    adaptiveWaveform = 1;

end

%% =========================================================
% 5. LIMIT PARAMETERS
% =========================================================

adaptiveFc = max(Fc_min,min(Fc_max,adaptiveFc));

adaptiveBW = max(BW_min,min(BW_max,adaptiveBW));

adaptiveTp = max(Tp_min,min(Tp_max,adaptiveTp));

adaptiveAmplitude = ...
    max(A_min,min(A_max,adaptiveAmplitude));

%% =========================================================
% 6. DISPLAY ENVIRONMENT
% =========================================================

fprintf('\n');
fprintf('====================================================\n');
fprintf('           SIH 26058 - ADAPTIVE CONTROLLER\n');
fprintf('====================================================\n');

fprintf('\nENVIRONMENT INPUTS\n');
fprintf('----------------------------------------------------\n');

fprintf('Depth       : %.2f m\n',currentDepth);
fprintf('Turbidity   : %.2f\n',currentTurbidity);
fprintf('Noise Level : %.2f dB\n',currentNoise);

%% =========================================================
% 7. DISPLAY ADAPTIVE OUTPUT
% =========================================================

fprintf('\nADAPTIVE TRANSMITTER OUTPUT\n');
fprintf('----------------------------------------------------\n');

fprintf('Centre Frequency : %.2f kHz\n', ...
    adaptiveFc/1e3);

fprintf('Bandwidth        : %.2f kHz\n', ...
    adaptiveBW/1e3);

fprintf('Pulse Duration   : %.2f ms\n', ...
    adaptiveTp*1e3);

fprintf('Amplitude        : %.2f\n', ...
    adaptiveAmplitude);

%% =========================================================
% 8. WAVEFORM NAME
% =========================================================

switch adaptiveWaveform

    case 1
        waveformName = 'LFM Chirp';

    case 2
        waveformName = 'Geometric Sweep';

    case 3
        waveformName = 'Phase-Coded Pulse';

end

fprintf('Waveform         : %s\n',waveformName);

fprintf('====================================================\n');

%% =========================================================
% 9. SHOW ADAPTATION
% =========================================================

figure;

parametersBefore = [Fc/1e3, BW/1e3, Tp*1e3, A];

parametersAfter = ...
    [adaptiveFc/1e3, adaptiveBW/1e3, ...
     adaptiveTp*1e3, adaptiveAmplitude];

bar([parametersBefore; parametersAfter].');

set(gca,'XTickLabel', ...
    {'Centre Frequency','Bandwidth', ...
     'Pulse Duration','Amplitude'});

ylabel('Value');

legend('Before Adaptation','After Adaptation');

title('SIH 26058 - Adaptive Transmitter Parameters');

grid on;

%% =========================================================
% 10. END
% =========================================================

fprintf('\n');
fprintf('ADAPTIVE CONTROLLER TEST COMPLETE\n');
fprintf('====================================================\n');