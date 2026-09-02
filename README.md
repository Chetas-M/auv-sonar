# AUV Low-Power Adaptive Software-Defined Sonar Transmitter Digital Twin

A Python-based engineering digital twin simulator for the transmitter payload of a low-power adaptive software-defined sonar designed for Autonomous Underwater Vehicles (AUVs).

This simulator models the pre-silicon signal synthesis and adaptation pipeline targeted for the **STMicroelectronics STM32G474** (170 MHz ARM Cortex-M4F with high-speed DAC and DMA).

---

> [!IMPORTANT]
> **Standard Engineering Limitation Statement**:
> This simulator validates waveform generation, adaptation logic, quantization, DMA buffer sizing, and estimated duty-cycle power. It does not validate transducer impedance, acoustic propagation, real environmental sensing, analog settling, amplifier stability, or actual current draw.

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
1. **Algorithmic Correctness**: Validates exact phase-integrated Linear Frequency Modulation (LFM) synthesis across all operational bands (Muddy: 100–220 kHz, Balanced: 200–400 kHz, Clear: 350–500 kHz).
2. **Spectral Discontinuity Mitigation**: Confirms that applying a Hann window reduces start/end edge discontinuities and attenuates out-of-band spectral sidelobes in the discrete simulation; physical analog harmonic rejection must be validated on bench scope/FFT.
3. **DAC Quantization Modeling**: Proves that a 12-bit unsigned DAC running at $4.0\text{ MSPS}$ yields $\sim 69.7\text{ dB}$ simulated SQNR, maintaining quantization error strictly within $\pm 0.5\text{ LSB}$ ($\pm 0.403\text{ mV}$ at $3.3\text{V}$ reference).
4. **Memory Feasibility on STM32G4**: Verifies that a $2.0\text{ ms}$ pulse at $4\text{ MSPS}$ requires exactly **8,000 samples** ($16.0\text{ KB}$ as `uint16_t`). Storing 3 canonical profiles in Flash requires only $48\text{ KB}$ ($<9.4\%$ of the $512\text{ KB}$ Flash on STM32G474), and streaming a pulse occupies only $12.5\%$ of the $128\text{ KB}$ SRAM.
5. **Jitter-Free Adaptation**: Proves that two-tier Schmitt-trigger hysteresis ($10\%$ deadband) and debounce persistence filters eliminate state flickering caused by potentiometer wiper noise or ADC thermal fluctuation.
6. **Atomic Profile Latching**: Demonstrates that transmitter profile switches occur strictly at ping repetition boundaries (modeling DMA Transfer Complete ISRs), preventing mid-pulse phase jumps that would destroy matched-filter coherence.
7. **Architectural Duty-Cycle Power Bounds**: Demonstrates that operating at a $10\%$ duty cycle ($2\text{ ms}$ pulse, $20\text{ ms}$ PRI) throttles average transmitter electrical power to $\sim 0.54\text{ W}$. For the modeled transmitter payload load alone against a hypothetical $99\text{ Wh}$ pack, this corresponds to $\sim 183\text{ hours}$ of operation. **Note: This does NOT represent full AUV mission endurance**, as the complete vehicle requires substantial power for thruster propulsion, navigation computers, INS/DVL, cameras, and acoustic communications.

### What This Simulator Does Not Prove
- **Piezoelectric Transducer Impedance**: Does not simulate the complex electrical impedance, electromechanical coupling coefficient ($k_t$), or Butterworth-Van Dyke (BVD) resonant response of the physical ceramic transducer.
- **Analog Front-End & Settling**: Does not simulate analog DAC buffer settling time, amplifier slew rate, crossover distortion, or power amplifier thermal efficiency.
- **High-Speed DAC Bring-Up**: At $4.0\text{ MSPS}$, the exact STM32G4 high-speed DAC channel configuration, output buffer bypass, and external op-amp reconstruction filtering must be verified on hardware.
- **Underwater Acoustic Propagation**: Does not simulate seawater volume attenuation, multipath surface/bottom reflections, thermoclines, or acoustic reverberation.
- **Bench Power Consumption**: Power metrics are analytical engineering models, not empirical bench multimeter measurements.

---

## 3. Locked v1 Parameters

