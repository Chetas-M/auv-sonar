%% =========================================================
% SIH 26058
% COMPLETE ADAPTIVE SONAR SYSTEM
%
% Environment
%      ↓
% Adaptive SNR Controller
%      ↓
% Waveform Generation
%      ↓
% Underwater Channel
%      ↓
% Echo + Noise
%      ↓
% Matched Filter
%      ↓
% Target Detection
% =========================================================

clear;
clc;
close all;

rng(500);

%% =========================================================
% 1. BASIC PARAMETERS
% =========================================================

Fs = 2e6;
Ts = 1/Fs;

soundSpeed = 1500;

targetRange = 5;

channelGain = 1;

%% =========================================================
% 2. ENVIRONMENT
% =========================================================

depth = 50;
turbidity = 100;
noiseLevel = -20;

%% =========================================================
% 3. RECEIVER SNR INPUT
% =========================================================

estimatedSNR = -22;

%% =========================================================
% 4. BASE TRANSMITTER PARAMETERS
% =========================================================

Fc = 300e3;
BW = 200e3;
Tp = 2e-3;
A = 1;

%% =========================================================
% 5. ADAPTIVE LIMITS
% =========================================================

Fc_min = 100e3;
Fc_max = 500e3;

BW_min = 50e3;
BW_max = 200e3;

Tp_min = 0.5e-3;
Tp_max = 5e-3;

A_min = 0.1;
A_max = 1.0;

%% =========================================================
% 6. THRESHOLDS
% =========================================================

depth_threshold = 100;

turbidity_threshold = 500;

noise_threshold = -10;

%% =========================================================
% 7. INITIAL ADAPTIVE PARAMETERS
% =========================================================

adaptiveFc = Fc;
adaptiveBW = BW;
adaptiveTp = Tp;
adaptiveAmplitude = A;
adaptiveWaveform = 1;

adaptationReason = ...
    'Normal operating condition';

%% =========================================================
% 8. ADAPTIVE CONTROLLER
% =========================================================

if estimatedSNR < -25

    adaptiveFc = 300e3;
    adaptiveBW = 200e3;
    adaptiveTp = 4e-3;
    adaptiveAmplitude = 1.0;
    adaptiveWaveform = 3;

    adaptationReason = ...
        'Very low SNR - phase-coded robust mode';

elseif estimatedSNR < -20

    adaptiveFc = 300e3;
    adaptiveBW = 200e3;
    adaptiveTp = 3e-3;
    adaptiveAmplitude = 1.0;
    adaptiveWaveform = 1;

    adaptationReason = ...
        'Low SNR - increased pulse duration';

elseif turbidity > turbidity_threshold

    adaptiveFc = 200e3;
    adaptiveBW = 100e3;
    adaptiveTp = 3e-3;
    adaptiveAmplitude = 0.8;
    adaptiveWaveform = 1;

    adaptationReason = ...
        'High turbidity';

elseif noiseLevel > noise_threshold

    adaptiveFc = 300e3;
    adaptiveBW = 200e3;
    adaptiveTp = 2e-3;
    adaptiveAmplitude = 1.0;
    adaptiveWaveform = 3;

    adaptationReason = ...
        'High environmental noise';

elseif depth > depth_threshold

    adaptiveFc = 250e3;
    adaptiveBW = 150e3;
    adaptiveTp = 3e-3;
    adaptiveAmplitude = 1.0;
    adaptiveWaveform = 2;

    adaptationReason = ...
        'Deep water';

end

%% =========================================================
% 9. APPLY LIMITS
% =========================================================

adaptiveFc = ...
    max(Fc_min,min(Fc_max,adaptiveFc));

adaptiveBW = ...
    max(BW_min,min(BW_max,adaptiveBW));

adaptiveTp = ...
    max(Tp_min,min(Tp_max,adaptiveTp));

adaptiveAmplitude = ...
    max(A_min,min(A_max,adaptiveAmplitude));

%% =========================================================
% 10. WAVEFORM NAME
% =========================================================

switch adaptiveWaveform

    case 1
        waveformName = 'LFM Chirp';

    case 2
        waveformName = 'Geometric Sweep';

    case 3
        waveformName = 'Phase-Coded Pulse';

end

%% =========================================================
% 11. GENERATE ADAPTIVE WAVEFORM
% =========================================================

N = round(adaptiveTp*Fs);

t = (0:N-1)*Ts;

switch adaptiveWaveform

    %% -----------------------------------------------------
    % LFM
    % -----------------------------------------------------

    case 1

        fStart = ...
            adaptiveFc-adaptiveBW/2;

        fStop = ...
            adaptiveFc+adaptiveBW/2;

        k = ...
            (fStop-fStart)/adaptiveTp;

        phase = ...
            2*pi*( ...
            fStart*t + ...
            0.5*k*t.^2);

        txSignal = ...
            adaptiveAmplitude*cos(phase);

    %% -----------------------------------------------------
    % GEOMETRIC SWEEP
    % -----------------------------------------------------

    case 2

        fStart = ...
            adaptiveFc-adaptiveBW/2;

        fStop = ...
            adaptiveFc+adaptiveBW/2;

        ratio = ...
            fStop/fStart;

        instFreq = ...
            fStart*ratio.^(t/adaptiveTp);

        phase = ...
            2*pi*cumtrapz(t,instFreq);

        txSignal = ...
            adaptiveAmplitude*cos(phase);

    %% -----------------------------------------------------
    % PHASE CODED
    % -----------------------------------------------------

    case 3

        phaseCode = ...
            [1 1 -1 1 -1 -1 1];

        txSignal = ...
            zeros(size(t));

        codeLength = ...
            length(phaseCode);

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
                adaptiveAmplitude * ...
                phaseCode(chip) .* ...
                cos(2*pi*adaptiveFc* ...
                t(startIndex:endIndex));

        end

