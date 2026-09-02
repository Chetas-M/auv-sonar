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
| **Pulse Duration** | $T_p$ | $2.0\text{ ms}$ | $N_p = F_s \cdot T_p = 8,000\text{ samples}$. |
| **Pulse Repetition**| $\text{PRI}$ | $20.0\text{ ms}$ | $50\text{ Hz}$ ping repetition rate; max unambiguous acoustic range $\approx 15\text{ m}$. |
| **Adaptive Profiles**| — | Exactly $3$ | Profile 1 (MUDDY), Profile 2 (BALANCED), Profile 3 (CLEAR). |

### [ADAPTIVE] Runtime Parameters (Controlled by Adaptation Logic)
| Parameter | Symbol | Range / States | Selection Mechanism |
|---|---|---|---|
| **Active Profile** | $\text{Profile\_ID}$ | `1 (MUDDY), 2 (BALANCED), 3 (CLEAR)` | Selected via Channel Quality Score $Q$ with hysteresis and debounce. |
| **Transmit Amplitude**| $A$ | $0.40, 0.70, 1.00$ | Normalized scaling: $A=1.0$ (poor channel), $A=0.7$ (moderate), $A=0.4$ (good channel). |

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
| **Battery Rail Voltage** | $V_{\text{bat}}$ | $12.0\text{ V}$ | Assumed subsea battery bus voltage for current calculation. |
| **Hypothetical Pack** | $E_{\text{bat}}$ | $99.0\text{ Wh}$ | Standard carry-on compliant battery pack for transmitter-only load model. |

### [DERIVED] Analytically Computed Values
| Parameter | Expression | Value | Significance |
|---|---|---|---|
| **Sample Count** | $N_p = F_s \cdot T_p$ | $8,000\text{ samples}$ | Fixed buffer length per ping table. |
| **Buffer Memory** | $N_p \times 2\text{ bytes}$ | $16,000\text{ bytes}$ | $15.62\text{ KB}$ per profile as `uint16_t`. |
| **Duty Cycle** | $D = T_p / \text{PRI}$ | $10.0\%$ | $2.0\text{ ms} / 20.0\text{ ms} = 0.10$. |
| **Average Power** | $P_{\text{avg}} = P_{\text{act}}D + P_{\text{idle}}(1-D)$ | $0.540\text{ W}$ | Nominal average power at $10\%$ duty cycle and $A=1.0$. |
| **SRAM Load** | $\text{LUT} / 128\text{ KB}$ | $12.5\%$ | Memory footprint in STM32G474 SRAM. |
| **Flash Load** | $3 \times \text{LUT} / 512\text{ KB}$ | $9.37\%$ | Storage for all 3 profiles in STM32G474 Flash. |

---

## 2. Three Fixed Transmission Profiles

```
        Profile 1: MUDDY                  Profile 2: BALANCED                 Profile 3: CLEAR
        (High Turbidity)                  (Nominal Default)                   (Clear Pelagic)
  [==== 100 - 220 kHz ====]             [==== 200 - 400 kHz ====]           [==== 350 - 500 kHz ====]
    fc = 160 kHz, B = 120 kHz             fc = 300 kHz, B = 200 kHz           fc = 425 kHz, B = 150 kHz
  Penetrates sediment clouds            Balanced range & resolution         Fine range resolution (~5mm)
```

1. **Profile 1 (MUDDY / DEGRADED CHANNEL)**:
   - Sweep: $100.0\text{ kHz} \to 220.0\text{ kHz}$ ($f_c = 160.0\text{ kHz}, B = 120.0\text{ kHz}$)
   - Purpose: Mitigates acoustic scattering from suspended particulate and sediment plumes.
2. **Profile 2 (BALANCED / DEFAULT CHANNEL)**:
   - Sweep: $200.0\text{ kHz} \to 400.0\text{ kHz}$ ($f_c = 300.0\text{ kHz}, B = 200.0\text{ kHz}$)
   - Purpose: Nominal default operating mode balancing absorption loss and spatial resolution.
3. **Profile 3 (CLEAR / HIGH-RESOLUTION CHANNEL)**:
   - Sweep: $350.0\text{ kHz} \to 500.0\text{ kHz}$ ($f_c = 425.0\text{ kHz}, B = 150.0\text{ kHz}$)
   - Purpose: High-frequency mode providing fine spatial resolution ($\Delta R \approx \frac{c}{2B} \approx 5\text{ mm}$) in clear water.

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
             Q = 1.0 - (0.50*P_turb + 0.25*P_attn + 0.25*P_noise)
                                      ↓
             Threshold Decision with 10% Schmitt Hysteresis
         - To enter CLEAR: Q >= 0.75; to leave CLEAR: Q < 0.65
         - To enter MUDDY: Q <= 0.30; to leave MUDDY: Q > 0.40
         - Deadbands prevent profile flickering from sensor noise
                                      ↓
                  Debounce Persistence Filter (N = 2)
       Requires condition to persist for 2 consecutive cycles
                                      ↓
                 Atomic Ping-Boundary Profile Latching
             Committed strictly at the start of the next PRI
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

