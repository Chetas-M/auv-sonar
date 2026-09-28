%% =========================================================
% SIH 26058
% PROPER SNR-BASED DETECTION PERFORMANCE
%
% Tests sonar detection at different SNR values.
%
% Target Range : 5 m
% Waveform     : LFM Chirp
%
% Metrics:
%   - Input SNR
%   - Detection Probability
%   - Range Error
%   - Matched Filter Peak
% =========================================================

clear;
clc;
close all;

%% =========================================================
% 1. RANDOM SEED
% =========================================================

rng(10);

%% =========================================================
% 2. SYSTEM PARAMETERS
% =========================================================

Fs = 2e6;
Ts = 1/Fs;

soundSpeed = 1500;

targetRange = 5;

channelGain = 1;

%% =========================================================
% 3. LFM TRANSMITTER
% =========================================================

Fc = 300e3;
BW = 200e3;
Tp = 2e-3;
A = 1.0;

fStart = Fc - BW/2;
fStop  = Fc + BW/2;

%% =========================================================
% 4. SNR VALUES
% =========================================================

snrValues = [-10 -5 0 5 10 15 20];

numSNR = length(snrValues);

%% =========================================================
% 5. NUMBER OF MONTE CARLO TRIALS
% =========================================================

numTrials = 30;

%% =========================================================
% 6. GENERATE TRANSMITTED LFM
% =========================================================

N = round(Tp*Fs);

t = (0:N-1)*Ts;

k = (fStop-fStart)/Tp;

phase = 2*pi*( ...
    fStart*t + 0.5*k*t.^2);

txSignal = A*cos(phase);

%% =========================================================
% 7. APPLY HANN WINDOW
% =========================================================

txSignal = txSignal .* hann(N).';

%% =========================================================
% 8. CREATE TARGET ECHO
% =========================================================

roundTripTime = ...
    (2*targetRange)/soundSpeed;

delaySamples = ...
    round(roundTripTime*Fs);

receiveLength = ...
    length(txSignal)+delaySamples;

receivedSignal = zeros(1,receiveLength);

echoGain = ...
    channelGain/(1+targetRange);

echoSignal = ...
    echoGain*txSignal;

startIndex = delaySamples+1;

endIndex = ...
    startIndex+length(echoSignal)-1;

receivedSignal(startIndex:endIndex) = ...
    echoSignal;

%% =========================================================
% 9. SIGNAL POWER
% =========================================================

signalPower = mean(echoSignal.^2);

%% =========================================================
% 10. RESULT STORAGE
% =========================================================

measuredSNR = zeros(numSNR,1);

detectionProbability = zeros(numSNR,1);

meanRangeError = zeros(numSNR,1);

meanPeak = zeros(numSNR,1);

%% =========================================================
% 11. SNR TEST LOOP
% =========================================================

for s = 1:numSNR

    targetSNR = snrValues(s);

    detectedCount = 0;

    rangeErrors = zeros(numTrials,1);

    peakValues = zeros(numTrials,1);

    actualSNRs = zeros(numTrials,1);

    for trial = 1:numTrials

        %% -------------------------------------------------
        % CALCULATE REQUIRED NOISE POWER
        % -------------------------------------------------

        noisePower = ...
            signalPower / ...
            (10^(targetSNR/10));

        noiseStd = sqrt(noisePower);

        %% -------------------------------------------------
        % GENERATE NOISE
        % -------------------------------------------------

        noise = ...
            noiseStd * randn(size(receivedSignal));

        noisyReceivedSignal = ...
            receivedSignal + noise;

        %% -------------------------------------------------
        % MEASURE ACTUAL SNR
        % -------------------------------------------------

        actualSNR = ...
            10*log10(signalPower/noisePower);

        actualSNRs(trial) = actualSNR;

        %% -------------------------------------------------
        % MATCHED FILTER
        % -------------------------------------------------

        matchedFilter = ...
            conj(fliplr(txSignal));

        matchedOutput = conv( ...
            noisyReceivedSignal, ...
            matchedFilter);

        %% -------------------------------------------------
        % FIND PEAK
        % -------------------------------------------------

        [peakValue,peakIndex] = ...
            max(abs(matchedOutput));

        peakValues(trial) = peakValue;

        %% -------------------------------------------------
        % CALCULATE DELAY
        % -------------------------------------------------

        detectedDelaySamples = ...
            peakIndex-length(txSignal);

        detectedDelay = ...
            detectedDelaySamples/Fs;

        %% -------------------------------------------------
        % CALCULATE RANGE
        % -------------------------------------------------

        detectedRange = ...
            (detectedDelay*soundSpeed)/2;

        %% -------------------------------------------------
        % RANGE ERROR
        % -------------------------------------------------

        rangeError = ...
            abs(detectedRange-targetRange);

        rangeErrors(trial) = rangeError;

        %% -------------------------------------------------
        % DETECTION DECISION
        % -------------------------------------------------

        if rangeError < 0.1

            detectedCount = ...
                detectedCount + 1;

        end

    end

    %% -----------------------------------------------------
    % STORE SNR RESULTS
    % -----------------------------------------------------

    measuredSNR(s) = mean(actualSNRs);

    detectionProbability(s) = ...
        detectedCount/numTrials;

    meanRangeError(s) = ...
        mean(rangeErrors);

    meanPeak(s) = ...
        mean(peakValues);

