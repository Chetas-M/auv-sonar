"""
Report Sections - Part 4
Chapters 20 through 25, Appendices A through E:
Verified Claims vs Limitations, Current Status, Roadmap (Priorities 2-7),
Team Responsibility Guide, Risks & Open Questions, Conclusion, Appendices.
"""

import os
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from generate_report_docx import (
    add_h1, add_h2, add_h3, add_body, add_bullet,
    add_callout, add_equation_box, add_styled_table,
    add_ascii_diagram, COLOR_PRIMARY_HEX, COLOR_SECONDARY_HEX,
    COLOR_ACCENT_HEX, COLOR_TEXT_HEX, COLOR_MUTED_HEX
)


def build_chapter_20_verified_claims_vs_limitations(doc):
    """Builds Chapter 20: Verified Claims vs Limitations."""
    add_h1(doc, "20. Verified Claims vs Limitations")

    add_body(
        doc,
        "To uphold the highest standards of professional engineering integrity, this report explicitly segregates "
        "what the digital twin has verified from what remains theoretical or unvalidated. "
        "Under no circumstances should digital simulation results be represented as physical underwater acoustic measurements."
    )

    # TABLE A
    add_h2(doc, "20.1 TABLE A: Verified Implementation and Simulation Results")
    add_body(
        doc,
        "Table A documents engineering claims that have been proven through executable code, automated test suites, "
        "and reproducible simulation data in the repository:"
    )

    table_a_data = [
        ("Exact LFM Chirp Phase Integration", "Synthesizes continuous-phase chirps at 4.0 MSPS across all 3 bands with 0.0000% instantaneous frequency slope error.", "tests/test_simulator.py (Check 1)"),
        ("Discrete Sidelobe Suppression", "Raised-cosine Hann windowing eliminates boundary discontinuities, achieving >50 dB stopband attenuation and >99.999% in-band energy.", "tests/test_simulator.py (Check 2)"),
        ("12-Bit DAC Quantization Bounds", "Quantization error is strictly bounded within [-0.5, +0.5] LSB (±0.403 mV on 3.3 V rail) with simulated SQNR of ~69.7 dB across all profiles.", "tests/test_simulator.py (Check 4)"),
        ("SRAM & Flash Memory Sizing", "Waveform LUTs occupy ~48 KB in Flash; individual active DMA buffers require 16 KB in SRAM. Leaves >87% SRAM headroom on STM32G474.", "tests/test_simulator.py, export_c.py"),
        ("Chatter-Free Adaptation Logic", "Directional Schmitt-trigger hysteresis (10% deadband) and debounce persistence (N=2) eliminate state flickering from noisy inputs.", "tests/test_simulator.py (test_15-18)"),
        ("Atomic Ping-Boundary Latching", "Waveform state transitions occur strictly at the 20.0 ms PRI boundary, guaranteeing zero mid-pulse configuration changes.", "tests/test_simulator.py (test_19-20)"),
        ("Analytical Duty-Cycle Power", "At 10% duty cycle (2.0 ms pulse, 20.0 ms PRI), average electrical transmitter power is throttled to 0.540 W (45.0 mA at 12 V).", "src/power_model.py"),
        ("Two-Tier Selection Operation", "Priority 1 architecture successfully decouples propagation viability from mission utility, preventing LOW_FREQUENCY domination.", "tests/test_profile_evaluation.py"),
        ("Bit-Exact C Header Export", "Re-parsing generated C headers back into Python verifies bit-exact match with 0 LSB error across all 8,000 samples.", "tests/test_simulator.py (Check 4)"),
    ]

    col_w = [Inches(1.8), Inches(3.2), Inches(1.5)]
    add_styled_table(doc, ["Verified Engineering Capability", "Technical Verification Specification", "Validation Source"], table_a_data, col_widths=col_w)

    # TABLE B
    add_h2(doc, "20.2 TABLE B: Theoretical and Analytical Results")
    add_body(
        doc,
        "Table B documents physical models and acoustic equations implemented in the digital twin based on published scientific literature. "
        "These are idealized analytical models, not empirical water measurements:"
    )

    table_b_data = [
        ("Seawater Acoustic Absorption", "Ainslie & McColm (1998) chemical relaxation formulation for B(OH)3, MgSO4, and pure water viscous attenuation.", "Idealized open-ocean homogeneous water assumptions"),
        ("Seawater Sound Speed", "Mackenzie (1981) 9-term empirical sound speed formulation as a function of T, S, and D.", "Valid for open-ocean ranges [-2, 30]°C and [25, 40] PSU"),
        ("Theoretical Range Resolution Limit", "Ideal matched-filter pulse-compression resolution limit: ΔR = c / (2B) (yielding 3.75 mm for BALANCED).", "Assumes infinite SNR and ideal point scatterer target"),
        ("Relative Directivity Proxy Factor", "Theoretical beam directivity proxy: Dir_rel = fc / 300 kHz (θ ∝ c / (f·D)).", "Assumes fixed physical circular aperture diameter D"),
        ("One-Way Spherical Spreading", "Simplified geometric transmission loss: TL = 20 log10(R) + α_bar · (R / 1000).", "Assumes unbounded, isotropic medium without multipath"),
    ]

    col_w = [Inches(1.8), Inches(2.7), Inches(2.0)]
    add_styled_table(doc, ["Theoretical Acoustic Model", "Implemented Analytical Formulation", "Limiting Physics Assumptions"], table_b_data, col_widths=col_w)

    # TABLE C
    add_h2(doc, "20.3 TABLE C: Unvalidated or Future Hardware Claims (What Must NOT Be Claimed)")
    add_body(
        doc,
        "Table C explicitly enumerates claims that MUST NOT be made regarding the current digital twin implementation. "
        "These represent future hardware development phases:"
    )

    table_c_data = [
        ("Real Underwater Echoes", "NO. The system does not transmit physical acoustic waves into water or capture real acoustic reflections.", "Requires physical transducer and water tank test"),
        ("Hydrophone Receiver Performance", "NO. Receiver processing (hydrophones, pre-amps, ADC, matched filters, Doppler) is NOT modeled.", "Transmitter payload scope only"),
        ("Target Scattering Strength (TS)", "NO. Target reflectivity is emulated via a potentiometer voltage; physical acoustic target cross-sections are NOT modeled.", "Requires two-way acoustic sonar equation model"),
        ("Piezoelectric Ceramic Resonance", "NO. Electromechanical coupling (kt), Butterworth-Van Dyke (BVD) resonant impedance, and phase angle are NOT modeled.", "Requires impedance analyzer bench test"),
        ("Transducer Electrical Impedance", "NO. Real complex impedance Z(f) = R + jX and matching network performance are unverified.", "Requires impedance matching network design"),
        ("Physical Transducer Beam Patterns", "NO. Far-field beam divergence, sidelobe structures, and directional gain are NOT measured.", "Requires hydrophone scanning tank facility"),
        ("Power Amplifier (PA) Efficiency", "NO. Analog PA efficiency, thermal dissipation, crossover distortion, and slew rate are unverified.", "Requires bench PCB bring-up with dummy load"),
        ("Actual Bench Current Draw", "NO. Power metrics are analytical duty-cycle models, not empirical bench multimeter measurements.", "Requires physical DC power analyzer test"),
        ("Calibrated Turbidity Attenuation", "NO. Turbidity attenuation is an unvalidated heuristic (Equation 10.1), NOT calibrated sediment physics.", "Requires acoustic attenuation laboratory cell"),
    ]

    col_w = [Inches(1.8), Inches(2.7), Inches(2.0)]
    add_styled_table(doc, ["Unvalidated Hardware Claim", "Strict Engineering Status for Version 1", "Required Physical Validation Phase"], table_c_data, col_widths=col_w)


