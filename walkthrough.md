# Engineering Walkthrough: AUV Adaptive Sonar Transmitter Digital Twin

A Python-based engineering digital twin simulator for the transmitter payload of a low-power adaptive software-defined sonar designed for Autonomous Underwater Vehicles (AUVs).

---

> [!IMPORTANT]
> **Standard Engineering Limitation Statement**:
> This simulator validates waveform generation, adaptation logic, quantization, DMA buffer sizing, and estimated duty-cycle power. It does not validate transducer impedance, acoustic propagation, real environmental sensing, analog settling, amplifier stability, or actual current draw.

---

## 1. System Architecture & Technical Specifications

```
                      +---------------------------------------+
                      |       Simulated Analog Inputs         |
                      | 3 Potentiometers: Turbidity, Range,   |
                      | Target Strength (Emulates RX SNR)     |
                      +---------------------------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |       Hysteresis State Machine        |
                      |     10% Deadband & Debounce (N=2)     |
                      +---------------------------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |         Atomic Ping Boundary          |
                      |      Latch (PRI = 20.0 ms, 50 Hz)     |
                      +---------------------------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |        LFM Phase Integration          |
                      |        & Hann Window Tapering         |
                      +---------------------------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |      12-Bit DAC Quantization          |
                      |    (4.0 MSPS, Code: 0 to 4095)        |
                      +---------------------------------------+
                                          |
                   +----------------------+----------------------+
                   |                                             |
                   v                                             v
    +-----------------------------+               +-----------------------------+
    | Firmware-Ready Prototype    |               |   Duty-Cycle Power Model    |
    | C Headers (uint16_t tables) |               | (P_avg ~ 0.54 W @ 10% Duty) |
    +-----------------------------+               +-----------------------------+
```

### Profile Specifications (at $F_s = 4.0\text{ MSPS}$, $T = 2.0\text{ ms}$)

| Parameter | Muddy Profile | Balanced Profile (Default) | Clear Profile |
|---|---|---|---|
| **Frequency Sweep** | $100.0 \to 220.0\text{ kHz}$ | $200.0 \to 400.0\text{ kHz}$ | $350.0 \to 500.0\text{ kHz}$ |
| **Center Freq ($f_c$)** | $160.0\text{ kHz}$ | $300.0\text{ kHz}$ | $425.0\text{ kHz}$ |
| **Bandwidth ($B$)** | $120.0\text{ kHz}$ | $200.0\text{ kHz}$ | $150.0\text{ kHz}$ |
| **Acoustic Rationale** | Lower attenuation through suspended sediment | Optimal range vs resolution balance | Fine spatial resolution ($\Delta R \approx 5\text{ mm}$) |
| **Sample Count** | $8,000\text{ samples}$ | $8,000\text{ samples}$ | $8,000\text{ samples}$ |
| **Memory Footprint** | $16.0\text{ KB}$ ($15.62\text{ KiB}$) | $16.0\text{ KB}$ ($15.62\text{ KiB}$) | $16.0\text{ KB}$ ($15.62\text{ KiB}$) |
| **STM32 SRAM Load** | $12.5\%$ of $128\text{ KB}$ | $12.5\%$ of $128\text{ KB}$ | $12.5\%$ of $128\text{ KB}$ |
| **Flash Load (All 3)** | \multicolumn{3}{c|}{$48.0\text{ KB}$ ($9.37\%$ of $512\text{ KB}$ Flash on STM32G474)} |
| **Simulated SQNR** | $69.67\text{ dB}$ | $69.67\text{ dB}$ | $69.70\text{ dB}$ |

---

## 2. Signal Validation & Visualizations

