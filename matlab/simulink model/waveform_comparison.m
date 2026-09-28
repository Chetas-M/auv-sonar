%% =========================================================
% SIH 26058
% THREE-WAVEFORM PERFORMANCE COMPARISON
%
% Compares:
%   1. LFM Chirp
%   2. Geometric Sweep
%   3. Phase-Coded Pulse
%
% Same:
%   Target range
%   Sound speed
%   SNR
%   Sampling rate
%
% Metrics:
%   Detected range
%   Range error
%   Matched-filter peak
%   Detection status
% =========================================================

clear;
clc;
close all;

rng(20);

%% =========================================================
% 1. SYSTEM PARAMETERS
% =========================================================

Fs = 2e6;
Ts = 1/Fs;

soundSpeed = 1500;

targetRange = 5;

channelGain = 1;

inputSNR = 0;

%% =========================================================
% 2. WAVEFORM PARAMETERS
% =========================================================

Fc = 300e3;
BW = 200e3;
Tp = 2e-3;
A = 1.0;

phaseCode = [1 1 -1 1 -1 -1 1];

%% =========================================================
% 3. WAVEFORM NAMES
% =========================================================

waveformNames = {
    'LFM Chirp'
    'Geometric Sweep'
    'Phase-Coded Pulse'
    };

numWaveforms = 3;

%% =========================================================
% 4. RESULT STORAGE
% =========================================================

detectedRange = zeros(numWaveforms,1);
rangeError = zeros(numWaveforms,1);
matchedPeak = zeros(numWaveforms,1);
detectionSuccess = false(numWaveforms,1);

%% =========================================================
% 5. TEST EACH WAVEFORM
% =========================================================

for w = 1:numWaveforms

    %% -----------------------------------------------------
    % TIME VECTOR
    % -----------------------------------------------------

    N = round(Tp*Fs);

    t = (0:N-1)*Ts;

    %% -----------------------------------------------------
    % GENERATE WAVEFORM
    % -----------------------------------------------------

    switch w

        %% =================================================
        % LFM CHIRP
        % =================================================

        case 1

            fStart = Fc - BW/2;
            fStop = Fc + BW/2;

            k = (fStop-fStart)/Tp;

            phase = 2*pi*( ...
                fStart*t + ...
                0.5*k*t.^2);

            txSignal = A*cos(phase);

        %% =================================================
        % GEOMETRIC SWEEP
        % =================================================

        case 2

            fStart = Fc - BW/2;
            fStop = Fc + BW/2;

            ratio = fStop/fStart;

            instFreq = ...
                fStart*ratio.^(t/Tp);

            phase = ...
                2*pi*cumtrapz(t,instFreq);

            txSignal = A*cos(phase);

        %% =================================================
        % PHASE-CODED PULSE
        % =================================================

        case 3

            txSignal = zeros(size(t));

            codeLength = length(phaseCode);

            samplesPerChip = floor(N/codeLength);

            for chip = 1:codeLength

                startIndex = ...
                    (chip-1)*samplesPerChip + 1;

                if chip == codeLength

                    endIndex = N;

                else

                    endIndex = ...
                        chip*samplesPerChip;

                end

                txSignal(startIndex:endIndex) = ...
                    A*phaseCode(chip)* ...
                    cos(2*pi*Fc*t(startIndex:endIndex));

            end

    end

    %% -----------------------------------------------------
    % APPLY HANN WINDOW
    % -----------------------------------------------------

    txSignal = txSignal .* hann(N).';

    %% -----------------------------------------------------
    % TARGET PROPAGATION
    % -----------------------------------------------------

    roundTripTime = ...
        (2*targetRange)/soundSpeed;

    delaySamples = ...
        round(roundTripTime*Fs);

    receiveLength = ...
        length(txSignal)+delaySamples;

    receivedSignal = ...
        zeros(1,receiveLength);

    %% -----------------------------------------------------
    % TARGET ECHO
    % -----------------------------------------------------

    echoGain = ...
        channelGain/(1+targetRange);

    echoSignal = ...
        echoGain*txSignal;

    startIndex = delaySamples+1;

    endIndex = ...
        startIndex+length(echoSignal)-1;

    receivedSignal(startIndex:endIndex) = ...
        echoSignal;

    %% -----------------------------------------------------
    % CALCULATE NOISE POWER FROM SNR
    % -----------------------------------------------------

    signalPower = mean(echoSignal.^2);

    noisePower = ...
        signalPower/(10^(inputSNR/10));

    noiseStd = sqrt(noisePower);

    noise = ...
        noiseStd*randn(size(receivedSignal));

    noisyReceivedSignal = ...
        receivedSignal+noise;

    %% -----------------------------------------------------
    % MATCHED FILTER
    % -----------------------------------------------------

    matchedFilter = ...
        conj(fliplr(txSignal));

    matchedOutput = ...
        conv(noisyReceivedSignal,matchedFilter);

    %% -----------------------------------------------------
    % FIND PEAK
    % -----------------------------------------------------

    [peakValue,peakIndex] = ...
        max(abs(matchedOutput));

    detectedDelaySamples = ...
        peakIndex-length(txSignal);

    detectedDelay = ...
        detectedDelaySamples/Fs;

    currentDetectedRange = ...
        (detectedDelay*soundSpeed)/2;

    currentRangeError = ...
        abs(currentDetectedRange-targetRange);

    %% -----------------------------------------------------
    % DETECTION
    % -----------------------------------------------------

    if currentRangeError < 0.1

        detectionSuccess(w) = true;

    else

        detectionSuccess(w) = false;

    end

    %% -----------------------------------------------------
    % STORE
    % -----------------------------------------------------

    detectedRange(w) = currentDetectedRange;

    rangeError(w) = currentRangeError;

    matchedPeak(w) = peakValue;

