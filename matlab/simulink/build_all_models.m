% ==============================================================================
% SIH Problem 26058: AUV Sonar Transmitter Digital Twin
%
% File: build_all_models.m
% Description: Programmatic model builder for the complete Simulink model suite.
% Generates, configures, wires, and saves:
%   1. auv_sonar_transmitter_payload.slx (ALL-IN-ONE Master Unified Model)
%   2. auv_sonar_mission_controller.slx  (Ping-rate adaptation & power model)
%   3. auv_sonar_waveform_pipeline.slx   (High-speed 4.0 MSPS DAC & DSP pipeline)
%   4. auv_sonar_payload_top.slx         (Top-level integrated payload architecture)
%
% Every model features self-healing path-detecting callbacks to prevent
% 'Unrecognized function or variable init_sonar_simulink' errors regardless
% of how or from where the model is opened.
% ==============================================================================

function build_all_models()
    fprintf('==============================================================================\n');
    fprintf('  BUILDING SIMULINK MODELS REFERENCED TO MATLAB DIGITAL TWIN (SIH 26058)\n');
    fprintf('==============================================================================\n');

    % Setup environment and paths
    simulink_dir = fileparts(mfilename('fullpath'));
    matlab_dir = fullfile(simulink_dir, '..');
    addpath(matlab_dir);
    addpath(simulink_dir);

    % Initialize workspace data
    init_sonar_simulink();

    % Output model paths
    model_unified_name = 'auv_sonar_transmitter_payload';
    model1_name = 'auv_sonar_mission_controller';
    model2_name = 'auv_sonar_waveform_pipeline';
    model3_name = 'auv_sonar_payload_top';

    model_unified_path = fullfile(simulink_dir, [model_unified_name '.slx']);
    model1_path = fullfile(simulink_dir, [model1_name '.slx']);
    model2_path = fullfile(simulink_dir, [model2_name '.slx']);
    model3_path = fullfile(simulink_dir, [model3_name '.slx']);

    % Close any open instances before rebuilding
    close_if_open(model_unified_name);
    close_if_open(model1_name);
    close_if_open(model2_name);
    close_if_open(model3_name);

    % --------------------------------------------------------------------------
    % Build Unified Model: auv_sonar_transmitter_payload
    % --------------------------------------------------------------------------
    fprintf('\n[*] Building All-In-One Model: %s.slx...\n', model_unified_name);
    build_unified_model(model_unified_name, model_unified_path);
    fprintf('    [+] Saved: %s\n', model_unified_path);

    % --------------------------------------------------------------------------
    % Build Model 1: auv_sonar_mission_controller
    % --------------------------------------------------------------------------
    fprintf('\n[*] Building Model 1: %s.slx (Ping-rate controller, Ts = 20 ms)...\n', model1_name);
    build_mission_controller(model1_name, model1_path);
    fprintf('    [+] Saved: %s\n', model1_path);

    % --------------------------------------------------------------------------
    % Build Model 2: auv_sonar_waveform_pipeline
    % --------------------------------------------------------------------------
    fprintf('\n[*] Building Model 2: %s.slx (4.0 MSPS DAC & DSP pipeline)...\n', model2_name);
    build_waveform_pipeline(model2_name, model2_path);
    fprintf('    [+] Saved: %s\n', model2_path);

    % --------------------------------------------------------------------------
    % Build Model 3: auv_sonar_payload_top
    % --------------------------------------------------------------------------
    fprintf('\n[*] Building Model 3: %s.slx (Integrated top-level payload)...\n', model3_name);
    build_payload_top(model3_name, model3_path);
    fprintf('    [+] Saved: %s\n', model3_path);

    fprintf('\n==============================================================================\n');
    fprintf('  ALL 4 SIMULINK MODELS BUILT AND SAVED SUCCESSFULLY\n');
    fprintf('==============================================================================\n');
end

% ==============================================================================
% Self-Healing Callback Generator
% Automatically discovers model directory and adds matlab paths before loading
% ==============================================================================
function cb = get_self_healing_callback()
    cb = sprintf([ ...
        '%% Self-healing path configuration for AUV Sonar Simulink Suite\n' ...
        'm_file = get_param(bdroot, ''FileName'');\n' ...
        'if ~isempty(m_file)\n' ...
        '    m_dir = fileparts(m_file);\n' ...
        '    addpath(m_dir);\n' ...
        '    addpath(fullfile(m_dir, ''..''));\n' ...
        'else\n' ...
        '    if exist(fullfile(pwd, ''matlab'', ''simulink''), ''dir'')\n' ...
        '        addpath(fullfile(pwd, ''matlab'', ''simulink''));\n' ...
        '        addpath(fullfile(pwd, ''matlab''));\n' ...
        '    end\n' ...
        'end\n' ...
        'if exist(''init_sonar_simulink'', ''file'') == 2\n' ...
        '    init_sonar_simulink;\n' ...
        'end\n']);
end

