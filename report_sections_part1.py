"""
Report Sections - Part 1
Chapters: Cover Page, TOC, Chapters 1 through 7
"""

import os
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from generate_report_docx import (
    add_h1, add_h2, add_h3, add_body, add_bullet,
    add_callout, add_equation_box, add_styled_table,
    add_ascii_diagram, COLOR_PRIMARY_HEX, COLOR_SECONDARY_HEX,
    COLOR_ACCENT_HEX, COLOR_TEXT_HEX, COLOR_MUTED_HEX,
    set_cell_background, set_cell_margins, set_table_borders
)
from src.canonical_data import get_canonical_results


def build_cover_page(doc):
    """Builds a formal engineering report cover page."""
    # Add spacing
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(36)

    # Top Category / Problem Identifier
    p_prob = doc.add_paragraph()
    p_prob.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_prob = p_prob.add_run("SMART INDIA HACKATHON — PROBLEM STATEMENT 26058")
    r_prob.bold = True
    r_prob.font.name = "Calibri"
    r_prob.font.size = Pt(13)
    r_prob.font.color.rgb = RGBColor.from_string(COLOR_ACCENT_HEX)

    # Main Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("AUV Adaptive Sonar Transmitter\nDigital Twin")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(28)
    r_title.font.color.rgb = RGBColor.from_string(COLOR_PRIMARY_HEX)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(6)
    p_sub.paragraph_format.space_after = Pt(24)
    r_sub = p_sub.add_run(
        "End-to-End Engineering Implementation, Validation, Profile Performance Evaluation, "
        "Adaptive Selection Architecture and Current Project Status"
    )
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor.from_string(COLOR_SECONDARY_HEX)

    # Horizontal Accent Line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_line = p_line.add_run("―" * 45)
    r_line.font.name = "Calibri"
    r_line.font.size = Pt(14)
    r_line.font.color.rgb = RGBColor.from_string(COLOR_ACCENT_HEX)

    # Metadata Table
    p_space2 = doc.add_paragraph()
    p_space2.paragraph_format.space_before = Pt(36)

    meta_table = doc.add_table(rows=7, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    meta_data = [
        ("Project Identifier", "SIH 2024–2026 Problem ID: 26058"),
        ("System Classification", "AUV Transmitter Payload Software-Defined Digital Twin"),
        ("Engineering Maturity", "Stage 1 Complete — Pre-Silicon Digital Twin & Analytical Validation"),
        ("Target Embedded Hardware", "STMicroelectronics STM32G474 (170 MHz ARM Cortex-M4F)"),
        ("Document Release Version", "Version 1.1 — Comprehensive Engineering Baseline"),
        ("Automated Validation Status", "64 / 64 Unit & Regression Tests Passing (99 Total Across Suites)"),
        ("Engineering Focus Area", "Adaptive Waveform Profiling, Seawater Absorption & DMA Mapping"),
    ]

    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.3)
        c1.width = Inches(4.2)
        set_cell_background(c0, "F0F4F8")
        set_cell_background(c1, "FAFCFD")
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.name = "Calibri"
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = RGBColor.from_string(COLOR_PRIMARY_HEX)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor.from_string(COLOR_TEXT_HEX)

    # Disclaimer Callout on Cover Page
    doc.add_paragraph().paragraph_format.space_before = Pt(30)
    add_callout(
        doc,
        tag="Engineering Scope Notice",
        title="Pre-Silicon Simulation and Analytical Model Scope",
        body=(
            "This report documents a software-defined digital twin of an adaptive AUV sonar transmitter. "
            "All reported metrics, signal properties, memory allocations, and power estimations are derived from "
            "algorithmic pre-silicon digital simulation and analytical acoustic equations. The current implementation "
            "validates transmitter-side signal synthesis, DAC quantization, DMA memory buffers, and deterministic "
            "adaptation logic. It does NOT validate real physical underwater acoustic propagation, hydrophone reception, "
            "piezoelectric transducer impedance, or hardware bench measurements."
        ),
        callout_type="IMPORTANT"
    )

    doc.add_page_break()


def build_table_of_contents(doc):
    """Builds a formatted Table of Contents overview."""
    add_h1(doc, "Table of Contents")
    add_body(
        doc,
        "This engineering report is organized into 25 technical chapters, structured tables, "
        "and technical appendices detailing the complete digital twin implementation for SIH Problem 26058."
    )

    toc_items = [
        ("1. Executive Summary", "Project summary, concept, digital twin scope, Priority 1 contribution, and architecture"),
        ("2. Problem Statement and Project Motivation", "SIH 26058 context, acoustic trade-offs, and need for adaptive profiling"),
        ("3. Original System Architecture", "Baseline implementation before Priority 1, composite score Q, and weaknesses"),
        ("4. Complete Digital Twin Architecture", "End-to-end signal and control processing pipeline from acquisition to DMA"),
        ("5. LFM Waveform Generation", "Chirp mathematical formulation, phase integration, Hann windowing, and 3 profiles"),
        ("6. DAC Quantization and Memory Implementation", "12-bit DAC mapping, midscale offset, SQNR, and qualified memory footprint"),
        ("7. Adaptive Controller Architecture", "Schmitt hysteresis, N=2 debounce persistence, and ping-boundary latching"),
        ("8. Priority 1: Profile Performance Evaluation", "Transition from passive LUTs to explicit physical profile evaluation"),
        ("9. Frequency-Dependent Seawater Attenuation", "Ainslie-McColm absorption formulation and 5-point discrete band sampling"),
        ("10. Turbidity Model and Engineering Limitations", "Particulate scattering heuristic and honest physical qualification"),
        ("11. Propagation Model", "Simplified relative spherical transmission loss model and boundaries"),
        ("12. Why Each Profile Exists", "Physical justification: LOW_FREQUENCY, BALANCED, and HIGH_FREQUENCY trade-offs"),
        ("13. Two-Tier Profile Selection Architecture", "Propagation viability filtering decoupled from mission utility selection"),
        ("14. Dual Confidence Metrics", "Viability confidence Cv and mission selection confidence Cs formulations"),
        ("15. Parameter Sweep Experiments", "Experimental methodologies and results: Range, Noise, and Environmental sweeps"),
        ("16. Figure-by-Figure Analysis", "Comprehensive visual and technical analysis of all 20 engineering figures"),
        ("17. Hardware Bring-Up Protocol", "Step-by-step engineering roadmap for bench and oscilloscope validation"),
        ("18. Automated Validation", "64/64 passing Python tests, 35 MATLAB checks (99 total), methodology, and verified properties"),
        ("19. Mathematical Derivations", "Analytical proofs of energy conservation, Hilbert phase, and SQNR bounds"),
        ("20. Verified Claims vs Limitations", "Structured tables: Verified Results, Theoretical Limits, and Future Claims"),
        ("21. Current Project Status", "Engineering maturity assessment: what is completed vs what remains for hardware"),
        ("22. Recommended Next Development Roadmap", "Prioritized development roadmap from Priority 2 (Hardware) to Priority 7 (Tank)"),
        ("23. Team Responsibility Guide", "Subsystem ownership guide for firmware, analog, acoustic, and validation leads"),
        ("24. Risks and Open Engineering Questions", "Top 10 ranked engineering challenges, transducer feasibility, and PA design"),
        ("25. Conclusion", "Engineering synthesis, validated contributions, and transition to physical prototyping"),
        ("Appendices (A through E)", "Profile specifications, mathematical equations, test index, file map, and glossary"),
    ]

    toc_table = doc.add_table(rows=len(toc_items), cols=2)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(toc_table)

    for i, (ch, desc) in enumerate(toc_items):
        row = toc_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.8)
        c1.width = Inches(3.7)
        set_cell_margins(c0, top=50, bottom=50, left=80, right=80)
        set_cell_margins(c1, top=50, bottom=50, left=80, right=80)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(ch)
        r0.bold = True
        r0.font.name = "Calibri"
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = RGBColor.from_string(COLOR_PRIMARY_HEX)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(desc)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9)
        r1.font.color.rgb = RGBColor.from_string(COLOR_MUTED_HEX)

    doc.add_page_break()


