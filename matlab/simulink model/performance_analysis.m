%% =========================================================
% SIH 26058
% ADAPTIVE SONAR PERFORMANCE ANALYSIS
%
% Automatically tests:
%   1. Normal condition
%   2. High turbidity
%   3. High noise
%   4. Deep water
%
% Measures:
%   - Selected waveform
%   - Adaptive parameters
%   - Target range
%   - Detected range
%   - Range error
%   - Detection status
%   - Matched-filter peak
% =========================================================

clear;
clc;
close all;

%% =========================================================
% 1. PROJECT PARAMETERS
% =========================================================

Fs = 2e6;
Ts = 1/Fs;

Fc = 300e3;
BW = 200e3;
Tp = 2e-3;
A = 1.0;

range = 5;
soundSpeed = 1500;

channelGain = 1;

windowType = 2;

phaseCode = [1 1 -1 1 -1 -1 1];

%% =========================================================
% 2. ADAPTIVE LIMITS / THRESHOLDS
% =========================================================

Fc_min = 100e3;
Fc_max = 500e3;

BW_min = 50e3;
BW_max = 200e3;

Tp_min = 0.5e-3;
Tp_max = 5e-3;

A_min = 0.1;
A_max = 1.0;

depth_threshold = 100;
turbidity_threshold = 500;
noise_threshold = -10;

%% =========================================================
% 3. TEST CONDITIONS
% =========================================================

conditionName = {
    'Normal'
    'High Turbidity'
    'High Noise'
    'Deep Water'
    };

depthTest = [
    50
    50
    50
    150
    ];

turbidityTest = [
    100
    600
    100
    100
    ];

noiseTest = [
    -20
    -20
    -5
    -20
    ];

numTests = length(conditionName);

%% =========================================================
% 4. RESULT STORAGE
% =========================================================

waveformResult = cell(numTests,1);

fcResult = zeros(numTests,1);
bwResult = zeros(numTests,1);
tpResult = zeros(numTests,1);
amplitudeResult = zeros(numTests,1);

detectedRangeResult = zeros(numTests,1);
rangeErrorResult = zeros(numTests,1);

peakResult = zeros(numTests,1);

detectionResult = false(numTests,1);

%% =========================================================
% 5. RUN ALL TEST CONDITIONS
% =========================================================

for test = 1:numTests

    %% -----------------------------------------------------
    % ENVIRONMENT
    % -----------------------------------------------------

    currentDepth = depthTest(test);
    currentTurbidity = turbidityTest(test);
    currentNoise = noiseTest(test);

    %% -----------------------------------------------------
    % DEFAULT TRANSMITTER
    % -----------------------------------------------------

    adaptiveFc = Fc;
    adaptiveBW = BW;
    adaptiveTp = Tp;
    adaptiveAmplitude = A;
    adaptiveWaveform = 1;

    %% -----------------------------------------------------
    % ADAPTIVE CONTROLLER
    % -----------------------------------------------------

    if currentTurbidity > turbidity_threshold

        adaptiveFc = 200e3;
        adaptiveBW = 100e3;
        adaptiveTp = 3e-3;
        adaptiveAmplitude = 0.8;
        adaptiveWaveform = 1;

    elseif currentNoise > noise_threshold

        adaptiveFc = 300e3;
        adaptiveBW = 200e3;
        adaptiveTp = 2e-3;
        adaptiveAmplitude = 1.0;
        adaptiveWaveform = 3;

    elseif currentDepth > depth_threshold

        adaptiveFc = 250e3;
        adaptiveBW = 150e3;
        adaptiveTp = 3e-3;
        adaptiveAmplitude = 1.0;
        adaptiveWaveform = 2;

    end

    %% -----------------------------------------------------
    % APPLY LIMITS
    % -----------------------------------------------------

    adaptiveFc = max(Fc_min,min(Fc_max,adaptiveFc));
    adaptiveBW = max(BW_min,min(BW_max,adaptiveBW));
    adaptiveTp = max(Tp_min,min(Tp_max,adaptiveTp));
    adaptiveAmplitude = max(A_min,min(A_max,adaptiveAmplitude));

    %% -----------------------------------------------------
    % WAVEFORM NAME
    % -----------------------------------------------------

    switch adaptiveWaveform

        case 1
            waveformName = 'LFM Chirp';

        case 2
            waveformName = 'Geometric Sweep';

        case 3
            waveformName = 'Phase-Coded Pulse';

    end

    waveformResult{test} = waveformName;

    %% -----------------------------------------------------
    % GENERATE ADAPTIVE WAVEFORM
    % -----------------------------------------------------

    N = round(adaptiveTp * Fs);

    t = (0:N-1)*Ts;

    fStart = adaptiveFc - adaptiveBW/2;
    fStop = adaptiveFc + adaptiveBW/2;

    switch adaptiveWaveform

        %% LFM
        case 1

            k = (fStop-fStart)/adaptiveTp;

            phase = 2*pi*( ...
                fStart*t + 0.5*k*t.^2);

            txSignal = adaptiveAmplitude*cos(phase);

        %% GEOMETRIC SWEEP
        case 2

            ratio = fStop/fStart;

            instFreq = fStart * ...
                ratio.^(t/adaptiveTp);

            phase = 2*pi*cumtrapz(t,instFreq);

            txSignal = adaptiveAmplitude*cos(phase);

        %% PHASE CODED
        case 3

            codeLength = length(phaseCode);

            txSignal = zeros(size(t));

            for n = 1:codeLength

                startIndex = floor((n-1)*N/codeLength)+1;

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

    end

    %% -----------------------------------------------------
    % WINDOW
    % -----------------------------------------------------

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

    txSignal = txSignal .* win;

    %% -----------------------------------------------------
    % UNDERWATER PROPAGATION
    % -----------------------------------------------------

    roundTripTime = (2*range)/soundSpeed;

    delaySamples = round(roundTripTime*Fs);

    receiveLength = length(txSignal)+delaySamples;

    receivedSignal = zeros(1,receiveLength);

    echoGain = channelGain/(1+range);

    echoSignal = echoGain*txSignal;

    startIndex = delaySamples+1;

    endIndex = startIndex+length(echoSignal)-1;

    receivedSignal(startIndex:endIndex) = echoSignal;

    %% -----------------------------------------------------
    % ADD NOISE
    % -----------------------------------------------------

    noiseAmplitude = 10^(currentNoise/20);

    noise = noiseAmplitude * ...
        randn(size(receivedSignal));

    noisyReceivedSignal = receivedSignal + noise;

    %% -----------------------------------------------------
    % MATCHED FILTER
    % -----------------------------------------------------

    matchedFilter = conj(fliplr(txSignal));

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

    rangeError = ...
        abs(detectedRange-range);

    %% -----------------------------------------------------
    % DETECTION DECISION
    % -----------------------------------------------------

    if rangeError < 0.1
        detectionSuccess = true;
    else
        detectionSuccess = false;
    end

    %% -----------------------------------------------------
    % STORE RESULTS
    % -----------------------------------------------------

    fcResult(test) = adaptiveFc;
    bwResult(test) = adaptiveBW;
    tpResult(test) = adaptiveTp;
    amplitudeResult(test) = adaptiveAmplitude;

    detectedRangeResult(test) = detectedRange;
    rangeErrorResult(test) = rangeError;

    peakResult(test) = peakValue;

    detectionResult(test) = detectionSuccess;

