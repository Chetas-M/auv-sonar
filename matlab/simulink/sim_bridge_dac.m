% ==============================================================================
% SIH Problem 26058: AUV Sonar Transmitter Digital Twin
%
% File: sim_bridge_dac.m
% Description: Simulink bridge function for 12-Bit DAC Quantization.
% Directly references and invokes dac_quantize.m.
% ==============================================================================

function [dac_code, v_dac_volts, quant_error_lsb, quant_error_mv] = sim_bridge_dac(x_in)
    x_val = double(x_in(1));

    % Invoke repository dac_quantize.m
    [codes, qm] = dac_quantize(x_val);

    dac_code = double(codes(1));
    v_dac_volts = double(codes(1)) * (3.3 / 4095.0);
    quant_error_lsb = double(qm.quant_error_lsb(1));
    quant_error_mv = double(qm.quant_error_mv(1));
end
