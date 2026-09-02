# AUV Low-Power Adaptive Software-Defined Sonar Transmitter Digital Twin

A Python- and MATLAB-based engineering digital twin simulator for the transmitter payload of a low-power adaptive software-defined sonar designed for Autonomous Underwater Vehicles (AUVs), implementing **SIH Problem 26058**.

This simulator models the pre-silicon signal synthesis, adaptive channel decision logic, and DMA memory architecture targeted for the **STMicroelectronics STM32G474** (170 MHz ARM Cortex-M4F with high-speed DAC and DMA).

---

> [!IMPORTANT]
> **Core Project Narrative & Engineering Scope Statement**:
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

---

## 1. Engineering Scope & Constraints

> [!IMPORTANT]
> **Payload-Only Scope**:
> - This project models **only the adaptive transmitter payload pipeline** (analog potentiometer acquisition $\to$ discrete threshold adaptation $\to$ LFM chirp synthesis $\to$ 12-bit DAC quantization $\to$ DMA memory mapping $\to$ duty-cycle power estimation).
> - It is **NOT** a full sonar imaging system, bathymetric scanner, side-scan processor, or beamformer. Receiver processing (hydrophone front-ends, match-filtering, Doppler estimation) is outside the scope of this transmitter model.

> [!WARNING]
> **Input Emulation vs Real Sensors**:
> - For **v1 hardware**, the 3 environmental controls (turbidity, range/depth, and target reflectivity) are emulated via **three precision potentiometers** connected to STM32 12-bit ADC channels.
> - **Target-strength input emulates a future receiver/SNR feedback signal**; without a receiver/hydrophone path, the system cannot know whether a real target is strong or weak.
> - Do not claim or infer optical turbidity, nephelometric turbidity units (NTU), or CTD salinity measurement unless physical subsea oceanographic sensors are integrated in future revisions.

---

## 2. What This Simulator Proves vs What It Does Not Prove

### What This Simulator Proves
1. **Algorithmic Correctness**: Validates exact phase-integrated Linear Frequency Modulation (LFM) synthesis across all 3 canonical operational bands (`LOW_FREQUENCY`: 100–220 kHz, `BALANCED`: 200–400 kHz, `HIGH_FREQUENCY`: 350–500 kHz).
2. **Spectral Discontinuity Mitigation**: Confirms that applying a Hann window reduces start/end edge discontinuities and attenuates out-of-band spectral sidelobes in discrete simulation; physical analog harmonic rejection must be validated on bench scope/FFT.
3. **DAC Quantization Modeling**: Proves that a 12-bit unsigned DAC running at $4.0\text{ MSPS}$ yields $\sim 69.7\text{ dB}$ simulated SQNR, maintaining quantization error strictly within $\pm 0.5\text{ LSB}$ ($\pm 0.403\text{ mV}$ at $3.3\text{V}$ reference).
4. **Memory Allocation on STM32G4**: Verifies that a $2.0\text{ ms}$ pulse at $4\text{ MSPS}$ requires exactly **8,000 samples** ($16.0\text{ KB}$ as `uint16_t`). The generated waveform LUTs occupy approximately $48\text{ KB}$ before firmware and other memory allocations; individual active DMA buffers require approximately $16\text{ KB}$.
5. **Model-Derived Profile Selection**: Proves that distinguishing **propagation viability** from **mission utility** prevents `LOW_FREQUENCY` from artificially dominating all ranges, producing model-derived profile transition regimes under explicitly defined propagation and viability policy assumptions.
6. **Jitter-Free Adaptation**: Proves that directional Schmitt-trigger hysteresis and debounce persistence filters ($N=2$) eliminate state flickering caused by potentiometer wiper noise or ADC thermal fluctuation.
7. **Ping-Boundary Profile Latching**: Demonstrates that transmitter profile switches occur strictly at ping repetition boundaries, designed to be compatible with DMA transfer-complete synchronization to prevent mid-pulse phase jumps.
8. **Architectural Duty-Cycle Power Bounds**: Demonstrates that operating at a $10\%$ duty cycle ($2\text{ ms}$ pulse, $20\text{ ms}$ PRI) throttles average transmitter electrical power to $\sim 0.54\text{ W}$. For the modeled transmitter payload load alone against a hypothetical $99\text{ Wh}$ pack, this corresponds to $\sim 183\text{ hours}$ of operation. **Note: This does NOT represent full AUV mission endurance**, as the complete vehicle requires substantial power for thruster propulsion, navigation computers, INS/DVL, cameras, and acoustic communications.