| Parameter | Value | Engineering Rationale |
|---|---|---|
| **MCU Target** | STM32G4 / STM32G474 | 170 MHz Cortex-M4, high-speed DAC (up to 15 MSPS), DMA1/DMA2 |
| **DAC Sample Rate ($F_s$)** | $4.0\text{ MHz}$ ($T_s = 250\text{ ns}$) | Nyquist boundary is $2.0\text{ MHz}$; 8 samples/cycle @ 500 kHz ensures clean analog reconstruction |
| **DAC Resolution** | 12-bit unsigned (`uint16_t`) | Codes $0$ to $4095$; midscale $2048$ ($1.65\text{ V}$ bias for AC-coupled output) |
| **Operating Band** | $100\text{ kHz}$ to $500\text{ kHz}$ | Subsea payload transducer operational frequency range |
| **Default Center Freq ($f_c$)** | $300\text{ kHz}$ | Optimal trade-off between acoustic absorption and range resolution |
| **Default Bandwidth ($B$)** | $200\text{ kHz}$ ($200 \to 400\text{ kHz}$) | Theoretical range resolution $\Delta R = \frac{c}{2B} \approx 3.75\text{ mm}$ (in water $c \approx 1500\text{ m/s}$) |
| **Default Pulse Duration ($T$)** | $2.0\text{ ms}$ | 8,000 samples @ 4 MSPS = 16,000 bytes ($15.62\text{ KB}$) |
| **Pulse Repetition Interval (PRI)**| $20.0\text{ ms}$ ($50\text{ Hz}$ ping rate) | Max unambiguous round-trip acoustic range: $R_{\max} = \frac{c \cdot \text{PRI}}{2} \approx 15.0\text{ m}$ |
| **Default Duty Cycle** | $10.0\%$ | Low duty-cycle envelope for subsea battery conservation |
| **Modulation** | LFM Chirp only | Up-chirp linear frequency modulation with Hann window envelope |
| **Analog Controls** | 3 Potentiometers | Turbidity (0–3.3V), Range/Depth (0–3.3V), Target Strength (0–3.3V, emulating future RX SNR feedback) |

---

## 4. Adaptive Profile Matrix

### 4.1 Turbidity $\to$ Frequency Band Profile
Turbidity causes acoustic scattering from suspended particles. The system adapts frequency band based on potentiometer-emulated turbidity:
- **CLEAR ($350\text{–}500\text{ kHz}$)**: High spatial resolution in low-turbidity water.
- **BALANCED ($200\text{–}400\text{ kHz}$)**: Default balanced compromise between absorption and resolution.
- **MUDDY ($100\text{–}220\text{ kHz}$)**: Lower acoustic frequencies penetrate suspended particulate with reduced Rayleigh scattering.
- **Hysteresis Deadband**: Transitions up occur at $0.40$ and $0.70$; transitions down occur at $0.30$ and $0.60$ with a 2-ping debounce persistence filter.

### 4.2 Range / Depth $\to$ Pulse Duration
Controls total acoustic energy delivered:
- **SHORT ($1.0\text{ ms}$ / 4,000 samples / 8 KB)**: Near-field navigation; minimizes blind zone.
- **MEDIUM ($2.0\text{ ms}$ / 8,000 samples / 16 KB)**: Standard search range (default).
- **LONG ($3.0\text{ ms}$ / 12,000 samples / 24 KB)**: Far-range detection; delivers $+1.76\text{ dB}$ energy over nominal while remaining well within STM32 RAM limits.

### 4.3 Target Strength $\to$ Amplitude Scaling
Emulates a future receiver/SNR feedback signal to scale transmit amplitude:
- **WEAK ($A = 1.00$, full scale $0\text{ dB}$)**: Emulates low return SNR -> maximum transmit drive.
- **MODERATE ($A = 0.70$, $-3.1\text{ dB}$)**: Emulates moderate return SNR -> balanced drive.
- **STRONG ($A = 0.40$, $-7.96\text{ dB}$)**: Emulates strong echo / high SNR -> throttles power to avoid hydrophone receiver saturation and conserve battery.

---

## 5. Firmware Mapping: STM32 Timer + DMA + High-Speed DAC

```
+-----------------------------------------------------------------------------------+
|                                  STM32G474 MCU                                    |
|                                                                                   |
|  +--------------------+        TRGO Trigger Event (4.0 MHz)                       |
|  |  TIM6 Basic Timer  | ---------------------------------------+                  |
|  |  (170MHz / 42.5)   |                                        |                  |
|  +--------------------+                                        v                  |
|                                                       +-------------------------+ |
|  +-------------------------+      Circular/Normal DMA | High-Speed STM32G4 DAC  | |
|  | Flash / SRAM LUT Buffer | -----------------------> | (Instance/pin verified  | |
|  | (CHIRP_BALANCED_LUT)    |      DMA Stream          | during board bring-up)  | |
|  +-------------------------+                          +-------------------------+ |
|                                                                    |              |
|                                                                    | Analog       |
+--------------------------------------------------------------------|--------------+
                                                                     v 0-3.3V
                                                       +----------------------------+
                                                       | High-Speed External Op-Amp |
                                                       | Reconstruction Filter & PA |
                                                       +----------------------------+
```

