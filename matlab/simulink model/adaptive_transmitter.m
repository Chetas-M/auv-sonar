%% =========================================================
% SIH 26058
% INTEGRATED SOFTWARE-DEFINED SONAR TRANSMITTER
%
% Waveform Selector:
% 1 = LFM
% 2 = Geometric Sweep
% 3 = Phase-Coded Pulse
% =========================================================

clear;
clc;
close all;

%% =========================================================
% 1. LOAD PARAMETERS
% =========================================================
parameters;

%% =========================================================
% 2. SELECT WAVEFORM
% =========================================================
fprintf('\n');
fprintf('============================================\n');
fprintf('      SIH 26058 INTEGRATED TRANSMITTER\n');
fprintf('============================================\n');

fprintf('Selected Waveform Type : %d\n', waveformType);

%% =========================================================
% 3. GENERATE SELECTED WAVEFORM
% =========================================================

switch waveformType

    %% -----------------------------------------------------
    % WAVEFORM 1 - LFM CHIRP
    % ------------------------------------------------------
    case 1

        waveformName = 'LFM Chirp';

        f0 = LFM_fstart;
        f1 = LFM_fstop;
        T  = LFM_T;

        t = 0:Ts:T-Ts;

        K = (f1-f0)/T;

        phase = 2*pi*(f0*t + 0.5*K*t.^2);

        txSignal = A*cos(phase);

        instantaneousFrequency = f0 + K*t;

    %% -----------------------------------------------------
    % WAVEFORM 2 - GEOMETRIC SWEEP
    % ------------------------------------------------------
    case 2

        waveformName = 'Geometric Sweep';

        f0 = Geo_fstart;
        f1 = Geo_fstop;
        T  = Geo_T;

        t = 0:Ts:T-Ts;

        instantaneousFrequency = ...
            f0*(f1/f0).^(t/T);

        phase = 2*pi*cumtrapz(t,instantaneousFrequency);

        txSignal = A*cos(phase);

    %% -----------------------------------------------------
    % WAVEFORM 3 - PHASE-CODED PULSE
    % ------------------------------------------------------
    case 3

        waveformName = 'Phase-Coded Pulse';

        code = phaseCode;

        chipTime = chipDuration;

        numChips = length(code);

        samplesPerChip = round(chipTime*Fs);

        T = numChips*chipTime;

        t = 0:Ts:T-Ts;

        N = length(t);

        txSignal = zeros(1,N);

        for k = 1:numChips

            startIndex = (k-1)*samplesPerChip + 1;

            endIndex = min(k*samplesPerChip,N);

            chipTimeVector = t(startIndex:endIndex);

            txSignal(startIndex:endIndex) = ...
                A*code(k).*cos(2*pi*Fc*chipTimeVector);

        end

        instantaneousFrequency = Fc*ones(size(t));

    otherwise

        error('Invalid waveformType. Use 1, 2, or 3.');

end

%% =========================================================
% 4. WINDOWING
% =========================================================

N = length(txSignal);

switch windowType

    case 1
        win = hamming(N).';
        windowName = 'Hamming';

    case 2
        win = hann(N).';
        windowName = 'Hann';

    case 3
        win = blackman(N).';
        windowName = 'Blackman';

    otherwise
        win = ones(1,N);
        windowName = 'None';

end

windowedSignal = txSignal .* win;

%% =========================================================
% 5. DISPLAY INFORMATION
% =========================================================

fprintf('Waveform Name          : %s\n', waveformName);
fprintf('Sampling Frequency     : %.2f MHz\n', Fs/1e6);
fprintf('Window                 : %s\n', windowName);
fprintf('Signal Duration        : %.3f ms\n', ...
    length(txSignal)/Fs*1e3);
fprintf('Number of Samples      : %d\n', ...
    length(txSignal));

fprintf('============================================\n');

%% =========================================================
% 6. TIME-DOMAIN GRAPH
% =========================================================

figure;

plot(t*1e3,txSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title(['SIH 26058 - Selected Waveform: ' waveformName]);

grid on;

%% =========================================================
% 7. INSTANTANEOUS FREQUENCY
% =========================================================

figure;

plot(t*1e3,instantaneousFrequency/1e3);

xlabel('Time (ms)');
ylabel('Frequency (kHz)');

title(['SIH 26058 - Instantaneous Frequency: ' waveformName]);

grid on;

%% =========================================================
% 8. WINDOWED WAVEFORM
% =========================================================

figure;

plot(t*1e3,windowedSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title(['SIH 26058 - Windowed ' waveformName]);

grid on;

%% =========================================================
% 9. FFT
% =========================================================

Y = fft(windowedSignal);

P2 = abs(Y/N);

P1 = P2(1:floor(N/2)+1);

if length(P1) > 2
    P1(2:end-1) = 2*P1(2:end-1);
end

f = Fs*(0:floor(N/2))/N;

figure;

plot(f/1e3,P1);

xlabel('Frequency (kHz)');
ylabel('Magnitude');

title(['SIH 26058 - FFT: ' waveformName]);

grid on;

xlim([0 600]);

%% =========================================================
% 10. SPECTROGRAM
% =========================================================

figure;

spectrogram(windowedSignal,256,200,1024,Fs,'yaxis');

title(['SIH 26058 - Spectrogram: ' waveformName]);

%% =========================================================
% 11. BASIC VALIDATION
% =========================================================

fprintf('\nVALIDATION\n');
fprintf('--------------------------------------------\n');

if max(abs(txSignal)) <= A + 1e-6
    fprintf('Amplitude Limit       : VALID\n');
else
    fprintf('Amplitude Limit       : INVALID\n');
end

if Fs >= 2*Fmax
    fprintf('Sampling Condition    : VALID\n');
else
    fprintf('Sampling Condition    : INVALID\n');
end

fprintf('--------------------------------------------\n');

fprintf('TRANSMITTER GENERATION COMPLETE\n');
fprintf('============================================\n');