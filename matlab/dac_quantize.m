% ==============================================================================
% File: dac_quantize.m
% Description: 12-bit unsigned DAC quantization model (0 to 4095) with SQNR analysis.
% ==============================================================================

function [dac_codes, quant_metrics] = dac_quantize(normalized_signal, cfg)
    if nargin < 2
        cfg = config_sonar();
    end

    % Verify input is bounded within [-1.0, 1.0]
    peak_in = max(abs(normalized_signal));
    if peak_in > 1.0001
        warning('Input signal exceeds [-1.0, 1.0], clipping applied.');
    end
    clipped_in = max(-1.0, min(1.0, normalized_signal));

    % Continuous ideal DAC representation centered at midscale (2048)
    % Peak swing spans [0.0, 4095.0]
    dac_scale = 2047.5;
    dac_mid = 2047.5;
    dac_ideal = dac_mid + (dac_scale .* clipped_in);

    % 12-bit Integer Quantization: standard rounding and clipping [0, 4095]
    dac_rounded = round(dac_ideal);
    dac_clamped = max(cfg.DAC_min_code, min(cfg.DAC_max_code, dac_rounded));

    % Convert to uint16 array for embedded compatibility
    dac_codes = uint16(dac_clamped);

    % Quantization error in LSBs: e[n] = quantized - ideal
    quant_error_lsb = double(dac_codes) - dac_ideal;

    % Quantization error in physical millivolts on 3.3V reference
    lsb_mv = (cfg.DAC_vref / double(cfg.DAC_max_code)) * 1000.0; % ~0.806 mV
    quant_error_mv = quant_error_lsb * lsb_mv;

    % Empirical Signal-to-Quantization-Noise Ratio (SQNR in dB)
    signal_power = mean((dac_ideal - dac_mid) .^ 2);
    noise_power = mean(quant_error_lsb .^ 2);
    if noise_power <= 1e-12
        sqnr_db = 120.0;
    else
        sqnr_db = 10.0 * log10(signal_power / noise_power);
    end

    % Compile quantization metrics
    quant_metrics = struct();
    quant_metrics.dac_ideal = dac_ideal;
    quant_metrics.quant_error_lsb = quant_error_lsb;
    quant_metrics.quant_error_mv = quant_error_mv;
    quant_metrics.max_error_lsb = max(abs(quant_error_lsb));
    quant_metrics.mean_error_lsb = mean(quant_error_lsb);
    quant_metrics.variance_error_lsb = var(quant_error_lsb);
    quant_metrics.sqnr_db = sqnr_db;
    quant_metrics.theoretical_sine_sqnr_db = 6.02 * cfg.DAC_bits + 1.76; % 74.0 dB
    quant_metrics.has_overflow = any(dac_rounded > cfg.DAC_max_code);
    quant_metrics.has_underflow = any(dac_rounded < cfg.DAC_min_code);
    quant_metrics.lsb_mv = lsb_mv;
end