def build_chapter_01_executive_summary(doc):
    """Builds Chapter 1: Executive Summary."""
    add_h1(doc, "1. Executive Summary")

    add_body(
        doc,
        "Autonomous Underwater Vehicles (AUVs) deployed in subsea exploration, harbor defense, pipeline inspection, "
        "and environmental monitoring operate under severe physical constraints: tightly bounded onboard energy storage, "
        "harsh acoustic propagation environments, and dynamically fluctuating channel conditions. High-frequency acoustic "
        "sonar payloads represent one of the primary sensory mechanisms for subsea navigation, obstacle avoidance, and "
        "bathymetric imaging. However, active sonar transmitters face fundamental physical trade-offs governed by underwater "
        "acoustics: higher frequencies yield narrow spatial beam directivity and superior spatial target discrimination, but "
        "suffer catastrophic chemical absorption losses in seawater; conversely, lower frequencies penetrate far deeper through "
        "turbid and attenuating channels, but require larger physical apertures to avoid beam divergence and deliver coarser "
        "range resolution. Operating with a fixed, static transmission pulse severely degrades either battery endurance, spatial "
        "resolution, or mission operational envelope."
    )

    add_body(
        doc,
        "To solve Smart India Hackathon (SIH) Problem Statement 26058, our engineering team designed, implemented, and "
        "validated a pre-silicon digital twin of a Low-Power, Real-Time Adaptive Software-Defined Sonar Transmitter Payload. "
        "The digital twin models the end-to-end transmitter signal synthesis, 12-bit digital-to-analog converter (DAC) quantization, "
        "direct memory access (DMA) memory architecture, frequency-dependent seawater absorption, and deterministic state-machine "
        "adaptation targeting the STMicroelectronics STM32G474 (170 MHz ARM Cortex-M4F) microcontroller."
    )

    add_callout(
        doc,
        tag="Core Engineering Scope Qualification",
        title="Transmitter-Side Digital Twin Boundary",
        body=(
            "The project currently validates a transmitter-side digital simulation and analytical architecture. "
            "It does NOT yet validate complete real underwater sonar performance, physical two-way echo reflection, "
            "hydrophone receiver SNR, piezoelectric ceramic resonance, or measured bench current consumption. "
            "The physical demonstration for Version 1 is strictly transmitter-side."
        ),
        callout_type="CRITICAL"
    )

    add_h2(doc, "1.1 The Priority 1 Contribution: Physically Justified Profile Selection")
    add_body(
        doc,
        "In the original baseline architecture, profile adaptation was governed by a single heuristic composite score (Q) "
        "that combined turbidity, attenuation, and noise into an arbitrary scalar between 0.0 and 1.0. While algorithmically stable, "
        "this score could not physically answer the central engineering question: 'Why should the transmitter select one waveform "
        "profile over another under a given simulated operational scenario?'"
    )

    add_body(
        doc,
        "The implementation of Priority 1 ('Profile Performance Evaluation & Physical Justification') fundamentally transformed "
        "the transmitter architecture from passive lookup tables into an active, physics-grounded evaluation engine. Specifically, "
        "Priority 1 introduced:"
    )

    add_bullet(doc, "Five-Point In-Band Seawater Absorption: ", "Evaluates chemical relaxation and viscous absorption across 5 discrete frequencies per chirp band using the Ainslie-McColm (1998) model.")
    add_bullet(doc, "Decoupled Two-Tier Selection Hierarchy: ", "Separates physical propagation viability filtering from mission utility optimization, preventing low-frequency chirps from artificially dominating all ranges.")
    add_bullet(doc, "Dual Explainable Confidence Metrics: ", "Computes both Viability Confidence (safety margin above the -65 dB relative policy threshold) and Mission Selection Confidence (utility separation between winner and runner-up).")
    add_bullet(doc, "Deterministic Fallback Architecture: ", "Ensures that if higher-frequency survey or directivity modes fail propagation viability, the controller deterministically falls back to the low-attenuation profile.")
    add_bullet(doc, "Comprehensive Verification: ", "Validated across 64 automated unit and regression tests in Python and 35 validation checks in MATLAB (99 total validation checks across suites) with demonstrated determinism under documented simulation inputs.")

    add_h2(doc, "1.2 End-to-End Architectural Dataflow")
    add_body(
        doc,
        "The complete operational pipeline processes simulated environmental scenarios through analytical acoustics, "
        "filters viable waveforms, optimizes for active mission intent, stabilizes transitions via hysteresis and debounce, "
        "and latches updates strictly at atomic ping boundaries:"
    )

    add_ascii_diagram(
        doc,
        "              Simulated Scenario Inputs (Range R, Depth D, Temp T, Salinity S, Turbidity)\n"
        "                                           │\n"
        "                                           ▼\n"
        "                         Profile Performance Evaluation Engine\n"
        "               [ Ainslie-McColm α(f), Mackenzie c, TL(R), ΔR = c/(2B), Dir_rel ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                              Propagation Viability Filter\n"
        "                     [ Is Relative Propagation Margin >= -65.0 dB ? ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                         Externally Commanded Operating Mode\n"
        "                     [ SURVEY (Resolution) vs DIRECTIVITY (Narrow-Beam) ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                               Mission Utility Selection\n"
        "                     [ Select Viable Candidate with Highest Mission Utility ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                                 Viable Fallback Chain\n"
        "                  [ If Preferred Mode Fails Viability -> Fallback to LOW_FREQ ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                       Raw Candidate Profile + Dual Confidence Metrics\n"
        "                  [ Viability Confidence C_v  &  Mission Selection Confidence C_s ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                             Directional Schmitt Hysteresis\n"
        "                       [ 10% Performance Deadbands Rejection ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                               Debounce Persistence Filter\n"
        "                         [ N = 2 Consecutive Evaluation Cycles ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                               Atomic Ping-Boundary Latch\n"
        "                    [ Latches State at PRI Boundary (DMA TC Emulation) ]\n"
        "                                           │\n"
        "                                           ▼\n"
        "                             Active Waveform Playback & Power\n"
        "                  [ 12-Bit DAC Quantization -> DMA Buffers -> Duty-Cycle Power ]"
    )

    add_h2(doc, "1.3 Current Implementation Maturity Level")
    add_body(
        doc,
        "The project is currently at Stage 1 maturity: Pre-Silicon Algorithmic and Analytical Verification. "
        "The digital twin proves that the mathematical waveform synthesis, 12-bit DAC quantization bounds, "
        "DMA buffer requirements, hysteresis noise immunity, and profile selection logic are robust, explainable, and fully verified. "
        "The next phase of the project transitions this validated digital twin to physical embedded firmware on the STM32G474 "
        "microcontroller and bench oscilloscope characterization."
    )


