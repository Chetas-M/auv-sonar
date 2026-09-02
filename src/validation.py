"""
Signal validation and visualization suite for AUV sonar transmitter digital twin.
Generates publication-quality validation plots:
1. Single pulse time-domain waveform (ideal vs quantized, Hann window envelope).
2. FFT magnitude spectrum (occupied band, in-band flatness, out-of-band rejection).
3. Spectrogram (STFT time-frequency linear chirp trajectory).
4. DAC quantization error and residual analysis (LSB error, SQNR distribution).
5. Dynamic multi-ping simulation timeline (analog inputs, profile switching, power).
6. Cross-profile comparative analysis (Muddy vs Balanced vs Clear).
"""

import os
from typing import List, Dict, Tuple, Any
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Headless rendering
import matplotlib.pyplot as plt
from scipy import signal

from .waveform import Waveform
from .profiles import BAND_PROFILES, TurbidityProfileType
from .config import DAC_SAMPLE_RATE_HZ, NYQUIST_LIMIT_HZ, DAC_MIDSCALE_CODE, DAC_MAX_CODE


# Styling configuration
PALETTE = {
    "bg_dark": "#0d1b2a",
    "card_bg": "#1b263b",
    "cyan": "#00b4d8",
    "teal": "#48cae4",
    "orange": "#f77f00",
    "green": "#06d6a0",
    "red": "#ef476f",
    "yellow": "#ffd166",
    "purple": "#9d4edd",
    "text": "#e0e1dd",
    "grid": "#415a77",
}


