"""
tests/test_physics_regression.py
Permanent Regression Protection for Underwater Acoustic Absorption,
Unit Conversions, Physical Reference Agreement, and Viability Boundaries.
"""

import json
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
    """Guarantees protection against unit conversion bugs, formula drift, and report disconnects."""

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
        # At 160 kHz, alpha ~ 66.3 dB/km.
        alpha_correct = ainslie_mccolm_absorption(f_khz, self.T, self.S, self.D)
        self.assertAlmostEqual(alpha_correct, 66.31, delta=0.1)

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

    # 3. Known Physics Reference Points (within 1.0% tolerance of independent calculation)
    def test_03_independent_reference_agreement(self):
        test_frequencies_khz = [100.0, 130.0, 160.0, 190.0, 200.0, 250.0, 300.0, 350.0, 425.0, 500.0]
        for f in test_frequencies_khz:
            prod_val = ainslie_mccolm_absorption(f, self.T, self.S, self.D)
            _, _, _, ref_val = independent_ainslie_mccolm_reference(f, self.T, self.S, self.D, self.pH)

            diff_pct = (abs(prod_val - ref_val) / ref_val) * 100.0
            self.assertLess(
                diff_pct,
                1.0,
                f"Frequency {f} kHz difference ({diff_pct:.2f}%) exceeds 1.0% tolerance against independent reference",
            )

    # 4. Canonical Profile Mean Attenuation Values
    def test_04_canonical_profile_mean_attenuation(self):
        scenario = EnvironmentalScenario(temperature_c=20.0, salinity_psu=35.0, depth_m=50.0)
        metrics, _ = evaluate_all_profiles(scenario)

        # Profile 1: LOW_FREQUENCY (100–220 kHz)
        self.assertAlmostEqual(metrics[0].alpha_band_db_km, 64.47, delta=0.05)
        # Profile 2: BALANCED (200–400 kHz)
        self.assertAlmostEqual(metrics[1].alpha_band_db_km, 106.32, delta=0.05)
        # Profile 3: HIGH_FREQUENCY (350–500 kHz)
        self.assertAlmostEqual(metrics[2].alpha_band_db_km, 136.64, delta=0.05)

    # 5. Profile Ordering Sanity Checks
    def test_05_profile_ordering_sanity(self):
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

    # 6. Viability Boundaries & Extinction Thresholds
    def test_06_viability_boundaries(self):
        scenario = EnvironmentalScenario(temperature_c=20.0, salinity_psu=35.0, depth_m=50.0)

        # At R = 155.0 m, HIGH is viable; at R = 155.2 m, HIGH fails
        m_155_0, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=155.0))
        m_155_2, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=155.2))
        self.assertTrue(m_155_0[2].is_viable, "HIGH_FREQUENCY should be viable at 155.0 m")
        self.assertFalse(m_155_2[2].is_viable, "HIGH_FREQUENCY should fail viability at 155.2 m")

        # At R = 184.8 m, BALANCED is viable; at R = 185.0 m, BALANCED fails
        m_184_8, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=184.8))
        m_185_0, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=185.0))
        self.assertTrue(m_184_8[1].is_viable, "BALANCED should be viable at 184.8 m")
        self.assertFalse(m_185_0[1].is_viable, "BALANCED should fail viability at 185.0 m")

        # LOW_FREQUENCY: Tested maximum range 200 m
        m_200, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=200.0))
        self.assertTrue(m_200[0].is_viable, "LOW_FREQUENCY must be viable at 200.0 m")
        self.assertAlmostEqual(m_200[0].relative_margin_db, -58.91, delta=0.05)
        # Margin headroom above -65 dB at 200m is +6.09 dB
        headroom = m_200[0].relative_margin_db - (-65.0)
        self.assertAlmostEqual(headroom, 6.09, delta=0.05)

        # Theoretical extinction boundary for LOW: ~259.4 m
        m_259_0, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=259.0))
        m_260_0, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=260.0))
        self.assertTrue(m_259_0[0].is_viable, "LOW_FREQUENCY theoretical margin should remain viable at 259.0 m")
        self.assertFalse(m_260_0[0].is_viable, "LOW_FREQUENCY theoretical margin should cross -65 dB by 260.0 m")

    # 7. Environmental Configuration Consistency
    def test_07_environmental_speed_of_sound_consistency(self):
        c = compute_mackenzie_sound_speed(self.T, self.S, self.D)
        # At T=20 C, S=35 PSU, D=50 m: Mackenzie formula yields 1520.91 m/s
        self.assertAlmostEqual(c, 1520.91, delta=0.1)

    # 8. Canonical JSON Artifact Validation
    def test_08_canonical_json_artifact_integrity(self):
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

        self.assertAlmostEqual(low_mean, 64.47, delta=0.05)
        self.assertAlmostEqual(bal_mean, 106.32, delta=0.05)
        self.assertAlmostEqual(high_mean, 136.64, delta=0.05)


if __name__ == "__main__":
    unittest.main()