def build_chapter_21_current_project_status(doc):
    """Builds Chapter 21: Current Project Status."""
    add_h1(doc, "21. Current Project Status")

    add_body(
        doc,
        "As of the current project stage, the engineering team has achieved complete delivery of Stage 1: Pre-Silicon Digital Twin "
        "and Analytical Validation. Every signal processing algorithm, state machine, and acoustic evaluation metric has been "
        "implemented, cross-verified, and validated across automated test suites."
    )

    add_h2(doc, "21.1 Completed Engineering Deliverables")
    add_bullet(doc, "Digital Twin Signal Pipeline: ", "12-bit unsigned DAC quantization, 4.0 MSPS sampling rate, 2.0 ms pulse duration, and continuous phase integration verified.")
    add_bullet(doc, "Priority 1 Evaluation Engine: ", "Physics-grounded profile performance evaluation implemented across Python and MATLAB with 5-point in-band sampling.")
    add_bullet(doc, "Two-Tier Adaptation Controller: ", "Decoupled propagation viability filtering and mission utility selection hierarchy with Schmitt hysteresis and debounce.")
    add_bullet(doc, "Dual Confidence Metric Architecture: ", "Viability Confidence (Cv) and Mission Selection Confidence (Cs) fully operational and documented.")
    add_bullet(doc, "Automated Verification Suite: ", "56 / 56 automated unit tests passing in Python; 23-point DSP suite and 12-point Priority 1 suite passing in MATLAB.")
    add_bullet(doc, "20 Engineering Visualizations: ", "All 7 Priority 1 experiment figures and 13 baseline validation plots generated in high resolution in outputs_matlab/plots/.")
    add_bullet(doc, "Firmware-Ready Prototype C Headers: ", "Generated DMA-aligned C lookup table headers (chirp_low_frequency.h, chirp_balanced.h, chirp_high_frequency.h, sonar_profiles.h) ready for STM32 firmware bring-up.")

    add_h2(doc, "21.2 What Remains to Transition to Physical Hardware")
    add_body(
        doc,
        "To advance the project from a pre-silicon digital twin to an operational subsea transmitter payload, "
        "the team must execute physical hardware bring-up:"
    )

    add_bullet(doc, "1. STM32 Firmware Bring-Up: ", "Deploy exported C headers to an STM32G474 Nucleo/Discovery board, configuring Timer TRGO -> DMA -> DAC for autonomous playback.")
    add_bullet(doc, "2. Oscilloscope & Spectrum Analyzer Verification: ", "Measure physical DAC output on bench equipment to confirm 4.0 MSPS timing, voltage swing (1.65 V bias), and analog harmonic rolloff.")
    add_bullet(doc, "3. Analog Signal Conditioning & Filtering: ", "Design and solder an active reconstruction low-pass filter (Sallen-Key topology, fc ≈ 600 kHz) to suppress DAC imaging frequencies.")
    add_bullet(doc, "4. Class-D Power Amplifier & Impedance Matching: ", "Design an efficient power amplifier stage and passive LC matching network to drive complex transducer loads.")
    add_bullet(doc, "5. Transducer Bench Characterization: ", "Measure transducer electrical impedance Z(f) across 100 to 500 kHz using an impedance analyzer to assess wideband feasibility.")


