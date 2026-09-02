"""
Automated parity test verifying that the MATLAB implementation files
match the Single Source of Truth parameters, formulas, and locked specifications.
"""

import os
import unittest
import re


class TestMatlabArchitectureParity(unittest.TestCase):
    """Verifies existence, parameter alignment, and syntax integrity of MATLAB files."""

    def setUp(self):
        self.matlab_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "matlab")
        self.required_files = [
            "config_sonar.m",
            "profile_definitions.m",
            "generate_lfm_chirp.m",
            "channel_model.m",
            "adaptive_controller.m",
            "dac_quantize.m",
            "power_model.m",
            "export_c_headers.m",
            "run_validation_suite.m",
            "run_simulation.m",
            "README.md",
        ]

    def test_all_matlab_files_exist(self):
        """Verify all 10 MATLAB scripts and README exist."""
        for filename in self.required_files:
            file_path = os.path.join(self.matlab_dir, filename)
            self.assertTrue(os.path.exists(file_path), f"Missing MATLAB file: {filename}")

    def test_config_sonar_parameters(self):
        """Verify locked implementation parameters in config_sonar.m."""
        cfg_path = os.path.join(self.matlab_dir, "config_sonar.m")
        with open(cfg_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("cfg.Fs = 4.0e6;", content)
        self.assertIn("cfg.DAC_bits = 12;", content)
        self.assertIn("cfg.DAC_max_code = 4095;", content)
        self.assertIn("cfg.DAC_midscale = 2048;", content)
        self.assertIn("cfg.Tp_s = 0.002;", content)
        self.assertIn("cfg.PRI_s = 0.020;", content)
        self.assertIn("cfg.num_profiles = 3;", content)
        self.assertIn("STM32G474", content)

    def test_profile_definitions(self):
        """Verify exact canonical profile names, sweep bands, and headers in profile_definitions.m."""
        prof_path = os.path.join(self.matlab_dir, "profile_definitions.m")
        with open(prof_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Profile 1: LOW_FREQUENCY (100k - 220k)
        self.assertIn("LOW_FREQUENCY", content)
        self.assertIn("100.0e3", content)
        self.assertIn("220.0e3", content)
        self.assertIn("160.0e3", content)
        self.assertIn("120.0e3", content)
        self.assertIn("chirp_low_frequency.h", content)

        # Profile 2: BALANCED (200k - 400k)
        self.assertIn("BALANCED", content)
        self.assertIn("200.0e3", content)
        self.assertIn("400.0e3", content)
        self.assertIn("300.0e3", content)
        self.assertIn("200.0e3", content)
        self.assertIn("chirp_balanced.h", content)

        # Profile 3: HIGH_FREQUENCY (350k - 500k)
        self.assertIn("HIGH_FREQUENCY", content)
        self.assertIn("350.0e3", content)
        self.assertIn("500.0e3", content)
        self.assertIn("425.0e3", content)
        self.assertIn("150.0e3", content)
        self.assertIn("chirp_high_frequency.h", content)

    def test_lfm_math_formula(self):
        """Verify analytical phase integration formula in generate_lfm_chirp.m."""
        lfm_path = os.path.join(self.matlab_dir, "generate_lfm_chirp.m")
        with open(lfm_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Phase integration: 2*pi*(f_0*t + 0.5*k*t^2)
        self.assertIn("0.5 * k", content)
        self.assertIn("2.0 * pi", content)
        # Hann window formula: 0.5*(1 - cos(2*pi*n/(Np-1)))
        self.assertIn("cos(2.0 * pi * n / (Np - 1))", content)

    def test_channel_model_score_formula(self):
        """Verify Channel Quality Score Q calculation in channel_model.m."""
        ch_path = os.path.join(self.matlab_dir, "channel_model.m")
        with open(ch_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Mackenzie", content)
        self.assertIn("cfg.w_environment", content)
        self.assertIn("Q_raw", content)

    def test_adaptive_controller_hysteresis_debounce(self):
        """Verify hysteresis deadbands and debounce persistence in adaptive_controller.m."""
        ctrl_path = os.path.join(self.matlab_dir, "adaptive_controller.m")
        with open(ctrl_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check directional deadband thresholds
        self.assertIn("cfg.thresh_bal_to_high", content)
        self.assertIn("cfg.thresh_high_to_bal", content)
        self.assertIn("cfg.thresh_low_to_bal", content)
        self.assertIn("cfg.thresh_bal_to_low", content)
        self.assertIn("debounce_count >= cfg.debounce_count", content)

    def test_validation_suite_tests_count(self):
        """Verify run_validation_suite.m implements all 23 tests."""
        suite_path = os.path.join(self.matlab_dir, "run_validation_suite.m")
        with open(suite_path, "r", encoding="utf-8") as f:
            content = f.read()

        for t_idx in range(1, 24):
            self.assertIn(f"report_test({t_idx},", content, f"Missing test #{t_idx} in run_validation_suite.m")

    def test_run_simulation_plots_count(self):
        """Verify run_simulation.m generates all 13 plots."""
        sim_path = os.path.join(self.matlab_dir, "run_simulation.m")
        with open(sim_path, "r", encoding="utf-8") as f:
            content = f.read()

        for p_idx in range(1, 14):
            plot_str = f"0{p_idx}_" if p_idx < 10 else f"{p_idx}_"
            self.assertIn(plot_str, content, f"Missing plot #{p_idx} save in run_simulation.m")


if __name__ == "__main__":
    unittest.main()
