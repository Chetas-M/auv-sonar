"""
Adaptation engine and state machine for AUV sonar transmitter payload.
Implements hysteresis-backed thresholding, debounce persistence filtering,
and strict ping-boundary latching (modeling STM32 DMA TC interrupt behavior).
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from .profiles import (
    TurbidityProfileType,
    RangeDurationMode,
    TargetStrengthMode,
    RANGE_DURATIONS,
    TARGET_AMPLITUDE_FACTORS,
    TransmitterState,
)
from .config import DEFAULT_PRI_S


@dataclass
class AnalogInputs:
    """
    Simulated analog control inputs representing potentiometer voltages (0.0 to 1.0).
    In v1 hardware, these are 3 potentiometers connected to STM32 ADC channels.
    Target-strength input emulates a future receiver/SNR feedback signal.
    """
    turbidity: float        # 0.0 (crystal clear) to 1.0 (dense sediment / muddy)
    range_depth: float      # 0.0 (near-field obstacle) to 1.0 (far search range)
    target_strength: float  # 0.0 to 1.0 (emulates future receiver/SNR feedback signal via potentiometer)

    def __post_init__(self):
        self.turbidity = max(0.0, min(1.0, float(self.turbidity)))
        self.range_depth = max(0.0, min(1.0, float(self.range_depth)))
        self.target_strength = max(0.0, min(1.0, float(self.target_strength)))


class HysteresisThreshold:
    """
    Two-threshold Schmitt-trigger style hysteresis for 3-tier discrete profiling.
    Prevents profile flickering when potentiometer voltage sits near threshold.
    """
    def __init__(
        self,
        low_to_mid_threshold: float = 0.40,
        mid_to_low_threshold: float = 0.30,
        mid_to_high_threshold: float = 0.70,
        high_to_mid_threshold: float = 0.60,
    ):
        assert low_to_mid_threshold > mid_to_low_threshold, "Deadband 1 inverted"
        assert mid_to_high_threshold > high_to_mid_threshold, "Deadband 2 inverted"
        assert mid_to_high_threshold > low_to_mid_threshold, "Threshold sequence error"

        self.low_to_mid = low_to_mid_threshold
        self.mid_to_low = mid_to_low_threshold
        self.mid_to_high = mid_to_high_threshold
        self.high_to_mid = high_to_mid_threshold

    def update_state(self, current_tier: int, value: float) -> int:
        """
        Calculates next discrete state tier (0: Low, 1: Medium, 2: High) with hysteresis.
        Tier 0: Clear / Short / Weak
        Tier 1: Balanced / Medium / Moderate
        Tier 2: Muddy / Long / Strong
        """
        if current_tier == 0:  # Currently in LOW tier
            if value >= self.mid_to_high:
                return 2
            elif value >= self.low_to_mid:
                return 1
            else:
                return 0
        elif current_tier == 1:  # Currently in MID tier
            if value >= self.mid_to_high:
                return 2
            elif value <= self.mid_to_low:
                return 0
            else:
                return 1
        elif current_tier == 2:  # Currently in HIGH tier
            if value <= self.mid_to_low:
                return 0
            elif value <= self.high_to_mid:
                return 1
            else:
                return 2
        return current_tier


class AdaptationEngine:
    """
    Translates raw potentiometer readings into discrete transmitter configurations
    using hysteresis and debounce filtering.
    """

    def __init__(self, debounce_count: int = 2):
        """
        Args:
            debounce_count: Number of consecutive pings an input must persist
                           in a new threshold zone before switching profile.
        """
        self.debounce_count = max(1, debounce_count)

        # Hysteresis units for each axis
        self.turbidity_hyst = HysteresisThreshold(
            low_to_mid_threshold=0.40,
            mid_to_low_threshold=0.30,
            mid_to_high_threshold=0.70,
            high_to_mid_threshold=0.60,
        )
        self.range_hyst = HysteresisThreshold(
            low_to_mid_threshold=0.40,
            mid_to_low_threshold=0.30,
            mid_to_high_threshold=0.70,
            high_to_mid_threshold=0.60,
        )
        self.target_hyst = HysteresisThreshold(
            low_to_mid_threshold=0.40,
            mid_to_low_threshold=0.30,
            mid_to_high_threshold=0.70,
            high_to_mid_threshold=0.60,
        )

        # Current latched discrete states (0: Low, 1: Mid, 2: High)
        self.curr_turbidity_tier = 1    # Default: BALANCED
        self.curr_range_tier = 1        # Default: MEDIUM (2.0 ms)
        self.curr_target_tier = 0       # Default: WEAK target -> 1.0 Amplitude

        # Debounce tracking
        self.candidate_turbidity_tier = self.curr_turbidity_tier
        self.turbidity_debounce_counter = 0

        self.candidate_range_tier = self.curr_range_tier
        self.range_debounce_counter = 0

        self.candidate_target_tier = self.curr_target_tier
        self.target_debounce_counter = 0

    def evaluate(self, inputs: AnalogInputs) -> TransmitterState:
        """
        Evaluate raw analog inputs, apply hysteresis and debounce, and return
        the resulting TransmitterState.
        """
        # 1. Turbidity -> Frequency band
        next_turb_candidate = self.turbidity_hyst.update_state(self.curr_turbidity_tier, inputs.turbidity)
        if next_turb_candidate != self.curr_turbidity_tier:
            if next_turb_candidate == self.candidate_turbidity_tier:
                self.turbidity_debounce_counter += 1
            else:
                self.candidate_turbidity_tier = next_turb_candidate
                self.turbidity_debounce_counter = 1

            if self.turbidity_debounce_counter >= self.debounce_count:
                self.curr_turbidity_tier = next_turb_candidate
                self.turbidity_debounce_counter = 0
        else:
            self.candidate_turbidity_tier = self.curr_turbidity_tier
            self.turbidity_debounce_counter = 0

        # 2. Range/Depth -> Duration
        next_range_candidate = self.range_hyst.update_state(self.curr_range_tier, inputs.range_depth)
        if next_range_candidate != self.curr_range_tier:
            if next_range_candidate == self.candidate_range_tier:
                self.range_debounce_counter += 1
            else:
                self.candidate_range_tier = next_range_candidate
                self.range_debounce_counter = 1

            if self.range_debounce_counter >= self.debounce_count:
                self.curr_range_tier = next_range_candidate
                self.range_debounce_counter = 0
        else:
            self.candidate_range_tier = self.curr_range_tier
            self.range_debounce_counter = 0

        # 3. Target Strength -> Amplitude
        next_target_candidate = self.target_hyst.update_state(self.curr_target_tier, inputs.target_strength)
        if next_target_candidate != self.curr_target_tier:
            if next_target_candidate == self.candidate_target_tier:
                self.target_debounce_counter += 1
            else:
                self.candidate_target_tier = next_target_candidate
                self.target_debounce_counter = 1

            if self.target_debounce_counter >= self.debounce_count:
                self.curr_target_tier = next_target_candidate
                self.target_debounce_counter = 0
        else:
            self.candidate_target_tier = self.curr_target_tier
            self.target_debounce_counter = 0

        # Map tiers to domain types
        turb_map = {0: TurbidityProfileType.CLEAR, 1: TurbidityProfileType.BALANCED, 2: TurbidityProfileType.MUDDY}
        range_map = {0: RangeDurationMode.SHORT, 1: RangeDurationMode.MEDIUM, 2: RangeDurationMode.LONG}
        target_map = {0: TargetStrengthMode.WEAK, 1: TargetStrengthMode.MODERATE, 2: TargetStrengthMode.STRONG}

        band_type = turb_map[self.curr_turbidity_tier]
        range_mode = range_map[self.curr_range_tier]
        target_mode = target_map[self.curr_target_tier]

        return TransmitterState(
            band=band_type,
            duration_mode=range_mode,
            target_mode=target_mode,
            pulse_duration_s=RANGE_DURATIONS[range_mode],
            amplitude_factor=TARGET_AMPLITUDE_FACTORS[target_mode],
            pri_s=DEFAULT_PRI_S,
        )


class PingController:
    """
    Simulates real-time transmitter operation across multiple pings.
    Guarantees atomic profile changes at ping boundaries only, modeling STM32 DMA
    completion ISRs.
    """
    def __init__(self, debounce_count: int = 2):
        self.adaptation_engine = AdaptationEngine(debounce_count=debounce_count)
        self.active_state: TransmitterState = self.adaptation_engine.evaluate(
            AnalogInputs(turbidity=0.5, range_depth=0.5, target_strength=0.1)
        )
        self.ping_counter: int = 0
        self.elapsed_time_s: float = 0.0

    def trigger_ping(self, current_inputs: AnalogInputs) -> Tuple[int, float, TransmitterState, bool]:
        """
        Executes one ping cycle.
        1. Latches profile changes that were settled before this ping boundary.
        2. Evaluates new inputs (ready for next ping).
        
        Returns:
            (ping_index, start_time_s, active_transmitter_state, profile_changed_flag)
        """
        ping_index = self.ping_counter
        ping_start_time = self.elapsed_time_s

        # Latch candidate state at ping boundary
        new_state = self.adaptation_engine.evaluate(current_inputs)
        changed = (new_state != self.active_state)
        self.active_state = new_state

        # Advance timeline by PRI
        self.elapsed_time_s += self.active_state.pri_s
        self.ping_counter += 1

        return ping_index, ping_start_time, self.active_state, changed
