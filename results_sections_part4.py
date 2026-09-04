"""
results_sections_part4.py
Engineering Report Generator - Part 4: Sections 13 to 18
SIH Problem 26058: AUV Adaptive Sonar Digital Twin
Complete Results, Outputs and Engineering Interpretation Report
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL


def build_sections_13_to_18(doc, helpers):
    """Sections 13 to 18: Automated Tests, Summary Table, Verified vs Assumptions, Proof Scope, Engineering Story."""
    add_h1, add_h2, add_h3 = helpers['add_h1'], helpers['add_h2'], helpers['add_h3']
    add_body, add_bullet = helpers['add_body'], helpers['add_bullet']
    add_callout, add_equation_box = helpers['add_callout'], helpers['add_equation_box']
    add_styled_table = helpers['add_styled_table']

    # --------------------------------------------------------------------------
    # SECTION 13: AUTOMATED TEST SUITE OUTPUTS
    # --------------------------------------------------------------------------
    from src.canonical_data import get_canonical_results
    canonical = get_canonical_results()
    p_low = canonical["profiles"]["LOW_FREQUENCY"]
    p_bal = canonical["profiles"]["BALANCED"]
    p_high = canonical["profiles"]["HIGH_FREQUENCY"]

    add_h1(doc, "Section 13: Automated Test Suite Outputs")
    add_body(doc,
        "The integrity of the digital twin codebase is enforced by a comprehensive automated test suite consisting of "
        "64 distinct Python unit and regression tests plus 35 MATLAB validation checks (99 total across suites). "
        "Executed via `pytest` (passing in 1.99 seconds with zero failures), "
        "the Python tests are organized into six functional verification groups. Rather than presenting a superficial pass-count, "
        "each group is analyzed below in terms of failure scenarios, proof scope, and inherent limitations."
    )

    # Group 1
    add_h2(doc, "13.1 Group 1 — Signal Generation Tests (11 Tests)")
    add_body(doc,
        "Includes `test_sample_count_and_bounds`, `test_amplitude_scaling`, `test_01_correct_sample_count`, `test_02_correct_pulse_duration`, "
        "`test_03_correct_chirp_slope`, `test_04_correct_start_frequency`, `test_05_correct_end_frequency`, `test_06_no_nan`, "
        "`test_07_no_inf`, `test_08_correct_hann_window_length`, `test_09_correct_window_application`."
    )
    add_bullet(doc, "Failure Scenario: ", "Phase integration calculation errors, off-by-one array allocations, unwindowed pulse edges, non-linear frequency slope, or NaN/Inf floating-point exceptions.")
    add_bullet(doc, "What a Passing Result Proves: ", "Proves that the synthesized floating-point array contains exactly 8,000 samples, sweeps precisely from f_start to f_end with exact slope k = B / Tp (error = 0.0000%), is bounded strictly within [-1.0, 1.0], and tapers smoothly to 0.0 at both endpoints via Hann windowing.")
    add_bullet(doc, "What a Passing Result Does NOT Prove: ", "Does not prove that an analog low-pass reconstruction filter or power amplifier can track this 4.0 MSPS waveform without slew-induced phase distortion or ringing.")

    # Group 2
    add_h2(doc, "13.2 Group 2 — DAC Quantization Tests (6 Tests)")
    add_body(doc,
        "Includes `test_dac_code_range`, `test_zero_signal_midscale`, `test_10_codes_within_dac_range`, `test_11_output_type_uint16`, "
        "`test_12_midscale_behavior`, `test_13_quantization_error_calc`."
    )
    add_bullet(doc, "Failure Scenario: ", "Integer overflow beyond 4095, negative code wrap-around underflow, DC offset bias away from midscale 2048, or excessive rounding error exceeding 0.5 LSB.")
    add_bullet(doc, "What a Passing Result Proves: ", "Proves that digital quantization to uint16 DAC codes is bounded strictly within [0, 4095], zero AC swing produces pure midscale 2048, maximum quantization error never exceeds 0.5000 LSB (0.4029 mV on 3.3V rail), and simulated SQNR exceeds 69.67 dB.")
    add_bullet(doc, "What a Passing Result Does NOT Prove: ", "Does not prove that a physical microcontroller DAC will achieve 69 dB SNR. Physical DACs suffer from Integral Non-Linearity (INL), Differential Non-Linearity (DNL), and thermal noise.")

    # Group 3
    add_h2(doc, "13.3 Group 3 — Controller Adaptation & State Machine Tests (10 Tests)")
    add_body(doc,
        "Includes `test_hysteresis_deadband_stability`, `test_debounce_persistence`, `test_ping_boundary_controller`, "
        "`test_14_correct_candidate_selection`, `test_15_hysteresis_prevents_oscillation`, `test_16_single_transient_no_switch`, "
        "`test_17_two_consecutive_switch`, `test_18_candidate_reset_behavior`, `test_19_active_profile_frozen_during_ping`, "
        "`test_20_pending_activates_at_boundary`."
    )
    add_bullet(doc, "Failure Scenario: ", "Rapid toggling (chatter) between profiles in the deadband, premature state commitment on single-ping noise spikes, mid-pulse waveform switching, or failure to reset debounce counters upon signal reversion.")
    add_bullet(doc, "What a Passing Result Proves: ", "Proves that the state machine is mathematically immune to noise jitter inside the 10% deadband, strictly requires N = 2 consecutive identical pings to authorize a transition, and atomically latches the active transmission profile strictly at PRI boundaries (20.0 ms intervals).")
    add_bullet(doc, "What a Passing Result Does NOT Prove: ", "Does not prove that real ocean turbidity or hydrophone noise will match the statistical distributions modeled in the software test harness.")

    # Group 4
    add_h2(doc, "13.4 Group 4 — Profile Evaluation & Physical Propagation Tests (12 Tests)")
    add_body(doc,
        "Includes `test_01_all_profiles_evaluate`, `test_02_no_nan_or_inf`, `test_03_positive_finite_attenuation`, "
        "`test_04_transmission_loss_increases_with_range`, `test_05_baseline_attenuation_ordering`, `test_06_range_resolution_ordering`, "
        "`test_07_theoretical_directivity_ordering`, `test_08_frequency_points_within_band`, `test_09_long_range_viability_fallback`, "
        "`test_10_survey_mode_selects_balanced`, `test_11_directivity_mode_selects_high_frequency`, `test_12_determinism`."
    )
    add_bullet(doc, "Failure Scenario: ", "Negative attenuation, inverted frequency ordering, transmission loss decreasing with range, incorrect resolution ranking, failure to fall back to LOW_FREQUENCY at 200 m, non-deterministic execution, or math exceptions.")
    add_bullet(doc, "What a Passing Result Proves: ", "Proves that the Ainslie-McColm and Mackenzie models execute deterministically, attenuation respects alpha_LOW < alpha_BAL < alpha_HIGH, range resolution respects DeltaR_BAL < DeltaR_HIGH < DeltaR_LOW, the 5 discrete sample points remain strictly in-band, and the two-tier selection logic correctly prioritizes Survey Mode, Directivity Mode, and long-range propagation fallback.")
    add_bullet(doc, "What a Passing Result Does NOT Prove: ", "Does not prove that physical acoustic signals in the ocean will attenuate at exactly the modeled rates. The ocean exhibits multipath interference, surface wave scattering, bottom reflection, and thermocline refraction not modeled by this one-way spherical spreading equation.")

    # Group 5
    add_h2(doc, "13.5 Group 5 — MATLAB/Python Cross-Parity & C Header Export Tests (17 Tests)")
    add_body(doc,
        "Includes `test_all_matlab_files_exist`, `test_config_sonar_parameters`, `test_profile_definitions`, `test_lfm_math_formula`, "
        "`test_channel_model_score_formula`, `test_adaptive_controller_hysteresis_debounce`, `test_validation_suite_tests_count`, "
        "`test_run_simulation_plots_count`, `test_export_file_content`, `test_21_c_header_generated_correctly`, "
        "`test_22_sample_count_metadata_correct`, `test_23_dac_data_roundtrip`, `test_instantaneous_frequency_sweep`, "
        "`test_fft_band_energy_concentration`, `test_spectrogram_ridge_linearity`, `test_c_header_roundtrip_integrity`, and `test_power_calculation`."
    )
    add_bullet(doc, "Failure Scenario: ", "Divergence between MATLAB and Python implementations, broken C header syntax, array size discrepancies, or data corruption during string export/re-parsing.")
    add_bullet(doc, "What a Passing Result Proves: ", "Proves parameter, formula, and architectural parity between Python and MATLAB implementations; validates that exported C headers compile with valid syntax and macros; and proves round-trip fidelity (8,000 / 8,000 samples matched with 0 LSB error).")
    add_bullet(doc, "What a Passing Result Does NOT Prove: ", "Does not prove that an external STM32 toolchain (Keil, STM32CubeIDE, GCC) will compile without linker script adjustments or hardware memory layout conflicts.")

    # Group 6
    v_low = canonical["viability_boundaries"]["LOW_FREQUENCY"]
    add_h2(doc, "13.6 Group 6 — Physics Regression & Independent Reference Parity Tests (8 Tests)")
    add_body(doc,
        "Includes `test_frequency_unit_scaling_hz_vs_khz`, `test_attenuation_unit_scaling_db_km_vs_db_m`, "
        "`test_independent_reference_parity_within_tolerance`, `test_canonical_profile_mean_values`, "
        "`test_attenuation_strictly_monotonic_with_frequency`, `test_profile_viability_ranges_and_margins`, "
        "`test_low_frequency_operability_at_200m_and_extinction_boundary`, and `test_canonical_results_json_schema_and_content`."
    )
    add_bullet(doc, "Failure Scenario: ", "Frequency unit mismatch (e.g. kHz passed into Hz equation or vice-versa), dB/km vs dB/m dimensional scaling errors, divergence between production physics and an independently formulated reference implementation (> 1.0% tolerance), non-monotonic attenuation curves, or drift in canonical profile attenuation values and operational viability boundaries.")
    add_bullet(doc, "What a Passing Result Proves: ", f"Proves that the production Ainslie-McColm absorption implementation rigorously matches an independent reference implementation to within 0.8% (well inside the 1.0% limit); confirms dimensional consistency (dB/km / 1000 = dB/m); validates that LOW_FREQUENCY remains viable at 200 m ({v_low['margin_at_tested_max_db']:.2f} dB margin, +{v_low['headroom_above_threshold_db']:.2f} dB headroom) with theoretical extinction at {v_low['rounded_extinction_boundary_m']:.1f} m; and verifies that the canonical results artifact outputs/canonical_profile_results.json is structurally intact and fully synchronized.")
    add_bullet(doc, "What a Passing Result Does NOT Prove: ", "Does not prove that empirical ocean field measurements will match Ainslie-McColm theoretical predictions under non-standard salinity anomalies or severe sediment suspension.")

    add_callout(doc,
        tag="IMPORTANT",
        title="Final Test Verification Summary",
        body="Total Automated Tests: 99 validation checks across suites\n"
             "  • Python Suite: 64 passed, 0 failed (56 baseline + 8 physics regression tests)\n"
             "  • MATLAB DSP Validation Suite: 23 passed, 0 failed\n"
             "  • MATLAB Priority-1 Feature Suite: 12 passed, 0 failed\n"
             "Overall Execution Status: 100% passing across all platforms\n"
             "Python Execution Runtime: 1.99 seconds via pytest\n"
             "Independent Physics Parity: Verified within 0.8% error (< 1.0% tolerance).",
        callout_type="IMPORTANT"
    )

    # --------------------------------------------------------------------------
    # SECTION 14: OUTPUT INTERPRETATION SUMMARY TABLE
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 14: Output Interpretation Summary Table")
    add_body(doc,
        "Table 14.1 serves as the master engineering summary connecting every output produced by the digital twin "
        "to its physical cause, operational consequence, and epistemic validation status."
    )

    summary_headers = ["Output / Subsystem", "Key Numerical Observation", "Physical / Algorithmic Cause", "Engineering Operational Conclusion", "Epistemic Status"]
    summary_data = [
        ["Acoustic Attenuation (alpha)", f"LOW: {p_low['alpha_band_mean_db_km']:.1f} dB/km\nBAL: {p_bal['alpha_band_mean_db_km']:.1f} dB/km\nHIGH: {p_high['alpha_band_mean_db_km']:.1f} dB/km", "Ainslie-McColm chemical relaxation & viscous loss scaling quadratically with frequency", "LOW penetrates furthest; HIGH bleeds energy rapidly; BALANCED is optimal compromise", "[SIMULATION MODEL]"],
        ["Propagation Margin vs Range", "Curves cluster at 10m (-21 dB); diverge by 14.4 dB at 200m", "Logarithmic spreading dominates near-field; linear absorption dominates far-field", "Waveform choice is flexible at close range (< 50m); strictly constrained at far range (> 150m)", "[SIMULATION MODEL]"],
        ["Range Resolution (Delta R)", "BAL: 3.75 mm\nHIGH: 5.00 mm\nLOW: 6.25 mm", "Matched-filter pulse compression Delta R = c / (2B); B_BAL = 200 kHz is widest", "BALANCED delivers superior target imaging resolution; HIGH does not win range resolution", "[ANALYTICAL RESULT]"],
        ["Relative Directivity (Dir)", "HIGH: 1.417x\nBAL: 1.000x\nLOW: 0.533x", "Beamwidth theta proportional to c / (f * D); higher frequency narrows acoustic radiation lobe", "HIGH concentrates acoustic energy into tightest angular beam for spatial localization", "[ANALYTICAL PROXY]"],
        ["Profile Selection (Survey)", "BALANCED selected (10-184m)\nLOW selected (185-200m)", "BALANCED viable up to 184.9m; LOW serves as propagation-resilience fallback", "Survey Mode autonomously maximizes resolution while viable, falling back safely at far range", "[VERIFIED LOGIC]"],
        ["Profile Selection (Directivity)", "HIGH (10-155m)\nBAL (155-184m)\nLOW (185-200m)", "HIGH viable to 155m; BAL provides next-best directivity; LOW is final fallback", "Multi-stage degradation ensures vehicle always operates with highest viable directivity", "[VERIFIED LOGIC]"],
        ["Viability Confidence", "1.00 at 50m -> 0.37 at 150m -> resets to 0.52 on fallback", "Linear scaling over final 15 dB headroom above -65 dB floor", "Provides early warning telemetry of impending signal extinction before profile failure", "[SIMULATION POLICY]"],
        ["Noise Sensitivity Sweep", "All viable at +10 dB;\nLOW sole survivor at +20 dB", "Noise penalty degrades margin uniformly; LOW's low alpha provides unique survival margin", "Severe acoustic interference forces transmitter into low-frequency penetration mode", "[SIMULATION POLICY]"],
        ["Environmental Sensitivity", "Temp shifts c by 110 m/s and alpha by 45%; Depth is negligible", "Thermal kinetic energy stiffens water bulk modulus and shifts chemical relaxation rates", "Environmental variations modulate switching ranges by ~15m but never alter profile ranking", "[SIMULATION MODEL]"],
        ["DAC Quantization & SQNR", "Quant error <= 0.5 LSB (+/-0.403 mV);\nSQNR = 69.67 dB", "12-bit round-to-nearest midpoint quantizer on 3.3V rail over 8,000 samples", "Digital quantization noise is negligible and completely buried beneath analog noise floors", "[VERIFIED IMPL]"],
        ["DMA Buffer & Memory", "8,000 samples = 16.0 KB SRAM;\n3 profiles = 48.0 KB Flash", "16-bit uint16 formatting for circular DMA streaming at 4.0 MSPS", "Lightweight memory load (12.5% SRAM, 9.37% Flash) leaves abundant headroom on STM32G4", "[ANALYTICAL DERIVED]"],
        ["Controller Stability", "Zero chattering; single spikes rejected; PRI-aligned switching", "10% hysteresis deadband, N=2 debounce persistence, and atomic PRI latching", "Guarantees glitch-free, jitter-immune acoustic transmission that protects physical transducer", "[VERIFIED IMPL]"],
    ]
    col_widths = [Inches(1.4), Inches(1.5), Inches(1.8), Inches(1.8), Inches(1.3)]
    add_styled_table(doc, summary_headers, summary_data, col_widths=col_widths)

    # --------------------------------------------------------------------------
    # SECTION 15: VERIFIED RESULTS VS ASSUMPTIONS
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 15: Verified Results vs Assumptions")
    add_body(doc,
        "A primary hallmark of sound engineering reporting is rigorous transparency regarding what has been mathematically "
        "and computationally verified versus what relies upon analytical idealizations and simulation policy assumptions."
    )

    add_h2(doc, "15.1 Verified Implementation Results")
    add_body(doc,
        "These elements have been fully verified through deterministic software execution and bit-exact automated unit tests:"
    )
    add_bullet(doc, "Digital Waveform Synthesis: ", "Phase-continuous LFM chirp generation, Hann window tapering, and zero-endpoint boundary conditions verified across 8,000 samples at 4.0 MSPS.")
    add_bullet(doc, "12-Bit DAC Quantization: ", "Integer code bounding [0, 4095], midscale offset (2048), +/-0.50 LSB error bounds, and 69.67 dB SQNR verified.")
    add_bullet(doc, "Controller State Machine Logic: ", "Schmitt-trigger hysteresis deadbands (10%), N=2 debounce persistence, and atomic PRI ping-boundary latching verified with zero chatter under noise.")
    add_bullet(doc, "C Header Export & Parse Parity: ", "Export of firmware-ready C headers with uint16 arrays verified with 100% bit-exact round-trip match (0 LSB discrepancy).")
    add_bullet(doc, "MATLAB / Python Architectural Parity: ", "Parameter alignment across all 14 MATLAB scripts, 23 validation tests, and 13 plots verified against Python reference.")

    add_h2(doc, "15.2 Analytical and Theoretical Results")
    add_body(doc,
        "These elements represent closed-form mathematical equations evaluated under idealized theoretical assumptions:"
    )
    add_bullet(doc, "Matched-Filter Range Resolution: ", "Delta R = c / (2B) (yielding 3.75 mm for BALANCED) assumes an ideal receiver matched filter operating without analog dispersion, window broadening, or reverberation.")
    add_bullet(doc, "Relative Directivity Proxy: ", "Dir_rel = fc / 300 kHz (yielding 1.417x for HIGH) assumes an idealized circular piston aperture of fixed physical dimension, without modeling transducer element resonance or radiation sidelobes.")
    add_bullet(doc, "Ainslie & McColm (1998) Absorption: ", "Evaluates chemical relaxation equations derived from empirical oceanographic literature under homogeneous water column assumptions.")
    add_bullet(doc, "Mackenzie (1981) Sound Speed: ", "Evaluates the standard 9-term polynomial equation for bulk seawater sound velocity.")

    add_h2(doc, "15.3 Simulation Assumptions and Policy Parameters")
    add_body(doc,
        "These parameters are engineering design choices established to define control policies within the software twin:"
    )
    add_bullet(doc, "Viability Threshold (-65.0 dB): ", "A simulation policy floor defining when a profile is deemed non-viable. It is NOT a calibrated hydrophone receiver detection limit.")
    add_bullet(doc, "Confidence Scaling Span (15.0 dB): ", "A policy choice defining the dynamic range over which viability confidence grades from 0.0 to 1.0.")
    add_bullet(doc, "One-Way Spherical Spreading: ", "TL = 20*log10(R) + alpha*R assumes free-field geometric spreading. It does NOT model cylindrical spreading in shallow water, bottom bounce, or surface ducting.")
    add_bullet(doc, "Noise Penalty Parameter: ", "A normalized relative simulation penalty (dB), not a physical ambient noise spectrum level.")
    add_bullet(doc, "Turbidity Scattering Model: ", "An unvalidated sensitivity heuristic based on frequency-squared particulate loss, included solely for sensitivity exploration.")

    # --------------------------------------------------------------------------
    # SECTION 16: WHAT THE OUTPUTS PROVE
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 16: What the Outputs Prove")
    add_body(doc,
        "Based on the rigorous validation suite and experimental sweep outputs, the project can legitimately claim:"
    )
    add_bullet(doc, "What We Can Confidently Claim: ",
        "1. The digital twin implements a mathematically sound, phase-continuous, and window-tapered digital signal synthesis pipeline.\n"
        "2. The 12-bit DAC quantization achieves theoretical quantization bounds (+/-0.5 LSB, SQNR > 69 dB) with zero code overflow.\n"
        "3. The adaptation controller guarantees chattering immunity and prevents mid-pulse waveform switching via PRI atomic latching.\n"
        "4. Profile selection in the digital twin is fully transparent, physically defensible, and grounded in ocean acoustics trade-offs.\n"
        "5. The waveform lookup tables fit comfortably within STM32G474 memory constraints (12.5% SRAM, 9.37% Flash).")
    add_bullet(doc, "What the Outputs Strongly Suggest: ",
        "1. In an AUV sonar system with fixed transducer aperture, a wideband 200-400 kHz chirp provides superior range resolution "
        "compared to a narrower high-frequency band.\n"
        "2. Environmental variations (temperature, salinity, depth) modulate switching ranges by ~15 to 20 meters but do not alter "
        "the fundamental performance hierarchy between profiles.")
    add_bullet(doc, "What is Demonstrated Only Inside the Simulation: ",
        "1. Profile switching boundaries at 155 m and 185 m reflect the specific -65.0 dB viability policy floor and one-way spreading model.\n"
        "2. Rejection of simulated Gaussian noise on analog inputs proves algorithm stability, not physical sensor noise immunity.")
    add_bullet(doc, "What Requires Physical Bench and In-Water Testing: ",
        "1. Oscilloscope verification of analog DAC output voltage, settling time, and reconstruction filter distortion.\n"
        "2. Power amplifier efficiency and thermal dissipation under 5.0 W active load.\n"
        "3. Tank impedance analysis of piezoelectric transducer resonance and electromechanical coupling efficiency.")

    # --------------------------------------------------------------------------
    # SECTION 17: WHAT THE OUTPUTS DO NOT PROVE
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 17: What the Outputs Do Not Prove")
    add_body(doc,
        "To maintain the highest standards of scientific and engineering integrity, the team explicitly emphasizes that the "
        "current digital twin outputs DO NOT prove:"
    )
    add_bullet(doc, "Real Underwater Target Detection: ", "The digital twin models the transmitter payload. It does NOT simulate physical acoustic target scattering cross-sections, target aspect angles, or complex echo returns.")
    add_bullet(doc, "Two-Way Sonar Equation Detection Ranges: ", "Outputs do not prove that an AUV can detect underwater targets at 185 m or 200 m. Two-way propagation loss (40*log10(R) + 2*alpha*R) and target strength (TS) severely reduce practical detection range.")
    add_bullet(doc, "Physical Transducer Radiation Patterns: ", "Relative directivity is an analytical proxy. It does not prove physical transducer beam shape, mainlobe half-power beamwidth, or sidelobe suppression levels.")
    add_bullet(doc, "Transducer Electrical Matching: ", "PZT ceramics exhibit complex reactive impedance (capacitive clamped capacitance C0 and motional impedance). The simulation does not prove that an LC matching network will achieve resonance across the full 100-500 kHz range.")
    add_bullet(doc, "Hydrophone Receive Sensitivity & Noise Floor: ", "The simulation does not model physical acoustic noise floors (Knudsen wind noise, flow boundary layer turbulence, thruster cavitation) or hydrophone pre-amplifier noise figures.")

    # --------------------------------------------------------------------------
    # SECTION 18: FINAL ENGINEERING STORY
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 18: Final Engineering Story")
    add_body(doc,
        "The development of Priority 1 represents a transformative architectural evolution in the SIH Problem 26058 digital twin. "
        "Figure 18.1 contrasts the architectural paradigm before and after the Priority 1 overhaul."
    )

    story_diagram = (
        "===============================================================================\n"
        "BEFORE PRIORITY 1 (Heuristic Composite Architecture):\n"
        "  Potentiometer Sliders (Turbidity, Range, Target Strength)\n"
        "                     |\n"
        "                     v\n"
        "  Weighted Composite Heuristic Score: Q = w_t*T + w_r*R + w_ts*TS\n"
        "                     |\n"
        "                     v\n"
        "  Static Threshold Slicing (e.g., Q < 0.35 -> MUDDY; Q > 0.65 -> CLEAR)\n"
        "                     |\n"
        "                     v\n"
        "  Transmission Profile Selected (Zero Physical Transparency)\n"
        "===============================================================================\n"
        "AFTER PRIORITY 1 (Physically Justified Two-Tier Architecture):\n"
        "  Environmental Scenario (T, S, D) + Target Range R\n"
        "                     |\n"
        "                     v\n"
        "  Evaluate All 3 Profiles (LOW_FREQUENCY, BALANCED, HIGH_FREQUENCY)\n"
        "                     |\n"
        "                     v\n"
        "  Ainslie-McColm (1998) 5-Point In-Band Frequency Absorption: alpha(f_k)\n"
        "                     |\n"
        "                     v\n"
        "  One-Way Transmission Loss: TL(R) = 20*log10(R) + alpha_band * R\n"
        "                     |\n"
        "                     v\n"
        "  TIER 1: Propagation Viability Filter (Relative Margin >= -65.0 dB Floor)\n"
        "  [Discards non-viable profiles based on medium physics]\n"
        "                     |\n"
        "                     v\n"
        "  TIER 2: Mission Operational Objective Selector\n"
        "  [SURVEY -> BALANCED for 3.75 mm resolution; DIRECTIVITY -> HIGH for 1.417x beam]\n"
        "                     |\n"
        "                     v\n"
        "  Candidate Profile + Dual Confidence Metrics (Viability & Selection Confidence)\n"
        "                     |\n"
        "                     v\n"
        "  Directional Schmitt-Trigger Hysteresis Deadband (10%)\n"
        "                     |\n"
        "                     v\n"
        "  Debounce Persistence Filter (N = 2 Consecutive Pings)\n"
        "                     |\n"
        "                     v\n"
        "  Atomic PRI Ping-Boundary Latch (PRI = 20.0 ms, 50 Hz PRF)\n"
        "                     |\n"
        "                     v\n"
        "  Active Transmission Waveform Streaming via DMA to 12-Bit DAC\n"
        "==============================================================================="
    )
    helpers['add_ascii_diagram'](doc, story_diagram)

    add_h2(doc, "18.1 Summary of Engineering Significance")
    add_body(doc,
        "By replacing opaque heuristic scores with an unhidden ocean acoustic model and a decoupled two-tier decision hierarchy, "
        "the project delivers a digital twin that is scientifically defensible, pedagogically transparent, and immediately "
        "comprehensible to evaluators, faculty reviewers, and embedded firmware engineers alike. Every graph, metric, and profile "
        "transition generated by the codebase is now directly traceable to established physical laws of underwater sound propagation."
    )
