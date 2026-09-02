"""
Waveform generation and DAC quantization pipeline for sonar transmitter.
Implements LFM chirp synthesis via phase integration, spectral windowing,
and 12-bit DAC quantization modeling.
"""

from dataclasses import dataclass
from typing import Optional, Literal
import numpy as np
from .config import (
    DAC_SAMPLE_RATE_HZ,
    DAC_MIN_CODE,
    DAC_MAX_CODE,
    DAC_MIDSCALE_CODE,
    DAC_VREF_VOLTS,
)


@dataclass
class Waveform:
    """Container for synthesized sonar waveform data and quantization metrics."""
    time_s: np.ndarray             # Time array in seconds [0, T]
    ideal_signal: np.ndarray       # Continuous windowed signal in [-1.0, 1.0]
    window: np.ndarray             # Tapering window weights [0, 1]
    dac_ideal_codes: np.ndarray    # Continuous ideal DAC codes [0.0, 4095.0]
    dac_codes: np.ndarray          # Quantized 12-bit uint16 DAC codes [0, 4095]
    quant_error_lsb: np.ndarray    # Quantization error in LSBs
    f_start_hz: float
    f_end_hz: float
    duration_s: float
    sample_rate_hz: int
    amplitude_factor: float
    window_type: str

    @property
    def sample_count(self) -> int:
        return len(self.dac_codes)

    @property
    def sqnr_db(self) -> float:
        """Signal-to-Quantization-Noise Ratio (SQNR) in decibels."""
        signal_power = np.mean((self.dac_ideal_codes - DAC_MIDSCALE_CODE) ** 2)
        noise_power = np.mean(self.quant_error_lsb ** 2)
        if noise_power <= 1e-15:
            return 120.0
        return float(10.0 * np.log10(signal_power / noise_power))

    @property
    def max_quant_error_lsb(self) -> float:
        return float(np.max(np.abs(self.quant_error_lsb)))

    @property
    def mean_quant_error_lsb(self) -> float:
        return float(np.mean(self.quant_error_lsb))

    @property
    def chirp_rate_hz_per_s(self) -> float:
        return (self.f_end_hz - self.f_start_hz) / self.duration_s

    @property
    def voltage_ideal(self) -> np.ndarray:
        """Analog output voltage estimate in Volts (0 to VREF)."""
        return (self.dac_codes / DAC_MAX_CODE) * DAC_VREF_VOLTS


def generate_lfm_chirp(
    f_start_hz: float,
    f_end_hz: float,
    duration_s: float,
    sample_rate_hz: int = DAC_SAMPLE_RATE_HZ,
    amplitude_factor: float = 1.0,
    window_type: Literal["hann", "hamming", "rectangular"] = "hann",
) -> Waveform:
    """
    Generate an LFM chirp using exact phase integration:
        phase(t) = 2*pi*(f_start*t + 0.5*k*t^2)
        k = (f_end - f_start) / duration_s
    
    Applies amplitude scaling and smoothing window, then quantizes to 12-bit DAC codes.

    Args:
        f_start_hz: Starting sweep frequency in Hz.
        f_end_hz: Ending sweep frequency in Hz.
        duration_s: Pulse duration in seconds (e.g. 0.002 s).
        sample_rate_hz: DAC sample rate in Hz (default 4 MHz).
        amplitude_factor: Linear amplitude factor [0.0, 1.0].
        window_type: 'hann', 'hamming', or 'rectangular'.

    Returns:
        Waveform instance with time, ideal, and quantized signals.
    """
    if duration_s <= 0:
        raise ValueError(f"Pulse duration must be > 0, got {duration_s}")
    if sample_rate_hz <= 0:
        raise ValueError(f"Sample rate must be > 0, got {sample_rate_hz}")
    amplitude_factor = max(0.0, min(1.0, float(amplitude_factor)))

    num_samples = int(round(duration_s * sample_rate_hz))
    # Discrete time points t_n = n / Fs for n = 0, ..., N-1
    t = np.arange(num_samples, dtype=np.float64) / sample_rate_hz

    # Chirp sweep rate k = delta_f / T
    k = (f_end_hz - f_start_hz) / duration_s

    # Instantaneous phase via analytical integration:
    # phase(t) = 2*pi * integral_0^t (f_start + k*tau) dtau = 2*pi * (f_start*t + 0.5*k*t^2)
    phase = 2.0 * np.pi * (f_start_hz * t + 0.5 * k * (t ** 2))

    # Raw carrier sinusoid
    raw_carrier = np.cos(phase)

    # Window generation to prevent spectral splatter and turn-on transients
    if window_type == "hann":
        # Hann window: 0.5 * (1 - cos(2*pi*n / (N - 1)))
        window = np.hanning(num_samples)
    elif window_type == "hamming":
        window = np.hamming(num_samples)
    elif window_type == "rectangular":
        window = np.ones(num_samples, dtype=np.float64)
    else:
        raise ValueError(f"Unsupported window type '{window_type}'")

    # Scaled ideal continuous signal in [-1.0, 1.0]
    ideal_signal = amplitude_factor * raw_carrier * window

    # Map to 12-bit DAC code space [0, 4095]
    # Midscale is 2048. Peak swing is +/- 2047.5.
    # dac_ideal = 2047.5 + 2047.5 * ideal_signal
    dac_scale = 2047.5
    dac_mid = 2047.5
    dac_ideal = dac_mid + (dac_scale * ideal_signal)

    # 12-bit integer quantization (round half away from zero / standard round + clip)
    dac_quantized = np.clip(np.round(dac_ideal), DAC_MIN_CODE, DAC_MAX_CODE).astype(np.uint16)

    # Quantization error residual (in LSB units)
    quant_error = dac_quantized.astype(np.float64) - dac_ideal

    return Waveform(
        time_s=t,
        ideal_signal=ideal_signal,
        window=window,
        dac_ideal_codes=dac_ideal,
        dac_codes=dac_quantized,
        quant_error_lsb=quant_error,
        f_start_hz=f_start_hz,
        f_end_hz=f_end_hz,
        duration_s=duration_s,
        sample_rate_hz=sample_rate_hz,
        amplitude_factor=amplitude_factor,
        window_type=window_type,
    )
