%% =========================================================
% SIH 26058
% ADAPTIVE SOFTWARE-DEFINED SONAR TRANSMITTER
%
% PHASE-CODED PULSE GENERATOR + ANALYSIS
% =========================================================

clear;
clc;
close all;

%% =========================================================
% 1. LOAD PROJECT PARAMETERS
% =========================================================

parameters;

%% =========================================================
% 2. PHASE-CODE PARAMETERS
% =========================================================

code = phaseCode;
chipTime = chipDuration;

numChips = length(code);

%% =========================================================
% 3. SAMPLES PER CHIP
% =========================================================

samplesPerChip = round(chipTime * Fs);

%% =========================================================
% 4. TOTAL CODE DURATION
% =========================================================

T = numChips * chipTime;

t = 0:Ts:T-Ts;

N = length(t);

%% =========================================================
% 5. CARRIER FREQUENCY
% =========================================================

carrierFrequency = Fc;

%% =========================================================
% 6. CREATE PHASE-CODED SIGNAL
% =========================================================

phaseCodedSignal = zeros(1,N);

for k = 1:numChips

    startIndex = (k-1)*samplesPerChip + 1;

    endIndex = min(k*samplesPerChip,N);

    chipTimeVector = t(startIndex:endIndex);

    phaseCodedSignal(startIndex:endIndex) = ...
        A * code(k) .* cos(2*pi*carrierFrequency*chipTimeVector);

end

%% =========================================================
% 7. CREATE PHASE SEQUENCE
% =========================================================

phaseSequence = zeros(size(t));

for k = 1:numChips

    startIndex = (k-1)*samplesPerChip + 1;

    endIndex = min(k*samplesPerChip,N);

    if code(k) == 1

        phaseSequence(startIndex:endIndex) = 0;

    else

        phaseSequence(startIndex:endIndex) = 180;

    end

end

%% =========================================================
% 8. WINDOWING
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

windowedSignal = phaseCodedSignal .* win;

%% =========================================================
% 9. DISPLAY PARAMETERS
% =========================================================

fprintf('\n');
fprintf('====================================================\n');
fprintf('        SIH 26058 - PHASE-CODED PULSE\n');
fprintf('====================================================\n');

fprintf('Sampling Frequency : %.2f MHz\n',Fs/1e6);

fprintf('Carrier Frequency  : %.2f kHz\n', ...
    carrierFrequency/1e3);

fprintf('Number of Chips    : %d\n',numChips);

fprintf('Chip Duration      : %.2f us\n', ...
    chipTime*1e6);

fprintf('Total Pulse Time   : %.2f us\n', ...
    T*1e6);

fprintf('Phase Code         : ');

fprintf('%d ',code);

fprintf('\n');

fprintf('Window             : %s\n',windowName);

fprintf('====================================================\n');

%% =========================================================
% 10. GRAPH 1 - PHASE CODE SEQUENCE
% =========================================================

figure;

stairs(t*1e6,phaseSequence);

xlabel('Time (\mus)');
ylabel('Phase (degrees)');

title('SIH 26058 - Phase Code Sequence');

grid on;

ylim([-20 200]);

xlim([0 T*1e6]);

%% =========================================================
% 11. GRAPH 2 - PHASE-CODED SIGNAL
% =========================================================

figure;

plot(t*1e6,phaseCodedSignal);

xlabel('Time (\mus)');
ylabel('Amplitude');

title('SIH 26058 - Phase-Coded Sonar Pulse');

grid on;

xlim([0 T*1e6]);

%% =========================================================
% 12. GRAPH 3 - WINDOWED SIGNAL
% =========================================================

figure;

plot(t*1e6,windowedSignal);

xlabel('Time (\mus)');
ylabel('Amplitude');

title(['SIH 26058 - Windowed Phase-Coded Pulse (' ...
       windowName ')']);

grid on;

xlim([0 T*1e6]);

%% =========================================================
% 13. FFT ANALYSIS
% =========================================================

Y = fft(windowedSignal);

P2 = abs(Y/N);

P1 = P2(1:N/2+1);

P1(2:end-1) = 2*P1(2:end-1);

f = Fs*(0:N/2)/N;

%% =========================================================
% 14. GRAPH 4 - FFT SPECTRUM
% =========================================================

figure;

plot(f/1e3,P1);

xlabel('Frequency (kHz)');
ylabel('Magnitude');

title('SIH 26058 - FFT Spectrum of Phase-Coded Pulse');

grid on;

xlim([0 600]);

%% =========================================================
% 15. GRAPH 5 - SPECTROGRAM
% =========================================================

figure;

spectrogram(windowedSignal,256,200,1024,Fs,'yaxis');

title('SIH 26058 - Phase-Coded Pulse Spectrogram');

%% =========================================================
% 16. PERFORMANCE CALCULATION
% =========================================================

bandwidth = 1/chipTime;

rangeResolution = soundSpeed/(2*bandwidth);

fprintf('\n');
fprintf('PERFORMANCE INFORMATION\n');
fprintf('----------------------------------------------------\n');

fprintf('Approx. Code Bandwidth       : %.2f kHz\n', ...
    bandwidth/1e3);

fprintf('Theoretical Range Resolution : %.4f m\n', ...
    rangeResolution);

fprintf('Theoretical Range Resolution : %.2f mm\n', ...
    rangeResolution*1000);

fprintf('----------------------------------------------------\n');

%% =========================================================
% 17. FREQUENCY / SAMPLING CHECK
% =========================================================

if carrierFrequency >= Fmin && carrierFrequency <= Fmax

    fprintf('Carrier Frequency  : VALID');

else

    fprintf('Carrier Frequency  : OUTSIDE LIMITS');

end

fprintf('\n');

if Fs >= 2*carrierFrequency

    fprintf('Sampling Condition : VALID');

else

    fprintf('Sampling Condition : INVALID');

end

fprintf('\n');

%% =========================================================
% 18. CODE VALIDATION
% =========================================================

if all(code == 1 | code == -1)

    fprintf('Phase Code          : VALID');

else

    fprintf('Phase Code          : INVALID');

end

fprintf('\n');

%% =========================================================
% 19. END
% =========================================================

fprintf('====================================================\n');
fprintf('PHASE-CODED PULSE GENERATION COMPLETE\n');
fprintf('====================================================\n');