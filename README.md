# AUV Low-Power Adaptive Software-Defined Sonar Transmitter Digital Twin

A Python- and MATLAB-based engineering digital twin simulator for the transmitter payload of a low-power adaptive software-defined sonar designed for Autonomous Underwater Vehicles (AUVs), implementing **SIH Problem 26058**.

This simulator models the pre-silicon signal synthesis, adaptive channel decision logic, and DMA memory architecture targeted for the **STMicroelectronics STM32G474** (170 MHz ARM Cortex-M4F with high-speed DAC and DMA).

---

> [!IMPORTANT]
> **Honest Engineering Scope & Limitation Statement**:
> This simulator validates waveform generation, environmental scenario mapping, channel quality estimation, hysteresis-backed profile adaptation, 12-bit DAC quantization, DMA buffer sizing, and estimated duty-cycle power dissipation.
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
4. **Memory Feasibility on STM32G4**: Verifies that a $2.0\text{ ms}$ pulse at $4\text{ MSPS}$ requires exactly **8,000 samples** ($16.0\text{ KB}$ as `uint16_t`). Storing 3 canonical profiles in Flash requires only $48\text{ KB}$ ($<9.4\%$ of the $512\text{ KB}$ Flash on STM32G474), and streaming a pulse occupies only $12.5\%$ of the $128\text{ KB}$ SRAM.
5. **Jitter-Free Adaptation**: Proves that directional Schmitt-trigger hysteresis and debounce persistence filters eliminate state flickering caused by potentiometer wiper noise or ADC thermal fluctuation.
6. **Atomic Profile Latching**: Demonstrates that transmitter profile switches occur strictly at ping repetition boundaries (modeling DMA Transfer Complete ISRs), preventing mid-pulse phase jumps that would destroy matched-filter coherence.
7. **Architectural Duty-Cycle Power Bounds**: Demonstrates that operating at a $10\%$ duty cycle ($2\text{ ms}$ pulse, $20\text{ ms}$ PRI) throttles average transmitter electrical power to $\sim 0.54\text{ W}$. For the modeled transmitter payload load alone against a hypothetical $99\text{ Wh}$ pack, this corresponds to $\sim 183\text{ hours}$ of operation. **Note: This does NOT represent full AUV mission endurance**, as the complete vehicle requires substantial power for thruster propulsion, navigation computers, INS/DVL, cameras, and acoustic communications.

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
| **[FIXED]** | Locked implementation parameters | $F_s = 4.0\text{ MHz}$, $12\text{-bit DAC}$, $T_p = 2.0\text{ ms}$, $\text{PRI} = 20.0\text{ ms}$, $\text{MCU} = \text{STM32G474}$, $\text{Hann window}$ |
| **[ADAPTIVE]** | Controlled by adaptation logic | Profile ID (`LOW_FREQUENCY`, `BALANCED`, `HIGH_FREQUENCY`), Amplitude Factor $A \in \{0.4, 0.7, 1.0\}$ |
| **[ENVIRONMENT]** | Simulation scenario inputs | Depth ($50\text{ m}$), Temp ($20^\circ\text{C}$), Salinity ($35\text{ PSU}$), Turbidity ($0\text{–}100\text{ NTU}$), Ambient Noise ($55\text{ dB}$) |
| **[ASSUMPTION]** | Unmeasured model assumptions | $P_{\text{active}} = 5.0\text{ W}$, $P_{\text{idle}} = 45\text{ mW}$, $P_{\text{elec}} = 0.30\text{ W}$, $V_{\text{bat}} = 12.0\text{ V}$, $E_{\text{bat}} = 99.0\text{ Wh}$ |
| **[DERIVED]** | Analytically computed metrics | $N_p = 8000$, $\text{Table Size} = 16\text{ KB}$, $\text{Duty Cycle} = 10\%$, $P_{\text{avg}} = 0.540\text{ W}$, $\text{SQNR} \approx 69.7\text{ dB}$ |

---

## 4. Three Canonical Transmission Profiles

