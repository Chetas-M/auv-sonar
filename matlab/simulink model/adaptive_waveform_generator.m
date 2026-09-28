%% =========================================================
% SIH 26058
% ADAPTIVE SOFTWARE-DEFINED SONAR TRANSMITTER
%
% ADAPTIVE WAVEFORM GENERATOR
%
% This script uses the outputs of adaptive_controller.m
% to generate the ACTUAL adaptive sonar waveform.
% =========================================================

clearvars -except ...
    Fs Fc BW Tp A ...
    adaptiveFc adaptiveBW adaptiveTp ...
    adaptiveAmplitude adaptiveWaveform ...
    windowType phaseCode ...
    range soundSpeed channelGain noiseLevel

clc;
close all;

%% =========================================================
% 1. CHECK CONTROLLER OUTPUT
% =========================================================

if ~exist('adaptiveFc','var') || ...
   ~exist('adaptiveBW','var') || ...
   ~exist('adaptiveTp','var') || ...
   ~exist('adaptiveAmplitude','var') || ...
   ~exist('adaptiveWaveform','var')

    error(['Run adaptive_controller first. ' ...
           'The adaptive transmitter parameters are not available.']);
end

%% =========================================================
% 2. SAMPLING
% =========================================================

Ts = 1/Fs;

% Number of samples for adaptive pulse
N = round(adaptiveTp * Fs);

t = (0:N-1) * Ts;

%% =========================================================
% 3. FREQUENCY LIMITS
% =========================================================

adaptiveFstart = adaptiveFc - adaptiveBW/2;
adaptiveFstop  = adaptiveFc + adaptiveBW/2;

%% =========================================================
% 4. GENERATE SELECTED WAVEFORM
% =========================================================

switch adaptiveWaveform

    %% -----------------------------------------------------
    % LFM CHIRP
    % -----------------------------------------------------

    case 1

        k = (adaptiveFstop - adaptiveFstart) ...
            / adaptiveTp;

        phase = 2*pi * ...
            (adaptiveFstart*t + 0.5*k*t.^2);

        txSignal = adaptiveAmplitude * cos(phase);

        waveformName = 'LFM Chirp';

        % Instantaneous frequency
        instFreq = adaptiveFstart + k*t;


    %% -----------------------------------------------------
    % GEOMETRIC SWEEP
    % -----------------------------------------------------

    case 2

        % Exponential/geometric frequency sweep

        ratio = adaptiveFstop / adaptiveFstart;

        instFreq = adaptiveFstart * ...
            ratio.^(t/adaptiveTp);

        % Integrate frequency to obtain phase
        phase = 2*pi * cumtrapz(t,instFreq);

        txSignal = adaptiveAmplitude * cos(phase);

        waveformName = 'Geometric Sweep';


    %% -----------------------------------------------------
    % PHASE-CODED PULSE
    % -----------------------------------------------------

    case 3

        codeLength = length(phaseCode);

        chipDurationAdaptive = adaptiveTp / codeLength;

        txSignal = zeros(size(t));

        for n = 1:codeLength

            startIndex = floor((n-1)*N/codeLength) + 1;

            if n == codeLength
                endIndex = N;
            else
                endIndex = floor(n*N/codeLength);
            end

            chipTime = t(startIndex:endIndex);

            txSignal(startIndex:endIndex) = ...
                adaptiveAmplitude * ...
                phaseCode(n) .* ...
                cos(2*pi*adaptiveFc*chipTime);

        end

        waveformName = 'Phase-Coded Pulse';

        instFreq = adaptiveFc * ones(size(t));

end

%% =========================================================
% 5. APPLY WINDOW
% =========================================================

switch windowType

    case 1
        win = hamming(N).';

    case 2
        win = hann(N).';

    case 3
        win = blackman(N).';

    otherwise
        win = ones(1,N);

end

windowedSignal = txSignal .* win;

%% =========================================================
% 6. FFT
% =========================================================

NFFT = 2^nextpow2(N);

Y = fft(windowedSignal,NFFT);

f = (0:NFFT/2-1) * Fs/NFFT;

magnitude = abs(Y(1:NFFT/2));

magnitude = magnitude / max(magnitude);

magnitude_dB = 20*log10(magnitude + eps);

%% =========================================================
% 7. DISPLAY ADAPTIVE SETTINGS
% =========================================================

fprintf('\n');
fprintf('====================================================\n');
fprintf('       SIH 26058 - ADAPTIVE WAVEFORM GENERATOR\n');
fprintf('====================================================\n');

fprintf('\nADAPTIVE TRANSMITTER SETTINGS\n');
fprintf('----------------------------------------------------\n');

fprintf('Waveform         : %s\n',waveformName);
fprintf('Centre Frequency : %.2f kHz\n',adaptiveFc/1e3);
fprintf('Bandwidth        : %.2f kHz\n',adaptiveBW/1e3);
fprintf('Start Frequency  : %.2f kHz\n',adaptiveFstart/1e3);
fprintf('Stop Frequency   : %.2f kHz\n',adaptiveFstop/1e3);
fprintf('Pulse Duration   : %.2f ms\n',adaptiveTp*1e3);
fprintf('Amplitude        : %.2f\n',adaptiveAmplitude);

fprintf('Samples          : %d\n',N);
fprintf('Sampling Rate    : %.2f MHz\n',Fs/1e6);

fprintf('====================================================\n');

%% =========================================================
% 8. TIME DOMAIN WAVEFORM
% =========================================================

figure;

plot(t*1e3,txSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title(['Adaptive Sonar Waveform - ' waveformName]);

grid on;

%% =========================================================
% 9. INSTANTANEOUS FREQUENCY
% =========================================================

figure;

plot(t*1e3,instFreq/1e3);

xlabel('Time (ms)');
ylabel('Frequency (kHz)');

title(['Adaptive Instantaneous Frequency - ' waveformName]);

grid on;

%% =========================================================
% 10. FFT
% =========================================================

figure;

plot(f/1e3,magnitude_dB);

xlabel('Frequency (kHz)');
ylabel('Magnitude (dB)');

title(['Adaptive Waveform Spectrum - ' waveformName]);

xlim([0 Fs/2/1e3]);

grid on;

%% =========================================================
% 11. SPECTROGRAM
% =========================================================

figure;

spectrogram(windowedSignal,256,200,1024,Fs,'yaxis');

title(['Adaptive Sonar Spectrogram - ' waveformName]);

%% =========================================================
% 12. BASIC VALIDATION
% =========================================================

fprintf('\nVALIDATION\n');
fprintf('----------------------------------------------------\n');

fprintf('Frequency range : %.2f - %.2f kHz\n', ...
    adaptiveFstart/1e3,adaptiveFstop/1e3);

fprintf('Expected BW     : %.2f kHz\n', ...
    adaptiveBW/1e3);

fprintf('Actual duration : %.3f ms\n', ...
    N/Fs*1e3);

fprintf('Peak amplitude  : %.3f\n', ...
    max(abs(txSignal)));

fprintf('\nADAPTIVE WAVEFORM GENERATION COMPLETE\n');
fprintf('====================================================\n');