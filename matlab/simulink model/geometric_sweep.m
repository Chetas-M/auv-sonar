%% =========================================================
% SIH 26058
% ADAPTIVE SOFTWARE-DEFINED SONAR TRANSMITTER
%
% GEOMETRIC FREQUENCY SWEEP GENERATOR
% =========================================================

clear;
clc;
close all;

%% =========================================================
% 1. LOAD PROJECT PARAMETERS
% =========================================================

parameters;

%% =========================================================
% 2. GEOMETRIC SWEEP PARAMETERS
% =========================================================

f0 = Geo_fstart;
f1 = Geo_fstop;
T  = Geo_T;

%% =========================================================
% 3. TIME VECTOR
% =========================================================

t = 0:Ts:T-Ts;
N = length(t);

%% =========================================================
% 4. GEOMETRIC FREQUENCY SWEEP
% =========================================================

% Frequency changes exponentially with time

instantaneousFrequency = f0 * (f1/f0).^(t/T);

%% =========================================================
% 5. GENERATE PHASE
% =========================================================

phase = 2*pi * cumtrapz(t, instantaneousFrequency);

%% =========================================================
% 6. GENERATE SIGNAL
% =========================================================

geometricSignal = A*cos(phase);

%% =========================================================
% 7. WINDOWING
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

        win = ones(1,N);
        windowName = 'None';

end

windowedSignal = geometricSignal .* win;

%% =========================================================
% 8. DISPLAY PARAMETERS
% =========================================================

fprintf('\n');
fprintf('====================================================\n');
fprintf('       SIH 26058 - GEOMETRIC FREQUENCY SWEEP\n');
fprintf('====================================================\n');

fprintf('Sampling Frequency : %.2f MHz\n', Fs/1e6);
fprintf('Start Frequency    : %.2f kHz\n', f0/1e3);
fprintf('Stop Frequency     : %.2f kHz\n', f1/1e3);
fprintf('Sweep Duration     : %.2f ms\n', T*1e3);
fprintf('Number of Samples  : %d\n', N);
fprintf('Window             : %s\n', windowName);

fprintf('====================================================\n');

%% =========================================================
% 9. GRAPH 1 - TIME DOMAIN
% =========================================================

figure;

plot(t*1e3, geometricSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title('SIH 26058 - Geometric Frequency Sweep');

grid on;

xlim([0 T*1e3]);

%% =========================================================
% 10. GRAPH 2 - INSTANTANEOUS FREQUENCY
% =========================================================

figure;

plot(t*1e3, instantaneousFrequency/1e3);

xlabel('Time (ms)');
ylabel('Instantaneous Frequency (kHz)');

title('SIH 26058 - Geometric Sweep Instantaneous Frequency');

grid on;

xlim([0 T*1e3]);

ylim([0 550]);

%% =========================================================
% 11. GRAPH 3 - WINDOWED SIGNAL
% =========================================================

figure;

plot(t*1e3, windowedSignal);

xlabel('Time (ms)');
ylabel('Amplitude');

title(['SIH 26058 - Windowed Geometric Sweep (' ...
       windowName ')']);

grid on;

xlim([0 T*1e3]);

%% =========================================================
% 12. FFT ANALYSIS
% =========================================================

Y = fft(windowedSignal);

P2 = abs(Y/N);

P1 = P2(1:N/2+1);

P1(2:end-1) = 2*P1(2:end-1);

f = Fs*(0:N/2)/N;

%% =========================================================
% 13. GRAPH 4 - FFT SPECTRUM
% =========================================================

figure;

plot(f/1e3, P1);

xlabel('Frequency (kHz)');
ylabel('Magnitude');

title('SIH 26058 - FFT Spectrum of Geometric Sweep');

grid on;

xlim([0 600]);

%% =========================================================
% 14. GRAPH 5 - SPECTROGRAM
% =========================================================

figure;

spectrogram(windowedSignal,256,200,1024,Fs,'yaxis');

title('SIH 26058 - Geometric Frequency Sweep Spectrogram');

%% =========================================================
% 15. PERFORMANCE CALCULATION
% =========================================================

bandwidth = f1-f0;

rangeResolution = soundSpeed/(2*bandwidth);

fprintf('\n');
fprintf('PERFORMANCE INFORMATION\n');
fprintf('----------------------------------------------------\n');

fprintf('Bandwidth                  : %.2f kHz\n', ...
    bandwidth/1e3);

fprintf('Theoretical Range Resolution : %.4f m\n', ...
    rangeResolution);

fprintf('Theoretical Range Resolution : %.2f mm\n', ...
    rangeResolution*1000);

fprintf('----------------------------------------------------\n');

%% =========================================================
% 16. FREQUENCY LIMIT CHECK
% =========================================================

if f0 >= Fmin && f1 <= Fmax

    fprintf('Frequency Range    : VALID\n');

else

    fprintf('Frequency Range    : OUTSIDE LIMITS\n');

end

%% =========================================================
% 17. NYQUIST CHECK
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
fprintf('GEOMETRIC SWEEP GENERATION COMPLETE\n');
fprintf('====================================================\n');