def build_chapter_02_problem_statement(doc):
    """Builds Chapter 2: Problem Statement and Project Motivation."""
    add_h1(doc, "2. Problem Statement and Project Motivation")

    add_h2(doc, "2.1 SIH Problem Statement 26058 Context")
    add_body(
        doc,
        "Smart India Hackathon Problem 26058 calls for the development of a 'Low-Power, Real-Time Adaptive Software-Defined Sonar "
        "Transmitter Payload for Autonomous Underwater Vehicles (AUVs)'. Modern AUVs are tasked with executing complex, multi-phase "
        "subsea missions ranging from wide-area seabed survey and shallow-water obstacle avoidance to pipeline tracking and port security. "
        "In these missions, acoustic sonar represents the only viable long-range sensing modality, as electromagnetic and optical signals "
        "suffer catastrophic attenuation in seawater within meters."
    )

    add_body(
        doc,
        "However, existing commercial-off-the-shelf (COTS) sonar transmitters suffer from rigid operational limitations: they typically "
        "utilize fixed-frequency, single-bandwidth acoustic pulses driven by analog circuitry or rigid FPGA lookup tables. When an AUV "
        "encounters variable oceanographic conditions—such as entering a sediment-laden river plume, transiting through a thermocline, "
        "or searching for long-range boundaries—a fixed sonar transmitter cannot adapt its acoustic emission. The vehicle either exhausts "
        "its battery through excessive power transmission or loses sensory contact due to acoustic absorption."
    )

    add_h2(doc, "2.2 The Fundamental Acoustic Physics Trade-Offs")
    add_body(
        doc,
        "The design of an adaptive sonar transmitter is governed by three coupled, non-negotiable physical trade-offs in underwater acoustics:"
    )

    add_bullet(
        doc,
        "1. Frequency vs. Acoustic Absorption: ",
        "Seawater acoustic absorption increases dramatically with frequency, governed by chemical relaxation of boric acid (B(OH)3), "
        "magnesium sulfate (MgSO4), and pure water viscous attenuation. At 160 kHz (LOW_FREQUENCY), modeled baseline attenuation is "
        "approximately 18 dB/km; at 425 kHz (HIGH_FREQUENCY), attenuation escalates to ~65 dB/km—a more than 3.5-fold increase in signal "
        "decay per kilometer. High-frequency signals are rapidly absorbed over extended propagation distances."
    )

    add_bullet(
        doc,
        "2. Bandwidth vs. Range Resolution: ",
        "Under ideal matched-filter pulse compression, the theoretical range resolution limit (ΔR) is governed strictly by the chirp sweep "
        "bandwidth B through ΔR = c / (2B), where c is seawater sound speed (~1500 m/s). To achieve fine range resolution capable of resolving "
        "closely spaced structural features (such as pipeline flanges or underwater cables), the transmitter must emit the widest possible "
        "bandwidth. A 200 kHz bandwidth achieves an ideal range resolution limit of 3.75 mm, whereas a 120 kHz bandwidth yields only 6.25 mm."
    )

    add_bullet(
        doc,
        "3. Frequency vs. Spatial Beam Directivity: ",
        "For an acoustic transducer of fixed physical diameter D, the acoustic wavelength is λ = c / f. The theoretical beam divergence "
        "angle θ is inversely proportional to frequency (θ ∝ λ / D = c / (f · D)). Consequently, higher operating frequencies yield "
        "tighter beam directivity and superior spatial angular resolution, minimizing boundary reverberation and pinpointing small obstacles. "
        "A 425 kHz center frequency delivers 1.417× higher theoretical directivity proxy than a 300 kHz reference."
    )

    add_h2(doc, "2.3 The Central Engineering Question")
    add_body(
        doc,
        "The limitations of fixed-frequency transmitters lead directly to the core engineering question motivating this digital twin:"
    )

    add_callout(
        doc,
        tag="Central Engineering Inquiry",
        title="Physical Justification of Waveform Adaptation",
        body=(
            "'Why should the adaptive transmitter select one waveform profile instead of another under a given simulated scenario?'\n\n"
            "An adaptive controller must not switch waveforms arbitrarily or rely on opaque heuristics. It must possess an explicit, "
            "explainable physical rationale: balancing propagation viability (ensuring the signal survives seawater absorption to reach the target) "
            "against mission utility (maximizing range resolution for survey mapping or maximizing spatial directivity for obstacle tracking)."
        ),
        callout_type="NOTE"
    )

    add_h2(doc, "2.4 Why Multiple Predefined LFM Profiles are Required")
    add_body(
        doc,
        "On an energy-constrained embedded microcontroller such as the STM32G474 (operating at 170 MHz with limited mathematical co-processing), "
        "synthesizing arbitrary, continuously variable wideband waveforms in real time is computationally prohibitive and introduces unacceptable "
        "phase jitter. Furthermore, physical acoustic transducers possess finite electromechanical bandwidths and resonant impedance characteristics. "
        "Therefore, modern software-defined sonar architectures employ a discrete set of carefully engineered canonical Linear Frequency Modulated "
        "(LFM) profiles stored as precomputed lookup tables (LUTs) in memory. This enables deterministic, zero-latency DMA playback while "
        "providing the controller with distinct operating regimes."
    )


