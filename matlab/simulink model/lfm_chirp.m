%% =========================================================
% SIH 26058
% ADAPTIVE SOFTWARE-DEFINED SONAR TRANSMITTER
%
% LFM CHIRP GENERATOR + ANALYSIS
% =========================================================

clear;
clc;
close all;


%% =========================================================
% 1. LOAD PROJECT PARAMETERS
% =========================================================

parameters;


%% =========================================================
% 2. LFM CHIRP PARAMETERS
% =========================================================

f0 = LFM_fstart;        % Start frequency
f1 = LFM_fstop;         % Stop frequency
T  = LFM_T;             % Chirp duration

K = (f1 - f0) / T;      % Chirp rate (Hz/s)


%% =========================================================
% 3. TIME VECTOR
% =========================================================

t = 0:Ts:T-Ts;

N = length(t);


%% =========================================================
% 4. GENERATE LFM CHIRP
% =========================================================

phase = 2*pi*(f0*t + 0.5*K*t.^2);

chirpSignal = A*cos(phase);


%% =========================================================
% 5. INSTANTANEOUS FREQUENCY
% =========================================================

instantaneousFrequency = f0 + K*t;


%% =========================================================
% 6. WINDOWING
% =========================================================

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
        win = ones(1,N).';
        windowName = 'None';

end

windowedSignal = chirpSignal .* win;


%% =========================================================
% 7. DISPLAY PARAMETERS
% =========================================================

fprintf('\n');
fprintf('====================================================\n');
fprintf('          SIH 26058 - LFM SONAR CHIRP\n');
fprintf('====================================================\n');

fprintf('Sampling Frequency : %.2f MHz\n', Fs/1e6);
fprintf('Start Frequency    : %.2f kHz\n', f0/1e3);
fprintf('Stop Frequency     : %.2f kHz\n', f1/1e3);
fprintf('Bandwidth           : %.2f kHz\n', (f1-f0)/1e3);
fprintf('Pulse Duration      : %.2f ms\n', T*1e3);
fprintf('Chirp Rate          : %.3e Hz/s\n', K);
fprintf('Number of Samples   : %d\n', N);
fprintf('Window              : %s\n', windowName);

fprintf('====================================================\n');


%% =========================================================
% 8. GRAPH 1 - TIME DOMAIN LFM CHIRP
% =========================================================

figure;

plot(t*1e3, chirpSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title('SIH 26058 - LFM Sonar Chirp');

grid on;

xlim([0 T*1e3]);


%% =========================================================
% 9. GRAPH 2 - INSTANTANEOUS FREQUENCY
% =========================================================

figure;

plot(t*1e3, instantaneousFrequency/1e3);

xlabel('Time (ms)');
ylabel('Instantaneous Frequency (kHz)');

title('SIH 26058 - LFM Instantaneous Frequency');

grid on;

xlim([0 T*1e3]);

ylim([0 500]);


%% =========================================================
% 10. GRAPH 3 - WINDOWED LFM CHIRP
% =========================================================

figure;

plot(t*1e3, windowedSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title(['SIH 26058 - Windowed LFM Chirp (' windowName ')']);

grid on;

xlim([0 T*1e3]);


%% =========================================================
% 11. FFT ANALYSIS
% =========================================================

Y = fft(windowedSignal);

P2 = abs(Y/N);

P1 = P2(1:N/2+1);

P1(2:end-1) = 2*P1(2:end-1);

f = Fs*(0:N/2)/N;


%% =========================================================
% 12. GRAPH 4 - FFT SPECTRUM
% =========================================================

figure;

plot(f/1e3, P1);

xlabel('Frequency (kHz)');
ylabel('Magnitude');

title('SIH 26058 - FFT Spectrum of LFM Chirp');

grid on;

xlim([0 600]);


%% =========================================================
% 13. GRAPH 5 - SPECTROGRAM
% =========================================================

figure;

spectrogram(windowedSignal, ...
    256, ...
    200, ...
    1024, ...
    Fs, ...
    'yaxis');

title('SIH 26058 - LFM Sonar Chirp Spectrogram');


%% =========================================================
% 14. BASIC PERFORMANCE CALCULATIONS
% =========================================================

bandwidth = f1 - f0;

rangeResolution = soundSpeed/(2*bandwidth);

fprintf('\n');
fprintf('PERFORMANCE INFORMATION\n');
fprintf('----------------------------------------------------\n');

fprintf('Bandwidth          : %.2f kHz\n', bandwidth/1e3);

fprintf('Theoretical Range Resolution : %.4f m\n', ...
    rangeResolution);

fprintf('Theoretical Range Resolution : %.2f mm\n', ...
    rangeResolution*1000);

fprintf('----------------------------------------------------\n');


%% =========================================================
% 15. CHECK FREQUENCY LIMITS
% =========================================================

if f0 >= Fmin && f1 <= Fmax

    fprintf('Frequency Range    : VALID\n');

else

    fprintf('Frequency Range    : OUTSIDE LIMITS\n');

end


%% =========================================================
% 16. CHECK NYQUIST CONDITION
% =========================================================

if Fs >= 2*f1

    fprintf('Sampling Condition : VALID\n');

else

    fprintf('Sampling Condition : INVALID\n');

end


%% =========================================================
% END
% =========================================================

fprintf('====================================================\n');
fprintf('LFM CHIRP GENERATION COMPLETE\n');
fprintf('====================================================\n');