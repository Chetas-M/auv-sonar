# SIH Problem 26058: Low-Power, Real-Time Adaptive Software-Defined Sonar Transmitter Payload for Autonomous Underwater Vehicles (AUVs)

## MATLAB Digital Twin Simulation Architecture

This directory contains the official MATLAB-based digital twin simulator for the transmitter payload of an adaptive software-defined sonar targeting the **STMicroelectronics STM32G474** microcontroller.

---

> [!IMPORTANT]
> **Core Project Narrative & Engineering Scope Statement**:
> We built and validated a digital twin of an adaptive sonar transmitter waveform pipeline. The simulation evaluates frequency-dependent propagation using established absorption equations and compares three predefined LFM profiles under explicit environmental and mission assumptions. A two-tier policy first rejects profiles that fail a defined relative propagation criterion and then selects among viable profiles based on the simulated mission objective: resolution, directivity, or long-range robustness.
>
> The digital twin models the **transmitter payload pipeline**:
> Waveform synthesis $\to$ 12-bit DAC quantization $\to$ DMA memory mapping $\to$ frequency-dependent attenuation $\to$ propagation viability filtering $\to$ mission objective profile selection $\to$ directional hysteresis & debounce $\to$ atomic ping-boundary latching $\to$ duty-cycle power dissipation.
>
> It **DOES NOT** claim to validate:
> - Real underwater acoustic performance or measured echoes
> - Physical two-way echo reflection, target scattering strength, or receiver hydrophone gain
> - Actual piezoelectric transducer impedance or ceramic resonance
> - Acoustic propagation measurements in physical ocean water
> - Power amplifier (PA) thermal stability or analog settling
> - Actual hardware current consumption
> - Receiver hardware or closed-loop hydrophone acoustic feedback
> - Experimentally calibrated turbidity-to-frequency mapping
>
> The physical hardware demonstration is **transmitter-side only**.

```text
================================================================================
SIMULATION STATUS:
Simulation correctness level: algorithmically credible, physically unverified.
================================================================================
```

---

## 1. Single Source of Truth: Parameter Taxonomy

To maintain strict engineering rigor, every parameter in this digital twin is categorized into one of five distinct classes:

### [FIXED] Implementation Parameters (Hardware Locked for v1)
| Parameter | Symbol | Value | Engineering Justification |
|---|---|---|---|
| **DAC Sample Rate** | $F_s$ | $4.0\times 10^6\text{ Hz}$ | $T_s = 250\text{ ns}$. Nyquist frequency is $2.0\text{ MHz}$; provides 8 samples/cycle at $500\text{ kHz}$. |
| **DAC Resolution** | $\text{DAC\_bits}$ | $12\text{-bit unsigned}$ | Integer codes $0$ to $4095$; midscale $2048$ ($1.65\text{ V}$ bias for AC-coupled output). |
| **Target MCU** | — | `STM32G474` | 170 MHz ARM Cortex-M4F with high-speed DAC and DMA controller. |
| **Waveform Family** | — | `LFM Chirp Only` | Linear frequency modulation with exact phase integration. |
| **Window Function**| — | `Hann Window` | $w[n] = 0.5(1 - \cos(2\pi n / (N-1)))$; suppresses start/end transients. |
| **Pulse Duration** | $T_p$ | $2.0\text{ ms}$ | $N_p = F_s \cdot T_p = 8,000\text{ samples}$ (fixed for v1 runtime). |
| **Pulse Repetition**| $\text{PRI}$ | $20.0\text{ ms}$ | $50\text{ Hz}$ ping repetition rate; max unambiguous acoustic range $\approx 15\text{ m}$. |
| **Adaptive Profiles**| — | Exactly $3$ | Profile 1 (`LOW_FREQUENCY`), Profile 2 (`BALANCED`), Profile 3 (`HIGH_FREQUENCY`). |

### [ADAPTIVE] Runtime Parameters (Controlled by Adaptation Logic)
| Parameter | Symbol | Range / States | Selection Mechanism |
|---|---|---|---|
| **Active Profile** | $\text{Profile\_ID}$ | `1 (LOW_FREQUENCY), 2 (BALANCED), 3 (HIGH_FREQUENCY)` | Selected via Propagation Viability Filter + Mission Objective Hierarchy. |
| **Transmit Amplitude**| $A$ | $0.40, 0.70, 1.00$ | Normalized scaling: $A=1.0$ (Low Freq), $A=0.7$ (Balanced), $A=0.4$ (High Freq). |

