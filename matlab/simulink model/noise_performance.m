%% =========================================================
% SIH 26058
% NOISE ROBUSTNESS PERFORMANCE ANALYSIS
%
% Tests target detection at different noise levels.
%
% Target = 5 m
% Waveform = LFM Chirp
% =========================================================

clear;
clc;
close all;

rng(1);   % Repeatable noise for comparison

%% =========================================================
% 1. SYSTEM PARAMETERS
% =========================================================

Fs = 2e6;
Ts = 1/Fs;

soundSpeed = 1500;
channelGain = 1;

targetRange = 5;

Fc = 300e3;
BW = 200e3;
Tp = 2e-3;
A = 1.0;

%% =========================================================
% 2. NOISE LEVELS TO TEST
% =========================================================

noiseLevels = [-30 -20 -10 -5 0];

numTests = length(noiseLevels);

%% =========================================================
% 3. GENERATE LFM TRANSMITTED SIGNAL
% =========================================================

N = round(Tp*Fs);

t = (0:N-1)*Ts;

fStart = Fc - BW/2;
fStop = Fc + BW/2;

k = (fStop-fStart)/Tp;

phase = 2*pi*( ...
    fStart*t + 0.5*k*t.^2);

txSignal = A*cos(phase);

%% =========================================================
% 4. APPLY HANN WINDOW
% =========================================================

txSignal = txSignal .* hann(N).';

%% =========================================================
% 5. RESULT STORAGE
% =========================================================

detectedRanges = zeros(numTests,1);
rangeErrors = zeros(numTests,1);
detectedDelays = zeros(numTests,1);
peakValues = zeros(numTests,1);
detectionSuccess = false(numTests,1);

%% =========================================================
% 6. RUN NOISE TESTS
% =========================================================

for test = 1:numTests

    noiseLevel = noiseLevels(test);

    %% -----------------------------------------------------
    % PROPAGATION DELAY
    % -----------------------------------------------------

    roundTripTime = ...
        (2*targetRange)/soundSpeed;

    delaySamples = ...
        round(roundTripTime*Fs);

    %% -----------------------------------------------------
    % CREATE RECEIVED SIGNAL
    % -----------------------------------------------------

    receiveLength = ...
        length(txSignal)+delaySamples;

    receivedSignal = ...
        zeros(1,receiveLength);

    %% -----------------------------------------------------
    % ECHO ATTENUATION
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
    % RANGE ERROR
    % -----------------------------------------------------

    rangeError = ...
        abs(detectedRange-targetRange);

    %% -----------------------------------------------------
    % DETECTION DECISION
    % -----------------------------------------------------

    if rangeError < 0.1

        detectionSuccess(test) = true;

    else

        detectionSuccess(test) = false;

    end

    %% -----------------------------------------------------
    % STORE RESULTS
    % -----------------------------------------------------

    detectedRanges(test) = detectedRange;
    rangeErrors(test) = rangeError;
    detectedDelays(test) = detectedDelay;
    peakValues(test) = peakValue;

end

%% =========================================================
% 7. DISPLAY RESULTS
% =========================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('       SIH 26058 - NOISE ROBUSTNESS TEST\n');
fprintf('============================================================\n');

fprintf('\nTarget Range       : %.2f m\n',targetRange);
fprintf('Waveform           : LFM Chirp\n');
fprintf('Centre Frequency   : %.1f kHz\n',Fc/1e3);
fprintf('Bandwidth          : %.1f kHz\n',BW/1e3);
fprintf('Pulse Duration     : %.2f ms\n',Tp*1e3);

fprintf('\n');

fprintf('%-12s %-15s %-15s %-15s %-15s\n', ...
    'Noise(dB)', ...
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

    fprintf('%-12.1f %-15.3f %-15.3f %-15.3f %-15s\n', ...
        noiseLevels(test), ...
        detectedDelays(test)*1e3, ...
        detectedRanges(test), ...
        rangeErrors(test), ...
        statusText);

end

fprintf('============================================================\n');

%% =========================================================
% 8. MATCHED FILTER PEAK GRAPH
% =========================================================

figure;

plot(noiseLevels,peakValues,'o-','LineWidth',2);

xlabel('Noise Level (dB)');
ylabel('Matched Filter Peak');

title('SIH 26058 - Matched Filter Peak vs Noise');

grid on;

%% =========================================================
% 9. RANGE ERROR GRAPH
% =========================================================

figure;

plot(noiseLevels,rangeErrors,'o-','LineWidth',2);

xlabel('Noise Level (dB)');
ylabel('Range Error (m)');

title('SIH 26058 - Range Error vs Noise');

grid on;

%% =========================================================
% 10. DETECTION SUCCESS GRAPH
% =========================================================

figure;

bar(noiseLevels,double(detectionSuccess));

xlabel('Noise Level (dB)');
ylabel('Detection Success');

title('SIH 26058 - Detection Success vs Noise');

ylim([0 1.2]);

grid on;

%% =========================================================
% 11. DETECTED RANGE GRAPH
% =========================================================

figure;

plot(noiseLevels,detectedRanges,'o-','LineWidth',2);

hold on;

plot(noiseLevels, ...
     targetRange*ones(size(noiseLevels)), ...
     '--','LineWidth',1.5);

xlabel('Noise Level (dB)');
ylabel('Detected Range (m)');

title('SIH 26058 - Detected Range vs Noise');

legend('Detected Range','Actual Range');

grid on;

hold off;

%% =========================================================
% 12. COMPLETE
% =========================================================

fprintf('\nNOISE ROBUSTNESS TEST COMPLETE\n');
fprintf('============================================================\n');