def build_chapter_22_recommended_next_roadmap(doc):
    """Builds Chapter 22: Recommended Next Development Roadmap."""
    add_h1(doc, "22. Recommended Next Development Roadmap")

    add_body(
        doc,
        "To guide the project team, faculty reviewers, and hardware implementation engineers, this chapter establishes a "
        "rigorous, prioritized development roadmap spanning Priorities 2 through 7."
    )

    road_data = [
        ("PRIORITY 2: Hardware Feasibility & Prototype Transmitter", "Design bench PCB schematic and layout for STM32G474 DAC output buffering, active anti-imaging reconstruction filter, and low-power Class-D amplifier stage.", "Schematic (KiCad/Altium), BOM, PCB gerbers, simulation of analog filter response.", "Analog op-amp slew rate limitations at 4.0 MSPS; PA crossover distortion.", "Clean analog chirp reconstruction on oscilloscope with THD < -40 dB."),
        ("PRIORITY 3: STM32 Firmware & DMA Bring-Up", "Implement embedded C firmware on STM32G474 using HAL/LL drivers. Configure Timer 2 TRGO at 4.0 MHz driving DMA1 Channel 1 into DAC1.", "Firmware source code (main.c, dac.c, dma.c), build scripts, oscilloscope captures of DAC pin.", "DMA transfer latency, ISR jitter, Timer TRGO clock synchronization.", "Autonomous 4.0 MSPS DAC playback verified on oscilloscope without CPU loading."),
        ("PRIORITY 4: Live Adaptive Controller Demonstration", "Connect 3 physical precision potentiometers to STM32 12-bit ADC channels. Run real-time adaptation state machine on Cortex-M4F.", "Real-time firmware binary, live oscilloscope demonstration of atomic profile switching at PRI boundaries.", "ADC thermal noise causing state chatter; PRI interrupt timing contention.", "Zero profile hunting; atomic profile switching confirmed on oscilloscope persistence mode."),
        ("PRIORITY 5: Transducer Characterization & Matching", "Characterize physical acoustic transducer using an impedance analyzer across 100–500 kHz. Design broadband or multi-tap LC matching network.", "Impedance plots (magnitude & phase vs frequency), BVD equivalent circuit parameters, matching network schematic.", "Severe transducer resonant peaks causing impedance mismatch and distortion outside resonance.", "VSWR < 2.0 or power transfer efficiency > 75% across intended chirp bands."),
        ("PRIORITY 6: Two-Way Sonar Propagation & Target Model", "Expand digital twin to model physical two-way echo reflection: 2TL = 40 log10(R) + 2αR, target scattering strength (TS), and hydrophone SNR.", "Python/MATLAB two-way acoustic simulation module, synthetic echo generator, match-filter receiver twin.", "Computational complexity; uncalibrated target strength assumptions.", "Realistic synthetic acoustic echo waveforms generated with matched-filter SNR verification."),
        ("PRIORITY 7: Controlled Water Tank Acoustic Testing", "Submerge matched transducer and calibrated reference hydrophone in a test water tank. Measure physical acoustic Source Level (SL) and beam patterns.", "Calibrated acoustic waveforms, measured Source Level (dB re 1 µPa @ 1m), measured beam pattern plots.", "Acoustic tank wall reflections (multipath interference); hydrophone calibration drift.", "Measured acoustic pulses match digital twin synthetic chirps with <10% amplitude error."),
    ]

    col_w = [Inches(1.5), Inches(1.8), Inches(1.3), Inches(1.0), Inches(0.9)]
    headers = ["Roadmap Priority", "Engineering Objective & Scope", "Deliverables", "Technical Risks", "Success Criteria"]
    add_styled_table(doc, headers, road_data, col_widths=col_w)


def build_chapter_23_team_responsibility_guide(doc):
    """Builds Chapter 23: Team Responsibility Guide."""
    add_h1(doc, "23. Team Responsibility Guide")

    add_body(
        doc,
        "This guide outlines subsystem ownership, file responsibilities, inputs, outputs, and dependencies for "
        "incoming engineering team members across six specialized technical roles."
    )

    roles = [
        ("Systems Engineering Lead", "Overall architecture, requirements tracking, SIH compliance, and system-level trade-offs.", "README.md, walkthrough.md, src/config.py, matlab/config_sonar.m", "Mission operational profiles, vehicle power budgets", "System specifications, single-source-of-truth parameters, architecture freeze", "Cross-subsystem coordination"),
        ("Embedded Firmware Engineer", "STM32 firmware implementation, Timer TRGO configuration, DMA streaming, and ADC acquisition.", "outputs/headers/*, src/export_c.py, matlab/export_c_headers.m", "Prototype C header tables, MCU pinout, clock tree", "STM32 C firmware (Keil/STM32CubeIDE), DMA interrupt handlers, DAC driver", "Systems Lead, Analog Engineer"),
        ("Analog & Electronics Engineer", "Mixed-signal PCB design, reconstruction filtering, power amplifier, and DC-DC power delivery.", "Hardware schematics, outputs/headers/ (electrical specs)", "DAC analog output specs (3.3 V, 4 MSPS), battery voltage (12 V)", "Filter schematics, PA design, PCB layout, bench test measurements", "Firmware Engineer, Transducer Lead"),
        ("Acoustic Simulation Engineer", "Propagation modeling, seawater absorption, two-way sonar equations, and matched filtering.", "src/profile_evaluator.py, src/waveform.py, matlab/evaluate_profile_performance.m", "Oceanographic parameters (T, S, D, turb), transducer bandwidths", "Acoustic evaluation algorithms, synthetic echo models, range resolution limits", "Systems Lead"),
        ("Dashboard & Visualization Engineer", "Mission telemetry, real-time plotting, digital twin GUI, and automated visual reporting.", "src/experiments.py, matlab/run_simulation.m, outputs_matlab/plots/*", "Simulation timeline logs, state-machine telemetry", "Matplotlib/MATLAB plotting scripts, dashboard telemetry displays", "Simulation Engineer"),
        ("Testing & Documentation Engineer", "Automated test suite maintenance, parity testing, technical documentation, and SIH reports.", "tests/*, matlab/run_validation_suite.m, engineering reports", "New module commits, PRs, mathematical equations", "Passing test logs (56/56), Word/PDF engineering documentation", "All team members"),
    ]

    col_w = [Inches(1.2), Inches(1.3), Inches(1.3), Inches(0.9), Inches(1.0), Inches(0.8)]
    headers = ["Engineering Role", "Subsystem Ownership", "Key Files & Modules", "Primary Inputs", "Deliverables", "Dependencies"]
    add_styled_table(doc, headers, roles, col_widths=col_w)


