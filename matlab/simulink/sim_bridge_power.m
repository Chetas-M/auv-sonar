% ==============================================================================
% SIH Problem 26058: AUV Sonar Transmitter Digital Twin
%
% File: sim_bridge_power.m
% Description: Simulink bridge function for Duty-Cycle Power & Battery Life.
% Directly references and invokes power_model.m.
% ==============================================================================

function [P_avg_w, I_avg_ma, endurance_hrs, energy_ping_mj] = sim_bridge_power(amp, Tp_val)
    amp_scalar = double(amp(1));
    tp_scalar = double(Tp_val(1));

    pm = power_model(tp_scalar, amp_scalar);

    P_avg_w = double(pm.average_power_w);
    I_avg_ma = double(pm.average_current_ma);
    endurance_hrs = double(pm.transmitter_alone_endurance_hours);
    energy_ping_mj = double(pm.energy_per_ping_mj);
end
