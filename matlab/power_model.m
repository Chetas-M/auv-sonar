% ==============================================================================
% File: power_model.m
% Description: Duty-cycle and amplitude-dependent average power estimator.
%
% IMPORTANT DISCLAIMER:
% Power figures are simulation estimates for the modeled transmitter payload load
% alone against a hypothetical 99 Wh pack. They do not represent full AUV
% mission life (which is dominated by thrusters, compute, sensors, and comms)
% and do not constitute bench measurement proof of physical power draw.
% ==============================================================================

function metrics = power_model(duration_s, amplitude, cfg)
    if nargin < 3
        cfg = config_sonar();
    end
    if nargin < 2
        amplitude = 1.0;
    end
    if nargin < 1
        duration_s = cfg.Tp_s;
    end

    % 1. Duty cycle calculation
    duty_cycle = duration_s / cfg.PRI_s;

    % 2. Effective active power modeling:
    % Constant electronic baseline overhead (MCU + DAC + OpAmp) ~ 0.30 W
    % Remainder is Power Amplifier (PA) driving transducer, scaling with A^2
    elec_overhead_w = 0.30;
    pa_max_w = max(0.0, cfg.P_active_w - elec_overhead_w);
    effective_active_w = elec_overhead_w + pa_max_w * (amplitude ^ 2);

    % 3. Average power across PRI
    % P_avg = P_active * D + P_idle * (1 - D)
    p_avg_w = (effective_active_w * duty_cycle) + (cfg.P_idle_w * (1.0 - duty_cycle));

    % 4. Average current drawn from 12V battery rail
    i_avg_ma = (p_avg_w / cfg.V_battery_v) * 1000.0;

    % 5. Theoretical transmitter-only battery endurance on hypothetical 99 Wh pack
    if p_avg_w > 0
        endurance_hours = cfg.battery_capacity_wh / p_avg_w;
    else
        endurance_hours = 0.0;
    end

    % 6. Energy consumed per ping (mJ)
    energy_per_ping_mj = ((effective_active_w * duration_s) + ...
                          (cfg.P_idle_w * (cfg.PRI_s - duration_s))) * 1000.0;

    % Output struct
    metrics = struct();
    metrics.pulse_duration_ms = duration_s * 1000.0;
    metrics.pri_ms = cfg.PRI_s * 1000.0;
    metrics.duty_cycle_pct = duty_cycle * 100.0;
    metrics.amplitude = amplitude;
    metrics.effective_active_power_w = effective_active_w;
    metrics.idle_power_w = cfg.P_idle_w;
    metrics.average_power_w = p_avg_w;
    metrics.average_current_ma = i_avg_ma;
    metrics.battery_voltage_v = cfg.V_battery_v;
    metrics.transmitter_alone_endurance_hours = endurance_hours;
    metrics.energy_per_ping_mj = energy_per_ping_mj;
end
