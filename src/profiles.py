"""
Profile definitions for adaptive sonar transmitter.
Defines frequency band profiles (Muddy, Balanced, Clear), pulse duration modes,
and amplitude scaling modes.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict
from .config import (
    DAC_SAMPLE_RATE_HZ,
    BYTES_PER_SAMPLE,
    MCU_SRAM_TOTAL_BYTES,
    DEFAULT_PRI_S,
)


class TurbidityProfileType(str, Enum):
    """Discrete environmental profiles driven by turbidity / scattering."""
    MUDDY = "MUDDY"
    BALANCED = "BALANCED"
    CLEAR = "CLEAR"


class RangeDurationMode(str, Enum):
    """Pulse duration modes driven by range/depth requirements."""
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"


class TargetStrengthMode(str, Enum):
    """
    Amplitude scaling modes driven by target reflectivity.
    NOTE: In v1, this is driven by a potentiometer emulating a future receiver/SNR feedback signal.
    """
    WEAK = "WEAK"        # Weak target emulation -> Full transmit power
    MODERATE = "MODERATE" # Moderate target emulation -> Moderate transmit power
    STRONG = "STRONG"    # Strong target emulation -> Reduced transmit power (emulates power throttling & RX saturation avoidance)


@dataclass(frozen=True)
class BandProfile:
    """Acoustic frequency band configuration for a turbidity profile."""
    profile_type: TurbidityProfileType
    f_start_hz: float
    f_end_hz: float
    description: str
    rationale: str

    @property
    def center_freq_hz(self) -> float:
        return (self.f_start_hz + self.f_end_hz) / 2.0

    @property
    def bandwidth_hz(self) -> float:
        return abs(self.f_end_hz - self.f_start_hz)

    @property
    def chirp_rate_hz_per_s(self) -> float:
        # Default for 2 ms pulse
        return self.bandwidth_hz / 0.002


# Canonical frequency band profiles locked for v1
BAND_PROFILES: Dict[TurbidityProfileType, BandProfile] = {
    TurbidityProfileType.MUDDY: BandProfile(
        profile_type=TurbidityProfileType.MUDDY,
        f_start_hz=100_000.0,
        f_end_hz=220_000.0,
        description="High turbidity / suspended sediment mode",
        rationale="Lower acoustic frequencies (100-220 kHz) penetrate particulate scattering with lower Rayleigh attenuation."
    ),
    TurbidityProfileType.BALANCED: BandProfile(
        profile_type=TurbidityProfileType.BALANCED,
        f_start_hz=200_000.0,
        f_end_hz=400_000.0,
        description="Nominal balanced profile",
        rationale="Default 200 kHz bandwidth (200-400 kHz) providing optimal range vs range resolution trade-off."
    ),
    TurbidityProfileType.CLEAR: BandProfile(
        profile_type=TurbidityProfileType.CLEAR,
        f_start_hz=350_000.0,
        f_end_hz=500_000.0,
        description="Clear / low-turbidity pelagic mode",
        rationale="Higher frequencies (350-500 kHz) yield finer spatial resolution (c/2B ~ 5mm) in low-absorption clear water."
    ),
}


# Pulse duration profiles (Range / Depth)
RANGE_DURATIONS: Dict[RangeDurationMode, float] = {
    RangeDurationMode.SHORT: 0.0010,   # 1.0 ms -> 4,000 samples @ 4 MSPS (8 KB)
    RangeDurationMode.MEDIUM: 0.0020,  # 2.0 ms -> 8,000 samples @ 4 MSPS (16 KB)
    RangeDurationMode.LONG: 0.0030,    # 3.0 ms -> 12,000 samples @ 4 MSPS (24 KB)
}


# Amplitude scaling factors (Target Strength)
TARGET_AMPLITUDE_FACTORS: Dict[TargetStrengthMode, float] = {
    TargetStrengthMode.WEAK: 1.00,      # Full scale (0 dB attenuation)
    TargetStrengthMode.MODERATE: 0.70,  # -3.1 dB attenuation
    TargetStrengthMode.STRONG: 0.40,    # -7.96 dB attenuation (saves power & avoids RX clipping)
}


@dataclass(frozen=True)
class TransmitterState:
    """Full operational state of the transmitter for a single ping."""
    band: TurbidityProfileType
    duration_mode: RangeDurationMode
    target_mode: TargetStrengthMode
    pulse_duration_s: float
    amplitude_factor: float
    pri_s: float = DEFAULT_PRI_S

    @property
    def sample_count(self) -> int:
        return int(round(self.pulse_duration_s * DAC_SAMPLE_RATE_HZ))

    @property
    def buffer_bytes(self) -> int:
        return self.sample_count * BYTES_PER_SAMPLE

    @property
    def sram_utilization_pct(self) -> float:
        return (self.buffer_bytes / MCU_SRAM_TOTAL_BYTES) * 100.0

    @property
    def duty_cycle(self) -> float:
        return self.pulse_duration_s / self.pri_s