````carousel
![Single Pulse Analysis: Time-domain, DAC zoom, FFT spectrum, and Spectrogram](C:/Users/cheta/.gemini/antigravity-ide/brain/413f957b-735a-437e-bc44-0ff65895d84b/plots/single_pulse_analysis.png)
<!-- slide -->
![Quantization Analysis: Error time series, LSB histogram, residual mV, and SQNR card](C:/Users/cheta/.gemini/antigravity-ide/brain/413f957b-735a-437e-bc44-0ff65895d84b/plots/quantization_analysis.png)
<!-- slide -->
![Profile Comparison: Time domain and spectral overlay across Muddy, Balanced, and Clear bands](C:/Users/cheta/.gemini/antigravity-ide/brain/413f957b-735a-437e-bc44-0ff65895d84b/plots/profile_comparison.png)
<!-- slide -->
![Dynamic Simulation: 150-ping timeline showing potentiometer noise rejection, hysteresis, and power](C:/Users/cheta/.gemini/antigravity-ide/brain/413f957b-735a-437e-bc44-0ff65895d84b/plots/dynamic_simulation_timeline.png)
````

### Key Engineering Observations:
- **Phase Continuity**: Analytical phase integration ensures continuous frequency transitions across the chirp pulse.
- **Spectral Discontinuity Mitigation**: Hann windowing smoothly tapers pulse start/end to suppress edge transients and reduce out-of-band sidelobes in the digital simulation; physical analog harmonic attenuation must be verified on bench oscilloscope/spectrum analyzer.
- **Linear Modulation Slope**: Spectrogram confirms uniform linear frequency modulation trajectory across the pulse duration.
- **Strict Quantization Bounds**: Quantization error is bounded within $\pm 0.5\text{ LSB}$ ($\pm 0.403\text{ mV}$ on $3.3\text{V}$ rail) with simulated SQNR of $69.67\text{ dB}$.
- **Hysteresis Noise Immunity**: In the dynamic simulation timeline, random potentiometer noise ($\sigma = 0.02$) is rejected by the $10\%$ hysteresis deadband; profile switching occurs strictly at the onset of subsequent pings. The target-strength input emulates a future receiver/SNR feedback signal.

---

## 3. Power Model & Endurance Estimations

> [!WARNING]
> **Payload-Only Scope for Endurance**:
> The endurance figures below represent **only the modeled transmitter payload load alone** against a hypothetical $99\text{ Wh}$ battery pack. They **do NOT represent full AUV mission life**, which is dominated by thruster propulsion, navigation computers, INS/DVL, cameras, and comms.

Equations applied:
$$\text{Duty Cycle} (D) = \frac{T_{\text{pulse}}}{\text{PRI}} = \frac{2.0\text{ ms}}{20.0\text{ ms}} = 10.0\%$$
$$P_{\text{avg}} = P_{\text{active}} \cdot D + P_{\text{idle}} \cdot (1 - D) = 5.0\text{ W} \times 0.10 + 0.045\text{ W} \times 0.90 = 0.540\text{ W}$$
$$I_{\text{avg}} = \frac{P_{\text{avg}}}{V_{\text{bat}}} = \frac{0.540\text{ W}}{12.0\text{ V}} \approx 45.0\text{ mA}$$

| Duration Mode | Duration | PRI | Duty Cycle | Average Power | Average Current (12V) | TX-Only Endurance (Hypothetical 99 Wh Pack) |
|---|---|---|---|---|---|---|
| **Short (Near-Field)** | $1.0\text{ ms}$ | $20.0\text{ ms}$ | $5.0\%$ | $0.293\text{ W}$ | $24.4\text{ mA}$ | **$338.2\text{ hours}$ (TX load alone)** |
| **Medium (Nominal)** | $2.0\text{ ms}$ | $20.0\text{ ms}$ | $10.0\%$ | $0.540\text{ W}$ | $45.0\text{ mA}$ | **$183.2\text{ hours}$ (TX load alone)** |
| **Long (Far-Range)** | $3.0\text{ ms}$ | $20.0\text{ ms}$ | $15.0\%$ | $0.788\text{ W}$ | $65.7\text{ mA}$ | **$125.6\text{ hours}$ (TX load alone)** |
| **Strong Target Emulation ($A=0.4$)** | $2.0\text{ ms}$ | $20.0\text{ ms}$ | $10.0\%$ | $0.146\text{ W}$ | $12.1\text{ mA}$ | **$679.5\text{ hours}$ (TX load alone)** |