```
      Profile 1: LOW_FREQUENCY          Profile 2: BALANCED             Profile 3: HIGH_FREQUENCY
      (High Particulate/Scattering)     (Default Operating Mode)        (High Beam Directivity)
  [======== 100 - 220 kHz ========]   [======== 200 - 400 kHz ========]   [======== 350 - 500 kHz ========]
     fc = 160 kHz, B = 120 kHz           fc = 300 kHz, B = 200 kHz           fc = 425 kHz, B = 150 kHz
     Penetrates turbidity plumes        Best Range Resolution (3.75 mm)     Narrow Acoustic Beam Directivity
```

### Acoustic Physics: Range Resolution vs. Beam Directivity
- **Range Resolution ($\Delta R = \frac{c}{2B}$)**:
  - Governed strictly by the **sweep bandwidth $B$**.
  - **Profile 2 (`BALANCED`)** has the widest bandwidth ($B = 200\text{ kHz}$), delivering the highest idealized bandwidth-based range resolution:
    $$\Delta R = \frac{1500\text{ m/s}}{2 \times 200\times 10^3\text{ Hz}} = 3.75\text{ mm}$$
  - **Profile 3 (`HIGH_FREQUENCY`)** has $B = 150\text{ kHz}$, giving $\Delta R = 5.00\text{ mm}$.
- **Beam Directivity ($\theta \propto \frac{\lambda}{D} = \frac{c}{f \cdot D}$)**:
  - **Profile 3 (`HIGH_FREQUENCY`)** operates at the highest frequencies ($350\text{–}500\text{ kHz}$, $\lambda \approx 3.0\text{–}4.3\text{ mm}$), providing a significantly narrower acoustic beam pattern for a fixed physical transducer aperture diameter $D$.
  - Therefore, `HIGH_FREQUENCY` is selected for **high spatial angular directivity**, not because it has superior range resolution over `BALANCED`.

---

## 5. Automated Engineering Validation Test Suite

The repository contains automated validation test suites in both MATLAB (`matlab/run_validation_suite.m`) and Python (`tests/test_simulator.py` and `tests/test_matlab_parity.py`) verifying all 23 requirements specified in SIH Problem 26058:

| # | Group | Requirement | Verification Target | Status |
|---|---|---|---|---|
| **01** | Waveform | Sample Count | $N_p = F_s \cdot T_p = 8,000\text{ samples}$ | **PASSED** |
| **02** | Waveform | Pulse Duration | Exact $2.000\text{ ms}$ discrete time base | **PASSED** |
| **03** | Waveform | Chirp Slope | $k = (f_1 - f_0)/T_p$ ($\text{error} < 0.1\%$) | **PASSED** |
| **04** | Waveform | Start Frequency | $f_0 = 200.0\text{ kHz}$ ($\text{error} < 0.1\%$) | **PASSED** |
| **05** | Waveform | End Frequency | $f_1 = 400.0\text{ kHz}$ ($\text{error} < 0.1\%$) | **PASSED** |
| **06** | Waveform | No NaN Values | Waveform contains no NaN elements | **PASSED** |
| **07** | Waveform | No Inf Values | Waveform contains no Inf elements | **PASSED** |
| **08** | Window | Window Length | Hann window length equals $N_p = 8000$ | **PASSED** |
| **09** | Window | Window Application | Endpoints taper to zero ($<10^{-6}$) | **PASSED** |
| **10** | DAC | Code Range | $0 \le \text{code} \le 4095$ (no overflow/underflow) | **PASSED** |
| **11** | DAC | Data Type | `uint16` array for DMA peripheral | **PASSED** |
| **12** | DAC | Midscale Behavior | Midscale code $2048$ at $0\text{ V AC}$ swing | **PASSED** |
| **13** | DAC | Quantization Error | $\text{Max} \le 0.5\text{ LSB}, \text{SQNR} \ge 68\text{ dB}$ | **PASSED** |
| **14** | Controller | Candidate Selection | $Q \le 0.30 \to \text{LOW}$, $Q \ge 0.75 \to \text{HIGH}$ | **PASSED** |
| **15** | Controller | Hysteresis Stability | Deadbands prevent flicker from noise | **PASSED** |
| **16** | Controller | Single Transient | 1-cycle spike does not switch profile | **PASSED** |
| **17** | Controller | Two Consecutive | 2 cycles commit candidate profile ($N=2$) | **PASSED** |
| **18** | Controller | Candidate Reset | Counter resets when input reverts | **PASSED** |
| **19** | Ping State | Active Profile Frozen | Profile unchanged during active ping | **PASSED** |
| **20** | Ping State | Pending Activates at PRI | Changes committed at ping boundary | **PASSED** |
| **21** | Export | C Headers Generated | Valid syntax, includes, and guards | **PASSED** |
| **22** | Export | Sample Count Metadata | Sample count & size macros match table | **PASSED** |
| **23** | Export | Round-Trip Integrity | Parsed C table == Synthesized table bit-exact | **PASSED** |

