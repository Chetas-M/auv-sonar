# AUV Sonar Transmitter Digital Twin: MATLAB Simulink Modeling Suite

**SIH Problem 26058: Low-Power, Real-Time Adaptive Software-Defined Sonar Transmitter Payload for Autonomous Underwater Vehicles (AUVs)**

This directory contains the official **MATLAB Simulink Model Suite** for the adaptive sonar transmitter payload targeting the **STMicroelectronics STM32G474RET6** microcontroller.

---

> [!IMPORTANT]
> **Truth in Engineering (Strict Scope Statement)**:
> This Simulink suite models and validates the **transmitter payload pipeline**:
> Waveform synthesis $\to$ 12-bit DAC quantization $\to$ DMA memory mapping $\to$ frequency-dependent attenuation $\to$ propagation viability filtering $\to$ mission objective profile selection $\to$ directional hysteresis & debounce $\to$ atomic ping-boundary latching $\to$ duty-cycle power dissipation.
>
> It **DOES NOT** validate physical ocean acoustic propagation, real echoes, hydrophone receiver processing, transducer piezoelectric resonance, or analog power amplifier settling. Hardware bring-up is transmitter-side only.

```text
================================================================================
SIMULATION STATUS:
Simulation correctness level: algorithmically credible, physically unverified.
================================================================================
```

---

## 1. Quickstart & Execution

All models feature **self-healing, path-detecting callbacks** (`PreLoadFcn` and `InitFcn`) that dynamically locate the model file on disk and add both `matlab/` and `matlab/simulink/` to your MATLAB search path. You can open any model directly from the MATLAB command window, the file browser, or a script without encountering `'Unrecognized function or variable init_sonar_simulink'` errors.

### In Interactive MATLAB (R2020a+ or R2026a)
```matlab
% 1. Optional setup (callbacks self-heal automatically if skipped)
setup_sonar_project;

% 2. Open the ALL-IN-ONE Master Unified Model
open_system('auv_sonar_transmitter_payload');

% Or open any of the modular subsystems:
open_system('auv_sonar_mission_controller');  % Dynamic ping-rate controller (Ts = 20 ms)
open_system('auv_sonar_waveform_pipeline');   % High-speed 4.0 MSPS DAC & DSP pipeline
open_system('auv_sonar_payload_top');         % Integrated top-level architecture

% 3. Run automated 18-point parity verification & render report figures
res = run_simulink_validation;
```

### In Headless Batch Mode (Terminal / CI)
Run the automated test suite and report figure generator directly from the command line:
```bash
matlab -batch "addpath('matlab'); setup_sonar_project; run_simulink_validation;"
```

To rebuild and re-wire all models from code:
```bash
matlab -batch "addpath('matlab'); setup_sonar_project; build_all_models;"
```

---

## 2. Simulink Models Overview

| Model File | Type | Simulation Time Base | Primary Subsystems & Engineering Roles |
|---|---|---|---|
| **[`auv_sonar_transmitter_payload.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_transmitter_payload.slx)** | **ALL-IN-ONE Unified Master Model** | $T_s = \text{PRI} = 20.0\text{ ms}$<br>($50\text{ Hz}$ ping rate, $3.0\text{ s}$ duration) | Complete end-to-end payload: Environment Plume $\to$ Channel Absorption Evaluator $\to$ Directional Schmitt Hysteresis ($0.30/0.40$ & $0.65/0.75$) with $N=2$ Debounce $\to$ Atomic Ping-Boundary Latching $\to$ DMA Memory Buffer Mapping ($16\text{ KB}$) $\to$ Duty-Cycle Power ($10\%$) & 99 Wh Battery Endurance. Features dedicated scopes aligned with Figures 1–13 of the Engineering Report. |
| **[`auv_sonar_mission_controller.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_mission_controller.slx)** | Modular Controller | $T_s = \text{PRI} = 20.0\text{ ms}$ | Standalone ping-rate adaptation FSM and duty-cycle power estimator. |
| **[`auv_sonar_waveform_pipeline.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_waveform_pipeline.slx)** | High-Speed DSP | $T_s = 250\text{ ns}$<br>($F_s = 4.0\text{ MSPS}$, $T_p = 2.0\text{ ms}$, $N_p = 8000$) | Synthesizes continuous-phase LFM chirp with Hann windowing for active profile, 12-bit unsigned DAC quantization ($0\text{--}4095$, midscale $2048$, $3.3\text{V}$ rail), LSB and millivolt quantization error, and OPAMP3 high-speed follower stage ($45\text{ V}/\mu\text{s}$, pin PB1). |
| **[`auv_sonar_payload_top.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_payload_top.slx)** | Integrated Architecture | $T_s = 20.0\text{ ms}$ | Master system architecture linking mission adaptation to the waveform and DMA memory buffer sizing. |

