"""
results_sections_part3.py
Engineering Report Generator - Part 3: Sections 6 to 12
SIH Problem 26058: AUV Adaptive Sonar Digital Twin
Complete Results, Outputs and Engineering Interpretation Report
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL


def build_sections_6_to_12(doc, helpers):
    """Sections 6 to 12: Range Sweep, Noise, Environmental, Signal Gen, DAC, Memory, Controller."""
    add_h1, add_h2, add_h3 = helpers['add_h1'], helpers['add_h2'], helpers['add_h3']
    add_body, add_bullet = helpers['add_body'], helpers['add_bullet']
    add_callout, add_equation_box = helpers['add_callout'], helpers['add_equation_box']
    add_styled_table = helpers['add_styled_table']

    # --------------------------------------------------------------------------
    # SECTION 6: RANGE SWEEP OUTPUTS
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 6: Range Sweep Outputs")
    add_body(doc,
        "The Range Sweep Experiment evaluates the acoustic performance, propagation viability, and autonomous selection "
        "decisions across nine discrete target distances spanning from 10.0 m to 200.0 m under the nominal Survey Mode objective. "
        "Table 6.1 presents the actual numerical values extracted directly from the repository's execution of `run_range_sweep()`."
    )

    range_headers = ["Range (m)", "LOW Margin (dB)", "BAL Margin (dB)", "HIGH Margin (dB)", "Viable Profiles", "Selected Profile", "Viability Conf", "Mission Conf"]
    range_data = [
        ["10.0 m", "-20.64 dB", "-21.06 dB", "-21.37 dB", "LOW, BAL, HIGH", "BALANCED", "1.00", "1.00"],
        ["25.0 m", "-29.57 dB", "-30.62 dB", "-31.37 dB", "LOW, BAL, HIGH", "BALANCED", "1.00", "1.00"],
        ["50.0 m", "-37.20 dB", "-39.30 dB", "-40.81 dB", "LOW, BAL, HIGH", "BALANCED", "1.00", "1.00"],
        ["75.0 m", "-42.34 dB", "-45.47 dB", "-47.75 dB", "LOW, BAL, HIGH", "BALANCED", "1.00", "1.00"],
        ["100.0 m", "-46.45 dB", "-50.63 dB", "-53.66 dB", "LOW, BAL, HIGH", "BALANCED", "0.96", "1.00"],
        ["125.0 m", "-50.00 dB", "-55.23 dB", "-59.02 dB", "LOW, BAL, HIGH", "BALANCED", "0.65", "1.00"],
        ["150.0 m", "-53.19 dB", "-59.47 dB", "-64.02 dB", "LOW, BAL, HIGH", "BALANCED", "0.37", "1.00"],
        ["175.0 m", "-56.14 dB", "-63.47 dB", "-68.77 dB", "LOW, BAL (HIGH Out)", "BALANCED", "0.10", "1.00"],
        ["200.0 m", "-58.91 dB", "-67.28 dB", "-73.35 dB", "LOW Only (BAL/HIGH Out)", "LOW_FREQUENCY", "0.41", "1.00"],
    ]
    col_widths = [Inches(0.9), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.4), Inches(1.2), Inches(0.9), Inches(0.9)]
    add_styled_table(doc, range_headers, range_data, col_widths=col_widths)

    add_h2(doc, "6.1 Narrative Analysis of Range Regime Transitions")
    add_body(doc,
        "The numerical sweep demonstrates three distinct operational regimes governed by the physical balance between "
        "spherical spreading loss and frequency-dependent absorption:"
    )
    add_bullet(doc, "Near-Field Regime (10 m to 50 m): ",
        "All three profiles maintain abundant acoustic margin (> 24 dB above viability floor). Spreading loss dominates "
        "completely, keeping margin separation between profiles tight (only 3.61 dB spread at 50 m). Because propagation "
        "is unconstrained, the controller selects BALANCED to capitalize on its 200 kHz bandwidth, achieving 3.75 mm spatial resolution. "
        "Viability Confidence and Selection Confidence both saturate at 1.00.")
    add_bullet(doc, "Transition Regime (75 m to 150 m): ",
        "Chemical relaxation absorption accelerates path loss for higher frequencies. By 150 m, HIGH_FREQUENCY margin drops to "
        "-64.02 dB—just 0.98 dB above the -65.0 dB cutoff. BALANCED margin drops to -59.47 dB (+5.53 dB headroom). "
        "Viability Confidence for BALANCED degrades steadily from 0.96 at 100 m to 0.37 at 150 m, providing an early software "
        "telemetry warning that margin headroom is being depleted.")
    add_bullet(doc, "Far-Field Fallback Regime (155 m to 200 m): ",
        "At R = 155.1 m, HIGH_FREQUENCY fails viability (< -65 dB) and is eliminated. At R = 175 m, BALANCED clings to viability with "
        "only 1.53 dB of margin (-63.47 dB, Viability Confidence = 0.10). At R = 184.9 m, BALANCED margin crosses -65.0 dB (-67.28 dB at 200 m). "
        "The controller executes an autonomous fallback to LOW_FREQUENCY. Because LOW exhibits an attenuation of only 64.47 dB/km, "
        "its margin at 200 m is -58.91 dB—leaving +6.09 dB of positive headroom and resetting Viability Confidence to 0.41.")

    # --------------------------------------------------------------------------
    # SECTION 7: NOISE SENSITIVITY OUTPUTS
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 7: Noise Sensitivity Outputs")
    add_body(doc,
        "The Noise Sensitivity Experiment tests the digital twin's robustness under simulated acoustic interference at a fixed "
        "nominal range of R = 75.0 m. The ambient noise penalty parameter is swept across five levels from -20.0 dB (exceptionally quiet) "
        "to +20.0 dB (severe acoustic interference). Table 7.1 presents the resulting profile viability flags and controller selections."
    )

    noise_headers = ["Noise Penalty (dB)", "LOW Viable", "BAL Viable", "HIGH Viable", "Selected Profile", "Selection Rationale"]
    noise_data = [
        ["-20.0 dB", "True (-22.34 dB)", "True (-25.47 dB)", "True (-27.75 dB)", "BALANCED", "Quiet medium: all viable; BALANCED selected for resolution"],
        ["-10.0 dB", "True (-32.34 dB)", "True (-35.47 dB)", "True (-37.75 dB)", "BALANCED", "Low noise: all viable; BALANCED selected for resolution"],
        ["0.0 dB", "True (-42.34 dB)", "True (-45.47 dB)", "True (-47.75 dB)", "BALANCED", "Nominal baseline: all viable; BALANCED selected"],
        ["+10.0 dB", "True (-52.34 dB)", "True (-55.47 dB)", "True (-57.75 dB)", "BALANCED", "Elevated noise: all remain viable (> -65 dB); BALANCED holds"],
        ["+20.0 dB", "True (-62.34 dB)", "False (-65.47 dB)", "False (-67.75 dB)", "LOW_FREQUENCY", "Severe noise: BAL and HIGH fail; LOW fallback chosen"],
    ]
    col_widths = [Inches(1.4), Inches(1.3), Inches(1.3), Inches(1.3), Inches(1.5), Inches(2.2)]
    add_styled_table(doc, noise_headers, noise_data, col_widths=col_widths)

    add_h2(doc, "7.1 Physical vs Simulation Noise Distinctions")
    add_callout(doc,
        tag="WARNING",
        title="Simulation Noise Penalty vs Physical Sonar Equation",
        body="The noise parameter swept in Table 7.1 is a NORMALIZED RELATIVE SIMULATION PENALTY (in dB) added to path loss, "
             "not a calibrated hydrophone acoustic noise spectrum level (NL in dB re 1 uPa^2/Hz). In a physical AUV sonar system, "
             "ambient noise is determined by sea state (Knudsen wind noise), thermal agitation, shipping traffic (Wenz curves), "
             "and vehicle self-noise (thrusters, motor bearings, flow boundary layer turbulence). Converting this model into a "
             "physically calibrated receiver would require specifying hydrophone Receive Voltage Sensitivity (RVS), pre-amplifier "
             "noise floor, receiver array Directivity Index (DI), and matched-filter processing gain 10*log10(B * T).",
        callout_type="WARNING"
    )

    # --------------------------------------------------------------------------
    # SECTION 8: ENVIRONMENTAL SWEEP OUTPUTS
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 8: Environmental Sweep Outputs")
    add_body(doc,
        "The Environmental Sweep Experiment isolates the individual oceanographic sensitivities of Temperature (-2 to 35°C), "
        "Salinity (0 to 40 PSU), and Hydrostatic Depth (0 to 500 m) on seawater sound speed (Mackenzie 1981) and high-frequency "
        "attenuation (Ainslie-McColm 1998). Table 8.1 quantifies the absolute and percentage impacts across all sweeps."
    )

    env_headers = ["Parameter Swept", "Sweep Range", "Sound Speed Impact Delta c", "Attenuation Impact @ 425k", "Profile Ranking Altered?"]
    env_data = [
        ["Temperature (T)", "-2.0°C to +35.0°C", "1440.2 -> 1550.8 m/s (+110.6 m/s, +7.68%)", "190.4 -> 105.2 dB/km (-85.2 dB/km, -44.7%)", "NO (Zero rank inversions)"],
        ["Salinity (S)", "0.0 to 40.0 PSU", "1475.4 -> 1527.1 m/s (+51.7 m/s, +3.50%)", "118.1 -> 138.4 dB/km (+20.3 dB/km, +17.2%)", "NO (Zero rank inversions)"],
        ["Depth (D)", "0.0 to 500.0 m", "1520.1 -> 1528.3 m/s (+8.2 m/s, +0.54%)", "136.8 -> 135.4 dB/km (-1.4 dB/km, -1.02%)", "NO (Zero rank inversions)"],
    ]
    add_styled_table(doc, env_headers, env_data, col_widths=[Inches(1.5), Inches(1.5), Inches(2.2), Inches(2.2), Inches(1.6)])

    add_h2(doc, "8.1 Hierarchy of Physical Drivers")
    add_body(doc,
        "Synthesizing the experimental data yields an unambiguous hierarchy of physical drivers in the AUV sonar digital twin:"
    )
    add_bullet(doc, "First-Order Determinants (Target Range R & Carrier Frequency f): ",
        "Path loss scales logarithmically with R and absorption scales quadratically with f. Together, R and f dictate over 90% "
        "of propagation margin variance. At 200 m, frequency selection creates a 14.44 dB performance gap between profiles.")
    add_bullet(doc, "Second-Order Modulator (Temperature T): ",
        "Water temperature alters sound speed by up to 7.7% and absorption by 44.7%. Warmer waters extend high-frequency viability "
        "by ~15 to 20 meters, while freezing Arctic waters contract viable range. However, temperature NEVER alters the relative ordering "
        "of the profiles: alpha_LOW < alpha_BAL < alpha_HIGH holds unconditionally across all temperatures.")
    add_bullet(doc, "Third-Order Modulator (Salinity S): ",
        "Freshwater (0 PSU) reduces MgSO4 absorption, slightly improving propagation margin compared to saline open ocean (35 PSU).")
    add_bullet(doc, "Negligible Factor (Hydrostatic Depth D < 500 m): ",
        "Depth influences sound speed by less than 0.54% and absorption by less than 1.1% over typical AUV diving depths.")

    # --------------------------------------------------------------------------
    # SECTION 9: SIGNAL GENERATION OUTPUTS
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 9: Signal Generation Outputs")
    add_body(doc,
        "The digital signal synthesis engine (`src/waveform.py` and `matlab/generate_lfm_chirp.m`) executes continuous-phase "
        "Linear Frequency Modulated chirp generation tailored for high-speed Direct Memory Access (DMA) streaming into a 12-bit DAC. "
        "Table 9.1 documents the exact mathematical parameters locked into the signal pipeline."
    )

    sig_headers = ["Parameter Name", "LOW_FREQUENCY", "BALANCED", "HIGH_FREQUENCY", "Units / Specification"]
    sig_data = [
        ["Start Frequency (f_start)", "100,000.0", "200,000.0", "350,000.0", "Hz (Locked band floor)"],
        ["End Frequency (f_end)", "220,000.0", "400,000.0", "500,000.0", "Hz (Locked band ceiling)"],
        ["Center Frequency (f_center)", "160,000.0", "300,000.0", "425,000.0", "Hz (Mid-band center)"],
        ["Chirp Bandwidth (B)", "120,000.0", "200,000.0", "150,000.0", "Hz (Sweep width)"],
        ["Pulse Duration (Tp)", "2.000", "2.000", "2.000", "ms (Nominal pulse length)"],
        ["Sample Rate (Fs)", "4,000,000", "4,000,000", "4,000,000", "Samples / second (4.0 MSPS)"],
        ["Sample Count (Np)", "8,000", "8,000", "8,000", "Samples (Fs * Tp)"],
        ["Chirp Rate (k)", "+60.00", "+100.00", "+75.00", "MHz / s (Slope = B / Tp)"],
        ["Window Function", "Hann", "Hann", "Hann", "0.5*(1 - cos(2*pi*n/(N-1)))"],
        ["In-Band Energy Pct", "100.0000%", "100.0000%", "100.0000%", "FFT spectral concentration"],
        ["Spectrogram Linearity R^2", "0.9901", "0.9901", "0.9901", "Linear ridge regression"],
    ]
    col_widths = [Inches(1.8), Inches(1.3), Inches(1.3), Inches(1.3), Inches(1.8)]
    add_styled_table(doc, sig_headers, sig_data, col_widths=col_widths)

    add_h2(doc, "9.1 Mapping from Synthesized Waveform to Physical Transmitter Chain")
    add_body(doc,
        "The digital twin outputs represent discrete digital codes destined for a physical hardware transmitter chain. "
        "Figure 9.1 illustrates the signal flow from digital twin LUT generation through physical acoustic radiation:"
    )

    flow_diagram = (
        "+-------------------------------------------------------------------------+\n"
        "|                     DIGITAL TWIN SIMULATION SCOPE                       |\n"
        "|  +---------------------+      +------------------+      +-------------+ |\n"
        "|  | Continuous LFM Math | ---> | Hann Windowing   | ---> | 12-Bit DAC  | |\n"
        "|  | phi(t) = 2*pi*f*t   |      | Edge Suppression |      | Quantizer   | |\n"
        "|  +---------------------+      +------------------+      +-------------+ |\n"
        "+----------------------------------------------------------------|--------+\n"
        "                                                                 v\n"
        "+-------------------------------------------------------------------------+\n"
        "|                     PHYSICAL HARDWARE TRANSMITTER CHAIN                 |\n"
        "|  +------------------+      +------------------+      +----------------+ |\n"
        "|  | STM32G4 Timer    | ---> | DMA Half-Word    | ---> | High-Speed DAC | |\n"
        "|  | Trigger (TRGO)   |      | Circular Stream  |      | Core (4 MSPS)  |\n"
        "|  +------------------+      +------------------+      +----------------+ |\n"
        "|                                                               |         |\n"
        "|                                                               v         |\n"
        "|  +------------------+      +------------------+      +----------------+ |\n"
        "|  | PZT Transducer   | <--- | LC Impedance     | <--- | Class-D / AB   | |\n"
        "|  | Acoustic Pulse   |      | Matching Network |      | Power Amp (5W) | |\n"
        "|  +------------------+      +------------------+      +----------------+ |\n"
        "+-------------------------------------------------------------------------+"
    )
    helpers['add_ascii_diagram'](doc, flow_diagram)

    # --------------------------------------------------------------------------
    # SECTION 10: DAC QUANTIZATION OUTPUTS
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 10: DAC Quantization Outputs")
    add_body(doc,
        "The quantization pipeline translates continuous floating-point signals into unsigned 12-bit integers formatted "
        "for the internal high-speed DAC of the STM32G474 microcontroller. Table 10.1 summarizes the numerical metrics."
    )

    dac_headers = ["Metric / Parameter", "Measured Simulation Value", "Theoretical Limit", "Compliance Status"]
    dac_data = [
        ["DAC Resolution", "12 bits", "12 bits", "Exact Match"],
        ["Digital Code Range", "0 to 4095 (Unsigned uint16)", "0 to 4095", "Verified: Zero clipping"],
        ["Midscale Zero-Signal Code", "2048", "2048 (V_dd / 2)", "Exact Match (1.6500 V on 3.3V)"],
        ["Full-Scale Voltage Range", "0.000 V to 3.300 V", "0.000 V to 3.300 V", "Verified rail-to-rail"],
        ["Quantization Step (1 LSB)", "0.80586 mV (3.3V / 4095)", "0.80586 mV", "Exact Match"],
        ["Max Quantization Error", "0.5000 LSB (0.4029 mV)", "+/-0.5000 LSB", "Verified Bounded"],
        ["Mean Quantization Error", "-0.00012 LSB (-0.096 uV)", "0.0000 LSB", "Zero DC Bias (< 0.001 LSB)"],
        ["Simulated SQNR (Muddy/LOW)", "69.67 dB", "74.0 dB (Unwindowed sine)", "Verified High-Fidelity"],
        ["Simulated SQNR (Balanced)", "69.67 dB", "74.0 dB (Unwindowed sine)", "Verified High-Fidelity"],
        ["Simulated SQNR (Clear/HIGH)", "69.70 dB", "74.0 dB (Unwindowed sine)", "Verified High-Fidelity"],
    ]
    col_widths = [Inches(2.2), Inches(2.0), Inches(2.0), Inches(1.8)]
    add_styled_table(doc, dac_headers, dac_data, col_widths=col_widths)

    add_body(doc,
        "Digital Simulation vs. Physical Analog Reality: In the digital simulation, the quantization error is purely "
        "algorithmic, reflecting round-to-nearest mathematical operations. Physical hardware DACs, however, suffer from analog non-idealities: "
        "Integral Non-Linearity (INL typically +/-2 LSB on STM32G4), Differential Non-Linearity (DNL typically +/-1 LSB), "
        "finite output amplifier slew rate, thermal Johnson noise, and sampling clock aperture jitter. While the simulated SQNR "
        "is 69.67 dB, a physical oscilloscope measurement of the DAC output pin will typically yield an effective number of bits (ENOB) "
        "of ~10.5 bits, corresponding to an analog Signal-to-Noise-and-Distortion ratio (SINAD) of ~65 dB."
    )

    # --------------------------------------------------------------------------
    # SECTION 11: MEMORY AND DMA OUTPUTS
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 11: Memory and DMA Outputs")
    add_body(doc,
        "To ensure seamless deployment to resource-constrained embedded microcontrollers, the digital twin explicitly models "
        "memory allocation for lookup table storage and active DMA streaming. Table 11.1 details the memory metrics against the "
        "STM32G474 target (128 KB SRAM, 512 KB Flash)."
    )

    mem_headers = ["Memory Element", "Muddy (LOW)", "Balanced", "Clear (HIGH)", "Total Flash (All 3)", "STM32 Capacity", "Resource Load"]
    mem_data = [
        ["Sample Count", "8,000 uint16", "8,000 uint16", "8,000 uint16", "24,000 uint16", "-", "-"],
        ["Bytes per Table", "16,000 bytes", "16,000 bytes", "16,000 bytes", "48,000 bytes", "-", "-"],
        ["KiB per Table", "15.625 KiB", "15.625 KiB", "15.625 KiB", "46.875 KiB", "-", "-"],
        ["Active Ping SRAM", "16.0 KB", "16.0 KB", "16.0 KB", "16.0 KB (Single)", "128.0 KB SRAM", "12.5% of SRAM"],
        ["Stored Flash LUTs", "16.0 KB", "16.0 KB", "16.0 KB", "48.0 KB (All 3)", "512.0 KB Flash", "9.37% of Flash"],
    ]
    col_widths = [Inches(1.8), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.3), Inches(1.2), Inches(1.1)]
    add_styled_table(doc, mem_headers, mem_data, col_widths=col_widths)

    add_callout(doc,
        tag="NOTE",
        title="Waveform LUT Memory vs Total Firmware Footprint",
        body="The 16.0 KB SRAM footprint represents strictly the active DMA ping buffer. It does NOT represent total AUV firmware "
             "memory consumption. Production embedded firmware requires substantial additional SRAM for the FreeRTOS kernel stack, "
             "DMA descriptor rings, communication buffers (UART/SPI/CAN), sensor telemetry queues, navigation state vectors, and "
             "interrupt service routine (ISR) contexts. However, dedicating 12.5% of SRAM to active sonar transmission leaves over "
             "112 KB of SRAM free, confirming high feasibility for single-chip STM32 integration.",
        callout_type="NOTE"
    )

    # --------------------------------------------------------------------------
    # SECTION 12: CONTROLLER OUTPUTS
    # --------------------------------------------------------------------------
    add_h1(doc, "Section 12: Controller Outputs")
    add_body(doc,
        "The adaptive transmission controller (`src/adaptation.py` and `matlab/adaptive_controller.m`) implements three interlocking "
        "protection mechanisms to guarantee operational stability in the presence of sensor noise and dynamic ocean fluctuations:"
    )

    add_h2(doc, "12.1 Directional Schmitt-Trigger Hysteresis")
    add_body(doc,
        "To prevent chattering when environmental or range inputs hover near a profile transition boundary, the controller applies "
        "a 10% hysteresis deadband. For instance, when transitioning between BALANCED and HIGH_FREQUENCY under heuristic control, "
        "the upward transition requires an input exceeding 0.70, while the downward transition requires the input to fall below 0.60. "
        "Any sensor oscillation within the [0.60, 0.70] deadband is ignored, locking the controller to its prior state."
    )

    add_h2(doc, "12.2 Debounce Persistence Filter (N = 2)")
    add_body(doc,
        "Even with hysteresis, transient disturbances (such as an air bubble sweeping past an optical turbidity probe or an acoustic "
        "multipath spike) could trigger an undesirable waveform switch. The controller enforces an N = 2 consecutive ping debounce filter. "
        "When an input change requests a new candidate profile, the controller increments an internal persistence counter. "
        "Only if the candidate profile is confirmed across two consecutive evaluation cycles is the state transition authorized. "
        "An isolated single-ping spike is discarded, preserving transmission continuity."
    )

    add_h2(doc, "12.3 Atomic Ping-Boundary Latching (PRI = 20.0 ms)")
    add_body(doc,
        "A critical vulnerability in software-defined transmitters is asynchronous profile switching during an active acoustic pulse, "
        "which produces severe phase discontinuities, frequency jumps, and acoustic shockwaves that can destroy piezoceramic elements. "
        "The digital twin enforces strict atomic latching synchronized to the Pulse Repetition Interval (PRI = 20.0 ms, 50 Hz PRF). "
        "During the active 2.0 ms pulse transmission, the active profile pointer is completely immutable. Any confirmed profile "
        "transition is held in a 'pending' state and committed strictly at the start of the subsequent ping period. "
        "In STM32 firmware, this maps directly to updating the DMA base address register inside the DMA Transfer-Complete (TC) interrupt."
    )
