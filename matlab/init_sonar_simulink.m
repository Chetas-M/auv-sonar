% ==============================================================================
% SIH Problem 26058: AUV Sonar Transmitter Digital Twin
%
% File: init_sonar_simulink.m
% Description: Model initialization and workspace pre-loader for Simulink models.
% Loads system parameters from config_sonar.m and profile_definitions.m,
% sets up simulation time vectors, and creates time-series input signals.
% ==============================================================================

function sim_data = init_sonar_simulink()
    % Ensure parent matlab directory is in MATLAB path
    simulink_dir = fileparts(mfilename('fullpath'));
    matlab_dir = fullfile(simulink_dir, '..');
    addpath(matlab_dir);

    % Load master configuration and profile definitions
    cfg = config_sonar();
    profiles = profile_definitions();

    % Assign into base workspace so Simulink blocks can access them directly
    assignin('base', 'cfg', cfg);
    assignin('base', 'profiles', profiles);

    % --------------------------------------------------------------------------
    % Timing and Sample Rates
    % --------------------------------------------------------------------------
    Ts_ping = cfg.PRI_s;            % Ping-rate controller sample time: 20 ms
    Ts_dac = cfg.Ts;                % High-speed DAC sample time: 250 ns (4 MSPS)
    Tp = cfg.Tp_s;                  % Pulse duration: 2.0 ms
    Np = cfg.Np;                    % Samples per ping: 8000
    num_pings = 150;                % 150 pings for dynamic scenario
    t_mission_end = num_pings * Ts_ping; % 3.0 seconds mission duration

    assignin('base', 'Ts_ping', Ts_ping);
    assignin('base', 'Ts_dac', Ts_dac);
    assignin('base', 'Tp', Tp);
    assignin('base', 'Np', Np);
    assignin('base', 'num_pings', num_pings);
    assignin('base', 't_mission_end', t_mission_end);

    % --------------------------------------------------------------------------
    % Pre-synthesize Baseline LUTs for High-Speed Waveform Subsystem
    % --------------------------------------------------------------------------
    lut_signal_matrix = zeros(Np, 3);
    lut_dac_matrix = zeros(Np, 3, 'uint16');

    for i = 1:3
        p = profiles(i);
        [wf, ~] = generate_lfm_chirp(p.f_start_hz, p.f_end_hz, p.duration_s, cfg.Fs, 1.0);
        [codes, ~] = dac_quantize(wf.signal, cfg);
        lut_signal_matrix(:, i) = wf.signal;
        lut_dac_matrix(:, i) = codes;
    end

    assignin('base', 'lut_signal_matrix', lut_signal_matrix);
    assignin('base', 'lut_dac_matrix', lut_dac_matrix);

    % --------------------------------------------------------------------------
    % Scenario Inputs: 151 time points covering 0 to 3.0 seconds inclusive
    % Matches dynamic turbidity scenario from run_simulation.m
    % --------------------------------------------------------------------------
    t_axis = (0:num_pings)' * Ts_ping;
    turb_base = 15.0 + 75.0 ./ (1.0 + exp(-10.0 * (t_axis - 1.2))) - ...
                45.0 ./ (1.0 + exp(-10.0 * (t_axis - 2.2)));
    rng(42);
    turb_traj = max(0, min(100, turb_base + 3.0 * randn(num_pings + 1, 1)));

    turb_timeseries = timeseries(turb_traj, t_axis);
    assignin('base', 'turb_timeseries', turb_timeseries);

    % Depth trajectory (constant 50 m)
    depth_timeseries = timeseries(50.0 * ones(num_pings + 1, 1), t_axis);
    assignin('base', 'depth_timeseries', depth_timeseries);

    % Temperature trajectory (constant 20.0 C)
    temp_timeseries = timeseries(20.0 * ones(num_pings + 1, 1), t_axis);
    assignin('base', 'temp_timeseries', temp_timeseries);

    % Salinity trajectory (constant 35.0 PSU)
    sal_timeseries = timeseries(35.0 * ones(num_pings + 1, 1), t_axis);
    assignin('base', 'sal_timeseries', sal_timeseries);

    % Ambient Noise trajectory (constant 55.0 dB)
    noise_timeseries = timeseries(55.0 * ones(num_pings + 1, 1), t_axis);
    assignin('base', 'noise_timeseries', noise_timeseries);

    % Target Range trajectory (constant 50.0 m)
    range_timeseries = timeseries(50.0 * ones(num_pings + 1, 1), t_axis);
    assignin('base', 'range_timeseries', range_timeseries);

    % Mission mode: 1 = SURVEY, 2 = DIRECTIVITY, 3 = PENETRATION
    mission_mode_timeseries = timeseries(ones(num_pings + 1, 1), t_axis);
    assignin('base', 'mission_mode_timeseries', mission_mode_timeseries);

    % --------------------------------------------------------------------------
    % Initial Controller State
    % --------------------------------------------------------------------------
    initial_controller_state = struct( ...
        'active_profile_id', 2, ...
        'pending_profile_id', 2, ...
        'candidate_profile_id', 2, ...
        'debounce_counter', 0, ...
        'amplitude', 0.70, ...
        'ping_index', 0, ...
        'time_s', 0.0 ...
    );
    assignin('base', 'initial_controller_state', initial_controller_state);

    % Return summary
    sim_data = struct();
    sim_data.cfg = cfg;
    sim_data.profiles = profiles;
    sim_data.t_axis = t_axis;
    sim_data.turb_traj = turb_traj;
    fprintf('[+] Simulink initialization complete: %d time points (%.1f s duration), Fs_dac = %.1f MHz, PRI = %.1f ms.\n', ...
            num_pings + 1, t_mission_end, cfg.Fs/1e6, Ts_ping*1000);
end
