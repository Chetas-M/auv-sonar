%% =========================================================
% SIH 26058
% ADAPTIVE SOFTWARE-DEFINED SONAR TRANSMITTER
%
% SONAR PULSE TRAIN GENERATOR
% =========================================================

clear;
clc;
close all;

%% =========================================================
% 1. LOAD PROJECT PARAMETERS
% =========================================================
parameters;

%% =========================================================
% 2. PULSE PARAMETERS
% =========================================================

pulseDuration = Tp;
pulseInterval = PRI;
pulseRepetitionFrequency = PRF;

%% =========================================================
% 3. SIMULATION TIME
% =========================================================

totalTime = 5 * PRI;

t = 0:Ts:totalTime-Ts;
N = length(t);

%% =========================================================
% 4. CREATE LFM PULSE
% =========================================================

f0 = LFM_fstart;
f1 = LFM_fstop;

K = (f1-f0)/pulseDuration;

%% =========================================================
% 5. CREATE SINGLE LFM PULSE
% =========================================================

pulseSamples = round(pulseDuration*Fs);

tp = (0:pulseSamples-1)*Ts;

phase = 2*pi*(f0*tp + 0.5*K*tp.^2);

singlePulse = A*cos(phase);

%% =========================================================
% 6. CREATE PULSE TRAIN
% =========================================================

pulseTrain = zeros(size(t));

for n = 0:floor(totalTime/PRI)-1

    startIndex = round(n*PRI*Fs) + 1;

    endIndex = startIndex + pulseSamples - 1;

    if endIndex <= length(pulseTrain)

        pulseTrain(startIndex:endIndex) = singlePulse;

    end

end

%% =========================================================
% 7. DISPLAY PARAMETERS
% =========================================================

fprintf('\n');
fprintf('====================================================\n');
fprintf('        SIH 26058 - SONAR PULSE TRAIN\n');
fprintf('====================================================\n');

fprintf('Sampling Frequency : %.2f MHz\n', Fs/1e6);
fprintf('Pulse Frequency    : %.2f kHz\n', Fc/1e3);
fprintf('Pulse Duration     : %.2f ms\n', Tp*1e3);
fprintf('PRI                : %.2f ms\n', PRI*1e3);
fprintf('PRF                : %.2f Hz\n', PRF);
fprintf('Duty Cycle         : %.2f %%\n', DutyCycle*100);
fprintf('Number of Pulses   : %d\n', floor(totalTime/PRI));

fprintf('====================================================\n');

%% =========================================================
% 8. GRAPH 1 - COMPLETE PULSE TRAIN
% =========================================================

figure;

plot(t*1e3,pulseTrain);

xlabel('Time (ms)');
ylabel('Amplitude');

title('SIH 26058 - Sonar LFM Pulse Train');

grid on;

%% =========================================================
% 9. GRAPH 2 - FIRST PULSE
% =========================================================

figure;

plot(tp*1e3,singlePulse);

xlabel('Time (ms)');
ylabel('Amplitude');

title('SIH 26058 - Single LFM Sonar Pulse');

grid on;

xlim([0 pulseDuration*1e3]);

%% =========================================================
% 10. GRAPH 3 - PULSE TRAIN ZOOM
% =========================================================

figure;

plot(t*1e3,pulseTrain);

xlabel('Time (ms)');
ylabel('Amplitude');

title('SIH 26058 - Pulse Train Timing');

grid on;

xlim([0 40]);

%% =========================================================
% 11. PERFORMANCE CALCULATIONS
% =========================================================

maxUnambiguousRange = soundSpeed*PRI/2;

pulseEnergy = sum(singlePulse.^2)*Ts;

peakPower = max(singlePulse.^2);

averagePower = pulseEnergy/PRI;

fprintf('\n');
fprintf('PERFORMANCE INFORMATION\n');
fprintf('----------------------------------------------------\n');

fprintf('Maximum Unambiguous Range : %.2f m\n', ...
    maxUnambiguousRange);

fprintf('Pulse Energy              : %.6e\n', ...
    pulseEnergy);

fprintf('Peak Normalized Power     : %.3f\n', ...
    peakPower);

fprintf('Average Normalized Power  : %.3f\n', ...
    averagePower);

fprintf('----------------------------------------------------\n');

%% =========================================================
% 12. RANGE CHECK
% =========================================================

if range <= maxUnambiguousRange

    fprintf('Target Range              : VALID\n');

else

    fprintf('Target Range              : INVALID\n');

end

%% =========================================================
% END
% =========================================================

fprintf('====================================================\n');
fprintf('SONAR PULSE TRAIN GENERATION COMPLETE\n');
fprintf('====================================================\n');