% 2. Run master simulation (generates all 10 plots and C headers)
run_simulation
```

### Running the 15-Point Automated Validation Suite
```matlab
% Runs all 15 DSP, quantization, hysteresis, debounce, and round-trip tests
run_validation_suite
```

---

## 5. Ten Generated Validation Figures

All generated plots are saved to `outputs_matlab/plots/`:

1. **`01_time_domain_waveform.png`**: Full 2.0 ms pulse showing Hann envelope tapering.
2. **`02_zoomed_waveform_section.png`**: Microscopic 80 µs view showing 12-bit DAC stair-step discretization tracking continuous reference.
3. **`03_instantaneous_frequency.png`**: Exact linear sweep $f(t) = f_0 + k\cdot t$ tracking $200 \to 400\text{ kHz}$.
4. **`04_fft_spectrum.png`**: Power spectral density verifying in-band passband and $>50\text{ dB}$ stopband rejection.
5. **`05_spectrogram.png`**: STFT spectrogram showing straight time-frequency energy ridge ($100\text{ MHz/s}$ slope).
6. **`06_window_comparison.png`**: Overlay comparing Hann windowed pulse against rectangular pulse, proving suppression of sidelobe splatter.
7. **`07_quantization_error.png`**: Quantization error residuals strictly bounded within $[-0.5, +0.5]\text{ LSB}$.
8. **`08_dac_code_histogram.png`**: 12-bit code distribution verifying midscale centering at code $2048$.
9. **`09_profile_comparison.png`**: Side-by-side spectral overlay of Muddy, Balanced, and Clear bands.
10. **`10_dynamic_simulation_timeline.png`**: 150-ping ($3.0\text{ s}$) mission timeline showing noisy turbidity input, quality score $Q$, raw candidate vs latched active profile, hysteresis stability, and average power throttling.

---

## 6. Fifteen Automated Engineering Checks (`run_validation_suite.m`)

| # | Validation Check | Target Specification | Measured Result | Status |
|---|---|---|---|---|
| **01** | **Sample Count** | $N_p = 8,000\text{ samples}$ | Exactly $8,000$ | **PASSED** |
| **02** | **Pulse Duration** | $T_p = 2.0\text{ ms}$ | $2.000\text{ ms}$ | **PASSED** |
| **03** | **DAC Range** | $0 \le \text{code} \le 4095$ | No overflow/underflow | **PASSED** |
| **04** | **Midscale Correctness**| $\text{code} = 2048$ at $0\text{ V AC}$ | Exactly $2048$ | **PASSED** |
| **05** | **Hann Endpoints** | $w[0] = 0, w[N-1] = 0$ | $< 10^{-6}$ | **PASSED** |
| **06** | **Chirp Slope** | $k = 100.0\text{ MHz/s}$ ($\text{err} < 0.1\%$) | Error $= 0.0000\%$ | **PASSED** |
| **07** | **Start Frequency** | $f_0 = 200.0\text{ kHz}$ ($\text{err} < 0.1\%$) | Error $= 0.0062\%$ | **PASSED** |
| **08** | **End Frequency** | $f_1 = 400.0\text{ kHz}$ ($\text{err} < 0.1\%$) | Error $= 0.0031\%$ | **PASSED** |
| **09** | **FFT Band-Energy** | $\ge 99.0\%$ in-band | $100.0000\%$ in-band | **PASSED** |
| **10** | **Hysteresis Stability**| Suppresses deadband noise | Zero flicker in deadband | **PASSED** |
| **11** | **Debounce Persistence**| $N=2$ cycles required | 1-cycle spike rejected | **PASSED** |
| **12** | **Ping-Boundary Latch** | Changes occur at PRI ($20\text{ ms}$) | Atomic PRI update | **PASSED** |
| **13** | **Power Model** | $P_{\text{avg}} = P_{\text{act}}D + P_{\text{idle}}(1-D)$| Exact analytical match | **PASSED** |
| **14** | **C Header Integrity** | Valid header guards and macros | Valid ANSI C generated | **PASSED** |
| **15** | **Bit-Exact Round-Trip**| C parsed array == MATLAB array | 8,000 / 8,000 matched | **PASSED** |

---

## 7. Firmware C Header Export

Firmware-ready prototype headers aligned for DMA burst transfers are exported to `outputs_matlab/headers/`:
- `chirp_muddy.h` ($100\text{–}220\text{ kHz}$, 8,000 samples, 16 KB)
- `chirp_balanced.h` ($200\text{–}400\text{ kHz}$, 8,000 samples, 16 KB)
- `chirp_clear.h` ($350\text{–}500\text{ kHz}$, 8,000 samples, 16 KB)
- `sonar_profiles.h` (Master registry with `SonarProfileDescriptor_t` lookup structs)

---

## 8. Embedded Hardware Bring-Up Protocol (STM32G474)

1. **Timer TRGO**: Configure TIM6 (or TIM2) at $170\text{ MHz}$ SYSCLK to generate a $4.0\text{ MHz}$ update trigger ($170 / 42.5$).
2. **High-Speed DAC Configuration**: Set STM32 DAC to **unbuffered mode** (`DAC_OUTPUTBUFFER_DISABLE`) to avoid slew-rate limitation.
3. **External Buffer & Reconstruction Filter**: Route DAC pin to a high-speed op-amp (e.g. OPA350 or ADA4807) configured as an active low-pass reconstruction filter ($f_c \approx 750\text{ kHz}$) before driving the power amplifier.
4. **Bench Measurement**: Probe the analog output with an oscilloscope ($>50\text{ MSPS}$ acquisition rate) and spectrum analyzer to measure physical rise time, THD, and harmonic suppression before water tank testing.
