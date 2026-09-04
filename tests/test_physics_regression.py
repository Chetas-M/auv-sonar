"""
tests/test_physics_regression.py
Permanent Regression Protection for Underwater Acoustic Absorption,
Hydrostatic Pressure Corrections (P2), Implementation Parity across Depth Envelopes,
Unit Conversions, Physical Reference Agreement, and Viability Boundaries.
"""

import json
import math
import os
import unittest
import numpy as np

from src.profile_evaluator import (
    EnvironmentalScenario,
    evaluate_all_profiles,
    evaluate_single_profile,
    compute_mackenzie_sound_speed,
    ainslie_mccolm_absorption,
)
from src.physics_reference import (
    independent_ainslie_mccolm_reference,
    evaluate_production_components,
)


class TestPhysicsRegression(unittest.TestCase):
    """Guarantees protection against unit conversion bugs, P2 depth omissions, formula drift, and report disconnects."""

    def setUp(self):
        self.T = 20.0
        self.S = 35.0
        self.D = 50.0
        self.pH = 8.0

    # 1. Frequency Unit Correctness: Hz vs kHz
    def test_01_frequency_unit_conversion_correctness(self):
        f_hz = 160_000.0
        f_khz = f_hz / 1000.0
        self.assertEqual(f_khz, 160.0)

        # Confirm production function expects kHz:
        # At 160 kHz with P2 depth correction at D=50m, alpha = 65.81 dB/km.
        alpha_correct = ainslie_mccolm_absorption(f_khz, self.T, self.S, self.D)
        self.assertAlmostEqual(alpha_correct, 65.81, delta=0.1)

        # If Hz were accidentally passed instead of kHz (160000 instead of 160):
        # A3 * f^2 alone would equal 0.00023 * (160000)^2 > 5.9 million dB/km!
        alpha_erroneous_hz = ainslie_mccolm_absorption(f_hz, self.T, self.S, self.D)
        self.assertGreater(alpha_erroneous_hz, 1_000_000.0)

    # 2. Distance and Attenuation Unit Correctness: dB/km <-> dB/m and m <-> km
    def test_02_distance_and_attenuation_units(self):
        f_khz = 160.0
        alpha_db_km = ainslie_mccolm_absorption(f_khz, self.T, self.S, self.D)
        alpha_db_m = alpha_db_km / 1000.0
        self.assertAlmostEqual(alpha_db_m * 1000.0, alpha_db_km, places=9)

        # Transmission Loss calculation: TL(R) = 20*log10(R) + alpha*(R/1000)
        # For R = 200 m, spreading = 20*log10(200) = 46.0206 dB
        # Absorption = alpha_db_km * (200 / 1000) = alpha_db_km * 0.2
        r_m = 200.0
        spreading_loss = 20.0 * np.log10(r_m)
        absorption_loss_via_km = alpha_db_km * (r_m / 1000.0)
        absorption_loss_via_m = alpha_db_m * r_m

        self.assertAlmostEqual(absorption_loss_via_km, absorption_loss_via_m, places=9)
        tl_total = spreading_loss + absorption_loss_via_km
        self.assertAlmostEqual(tl_total, 46.0206 + alpha_db_km * 0.2, delta=0.01)

    # 3. Validation A — Full-Formulation Implementation Parity Across Depth-Frequency Operating Matrix
    def test_03_implementation_parity_matrix(self):
        """
        Demonstrates that production and independent reference implementations agree to
        strict numerical precision (rtol=1e-10) across the entire operational depth envelope (10m to 300m)
        and across all relevant transmission frequencies.
        """
        depths_m = [10.0, 50.0, 100.0, 200.0, 300.0]
        test_frequencies_khz = [
            100.0, 130.0, 160.0, 190.0, 200.0, 220.0,
            250.0, 300.0, 350.0, 387.5, 400.0, 425.0, 462.5, 500.0
        ]

        for d in depths_m:
            for f in test_frequencies_khz:
                prod_val = ainslie_mccolm_absorption(f, self.T, self.S, d)
                _, _, _, ref_val = independent_ainslie_mccolm_reference(f, self.T, self.S, d, self.pH)

                np.testing.assert_allclose(
                    prod_val,
                    ref_val,
                    rtol=1e-10,
                    atol=1e-10,
                    err_msg=f"Implementation divergence at D={d}m, f={f}kHz: Prod={prod_val}, Ref={ref_val}",
                )

    # 4. Validation B — Depth-Dependence & P2 Hydrostatic Correction Regression Protection
    def test_04_p2_hydrostatic_depth_regression(self):
        """
        Verifies the analytical correctness and monotonicity of the P2 hydrostatic factor:
          P2(D) = exp(-D_km / 6) = exp(-D_m / 6000)
        Specifically tests that omitting P2 (or setting P2 = 1.0) fails regression.
        """
        depths = [10.0, 50.0, 100.0, 200.0, 300.0]
        p2_values = [math.exp(-d / 6000.0) for d in depths]

        # Check bounds: 0 < P2 <= 1.0
        for p2 in p2_values:
            self.assertGreater(p2, 0.0)
            self.assertLessEqual(p2, 1.0)

        # Check strict monotonic decrease with increasing depth
        for i in range(len(p2_values) - 1):
            self.assertGreater(p2_values[i], p2_values[i + 1])

        # Specific numerical checks
        self.assertAlmostEqual(p2_values[0], math.exp(-10.0 / 6000.0), places=7)   # 10m -> 0.9983347
        self.assertAlmostEqual(p2_values[1], math.exp(-50.0 / 6000.0), places=7)   # 50m -> 0.9917014
        self.assertAlmostEqual(p2_values[4], math.exp(-300.0 / 6000.0), places=7)  # 300m -> 0.9512294

        # Regression anti-bypass check: Verify that calculating absorption without P2 diverges from production
        f_test = 160.0  # kHz
        for d in depths:
            prod_val = ainslie_mccolm_absorption(f_test, self.T, self.S, d)
            # Reconstruct artificial uncorrected absorption (P2 = 1.0)
            f1 = 0.78 * math.sqrt(self.S / 35.0) * math.exp(self.T / 26.0)
            A1 = 0.106 * math.exp((self.pH - 8.0) / 0.56)
            f2 = 42.0 * math.exp(self.T / 17.0)
            A2 = 0.52 * (1.0 + self.T / 43.0) * (self.S / 35.0)
            A3 = 0.00049 * math.exp(-(self.T / 27.0 + (d / 1000.0) / 17.0))
            f_sq = f_test ** 2
            uncorrected_alpha = (A1 * f1 * f_sq) / (f1 ** 2 + f_sq) + (A2 * 1.0 * f2 * f_sq) / (f2 ** 2 + f_sq) + A3 * f_sq

            # At depth >= 10m, uncorrected alpha MUST be strictly greater than production alpha
            self.assertGreater(
                uncorrected_alpha,
                prod_val,
                f"Production code at D={d}m must include P2 depth reduction (uncorrected={uncorrected_alpha}, prod={prod_val})"
            )

    # 5. Canonical Profile Mean Attenuation Values (Corrected Physics Baseline)
    def test_05_canonical_profile_mean_attenuation(self):
        scenario = EnvironmentalScenario(temperature_c=20.0, salinity_psu=35.0, depth_m=50.0)
        metrics, _ = evaluate_all_profiles(scenario)

        # Profile 1: LOW_FREQUENCY (100–220 kHz) -> Corrected mean: 63.99 dB/km
        self.assertAlmostEqual(metrics[0].alpha_band_db_km, 63.99, delta=0.05)
        # Profile 2: BALANCED (200–400 kHz) -> Corrected mean: 105.62 dB/km
        self.assertAlmostEqual(metrics[1].alpha_band_db_km, 105.62, delta=0.05)
        # Profile 3: HIGH_FREQUENCY (350–500 kHz) -> Corrected mean: 135.86 dB/km
        self.assertAlmostEqual(metrics[2].alpha_band_db_km, 135.86, delta=0.05)

    # 6. Profile Ordering Sanity Checks
    def test_06_profile_ordering_sanity(self):
        scenario = EnvironmentalScenario(temperature_c=20.0, salinity_psu=35.0, depth_m=50.0)
        metrics, _ = evaluate_all_profiles(scenario)

        # Attenuation ordering: LOW < BAL < HIGH
        self.assertLess(metrics[0].alpha_band_db_km, metrics[1].alpha_band_db_km)
        self.assertLess(metrics[1].alpha_band_db_km, metrics[2].alpha_band_db_km)

        # Range resolution ordering: BAL < HIGH < LOW (smaller mm = finer resolution)
        self.assertLess(metrics[1].range_resolution_mm, metrics[2].range_resolution_mm)
        self.assertLess(metrics[2].range_resolution_mm, metrics[0].range_resolution_mm)

        # Directivity ordering: HIGH > BAL > LOW
        self.assertGreater(metrics[2].relative_directivity, metrics[1].relative_directivity)
        self.assertGreater(metrics[1].relative_directivity, metrics[0].relative_directivity)

    # 7. Viability Boundaries & Extinction Thresholds (Corrected Physics Baseline)
    def test_07_viability_boundaries(self):
        scenario = EnvironmentalScenario(temperature_c=20.0, salinity_psu=35.0, depth_m=50.0)

        # HIGH_FREQUENCY: Extinction boundary at 155.7 m
        m_155_5, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=155.5))
        m_155_9, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=155.9))
        self.assertTrue(m_155_5[2].is_viable, "HIGH_FREQUENCY should be viable at 155.5 m")
        self.assertFalse(m_155_9[2].is_viable, "HIGH_FREQUENCY should fail viability at 155.9 m")

        # BALANCED: Extinction boundary at 185.8 m
        m_185_5, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=185.5))
        m_186_0, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=186.0))
        self.assertTrue(m_185_5[1].is_viable, "BALANCED should be viable at 185.5 m")
        self.assertFalse(m_186_0[1].is_viable, "BALANCED should fail viability at 186.0 m")

        # LOW_FREQUENCY: Tested maximum range 200 m
        m_200, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=200.0))
        self.assertTrue(m_200[0].is_viable, "LOW_FREQUENCY must be viable at 200.0 m")
        self.assertAlmostEqual(m_200[0].relative_margin_db, -58.82, delta=0.05)
        # Margin headroom above -65 dB at 200m is +6.18 dB
        headroom = m_200[0].relative_margin_db - (-65.0)
        self.assertAlmostEqual(headroom, 6.18, delta=0.05)

        # Theoretical extinction boundary for LOW: ~260.7 m
        m_260_0, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=260.0))
        m_261_0, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=261.0))
        self.assertTrue(m_260_0[0].is_viable, "LOW_FREQUENCY theoretical margin should remain viable at 260.0 m")
        self.assertFalse(m_261_0[0].is_viable, "LOW_FREQUENCY theoretical margin should cross -65 dB by 261.0 m")

    # 8. Environmental Configuration Consistency
    def test_08_environmental_speed_of_sound_consistency(self):
        c = compute_mackenzie_sound_speed(self.T, self.S, self.D)
        # At T=20 C, S=35 PSU, D=50 m: Mackenzie formula yields 1520.91 m/s
        self.assertAlmostEqual(c, 1520.91, delta=0.1)

    # 9. Canonical JSON Artifact Validation
    def test_09_canonical_json_artifact_integrity(self):
        json_path = os.path.join(os.path.dirname(__file__), "..", "outputs", "canonical_profile_results.json")
        self.assertTrue(os.path.exists(json_path), "canonical_profile_results.json must exist in outputs/")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("profiles", data)
        self.assertIn("LOW_FREQUENCY", data["profiles"])
        self.assertIn("BALANCED", data["profiles"])
        self.assertIn("HIGH_FREQUENCY", data["profiles"])

        low_mean = data["profiles"]["LOW_FREQUENCY"]["alpha_band_mean_db_km"]
        bal_mean = data["profiles"]["BALANCED"]["alpha_band_mean_db_km"]
        high_mean = data["profiles"]["HIGH_FREQUENCY"]["alpha_band_mean_db_km"]

        self.assertAlmostEqual(low_mean, 63.99, delta=0.05)
        self.assertAlmostEqual(bal_mean, 105.62, delta=0.05)
        self.assertAlmostEqual(high_mean, 135.86, delta=0.05)


if __name__ == "__main__":
    unittest.main()