% ==============================================================================
% Model Builder: auv_sonar_transmitter_payload (ALL-IN-ONE Master Model)
% ==============================================================================
function build_unified_model(model_name, save_path)
    new_system(model_name);
    load_system(model_name);

    % Configuration
    set_param(model_name, 'SolverType', 'Fixed-step');
    set_param(model_name, 'Solver', 'FixedStepDiscrete');
    set_param(model_name, 'FixedStep', 'Ts_ping');
    set_param(model_name, 'StartTime', '0.0');
    set_param(model_name, 'StopTime', 't_mission_end');

    % Robust self-healing callbacks
    cb = get_self_healing_callback();
    set_param(model_name, 'PreLoadFcn', cb);
    set_param(model_name, 'InitFcn', cb);

    % 1. Input Sources: From Workspace
    add_block('simulink/Sources/From Workspace', [model_name '/Turbidity_Plume_NTU']);
    set_param([model_name '/Turbidity_Plume_NTU'], 'VariableName', 'turb_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 40, 200, 70]);

    add_block('simulink/Sources/From Workspace', [model_name '/Depth_m']);
    set_param([model_name '/Depth_m'], 'VariableName', 'depth_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 90, 200, 120]);

    add_block('simulink/Sources/From Workspace', [model_name '/Temperature_C']);
    set_param([model_name '/Temperature_C'], 'VariableName', 'temp_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 140, 200, 170]);

    add_block('simulink/Sources/From Workspace', [model_name '/Salinity_PSU']);
    set_param([model_name '/Salinity_PSU'], 'VariableName', 'sal_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 190, 200, 220]);

    add_block('simulink/Sources/From Workspace', [model_name '/Ambient_Noise_dB']);
    set_param([model_name '/Ambient_Noise_dB'], 'VariableName', 'noise_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 240, 200, 270]);

    add_block('simulink/Sources/From Workspace', [model_name '/Target_Range_m']);
    set_param([model_name '/Target_Range_m'], 'VariableName', 'range_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 290, 200, 320]);

    add_block('simulink/Sources/From Workspace', [model_name '/Mission_Objective_Mode']);
    set_param([model_name '/Mission_Objective_Mode'], 'VariableName', 'mission_mode_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 340, 200, 370]);

    add_block('simulink/Sources/Constant', [model_name '/Pulse_Duration_s']);
    set_param([model_name '/Pulse_Duration_s'], 'Value', 'Tp', 'Position', [50, 410, 200, 440]);

    % 2. Subsystem: Channel & Propagation Evaluator
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/Channel_Propagation_Evaluator']);
    set_param([model_name '/Channel_Propagation_Evaluator'], 'Position', [280, 150, 520, 270]);
    sf = sfroot;
    ch1 = sf.find('Path', [model_name '/Channel_Propagation_Evaluator'], '-isa', 'Stateflow.EMChart');
    ch1.Script = sprintf([ ...
        'function [Q, cand_id, viability_conf, p1_viable, p2_viable, p3_viable] = ...\n' ...
        '    Channel_Propagation_Evaluator(turb, depth, temp, sal, noise, range, mode)\n' ...
        'coder.extrinsic(''sim_bridge_channel'');\n' ...
        'Q = 0.0;\n' ...
        'cand_id = 1.0;\n' ...
        'viability_conf = 0.0;\n' ...
        'p1_viable = 0.0;\n' ...
        'p2_viable = 0.0;\n' ...
        'p3_viable = 0.0;\n' ...
        '[Q, cand_id, viability_conf, p1_viable, p2_viable, p3_viable] = ...\n' ...
        '    sim_bridge_channel(turb, depth, temp, sal, noise, range, mode);\n' ...
        'end\n']);

    % 3. Subsystem: Adaptive Controller FSM
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/Adaptive_Controller']);
    set_param([model_name '/Adaptive_Controller'], 'Position', [590, 160, 810, 260]);
    ch2 = sf.find('Path', [model_name '/Adaptive_Controller'], '-isa', 'Stateflow.EMChart');
    ch2.Script = sprintf([ ...
        'function [active_id, pending_id, cand_id, debounce_cnt, amp] = Adaptive_Controller(Q_val)\n' ...
        'coder.extrinsic(''sim_bridge_controller'');\n' ...
        'active_id = 2.0;\n' ...
        'pending_id = 2.0;\n' ...
        'cand_id = 2.0;\n' ...
        'debounce_cnt = 0.0;\n' ...
        'amp = 0.70;\n' ...
        '[active_id, pending_id, cand_id, debounce_cnt, amp] = sim_bridge_controller(Q_val);\n' ...
        'end\n']);

    % 4. Subsystem: Power Model & Battery Life Estimator
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/Power_Model_Estimator']);
    set_param([model_name '/Power_Model_Estimator'], 'Position', [880, 240, 1080, 330]);
    ch3 = sf.find('Path', [model_name '/Power_Model_Estimator'], '-isa', 'Stateflow.EMChart');
    ch3.Script = sprintf([ ...
        'function [P_avg_w, I_avg_ma, endurance_hrs, energy_ping_mj] = Power_Model_Estimator(amp, Tp_val)\n' ...
        'coder.extrinsic(''sim_bridge_power'');\n' ...
        'P_avg_w = 0.0;\n' ...
        'I_avg_ma = 0.0;\n' ...
        'endurance_hrs = 0.0;\n' ...
        'energy_ping_mj = 0.0;\n' ...
        '[P_avg_w, I_avg_ma, endurance_hrs, energy_ping_mj] = sim_bridge_power(amp, Tp_val);\n' ...
        'end\n']);

    % 5. Subsystem: DMA Memory Buffer & Waveform Mapper
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/DMA_Buffer_Mapper']);
    set_param([model_name '/DMA_Buffer_Mapper'], 'Position', [880, 110, 1080, 200]);
    ch4 = sf.find('Path', [model_name '/DMA_Buffer_Mapper'], '-isa', 'Stateflow.EMChart');
    ch4.Script = sprintf([ ...
        'function [buffer_bytes, peak_sample_code, center_freq_khz] = DMA_Buffer_Mapper(active_id, amp)\n' ...
        'buffer_bytes = 16000.0; %% 8000 samples * 2 bytes\n' ...
        'fc = 300.0;\n' ...
        'if active_id == 1\n' ...
        '    fc = 160.0;\n' ...
        'elseif active_id == 3\n' ...
        '    fc = 425.0;\n' ...
        'end\n' ...
        'center_freq_khz = fc;\n' ...
        'peak_sample_code = 2048.0 + (2047.5 * amp);\n' ...
        'end\n']);

    % 6. Sinks: To Workspace Blocks
    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Q']);
    set_param([model_name '/Log_Q'], 'VariableName', 'sim_Q', 'SaveFormat', 'Array', 'Position', [580, 60, 680, 90]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Turbidity']);
    set_param([model_name '/Log_Turbidity'], 'VariableName', 'sim_turbidity_ntu', 'SaveFormat', 'Array', 'Position', [280, 40, 380, 70]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Active_Profile']);
    set_param([model_name '/Log_Active_Profile'], 'VariableName', 'sim_active_profile', 'SaveFormat', 'Array', 'Position', [880, 60, 980, 90]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Candidate_Profile']);
    set_param([model_name '/Log_Candidate_Profile'], 'VariableName', 'sim_cand_profile', 'SaveFormat', 'Array', 'Position', [880, 10, 980, 40]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Amplitude']);
    set_param([model_name '/Log_Amplitude'], 'VariableName', 'sim_amplitude', 'SaveFormat', 'Array', 'Position', [1150, 190, 1250, 220]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Avg_Power']);
    set_param([model_name '/Log_Avg_Power'], 'VariableName', 'sim_avg_power_w', 'SaveFormat', 'Array', 'Position', [1150, 240, 1250, 270]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Avg_Current']);
    set_param([model_name '/Log_Avg_Current'], 'VariableName', 'sim_avg_current_ma', 'SaveFormat', 'Array', 'Position', [1150, 280, 1250, 310]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Endurance']);
    set_param([model_name '/Log_Endurance'], 'VariableName', 'sim_endurance_hrs', 'SaveFormat', 'Array', 'Position', [1150, 320, 1250, 350]);

    % 7. Scopes & Displays Aligned with Engineering Report
    add_block('simulink/Sinks/Scope', [model_name '/Scope_Channel_Adaptation_Report_Fig09_12']);
    set_param([model_name '/Scope_Channel_Adaptation_Report_Fig09_12'], 'NumInputPorts', '3', 'Position', [880, 360, 930, 410]);

    add_block('simulink/Sinks/Scope', [model_name '/Scope_Power_Battery_Report_Fig13']);
    set_param([model_name '/Scope_Power_Battery_Report_Fig13'], 'NumInputPorts', '3', 'Position', [1150, 370, 1200, 420]);

    add_block('simulink/Sinks/Scope', [model_name '/Scope_Telemetry_Overview']);
    set_param([model_name '/Scope_Telemetry_Overview'], 'NumInputPorts', '4', 'Position', [1150, 60, 1200, 120]);

    add_block('simulink/Sinks/Display', [model_name '/Display_Active_Profile']);
    set_param([model_name '/Display_Active_Profile'], 'Position', [1000, 55, 1080, 85]);

    add_block('simulink/Sinks/Display', [model_name '/Display_Amplitude']);
    set_param([model_name '/Display_Amplitude'], 'Position', [1150, 140, 1230, 170]);

    add_block('simulink/Sinks/Display', [model_name '/Display_Avg_Power_W']);
    set_param([model_name '/Display_Avg_Power_W'], 'Position', [1260, 240, 1340, 270]);

    add_block('simulink/Sinks/Display', [model_name '/Display_DMA_Buffer_Bytes']);
    set_param([model_name '/Display_DMA_Buffer_Bytes'], 'Position', [1150, 100, 1230, 130]);

    % 8. Wire Connections
    add_line(model_name, 'Turbidity_Plume_NTU/1', 'Channel_Propagation_Evaluator/1', 'autorouting', 'on');
    add_line(model_name, 'Turbidity_Plume_NTU/1', 'Log_Turbidity/1', 'autorouting', 'on');

    add_line(model_name, 'Depth_m/1', 'Channel_Propagation_Evaluator/2', 'autorouting', 'on');
    add_line(model_name, 'Temperature_C/1', 'Channel_Propagation_Evaluator/3', 'autorouting', 'on');
    add_line(model_name, 'Salinity_PSU/1', 'Channel_Propagation_Evaluator/4', 'autorouting', 'on');
    add_line(model_name, 'Ambient_Noise_dB/1', 'Channel_Propagation_Evaluator/5', 'autorouting', 'on');
    add_line(model_name, 'Target_Range_m/1', 'Channel_Propagation_Evaluator/6', 'autorouting', 'on');
    add_line(model_name, 'Mission_Objective_Mode/1', 'Channel_Propagation_Evaluator/7', 'autorouting', 'on');

    % Evaluator -> Controller & Sinks
    add_line(model_name, 'Channel_Propagation_Evaluator/1', 'Adaptive_Controller/1', 'autorouting', 'on');
    add_line(model_name, 'Channel_Propagation_Evaluator/1', 'Log_Q/1', 'autorouting', 'on');
    add_line(model_name, 'Channel_Propagation_Evaluator/1', 'Scope_Channel_Adaptation_Report_Fig09_12/1', 'autorouting', 'on');
    add_line(model_name, 'Channel_Propagation_Evaluator/1', 'Scope_Telemetry_Overview/1', 'autorouting', 'on');

    % Controller -> DMA Buffer Mapper & Outputs
    add_line(model_name, 'Adaptive_Controller/1', 'DMA_Buffer_Mapper/1', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/1', 'Log_Active_Profile/1', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/1', 'Display_Active_Profile/1', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/1', 'Scope_Channel_Adaptation_Report_Fig09_12/2', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/1', 'Scope_Telemetry_Overview/2', 'autorouting', 'on');

    add_line(model_name, 'Adaptive_Controller/3', 'Log_Candidate_Profile/1', 'autorouting', 'on');

    add_line(model_name, 'Adaptive_Controller/5', 'DMA_Buffer_Mapper/2', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/5', 'Power_Model_Estimator/1', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/5', 'Log_Amplitude/1', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/5', 'Display_Amplitude/1', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/5', 'Scope_Channel_Adaptation_Report_Fig09_12/3', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/5', 'Scope_Telemetry_Overview/3', 'autorouting', 'on');

    add_line(model_name, 'Pulse_Duration_s/1', 'Power_Model_Estimator/2', 'autorouting', 'on');

    % DMA Buffer Mapper -> Displays
    add_line(model_name, 'DMA_Buffer_Mapper/1', 'Display_DMA_Buffer_Bytes/1', 'autorouting', 'on');

    % Power Estimator -> Sinks
    add_line(model_name, 'Power_Model_Estimator/1', 'Log_Avg_Power/1', 'autorouting', 'on');
    add_line(model_name, 'Power_Model_Estimator/1', 'Display_Avg_Power_W/1', 'autorouting', 'on');
    add_line(model_name, 'Power_Model_Estimator/1', 'Scope_Power_Battery_Report_Fig13/1', 'autorouting', 'on');
    add_line(model_name, 'Power_Model_Estimator/1', 'Scope_Telemetry_Overview/4', 'autorouting', 'on');

    add_line(model_name, 'Power_Model_Estimator/2', 'Log_Avg_Current/1', 'autorouting', 'on');
    add_line(model_name, 'Power_Model_Estimator/2', 'Scope_Power_Battery_Report_Fig13/2', 'autorouting', 'on');

    add_line(model_name, 'Power_Model_Estimator/3', 'Log_Endurance/1', 'autorouting', 'on');
    add_line(model_name, 'Power_Model_Estimator/3', 'Scope_Power_Battery_Report_Fig13/3', 'autorouting', 'on');

    % Model Annotations
    ann_text = sprintf([ ...
        '====================================================================================\n' ...
        'SIH Problem 26058: ALL-IN-ONE AUV ADAPTIVE SONAR TRANSMITTER PAYLOAD (DIGITAL TWIN)\n' ...
        'Locked Hardware: STM32G474RET6 @ 160 MHz SYSCLK | 4.0 MSPS 12-Bit DAC | OPAMP3 PB1\n' ...
        'Timing: PRI = 20.0 ms (50 Hz ping rate) | Pulse Duration: Tp = 2.0 ms (10%% duty cycle)\n' ...
        'Profiles: 1: LOW (100-220kHz, A=1.0) | 2: BALANCED (200-400kHz, A=0.7) | 3: HIGH (350-500kHz, A=0.4)\n' ...
        'Simulink Scopes align directly with Engineering Report Figures 1-13.\n' ...
        '[SCOPE]: Validates transmitter payload pipeline only; physically unverified for physical ocean echoes.\n' ...
        '====================================================================================']);
    an = Simulink.Annotation(model_name, ann_text);
    an.Position = [50, 480];

    save_system(model_name, save_path);
    close_system(model_name);
end

% ==============================================================================
% Model 1 Builder: auv_sonar_mission_controller
% ==============================================================================
function build_mission_controller(model_name, save_path)
    new_system(model_name);
    load_system(model_name);

    % Model configuration parameters
    set_param(model_name, 'SolverType', 'Fixed-step');
    set_param(model_name, 'Solver', 'FixedStepDiscrete');
    set_param(model_name, 'FixedStep', 'Ts_ping');
    set_param(model_name, 'StartTime', '0.0');
    set_param(model_name, 'StopTime', 't_mission_end');

    % Robust self-healing callbacks
    cb = get_self_healing_callback();
    set_param(model_name, 'PreLoadFcn', cb);
    set_param(model_name, 'InitFcn', cb);

    % 1. Input Sources: From Workspace
    add_block('simulink/Sources/From Workspace', [model_name '/Turbidity_Plume_NTU']);
    set_param([model_name '/Turbidity_Plume_NTU'], 'VariableName', 'turb_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 40, 200, 70]);

    add_block('simulink/Sources/From Workspace', [model_name '/Depth_m']);
    set_param([model_name '/Depth_m'], 'VariableName', 'depth_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 90, 200, 120]);

    add_block('simulink/Sources/From Workspace', [model_name '/Temperature_C']);
    set_param([model_name '/Temperature_C'], 'VariableName', 'temp_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 140, 200, 170]);

    add_block('simulink/Sources/From Workspace', [model_name '/Salinity_PSU']);
    set_param([model_name '/Salinity_PSU'], 'VariableName', 'sal_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 190, 200, 220]);

    add_block('simulink/Sources/From Workspace', [model_name '/Ambient_Noise_dB']);
    set_param([model_name '/Ambient_Noise_dB'], 'VariableName', 'noise_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 240, 200, 270]);

    add_block('simulink/Sources/From Workspace', [model_name '/Target_Range_m']);
    set_param([model_name '/Target_Range_m'], 'VariableName', 'range_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 290, 200, 320]);

    add_block('simulink/Sources/From Workspace', [model_name '/Mission_Objective_Mode']);
    set_param([model_name '/Mission_Objective_Mode'], 'VariableName', 'mission_mode_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 340, 200, 370]);

    % Pulse Duration Constant (2.0 ms)
    add_block('simulink/Sources/Constant', [model_name '/Pulse_Duration_s']);
    set_param([model_name '/Pulse_Duration_s'], 'Value', 'Tp', 'Position', [50, 410, 200, 440]);

    % 2. Subsystem: Channel & Propagation Evaluator
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/Channel_Propagation_Evaluator']);
    set_param([model_name '/Channel_Propagation_Evaluator'], 'Position', [280, 150, 520, 270]);
    sf = sfroot;
    ch1 = sf.find('Path', [model_name '/Channel_Propagation_Evaluator'], '-isa', 'Stateflow.EMChart');
    ch1.Script = sprintf([ ...
        'function [Q, cand_id, viability_conf, p1_viable, p2_viable, p3_viable] = ...\n' ...
        '    Channel_Propagation_Evaluator(turb, depth, temp, sal, noise, range, mode)\n' ...
        'coder.extrinsic(''sim_bridge_channel'');\n' ...
        'Q = 0.0;\n' ...
        'cand_id = 1.0;\n' ...
        'viability_conf = 0.0;\n' ...
        'p1_viable = 0.0;\n' ...
        'p2_viable = 0.0;\n' ...
        'p3_viable = 0.0;\n' ...
        '[Q, cand_id, viability_conf, p1_viable, p2_viable, p3_viable] = ...\n' ...
        '    sim_bridge_channel(turb, depth, temp, sal, noise, range, mode);\n' ...
        'end\n']);

    % 3. Subsystem: Adaptive Controller (Directional Hysteresis & Debounce N=2)
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/Adaptive_Controller']);
    set_param([model_name '/Adaptive_Controller'], 'Position', [590, 160, 810, 260]);
    ch2 = sf.find('Path', [model_name '/Adaptive_Controller'], '-isa', 'Stateflow.EMChart');
    ch2.Script = sprintf([ ...
        'function [active_id, pending_id, cand_id, debounce_cnt, amp] = Adaptive_Controller(Q_val)\n' ...
        'coder.extrinsic(''sim_bridge_controller'');\n' ...
        'active_id = 2.0;\n' ...
        'pending_id = 2.0;\n' ...
        'cand_id = 2.0;\n' ...
        'debounce_cnt = 0.0;\n' ...
        'amp = 0.70;\n' ...
        '[active_id, pending_id, cand_id, debounce_cnt, amp] = sim_bridge_controller(Q_val);\n' ...
        'end\n']);

    % 4. Subsystem: Power Model & Battery Life Estimator
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/Power_Model_Estimator']);
    set_param([model_name '/Power_Model_Estimator'], 'Position', [880, 240, 1080, 330]);
    ch3 = sf.find('Path', [model_name '/Power_Model_Estimator'], '-isa', 'Stateflow.EMChart');
    ch3.Script = sprintf([ ...
        'function [P_avg_w, I_avg_ma, endurance_hrs, energy_ping_mj] = Power_Model_Estimator(amp, Tp_val)\n' ...
        'coder.extrinsic(''sim_bridge_power'');\n' ...
        'P_avg_w = 0.0;\n' ...
        'I_avg_ma = 0.0;\n' ...
        'endurance_hrs = 0.0;\n' ...
        'energy_ping_mj = 0.0;\n' ...
        '[P_avg_w, I_avg_ma, endurance_hrs, energy_ping_mj] = sim_bridge_power(amp, Tp_val);\n' ...
        'end\n']);

    % 5. Sinks: To Workspace Blocks
    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Q']);
    set_param([model_name '/Log_Q'], 'VariableName', 'sim_Q', 'SaveFormat', 'Array', 'Position', [580, 60, 680, 90]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Active_Profile']);
    set_param([model_name '/Log_Active_Profile'], 'VariableName', 'sim_active_profile', 'SaveFormat', 'Array', 'Position', [880, 150, 980, 180]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Candidate_Profile']);
    set_param([model_name '/Log_Candidate_Profile'], 'VariableName', 'sim_cand_profile', 'SaveFormat', 'Array', 'Position', [880, 195, 980, 225]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Amplitude']);
    set_param([model_name '/Log_Amplitude'], 'VariableName', 'sim_amplitude', 'SaveFormat', 'Array', 'Position', [1150, 190, 1250, 220]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Avg_Power']);
    set_param([model_name '/Log_Avg_Power'], 'VariableName', 'sim_avg_power_w', 'SaveFormat', 'Array', 'Position', [1150, 240, 1250, 270]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Avg_Current']);
    set_param([model_name '/Log_Avg_Current'], 'VariableName', 'sim_avg_current_ma', 'SaveFormat', 'Array', 'Position', [1150, 280, 1250, 310]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Endurance']);
    set_param([model_name '/Log_Endurance'], 'VariableName', 'sim_endurance_hrs', 'SaveFormat', 'Array', 'Position', [1150, 320, 1250, 350]);

    % 6. Scopes & Displays
    add_block('simulink/Sinks/Scope', [model_name '/Scope_Channel_Adaptation']);
    set_param([model_name '/Scope_Channel_Adaptation'], 'NumInputPorts', '3', 'Position', [880, 80, 930, 130]);

    add_block('simulink/Sinks/Scope', [model_name '/Scope_Power_Battery']);
    set_param([model_name '/Scope_Power_Battery'], 'NumInputPorts', '3', 'Position', [1150, 370, 1200, 420]);

    add_block('simulink/Sinks/Display', [model_name '/Display_Active_Profile']);
    set_param([model_name '/Display_Active_Profile'], 'Position', [1000, 145, 1080, 175]);

    add_block('simulink/Sinks/Display', [model_name '/Display_Avg_Power_W']);
    set_param([model_name '/Display_Avg_Power_W'], 'Position', [1150, 140, 1230, 170]);

    % 7. Wire Connections
    add_line(model_name, 'Turbidity_Plume_NTU/1', 'Channel_Propagation_Evaluator/1', 'autorouting', 'on');
    add_line(model_name, 'Depth_m/1', 'Channel_Propagation_Evaluator/2', 'autorouting', 'on');
    add_line(model_name, 'Temperature_C/1', 'Channel_Propagation_Evaluator/3', 'autorouting', 'on');
    add_line(model_name, 'Salinity_PSU/1', 'Channel_Propagation_Evaluator/4', 'autorouting', 'on');
    add_line(model_name, 'Ambient_Noise_dB/1', 'Channel_Propagation_Evaluator/5', 'autorouting', 'on');
    add_line(model_name, 'Target_Range_m/1', 'Channel_Propagation_Evaluator/6', 'autorouting', 'on');
    add_line(model_name, 'Mission_Objective_Mode/1', 'Channel_Propagation_Evaluator/7', 'autorouting', 'on');

    add_line(model_name, 'Channel_Propagation_Evaluator/1', 'Adaptive_Controller/1', 'autorouting', 'on');
    add_line(model_name, 'Channel_Propagation_Evaluator/1', 'Log_Q/1', 'autorouting', 'on');
    add_line(model_name, 'Channel_Propagation_Evaluator/1', 'Scope_Channel_Adaptation/1', 'autorouting', 'on');

    add_line(model_name, 'Adaptive_Controller/1', 'Log_Active_Profile/1', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/1', 'Display_Active_Profile/1', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/1', 'Scope_Channel_Adaptation/2', 'autorouting', 'on');

    add_line(model_name, 'Adaptive_Controller/3', 'Log_Candidate_Profile/1', 'autorouting', 'on');

    add_line(model_name, 'Adaptive_Controller/5', 'Power_Model_Estimator/1', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/5', 'Log_Amplitude/1', 'autorouting', 'on');
    add_line(model_name, 'Adaptive_Controller/5', 'Scope_Channel_Adaptation/3', 'autorouting', 'on');

    add_line(model_name, 'Pulse_Duration_s/1', 'Power_Model_Estimator/2', 'autorouting', 'on');

    add_line(model_name, 'Power_Model_Estimator/1', 'Log_Avg_Power/1', 'autorouting', 'on');
    add_line(model_name, 'Power_Model_Estimator/1', 'Display_Avg_Power_W/1', 'autorouting', 'on');
    add_line(model_name, 'Power_Model_Estimator/1', 'Scope_Power_Battery/1', 'autorouting', 'on');

    add_line(model_name, 'Power_Model_Estimator/2', 'Log_Avg_Current/1', 'autorouting', 'on');
    add_line(model_name, 'Power_Model_Estimator/2', 'Scope_Power_Battery/2', 'autorouting', 'on');

    add_line(model_name, 'Power_Model_Estimator/3', 'Log_Endurance/1', 'autorouting', 'on');
    add_line(model_name, 'Power_Model_Estimator/3', 'Scope_Power_Battery/3', 'autorouting', 'on');

    ann_text = sprintf([ ...
        'SIH Problem 26058: AUV Sonar Transmitter Mission Controller (Digital Twin)\n' ...
        'Sampling Rate: Ts = PRI = 20.0 ms (50 Hz ping rate) | Dynamic Duration: 3.0 s (150 Pings)\n' ...
        'Referenced Modules: channel_model.m, evaluate_profile_performance.m, adaptive_controller.m, power_model.m\n' ...
        '[SCOPE]: Transmitter payload adaptation only; does not model ocean multipath or receiver hydrophone echoes.']);
    an = Simulink.Annotation(model_name, ann_text);
    an.Position = [50, 480];

    save_system(model_name, save_path);
    close_system(model_name);
end

% ==============================================================================
% Model 2 Builder: auv_sonar_waveform_pipeline
% ==============================================================================
function build_waveform_pipeline(model_name, save_path)
    new_system(model_name);
    load_system(model_name);

    % Configuration
    set_param(model_name, 'SolverType', 'Fixed-step');
    set_param(model_name, 'Solver', 'FixedStepDiscrete');
    set_param(model_name, 'FixedStep', 'Ts_dac'); % 250 ns (4.0 MSPS)
    set_param(model_name, 'StartTime', '0.0');
    set_param(model_name, 'StopTime', 'Tp');      % 2.0 ms pulse duration

    % Robust self-healing callbacks
    cb = get_self_healing_callback();
    set_param(model_name, 'PreLoadFcn', cb);
    set_param(model_name, 'InitFcn', cb);

    % 1. Input Sources: Selected Profile and Amplitude
    add_block('simulink/Sources/Constant', [model_name '/Selected_Profile_ID']);
    set_param([model_name '/Selected_Profile_ID'], 'Value', '2', ...
              'SampleTime', 'Ts_dac', 'Position', [50, 80, 160, 110]);

    add_block('simulink/Sources/Constant', [model_name '/Transmit_Amplitude']);
    set_param([model_name '/Transmit_Amplitude'], 'Value', '0.70', ...
              'SampleTime', 'Ts_dac', 'Position', [50, 140, 160, 170]);

    add_block('simulink/Sources/Digital Clock', [model_name '/Digital_Time_Clock']);
    set_param([model_name '/Digital_Time_Clock'], 'SampleTime', 'Ts_dac', 'Position', [50, 200, 160, 230]);

    % 2. Subsystem: LFM Chirp Continuous Synthesizer & Hann Windowing
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/LFM_Chirp_Synthesizer']);
    set_param([model_name '/LFM_Chirp_Synthesizer'], 'Position', [220, 110, 450, 230]);
    sf = sfroot;
    ch1 = sf.find('Path', [model_name '/LFM_Chirp_Synthesizer'], '-isa', 'Stateflow.EMChart');
    ch1.Script = sprintf([ ...
        'function [x_ideal, inst_freq_khz, window_envelope] = LFM_Chirp_Synthesizer(prof_id, amp, t_sec)\n' ...
        'coder.extrinsic(''sim_bridge_waveform'');\n' ...
        'x_ideal = 0.0;\n' ...
        'inst_freq_khz = 200.0;\n' ...
        'window_envelope = 0.0;\n' ...
        '[x_ideal, inst_freq_khz, window_envelope] = sim_bridge_waveform(prof_id, amp, t_sec);\n' ...
        'end\n']);

    % 3. Subsystem: 12-Bit DAC Quantizer & DMA Memory Mapping
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/DAC_12Bit_Quantizer']);
    set_param([model_name '/DAC_12Bit_Quantizer'], 'Position', [520, 110, 750, 230]);
    ch2 = sf.find('Path', [model_name '/DAC_12Bit_Quantizer'], '-isa', 'Stateflow.EMChart');
    ch2.Script = sprintf([ ...
        'function [dac_code, v_dac_volts, quant_error_lsb, quant_error_mv] = DAC_12Bit_Quantizer(x_in)\n' ...
        'coder.extrinsic(''sim_bridge_dac'');\n' ...
        'dac_code = 2048.0;\n' ...
        'v_dac_volts = 1.65;\n' ...
        'quant_error_lsb = 0.0;\n' ...
        'quant_error_mv = 0.0;\n' ...
        '[dac_code, v_dac_volts, quant_error_lsb, quant_error_mv] = sim_bridge_dac(x_in);\n' ...
        'end\n']);

    % 4. Subsystem: OPAMP3 High-Speed Follower & Analog AC Output
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/OPAMP3_Follower_Stage']);
    set_param([model_name '/OPAMP3_Follower_Stage'], 'Position', [810, 110, 1020, 210]);
    ch3 = sf.find('Path', [model_name '/OPAMP3_Follower_Stage'], '-isa', 'Stateflow.EMChart');
    ch3.Script = sprintf([ ...
        'function [v_opamp_pin, v_ac_coupled] = OPAMP3_Follower_Stage(v_dac_in)\n' ...
        'v_opamp_pin = max(0.0, min(3.3, v_dac_in));\n' ...
        'v_ac_coupled = v_opamp_pin - 1.65;\n' ...
        'end\n']);

    % 5. Sinks: To Workspace Blocks
    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Ideal_Waveform']);
    set_param([model_name '/Log_Ideal_Waveform'], 'VariableName', 'sim_ideal_signal', 'SaveFormat', 'Array', 'Position', [520, 50, 620, 80]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_DAC_Codes']);
    set_param([model_name '/Log_DAC_Codes'], 'VariableName', 'sim_dac_codes', 'SaveFormat', 'Array', 'Position', [810, 50, 910, 80]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_Quant_Error_LSB']);
    set_param([model_name '/Log_Quant_Error_LSB'], 'VariableName', 'sim_quant_err_lsb', 'SaveFormat', 'Array', 'Position', [810, 250, 910, 280]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_V_DAC']);
    set_param([model_name '/Log_V_DAC'], 'VariableName', 'sim_v_dac', 'SaveFormat', 'Array', 'Position', [1080, 110, 1180, 140]);

    add_block('simulink/Sinks/To Workspace', [model_name '/Log_V_AC']);
    set_param([model_name '/Log_V_AC'], 'VariableName', 'sim_v_ac', 'SaveFormat', 'Array', 'Position', [1080, 170, 1180, 200]);

    % 6. Scopes
    add_block('simulink/Sinks/Scope', [model_name '/Scope_Waveform_Detail']);
    set_param([model_name '/Scope_Waveform_Detail'], 'NumInputPorts', '3', 'Position', [520, 260, 570, 310]);

    add_block('simulink/Sinks/Scope', [model_name '/Scope_DAC_Quantization']);
    set_param([model_name '/Scope_DAC_Quantization'], 'NumInputPorts', '2', 'Position', [810, 310, 860, 360]);

    add_block('simulink/Sinks/Scope', [model_name '/Scope_Analog_Output']);
    set_param([model_name '/Scope_Analog_Output'], 'NumInputPorts', '2', 'Position', [1080, 230, 1130, 280]);

    % 7. Wire Connections
    add_line(model_name, 'Selected_Profile_ID/1', 'LFM_Chirp_Synthesizer/1', 'autorouting', 'on');
    add_line(model_name, 'Transmit_Amplitude/1', 'LFM_Chirp_Synthesizer/2', 'autorouting', 'on');
    add_line(model_name, 'Digital_Time_Clock/1', 'LFM_Chirp_Synthesizer/3', 'autorouting', 'on');

    add_line(model_name, 'LFM_Chirp_Synthesizer/1', 'DAC_12Bit_Quantizer/1', 'autorouting', 'on');
    add_line(model_name, 'LFM_Chirp_Synthesizer/1', 'Log_Ideal_Waveform/1', 'autorouting', 'on');
    add_line(model_name, 'LFM_Chirp_Synthesizer/1', 'Scope_Waveform_Detail/1', 'autorouting', 'on');

    add_line(model_name, 'LFM_Chirp_Synthesizer/2', 'Scope_Waveform_Detail/2', 'autorouting', 'on');
    add_line(model_name, 'LFM_Chirp_Synthesizer/3', 'Scope_Waveform_Detail/3', 'autorouting', 'on');

    add_line(model_name, 'DAC_12Bit_Quantizer/1', 'Log_DAC_Codes/1', 'autorouting', 'on');

    add_line(model_name, 'DAC_12Bit_Quantizer/2', 'OPAMP3_Follower_Stage/1', 'autorouting', 'on');
    add_line(model_name, 'DAC_12Bit_Quantizer/2', 'Scope_DAC_Quantization/1', 'autorouting', 'on');

    add_line(model_name, 'DAC_12Bit_Quantizer/3', 'Log_Quant_Error_LSB/1', 'autorouting', 'on');
    add_line(model_name, 'DAC_12Bit_Quantizer/3', 'Scope_DAC_Quantization/2', 'autorouting', 'on');

    add_line(model_name, 'OPAMP3_Follower_Stage/1', 'Log_V_DAC/1', 'autorouting', 'on');
    add_line(model_name, 'OPAMP3_Follower_Stage/1', 'Scope_Analog_Output/1', 'autorouting', 'on');

    add_line(model_name, 'OPAMP3_Follower_Stage/2', 'Log_V_AC/1', 'autorouting', 'on');
    add_line(model_name, 'OPAMP3_Follower_Stage/2', 'Scope_Analog_Output/2', 'autorouting', 'on');

    ann_text = sprintf([ ...
        'SIH Problem 26058: 4.0 MSPS 12-Bit DAC & Waveform Pipeline (Digital Twin)\n' ...
        'Sample Rate: Fs = 4.0 MHz (Ts = 250 ns) | Pulse Duration: Tp = 2.0 ms (8000 Samples)\n' ...
        'Hardware Mapping: STM32G474 DAC3 CH2 -> OPAMP3 High-Speed Follower -> Pin PB1\n' ...
        'Referenced Modules: generate_lfm_chirp.m, dac_quantize.m, profile_definitions.m']);
    an = Simulink.Annotation(model_name, ann_text);
    an.Position = [50, 360];

    save_system(model_name, save_path);
    close_system(model_name);
end

% ==============================================================================
% Model 3 Builder: auv_sonar_payload_top
% ==============================================================================
function build_payload_top(model_name, save_path)
    new_system(model_name);
    load_system(model_name);

    % Master top-level model configuration
    set_param(model_name, 'SolverType', 'Fixed-step');
    set_param(model_name, 'Solver', 'FixedStepDiscrete');
    set_param(model_name, 'FixedStep', 'Ts_ping');
    set_param(model_name, 'StartTime', '0.0');
    set_param(model_name, 'StopTime', 't_mission_end');

    % Robust self-healing callbacks
    cb = get_self_healing_callback();
    set_param(model_name, 'PreLoadFcn', cb);
    set_param(model_name, 'InitFcn', cb);

    % 1. Model Reference: Mission Controller Subsystem
    add_block('simulink/Sources/From Workspace', [model_name '/Turbidity_Plume_NTU']);
    set_param([model_name '/Turbidity_Plume_NTU'], 'VariableName', 'turb_timeseries', ...
              'SampleTime', 'Ts_ping', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value', 'Position', [50, 100, 180, 130]);

    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/Mission_Adaptation_Engine']);
    set_param([model_name '/Mission_Adaptation_Engine'], 'Position', [250, 80, 520, 200]);
    sf = sfroot;
    ch1 = sf.find('Path', [model_name '/Mission_Adaptation_Engine'], '-isa', 'Stateflow.EMChart');
    ch1.Script = sprintf([ ...
        'function [latched_profile_id, transmit_amplitude, Q_score, P_avg_w] = ...\n' ...
        '    Mission_Adaptation_Engine(turbidity_ntu)\n' ...
        'coder.extrinsic(''sim_bridge_channel'', ''sim_bridge_controller'', ''sim_bridge_power'');\n' ...
        'latched_profile_id = 2.0;\n' ...
        'transmit_amplitude = 0.70;\n' ...
        'Q_score = 0.50;\n' ...
        'P_avg_w = 0.30;\n' ...
        '[Q_score, ~, ~, ~, ~, ~] = sim_bridge_channel(turbidity_ntu, 50.0, 20.0, 35.0, 55.0, 50.0, 1.0);\n' ...
        '[latched_profile_id, ~, ~, ~, transmit_amplitude] = sim_bridge_controller(Q_score);\n' ...
        '[P_avg_w, ~, ~, ~] = sim_bridge_power(transmit_amplitude, 0.002);\n' ...
        'end\n']);

    % 2. Subsystem: Waveform LUT & DMA Buffer Mapper
    add_block('simulink/User-Defined Functions/MATLAB Function', [model_name '/DMA_Ping_Buffer_Mapper']);
    set_param([model_name '/DMA_Ping_Buffer_Mapper'], 'Position', [600, 80, 860, 200]);
    ch2 = sf.find('Path', [model_name '/DMA_Ping_Buffer_Mapper'], '-isa', 'Stateflow.EMChart');
    ch2.Script = sprintf([ ...
        'function [lut_id, buffer_bytes, sqnr_db] = DMA_Ping_Buffer_Mapper(profile_id, amp)\n' ...
        'lut_id = double(profile_id);\n' ...
        'buffer_bytes = 16000.0; %% 8000 samples * 2 bytes (uint16)\n' ...
        'sqnr_db = 69.5;\n' ...
        'if profile_id == 1\n' ...
        '    sqnr_db = 70.8;\n' ...
        'elseif profile_id == 3\n' ...
        '    sqnr_db = 68.2;\n' ...
        'end\n' ...
        'end\n']);

    % 3. Sinks: Scopes & Displays
    add_block('simulink/Sinks/Display', [model_name '/Display_Active_Profile']);
    set_param([model_name '/Display_Active_Profile'], 'Position', [940, 50, 1020, 80]);

    add_block('simulink/Sinks/Display', [model_name '/Display_Amplitude']);
    set_param([model_name '/Display_Amplitude'], 'Position', [940, 95, 1020, 125]);

    add_block('simulink/Sinks/Display', [model_name '/Display_Avg_Power_W']);
    set_param([model_name '/Display_Avg_Power_W'], 'Position', [940, 140, 1020, 170]);

    add_block('simulink/Sinks/Display', [model_name '/Display_DMA_Buffer_KB']);
    set_param([model_name '/Display_DMA_Buffer_KB'], 'Position', [940, 185, 1020, 215]);

    add_block('simulink/Sinks/Scope', [model_name '/Scope_Payload_Telemetry']);
    set_param([model_name '/Scope_Payload_Telemetry'], 'NumInputPorts', '4', 'Position', [940, 240, 990, 300]);

    % 4. Wire Connections
    add_line(model_name, 'Turbidity_Plume_NTU/1', 'Mission_Adaptation_Engine/1', 'autorouting', 'on');

    add_line(model_name, 'Mission_Adaptation_Engine/1', 'DMA_Ping_Buffer_Mapper/1', 'autorouting', 'on');
    add_line(model_name, 'Mission_Adaptation_Engine/1', 'Display_Active_Profile/1', 'autorouting', 'on');
    add_line(model_name, 'Mission_Adaptation_Engine/1', 'Scope_Payload_Telemetry/1', 'autorouting', 'on');

    add_line(model_name, 'Mission_Adaptation_Engine/2', 'DMA_Ping_Buffer_Mapper/2', 'autorouting', 'on');
    add_line(model_name, 'Mission_Adaptation_Engine/2', 'Display_Amplitude/1', 'autorouting', 'on');
    add_line(model_name, 'Mission_Adaptation_Engine/2', 'Scope_Payload_Telemetry/2', 'autorouting', 'on');

    add_line(model_name, 'Mission_Adaptation_Engine/3', 'Scope_Payload_Telemetry/3', 'autorouting', 'on');

    add_line(model_name, 'Mission_Adaptation_Engine/4', 'Display_Avg_Power_W/1', 'autorouting', 'on');
    add_line(model_name, 'Mission_Adaptation_Engine/4', 'Scope_Payload_Telemetry/4', 'autorouting', 'on');

    add_line(model_name, 'DMA_Ping_Buffer_Mapper/2', 'Display_DMA_Buffer_KB/1', 'autorouting', 'on');

    ann_text = sprintf([ ...
        '====================================================================================\n' ...
        'SIH Problem 26058: AUV Low-Power Adaptive Sonar Transmitter Payload (Digital Twin)\n' ...
        'Target Hardware: STM32G474RET6 @ 160.0 MHz SYSCLK | DAC Update: 4.0 MSPS (12-bit unsigned)\n' ...
        'Pulse Duration: Tp = 2.0 ms (8000 samples / 16 KB) | PRI: 20.0 ms (50 Hz ping rate, 10%% duty)\n' ...
        'Profiles: 1: LOW_FREQ (100-220kHz, A=1.0) | 2: BALANCED (200-400kHz, A=0.7) | 3: HIGH_FREQ (350-500kHz, A=0.4)\n' ...
        'Hardware Path: DAC3 CH2 (unbuffered) -> OPAMP3 Follower (45 V/us) -> Pin PB1\n' ...
        '[SCOPE]: Validates transmitter payload pipeline only. physically unverified for physical ocean echoes.\n' ...
        '====================================================================================']);
    an = Simulink.Annotation(model_name, ann_text);
    an.Position = [50, 340];

    save_system(model_name, save_path);
    close_system(model_name);
end

% ==============================================================================
% Helper: Close system if already open
% ==============================================================================
function close_if_open(sys_name)
    if bdIsLoaded(sys_name)
        close_system(sys_name, 0);
    end
end
