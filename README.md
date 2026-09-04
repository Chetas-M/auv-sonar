# AUV Low-Power Adaptive Software-Defined Sonar Transmitter Digital Twin

A Python- and MATLAB-based engineering digital twin simulator and STM32G474 firmware prototype for the transmitter payload of a low-power adaptive software-defined sonar designed for Autonomous Underwater Vehicles (AUVs), implementing **SIH Problem 26058**.

Target Microcontroller: **STMicroelectronics STM32G474RET6** (ARM Cortex-M4F @ 160.0 MHz)  
Hardware DAC Rate: **4.0 MSPS (12-bit unsigned)** | Ping Repetition: **50 Hz (20.0 ms PRI, 10% Duty Cycle)**  
Automated Tests: **79 / 79 Passing in Pytest (100%)** | Parity: **Bit-Exact Firmware & Machine-Precision Physics**

---

## ⚡ 60-Second Quickstart

Get the full digital twin running in under a minute:

```bash
# 1. Clone & Set Up Python Environment
git clone https://github.com/Chetas-M/auv-sonar.git
cd auv-sonar
python -m venv .venv
.venv\Scripts\activate       # On Linux / macOS: source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the Full Automated Test Suite (79 Tests Passing)
pytest -v

# 3. Run Python Simulation & Priority 1 Experiments
python src/main.py
python -m src.experiments

# 4. Run MATLAB Digital Twin Mirror (No MATLAB License Required)
python matlab/generate_matlab_results.py

# 5. Verify & Compile STM32G474 Firmware (Host Build)
cd firmware
mingw32-make host            # On Linux / macOS: make host
cd ..

# 6. Generate Master Engineering Word Reports (Optional)
python generate_report_docx.py
python generate_results_report.py
```

---

## 🧭 Repository Map & Submodule Guides

```text
d:\AUV sonar\
├── src/                                  # Primary Python Digital Twin implementation
│   ├── config.py                         # Single source of truth for locked parameters
│   ├── profiles.py                       # Canonical acoustic profile definitions
│   ├── waveform.py                       # LFM chirp synthesis, Hann window, 12-bit DAC model
│   ├── profile_evaluator.py              # 5-point Ainslie-McColm absorption & mission selector
│   ├── physics_reference.py              # Reference acoustic models (Ainslie, Mackenzie, P2)
│   ├── adaptation.py                     # Schmitt-trigger hysteresis & N=2 debounce state machine
│   ├── power_model.py                    # Duty-cycle average power & battery endurance model
│   ├── export_c.py                       # C99 header & LUT exporter for STM32 firmware
│   ├── experiments.py                    # Priority 1 parameter sweeps (Exp 1 to 7)
│   ├── validation.py                     # 23-point DSP/waveform verification suite
│   ├── main.py                           # Master CLI pipeline runner
│   └── README.md                         # Detailed Python architecture guide
├── tests/                                # Automated verification & regression test suites
│   ├── test_simulator.py                 # Comprehensive 23-point hardware & DSP tests (36 tests)
│   ├── test_profile_evaluation.py        # Priority 1 profile evaluation tests (12 tests)
│   ├── test_physics_regression.py        # Acoustic physics & hydrostatic P2 tests (9 tests)
│   ├── test_matlab_parity.py             # Cross-platform Python/MATLAB parity tests (9 tests)
│   ├── test_firmware_lut_parity.py       # Bit-exact C header LUT parity tests (13 tests)
│   └── README.md                         # Test architecture & assertion matrix
├── firmware/                             # STM32G474 C11 embedded transmitter firmware
│   ├── Inc/ & Src/                       # Low-power bare-metal source (Clock, DAC, OPAMP, DMA, TIM)
│   ├── Makefile                          # Dual host-verification & ARM cross-compilation build
│   ├── hardware_bringup_checklist.md     # 8-step lab oscilloscope & DMM bring-up protocol
│   ├── stm32g4_dac_feasibility_audit.md  # Official 30KB hardware & datasheet feasibility audit
│   └── README.md                         # Embedded firmware architecture & flashing guide
├── matlab/                               # Standalone MATLAB digital twin mirror
│   ├── config_sonar.m                    # Configuration mirror
│   ├── evaluate_profile_performance.m    # Priority 1 evaluation engine mirror
│   ├── run_simulation.m                  # Master simulation runner (generates Figures 1–13)
│   ├── run_experiments.m                 # Priority 1 experiments (generates Figures 14–20)
│   ├── run_validation_suite.m            # 23-point MATLAB verification suite
│   ├── run_profile_evaluation_tests.m    # 12-point MATLAB profile evaluation suite
│   ├── adaptive_sonar_dashboard.m        # Interactive MATLAB GUI dashboard
│   ├── generate_matlab_results.py        # Headless Python mirror to run MATLAB pipeline
│   └── README.md                         # MATLAB digital twin documentation
├── outputs/                              # Python simulation outputs (plots, headers, canonical JSON)
├── outputs_matlab/                       # MATLAB mirror outputs (20 engineering plots, C headers)
├── walkthrough.md                        # High-level technical walkthrough & verification data
├── generate_report_docx.py               # Generates 70-page Digital Twin Engineering Report
├── generate_results_report.py            # Generates Complete Results Interpretation Report
└── requirements.txt                      # Python dependencies (numpy, scipy, matplotlib, pytest, docx)
```

