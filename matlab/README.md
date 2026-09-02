# SIH Problem 26058: Low-Power, Real-Time Adaptive Software-Defined Sonar Transmitter Payload for Autonomous Underwater Vehicles (AUVs)

## MATLAB Digital Twin Simulation Architecture

This directory contains the official MATLAB-based digital twin simulator for the transmitter payload of an adaptive software-defined sonar targeting the **STMicroelectronics STM32G474** microcontroller.

---

> [!IMPORTANT]
> **Honest Engineering Scope & Limitation Statement**:
> This simulation validates waveform generation, environmental scenario mapping, channel quality estimation, hysteresis-backed profile adaptation, 12-bit DAC quantization, DMA buffer sizing, and estimated duty-cycle power dissipation.
>
> It **DOES NOT** claim to validate:
> - Real underwater acoustic performance
> - Actual piezoelectric transducer impedance or resonance
> - Acoustic propagation measurements in physical water
> - Power amplifier (PA) thermal stability or analog settling
> - Actual hardware current consumption
> - Receiver hardware or hydrophone acoustic feedback
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
| **Active Profile** | $\text{Profile\_ID}$ | `1 (LOW_FREQUENCY), 2 (BALANCED), 3 (HIGH_FREQUENCY)` | Selected via Channel Quality Score $Q$ with directional Schmitt hysteresis and debounce. |
| **Transmit Amplitude**| $A$ | $0.40, 0.70, 1.00$ | Normalized scaling: $A=1.0$ (Low Freq), $A=0.7$ (Balanced), $A=0.4$ (High Freq). |

### [ENVIRONMENT] Environmental Scenario Inputs (Simulation Variables)
| Parameter | Symbol | Baseline | Role in Simulation |
|---|---|---|---|
| **Depth** | $D$ | $50.0\text{ m}$ | Inputs to sound speed and hydrostatic pressure absorption equations. |
| **Temperature** | $T$ | $20.0^\circ\text{C}$ | Influences seawater sound speed and chemical relaxation absorption frequencies. |
| **Salinity** | $S$ | $35.0\text{ PSU}$ | Standard seawater salinity scale. |
| **Turbidity** | $\text{turb}$ | $0 \to 100\text{ NTU}$ | Drives simulated particulate acoustic scattering loss ($\propto f^2$). |
| **Ambient Noise**| $N_{\text{amb}}$| $55.0\text{ dB}$ | Background acoustic noise power spectral density in simulation. |

### [ASSUMPTION] Simulation Model Assumptions (Unmeasured Estimates)
| Parameter | Symbol | Assumed Value | Purpose & Limitation |
|---|---|---|---|
| **Active Transmit Power** | $P_{\text{active}}$ | $5.0\text{ W}$ | Model assumption for PA + DAC + MCU active state. Unmeasured bench estimate. |
| **Idle Power** | $P_{\text{idle}}$ | $0.045\text{ W}$ | Model assumption for low-power sleep state between pings ($45\text{ mW}$). |
| **Analog Static Electronics**| $P_{\text{elec}}$ | $0.300\text{ W}$ | Base electronics power when transmitter is enabled. |
| **Battery Rail Voltage** | $V_{\text{bat}}$ | $12.0\text{ V}$ | Assumed subsea battery bus voltage for current calculation. |
| **Hypothetical Pack** | $E_{\text{bat}}$ | $99.0\text{ Wh}$ | Standard carry-on compliant battery pack for transmitter-only load model. |