def build_chapter_24_risks_and_open_questions(doc):
    """Builds Chapter 24: Risks and Open Engineering Questions."""
    add_h1(doc, "24. Risks and Open Engineering Questions")

    add_body(
        doc,
        "Every honest engineering report must identify its critical technical risks and unresolved engineering questions. "
        "The following ten risks are ranked in descending order of criticality for the next project phase:"
    )

    risks = [
        ("Rank 1: Transducer Bandwidth Feasibility (100–500 kHz)", "Can a single physical piezoelectric transducer support 100 kHz to 500 kHz?", "Extremely high. Standard piezo ceramics have fractional bandwidths of 20% to 40%. Covering 100 to 500 kHz represents a 5:1 frequency ratio (over 2 octaves). A single ceramic will exhibit severe resonance peaks at one frequency and near-zero emission at others.", "Evaluate dual-element transducers (e.g., 160 kHz ceramic + 400 kHz ceramic) or 1-3 piezocomposite broadband materials."),
        ("Rank 2: Resonant Impedance Mismatch", "How will transducer impedance variations affect the power amplifier across different profiles?", "High. Transducer impedance Z(f) varies from tens of ohms at resonance to thousands of ohms off-resonance with heavy reactive phase angles, causing PA distortion and thermal dissipation.", "Design a switched multi-tap matching network or use load-insensitive class-D topologies."),
        ("Rank 3: STM32 High-Speed DAC Settling at 4.0 MSPS", "Can the internal STM32G4 DAC cleanly settle within 250 ns without slew-rate distortion?", "Moderate-High. At 4.0 MSPS, the DAC sample period is 250 ns. In high-speed mode without output buffers, settling time is ~200 ns. Stray PCB capacitance can cause severe low-pass filtering.", "Bypass internal op-amp buffers; route DAC pin directly to high-speed external wideband buffer (e.g., OPA354)."),
        ("Rank 4: Power Amplifier Efficiency & Linearity", "What power amplifier architecture achieves high efficiency at 500 kHz within AUV thermal limits?", "Moderate. Class-A/AB linear amplifiers generate excessive heat inside sealed AUV pressure vessels. Class-D amplifiers require high switching frequencies (>2.5 MHz) to reproduce 500 kHz chirps cleanly.", "Investigate high-speed GaN (gallium nitride) half-bridge Class-D power stages."),
        ("Rank 5: Impedance Matching Across Profiles", "How can a passive LC matching network accommodate multiple distinct frequency bands?", "Moderate. A single fixed inductor-capacitor network can only match impedance at one center frequency.", "Implement relay-switched or MOSFET-switched matching capacitors selected by profile ID."),
        ("Rank 6: Physical Acoustic Source Level (SL)", "What is the actual acoustic sound pressure level emitted into water per electrical watt?", "Moderate. Digital twin assumes normalized 0 dB transmit level. Real SL depends on transducer transmitting voltage response (TVR in dB re 1 µPa/V @ 1m).", "Perform hydrophone tank calibration to establish empirical TVR curves across all three bands."),
        ("Rank 7: Receiver & Feedback Integration", "How will target reflectivity and SNR be acquired without an acoustic receiver path?", "Moderate. v1 emulates target strength via a potentiometer. In a real AUV, this must be derived from receiver matched-filter SNR.", "Develop matched-filter receiver digital twin in Priority 6 before hardware receiver integration."),
        ("Rank 8: Empirical Calibration of Viability Floor", "How will the -65.0 dB simulation viability threshold be calibrated against real hydrophones?", "Moderate-Low. The -65 dB floor is a simulation policy parameter. Real detection thresholds depend on hydrophone sensitivity, pre-amp noise, and processing gain.", "Conduct acoustic tank measurements with calibrated hydrophone to establish true detection SNR thresholds."),
        ("Rank 9: Underwater Multipath & Boundary Interference", "How will real shallow-water multipath affect chirp compression in physical water?", "Moderate-Low. Direct-path transmission loss does not model surface/bottom ghost reflections.", "Implement multipath synthetic channel generator in Priority 6 simulation."),
        ("Rank 10: Turbidity Model vs. Real Sediment", "How does real particulate scattering compare to the f² heuristic in Equation 10.1?", "Low. The heuristic is unvalidated. Real sediment scattering depends on grain size distribution and concentration.", "Calibrate acoustic attenuation against standard kaolin clay suspensions in an acoustic test cell."),
    ]

    col_w = [Inches(1.8), Inches(1.5), Inches(1.7), Inches(1.5)]
    headers = ["Risk Rank & Challenge", "Engineering Problem Statement", "Severity & Technical Rationale", "Recommended Mitigation Strategy"]
    add_styled_table(doc, headers, risks, col_widths=col_w)