---

## 3. Engineering Report Aligned Figures (`outputs/engineering_report/`)

Executing [`generate_simulink_report_figures.m`](file:///c:/AUV/auv-sonar/matlab/simulink/generate_simulink_report_figures.m) or [`run_simulink_validation.m`](file:///c:/AUV/auv-sonar/matlab/simulink/run_simulink_validation.m) runs the Simulink models and generates all 13 figures exactly matching the Engineering Report:

| Figure File | Report Section | Content & Engineering Meaning |
|---|---|---|
| `01_time_domain_waveform.png` | Fig 1 | Time-domain waveforms for all 3 profiles with exact Hann window envelope tapering |
| `02_zoomed_waveform_section.png` | Fig 2 | 80 µs microscopic detail showing 12-bit DAC stair-steps tracking continuous curve |
| `03_instantaneous_frequency.png` | Fig 3 | Instantaneous frequency trajectory tracking linear sweep ($200 \to 400\text{ kHz}$) |
| `04_fft_spectrum.png` | Fig 4 | Passband verification ($200\text{--}400\text{ kHz}$) and $>50\text{ dB}$ stopband suppression |
| `05_spectrogram.png` | Fig 5 | STFT spectrogram showing straight linear time-frequency energy ridge |
| `06_dac_quantization_error.png` | Fig 6 | 12-bit DAC quantization error residuals strictly bounded within $[-0.5, +0.5]\text{ LSB}$ |
| `07_dac_code_histogram.png` | Fig 7 | DAC output code distribution histogram centered at midscale code $2048$ |
| `08_profile_comparison.png` | Fig 8 | Spectral comparison overlay of all three bands (`LOW`, `BALANCED`, `HIGH`) |
| `09_channel_quality_timeline.png` | Fig 9 | Predicted Channel Quality Score $Q(t)$ vs directional hysteresis thresholds |
| `10_candidate_profile_timeline.png` | Fig 10 | Raw candidate profile timeline driven by instantaneous channel conditions |
| `11_active_profile_timeline.png` | Fig 11 | Committed active profile timeline showing stability after debounce |
| `12_hysteresis_debounce_demo.png` | Fig 12 | Zoomed detail ($t \in [1.0, 1.8]\text{ s}$) demonstrating hysteresis and $N=2$ debounce filter |
| `13_estimated_power_summary.png` | Fig 13 | Transmitter average power timeline and pulse duration sensitivity ($1, 2, 3\text{ ms}$) |

---

## 4. MATLAB File Reference & Bridge Mapping

| Simulink Subsystem / Block | Referenced MATLAB File | Bridge Function | Engineering Role |
|---|---|---|---|
| `Channel_Propagation_Evaluator` | [`channel_model.m`](file:///c:/AUV/auv-sonar/matlab/channel_model.m), [`evaluate_profile_performance.m`](file:///c:/AUV/auv-sonar/matlab/evaluate_profile_performance.m) | `sim_bridge_channel.m` | Calculates sound speed $c$, Ainslie-McColm absorption, transmission loss, and profile viability |
| `Adaptive_Controller` | [`adaptive_controller.m`](file:///c:/AUV/auv-sonar/matlab/adaptive_controller.m) | `sim_bridge_controller.m` | Executes directional Schmitt hysteresis, $N=2$ debounce persistence, and ping-boundary latching |
| `Power_Model_Estimator` | [`power_model.m`](file:///c:/AUV/auv-sonar/matlab/power_model.m) | `sim_bridge_power.m` | Evaluates $10\%$ duty-cycle power, $12\text{V}$ battery rail current, and 99 Wh pack endurance |
| `LFM_Chirp_Synthesizer` | [`generate_lfm_chirp.m`](file:///c:/AUV/auv-sonar/matlab/generate_lfm_chirp.m), [`profile_definitions.m`](file:///c:/AUV/auv-sonar/matlab/profile_definitions.m) | `sim_bridge_waveform.m` | Synthesizes continuous-phase LFM chirp with Hann windowing for active profile |
| `DAC_12Bit_Quantizer` | [`dac_quantize.m`](file:///c:/AUV/auv-sonar/matlab/dac_quantize.m) | `sim_bridge_dac.m` | 12-bit unsigned DAC quantization ($0\text{--}4095$), midscale $2048$, and SQNR evaluation |
| Model Initialization | [`config_sonar.m`](file:///c:/AUV/auv-sonar/matlab/config_sonar.m), [`profile_definitions.m`](file:///c:/AUV/auv-sonar/matlab/profile_definitions.m) | `init_sonar_simulink.m` | Pre-populates sample times, buffer sizes, and mission trajectories into workspace |

---

## 5. Automated Parity Verification Suite (18 Checks)

Executing [`run_simulink_validation.m`](file:///c:/AUV/auv-sonar/matlab/simulink/run_simulink_validation.m) runs an automated 18-point test harness verifying numeric and bit-exact parity:

```text
==============================================================================
  RUNNING 18-POINT SIMULINK PARITY VERIFICATION SUITE
==============================================================================
  Check 01: Model Files: All 4 .slx models present on disk (including unified) [PASSED]
  Check 02: Timing: Mission controller output length == 150 pings        [PASSED]
  Check 03: Channel: Quality Score Q Max Error = 0.00e+00 (< 1e-5)       [PASSED]
  Check 04: Controller: Candidate profile sequence exact match           [PASSED]
  Check 05: Controller: Latched active profile exact match               [PASSED]
  Check 06: Hysteresis: Directional deadbands exercised (P1 and P2)      [PASSED]
  Check 07: Controller: N=2 Debounce filter confirmed                    [PASSED]
  Check 08: Ping Latching: Active profile updates strictly on boundaries [PASSED]
  Check 09: Amplitude: Transmit amplitude policy exact match             [PASSED]
  Check 10: Power: Average power dissipation exact match                 [PASSED]
  Check 11: DSP: Pulse sample count == 8000 (4.0 MSPS, 2.0 ms)           [PASSED]
  Check 12: DSP: Ideal LFM waveform matches reference (Max Err = 2.1e-4) [PASSED]
  Check 13: DAC: Output integer codes within range (614 to 3481)         [PASSED]
  Check 14: DAC: Quantization error bounded (Max = 0.500 LSB <= 0.501)   [PASSED]
  Check 15: DAC: Empirical SQNR = 66.64 dB matches reference 66.62 dB    [PASSED]
  Check 16: Top Model: auv_sonar_payload_top simulated without errors    [PASSED]
  Check 17: Unified Model: auv_sonar_transmitter_payload simulated       [PASSED]
  Check 18: Unified Model: Exact state and channel score parity          [PASSED]
------------------------------------------------------------------------------
  VALIDATION SUMMARY: 18 / 18 TESTS PASSED (100.0%)
==============================================================================
```

---

## 6. Locked Hardware Parameter Summary

| Parameter | Symbol | Value | Hardware Justification |
|---|---|---|---|
| **Target MCU** | — | `STM32G474RET6` | 170 MHz ARM Cortex-M4F with DSP/FPU |
| **DAC Sample Rate** | $F_s$ | $4.0\text{ MSPS}$ | $T_s = 250\text{ ns}$ (Timer TRGO triggered DMA) |
| **DAC Resolution** | — | $12\text{-bit unsigned}$ | Integer codes $0\text{--}4095$, midscale $2048$ |
| **DAC Hardware Path**| — | `DAC3 CH2 -> OPAMP3 -> PB1` | Unbuffered DAC routed to OPAMP3 High-Speed Follower ($45\text{ V}/\mu\text{s}$) |
| **Pulse Duration** | $T_p$ | $2.0\text{ ms}$ | $N_p = 8000\text{ samples}$ ($16\text{ KB}$ buffer per ping) |
| **Ping Repetition** | $\text{PRI}$ | $20.0\text{ ms}$ | $50\text{ Hz}$ ping rate, $10.0\%$ duty cycle |
| **Profile 1 (`LOW_FREQ`)** | — | $100\text{--}220\text{ kHz}, A=1.0$ | Lowest seawater absorption ($64\text{ dB/km}$); long-range fallback |
| **Profile 2 (`BALANCED`)** | — | $200\text{--}400\text{ kHz}, A=0.7$ | Highest bandwidth ($B=200\text{ kHz}$); best range resolution ($\Delta R = 3.75\text{ mm}$) |
| **Profile 3 (`HIGH_FREQ`)** | — | $350\text{--}500\text{ kHz}, A=0.4$ | Highest theoretical directivity ($1.417\times$); angular resolution mode |