def build_chapter_03_original_system_architecture(doc):
    """Builds Chapter 3: Original System Architecture."""
    add_h1(doc, "3. Original System Architecture")

    add_body(
        doc,
        "Prior to the implementation of Priority 1, the digital twin simulator modeled a baseline adaptive transmitter pipeline "
        "designed to demonstrate real-time potentiometer acquisition, threshold-based profile switching, and DMA-compatible "
        "12-bit DAC waveform playback. This chapter documents the baseline architecture, its operating mechanisms, and its critical weaknesses."
    )

    add_h2(doc, "3.1 Baseline System Components")
    add_body(
        doc,
        "The original system modeled the transmitter payload across ten sequential functional stages:"
    )

    add_bullet(doc, "1. Analog Control Emulation: ", "Three simulated potentiometers generating voltages in [0.0, 1.0], emulating turbidity, range/depth, and target reflectivity (representing future receiver feedback).")
    add_bullet(doc, "2. Composite Channel Quality Score (Q): ", "A single weighted scalar in [0.0, 1.0] computed from environmental, attenuation, and noise penalty components.")
    add_bullet(doc, "3. Threshold-Based Profile Selection: ", "Static thresholds mapping Q into three profiles: Muddy (Q < 0.30), Balanced (0.30 <= Q <= 0.70), and Clear (Q > 0.70).")
    add_bullet(doc, "4. LFM Chirp Synthesis: ", "Analytical phase-integrated linear frequency modulated pulses generated at 4.0 MSPS across a 2.0 ms duration.")
    add_bullet(doc, "5. Hann Windowing: ", "Application of a raised-cosine Hann envelope to suppress pulse turn-on/turn-off edge transients.")
    add_bullet(doc, "6. 12-Bit DAC Quantization: ", "Scaling normalized floating-point signals to unsigned integer codes in [0, 4095] with a 2048 midscale bias.")
    add_bullet(doc, "7. DMA Waveform Storage: ", "Allocation of precomputed 8,000-sample uint16_t lookup tables in flash and active SRAM buffers.")
    add_bullet(doc, "8. Directional Schmitt Hysteresis: ", "10% deadbands applied to analog inputs to prevent rapid threshold chatter.")
    add_bullet(doc, "9. Debounce Persistence Filtering: ", "An N=2 ping persistence requirement before committing a new profile candidate.")
    add_bullet(doc, "10. Ping-Boundary Profile Latching: ", "Atomic state latching synchronized strictly to the 20.0 ms Pulse Repetition Interval (PRI).")

    add_h2(doc, "3.2 The Composite Channel Quality Score (Q)")
    add_body(
        doc,
        "In the original MATLAB channel model (channel_model.m), environmental parameters were compressed into a single "
        "quality score Q through a linear combination of normalized heuristic sub-penalties:"
    )

    add_equation_box(
        doc,
        "Q = w_env · Q_env + w_attn · Q_attn + w_noise · Q_noise\n"
        "where Q_env = 1.0 - turb/100,  Q_attn = 1.0 - clip(α_total / 160, 0, 1),  Q_noise = 1.0 - clip((Noise - 40)/40, 0, 1)",
        "Equation 3.1: Original Heuristic Composite Channel Quality Score Formulation"
    )

    add_body(
        doc,
        "The configuration weights were typically set to w_env = 0.40, w_attn = 0.40, and w_noise = 0.20. Based on the resulting scalar Q, "
        "a simple threshold selector assigned the candidate profile."
    )

    add_h2(doc, "3.3 Critical Analysis: Weaknesses of the Original Architecture")
    add_body(
        doc,
        "While the original architecture successfully proved real-time DSP stability, Schmitt hysteresis, debounce filtering, "
        "and DMA memory sizing, it suffered from a fundamental engineering deficiency: it lacked physical explainability. "
        "Specifically, four critical weaknesses were identified during architectural review:"
    )

    add_bullet(
        doc,
        "Conflation of Uncorrelated Physical Phenomena: ",
        "The composite score Q compressed optical turbidity, chemical absorption, and acoustic noise into an arbitrary dimensionless scalar. "
        "These three physical phenomena operate on entirely different physical mechanisms and have uncorrelated impacts on acoustic propagation. "
        "Collapsing them into a single weighted sum obscured which physical constraint was actually limiting transmission."
    )

    add_bullet(
        doc,
        "Inability to Answer 'Why Profile A vs. Profile B?': ",
        "Under the original controller, if Q dropped from 0.75 to 0.65, the system demoted from Clear to Balanced. However, the system could "
        "not state why Balanced was physically superior. It did not evaluate whether the target range exceeded the absorption limit of Clear, "
        "nor did it model the range resolution sacrifice incurred by the switch."
    )

    add_bullet(
        doc,
        "Absence of Range and Mission Context: ",
        "The original score Q did not incorporate target distance (range R) into the selection logic. A channel with high attenuation might be "
        "completely viable over a 15-meter range, but impossible over 150 meters. By ignoring range, the baseline system could not establish "
        "true propagation viability."
    )

    add_bullet(
        doc,
        "The Low-Frequency Paradox: ",
        "If the controller simply sought to minimize acoustic transmission loss, LOW_FREQUENCY (100–220 kHz) would win under every possible "
        "operating condition, because its seawater absorption is universally lower than higher frequencies. The original system lacked a mechanism "
        "to balance propagation survival against mission performance (range resolution and spatial directivity)."
    )

    add_callout(
        doc,
        tag="Architectural Limitation Summary",
        title="Why the Single Heuristic Score Was Insufficient",
        body=(
            "A single composite scalar cannot simultaneously represent propagation viability, range resolution requirements, "
            "and spatial directivity objectives. The controller could execute profile switches, but could not physically justify them. "
            "This limitation directly necessitated the design and implementation of Priority 1."
        ),
        callout_type="WARNING"
    )