### Why Precomputed Tables Instead of Real-Time Trigonometry?
1. **CPU Offload (0% CPU during Ping)**: Generating a $4\text{ MSPS}$ output in software would require computing $\cos(2\pi (f_0 t + 0.5 k t^2))$ every $250\text{ ns}$ ($42.5$ clock cycles at $170\text{ MHz}$). An ARM Cortex-M4 single-precision FPU cannot calculate sine/cosine in 42 cycles.
2. **Zero-Jitter Hardware Triggering**: The DMA controller is triggered directly by hardware timer TRGO (`TIMx_TRGO` $\to$ DAC channel). Sample delivery jitter is zero.
3. **Deep Low-Power Sleep**: During the $18\text{ ms}$ inter-ping idle window, the MCU enters `STOP` or `SLEEP` mode. Even during the $2\text{ ms}$ ping burst, the CPU is completely idle and can service telemetry or sleep.

---

## 6. Project Structure

```
d:\AUV sonar\
├── README.md                 # Technical specification and engineering guide
├── requirements.txt          # Python library dependencies
├── src/
│   ├── __init__.py           # Package entry
│   ├── config.py             # Locked hardware constants, frequencies, MCU memory
│   ├── profiles.py           # Dataclasses and enums for Muddy, Balanced, Clear bands
│   ├── waveform.py           # LFM phase integration, Hann window, 12-bit DAC quantization
│   ├── adaptation.py         # 3-axis hysteresis thresholding, debounce, ping controller
│   ├── power_model.py        # Duty-cycle and amplitude-dependent average power estimator
│   ├── export_c.py           # Firmware-ready prototype C header generator with uint16_t DMA tables
│   ├── validation.py         # Matplotlib signal analysis (FFT, STFT spectrogram, SQNR)
│   └── main.py               # Unified pipeline runner and dynamic mission simulator
├── tests/
│   ├── __init__.py
│   └── test_simulator.py     # Comprehensive unit tests (100% passing)
└── outputs/
    ├── plots/                # High-resolution PNG validation figures
    │   ├── single_pulse_analysis.png
    │   ├── quantization_analysis.png
    │   ├── profile_comparison.png
    │   └── dynamic_simulation_timeline.png
    └── headers/              # Firmware-ready prototype C headers for STM32
        ├── chirp_muddy.h
        ├── chirp_balanced.h
        ├── chirp_clear.h
        └── sonar_profiles.h  # Master registry & descriptor structs
```

---

## 7. How to Run the Simulator

### Prerequisites
- Python 3.9+ (tested on Python 3.13)
- Required packages: `numpy`, `scipy`, `matplotlib`

```bash
pip install -r requirements.txt
```

### Running the Complete Pipeline
To synthesize all waveforms, compute power models, render all engineering validation figures, run the 150-ping dynamic simulation, and export all C headers:

```bash
python src/main.py
```

### Running the Automated Unit Test Suite
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 8. Validation Plots & Verification Results

### 8.1 Single Pulse Spectral & Spectrogram Analysis (`single_pulse_analysis.png`)
- **Time Domain**: Smooth Hann envelope tapers start and end to zero amplitude.
- **DAC Zoom**: Demonstrates 12-bit stair-step discretization centered at midscale code $2048$.
- **FFT Spectrum**: Shows passband between $200\text{ kHz}$ and $400\text{ kHz}$; Hann windowing reduces edge discontinuities and sidelobes, but physical analog rejection must be validated on bench scope/FFT.
- **Spectrogram**: Clean linear time-frequency slope from $f_{\text{start}}$ to $f_{\text{end}}$.

### 8.2 DAC Quantization Error & SQNR Analysis (`quantization_analysis.png`)
- **Error Bounds**: All quantization residuals reside strictly within $[-0.5, +0.5]\text{ LSB}$.
- **Voltage Error**: Peak voltage error is $\pm 0.403\text{ mV}$ on a $3.3\text{V}$ reference rail.
- **Simulated SQNR**: $69.67\text{ dB}$, confirming low digital math distortion (analog settling, slew rate, and THD must be tested on hardware).

### 8.3 Cross-Profile Comparison (`profile_comparison.png`)
- Displays spectral separation across Muddy ($100\text{–}220\text{ kHz}$), Balanced ($200\text{–}400\text{ kHz}$), and Clear ($350\text{–}500\text{ kHz}$) modes.

