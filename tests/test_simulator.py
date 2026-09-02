"""
Automated unit test suite for AUV Sonar Transmitter Digital Twin.
Tests waveform math, DAC quantization, hysteresis adaptation, power model, and C header export.
"""

import os
import unittest
import numpy as np

from src.config import (
    DAC_SAMPLE_RATE_HZ,
    DAC_MIN_CODE,
    DAC_MAX_CODE,
    DAC_MIDSCALE_CODE,
    DEFAULT_PULSE_DURATION_S,
    DEFAULT_PRI_S,
)
from src.profiles import (
    TurbidityProfileType,
    BandProfile,
    BAND_PROFILES,
    TransmitterState,
    RangeDurationMode,
    TargetStrengthMode,
)
from src.waveform import generate_lfm_chirp, Waveform
from src.adaptation import AnalogInputs, HysteresisThreshold, AdaptationEngine, PingController
from src.power_model import SonarPowerModel, PowerMetrics
from src.export_c import export_waveform_to_c_header


class TestWaveformGeneration(unittest.TestCase):
    """Verifies physical and mathematical properties of LFM chirp generation."""

    def test_sample_count_and_bounds(self):
        wf = generate_lfm_chirp(
            f_start_hz=200_000,
            f_end_hz=400_000,
            duration_s=0.002,
            sample_rate_hz=4_000_000,
            amplitude_factor=1.0,
            window_type="hann",
        )
        # 0.002 s * 4,000,000 Hz = 8000 samples
        self.assertEqual(wf.sample_count, 8000)
        self.assertEqual(len(wf.dac_codes), 8000)
        self.assertEqual(len(wf.time_s), 8000)
        self.assertAlmostEqual(wf.time_s[0], 0.0)
        self.assertAlmostEqual(wf.time_s[-1], (8000 - 1) / 4_000_000)

        # Ideal signal bounded [-1.0, 1.0]
        self.assertTrue(np.all(wf.ideal_signal >= -1.0001))
        self.assertTrue(np.all(wf.ideal_signal <= 1.0001))

        # Window endpoints should taper smoothly to zero
        self.assertAlmostEqual(wf.window[0], 0.0, places=4)
        self.assertAlmostEqual(wf.window[-1], 0.0, places=4)

    def test_amplitude_scaling(self):
        wf_half = generate_lfm_chirp(
            f_start_hz=200_000,
            f_end_hz=400_000,
            duration_s=0.001,
            sample_rate_hz=4_000_000,
            amplitude_factor=0.5,
            window_type="hann",
        )
        self.assertAlmostEqual(np.max(np.abs(wf_half.ideal_signal)), 0.5, delta=0.05)


class TestDACQuantization(unittest.TestCase):
    """Verifies 12-bit DAC quantization, midscale offset, and SQNR limits."""

    def test_dac_code_range(self):
        wf = generate_lfm_chirp(
            f_start_hz=100_000,
            f_end_hz=220_000,
            duration_s=0.002,
            sample_rate_hz=4_000_000,
            amplitude_factor=1.0,
        )
        # Must be uint16 and within [0, 4095]
        self.assertEqual(wf.dac_codes.dtype, np.uint16)
        self.assertTrue(np.all(wf.dac_codes >= DAC_MIN_CODE))
        self.assertTrue(np.all(wf.dac_codes <= DAC_MAX_CODE))

        # Max quantization error should not exceed 0.5 LSB for standard rounding
        self.assertLessEqual(wf.max_quant_error_lsb, 0.5001)

        # High SQNR (>65 dB for 12-bit full-scale chirp with Hann window)
        self.assertGreater(wf.sqnr_db, 65.0)

    def test_zero_signal_midscale(self):
        # When amplitude is 0, signal is pure midscale 2048
        wf_zero = generate_lfm_chirp(
            f_start_hz=100_000,
            f_end_hz=200_000,
            duration_s=0.001,
            sample_rate_hz=4_000_000,
            amplitude_factor=0.0,
        )
        self.assertTrue(np.all(wf_zero.dac_codes == DAC_MIDSCALE_CODE))