def build_chapter_04_complete_digital_twin_architecture(doc):
    """Builds Chapter 4: Complete Digital Twin Architecture."""
    add_h1(doc, "4. Complete Digital Twin Architecture")

    add_body(
        doc,
        "Following the integration of Priority 1, the digital twin represents a complete, mathematically rigorous signal synthesis "
        "and adaptive control pipeline. Every functional block is explicitly modeled in both Python (src/) and MATLAB (matlab/), "
        "maintaining bit-exact determinism across platforms."
    )

    add_h2(doc, "4.1 Thirteen-Stage Signal and Control Pipeline")
    add_body(
        doc,
        "The complete digital twin processes acoustic scenarios through thirteen tightly coupled engineering stages:"
    )

    stages = [
        ("Stage 1: Analog Control Acquisition", "Acquires 3 simulated potentiometer voltages in [0.0, 1.0] representing turbidity, range/depth, and target reflectivity (future RX SNR feedback).", "src/adaptation.py", "matlab/channel_model.m"),
        ("Stage 2: Environmental Scenario Processing", "Scales analog controls to physical oceanographic variables: Range R (10–200 m), Depth D (50 m), Temp T (20°C), Salinity S (35 PSU).", "src/profile_evaluator.py", "matlab/evaluate_profile_performance.m"),
        ("Stage 3: 5-Point Profile Performance Evaluation", "Evaluates Ainslie-McColm (1998) absorption at 5 discrete frequencies across each profile's bandwidth, computing band-mean attenuation α_bar.", "src/profile_evaluator.py", "matlab/evaluate_profile_performance.m"),
        ("Stage 4: Relative Propagation Model", "Calculates simplified one-way transmission loss TL(R) = 20 log10(R) + α_bar · (R/1000) and relative propagation margin M_rel = -TL - NP.", "src/profile_evaluator.py", "matlab/evaluate_profile_performance.m"),
        ("Stage 5: Propagation Viability Filtering", "Applies relative viability threshold (Thresh_viab = -65.0 dB policy parameter) to classify each profile as viable or non-viable.", "src/profile_evaluator.py", "matlab/evaluate_profile_performance.m"),
        ("Stage 6: Mission Objective Selection", "Selects among viable profiles based on externally commanded mode: SURVEY (maximizes sweep bandwidth B) or DIRECTIVITY (maximizes center frequency fc).", "src/profile_evaluator.py", "matlab/evaluate_profile_performance.m"),
        ("Stage 7: Dual Confidence Metric Computation", "Calculates Viability Confidence Cv (margin above -65 dB floor) and Mission Selection Confidence Cs (utility separation over runner-up).", "src/profile_evaluator.py", "matlab/evaluate_profile_performance.m"),
        ("Stage 8: Directional Schmitt Hysteresis", "Applies 10% deadband filtering to prevent rapid oscillating transitions when inputs fluctuate near profile boundaries.", "src/adaptation.py", "matlab/adaptive_controller.m"),
        ("Stage 9: Debounce Persistence Filtering", "Requires candidate profile to persist across N=2 consecutive evaluation cycles before committing to pending profile state.", "src/adaptation.py", "matlab/adaptive_controller.m"),
        ("Stage 10: Atomic Ping-Boundary Latching", "Latches pending profile to active profile strictly at the 20.0 ms PRI boundary, modeling STM32 DMA Transfer-Complete (TC) interrupt synchronization.", "src/adaptation.py", "matlab/adaptive_controller.m"),
        ("Stage 11: LFM Chirp Phase Integration", "Synthesizes continuous-phase chirp s(t) = cos(2π(f0·t + 0.5·k·t²)) at 4.0 MSPS across 2.0 ms duration (8,000 samples).", "src/waveform.py", "matlab/generate_lfm_chirp.m"),
        ("Stage 12: Hann Window Tapering", "Multiplies chirp by raised-cosine Hann window w[n] = 0.5(1 - cos(2πn/(N-1))) to eliminate edge discontinuities and suppress spectral sidelobes.", "src/waveform.py", "matlab/generate_lfm_chirp.m"),
        ("Stage 13: 12-Bit DAC Quantization & DMA Mapping", "Quantizes windowed signal to uint16 codes in [0, 4095] with midscale 2048, verifying DMA-ready memory buffers and duty-cycle power.", "src/waveform.py, src/power_model.py", "matlab/dac_quantize.m, matlab/power_model.m"),
    ]

    col_w = [Inches(1.8), Inches(2.7), Inches(1.0), Inches(1.0)]
    aligns = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT]
    add_styled_table(doc, ["Pipeline Stage", "Functional Implementation Description", "Python Module", "MATLAB Script"], stages, col_widths=col_w, alignments=aligns)

    add_h2(doc, "4.2 Cross-Platform Architecture Mapping")
    add_body(
        doc,
        "Every Python module in src/ has an exact functional equivalent in matlab/. Parameter definitions are synchronized "
        "via Single Source of Truth configuration files (src/config.py and matlab/config_sonar.m). This dual-codebase "
        "strategy provides independent numerical validation, ensuring that digital twin conclusions are not artifacts of a "
        "single software environment."
    )