### 8.4 Dynamic Mission Simulation (`dynamic_simulation_timeline.png`)
- Simulates 150 consecutive pings ($3.0\text{ seconds}$ mission elapsed time).
- Injects noise into the potentiometer wiper voltages. Demonstrates that the **hysteresis deadband prevents profile oscillation**, and profile updates occur strictly at ping boundaries. Target strength emulates a future receiver/SNR feedback signal.

---

## 9. Five-Point Validation Framework & Bring-Up Protocol

To rigorously establish mathematical credibility while maintaining physical humility, the simulator implements a 5-point validation protocol:

### Check 1: Instantaneous Frequency Test (Hilbert Phase Derivative) — [AUTOMATED]
- **Method**: Computes the analytic signal via Hilbert transform: $z(t) = s(t) + j\mathcal{H}\{s(t)\}$. Extracts unwrapped phase $\phi(t)$ and differentiates: $f_{\text{inst}}(t) = \frac{1}{2\pi} \frac{d\phi}{dt}$.
- **Criteria**: Sweep must be strictly monotonic ($df/dt > 0$), sweep slope must match $k = (f_{\text{end}} - f_{\text{start}}) / T$ within $0.1\%$, and intercept must match $f_{\text{start}}$ within $0.1\%$.
- **Result**: **PASSED** (Slope = $100.00\text{ MHz/s}$, Error = $0.0000\%$, Monotonic = `True`).

### Check 2: FFT Band-Energy Concentration Test — [AUTOMATED]
- **Method**: Calculates the discrete power spectral density $|X(f)|^2$ up to the Nyquist limit ($2.0\text{ MHz}$). Integrates spectral power inside $[f_{\text{start}} - 5\text{kHz}, f_{\text{end}} + 5\text{kHz}]$ against total emitted power.
- **Criteria**: $\ge 99.0\%$ of total digital signal energy must reside within the allocated band.
- **Result**: **PASSED** ($100.0000\%$ in-band, out-of-band leakage $< 0.0001\%$).

### Check 3: Spectrogram Ridge Linearity Test — [AUTOMATED]
- **Method**: Evaluates STFT spectrogram time-frequency bins. Extracts instantaneous peak energy frequency $f_{\text{peak}}(t)$ and performs linear regression over time.
- **Criteria**: Correlation coefficient $R^2 \ge 0.98$ and regression slope within $5\%$ of theoretical chirp rate.
- **Result**: **PASSED** ($R^2 = 0.9901$, Slope = $100.57\text{ MHz/s}$, Slope Error = $0.57\%$).

### Check 4: Header Round-Trip Integrity Test — [AUTOMATED]
- **Method**: Generates C header file, parses all `0xXXXX` hex tokens back into an in-memory `uint16_t` array, and compares against the Python DAC array.
- **Criteria**: Bit-exact sample count match, exact numerical match, maximum discrepancy $= 0\text{ LSB}$.
- **Result**: **PASSED** (8,000 samples matched bit-for-bit, Max Discrepancy $= 0\text{ LSB}$).

### Check 5: Hardware Feasibility Test (STM32 Bring-Up Protocol) — [BENCH PROCEDURE]
Before deploying this payload in water, execute this bench verification procedure on the STM32G4:
1. **Clock & Timer Setup**: Configure SYSCLK to $170\text{ MHz}$. Set TIM6 prescaler $= 0$, auto-reload $= 42$ (or TIM2 for 32-bit counting) to output a clean $4.0\text{ MHz}$ TRGO pulse stream.
2. **DAC Mode Selection**: On STM32G474, the internal output buffer adds settling delay. **Bypass the internal DAC buffer** (`DAC_OUTPUTBUFFER_DISABLE`) and route DAC output directly to an external high-speed op-amp buffer (e.g. OPA350, ADA4807, or AD8065).
3. **DMA Burst**: Configure DMA1 Channel 3 in normal memory-to-peripheral mode, half-word (16-bit) width, circular or single-shot triggered on TIM6 TRGO.
4. **Oscilloscope / Spectrum Analyzer Measurement**:
   - Connect active high-impedance scope probe ($>50\text{ MSPS}$ acquisition rate) at DAC output pin.
   - Measure 10–90% rise time, settling time ($<200\text{ ns}$ required for 4 MSPS), and peak-to-peak voltage ($1.65\text{ V} \pm 1.65\text{ V}$).
   - Run instrument FFT: confirm passband ($200\text{–}400\text{ kHz}$), check spurious-free dynamic range (SFDR), and verify image suppression above Nyquist ($2\text{ MHz}$) through external reconstruction low-pass filter ($f_c \approx 750\text{ kHz}$).
5. **Current Shunt Measurement**: Insert an INA219 or bench current meter on the PA power supply rail to empirically measure active vs idle power dissipation across pings.

