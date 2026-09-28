%% =========================================================
% SIH 26058
% WAVEFORM vs SNR WITH DETECTION THRESHOLD
%
% Purpose:
% Compare LFM, Geometric Sweep and Phase-Coded waveforms
% using a matched-filter detection threshold.
%
% Target Range : 5 m
% SNR          : -20 to 20 dB
%
% Metrics:
%   Detection Probability
%   Range Error
%   Matched Filter Peak
%   Noise Floor
% =========================================================

clear;
clc;
close all;

rng(100);

%% =========================================================
% 1. SYSTEM PARAMETERS
% =========================================================

Fs = 2e6;
Ts = 1/Fs;

soundSpeed = 1500;

targetRange = 5;

channelGain = 1;

Fc = 300e3;
BW = 200e3;
Tp = 2e-3;
A = 1.0;

phaseCode = [1 1 -1 1 -1 -1 1];

%% =========================================================
% 2. SNR RANGE
% =========================================================

snrValues = [-20 -15 -10 -5 0 5 10 15 20];

numSNR = length(snrValues);

%% =========================================================
% 3. MONTE CARLO TRIALS
% =========================================================

numTrials = 50;

%% =========================================================
% 4. DETECTION THRESHOLD
% =========================================================

thresholdMultiplier = 6;

%% =========================================================
% 5. WAVEFORM NAMES
% =========================================================

waveformNames = {
    'LFM Chirp'
    'Geometric Sweep'
    'Phase-Coded Pulse'
    };

numWaveforms = 3;

%% =========================================================
% 6. RESULT STORAGE
% =========================================================

detectionProbability = zeros(numWaveforms,numSNR);

meanRangeError = nan(numWaveforms,numSNR);

meanPeak = zeros(numWaveforms,numSNR);

meanThreshold = zeros(numWaveforms,numSNR);

%% =========================================================
% 7. WAVEFORM LOOP
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

            samplesPerChip = ...
                floor(N/codeLength);

            for chip = 1:codeLength

                startIndex = ...
                    (chip-1)*samplesPerChip+1;

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
    % WINDOW
    % -----------------------------------------------------

    txSignal = ...
        txSignal .* hann(N).';

    %% -----------------------------------------------------
    % PROPAGATION DELAY
    % -----------------------------------------------------

    roundTripTime = ...
        2*targetRange/soundSpeed;

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
    % SIGNAL POWER
    % -----------------------------------------------------

    signalPower = ...
        mean(echoSignal.^2);

    %% -----------------------------------------------------
    % MATCHED FILTER
    % -----------------------------------------------------

    matchedFilter = ...
        conj(fliplr(txSignal));

    %% =====================================================
    % SNR LOOP
    % =====================================================

    for s = 1:numSNR

        targetSNR = snrValues(s);

        detectedCount = 0;

        successfulErrors = [];

        trialPeaks = zeros(numTrials,1);

        trialThresholds = zeros(numTrials,1);

        for trial = 1:numTrials

            %% -------------------------------------------------
            % NOISE POWER
            % -------------------------------------------------

            noisePower = ...
                signalPower / ...
                (10^(targetSNR/10));

            noiseStd = sqrt(noisePower);

            %% -------------------------------------------------
            % GENERATE NOISE
            % -------------------------------------------------

            noise = ...
                noiseStd*randn(size(receivedSignal));

            noisyReceivedSignal = ...
                receivedSignal + noise;

            %% -------------------------------------------------
            % MATCHED FILTER
            % -------------------------------------------------

            matchedOutput = ...
                conv(noisyReceivedSignal,matchedFilter);

            magnitudeOutput = ...
                abs(matchedOutput);

            %% -------------------------------------------------
            % ESTIMATE NOISE FLOOR
            %
            % Exclude region around expected target.
            % This prevents the target peak from entering
            % the noise estimate.
            % -------------------------------------------------

            expectedPeak = ...
                delaySamples + length(txSignal);

            exclusionWidth = ...
                round(0.01*length(matchedOutput));

            noiseRegion = true( ...
                size(magnitudeOutput));

            lowerIndex = ...
                max(1,expectedPeak-exclusionWidth);

            upperIndex = ...
                min(length(magnitudeOutput), ...
                    expectedPeak+exclusionWidth);

            noiseRegion(lowerIndex:upperIndex) = false;

            background = ...
                magnitudeOutput(noiseRegion);

            %% -------------------------------------------------
            % NOISE FLOOR
            % -------------------------------------------------

            noiseMean = mean(background);

            noiseStdMF = std(background);

            threshold = ...
                noiseMean + ...
                thresholdMultiplier*noiseStdMF;

            %% -------------------------------------------------
            % PEAK DETECTION
            % -------------------------------------------------

            [peakValue,peakIndex] = ...
                max(magnitudeOutput);

            trialPeaks(trial) = peakValue;

            trialThresholds(trial) = threshold;

            %% -------------------------------------------------
            % DETECTION DECISION
            % -------------------------------------------------

            if peakValue > threshold

                detectedDelaySamples = ...
                    peakIndex-length(txSignal);

                detectedDelay = ...
                    detectedDelaySamples/Fs;

                currentRange = ...
                    detectedDelay*soundSpeed/2;

                currentError = ...
                    abs(currentRange-targetRange);

                %% ---------------------------------------------
                % VALID RANGE CHECK
                % ---------------------------------------------

                if currentError < 0.1

                    detectedCount = ...
                        detectedCount+1;

                    successfulErrors = ...
                        [successfulErrors currentError];

                end

            end

        end

        %% -----------------------------------------------------
        % STORE RESULTS
        % -----------------------------------------------------

        detectionProbability(w,s) = ...
            detectedCount/numTrials;

        meanPeak(w,s) = ...
            mean(trialPeaks);

        meanThreshold(w,s) = ...
            mean(trialThresholds);

        if ~isempty(successfulErrors)

            meanRangeError(w,s) = ...
                mean(successfulErrors);

        end

    end