def build_chapter_05_lfm_waveform_generation(doc):
    """Builds Chapter 5: LFM Waveform Generation."""
    add_h1(doc, "5. LFM Waveform Generation")

    add_body(
        doc,
        "Linear Frequency Modulated (LFM) chirps are the standard waveform family for active subsea sonar systems. "
        "Unlike unmodulated continuous-wave (CW) pulses whose range resolution is fundamentally constrained by pulse duration "
        "(ΔR = c · T_p / 2), LFM chirps decouple signal energy from range resolution through matched-filter pulse compression. "
        "By linearly sweeping frequency across a wide bandwidth B, the effective pulse duration after matched filtering is "
        "compressed to approximately τ_comp ≈ 1 / B, achieving fine spatial resolution while delivering high acoustic energy on target."
    )

    add_h2(doc, "5.1 Mathematical Formulation and Continuous Phase Integration")
    add_body(
        doc,
        "The digital twin synthesizes LFM chirps using exact analytical continuous-phase integration. "
        "For a chirp spanning from start frequency f_0 to end frequency f_1 over pulse duration T_p, the chirp sweep slope k is:"
    )

    add_equation_box(
        doc,
        "k = (f_1 - f_0) / T_p  [Hz/s]",
        "Equation 5.1: Linear Frequency Modulation Chirp Rate (Chirp Slope)"
    )

    add_body(
        doc,
        "The instantaneous frequency f(t) varies linearly with time t across the interval t ∈ [0, T_p]:"
    )

    add_equation_box(
        doc,
        "f(t) = f_0 + k · t  [Hz]",
        "Equation 5.2: Instantaneous Frequency Modulation Trajectory"
    )

    add_body(
        doc,
        "To avoid severe phase discontinuities and harmonic splattering, the phase argument φ(t) must be the exact continuous "
        "integral of instantaneous angular frequency ω(t) = 2π f(t):"
    )

    add_equation_box(
        doc,
        "φ(t) = 2π ∫₀ᵗ f(τ) dτ = 2π ∫₀ᵗ (f_0 + k·τ) dτ = 2π (f_0 · t + 0.5 · k · t²)",
        "Equation 5.3: Analytical Continuous Phase Integration"
    )

    add_body(
        doc,
        "The unwindowed continuous-time chirp signal s_raw(t) scaled by normalized amplitude factor A ∈ (0.0, 1.0] is:"
    )

    add_equation_box(
        doc,
        "s_raw(t) = A · cos(φ(t)) = A · cos(2π (f_0 · t + 0.5 · k · t²))",
        "Equation 5.4: Unwindowed Continuous-Time LFM Chirp"
    )

    add_h2(doc, "5.2 Raised-Cosine Hann Window Tapering")
    add_body(
        doc,
        "In discrete signal synthesis, truncating a chirp abruptly at t = 0 and t = T_p creates sharp rectangular step discontinuities. "
        "In the frequency domain, rectangular gating convolves the chirp spectrum with a sinc(πf T_p) function, producing heavy "
        "spectral sidelobes (first sidelobe at only -13.3 dB relative to peak) and out-of-band spectral leakage. "
        "In an acoustic transmitter, these high-frequency edge transients excite out-of-band transducer resonances and cause acoustic ringing."
    )

    add_body(
        doc,
        "To eliminate start/end edge discontinuities and achieve steep stopband suppression, the digital twin applies a discrete "
        "symmetric raised-cosine Hann window w[n] across all N_p samples:"
    )

    add_equation_box(
        doc,
        "w[n] = 0.5 · (1 - cos(2π · n / (N_p - 1))),  for n = 0, 1, ..., N_p - 1",
        "Equation 5.5: Discrete Raised-Cosine Hann Window Formulation"
    )

    add_body(
        doc,
        "The final windowed discrete floating-point signal s[n] is computed as the point-wise product:"
    )

    add_equation_box(
        doc,
        "s[n] = w[n] · s_raw[n] = 0.5 · (1 - cos(2πn / (N_p - 1))) · A · cos(2π (f_0 · (n·T_s) + 0.5 · k · (n·T_s)²))",
        "Equation 5.6: Windowed Discrete LFM Chirp Signal"
    )

    add_callout(
        doc,
        tag="Engineering Validation Notice",
        title="Spectral Sidelobe Suppression vs. Physical Analog Filtering",
        body=(
            "Digital simulation confirms that Hann windowing suppresses spectral sidelobes by >50 dB in discrete FFT analysis. "
            "However, this digital suppression does not replace external analog reconstruction filtering. "
            "Physical harmonics resulting from DAC zero-order hold (ZOH) stair-steps and analog amplifier non-linearities "
            "must be validated using a bench spectrum analyzer during hardware bring-up."
        ),
        callout_type="NOTE"
    )

    add_h2(doc, "5.3 Detailed Specification of the Three Canonical Profiles")
    add_body(
        doc,
        "The digital twin establishes exactly three canonical transmission profiles locked for Version 1 runtime. "
        "All three profiles operate at sample rate F_s = 4.0 MSPS with pulse duration T_p = 2.0 ms (N_p = 8,000 samples):"
    )

    canon = get_canonical_results()
    low_p = canon["profiles"]["LOW_FREQUENCY"]
    bal_p = canon["profiles"]["BALANCED"]
    high_p = canon["profiles"]["HIGH_FREQUENCY"]

    prof_data = [
        ("LOW_FREQUENCY (Profile 1)", f"{low_p['f_start_khz']:.1f} kHz", f"{low_p['f_end_khz']:.1f} kHz", f"{low_p['f_center_khz']:.1f} kHz", f"{low_p['bandwidth_khz']:.1f} kHz", f"{low_p['chirp_slope_mhz_s']:.1f} MHz/s", f"{low_p['amplitude_factor']:.2f} (Max)", f"{low_p['alpha_band_mean_db_km']:.2f} dB/km", f"{low_p['range_resolution_mm']:.2f} mm", f"{low_p['relative_directivity']:.3f}x", "Degraded channel penetration & long-range fallback"),
        ("BALANCED (Profile 2)", f"{bal_p['f_start_khz']:.1f} kHz", f"{bal_p['f_end_khz']:.1f} kHz", f"{bal_p['f_center_khz']:.1f} kHz", f"{bal_p['bandwidth_khz']:.1f} kHz", f"{bal_p['chirp_slope_mhz_s']:.1f} MHz/s", f"{bal_p['amplitude_factor']:.2f} (Nom)", f"{bal_p['alpha_band_mean_db_km']:.2f} dB/km", f"{bal_p['range_resolution_mm']:.2f} mm", f"{bal_p['relative_directivity']:.3f}x", "Primary survey default: finest range resolution"),
        ("HIGH_FREQUENCY (Profile 3)", f"{high_p['f_start_khz']:.1f} kHz", f"{high_p['f_end_khz']:.1f} kHz", f"{high_p['f_center_khz']:.1f} kHz", f"{high_p['bandwidth_khz']:.1f} kHz", f"{high_p['chirp_slope_mhz_s']:.1f} MHz/s", f"{high_p['amplitude_factor']:.2f} (Low)", f"{high_p['alpha_band_mean_db_km']:.2f} dB/km", f"{high_p['range_resolution_mm']:.2f} mm", f"{high_p['relative_directivity']:.3f}x", "Narrow-beam directivity mode for obstacle tracking"),
    ]

    col_w = [Inches(1.5), Inches(0.5), Inches(0.5), Inches(0.5), Inches(0.5), Inches(0.6), Inches(0.5), Inches(0.6), Inches(0.5), Inches(0.4), Inches(1.4)]
    headers = ["Profile Name", "f_start", "f_end", "f_center", "Bandwidth", "Chirp Slope", "Amp A", "Mean α", "ΔR", "Dir_rel", "Engineering Mission Purpose"]
    add_styled_table(doc, headers, prof_data, col_widths=None)