### [DERIVED] Analytically Computed Values
| Parameter | Expression | Value | Significance |
|---|---|---|---|
| **Sample Count** | $N_p = F_s \cdot T_p$ | $8,000\text{ samples}$ | Fixed buffer length per ping table. |
| **Buffer Memory** | $N_p \times 2\text{ bytes}$ | $16,000\text{ bytes}$ | $15.625\text{ KB}$ per profile as `uint16_t`. |
| **Duty Cycle** | $D = T_p / \text{PRI}$ | $10.0\%$ | $2.0\text{ ms} / 20.0\text{ ms} = 0.10$. |
| **Average Power** | $P_{\text{avg}} = P_{\text{act}}D + P_{\text{idle}}(1-D)$ | $0.540\text{ W}$ | Nominal average power at $10\%$ duty cycle and $A=1.0$. |
| **SRAM Load** | $\text{LUT} / 128\text{ KB}$ | $12.5\%$ | Memory footprint in STM32G474 SRAM. |
| **Flash Load** | $3 \times \text{LUT} / 512\text{ KB}$ | $9.37\%$ | Storage for all 3 profiles in STM32G474 Flash. |

---

## 2. Three Canonical Transmission Profiles

```
      Profile 1: LOW_FREQUENCY          Profile 2: BALANCED             Profile 3: HIGH_FREQUENCY
      (High Particulate/Scattering)     (Default Operating Mode)        (High Beam Directivity)
  [======== 100 - 220 kHz ========]   [======== 200 - 400 kHz ========]   [======== 350 - 500 kHz ========]
     fc = 160 kHz, B = 120 kHz           fc = 300 kHz, B = 200 kHz           fc = 425 kHz, B = 150 kHz
     Penetrates turbidity plumes        Best Range Resolution (3.75 mm)     Narrow Acoustic Beam Directivity
```

### Critical Acoustic Distinction: Range Resolution vs. Beam Directivity
- **Range Resolution ($\Delta R = \frac{c}{2B}$)**:
  - Theoretical range resolution is governed strictly by the **sweep bandwidth $B$**, assuming matched-filter compression.
  - **Profile 2 (`BALANCED`)** possesses the widest bandwidth ($B = 200\text{ kHz}$), yielding an idealized range resolution of **$\Delta R = \frac{1500}{2 \times 200\times 10^3} = 3.75\text{ mm}$**.
  - **Profile 3 (`HIGH_FREQUENCY`)** has $B = 150\text{ kHz}$, yielding $\Delta R = \frac{1500}{2 \times 150\times 10^3} = 5.00\text{ mm}$.
- **Beam Directivity ($\theta \propto \frac{\lambda}{D} = \frac{c}{f \cdot D}$)**:
  - **Profile 3 (`HIGH_FREQUENCY`)** operates at the highest frequencies ($350\text{–}500\text{ kHz}$, $\lambda \approx 3.0\text{–}4.3\text{ mm}$), providing a significantly tighter acoustic beam pattern and reduced angular beamwidth for a fixed physical transducer aperture diameter $D$.
  - Therefore, `HIGH_FREQUENCY` is selected for **high spatial angular directivity**, not because it has superior range resolution over `BALANCED`.

---

## 3. Explainable Adaptive Decision Architecture

```
Environmental Scenario Inputs (Turbidity, Depth, Temp, Salinity, Ambient Noise)
                                      ↓
                   Simplified Acoustic Channel Model
   - Sound speed c(T,S,D) via Mackenzie (1981) formula
   - High-frequency chemical absorption alpha_chem(f) via Ainslie-McColm (1998)
   - Particulate scattering loss alpha_turb(f, turb)
                                      ↓
              Deterministic Channel Quality Score Q in [0, 1]
              Q = 0.50*q_env + 0.25*q_attn + 0.25*q_noise
                                      ↓
            Directional Schmitt-Trigger Hysteresis State Machine
        - In BALANCED:  Q >= 0.75 -> HIGH_FREQ;  Q <= 0.30 -> LOW_FREQ
        - In HIGH_FREQ: Q < 0.65  -> BALANCED;   Q <= 0.30 -> LOW_FREQ
        - In LOW_FREQ:  Q > 0.40  -> BALANCED;   Q >= 0.75 -> HIGH_FREQ
        - Deadbands [0.30, 0.40] and [0.65, 0.75] prevent profile flickering
                                      ↓
                   Debounce Persistence Filter (N = 2)
       Candidate condition must persist for 2 consecutive evaluations
                                      ↓
                  Atomic Ping-Boundary Profile Latching
        Active profile changes strictly at the start of the next PRI
                                      ↓
               Synthesized 12-Bit DAC Output (0 to 4095)
```