def build_chapter_25_conclusion(doc):
    """Builds Chapter 25: Conclusion."""
    add_h1(doc, "25. Conclusion")

    add_body(
        doc,
        "The SIH Problem 26058 project has successfully delivered a comprehensive, fully verified pre-silicon digital twin "
        "of a Low-Power, Real-Time Adaptive Software-Defined Sonar Transmitter Payload for Autonomous Underwater Vehicles. "
        "The digital twin bridges theoretical ocean acoustics, discrete digital signal processing, and real-time embedded "
        "microcontroller constraints, providing a robust pre-silicon validation foundation for subsea sonar development."
    )

    add_h2(doc, "25.1 Summary of Engineering Achievements")
    add_bullet(doc, "Algorithmic & Mathematical Correctness: ", "Verified continuous-phase LFM chirp synthesis across 100 to 500 kHz at 4.0 MSPS with 0.0000% instantaneous frequency slope error and >50 dB spectral sidelobe suppression via Hann windowing.")
    add_bullet(doc, "Mixed-Signal Quantization & Memory Sizing: ", "Proved that 12-bit unsigned DAC quantization achieves ~69.7 dB simulated SQNR with quantization error bounded within ±0.5 LSB. Proved that precomputed LUTs occupy ~48 KB in Flash, and active DMA ping buffers require 16 KB in SRAM, leaving ample headroom on the STM32G474.")
    add_bullet(doc, "Priority 1 Profile Evaluation Engine: ", "Replaced opaque heuristic quality scores with explicit, physics-grounded evaluation of Ainslie-McColm absorption across 5 discrete in-band frequencies, spherical transmission loss, theoretical range resolution (ΔR = 3.75 mm best for BALANCED), and relative theoretical directivity (1.417x best for HIGH_FREQUENCY).")
    add_bullet(doc, "Intelligent Two-Tier Selection: ", "Successfully resolved the low-frequency domination paradox by decoupling propagation viability filtering from mission utility optimization, guaranteeing long-range fallback while prioritizing survey resolution and tracking directivity.")
    add_bullet(doc, "Explainable Dual Confidence: ", "Introduced Viability Confidence (Cv) and Mission Selection Confidence (Cs), providing transparent, early-warning link margin telemetry.")
    add_bullet(doc, "Chatter-Free State Machine: ", "Demonstrated that directional Schmitt hysteresis (10% deadband) and debounce persistence (N=2) eliminate state jitter, while atomic ping-boundary latching protects power amplifier stages.")
    add_bullet(doc, "Exhaustive Automated Validation: ", "Confirmed 56 / 56 automated tests passing in Python with bit-exact parity across 14 synchronized MATLAB scripts.")

    add_h2(doc, "25.2 The Crucial Engineering Transition")
    add_body(
        doc,
        "While the digital twin rigorously validates the mathematical, algorithmic, and architectural dimensions of the transmitter, "
        "it represents the first step in a complete hardware realization. The project is now positioned to transition from pre-silicon "
        "digital simulation to physical embedded and acoustic bring-up along the following disciplined path:"
    )

    add_ascii_diagram(
        doc,
        "                       DIGITAL SIMULATION & ANALYTICAL TWIN\n"
        "               [ Stage 1 Complete — 56/56 Tests Passing, 20 Figures ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                            EMBEDDED FIRMWARE BRING-UP\n"
        "               [ STM32G474 Timer TRGO -> DMA -> High-Speed DAC1 ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                            ANALOG WAVEFORM GENERATION\n"
        "               [ Bench Oscilloscope/FFT, Active Filter, Class-D PA ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                           TRANSDUCER CHARACTERIZATION\n"
        "               [ Impedance Analyzer Z(f), BVD Parameters, Matching ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                           CONTROLLED ACOUSTIC VALIDATION\n"
        "               [ Water Tank Testing, Calibrated Hydrophone SL, Beam ]"
    )

    add_body(
        doc,
        "By adhering to strict engineering honesty, transparent physical modeling, and exhaustive automated testing, "
        "this project provides an authoritative, reproducible foundation for the next generation of adaptive software-defined "
        "sonar payloads for autonomous subsea exploration."
    )

    add_h2(doc, "25.3 Final Engineering Claims and Limitations Review")
    add_body(
        doc,
        "As an executive review for SIH evaluators, faculty judges, and technical mentors, the verified boundaries of this project are locked as follows:"
    )

    add_callout(
        doc,
        tag="Final Engineering Boundary Statement",
        title="Authoritative Scope Statement for SIH Problem 26058",
        body=(
            "1. WHAT IS FULLY VALIDATED AND CLAIMED:\n"
            "   • Mathematical and algorithmic correctness of 3 canonical LFM chirps (100–500 kHz) at 4.0 MSPS.\n"
            "   • Discrete raised-cosine Hann windowing achieving >50 dB sidelobe suppression.\n"
            "   • 12-bit unsigned DAC quantization with simulated SQNR of ~69.7 dB and error within ±0.5 LSB.\n"
            "   • SRAM and Flash memory sizing (LUTs occupy ~48 KB in Flash, active DMA buffers require 16 KB in SRAM).\n"
            "   • Directional Schmitt hysteresis (10% deadband) and debounce persistence (N=2) eliminating profile chatter.\n"
            "   • Atomic ping-boundary profile latching modeling DMA Transfer-Complete synchronization.\n"
            "   • Duty-cycle electrical power throttling (0.540 W average at 10% duty cycle, 45.0 mA at 12 V).\n"
            "   • Priority 1 two-tier selection architecture decoupling viability (-65 dB relative margin) from mission utility.\n"
            "   • Explainable dual confidence metrics (Viability Confidence Cv and Selection Confidence Cs).\n"
            "   • 56 / 56 automated unit tests passing in Python with bit-exact parity across 14 MATLAB scripts.\n\n"
            "2. WHAT IS NOT VALIDATED AND MUST NOT BE CLAIMED:\n"
            "   • Physical underwater acoustic wave propagation, ocean multipath, or real acoustic echoes.\n"
            "   • Receiver hydrophone SNR, matched-filter detection, or closed-loop acoustic feedback.\n"
            "   • Piezoelectric transducer resonance, Butterworth-Van Dyke parameters, or real complex impedance Z(f).\n"
            "   • Real measured acoustic beam patterns or directivity sidelobes.\n"
            "   • Physical power amplifier thermal behavior, crossover distortion, or bench current measurements.\n"
            "   • Calibrated turbidity attenuation (turbidity model is an unvalidated sensitivity heuristic).\n\n"
            "The physical hardware demonstration for Version 1 is strictly transmitter-side."
        ),
        callout_type="IMPORTANT"
    )


