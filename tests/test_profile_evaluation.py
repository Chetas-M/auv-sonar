"""
Automated unit tests for Priority 1: Profile Performance Evaluation & Selection.
Verifies the 12 required test conditions specified in the approved implementation plan.
"""

import unittest
import numpy as np

from src.profile_evaluator import (
    EnvironmentalScenario,
    ProfilePerformanceMetrics,
    EvaluationDecision,
    evaluate_all_profiles,
    evaluate_single_profile,
    compute_mackenzie_sound_speed,
    ainslie_mccolm_absorption,
)


class TestProfilePerformanceEvaluation(unittest.TestCase):
    """Verifies profile evaluation, attenuation, viability, and mission selection logic."""

    def setUp(self):
        self.baseline_scenario = EnvironmentalScenario(
            range_m=50.0,
            depth_m=50.0,
            temperature_c=20.0,
            salinity_psu=35.0,
            turbidity=0.0,
            ambient_noise_db=0.0,
        )
        self.metrics, self.decision = evaluate_all_profiles(self.baseline_scenario)

    # 1. All 3 profiles evaluate successfully
    def test_01_all_profiles_evaluate(self):
        self.assertEqual(len(self.metrics), 3)
        names = [m.name for m in self.metrics]
        self.assertIn("LOW_FREQUENCY", names)
        self.assertIn("BALANCED", names)
        self.assertIn("HIGH_FREQUENCY", names)

    # 2. No NaN or Inf
    def test_02_no_nan_or_inf(self):
        for m in self.metrics:
            self.assertFalse(np.isnan(m.alpha_band_db_km))
            self.assertFalse(np.isinf(m.alpha_band_db_km))
            self.assertFalse(np.isnan(m.transmission_loss_db))
            self.assertFalse(np.isinf(m.transmission_loss_db))
            self.assertFalse(np.isnan(m.relative_margin_db))
            self.assertFalse(np.isinf(m.relative_margin_db))
            self.assertFalse(np.isnan(m.range_resolution_mm))
            self.assertFalse(np.isnan(m.relative_directivity))
            for a in m.alpha_points_db_km:
                self.assertFalse(np.isnan(a))
                self.assertFalse(np.isinf(a))

    # 3. Finite positive attenuation
    def test_03_positive_finite_attenuation(self):
        for m in self.metrics:
            self.assertGreater(m.alpha_band_db_km, 0.0)
            for a in m.alpha_points_db_km:
                self.assertGreater(a, 0.0)

    # 4. Monotonic Transmission Loss with range
    def test_04_transmission_loss_increases_with_range(self):
        m10, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=10.0))
        m50, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=50.0))
        m200, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=200.0))
        for i in range(3):
            self.assertLess(m10[i].transmission_loss_db, m50[i].transmission_loss_db)
            self.assertLess(m50[i].transmission_loss_db, m200[i].transmission_loss_db)

    # 5. Baseline attenuation ordering across frequency bands
    def test_05_baseline_attenuation_ordering(self):
        alpha_low = self.metrics[0].alpha_band_db_km
        alpha_bal = self.metrics[1].alpha_band_db_km
        alpha_high = self.metrics[2].alpha_band_db_km
        self.assertLess(alpha_low, alpha_bal, "Profile 1 attenuation must be lower than Profile 2")
        self.assertLess(alpha_bal, alpha_high, "Profile 2 attenuation must be lower than Profile 3")

    # 6. Theoretical range resolution: BALANCED has the finest resolution
    def test_06_range_resolution_ordering(self):
        r_low = self.metrics[0].range_resolution_mm
        r_bal = self.metrics[1].range_resolution_mm
        r_high = self.metrics[2].range_resolution_mm
        # BALANCED (200 kHz BW) gives ~3.75 mm, HIGH (150 kHz) gives ~5.0 mm, LOW (120 kHz) gives ~6.25 mm
        self.assertLess(r_bal, r_high, "BALANCED must provide finer range resolution than HIGH_FREQUENCY")
        self.assertLess(r_high, r_low, "HIGH_FREQUENCY must provide finer range resolution than LOW_FREQUENCY")
        self.assertAlmostEqual(r_bal, 3.75, delta=0.2)

    # 7. Theoretical directivity metric: HIGH_FREQUENCY has highest directivity
    def test_07_theoretical_directivity_ordering(self):
        d_low = self.metrics[0].relative_directivity
        d_bal = self.metrics[1].relative_directivity
        d_high = self.metrics[2].relative_directivity
        self.assertGreater(d_high, d_bal, "HIGH_FREQUENCY must have higher directivity than BALANCED")
        self.assertGreater(d_bal, d_low, "BALANCED must have higher directivity than LOW_FREQUENCY")

    # 8. Band confinement of 5 evaluation frequency points
    def test_08_frequency_points_within_band(self):
        # LOW_FREQUENCY: 100 to 220 kHz
        self.assertAlmostEqual(self.metrics[0].f_points_khz[0], 100.0)
        self.assertAlmostEqual(self.metrics[0].f_points_khz[-1], 220.0)
        # BALANCED: 200 to 400 kHz
        self.assertAlmostEqual(self.metrics[1].f_points_khz[0], 200.0)
        self.assertAlmostEqual(self.metrics[1].f_points_khz[-1], 400.0)
        # HIGH_FREQUENCY: 350 to 500 kHz
        self.assertAlmostEqual(self.metrics[2].f_points_khz[0], 350.0)
        self.assertAlmostEqual(self.metrics[2].f_points_khz[-1], 500.0)

    # 9. Fallback to LOW_FREQUENCY at long range (propagation limited)
    def test_09_long_range_viability_fallback(self):
        long_range_scenario = EnvironmentalScenario(range_m=200.0)
        m, dec = evaluate_all_profiles(long_range_scenario, mission_objective="SURVEY")
        self.assertEqual(dec.candidate_name, "LOW_FREQUENCY")
        self.assertTrue(m[0].is_viable, "LOW_FREQUENCY must remain viable at 200m")
        self.assertFalse(m[1].is_viable, "BALANCED should exceed viability threshold at 200m")
        self.assertFalse(m[2].is_viable, "HIGH_FREQUENCY should exceed viability threshold at 200m")

    # 10. Survey Mode selects BALANCED at short/medium range
    def test_10_survey_mode_selects_balanced(self):
        short_scenario = EnvironmentalScenario(range_m=25.0)
        _, dec = evaluate_all_profiles(short_scenario, mission_objective="SURVEY")
        self.assertEqual(dec.candidate_name, "BALANCED")
        self.assertEqual(dec.candidate_profile_id, 2)

    # 11. Directivity Mode selects HIGH_FREQUENCY at short/medium range
    def test_11_directivity_mode_selects_high_frequency(self):
        short_scenario = EnvironmentalScenario(range_m=25.0)
        _, dec = evaluate_all_profiles(short_scenario, mission_objective="DIRECTIVITY")
        self.assertEqual(dec.candidate_name, "HIGH_FREQUENCY")
        self.assertEqual(dec.candidate_profile_id, 3)

    # 12. Determinism check: identical inputs yield identical outputs
    def test_12_determinism(self):
        m_a, d_a = evaluate_all_profiles(self.baseline_scenario, mission_objective="SURVEY")
        m_b, d_b = evaluate_all_profiles(self.baseline_scenario, mission_objective="SURVEY")
        self.assertEqual(d_a.candidate_profile_id, d_b.candidate_profile_id)
        self.assertEqual(d_a.profile_selection_confidence, d_b.profile_selection_confidence)
        for i in range(3):
            self.assertEqual(m_a[i].transmission_loss_db, m_b[i].transmission_loss_db)
            self.assertEqual(m_a[i].relative_margin_db, m_b[i].relative_margin_db)


if __name__ == "__main__":
    unittest.main()