---

## 4. How to Run the Simulation in MATLAB

### Prerequisites
- MATLAB R2020a or later (also compatible with GNU Octave 7.0+).
- Signal Processing Toolbox (recommended for `spectrogram`, fallback provided).

### Running the Complete Digital Twin Simulation
Open MATLAB, navigate to `d:\AUV sonar\matlab`, and execute:

```matlab
% 1. Add matlab directory to path
addpath(pwd);

% 2. Run master simulation (generates all 13 plots, memory budget, power model, headers)
run_simulation
```

### Running the 23-Point Automated Validation Suite
```matlab
% Runs all 23 DSP, window, quantization, controller, ping-state, and export tests
run_validation_suite
```

---

## 5. Thirteen Generated Validation Figures (`outputs_matlab/plots/`)

1. **`01_time_domain_waveform.png`**: Time-domain waveforms for all 3 profiles showing smooth Hann envelope tapering.
2. **`02_zoomed_waveform_section.png`**: Microscopic 80 µs view showing 12-bit DAC stair-step discretization tracking continuous reference.
3. **`03_instantaneous_frequency.png`**: Linear frequency modulation trajectory tracking $200 \to 400\text{ kHz}$ ($k = 100\text{ MHz/s}$).
4. **`04_fft_spectrum.png`**: Power spectral density verifying in-band passband and $>50\text{ dB}$ stopband rejection.
5. **`05_spectrogram.png`**: STFT spectrogram showing straight time-frequency energy ridge ($100\text{ MHz/s}$ slope).
6. **`06_dac_quantization_error.png`**: Quantization error residuals strictly bounded within $[-0.5, +0.5]\text{ LSB}$.
7. **`07_dac_code_histogram.png`**: 12-bit code distribution verifying midscale centering at code $2048$.
8. **`08_profile_comparison.png`**: Spectral overlay of all three bands (`LOW_FREQUENCY`, `BALANCED`, `HIGH_FREQUENCY`).
9. **`09_channel_quality_timeline.png`**: Predicted Channel Quality Score $Q(t)$ plotted against directional hysteresis thresholds.
10. **`10_candidate_profile_timeline.png`**: Raw candidate profile timeline driven by instantaneous channel score.
11. **`11_active_profile_timeline.png`**: Committed active profile timeline showing rock-solid stability after debounce.
12. **`12_hysteresis_debounce_demo.png`**: Detailed view demonstrating deadband hysteresis and $N=2$ debounce filtering during a sediment plume event.
13. **`13_estimated_power_summary.png`**: Transmitter payload average power timeline across mission and pulse duration sensitivity analysis ($1\text{ ms}, 2\text{ ms}, 3\text{ ms}$).

---

## 6. Twenty-Three Automated Engineering Checks (`run_validation_suite.m`)