### [ENVIRONMENT] Environmental Scenario Inputs (Simulation Variables)
| Parameter | Symbol | Baseline | Role in Simulation |
|---|---|---|---|
| **Target Range** | $R$ | $10.0 \to 200.0\text{ m}$ | Direct physical driver of spherical spreading transmission loss ($20\log_{10} R$). |
| **Depth** | $D$ | $50.0\text{ m}$ | Inputs to sound speed and hydrostatic pressure absorption equations. |
| **Temperature** | $T$ | $20.0^\circ\text{C}$ | Influences seawater sound speed and chemical relaxation absorption frequencies. |
| **Salinity** | $S$ | $35.0\text{ PSU}$ | Standard seawater salinity scale. |
| **Turbidity** | $\text{turb}$ | $0 \to 100\text{ NTU}$ | Optional sensitivity heuristic for particulate scattering loss ($\propto f^2$). |
| **Noise Penalty** | $\text{NP}_{\text{sim}}$ | $0.0\text{ dB}$ | Normalized relative noise penalty used to test controller robustness; not calibrated to a physical hydrophone. |

### [ASSUMPTION] Simulation Model Assumptions (Unmeasured Estimates)
| Parameter | Symbol | Assumed Value | Purpose & Limitation |
|---|---|---|---|
| **Active Transmit Power** | $P_{\text{active}}$ | $5.0\text{ W}$ | Model assumption for PA + DAC + MCU active state. Unmeasured bench estimate. |
| **Idle Power** | $P_{\text{idle}}$ | $0.045\text{ W}$ | Model assumption for low-power sleep state between pings ($45\text{ mW}$). |
| **Analog Static Electronics**| $P_{\text{elec}}$ | $0.300\text{ W}$ | Base electronics power when transmitter is enabled. |
| **Battery Rail Voltage** | $V_{\text{bat}}$ | $12.0\text{ V}$ | Assumed subsea battery bus voltage for current calculation. |
| **Hypothetical Pack** | $E_{\text{bat}}$ | $99.0\text{ Wh}$ | Standard carry-on compliant battery pack for transmitter-only load model. |
| **Relative Source Level** | $SL_{\text{rel}}$ | $0.0\text{ dB reference}$ | Normalized relative source level. No uncalibrated absolute acoustic SPL claimed. |
| **Viability Threshold** | $\text{Thresh}_{\text{viab}}$ | $-65.0\text{ dB relative}$ | Policy parameter used to demonstrate adaptive switching; not calibrated against a physical receiver. |

### [DERIVED] Analytically Computed Values
| Parameter | Expression | Value | Significance |
|---|---|---|---|
| **Sample Count** | $N_p = F_s \cdot T_p$ | $8,000\text{ samples}$ | Fixed buffer length per ping table. |
| **Buffer Memory** | $N_p \times 2\text{ bytes}$ | $16,000\text{ bytes}$ | $15.625\text{ KB}$ per profile as `uint16_t`. |
| **Duty Cycle** | $D = T_p / \text{PRI}$ | $10.0\%$ | $2.0\text{ ms} / 20.0\text{ ms} = 0.10$. |
| **Average Power** | $P_{\text{avg}} = P_{\text{act}}D + P_{\text{idle}}(1-D)$ | $0.540\text{ W}$ | Nominal average power at $10\%$ duty cycle and $A=1.0$. |
| **Active DMA Buffer** | $N_p \times 2\text{ bytes}$ | $16\text{ KB}$ | Individual active DMA buffer (12.5% of 128 KB SRAM before stack/heap). |
| **Waveform Flash LUTs** | $3 \times 16\text{ KB}$ | $48\text{ KB}$ | Storage for 3 profile LUTs (9.37% of 512 KB Flash before firmware code). |

---

## 2. Three Canonical Transmission Profiles & Physical Justification

```
      Profile 1: LOW_FREQUENCY          Profile 2: BALANCED             Profile 3: HIGH_FREQUENCY
      (Long-Range / Degraded Channel)   (Default Operating Mode)        (Narrow-Beam Directivity Mode)
  [======== 100 - 220 kHz ========]   [======== 200 - 400 kHz ========]   [======== 350 - 500 kHz ========]
     fc = 160 kHz, B = 120 kHz           fc = 300 kHz, B = 200 kHz           fc = 425 kHz, B = 150 kHz
     Lower attenuation envelope          Best Range Resolution (3.75 mm)     Narrow Theoretical Beamwidth
```