end

%% =========================================================
% 12. DISPLAY RESULTS
% =========================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('       SIH 26058 - SNR DETECTION PERFORMANCE\n');
fprintf('============================================================\n');

fprintf('\nTarget Range       : %.2f m\n',targetRange);
fprintf('Waveform           : LFM Chirp\n');
fprintf('Centre Frequency   : %.1f kHz\n',Fc/1e3);
fprintf('Bandwidth          : %.1f kHz\n',BW/1e3);
fprintf('Pulse Duration     : %.2f ms\n',Tp*1e3);
fprintf('Trials per SNR     : %d\n',numTrials);

fprintf('\n');

fprintf('%-12s %-15s %-20s %-15s\n', ...
    'SNR(dB)', ...
    'Measured(dB)', ...
    'Detection Prob.', ...
    'Mean Error(m)');

fprintf('------------------------------------------------------------\n');

for s = 1:numSNR

    fprintf('%-12.1f %-15.2f %-20.2f %-15.4f\n', ...
        snrValues(s), ...
        measuredSNR(s), ...
        detectionProbability(s), ...
        meanRangeError(s));

end

fprintf('============================================================\n');

%% =========================================================
% 13. DETECTION PROBABILITY GRAPH
% =========================================================

figure;

plot(measuredSNR, ...
     detectionProbability, ...
     'o-', ...
     'LineWidth',2);

xlabel('Input SNR (dB)');
ylabel('Detection Probability');

title('SIH 26058 - Detection Probability vs SNR');

ylim([0 1.1]);

grid on;

%% =========================================================
% 14. RANGE ERROR GRAPH
% =========================================================

figure;

plot(measuredSNR, ...
     meanRangeError, ...
     'o-', ...
     'LineWidth',2);

xlabel('Input SNR (dB)');
ylabel('Mean Range Error (m)');

title('SIH 26058 - Range Error vs SNR');

grid on;

%% =========================================================
% 15. MATCHED FILTER PEAK GRAPH
% =========================================================

figure;

plot(measuredSNR, ...
     meanPeak, ...
     'o-', ...
     'LineWidth',2);

xlabel('Input SNR (dB)');
ylabel('Mean Matched Filter Peak');

title('SIH 26058 - Matched Filter Peak vs SNR');

grid on;

%% =========================================================
% 16. DETECTION THRESHOLD
% =========================================================

successfulSNR = ...
    measuredSNR(detectionProbability >= 0.9);

if ~isempty(successfulSNR)

    thresholdSNR = min(successfulSNR);

    fprintf('\n');
    fprintf('DETECTION PERFORMANCE\n');
    fprintf('------------------------------------------------------------\n');

    fprintf(['Minimum tested SNR with >=90%% detection ' ...
             'probability: %.2f dB\n'], ...
             thresholdSNR);

else

    fprintf('\n');
    fprintf('No tested SNR achieved >=90%% detection probability.\n');

end

%% =========================================================
% 17. COMPLETE
% =========================================================

fprintf('\n');
fprintf('SNR PERFORMANCE ANALYSIS COMPLETE\n');
fprintf('============================================================\n');