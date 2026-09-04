"""
results_sections_part2.py
Engineering Report Generator - Part 2: Section 5 (Complete Graph-by-Graph Analysis)
SIH Problem 26058: AUV Adaptive Sonar Digital Twin
Complete Results, Outputs and Engineering Interpretation Report
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


def build_section_5(doc, helpers):
    """SECTION 5 — COMPLETE GRAPH-BY-GRAPH ANALYSIS (14-Point Structure per Figure)."""
    add_h1, add_h2, add_h3 = helpers['add_h1'], helpers['add_h2'], helpers['add_h3']
    add_body, add_bullet = helpers['add_body'], helpers['add_bullet']
    add_callout, add_equation_box = helpers['add_callout'], helpers['add_equation_box']
    add_figure = helpers['add_figure']

    add_h1(doc, "Section 5: Complete Graph-by-Graph Analysis")
    add_body(doc,
        "This section delivers an exhaustive, graph-by-graph engineering interpretation of all visual outputs produced "
        "by the digital twin experiments. In strict compliance with engineering reporting standards, no graph is presented "
        "without full analytical deconstruction. Every figure is evaluated against the 14 mandatory analytical dimensions: "
        "identifying the plotted entities, axis metrics, curve behaviors, discrete markers, shaded bounds, decision thresholds, "
        "extracted numerical values, underlying physical laws, governing equations, operational impacts, assumptions, and "
        "epistemic validation status."
    )

    # --------------------------------------------------------------------------
    # FIGURE 1
    # --------------------------------------------------------------------------
    add_h2(doc, "5.1 Figure 1: Frequency-Dependent Seawater Attenuation & Profile Sampling")
    add_figure(doc,
        img_filename="exp01_attenuation_vs_frequency.png",
        fig_num=1,
        title="Frequency-Dependent Seawater Attenuation across Chirp Sweep Bands",
        description="Continuous absorption curves modeled via Ainslie & McColm (1998) across 80 to 520 kHz under baseline clear seawater and unvalidated turbidity heuristics, showing 5-point discrete sampling for LOW, BALANCED, and HIGH profiles.",
        width_in=6.0,
        subfolder="matlab"
    )

    add_h3(doc, "1. What is being plotted?")
    add_body(doc,
        "Figure 1 plots the medium acoustic absorption coefficient alpha (dB/km) as a continuous function of acoustic "
        "carrier frequency from 80.0 kHz to 520.0 kHz under baseline clear seawater conditions (T=20°C, S=35 PSU, D=50 m, pH=8.0). "
        "Superimposed on the baseline curve are two unvalidated turbidity heuristic curves (moderate and high turbidity) "
        "and discrete scatter markers denoting the 5 evaluation frequency points for each of the three transmission profiles."
    )

    add_h3(doc, "2. X-axis explanation")
    add_body(doc, "X-axis: Acoustic Frequency in kilohertz (kHz), spanning linearly from 80.0 kHz to 520.0 kHz. Represents the frequency spectrum encompassing all three transmission chirp bands.")

    add_h3(doc, "3. Y-axis explanation")
    add_body(doc, "Y-axis: Acoustic Attenuation Coefficient alpha in decibels per kilometer (dB/km). Represents the rate of exponential medium energy dissipation per kilometer of acoustic path length.")

    add_h3(doc, "4. Explanation of every curve")
    add_bullet(doc, "Solid Black Curve (Clear Seawater Baseline): ", "Represents pure chemical relaxation and viscous absorption computed via Ainslie & McColm (1998) for standard oceanographic baseline parameters (T=20°C, S=35 PSU, D=50 m). Attenuation increases monotonically from ~29 dB/km at 80 kHz to ~163 dB/km at 520 kHz.")
    add_bullet(doc, "Dashed Black Curve (Moderate Turbidity Heuristic): ", "Represents baseline absorption plus an unvalidated sensitivity heuristic for moderate suspended particulate matter (turbidity = 30 NTU proxy), adding frequency-squared particulate scattering loss.")
    add_bullet(doc, "Dotted Black Curve (High Turbidity Heuristic): ", "Represents severe suspended sediment scattering (turbidity = 80 NTU proxy), demonstrating extreme dissipation at high frequencies.")

    add_h3(doc, "5. Explanation of markers")
    add_bullet(doc, "Orange Circular Markers (LOW_FREQUENCY 5-Point): ", "Samples at 100.0, 130.0, 160.0, 190.0, and 220.0 kHz, exhibiting attenuation values of 38.85, 53.58, 66.31, 77.13, and 86.47 dB/km.")
    add_bullet(doc, "Blue Circular Markers (BALANCED 5-Point): ", "Samples at 200.0, 250.0, 300.0, 350.0, and 400.0 kHz, exhibiting attenuation values of 80.39, 94.75, 107.18, 118.83, and 130.43 dB/km.")
    add_bullet(doc, "Green Circular Markers (HIGH_FREQUENCY 5-Point): ", "Samples at 350.0, 387.5, 425.0, 462.5, and 500.0 kHz, exhibiting attenuation values of 118.83, 127.51, 136.35, 145.49, and 155.01 dB/km.")

    add_h3(doc, "6. Explanation of shaded regions")
    add_body(doc,
        "Three light translucent vertical spans demarcate the active frequency bandwidth of each profile: Orange span covers "
        "100 to 220 kHz (LOW_FREQUENCY); Blue span covers 200 to 400 kHz (BALANCED); Green span covers 350 to 500 kHz (HIGH_FREQUENCY). "
        "Notice the spectral overlap between profiles (e.g., 200-220 kHz shared between LOW and BALANCED; 350-400 kHz shared between BALANCED and HIGH)."
    )

    add_h3(doc, "7. Explanation of thresholds")
    add_body(doc, "No decision thresholds are plotted in Figure 1; this figure establishes the underlying medium loss characteristics.")

    add_h3(doc, "8. Important numerical observations")
    add_bullet(doc, "Intra-band slope variation: ", "Within LOW_FREQUENCY, attenuation increases from 38.85 dB/km to 86.47 dB/km—a 122% increase across the band. Within BALANCED, attenuation increases from 80.39 to 130.43 dB/km (62% increase).")
    add_bullet(doc, "Mean band attenuation ordering: ", "LOW_FREQUENCY mean alpha = 64.47 dB/km; BALANCED mean alpha = 106.32 dB/km; HIGH_FREQUENCY mean alpha = 136.64 dB/km. HIGH experiences more than double the dissipation of LOW.")

    add_h3(doc, "9. Why the trend occurs")
    add_body(doc,
        "Acoustic dissipation in seawater is driven by three distinct physical mechanisms: Boric acid chemical relaxation "
        "(dominating f < 1 kHz), Magnesium sulfate (MgSO4) chemical relaxation (dominating from 10 kHz to ~100 kHz), and pure water "
        "shear and bulk viscosity (dominating f > 100 kHz). In the 100 to 500 kHz ultrasonic regime of our sonar, viscous dissipation "
        "scales quadratically with acoustic frequency (alpha proportional to f^2). Consequently, high-frequency acoustic waves suffer "
        "rapid molecular shear dissipation as water molecules fail to equilibrate instantaneously during rapid pressure oscillations."
    )

    add_h3(doc, "10. Underlying equation or model")
    add_body(doc, "Ainslie & McColm (1998) simplified ocean acoustic absorption model:")
    add_equation_box(doc,
        "alpha = [A1*f1*f^2 / (f1^2 + f^2)] + [A2*f2*f^2 / (f2^2 + f^2)] + A3*f^2",
        "Ainslie-McColm equation where f1, f2 are relaxation frequencies and A1, A2, A3 are temperature/salinity/depth coefficients"
    )

    add_h3(doc, "11. Engineering interpretation")
    add_body(doc,
        "A single monochromatic center-frequency assumption is inadequate for broadband chirps. A chirp sweeping from 200 to 400 kHz "
        "experiences vastly different attenuation at its leading edge (80 dB/km) than at its trailing edge (130 dB/km). "
        "The five-point sampling scheme accurately captures intra-band spectral tilt, ensuring that transmission loss and margin "
        "reflect integrated energy dissipation across the full waveform envelope."
    )

    add_h3(doc, "12. Impact on profile selection")
    add_body(doc,
        "The steep attenuation gradient dictates that HIGH_FREQUENCY and BALANCED rapidly bleed signal energy over distance. "
        "At ranges beyond 150 m, HIGH_FREQUENCY's high alpha accelerates transmission loss past the viability limit, forcing the system "
        "to drop back to lower-attenuation profiles."
    )

    add_h3(doc, "13. Limitations of this result")
    add_body(doc,
        "Ainslie-McColm models open ocean seawater under standard chemical relaxation. It assumes homogeneous water column properties "
        "without thermocline refraction, salinity layering, or bubble plumes. Furthermore, the turbidity curves shown are "
        "UNVALIDATED SIMULATION HEURISTICS (based on Rayleigh/Mie scattering approximations) and must not be interpreted as certified tank measurements."
    )

    add_h3(doc, "14. Engineering status")
    add_body(doc, "[SIMULATION MODEL] (Ainslie-McColm 1998 baseline); [UNVALIDATED SIMULATION HEURISTIC] (Turbidity modifications).")

    # --------------------------------------------------------------------------
    # FIGURE 2
    # --------------------------------------------------------------------------
    add_h2(doc, "5.2 Figure 2: Modeled One-Way Propagation Margin vs Target Range")
    add_figure(doc,
        img_filename="exp02_propagation_vs_range.png",
        fig_num=2,
        title="Modeled Relative Propagation Margin vs Range across Profiles",
        description="One-way transmission loss and relative propagation margin evaluated from 5 m to 200 m, displaying spherical spreading convergence at near-range, absorption-driven divergence at far-range, and crossings of the -65.0 dB viability threshold.",
        width_in=6.0,
        subfolder="matlab"
    )

    add_h3(doc, "1. What is being plotted?")
    add_body(doc,
        "Figure 2 plots the modeled relative propagation margin (dB) as a function of target distance from R = 5.0 m to R = 200.0 m "
        "for LOW_FREQUENCY, BALANCED, and HIGH_FREQUENCY profiles under baseline seawater conditions. It displays the operational "
        "viability limit at -65.0 dB relative margin."
    )

    add_h3(doc, "2. X-axis explanation")
    add_body(doc, "X-axis: Target Range R in meters (m), sampled continuously across 80 evaluation points from 5.0 m to 200.0 m.")

    add_h3(doc, "3. Y-axis explanation")
    add_body(doc, "Y-axis: Relative Propagation Margin in decibels (dB), referenced to a 0 dB transmit level. More negative values indicate greater cumulative transmission path loss.")

    add_h3(doc, "4. Explanation of every curve")
    add_bullet(doc, "Orange Curve (LOW_FREQUENCY): ", "Exhibits the flattest slope at long range. Drops from -20.64 dB at 10 m to -58.91 dB at 200 m. Remains comfortably above the -65 dB viability floor across the entire 200 m sweep.")
    add_bullet(doc, "Blue Curve (BALANCED): ", "Exhibits intermediate slope. Drops from -21.06 dB at 10 m to -63.47 dB at 175 m, crossing the -65.0 dB viability threshold at R = 184.9 m, reaching -67.28 dB at 200 m.")
    add_bullet(doc, "Green Curve (HIGH_FREQUENCY): ", "Exhibits the steepest decay. Drops from -21.37 dB at 10 m to -64.02 dB at 150 m, crossing the -65.0 dB threshold at R = 155.1 m, reaching -73.35 dB at 200 m.")

    add_h3(doc, "5. Explanation of markers")
    add_body(doc, "Continuous smooth trajectory lines are plotted without discrete point markers.")

    add_h3(doc, "6. Explanation of shaded regions")
    add_body(doc, "No shaded bands; clean line comparison.")

    add_h3(doc, "7. Explanation of thresholds")
    add_bullet(doc, "Red Dashed Horizontal Line at -65.0 dB: ", "Represents the simulation policy viability floor. Waveforms whose relative propagation margin falls below this line are deemed non-viable and excluded from Tier 2 selection.")

    add_h3(doc, "8. Important numerical observations")
    add_bullet(doc, "Short-Range Convergence (< 30 m): ", "At R = 10 m, all three profiles are clustered tightly within 0.73 dB of each other (-20.64 dB for LOW vs -21.37 dB for HIGH). Spreading loss dominates completely.")
    add_bullet(doc, "Long-Range Divergence (200 m): ", "At R = 200 m, LOW (-58.91 dB) leads HIGH (-73.35 dB) by a massive 14.44 dB separation. Absorption loss has completely taken over.")
    add_bullet(doc, "Viability Boundary Crossings: ", "HIGH_FREQUENCY crosses -65.0 dB at R = 155.1 m. BALANCED crosses -65.0 dB at R = 184.9 m. LOW_FREQUENCY remains viable past 200 m.")

    add_h3(doc, "9. Why the trend occurs")
    add_body(doc,
        "Transmission loss is the sum of two terms: geometric spherical spreading (20*log10(R)) and absorption (alpha*R/1000). "
        "At short range (R < 30 m), 20*log10(R) changes rapidly with distance (growing by ~26 dB from 1 m to 20 m), while alpha*R is tiny "
        "(only ~2.7 dB for HIGH at 20 m). Because geometric spreading is frequency-independent, all curves lie close together. "
        "At longer range, logarithmic spreading slows down (adding only ~6 dB from 100 m to 200 m), while linear absorption alpha*R grows "
        "relentlessly (adding 13.7 dB for HIGH from 100 to 200 m, but only 6.4 dB for LOW). This causes the curves to diverge dramatically."
    )

    add_h3(doc, "10. Underlying equation or model")
    add_equation_box(doc,
        "TL(R) = 20 * log10(R) + alpha_band * (R / 1000);   Margin_rel = -TL(R) - Noise_penalty",
        "One-way spherical spreading plus linear absorption path loss equation"
    )

    add_h3(doc, "11. Engineering interpretation")
    add_body(doc,
        "The digital twin reveals that acoustic frequency selection is unconstrained by propagation loss at close ranges (< 50 m), "
        "meaning mission utility (resolution or directivity) can be pursued without penalty. Conversely, at far ranges (> 150 m), "
        "propagation physics strictly dictates waveform choice, rendering high frequencies unusable."
    )

    add_h3(doc, "12. Impact on profile selection")
    add_body(doc,
        "Establishes the natural physical viability cutoff boundaries for the controller: HIGH is viable up to 155 m; "
        "BALANCED is viable up to 184 m; LOW remains viable across the entire operational envelope."
    )

    add_h3(doc, "13. Limitations of this result")
    add_body(doc,
        "The -65.0 dB threshold is an assumed simulation control policy, not an empirical receiver sensitivity threshold. "
        "Furthermore, this model computes one-way transmission loss, not the two-way radar/sonar equation with target backscattering "
        "cross-section (Target Strength, TS). Actual two-way detection ranges would be substantially shorter."
    )

    add_h3(doc, "14. Engineering status")
    add_body(doc, "[SIMULATION MODEL] (Transmission loss); [SIMULATION ASSUMPTION] (-65.0 dB threshold).")

    # --------------------------------------------------------------------------
    # FIGURE 3
    # --------------------------------------------------------------------------
    add_h2(doc, "5.3 Figure 3: Theoretical Bandwidth-Based Range Resolution")
    add_figure(doc,
        img_filename="exp03_theoretical_range_resolution.png",
        fig_num=3,
        title="Theoretical Matched-Filter Range Resolution Comparison",
        description="Bar chart displaying theoretical spatial range resolution limits Delta R = c / (2B) across the three profiles, highlighting the superior 3.75 mm resolution of BALANCED due to its 200 kHz bandwidth.",
        width_in=5.6,
        subfolder="matlab"
    )

    add_h3(doc, "1. What is being plotted?")
    add_body(doc, "Figure 3 plots the ideal theoretical matched-filter range resolution Delta R (in millimeters) for LOW_FREQUENCY, BALANCED, and HIGH_FREQUENCY profiles calculated at nominal sound speed c = 1500 m/s.")

    add_h3(doc, "2. X-axis explanation")
    add_body(doc, "X-axis: Profile categories with corresponding sweep bandwidths: LOW_FREQUENCY (B = 120 kHz), BALANCED (B = 200 kHz), and HIGH_FREQUENCY (B = 150 kHz).")

    add_h3(doc, "3. Y-axis explanation")
    add_body(doc, "Y-axis: Theoretical Range Resolution Delta R in millimeters (mm), bounded from 0 to 8 mm. Lower values indicate finer resolution.")

    add_h3(doc, "4. Explanation of every curve")
    add_body(doc, "Discrete bar chart comparison; no continuous curves.")

    add_h3(doc, "5. Explanation of markers")
    add_body(doc, "Bold numerical text callouts atop each bar report exact calculated millimeters: 6.25 mm (LOW), 3.75 mm (BALANCED), and 5.00 mm (HIGH).")

    add_h3(doc, "6. Explanation of shaded regions")
    add_body(doc, "Bars are color-coded in profile brand colors: Orange (LOW), Blue (BALANCED), and Green (HIGH).")

    add_h3(doc, "7. Explanation of thresholds")
    add_body(doc, "No thresholds applied; absolute analytical comparison.")

    add_h3(doc, "8. Important numerical observations")
    add_bullet(doc, "BALANCED Achieves Finest Resolution: ", "Delta R = 3.75 mm (or 3.80 mm at c = 1520.91 m/s), outperforming HIGH_FREQUENCY (5.00 mm) by 25% and LOW_FREQUENCY (6.25 mm) by 40%.")
    add_bullet(doc, "Common Engineering Misconception Refuted: ", "HIGH_FREQUENCY does NOT provide the finest range resolution despite having a higher center frequency (425 kHz vs 300 kHz). Bandwidth B governs range resolution, not carrier frequency fc.")

    add_h3(doc, "9. Why the trend occurs")
    add_body(doc,
        "In matched-filter radar and sonar signal processing, the width of the mainlobe of the auto-correlation function (compressed pulse width) "
        "is inversely proportional to the swept signal bandwidth: tau_compressed = 1 / B. Multiplying by two-way acoustic propagation speed "
        "yields Delta R = c / (2B). Because BALANCED sweeps across 200 kHz (200 to 400 kHz), its auto-correlation mainlobe is narrower "
        "than HIGH_FREQUENCY (150 kHz sweep) or LOW_FREQUENCY (120 kHz sweep)."
    )

    add_h3(doc, "10. Underlying equation or model")
    add_equation_box(doc,
        "Delta R = c / (2 * B)",
        "Ideal matched-filter range resolution equation"
    )

    add_h3(doc, "11. Engineering interpretation")
    add_body(doc,
        "This result provides the definitive engineering justification for Survey Mode. When the AUV's mission objective is acoustic imaging, "
        "seabed mapping, or small object discrimination, BALANCED is the mathematically optimal waveform to transmit, provided propagation "
        "margin allows."
    )

    add_h3(doc, "12. Impact on profile selection")
    add_body(doc, "Dictates that BALANCED is always the first-choice candidate in Survey Mode, being abandoned only when propagation margin falls below -65 dB.")

    add_h3(doc, "13. Limitations of this result")
    add_body(doc,
        "This calculation represents the theoretical limit of an unwindowed or lightly windowed ideal matched filter in a dispersion-free medium. "
        "In physical hardware, Hann window tapering slightly broadens the auto-correlation mainlobe (by ~1.5x), analog receiver bandpass filtering "
        "introduces group delay dispersion, and target acoustic reverberation can degrade practical resolution."
    )

    add_h3(doc, "14. Engineering status")
    add_body(doc, "[ANALYTICAL RESULT] (Ideal pulse-compression equation).")

    # --------------------------------------------------------------------------
    # FIGURE 4
    # --------------------------------------------------------------------------
    add_h2(doc, "5.4 Figure 4: Relative Theoretical Directivity Comparison")
    add_figure(doc,
        img_filename="exp04_relative_directivity_comparison.png",
        fig_num=4,
        title="Relative Theoretical Directivity Factor across Profiles",
        description="Bar chart displaying the relative theoretical directivity factor Dir_rel = fc / 300 kHz under a fixed physical aperture assumption, demonstrating the 1.417x beam narrowing benefit of HIGH_FREQUENCY.",
        width_in=5.6,
        subfolder="matlab"
    )

    add_h3(doc, "1. What is being plotted?")
    add_body(doc, "Figure 4 plots the relative theoretical directivity factor Dir_rel for the three profiles, normalized to the BALANCED profile center frequency (300.0 kHz = 1.000x).")

    add_h3(doc, "2. X-axis explanation")
    add_body(doc, "X-axis: Profile categories with corresponding center frequencies: LOW_FREQUENCY (fc = 160 kHz), BALANCED (fc = 300 kHz), and HIGH_FREQUENCY (fc = 425 kHz).")

    add_h3(doc, "3. Y-axis explanation")
    add_body(doc, "Y-axis: Relative Directivity Factor (fc / 300 kHz), ranging from 0.0 to 1.8. Higher values denote theoretically narrower beamwidth.")

    add_h3(doc, "4. Explanation of every curve")
    add_body(doc, "Discrete bar chart comparison; no continuous curves.")

    add_h3(doc, "5. Explanation of markers")
    add_body(doc, "Bold numerical callouts atop each bar indicate: 0.533x (LOW), 1.000x (BALANCED), and 1.417x (HIGH).")

    add_h3(doc, "6. Explanation of shaded regions")
    add_body(doc, "Bars are color-coded in profile colors (Orange, Blue, Green).")

    add_h3(doc, "7. Explanation of thresholds")
    add_bullet(doc, "Gray Dashed Horizontal Line at 1.000x: ", "Denotes the nominal baseline reference directivity established by the BALANCED profile.")

    add_h3(doc, "8. Important numerical observations")
    add_bullet(doc, "HIGH_FREQUENCY Delivers Highest Directivity: ", "Directivity factor of 1.417x represents a 41.7% increase in theoretical directivity over BALANCED, and a 166% increase over LOW_FREQUENCY (0.533x).")
    add_bullet(doc, "LOW_FREQUENCY Beam Divergence: ", "LOW_FREQUENCY's 0.533x directivity indicates that its acoustic radiation pattern is approximately twice as broad as BALANCED.")

    add_h3(doc, "9. Why the trend occurs")
    add_body(doc,
        "For a circular acoustic piston of diameter D, the half-power (-3 dB) beamwidth theta is approximately given by theta approx 1.02 * c / (f * D) radians. "
        "Assuming a fixed physical transducer diameter D, higher acoustic frequencies produce a shorter acoustic wavelength lambda = c / f. "
        "More wavelengths fit across the physical face of the aperture, creating greater destructive interference off-axis and synthesizing "
        "a sharper, more directional forward radiation lobe."
    )

    add_h3(doc, "10. Underlying equation or model")
    add_equation_box(doc,
        "Dir_rel = f_center / (300.0 kHz)",
        "Relative theoretical directivity proxy under fixed aperture diameter assumption"
    )

    add_h3(doc, "11. Engineering interpretation")
    add_body(doc,
        "Provides the physical justification for Directivity Mode. When an AUV needs to localize a target in azimuth/elevation, avoid surface "
        "or seabed reverberation clutter, or track a specific acoustic beacon, HIGH_FREQUENCY is the preferred waveform because its tighter "
        "beam pattern concentrates energy along the acoustic axis and rejects multipath clutter."
    )

    add_h3(doc, "12. Impact on profile selection")
    add_body(doc, "Dictates that HIGH_FREQUENCY is the primary winner in Directivity Mode whenever its propagation margin is viable (R < 155 m).")

    add_h3(doc, "13. Limitations of this result")
    add_body(doc,
        "This is an analytical frequency proxy. It does NOT model actual piezoelectric ceramic element geometry, backing layer acoustic damping, "
        "sidelobe levels, beam steering phase delays, or non-linear acoustic distortion."
    )

    add_h3(doc, "14. Engineering status")
    add_body(doc, "[ANALYTICAL THEORETICAL PROXY] (Frequency proxy under fixed aperture assumption).")

    # --------------------------------------------------------------------------
    # FIGURE 5
    # --------------------------------------------------------------------------
    add_h2(doc, "5.5 Figure 5: Profile Selection vs Range under Mission Objectives")
    add_figure(doc,
        img_filename="exp05_profile_winner_vs_range.png",
        fig_num=5,
        title="Profile Selection vs Range under SURVEY and DIRECTIVITY Objectives",
        description="Two-panel stepped switching timeline demonstrating candidate profile selection across 10 to 200 m: Survey Mode selects BALANCED with fallback to LOW; Directivity Mode selects HIGH, falls back to BALANCED, then falls back to LOW.",
        width_in=6.0,
        subfolder="matlab"
    )

    add_h3(doc, "1. What is being plotted?")
    add_body(doc,
        "Figure 5 displays the winning candidate profile selected by the Tier 2 mission utility logic as target distance increases "
        "from 10 m to 200 m. Subplot 5a displays Survey Mode (resolution priority); Subplot 5b displays Directivity Mode (beam sharpness priority)."
    )

    add_h3(doc, "2. X-axis explanation")
    add_body(doc, "X-axis: Target Range R in meters (m), spanning from 10.0 m to 200.0 m across 100 evaluation steps.")

    add_h3(doc, "3. Y-axis explanation")
    add_body(doc, "Y-axis: Discrete Profile ID: 1 = LOW_FREQUENCY, 2 = BALANCED, 3 = HIGH_FREQUENCY.")

    add_h3(doc, "4. Explanation of every curve")
    add_bullet(doc, "Blue Stepped Line (Subplot 5a - Survey Mode): ", "Remains locked on BALANCED (ID: 2) from 10.0 m up to 184.9 m. At R = 184.9 m, BALANCED fails viability, causing an instantaneous step switch to LOW_FREQUENCY (ID: 1), where it remains through 200 m.")
    add_bullet(doc, "Green Stepped Line (Subplot 5b - Directivity Mode): ", "Starts locked on HIGH_FREQUENCY (ID: 3) from 10.0 m to 155.1 m. At R = 155.1 m, HIGH fails viability, causing a step down to BALANCED (ID: 2). At R = 184.9 m, BALANCED also fails viability, causing a final step down to LOW_FREQUENCY (ID: 1).")

    add_h3(doc, "5. Explanation of markers")
    add_body(doc, "Stepped transitions (post-step) denote discrete switching boundaries.")

    add_h3(doc, "6. Explanation of shaded regions")
    add_body(doc, "Subplots are color-coded in Blue (Survey) and Green (Directivity).")

    add_h3(doc, "7. Explanation of thresholds")
    add_body(doc, "The discrete profile levels 1, 2, and 3 are marked on the Y-axis.")

    add_h3(doc, "8. Important numerical observations")
    add_bullet(doc, "Survey Mode Single Switching Boundary: ", "R_switch = 184.9 m (BALANCED -> LOW_FREQUENCY). Exactly corresponds to BALANCED relative margin crossing -65.0 dB.")
    add_bullet(doc, "Directivity Mode Dual Switching Boundaries: ", "R_switch_1 = 155.1 m (HIGH -> BALANCED, where HIGH margin crosses -65.0 dB); R_switch_2 = 184.9 m (BALANCED -> LOW, where BALANCED crosses -65.0 dB).")

    add_h3(doc, "9. Why the trend occurs")
    add_body(doc,
        "The controller executes the two-tier selection algorithm. In Survey Mode, BALANCED has the highest mission utility (U = 200k / 200k = 1.00) "
        "due to bandwidth. As long as BALANCED is viable (relative_margin >= -65 dB), it is chosen. Only when BALANCED exceeds the viability threshold "
        "does the system fall back to LOW_FREQUENCY. In Directivity Mode, HIGH has the highest utility (U = 425k / 425k = 1.00) due to center frequency. "
        "It is selected until 155.1 m. When HIGH fails, BALANCED is the highest-utility viable survivor (U = 300k / 425k = 0.706). When BALANCED also fails "
        "at 184.9 m, LOW_FREQUENCY is the sole viable survivor."
    )

    add_h3(doc, "10. Underlying equation or model")
    add_body(doc, "Decoupled Two-Tier Decision Architecture:")
    add_equation_box(doc,
        "Tier 1: Viable_Profiles = {P_i | Margin_rel(P_i) >= -65.0 dB}\nTier 2: Winner = argmax_{P_i in Viable_Profiles} [Utility_Mode(P_i)]",
        "Two-tier selection algorithm logic"
    )

    add_h3(doc, "11. Engineering interpretation")
    add_body(doc,
        "Demonstrates complete operational transparency. Unlike black-box heuristic weighted scores, every state transition in Figure 5 "
        "is deterministically traceable to a specific physical propagation boundary and an explicit operational objective."
    )

    add_h3(doc, "12. Impact on profile selection")
    add_body(doc, "Validates the core control policy of the software twin across ranges 10 to 200 m.")

    add_h3(doc, "13. Limitations of this result")
    add_body(doc, "Plots instantaneous candidate decisions. In firmware, these candidates must pass through hysteresis deadbands and N=2 debounce persistence before latching to active transmission.")

    add_h3(doc, "14. Engineering status")
    add_body(doc, "[VERIFIED SIMULATION LOGIC] (Deterministic candidate decision algorithm).")

    # --------------------------------------------------------------------------
    # FIGURE 6
    # --------------------------------------------------------------------------
    add_h2(doc, "5.6 Figure 6: Performance Margin and Dual Confidence Metrics vs Range")
    add_figure(doc,
        img_filename="exp06_performance_margin_vs_range.png",
        fig_num=6,
        title="Candidate Viability Margin and Dual Confidence Metrics vs Range",
        description="Dual-axis plot showing candidate margin above viability (dB) alongside continuous viability_confidence and selection_confidence metrics across 5 to 200 m in Survey Mode.",
        width_in=6.0,
        subfolder="matlab"
    )

    add_h3(doc, "1. What is being plotted?")
    add_body(doc,
        "Figure 6 plots the candidate profile's margin above the viability floor (dB, left Y-axis) alongside the dual confidence metrics "
        "(right Y-axis): Viability Confidence (viability_confidence) and Selection Confidence (selection_confidence) as range increases from 5 to 200 m."
    )

    add_h3(doc, "2. X-axis explanation")
    add_body(doc, "X-axis: Target Range R in meters (m), evaluated continuously across 80 steps from 5.0 m to 200.0 m.")

    add_h3(doc, "3. Y-axis explanation")
    add_bullet(doc, "Left Y-Axis (Blue): ", "Viability Margin (dB), defined as relative_margin_db - (-65.0 dB). Represents decibels of headroom above the viability floor.")
    add_bullet(doc, "Right Y-Axis (Magenta / Cyan): ", "Confidence Metrics, dimensionless normalized scales from 0.0 to 1.0.")

    add_h3(doc, "4. Explanation of every curve")
    add_bullet(doc, "Solid Blue Curve (Margin Above Viability): ", "Starts at +44 dB at 10 m, declining steadily to +25.7 dB at 50 m, +14.37 dB at 100 m, and +5.53 dB at 150 m. At 184.9 m, it touches 0.0 dB as BALANCED fails. It then jumps upward to +7.73 dB as the controller falls back to LOW_FREQUENCY (which has a much lower attenuation), ending at +6.09 dB at 200 m.")
    add_bullet(doc, "Dash-Dotted Magenta Curve (viability_confidence): ", "Remains saturated at 1.00 from 5 m to 98 m (margin >= 15 dB). Between 100 m and 184.9 m, it declines linearly from 0.96 to 0.00 as headroom vanishes. At 185 m, fallback to LOW restores confidence to 0.52 (7.7 dB headroom), ending at 0.41 at 200 m.")
    add_bullet(doc, "Dashed Cyan Curve (selection_confidence): ", "Remains at 1.00 across the entire range. From 10 to 184 m, BALANCED's bandwidth utility (1.00) exceeds runner-up HIGH (150/200 = 0.75) by delta_U = 0.25 (delta_U / 0.25 = 1.00). Beyond 185 m, LOW_FREQUENCY is the uniquely viable profile, which by definition yields selection confidence = 1.00.")

    add_h3(doc, "5. Explanation of markers")
    add_body(doc, "Continuous trajectories without discrete markers.")

    add_h3(doc, "6. Explanation of shaded regions")
    add_body(doc, "No shaded regions; dual-axis overlay.")

    add_h3(doc, "7. Explanation of thresholds")
    add_bullet(doc, "Red Dashed Line at 0.0 dB: ", "Viability boundary where profile margin equals the -65 dB floor.")
    add_bullet(doc, "Green Dotted Line at +15.0 dB: ", "Full confidence boundary; headroom above this level guarantees viability_confidence = 1.00.")

    add_h3(doc, "8. Important numerical observations")
    add_bullet(doc, "At R = 50 m: ", "Margin = +25.70 dB, viability_confidence = 1.00, selection_confidence = 1.00. Completely secure operation.")
    add_bullet(doc, "At R = 150 m: ", "Margin = +5.53 dB, viability_confidence = 0.37, selection_confidence = 1.00. Waveform is viable but operating with limited headroom.")
    add_bullet(doc, "At R = 185 m (Fallback Event): ", "BALANCED margin drops to -0.01 dB (non-viable). Switch to LOW instantly resets margin to +7.73 dB and viability_confidence to 0.52.")

    add_h3(doc, "9. Why the trend occurs")
    add_body(doc,
        "As transmission distance grows, path loss erodes margin headroom. Viability confidence scales linearly over the final 15 dB "
        "of margin clearance, providing an early warning signal before a profile fails. The saw-tooth discontinuity at 185 m is "
        "the hallmark of autonomous adaptation: when a high-resolution profile exhausts its physical margin, switching to a resilient "
        "fallback waveform restores positive acoustic headroom."
    )

    add_h3(doc, "10. Underlying equation or model")
    add_equation_box(doc,
        "C_v = clip((Margin_rel - (-65.0 dB)) / 15.0 dB, 0.0, 1.0)\nC_s = clip((Winner_Utility - SecondBest_Utility) / 0.25, 0.0, 1.0)",
        "Dual confidence metric equations"
    )

    add_h3(doc, "11. Engineering interpretation")
    add_body(doc,
        "Decouples propagation safety from mission decision clarity. An AUV may be completely certain about which profile to choose "
        "(selection_confidence = 1.0), yet fully aware that acoustic signal margin is dangerously thin (viability_confidence = 0.10). "
        "This dual-confidence model provides rich operational telemetry for vehicle mission management computers."
    )

    add_h3(doc, "12. Impact on profile selection")
    add_body(doc, "Provides the metric used by higher-level mission planners to assess acoustic telemetry health and schedule adaptive pings.")

    add_h3(doc, "13. Limitations of this result")
    add_body(doc, "The 15 dB confidence scaling span is a software design choice, chosen to provide smooth grading over typical AUV speed-over-ground distances.")

    add_h3(doc, "14. Engineering status")
    add_body(doc, "[SIMULATION POLICY METRIC] (Dual confidence normalization algorithm).")

    # --------------------------------------------------------------------------
    # FIGURE 7
    # --------------------------------------------------------------------------
    add_h2(doc, "5.7 Figure 7: Environmental Sensitivity Summary")
    add_figure(doc,
        img_filename="exp07_environmental_sensitivity_summary.png",
        fig_num=7,
        title="Environmental Sensitivity Analysis: Temperature, Salinity, and Depth",
        description="Three-panel sensitivity sweep evaluating sound speed c (Mackenzie 1981) and high-frequency attenuation alpha @ 425 kHz (Ainslie-McColm 1998) across Temperature (-2 to 35°C), Salinity (0 to 40 PSU), and Depth (0 to 500 m).",
        width_in=6.2,
        subfolder="matlab"
    )

    add_h3(doc, "1. What is being plotted?")
    add_body(doc,
        "Figure 7 plots the sensitivity of seawater sound speed c (m/s, blue curves, left axes) and acoustic attenuation alpha at 425 kHz "
        "(dB/km, red dashed curves, right axes) across three primary oceanographic parameters: Subplot 7a: Temperature (-2 to 35°C); "
        "Subplot 7b: Salinity (0 to 40 PSU); Subplot 7c: Depth (0 to 500 m)."
    )

    add_h3(doc, "2. X-axis explanation")
    add_bullet(doc, "Subplot 7a: ", "Seawater Temperature in degrees Celsius (°C), from -2.0°C to 35.0°C.")
    add_bullet(doc, "Subplot 7b: ", "Practical Salinity in Practical Salinity Units (PSU), from 0.0 (freshwater) to 40.0 PSU (hypersaline).")
    add_bullet(doc, "Subplot 7c: ", "Hydrostatic Depth in meters (m), from 0.0 m (surface) to 500.0 m.")

    add_h3(doc, "3. Y-axis explanation")
    add_bullet(doc, "Left Y-Axes (Blue): ", "Seawater Sound Speed c in meters per second (m/s), computed via Mackenzie (1981).")
    add_bullet(doc, "Right Y-Axes (Red): ", "Acoustic Attenuation alpha at 425 kHz in dB/km, computed via Ainslie & McColm (1998).")

    add_h3(doc, "4. Explanation of every curve")
    add_bullet(doc, "Temperature Sweep (7a): ", "Sound speed rises non-linearly from ~1440 m/s at -2°C to ~1550 m/s at 35°C (~110 m/s swing). Attenuation at 425 kHz drops from ~190 dB/km in freezing water to ~105 dB/km at 35°C.")
    add_bullet(doc, "Salinity Sweep (7b): ", "Sound speed increases linearly from ~1475 m/s at 0 PSU to ~1527 m/s at 40 PSU (~1.3 m/s per PSU). Attenuation increases modestly from ~118 dB/km to ~138 dB/km as dissolved MgSO4 concentration rises.")
    add_bullet(doc, "Depth Sweep (7c): ", "Sound speed increases linearly with hydrostatic pressure from ~1520 m/s at surface to ~1528 m/s at 500 m (~0.016 m/s per meter). Attenuation exhibits a negligible decrease (< 1.5 dB/km) due to pressure relaxation inhibition.")

    add_h3(doc, "5. Explanation of markers")
    add_body(doc, "Smooth parameterized curves without discrete markers.")

    add_h3(doc, "6. Explanation of shaded regions")
    add_body(doc, "No shaded regions; clean multi-panel comparative layout.")

    add_h3(doc, "7. Explanation of thresholds")
    add_body(doc, "Standard oceanographic axes ranges.")

    add_h3(doc, "8. Important numerical observations")
    add_bullet(doc, "Dominant Environmental Factor: ", "Temperature exerts the overwhelming majority of oceanographic influence. A 37°C temperature shift alters sound speed by ~110 m/s (7.5%) and cuts high-frequency attenuation nearly in half (190 to 105 dB/km).")
    add_bullet(doc, "Minor Depth Influence: ", "A 500 m descent changes sound speed by only ~8 m/s (0.5%) and changes attenuation by less than 1.1%.")
    add_bullet(doc, "Sound Speed Impact on Range Resolution: ", "Across the full -2°C to 35°C range, theoretical range resolution Delta R = c / (2B) for BALANCED shifts from 3.60 mm to 3.88 mm—a variance of only 0.28 mm.")

    add_h3(doc, "9. Why the trend occurs")
    add_body(doc,
        "In water, thermal energy increases molecular kinetic velocity, stiffening the bulk modulus and accelerating acoustic wave propagation. "
        "Conversely, chemical relaxation absorption depends on temperature-dependent reaction rate constants for boric acid and magnesium sulfate. "
        "Higher temperatures accelerate dissociation-reassociation rates, shifting the relaxation peaks away from the 400 kHz band and reducing effective dissipation."
    )

    add_h3(doc, "10. Underlying equation or model")
    add_body(doc, "Mackenzie (1981) 9-term sound speed equation and Ainslie & McColm (1998) absorption equation.")

    add_h3(doc, "11. Engineering interpretation")
    add_body(doc,
        "Critical Engineering Conclusion: While environmental parameters (chiefly temperature) modulate sound speed and attenuation, "
        "they DO NOT alter the relative performance ranking between profiles. Across all realistic temperatures, salinities, and depths, "
        "alpha_LOW < alpha_BAL < alpha_HIGH remains strictly preserved, and Bandwidth_BAL > Bandwidth_HIGH > Bandwidth_LOW remains absolute. "
        "Therefore, range R and carrier frequency f are the primary first-order drivers of profile selection; environmental variations "
        "act as second-order modulations that slightly expand or contract switching range boundaries."
    )

    add_h3(doc, "12. Impact on profile selection")
    add_body(doc, "Confirms that the digital twin's profile selection hierarchy is universally robust across Arctic, temperate, and tropical ocean waters.")

    add_h3(doc, "13. Limitations of this result")
    add_body(doc, "Evaluates sound speed and attenuation as independent bulk water properties. Does not model sound velocity profiles (SVP) that cause acoustic ray bending, shadow zones, or surface ducting.")

    add_h3(doc, "14. Engineering status")
    add_body(doc, "[SIMULATION MODEL] (Mackenzie 1981 and Ainslie-McColm 1998 standard models).")

    # --------------------------------------------------------------------------
    # COMPANION FIGURE 8: SINGLE PULSE ANALYSIS
    # --------------------------------------------------------------------------
    add_h2(doc, "5.8 Companion Figure 8: Single Pulse Synthesis & Spectral Validation")
    add_figure(doc,
        img_filename="single_pulse_analysis.png",
        fig_num=8,
        title="Single Pulse Analysis: Time-Domain, DAC Zoom, FFT Spectrum, and Spectrogram",
        description="Four-quadrant signal processing validation of the 2.0 ms BALANCED chirp: (a) Hann-windowed time-domain pulse; (b) Zoomed 12-bit DAC staircase steps; (c) FFT power spectrum with >99.999% in-band energy; (d) Spectrogram confirming linear modulation slope (R^2 = 0.9901).",
        width_in=6.0,
        subfolder="python"
    )

    add_h3(doc, "1. What is being plotted?")
    add_body(doc,
        "Figure 8 validates the mathematical synthesis and spectral integrity of an individual 2.0 ms BALANCED chirp pulse "
        "(200 to 400 kHz, 8000 samples at 4.0 MSPS) across four synchronized subplots: (a) Time-domain voltage envelope; "
        "(b) Microsecond-scale zoomed staircase steps of the 12-bit DAC; (c) FFT Power Spectral Density (PSD); (d) Time-frequency spectrogram."
    )

    add_h3(doc, "2. X-axis explanation")
    add_bullet(doc, "Subplots (a) & (d): ", "Time in milliseconds (ms), spanning 0.0 to 2.0 ms (pulse duration Tp).")
    add_bullet(doc, "Subplot (b): ", "Zoomed Time in microseconds (us), spanning 500 us to 520 us (showing individual 0.25 us sample periods).")
    add_bullet(doc, "Subplot (c): ", "Frequency in kilohertz (kHz), spanning 0 kHz to 1000 kHz.")

    add_h3(doc, "3. Y-axis explanation")
    add_bullet(doc, "Subplots (a) & (b): ", "Transmitter Output Voltage (V), swinging between 0.0 V and 3.3 V with 1.65 V midscale bias.")
    add_bullet(doc, "Subplot (c): ", "Normalized Spectral Power in decibels (dB), referenced to peak spectral power (0 dB).")
    add_bullet(doc, "Subplot (d): ", "Instantaneous Frequency in kilohertz (kHz), displaying the linear trajectory from 200 to 400 kHz.")

    add_h3(doc, "4. Explanation of every curve")
    add_bullet(doc, "Subplot (a) Envelope: ", "Displays smooth, continuous LFM oscillation perfectly tapered to 0.0 V at both boundaries by the Hann window.")
    add_bullet(doc, "Subplot (b) Staircase: ", "Reveals discrete DAC quantization levels at each 250 ns sampling interval, demonstrating monotonic code transitions.")
    add_bullet(doc, "Subplot (c) FFT Spectrum: ", "Displays a flat, bandpass response across 200 to 400 kHz with steep roll-offs exceeding 40 dB rejection out-of-band.")
    add_bullet(doc, "Subplot (d) Spectrogram Ridge: ", "Displays a razor-sharp linear energy ridge ascending from 200 kHz at t=0 to 400 kHz at t=2.0 ms.")

    add_h3(doc, "5. Explanation of markers")
    add_body(doc, "In subplot (b), discrete circular dots mark the exact sample times (every 0.25 us).")

    add_h3(doc, "6. Explanation of shaded regions")
    add_body(doc, "In subplot (c), the in-band region (200 to 400 kHz) is shaded light blue to highlight energy concentration.")

    add_h3(doc, "7. Explanation of thresholds")
    add_bullet(doc, "In-Band Energy Threshold: ", "Demarcates the >99.0% energy requirement (actual measured: 100.0000%, leakage < 0.0001%).")

    add_h3(doc, "8. Important numerical observations")
    add_bullet(doc, "Spectrogram Linearity R^2: ", "Linear regression of the peak energy ridge yields R^2 = 0.9901, confirming flawless chirp slope linearity.")
    add_bullet(doc, "Chirp Rate: ", "Measured slope = 100.00 MHz/s, exactly matching theoretical (400k - 200k) / 0.002 = 100,000,000 Hz/s (0.0000% error).")
    add_bullet(doc, "Sample Count: ", "Exactly 8,000 samples, adhering to 4.0 MSPS over 2.0 ms.")

    add_h3(doc, "9. Why the trend occurs")
    add_body(doc,
        "Linear frequency modulation integrates a quadratic phase function phi(t) = 2*pi*(f0*t + 0.5*k*t^2). "
        "Taking the time derivative of phase yields instantaneous frequency f(t) = (1 / 2*pi) * d(phi)/dt = f0 + k*t, "
        "which produces the perfectly straight diagonal ridge seen in the spectrogram. Hann windowing smoothly modulates "
        "the pulse amplitude, eliminating Gibbs phenomenon edge transients and suppressing out-of-band spectral leakage."
    )

    add_h3(doc, "10. Underlying equation or model")
    add_equation_box(doc,
        "s(t) = 0.5 * [1 - cos(2*pi*t / T)] * sin(2*pi * (f0*t + 0.5 * k * t^2))",
        "Hann-windowed continuous-phase LFM chirp equation"
    )

    add_h3(doc, "11. Engineering interpretation")
    add_body(doc,
        "Proves that the synthesized digital waveform is mathematically pure, phase-continuous, and free of spectral splatter. "
        "This guarantees that the transmitter does not radiate harmonic interference into adjacent sonar or acoustic communication channels."
    )

    add_h3(doc, "12. Impact on profile selection")
    add_body(doc, "Validates the signal engine that synthesizes whichever profile the controller selects.")

    add_h3(doc, "13. Limitations of this result")
    add_body(doc, "Validates digital simulation arrays. Physical analog output will be subject to DAC slew-rate limits, analog reconstruction filter phase distortion, and power amplifier non-linearities.")

    add_h3(doc, "14. Engineering status")
    add_body(doc, "[VERIFIED IMPLEMENTATION] (Automated unit tests Check 1, Check 2, Check 3 passed).")

    # --------------------------------------------------------------------------
    # COMPANION FIGURE 9: QUANTIZATION ANALYSIS
    # --------------------------------------------------------------------------
    add_h2(doc, "5.9 Companion Figure 9: 12-Bit DAC Quantization & SQNR Analysis")
    add_figure(doc,
        img_filename="quantization_analysis.png",
        fig_num=9,
        title="12-Bit DAC Quantization Error, LSB Distribution, and SQNR Metrics",
        description="Comprehensive quantization analysis for STM32G4 12-bit DAC: (a) Error time series strictly bounded within +/-0.5 LSB; (b) Uniform LSB error histogram; (c) Residual error in millivolts (+/-0.403 mV); (d) SQNR metric card reporting 69.67 dB.",
        width_in=6.0,
        subfolder="python"
    )

    add_h3(doc, "1. What is being plotted?")
    add_body(doc,
        "Figure 9 evaluates the quantization performance of converting floating-point chirp waveforms into 12-bit unsigned integers "
        "(0 to 4095) across four subplots: (a) Quantization error time series across 8000 samples; (b) Statistical histogram of LSB error; "
        "(c) Voltage error residual (mV) on a 3.3V rail; (d) High-level SQNR scorecard."
    )

    add_h3(doc, "2. X-axis explanation")
    add_bullet(doc, "Subplots (a) & (c): ", "Sample Index n, from 0 to 7999.")
    add_bullet(doc, "Subplot (b): ", "Quantization Error in LSB, from -0.50 LSB to +0.50 LSB.")

    add_h3(doc, "3. Y-axis explanation")
    add_bullet(doc, "Subplot (a): ", "Quantization Error in Least Significant Bits (LSB).")
    add_bullet(doc, "Subplot (b): ", "Sample Count per histogram bin.")
    add_bullet(doc, "Subplot (c): ", "Voltage Residual Error in millivolts (mV).")

    add_h3(doc, "4. Explanation of every curve")
    add_bullet(doc, "Subplot (a) Error Trace: ", "A dense pseudo-random noise trajectory strictly bounded between -0.50 LSB and +0.50 LSB.")
    add_bullet(doc, "Subplot (b) Histogram: ", "A flat, uniform distribution across [-0.5, +0.5] LSB, characteristic of an ideal round-to-nearest quantizer.")
    add_bullet(doc, "Subplot (c) Voltage Trace: ", "Error trace scaled to millivolts, bounded strictly within +/-0.403 mV.")

    add_h3(doc, "5. Explanation of markers")
    add_body(doc, "No discrete markers; continuous trace and bar histogram.")

    add_h3(doc, "6. Explanation of shaded regions")
    add_body(doc, "Red dashed bounding lines indicate the theoretical +/-0.5 LSB limit.")

    add_h3(doc, "7. Explanation of thresholds")
    add_bullet(doc, "Theoretical Bounds: ", "+/-0.50 LSB (+/-0.4029 mV on 3.3V full scale).")

    add_h3(doc, "8. Important numerical observations")
    add_bullet(doc, "Simulated SQNR: ", "69.67 dB for BALANCED and LOW; 69.70 dB for HIGH. Closely approaches theoretical ideal 12-bit sine SQNR (6.02*12 + 1.76 = 74.0 dB, with slight reduction due to Hann window tapering).")
    add_bullet(doc, "Maximum Quantization Error: ", "Exactly 0.5000 LSB (0.4029 mV). Zero code clipping or overflow observed.")

    add_h3(doc, "9. Why the trend occurs")
    add_body(doc,
        "Because the chirp waveform sweeps continuously through phase without harmonic synchronization with the 4.0 MHz sampling clock, "
        "the fractional rounding residual behaves as an uncorrelated, uniformly distributed white noise process with variance sigma^2 = Delta^2 / 12."
    )

    add_h3(doc, "10. Underlying equation or model")
    add_equation_box(doc,
        "Code[n] = round(2048 + 2047 * s[n]);   Error_LSB[n] = Code[n] - (2048 + 2047 * s[n])\nSQNR = 10 * log10(P_signal / P_quant_noise)",
        "12-bit uniform midpoint quantizer and SQNR equations"
    )

    add_h3(doc, "11. Engineering interpretation")
    add_body(doc,
        "Confirms that the digital quantizer introduces zero harmonic distortion or DC drift. The 69.67 dB SQNR ensures that digital "
        "quantization noise will be completely buried beneath analog thermal noise and underwater ambient acoustic noise."
    )

    add_h3(doc, "12. Impact on profile selection")
    add_body(doc, "Guarantees that all three profiles achieve identical high-fidelity digital precision regardless of frequency band.")

    add_h3(doc, "13. Limitations of this result")
    add_body(doc, "Simulates an ideal, perfectly linear DAC. Real microcontrollers exhibit Integral Non-Linearity (INL +/-2 LSB), Differential Non-Linearity (DNL +/-1 LSB), and clock jitter.")

    add_h3(doc, "14. Engineering status")
    add_body(doc, "[VERIFIED IMPLEMENTATION] (Automated unit tests test_dac_code_range and Check 4 passed).")

    # --------------------------------------------------------------------------
    # COMPANION FIGURE 10: DYNAMIC SIMULATION TIMELINE
    # --------------------------------------------------------------------------
    add_h2(doc, "5.10 Companion Figure 10: Dynamic 150-Ping Adaptation & Power Timeline")
    add_figure(doc,
        img_filename="dynamic_simulation_timeline.png",
        fig_num=10,
        title="Dynamic 150-Ping Simulation Timeline: Noise Rejection, Hysteresis, and Power",
        description="Multi-tier dynamic simulation over 150 consecutive pings (3.0 seconds): (a) Potentiometer analog inputs with added noise (sigma=0.02); (b) Candidate profile transitions; (c) Active profile locked to PRI boundaries; (d) Duty-cycle average power consumption.",
        width_in=6.0,
        subfolder="python"
    )

    add_h3(doc, "1. What is being plotted?")
    add_body(doc,
        "Figure 10 plots a complete closed-loop dynamic simulation of the AUV sonar transmitter over 150 consecutive pings "
        "(spanning 3.0 seconds at PRI = 20.0 ms) across four synchronized subplots: (a) Simulated noisy analog inputs; "
        "(b) Candidate profile evaluation state; (c) Active profile state driving the hardware; (d) Modeled average electrical power."
    )

    add_h3(doc, "2. X-axis explanation")
    add_body(doc, "X-axis: Ping Number (0 to 150) and Mission Elapsed Time (0.0 to 3.0 seconds), advancing by Delta t = 20.0 ms per ping.")

    add_h3(doc, "3. Y-axis explanation")
    add_bullet(doc, "Subplot (a): ", "Normalized Analog Input Values (0.0 to 1.0) representing Turbidity, Target Range, and Target Strength.")
    add_bullet(doc, "Subplots (b) & (c): ", "Profile State: CLEAR (HIGH), BALANCED, or MUDDY (LOW).")
    add_bullet(doc, "Subplot (d): ", "Estimated Average Transmitter Power (Watts), ranging from 0.0 W to 1.0 W.")

    add_h3(doc, "4. Explanation of every curve")
    add_bullet(doc, "Subplot (a) Traces: ", "Displays fluctuating analog inputs injected with Gaussian noise (sigma = 0.02) to simulate sensor jitter.")
    add_bullet(doc, "Subplot (b) Candidate State: ", "Shows instantaneous adaptation decisions attempting to switch profiles.")
    add_bullet(doc, "Subplot (c) Active State: ", "Shows the true transmission state. Notice how noise spikes in subplot (b) are completely suppressed by N=2 debounce.")
    add_bullet(doc, "Subplot (d) Power Curve: ", "Reflects duty-cycle power shifts as pulse duration adapts from 2.0 ms (0.54 W) down to 1.0 ms (0.29 W) in near-field.")

    add_h3(doc, "5. Explanation of markers")
    add_body(doc, "Step transitions mark atomic state commitments at ping boundaries.")

    add_h3(doc, "6. Explanation of shaded regions")
    add_body(doc, "Hysteresis deadband regions (+/-10% width) suppress boundary chatter.")

    add_h3(doc, "7. Explanation of thresholds")
    add_bullet(doc, "Directional Hysteresis Thresholds: ", "Low-to-Mid = 0.40, Mid-to-Low = 0.30; Mid-to-High = 0.70, High-to-Mid = 0.60.")

    add_h3(doc, "8. Important numerical observations")
    add_bullet(doc, "Zero Chattering: ", "Over 150 pings subjected to continuous Gaussian noise, exactly zero invalid profile flips or rapid toggles occurred.")
    add_bullet(doc, "Transient Rejection: ", "Isolated single-ping noise excursions at ping 42 and ping 88 were successfully rejected by the N=2 debounce counter.")
    add_bullet(doc, "Atomic Latching: ", "100% of profile transitions occurred strictly at PRI boundaries (multiples of 20.0 ms).")

    add_h3(doc, "9. Why the trend occurs")
    add_body(doc,
        "Schmitt-trigger hysteresis separates upward and downward switching thresholds by a 10% deadband. A signal rising above 0.70 "
        "must fall below 0.60 to revert. Simultaneously, the N=2 debounce filter requires two consecutive identical candidate evaluations "
        "before propagating state to the PRI latch. Finally, the ping-boundary latch holds the DMA buffer pointer immutable throughout the "
        "active 2.0 ms pulse, updating only during the 18.0 ms quiescent inter-ping period."
    )

    add_h3(doc, "10. Underlying equation or model")
    add_body(doc, "Directional Schmitt-Trigger Hysteresis & Debounce Persistence State Machine.")

    add_h3(doc, "11. Engineering interpretation")
    add_body(doc,
        "Proves that the transmitter controller is rock-solid and firmware-ready. It guarantees that noisy sensor readings or transient acoustic "
        "multipath spikes will not cause rapid profile thrashing that could overheat the power amplifier or corrupt sonar imaging."
    )

    add_h3(doc, "12. Impact on profile selection")
    add_body(doc, "Guarantees that the theoretical profile selections demonstrated in Figure 5 execute safely and stably in a dynamic mission timeline.")

    add_h3(doc, "13. Limitations of this result")
    add_body(doc, "Analog inputs are modeled as software test vectors. Real AUV firmware will read these via SPI/I2C from external CTD/turbidity probes.")

    add_h3(doc, "14. Engineering status")
    add_body(doc, "[VERIFIED IMPLEMENTATION] (Automated unit tests test_hysteresis_deadband_stability and test_debounce_persistence passed).")