end

%% =========================================================
% 8. DISPLAY DETECTION PROBABILITY
% =========================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('   SIH 26058 - THRESHOLD-BASED WAVEFORM vs SNR TEST\n');
fprintf('============================================================\n');

fprintf('\nTarget Range     : %.2f m\n',targetRange);
fprintf('Trials / SNR     : %d\n',numTrials);
fprintf('Threshold Factor : %.1f sigma\n',thresholdMultiplier);

fprintf('\n');
fprintf('================ DETECTION PROBABILITY ====================\n');

fprintf('\n%-23s', 'Waveform');

for s = 1:numSNR

    fprintf('%9.1f',snrValues(s));

end

fprintf('\n');
fprintf('------------------------------------------------------------\n');

for w = 1:numWaveforms

    fprintf('%-23s',waveformNames{w});

    for s = 1:numSNR

        fprintf('%9.2f', ...
            detectionProbability(w,s));

    end

    fprintf('\n');

end

%% =========================================================
% 9. DISPLAY RANGE ERROR
% =========================================================

fprintf('\n');
fprintf('================ MEAN RANGE ERROR ==========================\n');

fprintf('\n%-23s', 'Waveform');

for s = 1:numSNR

    fprintf('%9.1f',snrValues(s));

end

fprintf('\n');
fprintf('------------------------------------------------------------\n');

for w = 1:numWaveforms

    fprintf('%-23s',waveformNames{w});

    for s = 1:numSNR

        if isnan(meanRangeError(w,s))

            fprintf('%9s','N/A');

        else

            fprintf('%9.4f', ...
                meanRangeError(w,s));

        end

    end

    fprintf('\n');

end

fprintf('\n============================================================\n');

%% =========================================================
% 10. DETECTION PROBABILITY GRAPH
% =========================================================

figure;

for w = 1:numWaveforms

    plot(snrValues, ...
        detectionProbability(w,:), ...
        'o-', ...
        'LineWidth',2);

    hold on;

end

xlabel('SNR (dB)');
ylabel('Detection Probability');

title('SIH 26058 - Detection Probability vs SNR');

legend(waveformNames);

ylim([0 1.1]);

grid on;

hold off;

%% =========================================================
% 11. RANGE ERROR GRAPH
% =========================================================

figure;

for w = 1:numWaveforms

    plot(snrValues, ...
        meanRangeError(w,:), ...
        'o-', ...
        'LineWidth',2);

    hold on;

end

xlabel('SNR (dB)');
ylabel('Mean Range Error (m)');

title('SIH 26058 - Range Error vs SNR');

legend(waveformNames);

grid on;

hold off;

%% =========================================================
% 12. PEAK vs THRESHOLD
% =========================================================

figure;

for w = 1:numWaveforms

    plot(snrValues, ...
        meanPeak(w,:), ...
        'o-', ...
        'LineWidth',2);

    hold on;

    plot(snrValues, ...
        meanThreshold(w,:), ...
        '--', ...
        'LineWidth',1.5);

end

xlabel('SNR (dB)');
ylabel('Matched Filter Magnitude');

title('SIH 26058 - Matched Filter Peak and Detection Threshold');

legend( ...
    'LFM Peak', ...
    'LFM Threshold', ...
    'Geometric Peak', ...
    'Geometric Threshold', ...
    'Phase-Coded Peak', ...
    'Phase-Coded Threshold');

grid on;

hold off;

%% =========================================================
% 13. FIND 90% DETECTION POINT
% =========================================================

fprintf('\n');
fprintf('================ 90%% DETECTION POINT ======================\n');

for w = 1:numWaveforms

    validIndex = ...
        find(detectionProbability(w,:) >= 0.90,1);

    if ~isempty(validIndex)

        fprintf('%-23s : %.1f dB\n', ...
            waveformNames{w}, ...
            snrValues(validIndex));

    else

        fprintf('%-23s : Not reached\n', ...
            waveformNames{w});

    end

end

fprintf('\n');
fprintf('============================================================\n');
fprintf('THRESHOLD-BASED SNR TEST COMPLETE\n');
fprintf('============================================================\n');