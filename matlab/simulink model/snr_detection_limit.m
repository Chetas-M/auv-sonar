%% =========================================================
% SIH 26058
% SNR DETECTION LIMIT ANALYSIS
%
% Purpose:
% Find the SNR region where target detection starts to fail.
%
% Waveforms:
%   1. LFM Chirp
%   2. Geometric Sweep
%   3. Phase-Coded Pulse
%
% Target Range : 5 m
% SNR Range    : -40 to 0 dB
% =========================================================

clear;
clc;
close all;

rng(200);

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
% 2. SNR VALUES
% =========================================================

snrValues = [-40 -35 -30 -25 -20 -15 -10 -5 0];

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
% 6. RESULT ARRAYS
% =========================================================

detectionProbability = zeros(numWaveforms,numSNR);

meanRangeError = nan(numWaveforms,numSNR);

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

        case 1

            % LFM CHIRP

            fStart = Fc-BW/2;
            fStop = Fc+BW/2;

            k = (fStop-fStart)/Tp;

            phase = 2*pi*( ...
                fStart*t + ...
                0.5*k*t.^2);

            txSignal = A*cos(phase);

        case 2

            % GEOMETRIC SWEEP

            fStart = Fc-BW/2;
            fStop = Fc+BW/2;

            ratio = fStop/fStart;

            instFreq = ...
                fStart*ratio.^(t/Tp);

            phase = ...
                2*pi*cumtrapz(t,instFreq);

            txSignal = A*cos(phase);

        case 3

            % PHASE-CODED PULSE

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
    % HANN WINDOW
    % -----------------------------------------------------

    txSignal = ...
        txSignal .* hann(N).';

    %% -----------------------------------------------------
    % TARGET DELAY
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

        for trial = 1:numTrials

            %% -------------------------------------------------
            % NOISE POWER
            % -------------------------------------------------

            noisePower = ...
                signalPower/(10^(targetSNR/10));

            noiseStd = sqrt(noisePower);

            %% -------------------------------------------------
            % GENERATE NOISE
            % -------------------------------------------------

            noise = ...
                noiseStd*randn(size(receivedSignal));

            noisyReceivedSignal = ...
                receivedSignal+noise;

            %% -------------------------------------------------
            % MATCHED FILTER
            % -------------------------------------------------

            matchedOutput = ...
                conv(noisyReceivedSignal,matchedFilter);

            magnitudeOutput = ...
                abs(matchedOutput);

            %% -------------------------------------------------
            % ESTIMATE NOISE FLOOR
            % -------------------------------------------------

            expectedPeak = ...
                delaySamples+length(txSignal);

            exclusionWidth = ...
                round(0.01*length(matchedOutput));

            noiseRegion = true(size(magnitudeOutput));

            lowerIndex = ...
                max(1,expectedPeak-exclusionWidth);

            upperIndex = ...
                min(length(magnitudeOutput), ...
                    expectedPeak+exclusionWidth);

            noiseRegion(lowerIndex:upperIndex) = false;

            background = ...
                magnitudeOutput(noiseRegion);

            noiseMean = mean(background);

            noiseStdMF = std(background);

            threshold = ...
                noiseMean + ...
                thresholdMultiplier*noiseStdMF;

            %% -------------------------------------------------
            % PEAK
            % -------------------------------------------------

            [peakValue,peakIndex] = ...
                max(magnitudeOutput);

            %% -------------------------------------------------
            % DETECTION
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
                % VALID TARGET RANGE
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
        % STORE DETECTION PROBABILITY
        % -----------------------------------------------------

        detectionProbability(w,s) = ...
            detectedCount/numTrials;

        %% -----------------------------------------------------
        % STORE RANGE ERROR
        % -----------------------------------------------------

        if ~isempty(successfulErrors)

            meanRangeError(w,s) = ...
                mean(successfulErrors);

        end

    end

end

%% =========================================================
% 8. DISPLAY RESULTS
% =========================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('       SIH 26058 - SNR DETECTION LIMIT TEST\n');
fprintf('============================================================\n');

fprintf('\nTarget Range     : %.2f m\n',targetRange);
fprintf('Trials / SNR     : %d\n',numTrials);
fprintf('Threshold Factor : %.1f sigma\n',thresholdMultiplier);

%% =========================================================
% 9. DETECTION PROBABILITY TABLE
% =========================================================

fprintf('\n');
fprintf('================ DETECTION PROBABILITY ====================\n');

fprintf('\n%-23s','Waveform');

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
% 10. RANGE ERROR TABLE
% =========================================================

fprintf('\n');
fprintf('================ MEAN RANGE ERROR ==========================\n');

fprintf('\n%-23s','Waveform');

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

%% =========================================================
% 11. FIND 90% DETECTION LIMIT
% =========================================================

fprintf('\n');
fprintf('================ 90%% DETECTION LIMIT ======================\n');

for w = 1:numWaveforms

    successfulIndex = ...
        find(detectionProbability(w,:) >= 0.90,1,'first');

    if ~isempty(successfulIndex)

        fprintf('%-23s : %.1f dB\n', ...
            waveformNames{w}, ...
            snrValues(successfulIndex));

    else

        fprintf('%-23s : Not reached\n', ...
            waveformNames{w});

    end

end

%% =========================================================
% 12. FIND FIRST CLEAR FAILURE
% =========================================================

fprintf('\n');
fprintf('================ DETECTION DEGRADATION ====================\n');

for w = 1:numWaveforms

    failureIndex = ...
        find(detectionProbability(w,:) < 0.90,1,'last');

    if ~isempty(failureIndex)

        fprintf('%-23s : Detection below 90%% at %.1f dB\n', ...
            waveformNames{w}, ...
            snrValues(failureIndex));

    else

        fprintf('%-23s : No degradation below 90%% in range\n', ...
            waveformNames{w});

    end

end

%% =========================================================
% 13. DETECTION PROBABILITY GRAPH
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
% 14. RANGE ERROR GRAPH
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
% 15. COMPLETE
% =========================================================

fprintf('\n');
fprintf('SNR DETECTION LIMIT ANALYSIS COMPLETE\n');
fprintf('============================================================\n');