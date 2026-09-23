% ==============================================================================
% SIH Problem 26058: AUV Sonar Transmitter Digital Twin
%
% File: sim_bridge_controller.m
% Description: Simulink bridge function for Adaptive Controller FSM.
% Directly references and invokes adaptive_controller.m with persistent state.
% ==============================================================================

function [active_id, pending_id, cand_id, debounce_cnt, amp] = sim_bridge_controller(Q_val, reset_flag)
    if nargin < 2
        reset_flag = false;
    end

    persistent state;
    if isempty(state) || reset_flag
        state = struct('active_profile_id', 2, 'pending_profile_id', 2, ...
                       'candidate_profile_id', 2, 'debounce_counter', 0, ...
                       'amplitude', 0.70, 'ping_index', 0, 'time_s', 0.0);
    end

    q_scalar = double(Q_val(1));
    [next_state, ~] = adaptive_controller(q_scalar, state);
    state = next_state;

    active_id = double(state.active_profile_id);
    pending_id = double(state.pending_profile_id);
    cand_id = double(state.candidate_profile_id);
    debounce_cnt = double(state.debounce_counter);
    amp = double(state.amplitude);
end