def build_chapter_06_dac_quantization_and_memory(doc):
    """Builds Chapter 6: DAC Quantization and Memory Implementation."""
    add_h1(doc, "6. DAC Quantization and Memory Implementation")

    add_body(
        doc,
        "In an embedded software-defined sonar transmitter, synthesizing high-frequency acoustic signals requires bridging "
        "the discrete mathematical model and physical mixed-signal silicon. The target microcontroller—the STMicroelectronics "
        "STM32G474—features integrated 12-bit digital-to-analog converters capable of high-speed DMA-driven output up to several MSPS. "
        "The digital twin models this conversion process with exact integer arithmetic, evaluating quantization errors, signal-to-quantization-noise "
        "ratio (SQNR), and memory footprints."
    )

    add_h2(doc, "6.1 12-Bit Unsigned DAC Quantization Model")
    add_body(
        doc,
        "The STM32G474 DAC peripheral accepts 12-bit unsigned integers spanning codes 0 to 4095 (2¹² - 1). "
        "Because acoustic transducers are AC-coupled devices requiring bipolar voltage excitation (±V_peak), the transmitter "
        "must bias the resting acoustic state at DAC midscale (code 2048, corresponding to V_ref / 2 = 1.65 V on a 3.3 V analog rail). "
        "The normalized floating-point signal s[n] ∈ [-1.0, +1.0] is mapped to 12-bit integer DAC codes via:"
    )

    add_equation_box(
        doc,
        "DAC_Code[n] = round(2048 + 2047 · s[n])\n"
        "clamped strictly to: DAC_Code[n] ∈ [0, 4095],  stored as uint16_t",
        "Equation 6.1: 12-Bit Unsigned DAC Quantization Mapping"
    )

    add_body(
        doc,
        "When the transmitter is idle (zero AC acoustic swing, A = 0), the DAC outputs constant code 2048 (1.65 V DC bias). "
        "During transmission, a full-scale pulse (A = 1.0) swings symmetrically between code 1 (0.0008 V) and code 4095 (3.3000 V), "
        "maximizing dynamic range without digital saturation or clipping."
    )

    add_h2(doc, "6.2 Quantization Error and Simulated SQNR")
    add_body(
        doc,
        "Quantization error represents the difference between the reconstructed analog level and the ideal mathematical signal. "
        "For code DAC_Code[n], the reconstructed voltage on a 3.3 V reference rail is V_DAC[n] = (DAC_Code[n] / 4095) · 3.3 V. "
        "The quantization error in Least Significant Bits (LSB) is:"
    )

    add_equation_box(
        doc,
        "ε_q[n] = DAC_Code[n] - (2048 + 2047 · s[n])  [LSB]",
        "Equation 6.2: Quantization Error Residual in LSB"
    )

    add_body(
        doc,
        "Under standard rounding, quantization error is strictly bounded within [-0.5, +0.5] LSB. "
        "With 1 LSB = 3.3 V / 4095 ≈ 0.8058 mV, the maximum voltage error is bounded within ±0.4029 mV. "
        "The simulated Signal-to-Quantization-Noise Ratio (SQNR) is computed across all N_p samples:"
    )

    add_equation_box(
        doc,
        "SQNR = 10 · log10( ∑ₙ₌₀^{N_p-1} s²[n]  /  ∑ₙ₌₀^{N_p-1} (s[n] - s_quant[n])² )  [dB]\n"
        "where s_quant[n] = (DAC_Code[n] - 2048) / 2047",
        "Equation 6.3: Simulated Signal-to-Quantization-Noise Ratio (SQNR)"
    )

    add_body(
        doc,
        "For an ideal 12-bit converter excited by an unwindowed full-scale sine wave, theoretical SQNR is given by Bennett's formula: "
        "SQNR_theory = 6.02 · N_bits + 1.76 dB = 74.0 dB. In our digital twin, the application of the Hann window reduces total signal power "
        "relative to the quantization noise floor. The simulated SQNR measured across all three profiles is:"
    )

    add_bullet(doc, "LOW_FREQUENCY (100–220 kHz): ", "Simulated SQNR = 69.67 dB")
    add_bullet(doc, "BALANCED (200–400 kHz): ", "Simulated SQNR = 69.67 dB")
    add_bullet(doc, "HIGH_FREQUENCY (350–500 kHz): ", "Simulated SQNR = 69.70 dB")

    add_body(
        doc,
        "These results confirm that 12-bit quantization introduces virtually zero distortion into the synthesized chirp, "
        "maintaining dynamic range >69 dB prior to analog power amplification."
    )

    add_h2(doc, "6.3 Memory Footprint Qualification and DMA Architecture")
    add_body(
        doc,
        "A critical engineering question for embedded implementation is whether the microcontroller possesses sufficient memory "
        "to store and stream these wideband waveform tables without CPU intervention."
    )

    add_callout(
        doc,
        tag="Qualified Memory Footprint Statement",
        title="Lookup Table vs. Firmware Memory Allocation",
        body=(
            "The generated waveform LUTs occupy approximately 48 KB before firmware and other memory allocations, "
            "while individual active DMA buffers require approximately 16 KB.\n\n"
            "Do NOT claim that the entire firmware fits in 16 KB or 48 KB. The 48 KB figure accounts strictly for the three "
            "precomputed 8,000-sample uint16_t lookup tables in Flash. Compiled firmware, RTOS kernel, stack, heap, and peripheral "
            "descriptors require additional memory."
        ),
        callout_type="CRITICAL"
    )

    add_body(
        doc,
        "Memory sizing breakdown for the target STM32G474 (128 KB SRAM, 512 KB Flash):"
    )

    mem_data = [
        ("Single Waveform LUT Length", "8,000 samples", "F_s = 4.0 MSPS, T_p = 2.0 ms (N_p = 8,000)"),
        ("Single Waveform Data Size", "16,000 bytes (15.625 KiB / ~16.0 KB)", "8,000 samples × 2 bytes/sample (uint16_t)"),
        ("Active Ping DMA Buffer (SRAM)", "16.0 KB", "Occupies 12.5% of total 128 KB SRAM on STM32G474"),
        ("All 3 Waveform LUTs (Flash)", "48.0 KB (46.875 KiB)", "Occupies 9.375% of total 512 KB Flash on STM32G474"),
        ("Remaining SRAM for System", "112.0 KB (87.5% headroom)", "Available for RTOS, stack, heap, ADC DMA circular buffers"),
        ("Remaining Flash for Code", "464.0 KB (90.6% headroom)", "Available for compiled firmware image and communications"),
    ]

    col_w = [Inches(2.2), Inches(2.0), Inches(2.3)]
    add_styled_table(doc, ["Memory Parameter", "Allocated Capacity", "Engineering Context & Hardware Headroom"], mem_data, col_widths=col_w)

    add_body(
        doc,
        "DMA Playback Architecture: In the STM32G474, the high-speed DAC is triggered by Timer TRGO update events operating at exactly 4.0 MHz. "
        "Each TRGO event triggers a direct memory-to-peripheral DMA transfer (DMA1 Channel 1) moving one 16-bit half-word from the active LUT "
        "in memory directly into the DAC holding register (DAC_DHR12R1). The transfer operates autonomously with zero CPU overhead during pulse emission."
    )