class TestHysteresisAndAdaptation(unittest.TestCase):
    """Verifies Schmitt-trigger hysteresis deadbands and debounce filtering."""

    def test_hysteresis_deadband_stability(self):
        hyst = HysteresisThreshold(
            low_to_mid_threshold=0.40,
            mid_to_low_threshold=0.30,
            mid_to_high_threshold=0.70,
            high_to_mid_threshold=0.60,
        )
        # Starting in tier 0 (Low / Clear)
        # Input rises to 0.35: still below low_to_mid (0.40) -> stay in tier 0
        self.assertEqual(hyst.update_state(0, 0.35), 0)
        # Input crosses 0.42: exceeds 0.40 -> transition to tier 1
        self.assertEqual(hyst.update_state(0, 0.42), 1)

        # Now in tier 1 (Mid / Balanced)
        # Input drops to 0.35: above mid_to_low (0.30) -> stay in tier 1 (hysteresis works!)
        self.assertEqual(hyst.update_state(1, 0.35), 1)
        # Input drops to 0.28: below mid_to_low (0.30) -> transition to tier 0
        self.assertEqual(hyst.update_state(1, 0.28), 0)

        # Test upper boundary: in tier 1, input rises to 0.65 -> stay in tier 1
        self.assertEqual(hyst.update_state(1, 0.65), 1)
        # Exceeds 0.70 -> transition to tier 2
        self.assertEqual(hyst.update_state(1, 0.72), 2)
        # In tier 2, drops to 0.65 -> stay in tier 2 (above high_to_mid 0.60)
        self.assertEqual(hyst.update_state(2, 0.65), 2)
        # Drops to 0.58 -> transition to tier 1
        self.assertEqual(hyst.update_state(2, 0.58), 1)

    def test_debounce_persistence(self):
        # Debounce = 2 requires 2 consecutive pings
        engine = AdaptationEngine(debounce_count=2)
        # Starts in BALANCED (tier 1)
        # Single spike to clear (0.10)
        state1 = engine.evaluate(AnalogInputs(turbidity=0.10, range_depth=0.5, target_strength=0.1))
        # Should still be BALANCED because it only lasted 1 evaluation
        self.assertEqual(state1.band, TurbidityProfileType.BALANCED)

        # Second consecutive evaluation at 0.10
        state2 = engine.evaluate(AnalogInputs(turbidity=0.10, range_depth=0.5, target_strength=0.1))
        # Now confirmed -> switches to CLEAR
        self.assertEqual(state2.band, TurbidityProfileType.CLEAR)

    def test_ping_boundary_controller(self):
        controller = PingController(debounce_count=1)
        # Ping 0
        idx0, t0, state0, changed0 = controller.trigger_ping(AnalogInputs(turbidity=0.8, range_depth=0.5, target_strength=0.1))
        self.assertEqual(idx0, 0)
        self.assertAlmostEqual(t0, 0.0)
        self.assertEqual(state0.band, TurbidityProfileType.MUDDY)

        # Ping 1 (time advances by PRI = 0.020 s)
        idx1, t1, state1, changed1 = controller.trigger_ping(AnalogInputs(turbidity=0.8, range_depth=0.5, target_strength=0.1))
        self.assertEqual(idx1, 1)
        self.assertAlmostEqual(t1, DEFAULT_PRI_S)


class TestPowerModel(unittest.TestCase):
    """Verifies analytical accuracy of duty-cycle power estimation."""

    def test_power_calculation(self):
        # 5.0W active, 0.05W idle, 2ms pulse, 20ms PRI -> 10% duty cycle
        model = SonarPowerModel(
            base_active_power_w=5.0,
            idle_power_w=0.05,
            supply_voltage_v=12.0,
            model_pa_amplitude_scaling=False,  # Test exact linear duty cycle formula
        )
        dummy_state = TransmitterState(
            band=TurbidityProfileType.BALANCED,
            duration_mode=RangeDurationMode.MEDIUM,
            target_mode=TargetStrengthMode.WEAK,
            pulse_duration_s=0.002,
            amplitude_factor=1.0,
            pri_s=0.020,
        )
        metrics = model.compute(dummy_state)
        expected_duty = 0.10
        expected_power = 5.0 * 0.10 + 0.05 * 0.90  # 0.50 + 0.045 = 0.545 W
        expected_current_ma = (0.545 / 12.0) * 1000.0

        self.assertAlmostEqual(metrics.duty_cycle_pct, 10.0)
        self.assertAlmostEqual(metrics.average_power_w, expected_power, places=4)
        self.assertAlmostEqual(metrics.average_current_ma, expected_current_ma, places=2)


class TestCHeaderExport(unittest.TestCase):
    """Verifies valid C syntax, macros, and array generation in exported headers."""

    def test_export_file_content(self):
        wf = generate_lfm_chirp(
            f_start_hz=200_000,
            f_end_hz=400_000,
            duration_s=0.001,  # 1 ms -> 4000 samples
            sample_rate_hz=4_000_000,
        )
        test_file = "tests/test_chirp.h"
        try:
            export_waveform_to_c_header(wf, test_file, "TEST_CHIRP_LUT", "TEST")
            self.assertTrue(os.path.exists(test_file))
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Verify C header elements
            self.assertIn("#ifndef TEST_CHIRP_H_", content)
            self.assertIn("#define TEST_CHIRP_H_", content)
            self.assertIn("#define TEST_CHIRP_LUT_SAMPLE_COUNT    (4000U)", content)
            self.assertIn("#define TEST_CHIRP_LUT_SIZE_BYTES      (8000U)", content)
            self.assertIn("DMA_ALIGN const uint16_t TEST_CHIRP_LUT[4000] = {", content)
            self.assertIn("0x", content)
            self.assertIn("};", content)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


