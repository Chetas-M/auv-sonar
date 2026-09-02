% ==============================================================================
% File: adaptive_controller.m
% Description: Deterministic finite-state controller with directional Schmitt-trigger
% hysteresis, N=2 debounce persistence, and atomic ping-boundary profile latching.
%
% State Variables Maintained:
%   - active_profile_id:    Currently transmitting profile (latched at ping start)
%   - pending_profile_id:   Committed candidate waiting for next ping boundary
%   - candidate_profile_id: Current raw candidate under evaluation
%   - debounce_counter:     Number of consecutive evaluation cycles candidate has held
% ==============================================================================

function [next_state, decision_log] = adaptive_controller(Q, current_state, cfg)
    if nargin < 3
        cfg = config_sonar();
    end

    % Extract current state variables
    active_id = current_state.active_profile_id;
    pending_id = current_state.pending_profile_id;
    candidate_id = current_state.candidate_profile_id;
    debounce_count = current_state.debounce_counter;

    % --------------------------------------------------------------------------
    % 1. Directional Schmitt-Trigger Hysteresis Logic
    % Profile 1 = LOW_FREQUENCY, Profile 2 = BALANCED, Profile 3 = HIGH_FREQUENCY
    % --------------------------------------------------------------------------
    raw_candidate = pending_id;

    if pending_id == 3 % Currently in Profile 3 (HIGH_FREQUENCY)
        if Q <= cfg.thresh_bal_to_low
            raw_candidate = 1; % Severe degradation straight to LOW_FREQUENCY
        elseif Q < cfg.thresh_high_to_bal % Fall below 0.65 (lower threshold)
            raw_candidate = 2; % Drop down to BALANCED
        else
            raw_candidate = 3; % Maintain HIGH_FREQUENCY
        end
    elseif pending_id == 2 % Currently in Profile 2 (BALANCED)
        if Q >= cfg.thresh_bal_to_high % Rise above 0.75 (upper threshold)
            raw_candidate = 3; % Promote to HIGH_FREQUENCY
        elseif Q <= cfg.thresh_bal_to_low % Fall below 0.30 (lower threshold)
            raw_candidate = 1; % Demote to LOW_FREQUENCY
        else
            raw_candidate = 2; % Maintain BALANCED (within deadband)
        end
    elseif pending_id == 1 % Currently in Profile 1 (LOW_FREQUENCY)
        if Q >= cfg.thresh_bal_to_high
            raw_candidate = 3; % Direct improvement straight to HIGH_FREQUENCY
        elseif Q > cfg.thresh_low_to_bal % Rise above 0.40 (upper threshold)
            raw_candidate = 2; % Promote to BALANCED
        else
            raw_candidate = 1; % Maintain LOW_FREQUENCY
        end
    end

    % --------------------------------------------------------------------------
    % 2. Debounce Persistence Filter (Requires N = 2 consecutive evaluations)
    % --------------------------------------------------------------------------
    new_pending_id = pending_id;
    debounce_committed = false;

    if raw_candidate ~= pending_id
        if raw_candidate == candidate_id
            % Candidate condition has persisted for another cycle
            debounce_count = debounce_count + 1;
        else
            % First observation of a new candidate condition
            candidate_id = raw_candidate;
            debounce_count = 1;
        end

        % If candidate persists for required debounce cycles (N = 2), commit to pending
        if debounce_count >= cfg.debounce_count
            new_pending_id = candidate_id;
            debounce_count = 0;
            debounce_committed = true;
        end
    else
        % Input matches pending state: clear candidate counter
        candidate_id = pending_id;
        debounce_count = 0;
    end

    % --------------------------------------------------------------------------
    % 3. Amplitude Policy (0 < A <= 1)
    % --------------------------------------------------------------------------
    if new_pending_id == 3
        amp = cfg.amp_high;      % 0.40 (High frequency -> low power / prevent clipping)
    elseif new_pending_id == 2
        amp = cfg.amp_balanced;  % 0.70 (Balanced default)
    else
        amp = cfg.amp_low;       % 1.00 (Low frequency -> maximum penetration)
    end

    % --------------------------------------------------------------------------
    % 4. Atomic Ping-Boundary Latching
    % Active profile CANNOT change mid-ping; it latches from pending at ping start.
    % --------------------------------------------------------------------------
    % Default: at next ping start, active_profile latches pending_profile
    new_active_id = new_pending_id;

    next_state = struct();
    next_state.active_profile_id = new_active_id;
    next_state.pending_profile_id = new_pending_id;
    next_state.candidate_profile_id = candidate_id;
    next_state.debounce_counter = debounce_count;
    next_state.amplitude = amp;
    next_state.ping_index = current_state.ping_index + 1;
    next_state.time_s = current_state.time_s + cfg.PRI_s;

    % Detailed decision logging
    decision_log = struct();
    decision_log.Q = Q;
    decision_log.raw_candidate_id = raw_candidate;
    decision_log.candidate_profile_id = candidate_id;
    decision_log.debounce_counter = debounce_count;
    decision_log.pending_profile_id = new_pending_id;
    decision_log.active_profile_id = new_active_id;
    decision_log.debounce_committed = debounce_committed;
    decision_log.amplitude = amp;
end
