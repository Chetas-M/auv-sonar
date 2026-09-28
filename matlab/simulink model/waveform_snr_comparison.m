%% =========================================================
% SIH 26058
% WAVEFORM vs SNR PERFORMANCE COMPARISON
%
% Compares:
%   LFM Chirp
%   Geometric Sweep
%   Phase-Coded Pulse
%
% SNR values:
%   -10, -5, 0, 5, 10, 15, 20 dB
%
% Target:
%   5 m
%
% Metric:
%   Detection Probability
%   Mean Range Error
%   Matched Filter Peak
% =========================================================

clear;
clc;
close all;

rng(50);

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

snrValues = [-10 -5 0 5 10 15 20];

numSNR = length(snrValues);

%% =========================================================
% 3. MONTE CARLO TRIALS
% =========================================================

numTrials = 30;

%% =========================================================
% 4. WAVEFORM NAMES
% =========================================================

waveformNames = {
    'LFM Chirp'
    'Geometric Sweep'
    'Phase-Coded Pulse'
    };

numWaveforms = 3;

%% =========================================================
% 5. RESULT STORAGE
% =========================================================

detectionProbability = zeros(numWaveforms,numSNR);

meanRangeError = zeros(numWaveforms,numSNR);

meanMatchedPeak = zeros(numWaveforms,numSNR);

%% =========================================================
% 6. WAVEFORM LOOP
% =========================================================

for w = 1:numWaveforms

    %% -----------------------------------------------------
    % GENERATE TRANSMITTED WAVEFORM
    % -----------------------------------------------------

    N = round(Tp*Fs);

    t = (0:N-1)*Ts;

    switch w

        %% LFM CHIRP
        case 1

            fStart = Fc-BW/2;
            fStop = Fc+BW/2;

            k = (fStop-fStart)/Tp;

            phase = 2*pi*( ...
                fStart*t + ...
                0.5*k*t.^2);

            txSignal = A*cos(phase);

        %% GEOMETRIC SWEEP
        case 2

            fStart = Fc-BW/2;
            fStop = Fc+BW/2;

            ratio = fStop/fStart;

            instFreq = ...
                fStart*ratio.^(t/Tp);

            phase = ...
                2*pi*cumtrapz(t,instFreq);

            txSignal = A*cos(phase);

        %% PHASE CODED
        case 3

            txSignal = zeros(size(t));

            codeLength = length(phaseCode);

            samplesPerChip = floor(N/codeLength);

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

    txSignal = txSignal .* hann(N).';

    %% -----------------------------------------------------
    % TARGET ECHO
    % -----------------------------------------------------

    roundTripTime = ...
        2*targetRange/soundSpeed;

    delaySamples = ...
        round(roundTripTime*Fs);

    receiveLength = ...
        length(txSignal)+delaySamples;

    receivedSignal = ...
        zeros(1,receiveLength);

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

    signalPower = mean(echoSignal.^2);

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

        rangeErrors = zeros(numTrials,1);

        peakValues = zeros(numTrials,1);

        for trial = 1:numTrials

            %% -------------------------------------------------
            % NOISE POWER
            % -------------------------------------------------

            noisePower = ...
                signalPower / ...
                (10^(targetSNR/10));

            noiseStd = sqrt(noisePower);

            %% -------------------------------------------------
            % NOISE
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

            %% -------------------------------------------------
            % FIND PEAK
            % -------------------------------------------------

            [peakValue,peakIndex] = ...
                max(abs(matchedOutput));

            peakValues(trial) = peakValue;

            %% -------------------------------------------------
            % DELAY
            % -------------------------------------------------

            detectedDelaySamples = ...
                peakIndex-length(txSignal);

            detectedDelay = ...
                detectedDelaySamples/Fs;

            %% -------------------------------------------------
            % RANGE
            % -------------------------------------------------

            currentRange = ...
                detectedDelay*soundSpeed/2;

            currentError = ...
                abs(currentRange-targetRange);

            rangeErrors(trial) = currentError;

            %% -------------------------------------------------
            % DETECTION
            % -------------------------------------------------

            if currentError < 0.1

                detectedCount = ...
                    detectedCount+1;

            end

        end

        %% -----------------------------------------------------
        % STORE
        % -----------------------------------------------------

        detectionProbability(w,s) = ...
            detectedCount/numTrials;

        meanRangeError(w,s) = ...
            mean(rangeErrors);

        meanMatchedPeak(w,s) = ...
            mean(peakValues);

    end

end

%% =========================================================
% 7. DISPLAY RESULTS
% =========================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('       SIH 26058 - WAVEFORM vs SNR COMPARISON\n');
fprintf('============================================================\n');

fprintf('\nTarget Range : %.2f m\n',targetRange);
fprintf('Trials/SNR   : %d\n',numTrials);

%% =========================================================
% 8. DETECTION PROBABILITY TABLE
% =========================================================

fprintf('\n');
fprintf('================ DETECTION PROBABILITY ====================\n');

fprintf('\n%-23s', 'Waveform');

for s = 1:numSNR
    fprintf('%10.1f',snrValues(s));
end

fprintf('\n');
fprintf('------------------------------------------------------------\n');

for w = 1:numWaveforms

    fprintf('%-23s',waveformNames{w});

    for s = 1:numSNR

        fprintf('%10.2f',detectionProbability(w,s));

    end

    fprintf('\n');

end

%% =========================================================
% 9. RANGE ERROR TABLE
% =========================================================

fprintf('\n');
fprintf('================ MEAN RANGE ERROR ==========================\n');

fprintf('\n%-23s', 'Waveform');

for s = 1:numSNR
    fprintf('%10.1f',snrValues(s));
end

fprintf('\n');
fprintf('------------------------------------------------------------\n');

for w = 1:numWaveforms

    fprintf('%-23s',waveformNames{w});

    for s = 1:numSNR

        fprintf('%10.4f',meanRangeError(w,s));

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
% 12. MATCHED FILTER PEAK GRAPH
% =========================================================

figure;

for w = 1:numWaveforms

    plot(snrValues, ...
         meanMatchedPeak(w,:), ...
         'o-', ...
         'LineWidth',2);

    hold on;

end

xlabel('SNR (dB)');
ylabel('Mean Matched Filter Peak');

title('SIH 26058 - Matched Filter Peak vs SNR');

legend(waveformNames);

grid on;

hold off;

%% =========================================================
% 13. BEST WAVEFORM AT EACH SNR
% =========================================================

fprintf('\n');
fprintf('================ BEST WAVEFORM =============================\n');

for s = 1:numSNR

    [bestProbability,bestIndex] = ...
        max(detectionProbability(:,s));

    fprintf('SNR = %5.1f dB : %-23s Detection = %.2f\n', ...
        snrValues(s), ...
        waveformNames{bestIndex}, ...
        bestProbability);

end

fprintf('\n============================================================\n');
fprintf('WAVEFORM vs SNR ANALYSIS COMPLETE\n');
fprintf('============================================================\n');