end

%% =========================================================
% 6. DISPLAY RESULTS
% =========================================================

fprintf('\n');
fprintf('==============================================================\n');
fprintf('        SIH 26058 - ADAPTIVE SONAR PERFORMANCE\n');
fprintf('==============================================================\n');

fprintf('\nTarget Range = %.2f m\n',range);
fprintf('Sound Speed  = %.2f m/s\n',soundSpeed);

fprintf('\n');

for test = 1:numTests

    fprintf('--------------------------------------------------------------\n');

    fprintf('%s\n',conditionName{test});

    fprintf('Waveform          : %s\n',waveformResult{test});
    fprintf('Centre Frequency  : %.2f kHz\n',fcResult(test)/1e3);
    fprintf('Bandwidth         : %.2f kHz\n',bwResult(test)/1e3);
    fprintf('Pulse Duration    : %.2f ms\n',tpResult(test)*1e3);
    fprintf('Amplitude         : %.2f\n',amplitudeResult(test));

    fprintf('Detected Range    : %.3f m\n', ...
        detectedRangeResult(test));

    fprintf('Range Error       : %.3f m\n', ...
        rangeErrorResult(test));

    fprintf('Matched Filter Peak : %.3f\n', ...
        peakResult(test));

    if detectionResult(test)
        fprintf('Detection Status  : SUCCESS\n');
    else
        fprintf('Detection Status  : FAILED\n');
    end

end

fprintf('--------------------------------------------------------------\n');

%% =========================================================
% 7. PERFORMANCE TABLE
% =========================================================

fprintf('\n');
fprintf('================ PERFORMANCE SUMMARY =======================\n');

fprintf('\n');

fprintf('%-18s %-22s %-12s %-12s %-12s\n', ...
    'Condition','Waveform','Fc(kHz)', ...
    'BW(kHz)','Range(m)');

fprintf('--------------------------------------------------------------\n');

for test = 1:numTests

    fprintf('%-18s %-22s %-12.1f %-12.1f %-12.3f\n', ...
        conditionName{test}, ...
        waveformResult{test}, ...
        fcResult(test)/1e3, ...
        bwResult(test)/1e3, ...
        detectedRangeResult(test));

end

fprintf('==============================================================\n');

%% =========================================================
% 8. RANGE ERROR GRAPH
% =========================================================

figure;

bar(rangeErrorResult);

set(gca,'XTick',1:numTests);

set(gca,'XTickLabel',conditionName);

ylabel('Range Error (m)');

title('SIH 26058 - Range Detection Error');

grid on;

%% =========================================================
% 9. DETECTION PERFORMANCE GRAPH
% =========================================================

figure;

bar(double(detectionResult));

set(gca,'XTick',1:numTests);

set(gca,'XTickLabel',conditionName);

ylabel('Detection Success');

title('SIH 26058 - Adaptive Target Detection');

ylim([0 1.2]);

grid on;

%% =========================================================
% 10. ADAPTIVE FREQUENCY GRAPH
% =========================================================

figure;

bar(fcResult/1e3);

set(gca,'XTick',1:numTests);

set(gca,'XTickLabel',conditionName);

ylabel('Centre Frequency (kHz)');

title('SIH 26058 - Adaptive Centre Frequency');

grid on;

%% =========================================================
% 11. ADAPTIVE BANDWIDTH GRAPH
% =========================================================

figure;

bar(bwResult/1e3);

set(gca,'XTick',1:numTests);

set(gca,'XTickLabel',conditionName);

ylabel('Bandwidth (kHz)');

title('SIH 26058 - Adaptive Bandwidth');

grid on;

%% =========================================================
% 12. COMPLETE
% =========================================================

fprintf('\n');
fprintf('PERFORMANCE ANALYSIS COMPLETE\n');
fprintf('==============================================================\n');