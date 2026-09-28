%% =========================================================
% SIH 26058
% MULTI-RANGE TARGET PERFORMANCE ANALYSIS
%
% Tests target detection at multiple ranges.
%
% Target ranges:
%   2 m, 5 m, 8 m, 10 m, 12 m
%
% Uses:
%   LFM waveform
%   Underwater propagation
%   Noise
%   Matched filtering
%   Range estimation
% =========================================================

clear;
clc;
close all;

%% =========================================================
% 1. BASIC PARAMETERS
% =========================================================

Fs = 2e6;
Ts = 1/Fs;

soundSpeed = 1500;

channelGain = 1;

noiseLevel = -20;

%% =========================================================
% 2. TRANSMITTER PARAMETERS
% =========================================================

Fc = 300e3;
BW = 200e3;
Tp = 2e-3;
A = 1.0;

fStart = Fc - BW/2;
fStop  = Fc + BW/2;

%% =========================================================
% 3. TARGET RANGES
% =========================================================

targetRanges = [2 5 8 10 12];

numTests = length(targetRanges);

%% =========================================================
% 4. GENERATE REFERENCE LFM
% =========================================================

N = round(Tp*Fs);

t = (0:N-1)*Ts;

k = (fStop-fStart)/Tp;

phase = 2*pi*( ...
    fStart*t + 0.5*k*t.^2);

txSignal = A*cos(phase);

%% =========================================================
% 5. APPLY HANN WINDOW
% =========================================================

txSignal = txSignal .* hann(N).';

%% =========================================================
% 6. RESULT STORAGE
% =========================================================

detectedRanges = zeros(numTests,1);

rangeErrors = zeros(numTests,1);

detectedDelays = zeros(numTests,1);

peakValues = zeros(numTests,1);

detectionSuccess = false(numTests,1);

%% =========================================================
% 7. TEST EACH TARGET RANGE
% =========================================================

for test = 1:numTests

    targetRange = targetRanges(test);

    %% -----------------------------------------------------
    % PROPAGATION DELAY
    % -----------------------------------------------------

    roundTripTime = ...
        (2*targetRange)/soundSpeed;

    delaySamples = ...
        round(roundTripTime*Fs);

    %% -----------------------------------------------------
    % RECEIVED SIGNAL
    % -----------------------------------------------------

    receiveLength = ...
        length(txSignal)+delaySamples;

    receivedSignal = ...
        zeros(1,receiveLength);

    %% -----------------------------------------------------
    % SIMPLE ECHO ATTENUATION
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
    % ADD NOISE
    % -----------------------------------------------------

    noiseAmplitude = ...
        10^(noiseLevel/20);

    noise = ...
        noiseAmplitude*randn(size(receivedSignal));

    noisyReceivedSignal = ...
        receivedSignal+noise;

    %% -----------------------------------------------------
    % MATCHED FILTER
    % -----------------------------------------------------

    matchedFilter = ...
        conj(fliplr(txSignal));

    matchedOutput = conv( ...
        noisyReceivedSignal, ...
        matchedFilter);

    %% -----------------------------------------------------
    % FIND PEAK
    % -----------------------------------------------------

    [peakValue,peakIndex] = ...
        max(abs(matchedOutput));

    detectedDelaySamples = ...
        peakIndex-length(txSignal);

    detectedDelay = ...
        detectedDelaySamples/Fs;

    detectedRange = ...
        (detectedDelay*soundSpeed)/2;

    %% -----------------------------------------------------
    % ERROR
    % -----------------------------------------------------

    rangeError = ...
        abs(detectedRange-targetRange);

    %% -----------------------------------------------------
    % DETECTION
    % -----------------------------------------------------

    if rangeError < 0.1

        detectionSuccess(test) = true;

    else

        detectionSuccess(test) = false;

    end

    %% -----------------------------------------------------
    % STORE
    % -----------------------------------------------------

    detectedRanges(test) = detectedRange;

    rangeErrors(test) = rangeError;

    detectedDelays(test) = detectedDelay;

    peakValues(test) = peakValue;

end

%% =========================================================
% 8. DISPLAY RESULTS
% =========================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('       SIH 26058 - MULTI-RANGE PERFORMANCE TEST\n');
fprintf('============================================================\n');

fprintf('\nWaveform          : LFM Chirp\n');
fprintf('Centre Frequency  : %.1f kHz\n',Fc/1e3);
fprintf('Bandwidth         : %.1f kHz\n',BW/1e3);
fprintf('Pulse Duration    : %.2f ms\n',Tp*1e3);
fprintf('Noise Level       : %.1f dB\n',noiseLevel);
fprintf('Sound Speed       : %.1f m/s\n',soundSpeed);

fprintf('\n');

fprintf('%-12s %-15s %-15s %-15s %-15s\n', ...
    'Actual(m)', ...
    'Delay(ms)', ...
    'Detected(m)', ...
    'Error(m)', ...
    'Status');

fprintf('------------------------------------------------------------\n');

for test = 1:numTests

    if detectionSuccess(test)
        statusText = 'SUCCESS';
    else
        statusText = 'FAILED';
    end

    fprintf('%-12.2f %-15.3f %-15.3f %-15.3f %-15s\n', ...
        targetRanges(test), ...
        detectedDelays(test)*1e3, ...
        detectedRanges(test), ...
        rangeErrors(test), ...
        statusText);

end

fprintf('============================================================\n');

%% =========================================================
% 9. RANGE COMPARISON GRAPH
% =========================================================

figure;

plot(targetRanges,detectedRanges,'o-','LineWidth',2);

hold on;

plot(targetRanges,targetRanges,'--','LineWidth',1.5);

xlabel('Actual Target Range (m)');
ylabel('Detected Target Range (m)');

title('SIH 26058 - Actual vs Detected Target Range');

legend('Detected Range','Ideal Range');

grid on;

hold off;

%% =========================================================
% 10. RANGE ERROR GRAPH
% =========================================================

figure;

bar(targetRanges,rangeErrors);

xlabel('Actual Target Range (m)');
ylabel('Range Error (m)');

title('SIH 26058 - Range Detection Error');

grid on;

%% =========================================================
% 11. DETECTION SUCCESS GRAPH
% =========================================================

figure;

bar(targetRanges,double(detectionSuccess));

xlabel('Actual Target Range (m)');
ylabel('Detection Success');

title('SIH 26058 - Detection Success vs Target Range');

ylim([0 1.2]);

grid on;

%% =========================================================
% 12. THEORETICAL RANGE RESOLUTION
% =========================================================

rangeResolution = ...
    soundSpeed/(2*BW);

fprintf('\nTHEORETICAL RANGE RESOLUTION\n');
fprintf('------------------------------------------------------------\n');

fprintf('Bandwidth        : %.1f kHz\n',BW/1e3);

fprintf('Range Resolution : %.6f m\n',rangeResolution);

fprintf('Range Resolution : %.3f mm\n',rangeResolution*1000);

fprintf('============================================================\n');

fprintf('\nMULTI-RANGE PERFORMANCE TEST COMPLETE\n');
fprintf('============================================================\n');