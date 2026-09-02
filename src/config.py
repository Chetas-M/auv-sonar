"""
System configuration and locked parameters for AUV Sonar Transmitter Digital Twin.
Target hardware: STM32G4 / STM32G474.
"""

from dataclasses import dataclass

# ==============================================================================
# Locked Hardware & DAC Specifications (v1)
# ==============================================================================
DAC_SAMPLE_RATE_HZ: int = 4_000_000       # 4.0 MSPS DAC update rate
DAC_RESOLUTION_BITS: int = 12             # 12-bit unsigned DAC
DAC_MIN_CODE: int = 0
DAC_MAX_CODE: int = 4095
DAC_MIDSCALE_CODE: int = 2048             # Centered for AC-coupled transducer drive
DAC_VREF_VOLTS: float = 3.3               # STM32 VREF+ voltage

# Frequency boundaries
MIN_FREQUENCY_HZ: float = 100_000.0       # 100 kHz lowest transmit boundary
MAX_FREQUENCY_HZ: float = 500_000.0       # 500 kHz highest transmit boundary
NYQUIST_LIMIT_HZ: float = DAC_SAMPLE_RATE_HZ / 2.0  # 2.0 MHz

# Timing specifications
DEFAULT_CENTER_FREQ_HZ: float = 300_000.0 # 300 kHz
DEFAULT_BANDWIDTH_HZ: float = 200_000.0   # 200 kHz (200 kHz - 400 kHz)
DEFAULT_PULSE_DURATION_S: float = 0.002   # 2.0 ms (8000 samples @ 4 MSPS)
DEFAULT_PRI_S: float = 0.020              # 20.0 ms Pulse Repetition Interval
DEFAULT_DUTY_CYCLE: float = DEFAULT_PULSE_DURATION_S / DEFAULT_PRI_S  # 10.0%

# Target MCU Specifications (STM32G474RE / STM32G474CE)
MCU_NAME: str = "STM32G474"
MCU_MAX_SYSCLK_HZ: int = 170_000_000      # 170 MHz Cortex-M4
MCU_SRAM_TOTAL_BYTES: int = 128 * 1024    # 128 KB total SRAM
MCU_FLASH_TOTAL_BYTES: int = 512 * 1024   # 512 KB Flash
BYTES_PER_SAMPLE: int = 2                 # uint16_t for 12-bit DAC

# Power Model Defaults (Configurable Engineering Estimates)
# Note: These are model parameters for architectural evaluation, not bench proof.
POWER_ACTIVE_WATTS: float = 5.0           # Power during transmit ping (PA + DAC + MCU active)
POWER_IDLE_WATTS: float = 0.045           # Power between pings (PA shut down, MCU low-power sleep)
SUPPLY_VOLTAGE_VOLTS: float = 12.0        # Primary AUV battery bus voltage (V_bat)
AUV_BATTERY_CAPACITY_WH: float = 99.0     # Standard subsea battery pack (99 Wh)


@dataclass(frozen=True)
class SonarConfig:
    """Consolidated configuration container."""
    sample_rate_hz: int = DAC_SAMPLE_RATE_HZ
    dac_resolution_bits: int = DAC_RESOLUTION_BITS
    min_freq_hz: float = MIN_FREQUENCY_HZ
    max_freq_hz: float = MAX_FREQUENCY_HZ
    default_pulse_duration_s: float = DEFAULT_PULSE_DURATION_S
    default_pri_s: float = DEFAULT_PRI_S
    active_power_w: float = POWER_ACTIVE_WATTS
    idle_power_w: float = POWER_IDLE_WATTS
    supply_voltage_v: float = SUPPLY_VOLTAGE_VOLTS
