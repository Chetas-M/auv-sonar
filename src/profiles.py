"""
Profile definitions for adaptive sonar transmitter.
Defines frequency band profiles (LOW_FREQUENCY, BALANCED, HIGH_FREQUENCY)
strictly aligned with SIH Problem 26058.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict
from .config import (
    DAC_SAMPLE_RATE_HZ,
    BYTES_PER_SAMPLE,
    MCU_SRAM_TOTAL_BYTES,
    DEFAULT_PRI_S,
    DEFAULT_PULSE_DURATION_S,
)


class ProfileType(str, Enum):
    """Canonical Version 1 discrete transmission profiles."""
    LOW_FREQUENCY = "LOW_FREQUENCY"
    BALANCED = "BALANCED"
    HIGH_FREQUENCY = "HIGH_FREQUENCY"

    # Backward compatibility aliases
    MUDDY = "LOW_FREQUENCY"
    CLEAR = "HIGH_FREQUENCY"


# Alias for backward compatibility
TurbidityProfileType = ProfileType


class RangeDurationMode(str, Enum):
    """
    Pulse duration modes for sensitivity analysis.
    NOTE: In Version 1 runtime, pulse duration is FIXED at 2.0 ms (MEDIUM).
    """
    SHORT = "SHORT"    # 1.0 ms (Sensitivity analysis)
    MEDIUM = "MEDIUM"  # 2.0 ms (LOCKED VERSION 1 RUNTIME DEFAULT)
    LONG = "LONG"      # 3.0 ms (Sensitivity analysis)


class TargetStrengthMode(str, Enum):
    """
    Amplitude scaling modes driven by target reflectivity / channel quality.
    NOTE: In v1, this emulates a future receiver/SNR feedback signal.
    """
    WEAK = "WEAK"        # Weak target / poor channel -> Full transmit power (A = 1.0)
    MODERATE = "MODERATE"# Moderate target / balanced channel -> Moderate transmit power (A = 0.7)
    STRONG = "STRONG"    # Strong target / high channel -> Power throttling (A = 0.4)


@dataclass(frozen=True)
class BandProfile:
    """Acoustic frequency band configuration for a transmission profile."""
    profile_type: ProfileType
    id: int
    f_start_hz: float
    f_end_hz: float
    lut_name: str
    header_file: str
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
        return self.bandwidth_hz / DEFAULT_PULSE_DURATION_S


# Canonical frequency band profiles locked for v1
BAND_PROFILES: Dict[ProfileType, BandProfile] = {
    ProfileType.LOW_FREQUENCY: BandProfile(
        profile_type=ProfileType.LOW_FREQUENCY,
        id=1,
        f_start_hz=100_000.0,
        f_end_hz=220_000.0,
        lut_name="CHIRP_LOW_FREQUENCY_LUT",
        header_file="chirp_low_frequency.h",
        description="Low Frequency / degraded channel mode",
        rationale="Lower-frequency simulation profile for degraded/scattering channel scenarios."
    ),
    ProfileType.BALANCED: BandProfile(
        profile_type=ProfileType.BALANCED,
        id=2,
        f_start_hz=200_000.0,
        f_end_hz=400_000.0,
        lut_name="CHIRP_BALANCED_LUT",
        header_file="chirp_balanced.h",
        description="Nominal balanced profile",
        rationale="Default operating profile. Features largest bandwidth (200 kHz) and therefore best idealized bandwidth-based range resolution (3.75 mm)."
    ),
    ProfileType.HIGH_FREQUENCY: BandProfile(
        profile_type=ProfileType.HIGH_FREQUENCY,
        id=3,
        f_start_hz=350_000.0,
        f_end_hz=500_000.0,
        lut_name="CHIRP_HIGH_FREQUENCY_LUT",
        header_file="chirp_high_frequency.h",
        description="High Frequency channel mode",
        rationale="Higher-frequency operating-band simulation profile providing narrow acoustic beam directivity for a given physical transducer aperture."
    ),
}


# Pulse duration profiles (Version 1 runtime locked to MEDIUM = 2.0 ms)
RANGE_DURATIONS: Dict[RangeDurationMode, float] = {
    RangeDurationMode.SHORT: 0.0010,   # 1.0 ms -> 4,000 samples (Sensitivity analysis)
    RangeDurationMode.MEDIUM: 0.0020,  # 2.0 ms -> 8,000 samples (V1 LOCKED DEFAULT)
    RangeDurationMode.LONG: 0.0030,    # 3.0 ms -> 12,000 samples (Sensitivity analysis)
}


# Amplitude scaling factors
TARGET_AMPLITUDE_FACTORS: Dict[TargetStrengthMode, float] = {
    TargetStrengthMode.WEAK: 1.00,      # Full scale (0 dB attenuation)
    TargetStrengthMode.MODERATE: 0.70,  # -3.1 dB attenuation
    TargetStrengthMode.STRONG: 0.40,    # -7.96 dB attenuation
}


@dataclass(frozen=True)
class TransmitterState:
    """Full operational state of the transmitter for a single ping."""
    band: ProfileType
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