def apply_custom_style(ax: plt.Axes) -> None:
    """Applies a clean engineering dark-navy aesthetic to an Axes."""
    ax.set_facecolor(PALETTE["card_bg"])
    ax.grid(True, color=PALETTE["grid"], linestyle="--", linewidth=0.5, alpha=0.5)
    ax.tick_params(colors=PALETTE["text"], labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(PALETTE["grid"])
        spine.set_linewidth(0.8)
    ax.xaxis.label.set_color(PALETTE["text"])
    ax.yaxis.label.set_color(PALETTE["text"])
    ax.title.set_color(PALETTE["text"])


def plot_single_pulse_analysis(
    waveform: Waveform,
    output_path: str,
    profile_title: str = "Balanced Profile (200-400 kHz)",
) -> None:
    """
    Creates a comprehensive 4-panel figure for a single chirp pulse:
    - Time-domain waveform with envelope
    - Zoomed-in view showing 12-bit DAC stair-step quantization
    - Power spectral density / FFT magnitude spectrum
    - Spectrogram showing linear frequency modulation slope
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig = plt.figure(figsize=(14, 10), facecolor=PALETTE["bg_dark"])

    t_ms = waveform.time_s * 1000.0  # ms
    N = waveform.sample_count
    fs = waveform.sample_rate_hz

    # 1. Full Time Domain with Envelope (Top-Left)
    ax1 = fig.add_subplot(2, 2, 1)
    apply_custom_style(ax1)
    ax1.plot(t_ms, waveform.ideal_signal, color=PALETTE["cyan"], lw=0.8, label="LFM Chirp Signal")
    ax1.plot(t_ms, waveform.window * waveform.amplitude_factor, color=PALETTE["orange"], lw=1.5, ls="--", label=f"{waveform.window_type.capitalize()} Envelope")
    ax1.plot(t_ms, -waveform.window * waveform.amplitude_factor, color=PALETTE["orange"], lw=1.5, ls="--")
    ax1.set_title(f"{profile_title} - Time-Domain Pulse ({waveform.duration_s * 1e3:.1f} ms, N={N})", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Time (ms)")
    ax1.set_ylabel("Normalized Amplitude")
    ax1.set_ylim(-1.15, 1.15)
    ax1.legend(loc="upper right", facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"], fontsize=8)

    # 2. Zoomed-in DAC Quantization (Top-Right)
    ax2 = fig.add_subplot(2, 2, 2)
    apply_custom_style(ax2)
    # Zoom in on center 20 microseconds
    t_center_idx = N // 2
    window_samples = 80  # 80 samples @ 4 MSPS = 20 microseconds = ~6-8 chirp cycles
    idx_start = max(0, t_center_idx - window_samples // 2)
    idx_end = min(N, idx_start + window_samples)
    t_zoom_us = (waveform.time_s[idx_start:idx_end] - waveform.time_s[idx_start]) * 1e6

    ax2.plot(t_zoom_us, waveform.dac_ideal_codes[idx_start:idx_end], color=PALETTE["cyan"], lw=1.5, label="Ideal Continuous (Codes)")
    ax2.step(t_zoom_us, waveform.dac_codes[idx_start:idx_end], where="mid", color=PALETTE["yellow"], lw=1.2, label="12-bit Quantized DAC")
    ax2.set_title(f"DAC Quantization Detail (Center 20 µs, SQNR = {waveform.sqnr_db:.1f} dB)", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Time (µs)")
    ax2.set_ylabel("12-bit DAC Code (0 - 4095)")
    ax2.legend(loc="upper right", facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"], fontsize=8)

    # 3. FFT Magnitude Spectrum (Bottom-Left)
    ax3 = fig.add_subplot(2, 2, 3)
    apply_custom_style(ax3)
    # Windowed FFT with zero-padding for smooth spectrum
    n_fft = int(2 ** np.ceil(np.log2(N * 4)))
    fft_vals = np.fft.rfft(waveform.ideal_signal, n=n_fft)
    fft_freqs_khz = np.fft.rfftfreq(n_fft, d=1.0 / fs) / 1000.0  # kHz
    fft_mag_db = 20.0 * np.log10(np.abs(fft_vals) / (np.max(np.abs(fft_vals)) + 1e-12))

    ax3.plot(fft_freqs_khz, fft_mag_db, color=PALETTE["green"], lw=1.0, label="Chirp Spectrum")
    # Mark nominal chirp limits
    ax3.axvline(waveform.f_start_hz / 1000.0, color=PALETTE["yellow"], ls=":", lw=1.2, label=f"f_start ({waveform.f_start_hz/1e3:.0f} kHz)")
    ax3.axvline(waveform.f_end_hz / 1000.0, color=PALETTE["orange"], ls=":", lw=1.2, label=f"f_end ({waveform.f_end_hz/1e3:.0f} kHz)")
    ax3.set_xlim(0, min(1000.0, (NYQUIST_LIMIT_HZ / 1000.0)))
    ax3.set_ylim(-65, 5)
    ax3.set_title(f"FFT Spectrum (Occupied Band: {waveform.f_start_hz/1e3:.0f} - {waveform.f_end_hz/1e3:.0f} kHz)", fontsize=11, fontweight="bold")
    ax3.set_xlabel("Frequency (kHz)")
    ax3.set_ylabel("Normalized Magnitude (dB)")
    ax3.legend(loc="upper right", facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"], fontsize=8)

    # 4. Spectrogram (Bottom-Right)
    ax4 = fig.add_subplot(2, 2, 4)
    apply_custom_style(ax4)
    nperseg = min(256, N // 8)
    noverlap = nperseg * 3 // 4
    freqs_spec, times_spec, Sxx = signal.spectrogram(
        waveform.ideal_signal,
        fs=fs,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        scaling="density"
    )
    freqs_spec_khz = freqs_spec / 1000.0
    times_spec_ms = times_spec * 1000.0
    Sxx_db = 10.0 * np.log10(Sxx + 1e-12)
    Sxx_db -= np.max(Sxx_db)

    # Crop to 0-600 kHz
    mask = freqs_spec_khz <= 600.0
    im = ax4.pcolormesh(
        times_spec_ms,
        freqs_spec_khz[mask],
        Sxx_db[mask, :],
        shading="gouraud",
        cmap="magma",
        vmin=-50,
        vmax=0,
    )
    cbar = fig.colorbar(im, ax=ax4, pad=0.02)
    cbar.ax.tick_params(colors=PALETTE["text"], labelsize=8)
    cbar.set_label("Power Spectral Density (dB/Hz)", color=PALETTE["text"], fontsize=8)
    ax4.set_title("Spectrogram (Linear Frequency Modulation Slope)", fontsize=11, fontweight="bold")
    ax4.set_xlabel("Time (ms)")
    ax4.set_ylabel("Frequency (kHz)")

    plt.tight_layout()
    fig.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)


def plot_quantization_analysis(waveform: Waveform, output_path: str) -> None:
    """
    Detailed figure analyzing 12-bit DAC quantization behavior:
    - Quantization error time series (LSBs)
    - Error distribution histogram with normal and uniform comparison
    - Residual voltage error (mV)
    - SQNR vs theoretical limits
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig = plt.figure(figsize=(13, 8), facecolor=PALETTE["bg_dark"])

    t_ms = waveform.time_s * 1000.0
    errors = waveform.quant_error_lsb
    volt_err_mv = (errors / DAC_MAX_CODE) * 3300.0  # 3.3V full scale in mV

    # 1. Error time series
    ax1 = fig.add_subplot(2, 2, 1)
    apply_custom_style(ax1)
    # Plot a representative sample subset for clarity
    sample_sub = slice(0, min(1000, len(errors)))
    ax1.plot(t_ms[sample_sub], errors[sample_sub], color=PALETTE["yellow"], lw=0.7, alpha=0.9)
    ax1.axhline(0.5, color=PALETTE["red"], ls="--", lw=1.0, label="+0.5 LSB Limit")
    ax1.axhline(-0.5, color=PALETTE["red"], ls="--", lw=1.0, label="-0.5 LSB Limit")
    ax1.set_title("Quantization Error vs Time (First 1,000 Samples)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Time (ms)")
    ax1.set_ylabel("Error (LSB)")
    ax1.set_ylim(-0.7, 0.7)
    ax1.legend(loc="upper right", facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"], fontsize=8)

    # 2. Error Histogram
    ax2 = fig.add_subplot(2, 2, 2)
    apply_custom_style(ax2)
    n_bins = 31
    counts, bins, _ = ax2.hist(errors, bins=n_bins, range=(-0.6, 0.6), density=True, color=PALETTE["cyan"], alpha=0.75, edgecolor=PALETTE["bg_dark"])
    ax2.axvline(0.0, color=PALETTE["orange"], ls="-", lw=1.2, label=f"Mean: {np.mean(errors):+.4f} LSB")
    ax2.set_title(f"Quantization Error Distribution (RMS: {np.std(errors):.3f} LSB)", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Error (LSB)")
    ax2.set_ylabel("Probability Density")
    ax2.legend(loc="upper right", facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"], fontsize=8)

    # 3. Voltage error in millivolts
    ax3 = fig.add_subplot(2, 2, 3)
    apply_custom_style(ax3)
    ax3.plot(t_ms[sample_sub], volt_err_mv[sample_sub], color=PALETTE["green"], lw=0.7)
    lsb_mv = (1.0 / DAC_MAX_CODE) * 3300.0  # ~0.806 mV
    ax3.axhline(lsb_mv / 2.0, color=PALETTE["red"], ls="--", lw=1.0, label=f"+0.5 LSB (+{lsb_mv/2.0:.2f} mV)")
    ax3.axhline(-lsb_mv / 2.0, color=PALETTE["red"], ls="--", lw=1.0, label=f"-0.5 LSB (-{lsb_mv/2.0:.2f} mV)")
    ax3.set_title(f"Output Voltage Residual Error (1 LSB ≈ {lsb_mv:.3f} mV)", fontsize=11, fontweight="bold")
    ax3.set_xlabel("Time (ms)")
    ax3.set_ylabel("Voltage Error (mV)")
    ax3.set_ylim(-lsb_mv * 0.8, lsb_mv * 0.8)
    ax3.legend(loc="upper right", facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"], fontsize=8)

    # 4. SQNR Performance Card
    ax4 = fig.add_subplot(2, 2, 4)
    apply_custom_style(ax4)
    ax4.axis("off")

    theory_sqnr = 6.02 * 12 + 1.76  # ~74.0 dB for full-scale sine
    sim_sqnr = waveform.sqnr_db
    text_info = (
        f"12-BIT DAC QUANTIZATION METRICS\n"
        f"----------------------------------------\n"
        f"• DAC Resolution:         12-Bit Unsigned\n"
        f"• Code Range:             0 to 4095 (Midscale: {DAC_MIDSCALE_CODE})\n"
        f"• Reference Voltage:      3.300 V\n"
        f"• LSB Weight:             {lsb_mv:.3f} mV\n"
        f"• Max Quantization Error: {waveform.max_quant_error_lsb:.3f} LSB\n"
        f"• Mean Quantization Error:{waveform.mean_quant_error_lsb:+.4f} LSB\n"
        f"• Error Variance (sigma2):{np.var(errors):.4f} (Ideal: 1/12 = 0.0833)\n\n"
        f"SIGNAL-TO-QUANTIZATION-NOISE RATIO:\n"
        f"• Theoretical Sine SQNR:  {theory_sqnr:.2f} dB\n"
        f"• Empirical Waveform SQNR:{sim_sqnr:.2f} dB\n"
        f"• Window Attenuation Delta: {abs(theory_sqnr - sim_sqnr):.2f} dB\n\n"
        f"CONCLUSION:\n"
        f"Simulated quantization noise is ~70 dB below carrier,\n"
        f"confirming low digital math distortion. Physical analog\n"
        f"harmonic distortion, slew rate, and settling must be\n"
        f"validated on oscilloscope and bench spectrum analyzer."
    )
    ax4.text(
        0.05, 0.95, text_info,
        transform=ax4.transAxes,
        fontsize=9.5,
        verticalalignment="top",
        fontfamily="monospace",
        color=PALETTE["text"],
        bbox=dict(boxstyle="round,pad=0.8", facecolor=PALETTE["card_bg"], edgecolor=PALETTE["cyan"], lw=1.2)
    )

    plt.tight_layout()
    fig.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)


def plot_profile_comparison(
    waveforms: Dict[TurbidityProfileType, Waveform],
    output_path: str,
) -> None:
    """
    Compares the 3 primary operational band profiles (Muddy, Balanced, Clear)
    side by side in time domain and spectral domain.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig, axes = plt.subplots(2, 1, figsize=(13, 8), facecolor=PALETTE["bg_dark"])

    colors = {
        TurbidityProfileType.MUDDY: PALETTE["orange"],
        TurbidityProfileType.BALANCED: PALETTE["cyan"],
        TurbidityProfileType.CLEAR: PALETTE["green"],
    }

    # 1. Time domain comparison (zoom in to first 0.2 ms to see frequency differences)
    ax1 = axes[0]
    apply_custom_style(ax1)
    for p_type, wf in waveforms.items():
        sub_samples = int(0.00025 * wf.sample_rate_hz)  # 250 us
        t_us = wf.time_s[:sub_samples] * 1e6
        ax1.plot(
            t_us,
            wf.ideal_signal[:sub_samples],
            label=f"{p_type.value} ({wf.f_start_hz/1e3:.0f}-{wf.f_end_hz/1e3:.0f} kHz)",
            color=colors[p_type],
            lw=1.2,
            alpha=0.85
        )
    ax1.set_title("Time-Domain Waveform Comparison (First 250 µs of Pulse)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Time (µs)")
    ax1.set_ylabel("Normalized Amplitude")
    ax1.legend(loc="upper right", facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"])

    # 2. Spectral overlay comparison
    ax2 = axes[1]
    apply_custom_style(ax2)
    for p_type, wf in waveforms.items():
        n_fft = int(2 ** np.ceil(np.log2(wf.sample_count * 4)))
        fft_vals = np.fft.rfft(wf.ideal_signal, n=n_fft)
        fft_freqs_khz = np.fft.rfftfreq(n_fft, d=1.0 / wf.sample_rate_hz) / 1000.0
        fft_mag_db = 20.0 * np.log10(np.abs(fft_vals) / (np.max(np.abs(fft_vals)) + 1e-12))
        ax2.plot(
            fft_freqs_khz,
            fft_mag_db,
            label=f"{p_type.value} Band ({wf.f_start_hz/1e3:.0f} - {wf.f_end_hz/1e3:.0f} kHz)",
            color=colors[p_type],
            lw=1.3,
            alpha=0.9
        )
    ax2.set_xlim(50, 600)
    ax2.set_ylim(-60, 5)
    ax2.set_title("Spectral Comparison Across Environmental Adaptation Profiles", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Frequency (kHz)")
    ax2.set_ylabel("Normalized Magnitude (dB)")
    ax2.legend(loc="upper right", facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"])

    plt.tight_layout()
    fig.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)


def plot_dynamic_simulation_timeline(
    history: List[Dict],
    output_path: str,
) -> None:
    """
    Plots a multi-ping real-time mission simulation timeline:
    - Simulated analog potentiometer inputs (turbidity, range, target strength)
    - Latched discrete profile states over time
    - Pulse duration and memory footprint over time
    - Instantaneous duty cycle and average power dissipation
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig, axes = plt.subplots(4, 1, figsize=(14, 11), sharex=True, facecolor=PALETTE["bg_dark"])

    pings = [h["ping_index"] for h in history]
    times_s = [h["start_time_s"] for h in history]

    turb_in = [h["inputs"].turbidity for h in history]
    range_in = [h["inputs"].range_depth for h in history]
    target_in = [h["inputs"].target_strength for h in history]

    # Map profile strings to numeric levels for plotting
    band_level = [{"MUDDY": 2, "BALANCED": 1, "CLEAR": 0}[h["state"].band.value] for h in history]
    dur_ms = [h["state"].pulse_duration_s * 1000.0 for h in history]
    amp_fact = [h["state"].amplitude_factor for h in history]
    avg_power = [h["power"].average_power_w for h in history]
    duty_pct = [h["power"].duty_cycle_pct for h in history]

    # 1. Analog Inputs
    ax1 = axes[0]
    apply_custom_style(ax1)
    ax1.plot(times_s, turb_in, color=PALETTE["orange"], lw=1.5, label="Turbidity Potentiometer")
    ax1.plot(times_s, range_in, color=PALETTE["cyan"], lw=1.5, label="Range/Depth Potentiometer")
    ax1.plot(times_s, target_in, color=PALETTE["green"], lw=1.5, label="Target Strength Potentiometer (Emulates Future RX SNR)")
    ax1.axhline(0.70, color=PALETTE["red"], ls=":", alpha=0.5, label="Threshold High (0.70)")
    ax1.axhline(0.40, color=PALETTE["yellow"], ls=":", alpha=0.5, label="Threshold Low (0.40)")
    ax1.set_title("Simulated Analog Controls (Potentiometer Wiper Voltages Normalized 0.0 - 1.0)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Input Level")
    ax1.set_ylim(-0.05, 1.05)
    ax1.legend(loc="upper right", facecolor=PALETTE["card_bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"], fontsize=8, ncol=5)

    # 2. Discrete Band Profile with Hysteresis
    ax2 = axes[1]
    apply_custom_style(ax2)
    ax2.step(times_s, band_level, where="post", color=PALETTE["yellow"], lw=2.0)
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(["CLEAR (350-500k)", "BALANCED (200-400k)", "MUDDY (100-220k)"])
    ax2.set_title("Latched Frequency Band Profile (Updated Only at Ping Boundaries)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Frequency Band")

    # 3. Pulse Duration and Amplitude
    ax3 = axes[2]
    apply_custom_style(ax3)
    ax3_twin = ax3.twinx()
    ax3.step(times_s, dur_ms, where="post", color=PALETTE["cyan"], lw=1.8, label="Pulse Duration (ms)")
    ax3_twin.step(times_s, amp_fact, where="post", color=PALETTE["purple"], lw=1.8, ls="--", label="Amplitude Scale")
    ax3.set_ylabel("Pulse Duration (ms)", color=PALETTE["cyan"])
    ax3_twin.set_ylabel("Amplitude Factor (0-1)", color=PALETTE["purple"])
    ax3_twin.tick_params(colors=PALETTE["purple"])
    ax3.set_title("Adaptive Pulse Duration & Amplitude Scaling", fontsize=11, fontweight="bold")
    ax3.set_ylim(0.5, 3.5)
    ax3_twin.set_ylim(0.2, 1.1)

    # 4. Duty Cycle & Average Power
    ax4 = axes[3]
    apply_custom_style(ax4)
    ax4_twin = ax4.twinx()
    ax4.plot(times_s, duty_pct, color=PALETTE["green"], lw=1.5, label="Duty Cycle (%)")
    ax4_twin.plot(times_s, avg_power, color=PALETTE["red"], lw=1.8, label="Estimated TX Avg Power (W)")
    ax4.set_ylabel("Duty Cycle (%)", color=PALETTE["green"])
    ax4_twin.set_ylabel("Estimated TX Avg Power (W)", color=PALETTE["red"])
    ax4_twin.tick_params(colors=PALETTE["red"])
    ax4.set_title("Estimated Duty Cycle & Transmitter-Only Average Power (PRI = 20 ms, TX Payload Alone)", fontsize=11, fontweight="bold")
    ax4.set_xlabel("Mission Elapsed Time (seconds)")
    ax4.set_ylim(0, 20)
    ax4_twin.set_ylim(0, 1.2)

    plt.tight_layout()
    fig.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)


# ==============================================================================
# Rigorous Numerical Validation Suite
# ==============================================================================

def verify_instantaneous_frequency(waveform: Waveform) -> Dict[str, float]:
    """
    Validation Check 1: Numerically estimates instantaneous frequency from the
    analytic signal (Hilbert transform) to verify the sweep tracks f_start -> f_end.

    Evaluated across the central 60% of the pulse where window tapering does not
    suppress the carrier amplitude into numerical noise.
    """
    analytic = signal.hilbert(waveform.ideal_signal)
    inst_phase = np.unwrap(np.angle(analytic))
    dt = 1.0 / waveform.sample_rate_hz
    inst_freq = np.diff(inst_phase) / (2.0 * np.pi * dt)

    N = len(inst_freq)
    mid_slice = slice(int(N * 0.20), int(N * 0.80))
    t_mid = waveform.time_s[:-1][mid_slice]
    f_mid = inst_freq[mid_slice]

    slope_empirical, intercept_empirical = np.polyfit(t_mid, f_mid, 1)
    slope_theoretical = (waveform.f_end_hz - waveform.f_start_hz) / waveform.duration_s

    slope_error_pct = abs((slope_empirical - slope_theoretical) / slope_theoretical) * 100.0
    f_start_error_pct = abs((intercept_empirical - waveform.f_start_hz) / waveform.f_start_hz) * 100.0

    return {
        "slope_theoretical_hz_s": float(slope_theoretical),
        "slope_empirical_hz_s": float(slope_empirical),
        "slope_error_pct": float(slope_error_pct),
        "intercept_empirical_hz": float(intercept_empirical),
        "f_start_error_pct": float(f_start_error_pct),
        "is_sweep_monotonic": bool(slope_empirical > 0),
    }


def verify_band_energy_concentration(waveform: Waveform, margin_hz: float = 5000.0) -> Dict[str, float]:
    """
    Validation Check 2: Computes FFT power spectral density to verify that >99%
    of the emitted digital spectral energy resides strictly within the intended chirp band.
    """
    n_fft = waveform.sample_count * 4
    fft_vals = np.fft.rfft(waveform.ideal_signal, n=n_fft)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / waveform.sample_rate_hz)
    psd = np.abs(fft_vals) ** 2

    total_energy = float(np.sum(psd))
    band_mask = (freqs >= (waveform.f_start_hz - margin_hz)) & (freqs <= (waveform.f_end_hz + margin_hz))
    in_band_energy = float(np.sum(psd[band_mask]))

    energy_ratio = in_band_energy / total_energy if total_energy > 0 else 0.0

    return {
        "total_energy": total_energy,
        "in_band_energy": in_band_energy,
        "in_band_energy_pct": energy_ratio * 100.0,
        "out_of_band_leakage_pct": (1.0 - energy_ratio) * 100.0,
        "passed_99_pct_threshold": bool(energy_ratio >= 0.99),
    }


def verify_spectrogram_ridge(waveform: Waveform) -> Dict[str, float]:
    """
    Validation Check 3: Traces the spectrogram energy ridge to verify that
    instantaneous peak frequency increases linearly with time (R^2 > 0.98).
    """
    nperseg = min(256, waveform.sample_count // 8)
    noverlap = nperseg * 3 // 4
    f, t, Sxx = signal.spectrogram(
        waveform.ideal_signal,
        fs=waveform.sample_rate_hz,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
    )
    peak_indices = np.argmax(Sxx, axis=0)
    peak_freqs = f[peak_indices]

    # Evaluate middle 80% to avoid boundary window taper effects
    mid_slice = slice(int(len(t) * 0.10), int(len(t) * 0.90))
    t_eval = t[mid_slice]
    f_eval = peak_freqs[mid_slice]

    slope, intercept = np.polyfit(t_eval, f_eval, 1)
    corr_matrix = np.corrcoef(t_eval, f_eval)
    r_squared = float(corr_matrix[0, 1] ** 2) if corr_matrix.shape == (2, 2) else 0.0

    theoretical_slope = (waveform.f_end_hz - waveform.f_start_hz) / waveform.duration_s
    slope_error_pct = abs((slope - theoretical_slope) / theoretical_slope) * 100.0

    return {
        "ridge_slope_hz_s": float(slope),
        "ridge_r_squared": float(r_squared),
        "slope_error_pct": float(slope_error_pct),
        "passed_linearity": bool(r_squared >= 0.98),
    }


def verify_header_roundtrip(waveform: Waveform, header_path: str) -> Dict[str, Any]:
    """
    Validation Check 4: Header round-trip test.
    Parses exported C header file back into Python and verifies that every sample
    matches the Python DAC array exactly (bit-exact 12-bit integrity).
    """
    import re
    if not os.path.exists(header_path):
        return {"file_exists": False, "passed": False}

    with open(header_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract all hex uint16 tokens 0xXXXX
    hex_tokens = re.findall(r"0x([0-9A-Fa-f]{4})", content)
    parsed_samples = np.array([int(h, 16) for h in hex_tokens], dtype=np.uint16)

    count_match = (len(parsed_samples) == len(waveform.dac_codes))
    exact_match = count_match and bool(np.array_equal(parsed_samples, waveform.dac_codes))

    return {
        "file_exists": True,
        "sample_count_expected": len(waveform.dac_codes),
        "sample_count_parsed": len(parsed_samples),
        "count_matched": count_match,
        "exact_match": exact_match,
        "max_discrepancy_lsb": int(np.max(np.abs(parsed_samples.astype(int) - waveform.dac_codes.astype(int)))) if count_match else -1,
    }