def build_chapter_07_adaptive_controller_architecture(doc):
    """Builds Chapter 7: Adaptive Controller Architecture."""
    add_h1(doc, "7. Adaptive Controller Architecture")

    add_body(
        doc,
        "The adaptive controller acts as the real-time supervisor of the transmitter payload. Operating an adaptive subsea "
        "transmitter presents severe stability challenges: analog potentiometer voltages, ADC thermal noise, and fluctuating channel "
        "estimates can cause rapid, erratic profile switching (chatter). If profile switching occurs mid-pulse, it induces severe phase "
        "discontinuities, causing acoustic shock and damaging power amplifier stages. "
        "The digital twin implements a four-stage stabilization architecture to guarantee deterministic, chatter-free operation."
    )

    add_h2(doc, "7.1 Directional Schmitt-Trigger Hysteresis")
    add_body(
        doc,
        "To prevent state oscillation when an environmental control voltage sits near a profile decision boundary, the adaptation engine "
        "(src/adaptation.py and matlab/adaptive_controller.m) implements two-threshold directional Schmitt-trigger hysteresis. "
        "Each transition boundary is separated by a 10% deadband:"
    )

    add_bullet(doc, "Low-to-Mid Transition (LOW_FREQUENCY → BALANCED): ", "Triggered only when the candidate score rises strictly above upper threshold T_up = 0.40.")
    add_bullet(doc, "Mid-to-Low Transition (BALANCED → LOW_FREQUENCY): ", "Triggered only when the candidate score falls strictly below lower threshold T_dn = 0.30 (a 10% deadband).")
    add_bullet(doc, "Mid-to-High Transition (BALANCED → HIGH_FREQUENCY): ", "Triggered only when the candidate score rises strictly above upper threshold T_up = 0.70.")
    add_bullet(doc, "High-to-Mid Transition (HIGH_FREQUENCY → BALANCED): ", "Triggered only when the candidate score falls strictly below lower threshold T_dn = 0.60 (a 10% deadband).")

    add_body(
        doc,
        "If an input voltage fluctuates within [0.30, 0.40] or [0.60, 0.70], the controller maintains its previous committed state, "
        "completely eliminating boundary hunting."
    )

    add_h2(doc, "7.2 Debounce Persistence Filtering (N = 2 Pings)")
    add_body(
        doc,
        "Even with hysteresis, a single anomalous voltage spike (e.g., potentiometer wiper bounce, transient acoustic noise burst, or ADC EMI) "
        "could cross the deadband and trigger an unwanted profile switch. To filter out transient disturbances, the controller passes all "
        "hysteresis-approved candidates through a debounce persistence counter requiring N = 2 consecutive identical evaluations:"
    )

    add_equation_box(
        doc,
        "If Raw_Candidate ≠ Pending_Profile:\n"
        "    If Raw_Candidate == Debounce_Candidate:\n"
        "        Debounce_Counter = Debounce_Counter + 1\n"
        "    Else:\n"
        "        Debounce_Candidate = Raw_Candidate\n"
        "        Debounce_Counter = 1\n"
        "    If Debounce_Counter >= N (where N = 2):\n"
        "        Pending_Profile = Debounce_Candidate\n"
        "        Debounce_Counter = 0\n"
        "Else:\n"
        "    Debounce_Candidate = Pending_Profile\n"
        "    Debounce_Counter = 0",
        "Algorithm 7.1: N=2 Debounce Persistence Logic"
    )

    add_body(
        doc,
        "A transient condition that persists for only a single evaluation cycle is discarded, preventing unnecessary reconfiguration."
    )

    add_h2(doc, "7.3 Atomic Ping-Boundary Profile Latching")
    add_body(
        doc,
        "A foundational safety requirement of the sonar transmitter is that active waveform properties (frequency sweep, duration, amplitude) "
        "must NEVER alter during pulse transmission. Modifying DMA buffer pointers or frequency parameters mid-pulse causes abrupt voltage "
        "discontinuities, generates extreme spectral splattering, and can destroy output power amplifier stages."
    )

    add_body(
        doc,
        "The digital twin implements atomic ping-boundary latching (modeling PingController in src/adaptation.py). "
        "During the 2.0 ms active transmission window, the transmitter state is strictly locked. When a new profile is committed by the debounce "
        "filter, it is held in a 'Pending' register. Only at the completion of the 20.0 ms Pulse Repetition Interval (PRI)—corresponding to the "
        "DMA Transfer-Complete (TC) interrupt in embedded firmware—is the pending profile atomically latched into the 'Active' register for the "
        "subsequent ping."
    )

    add_callout(
        doc,
        tag="Hardware Synchronization Boundary",
        title="DMA Transfer-Complete Interrupt Emulation",
        body=(
            "Ping-boundary latching is designed to be compatible with STM32 DMA transfer-complete synchronization. "
            "In physical firmware bring-up, the DMA Transfer-Complete (TC) interrupt service routine (ISR) updates the active LUT buffer "
            "pointer between pings. Physical DMA interrupt behavior, ISR latency, and register latching have not yet been measured "
            "on bench hardware."
        ),
        callout_type="NOTE"
    )


print("Part 1 builder functions loaded.")
