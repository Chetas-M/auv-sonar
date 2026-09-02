% ==============================================================================
% File: adaptive_controller.m
% Description: Deterministic threshold-based adaptive decision algorithm with
% Schmitt-trigger hysteresis, debounce persistence, and ping-boundary latching.
% ==============================================================================

function [next_state, decision_log] = adaptive_controller(Q, current_state, cfg)
    if nargin < 3
        cfg = config_sonar();
    end

    % Current latched profile ID: 1 = MUDDY, 2 = BALANCED, 3 = CLEAR
    curr_id = current_state.active_profile_id;
    candidate_id = current_state.candidate_profile_id;
    debounce_count = current_state.debounce_counter;

    % --------------------------------------------------------------------------
    % 1. Schmitt-Trigger Hysteresis State Transition Logic
    % Deadbands: [0.30, 0.40] for Muddy/Balanced; [0.65, 0.75] for Balanced/Clear
    % --------------------------------------------------------------------------
    raw_candidate = curr_id;

    if curr_id == 3 % Currently in Profile 3 (CLEAR)
        if Q < 0.30
            raw_candidate = 1; % Severe drop straight to MUDDY
        elseif Q < 0.65       % Fall below 0.65 (10% deadband below 0.75)
            raw_candidate = 2; % Drop to BALANCED
        else
            raw_candidate = 3; % Stay in CLEAR
        end
    elseif curr_id == 2 % Currently in Profile 2 (BALANCED)
        if Q >= 0.75          % Rise above 0.75 (10% deadband above 0.65)
            raw_candidate = 3; % Transition up to CLEAR
        elseif Q <= 0.30      % Fall below 0.30 (10% deadband below 0.40)
            raw_candidate = 1; % Transition down to MUDDY
        else
            raw_candidate = 2; % Stay in BALANCED (within deadbands)
        end
    elseif curr_id == 1 % Currently in Profile 1 (MUDDY)
        if Q >= 0.75
            raw_candidate = 3; % Huge improvement straight to CLEAR
        elseif Q > 0.40       % Rise above 0.40 (10% deadband above 0.30)
            raw_candidate = 2; % Rise to BALANCED
        else
            raw_candidate = 1; % Stay in MUDDY
        end
    end

    % --------------------------------------------------------------------------
    % 2. Debounce Persistence Filter (Requires N = 2 consecutive cycles)
    % --------------------------------------------------------------------------
    profile_committed = false;
    new_active_id = curr_id;

    if raw_candidate ~= curr_id
        if raw_candidate == candidate_id
            % Candidate condition has persisted
            debounce_count = debounce_count + 1;
        else
            % First observation of a new candidate
            candidate_id = raw_candidate;
            debounce_count = 1;
        end

        % Check if persistence requirement (N = 2) is met
        if debounce_count >= cfg.debounce_count
            new_active_id = raw_candidate;
            debounce_count = 0;
            profile_committed = true;
        end
    else
        % Input remains in current state: reset candidate tracking
        candidate_id = curr_id;
        debounce_count = 0;
    end

    % --------------------------------------------------------------------------
    % 3. Amplitude Scaling (Normalized A in [0.4, 1.0])
    % --------------------------------------------------------------------------
    if new_active_id == 3
        amp = cfg.amp_good;      % 0.40 (Clear channel -> power conservation)
    elseif new_active_id == 2
        amp = cfg.amp_moderate;  % 0.70 (Balanced default)
    else
        amp = cfg.amp_poor;      % 1.00 (Muddy channel -> maximum acoustic energy)
    end

    % --------------------------------------------------------------------------
    % 4. Atomic Ping-Boundary State Packaging
    % --------------------------------------------------------------------------
    next_state = struct();
    next_state.active_profile_id = new_active_id;
    next_state.candidate_profile_id = candidate_id;
    next_state.debounce_counter = debounce_count;
    next_state.amplitude = amp;
    next_state.ping_index = current_state.ping_index + 1;
    next_state.time_s = current_state.time_s + cfg.PRI_s;

    decision_log = struct();
    decision_log.Q = Q;
    decision_log.previous_profile_id = curr_id;
    decision_log.raw_candidate_id = raw_candidate;
    decision_log.active_profile_id = new_active_id;
    decision_log.debounce_counter = debounce_count;
    decision_log.profile_committed = profile_committed;
    decision_log.amplitude = amp;
end
