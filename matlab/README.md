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

## 1. Quickstart & Execution

### Option A: Running in Native MATLAB (R2020a+ or GNU Octave 7.0+)
Open MATLAB, navigate to this directory (`matlab/`), and execute:
```matlab
% 1. Setup project paths and environment
setup_sonar_project;

% 2. Run the master simulation and generate baseline plots (Figures 1-13)
run_simulation;

% 3. Run Priority 1 parameter sweep experiments (Figures 14-20)
run_experiments;

% 4. Run automated validation suites (35 total tests)
run_validation_suite;             % 23-point DSP, waveform, and quantization suite
run_profile_evaluation_tests;     % 12-point Priority 1 profile evaluation suite

% 5. Open the interactive engineering dashboard GUI
adaptive_sonar_dashboard;
```

### Option B: Headless Execution via Python Mirror (Zero MATLAB License Required)
If you do not have MATLAB installed, run the exact Python-based execution mirror from the workspace root:
```bash
python matlab/generate_matlab_results.py
```
This script executes the identical mathematical models and renders all 20 MATLAB engineering figures into `outputs_matlab/plots/` and C headers into `outputs_matlab/headers/`.

---

## 2. Directory & Script Architecture

| MATLAB File | Purpose & Subsystem | Python Equivalent (`src/`) |
|---|---|---|
| **`setup_sonar_project.m`** | Sets up MATLAB workspace paths and environment | `src/__init__.py` |
| **`config_sonar.m`** | Master configuration and single source of truth | `src/config.py` |
| **`profile_definitions.m`** | Defines 3 canonical profiles (`LOW_FREQUENCY`, `BALANCED`, `HIGH_FREQUENCY`) | `src/profiles.py` |
| **`generate_lfm_chirp.m`** | Phase-integrated LFM chirp generator with Hann tapering | `src/waveform.py` |
| **`dac_quantize.m`** | 12-bit DAC quantization ($0\text{–}4095$) and SQNR evaluation | `src/waveform.py` |
| **`channel_model.m`** | Ainslie-McColm attenuation and transmission loss modeling | `src/profile_evaluator.py` |
| **`evaluate_profile_performance.m`** | Priority 1 5-point evaluation and mission objective selection | `src/profile_evaluator.py` |
| **`adaptive_controller.m`** | Directional hysteresis deadbands and $N=2$ debounce filter | `src/adaptation.py` |
| **`power_model.m`** | Duty-cycle power dissipation and battery life model | `src/power_model.py` |
| **`export_c_headers.m`** | Exports 12-bit quantized LUTs as C99 headers | `src/export_c.py` |
| **`run_simulation.m`** | Master simulation runner (generates 13 baseline plots) | `src/main.py` |
| **`run_experiments.m`** | Priority 1 parameter sweeps (generates 7 experiment plots) | `src/experiments.py` |
| **`run_validation_suite.m`** | 23-point automated DSP and waveform verification suite | `tests/test_simulator.py` |
| **`run_profile_evaluation_tests.m`**| 12-point Priority 1 profile evaluation test suite | `tests/test_profile_evaluation.py` |
| **`adaptive_sonar_dashboard.m`** | Interactive MATLAB App for real-time scenario tuning | — |

---

## 3. Parameter Taxonomy (Single Source of Truth)

Every parameter in this digital twin is categorized into one of five distinct classes:

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
| **Noise Penalty** | $\text{NP}_{\text{sim}}$ | $0.0\text{ dB}$ | Normalized relative noise penalty used to test controller robustness. |

### [ASSUMPTION] Simulation Model Assumptions (Unmeasured Estimates)
| Parameter | Symbol | Assumed Value | Purpose & Limitation |
|---|---|---|---|
| **Active Transmit Power** | $P_{\text{active}}$ | $5.0\text{ W}$ | Model assumption for PA + DAC + MCU active state. Unmeasured bench estimate. |
| **Idle Power** | $P_{\text{idle}}$ | $0.045\text{ W}$ | Model assumption for low-power sleep state between pings ($45\text{ mW}$). |
| **Analog Static Electronics**| $P_{\text{elec}}$ | $0.300\text{ W}$ | Base electronics power when transmitter is enabled. |
| **Battery Rail Voltage** | $V_{\text{bat}}$ | $12.0\text{ V}$ | Assumed subsea battery bus voltage for current calculation. |
| **Hypothetical Pack** | $E_{\text{bat}}$ | $99.0\text{ Wh}$ | Standard carry-on compliant battery pack for transmitter-only load model. |
| **Relative Source Level** | $SL_{\text{rel}}$ | $0.0\text{ dB reference}$ | Normalized relative source level. No uncalibrated absolute acoustic SPL claimed. |
| **Viability Threshold** | $\text{Thresh}_{\text{viab}}$ | $-65.0\text{ dB relative}$ | Policy parameter used to demonstrate adaptive switching. |

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

## 4. Three Canonical Transmission Profiles & Physical Justification