end

%% =========================================================
% 6. DISPLAY RESULTS
% =========================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('       SIH 26058 - THREE-WAVEFORM COMPARISON\n');
fprintf('============================================================\n');

fprintf('\nTarget Range       : %.2f m\n',targetRange);
fprintf('Centre Frequency   : %.1f kHz\n',Fc/1e3);
fprintf('Bandwidth          : %.1f kHz\n',BW/1e3);
fprintf('Pulse Duration     : %.2f ms\n',Tp*1e3);
fprintf('Input SNR          : %.1f dB\n',inputSNR);

fprintf('\n');

fprintf('%-23s %-15s %-15s %-15s %-15s\n', ...
    'Waveform', ...
    'Detected(m)', ...
    'Error(m)', ...
    'MF Peak', ...
    'Status');

fprintf('----------------------------------------------------------------\n');

for w = 1:numWaveforms

    if detectionSuccess(w)

        statusText = 'SUCCESS';

    else

        statusText = 'FAILED';

    end

    fprintf('%-23s %-15.3f %-15.4f %-15.3f %-15s\n', ...
        waveformNames{w}, ...
        detectedRange(w), ...
        rangeError(w), ...
        matchedPeak(w), ...
        statusText);

end

fprintf('================================================================\n');

%% =========================================================
% 7. RANGE COMPARISON
% =========================================================

figure;

bar(detectedRange);

set(gca,'XTick',1:numWaveforms);

set(gca,'XTickLabel',waveformNames);

ylabel('Detected Range (m)');

title('SIH 26058 - Detected Range Comparison');

grid on;

%% =========================================================
% 8. RANGE ERROR COMPARISON
% =========================================================

figure;

bar(rangeError);

set(gca,'XTick',1:numWaveforms);

set(gca,'XTickLabel',waveformNames);

ylabel('Range Error (m)');

title('SIH 26058 - Range Error Comparison');

grid on;

%% =========================================================
% 9. MATCHED FILTER PEAK COMPARISON
% =========================================================

figure;

bar(matchedPeak);

set(gca,'XTick',1:numWaveforms);

set(gca,'XTickLabel',waveformNames);

ylabel('Matched Filter Peak');

title('SIH 26058 - Matched Filter Peak Comparison');

grid on;

%% =========================================================
% 10. DETECTION SUCCESS
% =========================================================

figure;

bar(double(detectionSuccess));

set(gca,'XTick',1:numWaveforms);

set(gca,'XTickLabel',waveformNames);

ylabel('Detection Success');

title('SIH 26058 - Waveform Detection Comparison');

ylim([0 1.2]);

grid on;

%% =========================================================
% 11. COMPLETE
% =========================================================

fprintf('\n');
fprintf('THREE-WAVEFORM COMPARISON COMPLETE\n');
fprintf('============================================================\n');