### Why Does Each Profile Exist?
- **Profile 1 (`LOW_FREQUENCY`)**:
  - Sweep: $100.0\text{–}220.0\text{ kHz}$ ($f_c = 160.0\text{ kHz}, B = 120.0\text{ kHz}$)
  - Justification: Within the implemented propagation model, `LOW_FREQUENCY` experiences lower modeled frequency-dependent attenuation ($\sim 18\text{ dB/km}$ vs $\sim 60\text{ dB/km}$ at $425\text{ kHz}$) and therefore remains viable at ranges beyond $175\text{ m}$ where higher-frequency profiles fall below the simulation viability threshold.
- **Profile 2 (`BALANCED`)**:
  - Sweep: $200.0\text{–}400.0\text{ kHz}$ ($f_c = 300.0\text{ kHz}, B = 200.0\text{ kHz}$)
  - Justification: Possesses the largest sweep bandwidth ($B = 200\text{ kHz}$), providing an ideal theoretical range-resolution limit of approximately $3.75\text{ mm}$ under matched-filter pulse-compression assumptions ($\Delta R = \frac{c}{2B}$). It serves as the primary survey default whenever propagation viability is satisfied.
- **Profile 3 (`HIGH_FREQUENCY`)**:
  - Sweep: $350.0\text{–}500.0\text{ kHz}$ ($f_c = 425.0\text{ kHz}, B = 150.0\text{ kHz}$)
  - Justification: Has a $1.417\times$ higher relative frequency-based directivity metric than the $300\text{ kHz}$ reference under a fixed-aperture theoretical assumption ($\theta \propto \frac{\lambda}{D} = \frac{c}{f \cdot D}$). Transducer geometry, aperture shape, beam patterns, array effects, and piezoelectric resonance are NOT modeled. Selected when the simulated vehicle prioritizes narrow-beam spatial directivity.

---

## 3. Profile Evaluation & Selection Architecture (Priority 1)

```text
                       ENVIRONMENTAL SCENARIO
                   (Range, Temp, Salinity, Depth)
                                 │
                                 ▼
                     PROFILE EVALUATION ENGINE
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
    LOW_FREQUENCY             BALANCED            HIGH_FREQUENCY
  (100 - 220 kHz)         (200 - 400 kHz)        (350 - 500 kHz)
         │                       │                       │
         ▼                       ▼                       ▼
  Band Attenuation        Band Attenuation        Band Attenuation
  Transmission Loss       Transmission Loss       Transmission Loss
  Relative Margin         Relative Margin         Relative Margin
  Range Resolution        Range Resolution        Range Resolution
  Rel. Directivity        Rel. Directivity        Rel. Directivity
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    PROPAGATION VIABILITY FILTER
               (Margin >= Relative Viability Threshold?)
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       All / Multiple Viable             Single / None Viable
                 │                               │
                 ▼                               ▼
      MISSION OBJECTIVE SELECTOR         FAIL-SAFE SELECTION
     - Default: BALANCED (Best res.)    - Select LOW_FREQUENCY
     - High-Directivity: HIGH_FREQ        (Lowest attenuation)
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                       RAW CANDIDATE PROFILE
                   + profile_selection_confidence
                                 │
                                 ▼
                       DIRECTIONAL HYSTERESIS
                      (Performance Deadbands)
                                 │
                                 ▼
                    DEBOUNCE PERSISTENCE FILTER
                         (N = 2 Pings)
                                 │
                                 ▼
                          PENDING PROFILE
                                 │
                                 ▼
                    ATOMIC PING-BOUNDARY LATCH
                      (DMA TC Interrupt / PRI)
                                 │
                                 ▼
                          ACTIVE PROFILE
```

---

## 4. How to Run in MATLAB

### Prerequisites
- MATLAB R2020a or later (also GNU Octave 7.0+ compatible).

### Commands
```matlab
% 1. Run this once from the MATLAB Current Folder browser.
setup_sonar_project;

% 2. Run a quick test first, then the master simulation.
run_profile_evaluation_tests;
run_simulation;

% 3. Run Priority 1 parameter sweep experiments (generates 7 experiment figures)
run_experiments;

% 4. Run full validation suites
run_validation_suite;             % 23-point DSP/waveform/quantization suite
run_profile_evaluation_tests;     % 12-point Priority 1 profile evaluation suite
```

---

## 5. Seven Priority 1 Engineering Figures (`outputs_matlab/plots/`)