### What This Simulator Does Not Prove
- **Piezoelectric Transducer Impedance**: Does not simulate the complex electrical impedance, electromechanical coupling coefficient ($k_t$), or Butterworth-Van Dyke (BVD) resonant response of the physical ceramic transducer.
- **Analog Front-End & Settling**: Does not simulate analog DAC buffer settling time, amplifier slew rate, crossover distortion, or power amplifier thermal efficiency.
- **High-Speed DAC Bring-Up**: At $4.0\text{ MSPS}$, the exact STM32G4 high-speed DAC channel configuration, output buffer bypass, and external op-amp reconstruction filtering must be verified on hardware.
- **Underwater Acoustic Propagation**: Does not simulate seawater volume attenuation, multipath surface/bottom reflections, thermoclines, or acoustic reverberation.
- **Bench Power Consumption**: Power metrics are analytical engineering models, not empirical bench multimeter measurements.

---

## 3. Parameter Taxonomy (Single Source of Truth)

Every parameter across both Python and MATLAB implementations is categorized into one of five distinct classes:

| Category | Description | Primary Parameters |
|---|---|---|
| **`[FIXED]`** | Locked implementation parameters | $F_s = 4.0\text{ MHz}$, $12\text{-bit DAC}$, $T_p = 2.0\text{ ms}$, $\text{PRI} = 20.0\text{ ms}$, $\text{MCU} = \text{STM32G474}$, $\text{Hann window}$ |
| **`[ADAPTIVE]`** | Controlled by adaptation logic | Profile ID (`LOW_FREQUENCY`, `BALANCED`, `HIGH_FREQUENCY`), Amplitude Factor $A \in \{0.4, 0.7, 1.0\}$ |
| **`[ENVIRONMENT]`** | Simulation scenario inputs | Range ($10\text{–}200\text{ m}$), Depth ($50\text{ m}$), Temp ($20^\circ\text{C}$), Salinity ($35\text{ PSU}$), Turbidity ($0\text{–}100\text{ NTU}$), Noise ($0\text{ dB}$) |
| **`[ASSUMPTION]`** | Unmeasured model assumptions | $P_{\text{active}} = 5.0\text{ W}$, $P_{\text{idle}} = 45\text{ mW}$, $P_{\text{elec}} = 0.30\text{ W}$, $V_{\text{bat}} = 12.0\text{ V}$, $E_{\text{bat}} = 99.0\text{ Wh}$, $\text{Thresh}_{\text{viab}} = -65\text{ dB}$ |
| **`[DERIVED]`** | Analytically computed metrics | $N_p = 8000$, $\text{Table Size} = 16\text{ KB}$, $\text{Duty Cycle} = 10\%$, $P_{\text{avg}} = 0.540\text{ W}$, $\text{SQNR} \approx 69.7\text{ dB}$ |

---

## 4. Three Canonical Transmission Profiles

```
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

## 5. Automated Engineering Validation (56 Tests Passed)

The repository contains automated validation test suites in both MATLAB and Python verifying all 23 locked implementation requirements and 12 Priority 1 profile evaluation checks:

- **23 Hardware & Signal Validation Tests** (`matlab/run_validation_suite.m` & `tests/test_simulator.py`):
  - Sample count ($8,000$), pulse duration ($2.0\text{ ms}$), chirp slope ($100\text{ MHz/s}$), start/end frequency, no NaN/Inf, Hann tapering, 12-bit DAC codes, midscale code ($2048$), SQNR ($69.7\text{ dB}$), hysteresis deadbands, debounce persistence ($N=2$), ping-boundary latching, and bit-exact C header export round-trip.
- **12 Priority 1 Profile Evaluation Tests** (`matlab/run_profile_evaluation_tests.m` & `tests/test_profile_evaluation.py`):
  - 5-point discrete frequency evaluation across band, positive finite attenuation, monotonic transmission loss with range, baseline attenuation ordering ($\text{HIGH} > \text{BALANCED} > \text{LOW}$), bandwidth-based range resolution verification ($\Delta R = 3.75\text{ mm}$ best), relative directivity ordering ($\text{HIGH} > \text{BALANCED} > \text{LOW}$), band confinement of evaluation points, long-range viability fallback to `LOW_FREQUENCY`, Survey Mode selection of `BALANCED`, Directivity Mode selection of `HIGH_FREQUENCY`, and bit-exact determinism.

---

## 6. Generated Visualizations (20 Engineering Figures)

All 20 engineering figures are generated into `outputs_matlab/plots/`:

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

## 7. Execution Commands

### Running Python Pipeline & Experiments
```bash
python src/main.py
python -m src.experiments
```

### Running Complete Python Test Suite (56 Tests)
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Running MATLAB Simulation, Experiments, and Tests
```bash
# In Python execution mirror:
python matlab/generate_matlab_results.py

# In MATLAB interactive prompt:
cd matlab
run_simulation;
run_experiments;
run_validation_suite;
run_profile_evaluation_tests;
```