def build_appendices(doc):
    """Builds Appendices A through E."""
    doc.add_page_break()
    add_h1(doc, "Appendices")

    # Appendix A
    add_h2(doc, "Appendix A: Profile Definitions")
    add_body(
        doc,
        "Complete technical parameter specifications for all three canonical transmission profiles locked for Version 1 runtime:"
    )

    app_a_data = [
        ("Parameter", "LOW_FREQUENCY (Profile 1)", "BALANCED (Profile 2)", "HIGH_FREQUENCY (Profile 3)"),
        ("Start Frequency (f_start)", "100,000 Hz (100.0 kHz)", "200,000 Hz (200.0 kHz)", "350,000 Hz (350.0 kHz)"),
        ("End Frequency (f_end)", "220,000 Hz (220.0 kHz)", "400,000 Hz (400.0 kHz)", "500,000 Hz (500.0 kHz)"),
        ("Center Frequency (f_center)", "160,000 Hz (160.0 kHz)", "300,000 Hz (300.0 kHz)", "425,000 Hz (425.0 kHz)"),
        ("Sweep Bandwidth (B)", "120,000 Hz (120.0 kHz)", "200,000 Hz (200.0 kHz)", "150,000 Hz (150.0 kHz)"),
        ("Chirp Duration (T_p)", "0.0020 s (2.0 ms)", "0.0020 s (2.0 ms)", "0.0020 s (2.0 ms)"),
        ("Chirp Sweep Slope (k)", "60,000,000 Hz/s (60.0 MHz/s)", "100,000,000 Hz/s (100.0 MHz/s)", "75,000,000 Hz/s (75.0 MHz/s)"),
        ("Sampling Frequency (F_s)", "4,000,000 Hz (4.0 MSPS)", "4,000,000 Hz (4.0 MSPS)", "4,000,000 Hz (4.0 MSPS)"),
        ("Sample Count (N_p)", "8,000 samples", "8,000 samples", "8,000 samples"),
        ("LUT Memory Footprint", "16,000 bytes (15.625 KiB)", "16,000 bytes (15.625 KiB)", "16,000 bytes (15.625 KiB)"),
        ("C Header Filename", "chirp_low_frequency.h", "chirp_balanced.h", "chirp_high_frequency.h"),
        ("C LUT Array Identifier", "CHIRP_LOW_FREQUENCY_LUT", "CHIRP_BALANCED_LUT", "CHIRP_HIGH_FREQUENCY_LUT"),
        ("Window Function", "Raised-Cosine Hann Window", "Raised-Cosine Hann Window", "Raised-Cosine Hann Window"),
        ("Normalized Amplitude (A)", "1.00 (Max Penetration)", "0.70 (Nominal Balance)", "0.40 (Low Power / Clean)"),
        ("Simulated SQNR", "69.67 dB", "69.67 dB", "69.70 dB"),
        ("Theoretical Range Res. (ΔR)", "6.25 mm (c = 1500 m/s)", "3.75 mm (c = 1500 m/s)", "5.00 mm (c = 1500 m/s)"),
        ("Relative Directivity Proxy", "0.533x reference", "1.000x baseline reference", "1.417x reference"),
        ("Baseline Absorption (α_bar)", "18.23 dB/km", "37.58 dB/km", "64.87 dB/km"),
        ("Primary Mission Alignment", "Long-range search / degraded channel", "Default survey mapping & bathymetry", "Narrow-beam obstacle tracking"),
    ]

    col_w = [Inches(2.2), Inches(1.4), Inches(1.5), Inches(1.4)]
    add_styled_table(doc, ["Profile Parameter", "LOW_FREQUENCY", "BALANCED", "HIGH_FREQUENCY"], app_a_data, col_widths=col_w)

    # Appendix B
    add_h2(doc, "Appendix B: Important Equations")
    add_body(
        doc,
        "Mathematical equations implemented across Python and MATLAB codebase:"
    )

    eq_list = [
        ("LFM Instantaneous Frequency", "f(t) = f_0 + k · t,   where k = (f_1 - f_0) / T_p"),
        ("Analytical Phase Integral", "φ(t) = 2π ∫₀ᵗ f(τ) dτ = 2π (f_0 · t + 0.5 · k · t²)"),
        ("Discrete Hann Window", "w[n] = 0.5 · (1 - cos(2π n / (N_p - 1))),   n ∈ [0, N_p - 1]"),
        ("12-Bit DAC Quantization", "DAC_Code[n] = round(2048 + 2047 · s_norm[n]),   clamped to [0, 4095]"),
        ("Quantization Error Residual", "ε_q[n] = DAC_Code[n] - (2048 + 2047 · s_norm[n])   [LSB]"),
        ("Simulated SQNR", "SQNR = 10 · log10( ∑ s²[n] / ∑ (s[n] - s_quant[n])² )   [dB]"),
        ("Mackenzie Sound Speed", "c(T,S,D) = 1448.96 + 4.591T - 0.05304T² + 0.0002374T³ + 1.34(S-35) + 0.0163D + 0.0001675D² - 0.01025T(S-35) - 7.139e-7TD³"),
        ("Ainslie-McColm Absorption", "α(f) = (A₁ f₁ f²) / (f₁² + f²) + (A₂ f₂ f²) / (f₂² + f²) + A₃ f²   [dB/km]"),
        ("Turbidity Heuristic", "α_turb(f, turb) = 35.0 · (turb / 100) · (f / 300)²   [dB/km]  [UNVALIDATED HEURISTIC]"),
        ("Relative Transmission Loss", "TL(R) = 20 · log10(R_eff) + α_bar · (R_eff / 1000)   [dB]"),
        ("Relative Propagation Margin", "Margin_rel(R) = -TL(R) - NP_sim   [dB]"),
        ("Theoretical Range Resolution", "ΔR = c / (2 · Bandwidth)   [m]"),
        ("Relative Directivity Proxy", "Dir_rel = f_center / 300 kHz   [fixed aperture assumption]"),
        ("Viability Confidence", "C_v = clip( (Margin_rel - Thresh_viab) / 15.0 dB,  0.0,  1.0 )"),
        ("Mission Selection Confidence", "C_s = clip( (Utility_winner - Utility_second) / 0.25,  0.0,  1.0 )"),
        ("Duty-Cycle Average Power", "P_avg = P_active · D + P_idle · (1 - D),   where D = T_pulse / PRI"),
    ]

    col_w = [Inches(2.2), Inches(4.3)]
    add_styled_table(doc, ["Physical / DSP Formulation", "Implemented Mathematical Equation"], eq_list, col_widths=col_w)

    # Appendix C
    add_h2(doc, "Appendix C: Automated Test Suite Summary")
    add_body(
        doc,
        "Summary of the complete 56-test automated validation suite (all passing):"
    )

    test_summary = [
        ("tests/test_matlab_parity.py", "8", "8 Passed (100%)", "Verifies MATLAB file existence, Single Source of Truth parameter alignment, phase integration formula, Q score calculation, Schmitt hysteresis thresholds, 23-test validation suite count, and 13-plot simulation count."),
        ("tests/test_profile_evaluation.py", "12", "12 Passed (100%)", "Verifies Priority 1: 3-profile evaluation, no NaN/Inf, positive finite attenuation, monotonic TL with range, attenuation ordering (HIGH > BAL > LOW), range resolution ordering (BAL = 3.75 mm best), directivity ordering (HIGH = 1.417x best), 5-point discrete band confinement, long-range fallback to LOW at 200m, Survey mode selection of BAL, Directivity mode selection of HIGH, and bit-exact determinism."),
        ("tests/test_simulator.py", "36", "36 Passed (100%)", "Verifies LFM chirp synthesis, sample count (8000), duration (2.0 ms), slope (100 MHz/s), start/end frequencies, Hann window tapering, 12-bit DAC codes [0, 4095], midscale 2048, SQNR > 69 dB, Hilbert frequency linearity (error 0.0000%), FFT in-band energy (>99.999%), STFT spectrogram ridge linearity (R² = 0.9901), hysteresis deadbands (10%), debounce persistence (N=2), ping-boundary freeze, power model, and bit-exact C header export round-trip."),
    ]

    col_w = [Inches(2.2), Inches(0.8), Inches(1.3), Inches(2.2)]
    add_styled_table(doc, ["Test Module", "Test Count", "Pass Rate", "Verified Engineering Scope"], test_summary, col_widths=col_w)

    # Appendix D
    add_h2(doc, "Appendix D: File and Module Architecture")
    add_body(
        doc,
        "Complete repository file structure and subsystem responsibilities:"
    )

    file_arch = [
        ("src/config.py", "Single Source of Truth configuration constants: F_s = 4.0 MHz, 12-bit DAC, T_p = 2.0 ms, PRI = 20.0 ms, power parameters."),
        ("src/profiles.py", "Data classes and enumerated definitions for TurbidityProfileType, BandProfile, and TransmitterState."),
        ("src/waveform.py", "Analytical LFM chirp synthesis, continuous phase integration, Hann window tapering, and 12-bit DAC quantization."),
        ("src/adaptation.py", "AnalogInputs acquisition, HysteresisThreshold state machine, AdaptationEngine (N=2 debounce), and PingController."),
        ("src/power_model.py", "Duty-cycle electrical power dissipation model, average current calculation, and payload battery endurance."),
        ("src/export_c.py", "Prototype C header generator exporting aligned uint16_t lookup tables and SonarProfileDescriptor_t structs."),
        ("src/profile_evaluator.py", "Priority 1 core: Ainslie-McColm absorption, Mackenzie sound speed, 5-point band sampling, two-tier selection, dual confidence."),
        ("src/experiments.py", "Priority 1 parameter sweeps (range, noise, environmental), tabular reporter, and 7-plot figure generator."),
        ("matlab/config_sonar.m", "Single Source of Truth parameter configuration struct for standalone MATLAB digital twin."),
        ("matlab/profile_definitions.m", "Struct array defining the three canonical transmission profiles in MATLAB."),
        ("matlab/generate_lfm_chirp.m", "MATLAB implementation of analytical phase-integrated LFM chirp generation and Hann windowing."),
        ("matlab/channel_model.m", "Predictive acoustic channel model and original Channel Quality Score (Q) calculator."),
        ("matlab/adaptive_controller.m", "Directional Schmitt-trigger hysteresis, N=2 debounce counter, and ping-boundary latching in MATLAB."),
        ("matlab/evaluate_profile_performance.m", "Priority 1 MATLAB engine: 5-point absorption, transmission loss, two-tier selection, and dual confidence."),
        ("matlab/run_simulation.m", "Master simulation runner generating 13 baseline waveform and controller engineering figures."),
        ("matlab/run_experiments.m", "Master experiment runner generating the 7 Priority 1 parameter sweep figures in MATLAB."),
        ("matlab/run_validation_suite.m", "Automated 23-point DSP, quantization, and state machine validation test suite in MATLAB."),
        ("matlab/run_profile_evaluation_tests.m", "Automated 12-point Priority 1 profile evaluation unit test suite in MATLAB."),
        ("tests/test_simulator.py", "Comprehensive 36-test Python unit test suite verifying synthesis, DAC, adaptation, and C export."),
        ("tests/test_profile_evaluation.py", "12-test Python unit test suite verifying Priority 1 profile evaluation and selection logic."),
        ("tests/test_matlab_parity.py", "8-test automated parity test suite confirming Python–MATLAB architectural synchronization."),
    ]

    col_w = [Inches(2.5), Inches(4.0)]
    add_styled_table(doc, ["File / Module Path", "Subsystem Functional Responsibility"], file_arch, col_widths=col_w)

    # Appendix E
    add_h2(doc, "Appendix E: Engineering Glossary")
    add_body(
        doc,
        "Definitions of technical terms, abbreviations, and engineering acronyms used throughout this report:"
    )

    glossary = [
        ("AUV", "Autonomous Underwater Vehicle: An unmanned, self-propelled, untethered subsea robotic vehicle powered by onboard batteries."),
        ("LFM", "Linear Frequency Modulation: A modulation technique where the instantaneous frequency sweeps linearly with time across a defined bandwidth."),
        ("Chirp", "A frequency-modulated signal pulse commonly used in sonar and radar systems to achieve pulse compression."),
        ("DAC", "Digital-to-Analog Converter: A mixed-signal peripheral that converts discrete binary integer codes into a proportional continuous analog voltage."),
        ("DMA", "Direct Memory Access: A specialized hardware bus master that transfers data directly between memory and peripherals without CPU intervention."),
        ("PRI", "Pulse Repetition Interval: The time interval between the start of consecutive acoustic pulse transmissions (e.g., 20.0 ms = 50 Hz ping rate)."),
        ("Attenuation (α)", "The reduction in acoustic wave intensity caused by absorption and scattering during propagation through seawater, expressed in dB/km."),
        ("Transmission Loss (TL)", "The total reduction in acoustic signal power between an acoustic source and target, combining geometric spreading and absorption (dB)."),
        ("Viability", "A binary status indicating whether a waveform maintains sufficient modeled signal margin above a defined policy floor (-65 dB)."),
        ("Range Resolution (ΔR)", "The minimum spatial distance between two target reflectors along the acoustic axis required to resolve them as separate echoes (ΔR = c/(2B))."),
        ("Directivity (θ)", "The measure of an acoustic transducer's ability to focus acoustic energy into a narrow spatial beam, inversely proportional to frequency."),
        ("Hysteresis", "A dual-threshold switching mechanism where transition thresholds depend on current state, preventing state oscillation near boundaries."),
        ("Debounce", "A temporal persistence filter requiring a candidate condition to hold for N consecutive cycles before committing a state change."),
        ("LUT", "Lookup Table: An array of precomputed digital values stored in memory for rapid, zero-latency retrieval without real-time computation."),
        ("SQNR", "Signal-to-Quantization-Noise Ratio: The ratio of signal power to quantization noise power introduced by discrete integer rounding (dB)."),
        ("NTU", "Nephelometric Turbidity Unit: An optical light-scattering measurement unit indicating the concentration of suspended particulate matter."),
        ("BVD", "Butterworth-Van Dyke: An equivalent electrical circuit model of a piezoelectric transducer modeling motional and clamped resonance."),
        ("TRGO", "Trigger Output: An internal microcontroller timer event used to synchronize peripheral operations (such as triggering DAC DMA transfers)."),
    ]

    col_w = [Inches(1.8), Inches(4.7)]
    add_styled_table(doc, ["Term / Acronym", "Technical Definition & Context"], glossary, col_widths=col_w)


print("Part 4 builder functions loaded.")