1. **`exp01_attenuation_vs_frequency.png`**: Frequency-dependent attenuation curve across $80\text{–}520\text{ kHz}$ with 5 discrete evaluation points marked per profile.
2. **`exp02_propagation_vs_range.png`**: Modeled one-way propagation margin vs range ($5\text{–}200\text{ m}$) for all 3 profiles on the same axis with simulation viability threshold ($-65\text{ dB}$).
3. **`exp03_theoretical_range_resolution.png`**: Theoretical range resolution limit comparison showing `BALANCED` achieving $3.75\text{ mm}$ under matched-filter assumptions.
4. **`exp04_relative_directivity_comparison.png`**: Relative frequency-based directivity factor bar chart (*"Relative theoretical metric — fixed aperture assumption; transducer geometry and beam patterns are NOT modeled"*).
5. **`exp05_profile_winner_vs_range.png`**: Profile selection vs range under Survey (resolution priority) and Directivity (narrow-beam priority) mission objectives.
6. **`exp06_performance_margin_vs_range.png`**: Candidate margin above viability and dual confidence metrics (`viability_confidence` & `selection_confidence`) vs range.
7. **`exp07_environmental_sensitivity_summary.png`**: Multi-panel sensitivity analysis of $T, S, D$ on sound speed, absorption, and range resolution.

---

## 6. Critical Engineering Review of Priority 1 Decisions

| Decision | What Was Implemented? | Why Selected? | Alternatives Considered | Why Alternatives Rejected? | Introduced Assumptions | What Could Make It Wrong? | Hardware Impact |
|---|---|---|---|---|---|---|---|
| **5-Point Frequency Sampling** | Evaluated Ainslie-McColm absorption at 5 discrete points across each profile's bandwidth. | Captures frequency variation across wide chirp bandwidths ($120\text{–}200\text{ kHz}$). | Single center-frequency evaluation; continuous integral. | Single point masks band slope; continuous integral is computationally heavy on embedded targets. | Assumes 5-point mean adequately approximates continuous wideband attenuation. | Extreme non-linear chemical relaxation spikes within band. | None (pre-silicon analytical evaluation). |
| **Decoupling Viability from Utility** | Two-tier filter: check propagation viability first, then select based on mission objective. | Prevents `LOW_FREQUENCY` from artificially dominating all ranges due to low attenuation alone. | Single composite weighted score $w_1 TL + w_2 \Delta R + w_3 \text{Dir}$. | Arbitrary linear weightings lack physical units and obscure physical trade-offs. | Assumes a defined relative viability threshold ($-65\text{ dB}$). | Target reflectivity or receiver noise floor deviates from assumed threshold. | Matches standard AUV payload mission planning. |
| **Normalized Relative Margin** | Used $0\text{ dB}$ relative transmit reference and relative transmission loss $-TL - \text{NP}_{\text{sim}}$. | Avoids claiming an unverified absolute acoustic sound pressure level ($180\text{ dB}$). | Hardcoded $180\text{ dB re } 1\,\mu\text{Pa @ 1m}$. | Unjustified physical claim without transducer electromechanical coupling modeling. | Assumes one-way transmission loss is dominated by spherical spreading ($20\log_{10} R$). | Cylindrical shallow-water waveguide spreading ($10\log_{10} R$) or multipath. | Preserves honest engineering scope. |
| **Relative Viability Threshold (-65 dB)** | Explicitly classified as `[SIMULATION ASSUMPTION]`. | Demonstrates adaptive switching behavior without claiming physical receiver calibration. | Claiming calibrated hydrophone detection threshold. | Unsubstantiated claim since receiver hardware and hydrophones are not part of transmitter payload. | Assumed fixed $-65\text{ dB}$ relative signal floor. | Actual physical detection threshold depends on transducer, hydrophone, pre-amp, and DSP gain. | None (payload demo). |
| **Turbidity as Sensitivity Heuristic** | Evaluated turbidity scattering loss strictly as an optional sensitivity heuristic. | Acknowledges that turbidity-to-frequency mapping is uncalibrated in v1. | Hardcoded $50\%$ penalty on composite quality score. | Arbitrary heuristic presented as physical truth. | Assumes Rayleigh-type $f^2$ scattering proportionality coefficient. | Non-Rayleigh particulate sizes (Mie/geometric scattering regimes). | None. |
| **Dual Confidence Metrics** | Separated `viability_confidence` (margin above threshold) from `selection_confidence` (margin over runner-up). | Avoids confusing "comfortably viable" with "clearly superior to alternatives". | Single scalar score $Q$. | Overloaded environmental quality with winner separation. | Linear scaling over transition zones ($15\text{ dB}$ for viability, $6\text{ dB}$ for selection). | Sharp step thresholds without margin buffer. | Improves explainability of state transitions. |