class TestRigorousVerificationChecks(unittest.TestCase):
    """
    Validation tests requested to prove algorithm credibility:
    1. Instantaneous frequency test (Hilbert phase derivative sweep tracking)
    2. FFT band-energy concentration test (>99% energy in chirp band)
    3. Spectrogram ridge test (linear frequency increase with time, R^2 > 0.98)
    4. Header round-trip test (C header parsed back matches Python DAC codes bit-exact)
    """

    def setUp(self):
        from src.validation import (
            verify_instantaneous_frequency,
            verify_band_energy_concentration,
            verify_spectrogram_ridge,
            verify_header_roundtrip,
        )
        self.verify_inst_freq = verify_instantaneous_frequency
        self.verify_band_energy = verify_band_energy_concentration
        self.verify_spec_ridge = verify_spectrogram_ridge
        self.verify_header_rt = verify_header_roundtrip

    def test_instantaneous_frequency_sweep(self):
        """Check 1: Instantaneous frequency sweeps monotonically from f_start to f_end."""
        wf = generate_lfm_chirp(
            f_start_hz=200_000.0,
            f_end_hz=400_000.0,
            duration_s=0.002,
            sample_rate_hz=4_000_000,
        )
        res = self.verify_inst_freq(wf)
        self.assertTrue(res["is_sweep_monotonic"], "Chirp frequency must increase monotonically")
        # Theoretical slope: (400k - 200k) / 0.002 = 100 MHz/s. Error must be < 0.1%
        self.assertLess(res["slope_error_pct"], 0.1, f"Slope error {res['slope_error_pct']}% exceeds 0.1%")
        # Intercept matches f_start within 0.1%
        self.assertLess(res["f_start_error_pct"], 0.1, f"f_start error {res['f_start_error_pct']}% exceeds 0.1%")

    def test_fft_band_energy_concentration(self):
        """Check 2: FFT power spectral density concentrates >99% energy in intended chirp band."""
        wf = generate_lfm_chirp(
            f_start_hz=200_000.0,
            f_end_hz=400_000.0,
            duration_s=0.002,
            sample_rate_hz=4_000_000,
        )
        res = self.verify_band_energy(wf, margin_hz=5000.0)
        self.assertTrue(res["passed_99_pct_threshold"], "Must pass >99% in-band energy threshold")
        self.assertGreater(res["in_band_energy_pct"], 99.0, f"In-band energy {res['in_band_energy_pct']}% < 99.0%")
        self.assertLess(res["out_of_band_leakage_pct"], 1.0, f"Out-of-band leakage {res['out_of_band_leakage_pct']}% >= 1.0%")

    def test_spectrogram_ridge_linearity(self):
        """Check 3: Spectrogram peak energy ridge increases linearly with time (R^2 > 0.98)."""
        wf = generate_lfm_chirp(
            f_start_hz=200_000.0,
            f_end_hz=400_000.0,
            duration_s=0.002,
            sample_rate_hz=4_000_000,
        )
        res = self.verify_spec_ridge(wf)
        self.assertTrue(res["passed_linearity"], f"Spectrogram ridge R^2 {res['ridge_r_squared']} < 0.98")
        self.assertGreater(res["ridge_r_squared"], 0.98)
        self.assertLess(res["slope_error_pct"], 5.0, f"Ridge slope error {res['slope_error_pct']}% exceeds 5.0%")

    def test_c_header_roundtrip_integrity(self):
        """Check 4: Exported C header parsed back matches Python DAC codes bit-exact."""
        wf = generate_lfm_chirp(
            f_start_hz=100_000.0,
            f_end_hz=220_000.0,
            duration_s=0.002,
            sample_rate_hz=4_000_000,
        )
        test_file = "tests/test_roundtrip.h"
        try:
            export_waveform_to_c_header(wf, test_file, "CHIRP_RT_LUT", "MUDDY")
            res = self.verify_header_rt(wf, test_file)
            self.assertTrue(res["file_exists"])
            self.assertTrue(res["count_matched"], f"Count mismatch: expected {res['sample_count_expected']}, got {res['sample_count_parsed']}")
            self.assertTrue(res["exact_match"], "Parsed C array must match Python DAC array bit-for-bit")
            self.assertEqual(res["max_discrepancy_lsb"], 0, f"Discrepancy: {res['max_discrepancy_lsb']} LSB")
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


if __name__ == "__main__":
    unittest.main()
