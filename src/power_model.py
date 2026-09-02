"""
Power model and energy consumption estimator for AUV sonar transmitter payload.
Provides duty-cycle-based and amplitude-dependent average power/current estimations.
"""

from dataclasses import dataclass
from typing import Dict, Any
from .config import (
    POWER_ACTIVE_WATTS,
    POWER_IDLE_WATTS,
    SUPPLY_VOLTAGE_VOLTS,
    AUV_BATTERY_CAPACITY_WH,
)
from .profiles import TransmitterState


@dataclass(frozen=True)
class PowerMetrics:
    """Calculated power, current, and endurance metrics for a transmitter state."""
    pulse_duration_ms: float
    pri_ms: float
    duty_cycle_pct: float
    amplitude_factor: float
    active_power_w: float
    idle_power_w: float
    average_power_w: float
    average_current_ma: float
    supply_voltage_v: float
    transmitter_alone_endurance_hours: float  # Transmitter payload load only on hypothetical pack
    energy_per_ping_mj: float

    @property
    def battery_endurance_hours(self) -> float:
        """Alias for backward compatibility: transmitter-only estimated endurance."""
        return self.transmitter_alone_endurance_hours

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pulse_duration_ms": self.pulse_duration_ms,
            "pri_ms": self.pri_ms,
            "duty_cycle_pct": self.duty_cycle_pct,
            "amplitude_factor": self.amplitude_factor,
            "active_power_w": self.active_power_w,
            "idle_power_w": self.idle_power_w,
            "average_power_w": self.average_power_w,
            "average_current_ma": self.average_current_ma,
            "supply_voltage_v": self.supply_voltage_v,
            "transmitter_alone_endurance_hours": self.transmitter_alone_endurance_hours,
            "energy_per_ping_mj": self.energy_per_ping_mj,
        }


class SonarPowerModel:
    """
    Duty-cycle based power model.
    
    Equations:
        duty_cycle = pulse_duration / PRI
        average_power = active_power * duty_cycle + idle_power * (1 - duty_cycle)
        average_current = average_power / supply_voltage
        energy_per_ping = (active_power * pulse_duration) + (idle_power * (PRI - pulse_duration))
    """

    DISCLAIMER = (
        "ENGINEERING NOTE: Power figures are simulation estimates for the modeled transmitter "
        "payload load alone against a hypothetical 99 Wh pack. They do not represent full AUV "
        "mission life (which includes thrusters, compute, navigation, sensors, and comms) and "
        "do not constitute bench measurement proof of physical hardware power consumption."
    )

    def __init__(
        self,
        base_active_power_w: float = POWER_ACTIVE_WATTS,
        idle_power_w: float = POWER_IDLE_WATTS,
        supply_voltage_v: float = SUPPLY_VOLTAGE_VOLTS,
        battery_capacity_wh: float = AUV_BATTERY_CAPACITY_WH,
        model_pa_amplitude_scaling: bool = True,
    ):
        self.base_active_power_w = base_active_power_w
        self.idle_power_w = idle_power_w
        self.supply_voltage_v = supply_voltage_v
        self.battery_capacity_wh = battery_capacity_wh
        self.model_pa_amplitude_scaling = model_pa_amplitude_scaling

    def compute(self, state: TransmitterState) -> PowerMetrics:
        """Calculate power metrics for a given transmitter state."""
        duration_s = state.pulse_duration_s
        pri_s = state.pri_s
        duty_cycle = duration_s / pri_s

        # Effective active power:
        # If PA amplitude scaling is enabled, acoustic transmit power scales with A^2.
        # Electronic overhead (MCU, DAC, buffer opamp) is ~0.3W, PA absorbs the remainder.
        if self.model_pa_amplitude_scaling:
            elec_overhead_w = 0.30
            pa_max_w = max(0.0, self.base_active_power_w - elec_overhead_w)
            effective_active_w = elec_overhead_w + pa_max_w * (state.amplitude_factor ** 2)
        else:
            effective_active_w = self.base_active_power_w

        # Core duty cycle formula:
        # average_power = active_power * duty_cycle + idle_power * (1 - duty_cycle)
        avg_power_w = (effective_active_w * duty_cycle) + (self.idle_power_w * (1.0 - duty_cycle))
        avg_current_ma = (avg_power_w / self.supply_voltage_v) * 1000.0

        # Energy consumed in one complete ping period (Joules = Watts * Seconds)
        energy_ping_j = (effective_active_w * duration_s) + (self.idle_power_w * (pri_s - duration_s))
        energy_ping_mj = energy_ping_j * 1000.0

        # Theoretical battery endurance (hours)
        endurance_hours = self.battery_capacity_wh / avg_power_w if avg_power_w > 0 else 0.0

        return PowerMetrics(
            pulse_duration_ms=duration_s * 1000.0,
            pri_ms=pri_s * 1000.0,
            duty_cycle_pct=duty_cycle * 100.0,
            amplitude_factor=state.amplitude_factor,
            active_power_w=effective_active_w,
            idle_power_w=self.idle_power_w,
            average_power_w=avg_power_w,
            average_current_ma=avg_current_ma,
            supply_voltage_v=self.supply_voltage_v,
            transmitter_alone_endurance_hours=endurance_hours,
            energy_per_ping_mj=energy_ping_mj,
        )