| Component | Detailed Documentation | Primary Role |
|---|---|---|
| **Python Digital Twin** | [src/README.md](file:///d:/AUV%20sonar/src/README.md) | Pre-silicon signal synthesis, Ainslie-McColm absorption, adaptation logic, and power bounds |
| **Verification Suites** | [tests/README.md](file:///d:/AUV%20sonar/tests/README.md) | 79 automated tests validating DSP, math parity, hydrostatic pressure, and bit-exact C headers |
| **STM32 Firmware** | [firmware/README.md](file:///d:/AUV%20sonar/firmware/README.md) | 160 MHz bare-metal C11 firmware with TIM2 TRGO, DAC3+OPAMP3 follower, and DMA1 streaming |
| **Bring-Up Checklist** | [hardware_bringup_checklist.md](file:///d:/AUV%20sonar/firmware/hardware_bringup_checklist.md) | Oscilloscope, DMM, and probe spring protocol for physical bench verification |
| **Feasibility Audit** | [stm32g4_dac_feasibility_audit.md](file:///d:/AUV%20sonar/firmware/stm32g4_dac_feasibility_audit.md) | Datasheet analysis proving 4.0 MSPS DAC update feasibility and internal OPAMP follower routing |
| **MATLAB Twin Mirror**| [matlab/README.md](file:///d:/AUV%20sonar/matlab/README.md) | Full MATLAB simulation mirror, parameter sweeps, validation suites, and interactive GUI dashboard |
| **Engineering Walkthrough** | [walkthrough.md](file:///d:/AUV%20sonar/walkthrough.md) | Comprehensive engineering summary, SQNR analysis, duty-cycle power table, and results |

---

## 🔬 Core Engineering Scope & Boundary Statement

> [!IMPORTANT]
> **Engineering Scope & Model Limitations**:
> We built and validated a digital twin of an adaptive sonar transmitter waveform pipeline. The simulation evaluates frequency-dependent propagation using established absorption equations and compares three predefined LFM profiles under explicit environmental and mission assumptions. A two-tier policy first rejects profiles that fail a defined relative propagation criterion and then selects among viable profiles based on the simulated mission objective: resolution, directivity, or long-range robustness.
>
> This simulator models the **transmitter payload pipeline**:
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

### What This Simulator Proves vs What It Does Not Prove

#### Proved by Simulation & Testbench:
1. **Algorithmic Correctness**: Validates exact phase-integrated LFM chirp synthesis across all 3 canonical operational bands (`LOW_FREQUENCY`: 100–220 kHz, `BALANCED`: 200–400 kHz, `HIGH_FREQUENCY`: 350–500 kHz).
2. **Spectral Discontinuity Mitigation**: Confirms that applying a Hann window reduces start/end edge discontinuities and attenuates out-of-band spectral sidelobes in discrete simulation; physical analog harmonic rejection must be validated on bench scope/FFT.
3. **DAC Quantization Modeling**: Proves that a 12-bit unsigned DAC running at $4.0\text{ MSPS}$ yields $\sim 69.7\text{ dB}$ simulated SQNR, maintaining quantization error strictly within $\pm 0.5\text{ LSB}$ ($\pm 0.403\text{ mV}$ at $3.3\text{V}$ reference).
4. **Memory Allocation on STM32G4**: Verifies that a $2.0\text{ ms}$ pulse at $4\text{ MSPS}$ requires exactly **8,000 samples** ($16.0\text{ KB}$ as `uint16_t`). The generated waveform LUTs occupy approximately $48\text{ KB}$ before firmware and other memory allocations; individual active DMA buffers require approximately $16\text{ KB}$.
5. **Model-Derived Profile Selection**: Proves that distinguishing **propagation viability** from **mission utility** prevents `LOW_FREQUENCY` from artificially dominating all ranges, producing model-derived profile transition regimes under explicitly defined propagation and viability policy assumptions.
6. **Jitter-Free Adaptation**: Proves that directional Schmitt-trigger hysteresis and debounce persistence filters ($N=2$) eliminate state flickering caused by potentiometer wiper noise or ADC thermal fluctuation.
7. **Ping-Boundary Profile Latching**: Demonstrates that transmitter profile switches occur strictly at ping repetition boundaries, designed to be compatible with DMA transfer-complete synchronization to prevent mid-pulse phase jumps.
8. **Architectural Duty-Cycle Power Bounds**: Demonstrates that operating at a $10\%$ duty cycle ($2\text{ ms}$ pulse, $20\text{ ms}$ PRI) throttles average transmitter electrical power to $\sim 0.54\text{ W}$. For the modeled transmitter payload load alone against a hypothetical $99\text{ Wh}$ pack, this corresponds to $\sim 183\text{ hours}$ of operation. **Note: This does NOT represent full AUV mission endurance**, as the complete vehicle requires substantial power for thruster propulsion, navigation computers, INS/DVL, cameras, and acoustic communications.

#### Not Proved (Hardware / Field Dependent):
- **Transducer Resonance**: Does not simulate piezoelectric ceramic impedance, electromechanical coupling ($k_t$), or Butterworth-Van Dyke (BVD) equivalent circuit.
- **Analog Settling & Slew Rate**: Does not simulate analog DAC buffer settling time, amplifier slew rate, crossover distortion, or power amplifier thermal dissipation.
- **Ocean Channel Physics**: Does not simulate multipath acoustic scattering, thermocline refraction, or ambient ocean noise.
- **Bench Power Draw**: Power figures are analytical engineering models, not empirical multimeter measurements.

---

## 📐 Single Source of Truth: Parameter Taxonomy

Every parameter across both Python and MATLAB implementations is categorized into one of five distinct classes:

| Category | Description | Primary Parameters |
|---|---|---|
| **`[FIXED]`** | Locked implementation parameters | $F_s = 4.0\text{ MHz}$, $12\text{-bit DAC}$, $T_p = 2.0\text{ ms}$, $\text{PRI} = 20.0\text{ ms}$, $\text{MCU} = \text{STM32G474}$, $\text{Hann window}$ |
| **`[ADAPTIVE]`** | Controlled by adaptation logic | Profile ID (`LOW_FREQUENCY`, `BALANCED`, `HIGH_FREQUENCY`), Amplitude Factor $A \in \{0.4, 0.7, 1.0\}$ |
| **`[ENVIRONMENT]`** | Simulation scenario inputs | Range ($10\text{–}200\text{ m}$), Depth ($50\text{ m}$), Temp ($20^\circ\text{C}$), Salinity ($35\text{ PSU}$), Turbidity ($0\text{–}100\text{ NTU}$), Noise ($0\text{ dB}$) |
| **`[ASSUMPTION]`** | Unmeasured model assumptions | $P_{\text{active}} = 5.0\text{ W}$, $P_{\text{idle}} = 45\text{ mW}$, $P_{\text{elec}} = 0.30\text{ W}$, $V_{\text{bat}} = 12.0\text{ V}$, $E_{\text{bat}} = 99.0\text{ Wh}$, $\text{Thresh}_{\text{viab}} = -65\text{ dB}$ |
| **`[DERIVED]`** | Analytically computed metrics | $N_p = 8000$, $\text{Table Size} = 16\text{ KB}$, $\text{Duty Cycle} = 10\%$, $P_{\text{avg}} = 0.540\text{ W}$, $\text{SQNR} \approx 69.7\text{ dB}$ |

---

## 📡 Three Canonical Transmission Profiles

```text
      Profile 1: LOW_FREQUENCY          Profile 2: BALANCED             Profile 3: HIGH_FREQUENCY
      (Long-Range / Degraded Channel)   (Default Operating Mode)        (Narrow-Beam Directivity Mode)
  [======== 100 - 220 kHz ========]   [======== 200 - 400 kHz ========]   [======== 350 - 500 kHz ========]
     fc = 160 kHz, B = 120 kHz           fc = 300 kHz, B = 200 kHz           fc = 425 kHz, B = 150 kHz
     Lower attenuation envelope          Best Range Resolution (3.75 mm)     Narrow Theoretical Beamwidth
```

### Acoustic Physics: Range Resolution vs. Beam Directivity
- **Range Resolution ($\Delta R = \frac{c}{2B}$)**:
  - Governed strictly by the **sweep bandwidth $B$**.
  - **Profile 2 (`BALANCED`)** has an ideal theoretical range-resolution limit of approximately $3.75\text{ mm}$ under matched-filter pulse-compression assumptions ($B = 200\text{ kHz}$):
    $$\Delta R = \frac{1500\text{ m/s}}{2 \times 200\times 10^3\text{ Hz}} \approx 3.75\text{ mm}$$
  - **Profile 3 (`HIGH_FREQUENCY`)** has $B = 150\text{ kHz}$, giving an ideal limit of $5.00\text{ mm}$.
  - **Profile 1 (`LOW_FREQUENCY`)** has $B = 120\text{ kHz}$, giving an ideal limit of $6.25\text{ mm}$.
- **Beam Directivity ($\theta \propto \frac{\lambda}{D} = \frac{c}{f \cdot D}$)**:
  - **Profile 3 (`HIGH_FREQUENCY`)** has a $1.417\times$ higher relative frequency-based directivity metric than the $300\text{ kHz}$ reference under a fixed-aperture theoretical assumption. Transducer geometry, aperture shape, beam patterns, array effects, and piezoelectric resonance are NOT modeled.
  - Therefore, `HIGH_FREQUENCY` is selected for **high spatial angular directivity**, not because it has superior range resolution over `BALANCED`.
- **Long-Range Propagation Viability**:
  - Within the implemented propagation model, **`LOW_FREQUENCY`** experiences lower modeled frequency-dependent attenuation ($\sim 18\text{ dB/km}$ vs $\sim 60\text{ dB/km}$) and therefore remains viable at ranges beyond $175\text{ m}$ where higher-frequency profiles fall below the simulation viability threshold.

---

## 🧪 Automated Engineering Verification Suite

The repository contains 79 automated unit tests in Python (100% passing) and 35 tests in MATLAB verifying all 23 locked implementation requirements, 12 Priority 1 profile evaluation checks, 9 physics regression & hydrostatic parity tests, and cross-platform architecture alignment:

| Test Module | Test Method Count | Status | Key Subsystem Verified |
|---|:---:|:---:|---|
| **[`tests/test_simulator.py`](file:///d:/AUV%20sonar/tests/test_simulator.py)** | **36** | **PASSED** | 23 locked requirements ($8,000$ samples, $2.0\text{ ms}$, slope $100\text{ MHz/s}$, Hann tapering, 12-bit DAC bounds, $2048$ midscale, SQNR $\ge 69.5\text{ dB}$, deadbands, $N=2$ debounce, ping boundary latching, C header round-trip) |
| **[`tests/test_profile_evaluation.py`](file:///d:/AUV%20sonar/tests/test_profile_evaluation.py)** | **12** | **PASSED** | 5-point discrete frequency evaluation, positive finite attenuation, monotonic transmission loss with range, baseline attenuation ordering, range resolution vs directivity trade-off, survey/directivity mode selection |
| **[`tests/test_physics_regression.py`](file:///d:/AUV%20sonar/tests/test_physics_regression.py)** | **9** | **PASSED** | Seawater absorption parity against reference literature ($<10^{-10}$ error), $P_2 = \exp(-D/6000)$ hydrostatic scaling, canonical baseline constants ($63.99, 105.62, 135.86\text{ dB/km}$), extinction boundaries |
| **[`tests/test_matlab_parity.py`](file:///d:/AUV%20sonar/tests/test_matlab_parity.py)** | **9** | **PASSED** | Parity of all 18 MATLAB `.m` files with Python implementations across equations, constants, and plot counts |
| **[`tests/test_firmware_lut_parity.py`](file:///d:/AUV%20sonar/tests/test_firmware_lut_parity.py)** | **13** | **PASSED** | **Bit-exact identity** ($0\text{ LSB}$ max error) between Python generated waveforms and C firmware headers in `outputs/headers/*.h` |
| **Total Automated Tests** | **79** | **100% PASS** | **Complete pre-silicon digital twin validation** |

---

## 📊 Catalog of Generated Visualizations (20 Engineering Figures)

All 20 engineering figures are generated into `outputs_matlab/plots/` and `outputs/plots/`:

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
11. `11_active_profile_timeline.png`: Committed active profile timeline showing rock-solid stability after debounce.
12. `12_hysteresis_debounce_demo.png`: Detailed demonstration of hysteresis deadband and $N=2$ debounce filter action.
13. `13_estimated_power_summary.png`: Transmitter payload average power timeline across mission and pulse duration sensitivity analysis ($1\text{ ms}, 2\text{ ms}, 3\text{ ms}$).

### Priority 1 Evaluation & Experiment Figures (Exp 1–7)
14. `exp01_attenuation_vs_frequency.png`: Attenuation curve across $80\text{–}520\text{ kHz}$ with 5 discrete evaluation points marked per profile.
15. `exp02_propagation_vs_range.png`: Relative propagation margin vs range ($5\text{–}200\text{ m}$) for all 3 profiles on the same axis with viability threshold ($-65\text{ dB}$).
16. `exp03_theoretical_range_resolution.png`: Theoretical range resolution comparison showing `BALANCED` achieving $3.75\text{ mm}$ resolution.
17. `exp04_relative_directivity_comparison.png`: Relative theoretical directivity factor bar chart (*"Relative theoretical metric — fixed aperture assumption"*).
18. `exp05_profile_winner_vs_range.png`: Profile selection vs range under Survey (resolution priority) and Directivity (narrow-beam priority) mission objectives.
19. `exp06_performance_margin_vs_range.png`: Candidate margin above viability and `profile_selection_confidence` vs range.
20. `exp07_environmental_sensitivity_summary.png`: Multi-panel sensitivity analysis of $T, S, D$ on sound speed, absorption, and range resolution.

---

## ⚙️ Hardware Architecture & Pinout Summary

Target development platform: **STMicroelectronics NUCLEO-G474RE**

- **SYSCLK:** $160.000\text{ MHz}$ via PLL from $8.0\text{ MHz}$ ST-LINK MCO ($\text{PLLM}=1, \text{PLLN}=40, \text{PLLR}=2$).
- **Trigger Rate:** TIM2 TRGO at **$4,000,000.00\text{ Hz}$ with $0.000\%$ frequency error** ($\text{PSC}=0, \text{ARR}=39$).
- **DAC Routing:** Internal 15 MSPS **DAC3 Channel 2** routed on-chip directly to **OPAMP3** in High-Speed Follower mode ($45\text{ V}/\mu\text{s}$ slew rate) out to pin **PB1** (Morpho `CN10 Pin 24`). The slow internal 1 MSPS DAC buffer is explicitly bypassed.
- **DMA Streaming:** DMA1 Channel 1 (DMAMUX Request ID 103) streams 8,000 half-words per chirp directly from Flash to `DAC3->DHR12R2` at $8.0\text{ MB/s}$ throughput ($1.18\%$ AHB bus utilization).
- **Profile Latching:** Asynchronous candidate profile switches latch atomically at ping boundaries ($50\text{ Hz}$ PRI, $20.0\text{ ms}$) inside the DMA Transfer-Complete ISR.

For step-by-step physical bring-up procedures, consult [hardware_bringup_checklist.md](file:///d:/AUV%20sonar/firmware/hardware_bringup_checklist.md).
