%% =========================================================
% SIH 26058
% UNDERWATER CHANNEL AND TARGET ECHO MODEL
%
% This model takes the adaptive transmitted waveform and
% simulates:
%   1. Propagation delay
%   2. Target echo
%   3. Channel attenuation
%   4. Additive noise
%
% Current test:
%   Target range = 10 m
%   Sound speed = 1500 m/s
% =========================================================

clearvars -except ...
    Fs txSignal adaptiveTp ...
    range soundSpeed channelGain noiseLevel

clc;
close all;

%% =========================================================
% 1. CHECK REQUIRED VARIABLES
% =========================================================

if ~exist('txSignal','var')
    error(['Run adaptive_waveform_generator first. ' ...
           'The transmitted waveform is not available.']);
end

%% =========================================================
% 2. CHANNEL PARAMETERS
% =========================================================

targetRange = range;
c = soundSpeed;

%% =========================================================
% 3. TWO-WAY PROPAGATION DELAY
% =========================================================

roundTripTime = (2 * targetRange) / c;

delaySamples = round(roundTripTime * Fs);

actualDelay = delaySamples / Fs;

%% =========================================================
% 4. CREATE RECEIVED SIGNAL BUFFER
% =========================================================

% Add enough time to contain the delayed echo

receiveLength = length(txSignal) + delaySamples;

receivedSignal = zeros(1,receiveLength);

%% =========================================================
% 5. CHANNEL ATTENUATION
% =========================================================

% Simple simulation gain
echoAmplitude = channelGain / (1 + targetRange);

%% =========================================================
% 6. CREATE TARGET ECHO
% =========================================================

echoSignal = echoAmplitude * txSignal;

startIndex = delaySamples + 1;

endIndex = startIndex + length(echoSignal) - 1;

receivedSignal(startIndex:endIndex) = echoSignal;

%% =========================================================
% 7. ADD NOISE
% =========================================================

% Convert noise setting into a simple simulation noise level

noiseAmplitude = 10^(noiseLevel/20);

noise = noiseAmplitude * randn(size(receivedSignal));

noisyReceivedSignal = receivedSignal + noise;

%% =========================================================
% 8. TIME AXIS
% =========================================================

tTx = (0:length(txSignal)-1) / Fs;

tRx = (0:length(receivedSignal)-1) / Fs;

%% =========================================================
% 9. DISPLAY CHANNEL INFORMATION
% =========================================================

fprintf('\n');
fprintf('====================================================\n');
fprintf('       SIH 26058 - UNDERWATER CHANNEL MODEL\n');
fprintf('====================================================\n');

fprintf('\nCHANNEL PARAMETERS\n');
fprintf('----------------------------------------------------\n');

fprintf('Target Range       : %.2f m\n',targetRange);
fprintf('Sound Speed        : %.2f m/s\n',c);
fprintf('Channel Gain       : %.3f\n',channelGain);
fprintf('Noise Level        : %.2f dB\n',noiseLevel);

fprintf('\nPROPAGATION\n');
fprintf('----------------------------------------------------\n');

fprintf('Round-trip Time    : %.3f ms\n',roundTripTime*1e3);
fprintf('Delay Samples      : %d\n',delaySamples);
fprintf('Actual Delay       : %.3f ms\n',actualDelay*1e3);

fprintf('\nECHO\n');
fprintf('----------------------------------------------------\n');

fprintf('Echo Gain          : %.5f\n',echoAmplitude);

fprintf('====================================================\n');

%% =========================================================
% 10. TRANSMITTED SIGNAL
% =========================================================

figure;

plot(tTx*1e3,txSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title('Transmitted Sonar Signal');

grid on;

%% =========================================================
% 11. RECEIVED ECHO
% =========================================================

figure;

plot(tRx*1e3,receivedSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title('Received Target Echo');

grid on;

%% =========================================================
% 12. NOISY RECEIVED SIGNAL
% =========================================================

figure;

plot(tRx*1e3,noisyReceivedSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title('Received Signal with Noise');

grid on;

%% =========================================================
% 13. ZOOM AROUND EXPECTED ECHO
% =========================================================

figure;

plot(tRx*1e3,receivedSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title('Target Echo - Propagation Delay');

xlim([max(0,roundTripTime*1e3-2) ...
      roundTripTime*1e3+adaptiveTp*1e3+2]);

grid on;

%% =========================================================
% 14. VALIDATION
% =========================================================

fprintf('\nVALIDATION\n');
fprintf('----------------------------------------------------\n');

fprintf('Expected delay : %.3f ms\n',roundTripTime*1e3);
fprintf('Actual delay   : %.3f ms\n',actualDelay*1e3);

delayError = abs(actualDelay-roundTripTime);

fprintf('Delay error     : %.6f ms\n',delayError*1e3);

fprintf('\nUNDERWATER CHANNEL SIMULATION COMPLETE\n');
fprintf('====================================================\n');