---

## 6. Generated Visualizations (`outputs_matlab/plots/`)

The simulation generates 13 engineering validation figures:

1. **`01_time_domain_waveform.png`**: Time-domain waveforms for all 3 profiles showing Hann window tapering.
2. **`02_zoomed_waveform_section.png`**: 80 µs microscopic detail showing 12-bit DAC stair-steps tracking ideal curve.
3. **`03_instantaneous_frequency.png`**: Linear frequency modulation trajectory tracking $200 \to 400\text{ kHz}$.
4. **`04_fft_spectrum.png`**: Magnitude spectrum verifying passband and $>50\text{ dB}$ stopband suppression.
5. **`05_spectrogram.png`**: STFT spectrogram showing straight linear time-frequency energy ridge.
6. **`06_dac_quantization_error.png`**: Quantization error residuals strictly bounded within $[-0.5, +0.5]\text{ LSB}$.
7. **`07_dac_code_histogram.png`**: DAC code distribution histogram centered at midscale code $2048$.
8. **`08_profile_comparison.png`**: Spectral overlay of all three bands (`LOW_FREQUENCY`, `BALANCED`, `HIGH_FREQUENCY`).
9. **`09_channel_quality_timeline.png`**: Predicted Channel Quality Score $Q(t)$ vs directional hysteresis thresholds.
10. **`10_candidate_profile_timeline.png`**: Raw candidate profile timeline driven by instantaneous channel conditions.
11. **`11_active_profile_timeline.png`**: Committed active profile timeline showing rock-solid stability after debounce.
12. **`12_hysteresis_debounce_demo.png`**: Detailed demonstration of hysteresis deadband and $N=2$ debounce filter action.
13. **`13_estimated_power_summary.png`**: Transmitter payload average power timeline across mission and pulse duration sensitivity analysis ($1\text{ ms}, 2\text{ ms}, 3\text{ ms}$).

---

## 7. Firmware-Ready Prototype C Header Files

Exported headers in `outputs_matlab/headers/` and `outputs/headers/`:
- `chirp_low_frequency.h`: 12-bit DAC lookup table for $100\text{–}220\text{ kHz}$ ($8,000$ samples, $16\text{ KB}$).
- `chirp_balanced.h`: 12-bit DAC lookup table for $200\text{–}400\text{ kHz}$ ($8,000$ samples, $16\text{ KB}$).
- `chirp_high_frequency.h`: 12-bit DAC lookup table for $350\text{–}500\text{ kHz}$ ($8,000$ samples, $16\text{ KB}$).
- `sonar_profiles.h`: Master registry with `SonarProfileDescriptor_t` structs for zero-overhead runtime indexing.

---

## 8. Execution Commands

### Running Python Pipeline
```bash
python src/main.py
```

### Running Complete Python & Parity Test Suite (44 Tests)
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Running MATLAB Simulation & 13 Plots
```bash
# In Python execution mirror:
python matlab/generate_matlab_results.py

# In MATLAB interactive prompt:
cd matlab
run_simulation
```