---

## 4. Firmware-Ready Prototype C Headers

The simulator generated firmware-ready prototype C headers aligned for DMA playback and documented for STM32 firmware bring-up in `outputs/headers/`:

1. [chirp_muddy.h](file:///d:/AUV%20sonar/outputs/headers/chirp_muddy.h): 8,000 samples for $100\text{–}220\text{ kHz}$ chirp table (`CHIRP_MUDDY_LUT`).
2. [chirp_balanced.h](file:///d:/AUV%20sonar/outputs/headers/chirp_balanced.h): 8,000 samples for $200\text{–}400\text{ kHz}$ chirp table (`CHIRP_BALANCED_LUT`).
3. [chirp_clear.h](file:///d:/AUV%20sonar/outputs/headers/chirp_clear.h): 8,000 samples for $350\text{–}500\text{ kHz}$ chirp table (`CHIRP_CLEAR_LUT`).
4. [sonar_profiles.h](file:///d:/AUV%20sonar/outputs/headers/sonar_profiles.h): Master registration table with `SonarProfileDescriptor_t` structs for direct lookup by profile ID.

### Header Snippet (`chirp_balanced.h`)
```c
/**
 * @file    chirp_balanced.h
 * @brief   Firmware-Ready Prototype 12-bit DAC Lookup Table for BALANCED Sonar Chirp
 * @target  STM32G474 (Timer TRGO -> DMA -> high-speed STM32G4 DAC path, with exact DAC instance/pin verified during board bring-up)
 * ...
 * @note Prototype header for firmware bring-up. In STM32 firmware, configure DMA
 *       in Circular or Normal mode with half-word (16-bit) memory and peripheral sizes.
 *       At 4.0 MSPS, external analog buffering and high-speed DAC configuration must be validated on scope.
 */

#define CHIRP_BALANCED_LUT_SAMPLE_RATE_HZ  (4000000UL)
#define CHIRP_BALANCED_LUT_F_START_HZ      (200000UL)
#define CHIRP_BALANCED_LUT_F_END_HZ        (400000UL)
#define CHIRP_BALANCED_LUT_DURATION_US     (2000UL)
#define CHIRP_BALANCED_LUT_SAMPLE_COUNT    (8000U)
#define CHIRP_BALANCED_LUT_SIZE_BYTES      (16000U)

DMA_ALIGN const uint16_t CHIRP_BALANCED_LUT[8000] = {
    0x0800, 0x0800, 0x0800, 0x0800, 0x0800, 0x07FF, ...
};
```

---

## 5. Automated Test Suite Results

The unit test suite in [test_simulator.py](file:///d:/AUV%20sonar/tests/test_simulator.py) verified all 13 mathematical, algorithmic, and round-trip tests:

```
Ran 13 tests in 1.568s

OK:
[PASSED] test_sample_count_and_bounds: 8,000 samples exact match; Hann endpoints = 0
[PASSED] test_amplitude_scaling: Amplitude factor scaling strictly observed
[PASSED] test_dac_code_range: Codes within [0, 4095]; uint16 dtype
[PASSED] test_zero_signal_midscale: Midscale = 2048 at 0 V AC swing
[PASSED] test_hysteresis_deadband_stability: 10% deadband suppresses jitter
[PASSED] test_debounce_persistence: Requires N consecutive pings before committing state
[PASSED] test_ping_boundary_controller: Atomic state latching strictly at PRI boundary
[PASSED] test_power_calculation: Analytical duty cycle & power exact match
[PASSED] test_export_file_content: Valid C syntax, header guards, and array size
[PASSED] test_instantaneous_frequency_sweep: Hilbert phase derivative matches slope within 0.0000%
[PASSED] test_fft_band_energy_concentration: >99.999% spectral energy concentrated in-band
[PASSED] test_spectrogram_ridge_linearity: Spectrogram peak ridge R^2 = 0.9901
[PASSED] test_c_header_roundtrip_integrity: Bit-exact match between C header and Python DAC array
```

---

## 6. Five-Point Verification Results & Hardware Bring-Up Protocol

```text
================================================================================
SIMULATION STATUS:
Simulation correctness level: algorithmically credible, physically unverified.
================================================================================
```

| Validation Check | Target Metric | Measured Value | Status |
|---|---|---|---|
| **Check 1: Instantaneous Frequency** | Slope error $<0.1\%$, monotonic | Slope $= 100.00\text{ MHz/s}$ (Error: $0.0000\%$) | **PASSED** |
| **Check 2: Band-Energy Concentration** | $\ge 99.0\%$ energy in-band | $100.0000\%$ in-band (leakage $< 0.0001\%$) | **PASSED** |
| **Check 3: Spectrogram Ridge Linearity**| $R^2 \ge 0.98$, slope error $<5\%$ | $R^2 = 0.9901$ (Slope error: $0.57\%$) | **PASSED** |
| **Check 4: Header Round-Trip Test** | Bit-exact uint16 parse match | $8,000 / 8,000$ matched (Max Error: $0\text{ LSB}$) | **PASSED** |
| **Check 5: Hardware Feasibility Test** | Scope/FFT & INA219 bench test | Documented bring-up protocol for STM32G4 | **DEFINED** |

---

## 7. SIH Problem 26058: MATLAB Digital Twin Architecture Delivery

In accordance with SIH Problem 26058 specifications, a complete, standalone MATLAB simulation architecture has been constructed in [`d:\AUV sonar\matlab/`](file:///d:/AUV%20sonar/matlab/README.md):

```
d:\AUV sonar\matlab/
├── config_sonar.m            # Single Source of Truth parameter configuration
├── profile_definitions.m     # Struct definitions for Muddy, Balanced, and Clear profiles
├── generate_lfm_chirp.m      # LFM phase integration & Hann window synthesis
├── channel_model.m           # Environmental model (Mackenzie c, Ainslie-McColm alpha) & Score Q
├── adaptive_controller.m     # Schmitt-trigger hysteresis & N=2 debounce state machine
├── dac_quantize.m            # 12-bit unsigned DAC quantization model & SQNR metrics
├── power_model.m             # Duty-cycle average power estimator & battery endurance
├── export_c_headers.m        # Prototype C header exporter for STM32 bring-up
├── run_validation_suite.m    # Automated 15-point engineering validation test suite
├── run_simulation.m          # Master simulation runner generating all 10 required plots
└── README.md                 # Complete engineering documentation & classification table
```

### Parameter Categorization Table (MATLAB)
- **[FIXED]**: $F_s = 4.0\text{ MHz}$, $\text{DAC\_bits} = 12$, $T_p = 2.0\text{ ms}$, $\text{PRI} = 20.0\text{ ms}$, LFM Chirp, Hann Window, STM32G474.
- **[ADAPTIVE]**: $\text{Profile\_ID} \in \{1, 2, 3\}$, Amplitude $A \in \{0.40, 0.70, 1.00\}$.
- **[ENVIRONMENT]**: Depth ($50\text{ m}$), Temp ($20^\circ\text{C}$), Salinity ($35\text{ PSU}$), Turbidity ($0\text{–}100\text{ NTU}$), Ambient Noise ($55\text{ dB}$).
- **[ASSUMPTION]**: $P_{\text{active}} = 5.0\text{ W}$, $P_{\text{idle}} = 0.045\text{ W}$, $V_{\text{bat}} = 12.0\text{ V}$, $99\text{ Wh}$ hypothetical pack.
- **[DERIVED]**: Sample count ($8,000$), Buffer size ($16\text{ KB}$), Duty cycle ($10\%$), Average power ($0.54\text{ W}$), SRAM load ($12.5\%$), Flash load ($9.37\%$).