```
      Profile 1: LOW_FREQUENCY          Profile 2: BALANCED             Profile 3: HIGH_FREQUENCY
      (Long-Range / Degraded Channel)   (Default Operating Mode)        (Narrow-Beam Directivity Mode)
  [======== 100 - 220 kHz ========]   [======== 200 - 400 kHz ========]   [======== 350 - 500 kHz ========]
     fc = 160 kHz, B = 120 kHz           fc = 300 kHz, B = 200 kHz           fc = 425 kHz, B = 150 kHz
     Lower attenuation envelope          Best Range Resolution (3.75 mm)     Narrow Theoretical Beamwidth
```

- **Profile 1 (`LOW_FREQUENCY`)**:
  - Sweep: $100.0\text{–}220.0\text{ kHz}$ ($f_c = 160.0\text{ kHz}, B = 120.0\text{ kHz}$)
  - Justification: Lowest modeled attenuation ($\sim 18\text{ dB/km}$ vs $\sim 60\text{ dB/km}$ at $425\text{ kHz}$); provides long-range robustness beyond $175\text{ m}$.
- **Profile 2 (`BALANCED`)**:
  - Sweep: $200.0\text{–}400.0\text{ kHz}$ ($f_c = 300.0\text{ kHz}, B = 200.0\text{ kHz}$)
  - Justification: Largest sweep bandwidth ($B = 200\text{ kHz}$), providing an ideal theoretical range-resolution limit of approximately $3.75\text{ mm}$ ($\Delta R = \frac{c}{2B}$). Default survey mode.
- **Profile 3 (`HIGH_FREQUENCY`)**:
  - Sweep: $350.0\text{–}500.0\text{ kHz}$ ($f_c = 425.0\text{ kHz}, B = 150.0\text{ kHz}$)
  - Justification: $1.417\times$ higher relative frequency directivity than the $300\text{ kHz}$ reference under fixed-aperture assumptions. Selected when narrow-beam directivity is prioritized.

---

## 5. Twenty Engineering Figures (`outputs_matlab/plots/`)

### Baseline Waveform & Controller Figures (1–13)
1. `01_time_domain_waveform.png`: Time-domain waveforms for all 3 profiles showing Hann window tapering.
2. `02_zoomed_waveform_section.png`: 80 µs microscopic detail showing 12-bit DAC stair-steps tracking ideal curve.
3. `03_instantaneous_frequency.png`: Linear frequency modulation trajectory tracking $200 \to 400\text{ kHz}$.
4. `04_fft_spectrum.png`: Magnitude spectrum verifying passband and $>50\text{ dB}$ stopband suppression.
5. `05_spectrogram.png`: STFT spectrogram showing straight linear time-frequency energy ridge.
6. `06_dac_quantization_error.png`: Quantization error residuals strictly bounded within $[-0.5, +0.5]\text{ LSB}$.
7. `07_dac_code_histogram.png`: DAC code distribution histogram centered at midscale code $2048$.
8. `08_profile_comparison.png`: Spectral overlay of all three bands (`LOW_FREQUENCY`, `BALANCED`, `HIGH_FREQUENCY`).
9. `09_channel_quality_timeline.png`: Predicted Channel Quality Score $Q(t)$ vs directional hysteresis thresholds.
10. `10_candidate_profile_timeline.png`: Raw candidate profile timeline driven by instantaneous channel conditions.
11. `11_active_profile_timeline.png`: Committed active profile timeline showing stability after debounce.
12. `12_hysteresis_debounce_demo.png`: Detailed demonstration of hysteresis deadband and $N=2$ debounce filter action.
13. `13_estimated_power_summary.png`: Transmitter payload average power timeline across mission and pulse duration sensitivity ($1\text{ ms}, 2\text{ ms}, 3\text{ ms}$).

### Priority 1 Evaluation & Experiment Figures (Exp 1–7)
14. `exp01_attenuation_vs_frequency.png`: Attenuation curve across $80\text{–}520\text{ kHz}$ with 5 discrete evaluation points marked per profile.
15. `exp02_propagation_vs_range.png`: Modeled one-way propagation margin vs range ($5\text{–}200\text{ m}$) with viability threshold ($-65\text{ dB}$).
16. `exp03_theoretical_range_resolution.png`: Theoretical range resolution comparison showing `BALANCED` achieving $3.75\text{ mm}$ resolution.
17. `exp04_relative_directivity_comparison.png`: Relative theoretical directivity factor bar chart (*"Relative theoretical metric — fixed aperture assumption"*).
18. `exp05_profile_winner_vs_range.png`: Profile selection vs range under Survey (resolution priority) and Directivity (narrow-beam priority) mission objectives.
19. `exp06_performance_margin_vs_range.png`: Candidate margin above viability and confidence metrics vs range.
20. `exp07_environmental_sensitivity_summary.png`: Multi-panel sensitivity analysis of $T, S, D$ on sound speed, absorption, and range resolution.