end

%% =========================================================
% 12. WINDOW
% =========================================================

txSignal = ...
    txSignal .* hann(N).';

%% =========================================================
% 13. UNDERWATER PROPAGATION
% =========================================================

roundTripTime = ...
    2*targetRange/soundSpeed;

delaySamples = ...
    round(roundTripTime*Fs);

receiveLength = ...
    length(txSignal)+delaySamples;

receivedSignal = ...
    zeros(1,receiveLength);

%% =========================================================
% 14. TARGET ECHO
% =========================================================

echoGain = ...
    channelGain/(1+targetRange);

echoSignal = ...
    echoGain*txSignal;

startIndex = ...
    delaySamples+1;

endIndex = ...
    startIndex+length(echoSignal)-1;

receivedSignal(startIndex:endIndex) = ...
    echoSignal;

%% =========================================================
% 15. ADD NOISE
% =========================================================

signalPower = ...
    mean(echoSignal.^2);

noisePower = ...
    signalPower/(10^(estimatedSNR/10));

noiseStd = ...
    sqrt(noisePower);

noise = ...
    noiseStd*randn(size(receivedSignal));

receivedNoisy = ...
    receivedSignal+noise;

%% =========================================================
% 16. MATCHED FILTER
% =========================================================

matchedFilter = ...
    conj(fliplr(txSignal));

matchedOutput = ...
    conv(receivedNoisy,matchedFilter);

mfMagnitude = ...
    abs(matchedOutput);

%% =========================================================
% 17. DETECT PEAK
% =========================================================

[peakValue,peakIndex] = ...
    max(mfMagnitude);

detectedDelaySamples = ...
    peakIndex-length(txSignal);

detectedDelay = ...
    detectedDelaySamples/Fs;

detectedRange = ...
    detectedDelay*soundSpeed/2;

rangeError = ...
    abs(detectedRange-targetRange);

%% =========================================================
% 18. DISPLAY SYSTEM STATUS
% =========================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('          SIH 26058 - COMPLETE ADAPTIVE SONAR\n');
fprintf('============================================================\n');

fprintf('\nENVIRONMENT\n');
fprintf('------------------------------------------------------------\n');

fprintf('Depth          : %.2f m\n',depth);
fprintf('Turbidity      : %.2f\n',turbidity);
fprintf('Noise Level    : %.2f dB\n',noiseLevel);
fprintf('Estimated SNR  : %.2f dB\n',estimatedSNR);
fprintf('Target Range   : %.2f m\n',targetRange);

fprintf('\nADAPTIVE DECISION\n');
fprintf('------------------------------------------------------------\n');

fprintf('Reason         : %s\n',adaptationReason);

fprintf('\nTRANSMITTER\n');
fprintf('------------------------------------------------------------\n');

fprintf('Waveform       : %s\n',waveformName);
fprintf('Centre Freq.   : %.2f kHz\n',adaptiveFc/1e3);
fprintf('Bandwidth      : %.2f kHz\n',adaptiveBW/1e3);
fprintf('Pulse Duration : %.2f ms\n',adaptiveTp*1e3);
fprintf('Amplitude      : %.2f\n',adaptiveAmplitude);

fprintf('\nRECEIVER / DETECTION\n');
fprintf('------------------------------------------------------------\n');

fprintf('Propagation Delay : %.3f ms\n', ...
    roundTripTime*1e3);

fprintf('Detected Delay    : %.3f ms\n', ...
    detectedDelay*1e3);

fprintf('Detected Range    : %.3f m\n', ...
    detectedRange);

fprintf('Range Error       : %.4f m\n', ...
    rangeError);

fprintf('Matched Filter Peak : %.3f\n', ...
    peakValue);

if rangeError < 0.1

    fprintf('Detection Status  : SUCCESS\n');

else

    fprintf('Detection Status  : FAILED\n');

end

fprintf('============================================================\n');

%% =========================================================
% 19. TRANSMITTED SIGNAL
% =========================================================

figure;

plot(t*1e3,txSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title(['Adaptive Transmitted Waveform - ' waveformName]);

grid on;

%% =========================================================
% 20. RECEIVED SIGNAL
% =========================================================

figure;

timeReceived = ...
    (0:length(receivedNoisy)-1)*Ts;

plot(timeReceived*1e3,receivedNoisy);

xlabel('Time (ms)');
ylabel('Amplitude');

title('Received Signal with Noise');

grid on;

%% =========================================================
% 21. MATCHED FILTER OUTPUT
% =========================================================

figure;

mfTime = ...
    (0:length(matchedOutput)-1)*Ts;

plot(mfTime*1e3,mfMagnitude);

xlabel('Time (ms)');
ylabel('Matched Filter Magnitude');

title('Matched Filter Output');

grid on;

hold on;

plot( ...
    detectedDelay*1e3+adaptiveTp*1e3, ...
    peakValue, ...
    'o', ...
    'LineWidth',2);

legend('Matched Filter','Detected Peak');

hold off;

%% =========================================================
% 22. FINAL STATUS
% =========================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('COMPLETE MATLAB ADAPTIVE SONAR TEST COMPLETE\n');
fprintf('============================================================\n');