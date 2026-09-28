%% =========================================================
% SIH 26058
% MATCHED FILTER AND TARGET RANGE DETECTOR
%
% Uses the transmitted waveform as the reference and
% detects the target echo from the noisy received signal.
% =========================================================

clearvars -except ...
    Fs txSignal noisyReceivedSignal ...
    range soundSpeed adaptiveWaveform adaptiveTp

clc;
close all;

%% =========================================================
% 1. CHECK REQUIRED SIGNALS
% =========================================================

if ~exist('txSignal','var')
    error('Transmitted signal not found. Run adaptive_waveform_generator first.');
end

if ~exist('noisyReceivedSignal','var')
    error('Received signal not found. Run underwater_channel first.');
end

%% =========================================================
% 2. MATCHED FILTER
% =========================================================

% Reference waveform
referenceSignal = txSignal;

% Time-reversed conjugate
matchedFilter = conj(fliplr(referenceSignal));

% Perform matched filtering
matchedOutput = conv(noisyReceivedSignal, matchedFilter);

%% =========================================================
% 3. TIME AXIS
% =========================================================

tMatched = (0:length(matchedOutput)-1)/Fs;

%% =========================================================
% 4. FIND TARGET PEAK
% =========================================================

[peakValue, peakIndex] = max(abs(matchedOutput));

% Convert convolution index to propagation delay
delaySamplesDetected = peakIndex - length(referenceSignal);

detectedDelay = delaySamplesDetected/Fs;

%% =========================================================
% 5. CALCULATE TARGET RANGE
% =========================================================

detectedRange = (detectedDelay * soundSpeed)/2;

%% =========================================================
% 6. RANGE ERROR
% =========================================================

rangeError = abs(detectedRange - range);

%% =========================================================
% 7. NORMALIZED MATCHED FILTER OUTPUT
% =========================================================

matchedMagnitude = abs(matchedOutput);

matchedMagnitude = matchedMagnitude / max(matchedMagnitude);

matchedMagnitude_dB = ...
    20*log10(matchedMagnitude + eps);

%% =========================================================
% 8. DISPLAY RESULTS
% =========================================================

fprintf('\n');
fprintf('====================================================\n');
fprintf('       SIH 26058 - MATCHED FILTER DETECTOR\n');
fprintf('====================================================\n');

fprintf('\nINPUT\n');
fprintf('----------------------------------------------------\n');

fprintf('Sampling Rate       : %.2f MHz\n',Fs/1e6);
fprintf('Target Range        : %.2f m\n',range);

fprintf('\nDETECTED TARGET\n');
fprintf('----------------------------------------------------\n');

fprintf('Peak Sample         : %d\n',peakIndex);
fprintf('Detected Delay      : %.3f ms\n',detectedDelay*1e3);
fprintf('Detected Range      : %.3f m\n',detectedRange);
fprintf('Range Error         : %.3f m\n',rangeError);

fprintf('\nMATCHED FILTER\n');
fprintf('----------------------------------------------------\n');

fprintf('Peak Magnitude      : %.3f\n',peakValue);
fprintf('Reference Samples   : %d\n',length(referenceSignal));

fprintf('====================================================\n');

%% =========================================================
% 9. PLOT MATCHED FILTER OUTPUT
% =========================================================

figure;

plot(tMatched*1e3,matchedMagnitude_dB);

xlabel('Time (ms)');
ylabel('Matched Filter Magnitude (dB)');

title('SIH 26058 - Matched Filter Output');

grid on;

%% =========================================================
% 10. RANGE AXIS
% =========================================================

rangeAxis = (tMatched * soundSpeed)/2;

figure;

plot(rangeAxis,matchedMagnitude_dB);

xlabel('Range (m)');
ylabel('Matched Filter Magnitude (dB)');

title('SIH 26058 - Target Detection');

grid on;

%% =========================================================
% 11. MARK DETECTED TARGET
% =========================================================

figure;

plot(rangeAxis,matchedMagnitude_dB);

hold on;

plot(detectedRange, ...
     20*log10(1), ...
     'o', ...
     'MarkerSize',8, ...
     'LineWidth',2);

xlabel('Range (m)');
ylabel('Matched Filter Magnitude (dB)');

title('SIH 26058 - Detected Target Range');

legend('Matched Filter Output','Detected Target');

grid on;

hold off;

%% =========================================================
% 12. VALIDATION
% =========================================================

fprintf('\nVALIDATION\n');
fprintf('----------------------------------------------------\n');

fprintf('Actual Target Range    : %.3f m\n',range);
fprintf('Detected Target Range  : %.3f m\n',detectedRange);
fprintf('Range Error            : %.3f m\n',rangeError);

if rangeError < 0.1
    fprintf('STATUS                 : TARGET DETECTED CORRECTLY\n');
else
    fprintf('STATUS                 : CHECK DETECTION\n');
end

fprintf('\nMATCHED FILTER TEST COMPLETE\n');
fprintf('====================================================\n');