| # | Validation Check | Target Specification | Measured Result | Status |
|---|---|---|---|---|
| **01** | **Sample Count** | $N_p = 8,000\text{ samples}$ | Exactly $8,000$ | **PASSED** |
| **02** | **Pulse Duration** | $T_p = 2.0\text{ ms}$ | $2.000\text{ ms}$ | **PASSED** |
| **03** | **Chirp Slope** | $k = 100.0\text{ MHz/s}$ ($\text{err} < 0.1\%$) | Error $= 0.0000\%$ | **PASSED** |
| **04** | **Start Frequency** | $f_0 = 200.0\text{ kHz}$ ($\text{err} < 0.1\%$) | Error $= 0.0062\%$ | **PASSED** |
| **05** | **End Frequency** | $f_1 = 400.0\text{ kHz}$ ($\text{err} < 0.1\%$) | Error $= 0.0031\%$ | **PASSED** |
| **06** | **No NaN Values** | Waveform contains no NaN | 0 NaN elements | **PASSED** |
| **07** | **No Inf Values** | Waveform contains no Inf | 0 Inf elements | **PASSED** |
| **08** | **Hann Window Length** | $N = 8,000\text{ samples}$ | Exactly $8,000$ | **PASSED** |
| **09** | **Window Application**| $w[0] = 0, w[N-1] = 0$, $x[0]=0, x[N-1]=0$ | $< 10^{-6}$ | **PASSED** |
| **10** | **DAC Code Range** | $0 \le \text{code} \le 4095$ | No overflow/underflow | **PASSED** |
| **11** | **DAC Data Type** | `uint16` for DMA peripheral | `uint16` | **PASSED** |
| **12** | **Midscale Correctness**| $\text{code} = 2048$ at $0\text{ V AC}$ swing | Exactly $2048$ | **PASSED** |
| **13** | **Quantization Error** | $\text{Max} \le 0.5\text{ LSB}, \text{SQNR} \ge 68\text{ dB}$ | $0.500\text{ LSB}, 69.67\text{ dB}$ | **PASSED** |
| **14** | **Candidate Selection**| $Q=0.20 \to \text{LOW}, Q=0.85 \to \text{HIGH}$| Exact state mapping | **PASSED** |
| **15** | **Hysteresis Stability**| Suppresses noise inside deadband | Zero flicker in deadband | **PASSED** |
| **16** | **Single Transient** | 1-cycle spike does not switch profile | Retained current profile | **PASSED** |
| **17** | **Two Consecutive** | 2 consecutive cycles commit change | Profile committed | **PASSED** |
| **18** | **Candidate Reset** | Counter resets when input reverts | Counter reset to 0 | **PASSED** |
| **19** | **Active Frozen in Ping**| Active profile unchanged during transmit | Strictly latched | **PASSED** |
| **20** | **Pending Activates at PRI**| Pending switches at PRI boundary | Atomic PRI boundary update | **PASSED** |
| **21** | **C Headers Generated**| All 4 headers exist with valid guards | All 4 files verified | **PASSED** |
| **22** | **Sample Metadata** | Sample count and byte size macros match | Exact macro match | **PASSED** |
| **23** | **Bit-Exact Round-Trip**| Parsed C table == Synthesized table | 8,000 / 8,000 bit-exact | **PASSED** |

---

## 7. Firmware C Header Export

Firmware-ready prototype headers aligned for DMA burst transfers are exported to `outputs_matlab/headers/`:
- `chirp_low_frequency.h` ($100\text{–}220\text{ kHz}$, 8,000 samples, 16 KB)
- `chirp_balanced.h` ($200\text{–}400\text{ kHz}$, 8,000 samples, 16 KB)
- `chirp_high_frequency.h` ($350\text{–}500\text{ kHz}$, 8,000 samples, 16 KB)
- `sonar_profiles.h` (Master registry with `SonarProfileDescriptor_t` lookup structs)

---

## 8. Embedded Hardware Bring-Up Protocol (STM32G474)

1. **Timer TRGO**: Configure TIM6 (or TIM2) at $170\text{ MHz}$ SYSCLK to generate a $4.0\text{ MHz}$ update trigger ($170 / 42.5$).
2. **High-Speed DAC Configuration**: Set STM32 DAC to **unbuffered mode** (`DAC_OUTPUTBUFFER_DISABLE`) to avoid slew-rate limitation.
3. **External Buffer & Reconstruction Filter**: Route DAC pin to a high-speed op-amp (e.g. OPA350 or ADA4807) configured as an active low-pass reconstruction filter ($f_c \approx 750\text{ kHz}$) before driving the power amplifier.
4. **Bench Measurement**: Probe the analog output with an oscilloscope ($>50\text{ MSPS}$ acquisition rate) and spectrum analyzer to measure physical rise time, THD, and harmonic suppression before water tank testing.
