# Master Repository Context & Architecture Primer
## Autonomous Underwater Vehicle (AUV) Low-Power Adaptive Software-Defined Sonar Transmitter Payload

> **Document Identifier:** `REPOSITORY_CONTEXT.md`  
> **Target Audience:** AI Agents, Language Models, Systems Engineers, Embedded Firmware Developers  
> **Project Scope:** SIH Problem 26058 — Digital Twin, DSP Synthesis, Adaptation Logic, and STM32G474 Bare-Metal Firmware  
> **Current Status:** Pre-silicon digital twin validated (79/79 pytest tests passing, bit-exact C header parity, compile-ready C11 firmware). Physical hardware bring-up is transmitter-side only and pending lab bench test.

---

## 1. Executive Summary & Problem Statement

This repository implements an end-to-end engineering digital twin simulator and compile-ready bare-metal embedded firmware for the **transmitter payload** of a low-power, real-time adaptive software-defined sonar designed for Autonomous Underwater Vehicles (AUVs), addressing **Smart India Hackathon (SIH) Problem Statement 26058**.

### The Engineering Challenge:
Traditional oceanographic sonars operate at fixed acoustic frequencies, forcing an unavoidable compromise:
- **Low frequencies (<200 kHz)** achieve extended propagation range through water due to lower acoustic absorption, but suffer from coarse range resolution and broad beam angles.
- **High frequencies (>350 kHz)** deliver millimeter range resolution and tight directional spatial resolution, but undergo severe exponential acoustic absorption, especially in warm, saline, or turbid water.

### The Solution Built in This Repository:
1. **Adaptive Transmitter Payload:** Dynamically transitions between three canonical Linear Frequency Modulated (LFM) chirp profiles (`LOW_FREQUENCY`, `BALANCED`, `HIGH_FREQUENCY`) based on environmental propagation conditions and simulated mission objectives (survey resolution vs. narrow-beam directivity).
2. **Pre-Silicon Digital Twin:** Developed in dual Python 3.10+ (`src/`) and MATLAB R2020a+ (`matlab/`) architectures, modeling continuous phase integration, Hann window tapering, 12-bit unsigned DAC quantization, and 5-point Ainslie-McColm seawater acoustic absorption.
3. **Robust Control State Machine:** Implements directional Schmitt-trigger hysteresis deadbands ($\pm 5\%$) and a 2-ping debounce persistence filter ($N=2$) to reject potentiometer wiper noise and ADC thermal jitter, with atomic profile switching locked strictly to ping repetition boundaries ($20.0\text{ ms}$ PRI / $50\text{ Hz}$).
4. **Target Hardware Architecture (STM32G474RET6):** A 160.0 MHz ARM Cortex-M4F bare-metal C11 firmware (`firmware/`) utilizing TIM2 TRGO hardware triggers at exactly 4.000000 MSPS (0.000% frequency error), DMA1 Channel 1 streaming 8,000 samples per ping from Flash, and on-chip internal routing from 15 MSPS `DAC3_CH2` to high-speed `OPAMP3` in follower mode ($45\text{ V}/\mu\text{s}$ slew rate) out to pin `PB1`.
5. **Transmitter Power Optimization:** Operating at a $10.0\%$ duty cycle ($2.0\text{ ms}$ active chirp every $20.0\text{ ms}$ PRI) throttles average transmitter electrical power to **$0.540\text{ W}$**, projecting $\sim 183\text{ hours}$ of transmitter-only payload operation on a standard $99\text{ Wh}$ battery pack.

---

## 2. Truth-in-Engineering & Scope Boundaries

> [!IMPORTANT]
> **MANDATORY CONTEXT FOR ALL AGENTS & MODELS:**
> When reviewing, describing, or modifying this codebase, you must adhere strictly to the following engineering boundaries. Do **NOT** hallucinate physical field tests or claims beyond the transmitter payload digital twin.

```text
================================================================================
SIMULATION STATUS:
Simulation correctness level: algorithmically credible, physically unverified.
================================================================================
```

### What This Simulator Proves:
1. **Algorithmic Correctness:** Bit-exact continuous phase-integrated LFM chirp generation across all three canonical bands (`LOW_FREQUENCY`: 100–220 kHz, `BALANCED`: 200–400 kHz, `HIGH_FREQUENCY`: 350–500 kHz).
2. **Spectral Sidelobe Suppression:** Proves that symmetric Hann windowing attenuates out-of-band spectral sidelobes by $>50\text{ dB}$ in simulation.
3. **DAC Quantization Accuracy:** Proves that a 12-bit unsigned DAC at 4.0 MSPS achieves $\sim 69.7\text{ dB}$ simulated SQNR, with quantization errors strictly bounded within $[-0.5, +0.5]\text{ LSB}$ ($\pm 0.403\text{ mV}$ on $3.3\text{ V}$ reference).
4. **Memory Allocation:** Proves that an 8,000-sample pulse requires exactly $16.0\text{ KB}$ as `uint16_t` half-words ($12.5\%$ of STM32G474 128 KB SRAM; all 3 LUTs occupy $48.0\text{ KB}$ or $9.37\%$ of 512 KB Flash).
5. **Decoupled Adaptation Logic:** Proves that evaluating propagation viability separately from mission objective utility prevents `LOW_FREQUENCY` from artificially dominating near/medium ranges.
6. **State Machine Stability:** Proves that directional hysteresis and $N=2$ debounce filters completely eliminate state fluttering under simulated analog noise ($\sigma = 0.02$).
7. **Atomic Ping Latching:** Proves profile updates only take effect at ping repetition boundaries, preventing mid-pulse phase jumps.
8. **Transmitter Power Bounds:** Verifies the analytical $10\%$ duty cycle average power dissipation of $0.540\text{ W}$.

### What This Simulator Does NOT Claim or Prove:
- **Transducer Electromechanics:** Does not model piezoelectric ceramic resonance, electromechanical coupling ($k_t$), or Butterworth-Van Dyke (BVD) electrical impedance.
- **Physical Ocean Acoustic Propagation:** Does not simulate ocean multipath reflections, thermoclines, seabed reverberation, or real acoustic noise floors.
- **Receiver / Hydrophone Processing:** This is a **transmitter payload only**. Receiver front-ends, match filtering, and echo detection are out of scope.
- **Analog Front-End Settling:** Analog slew-rate limits, PCB trace parasitics, and power amplifier thermal stability must be verified on the physical lab bench.
- **Full AUV Vehicle Endurance:** The $183\text{ hours}$ metric is for the **transmitter payload electrical load alone** against a hypothetical $99\text{ Wh}$ battery; real AUV endurance is heavily dominated by thrusters, navigation computers, INS/DVL, and comms.
- **Real Environmental Sensors:** For the v1 physical bench demonstration, environmental inputs are emulated via **three precision potentiometers** connected to STM32 12-bit ADC channels. Target strength emulates a future receiver SNR feedback signal.

---

## 3. Mathematical & Signal Processing Pipeline

The signal processing chain converts environmental conditions and configuration parameters into a compile-ready 12-bit lookup table:

```text
  f_start, f_stop, T_p, F_s
              │
              ▼
   Phase Integration φ(t)
   φ(t) = 2π(f_start·t + 0.5·k·t²)
              │
              ▼
    Raw Continuous Chirp
    x(t) = A · sin(φ(t))
              │
              ▼
    Symmetric Hann Window
    w[n] = 0.5(1 - cos(2πn/(N-1)))
              │
              ▼
   Tapered Floating-Point Signal
   x_win[n] = x[n] · w[n]  ∈ [-1.0, +1.0]
              │
              ▼
     12-Bit DAC Quantization
     Code[n] = round(2048 + 2047 · x_win[n])  ∈ [0, 4095]
              │
              ▼
     DMA Flash Table (C99 uint16_t[8000])
```

### Key DSP Formulations:
1. **Chirp Modulation Rate ($k$):**
   $$k = \frac{f_{\text{stop}} - f_{\text{start}}}{T_p} \quad [\text{Hz/s}]$$
   For `BALANCED`: $k = \frac{400\text{ kHz} - 200\text{ kHz}}{0.002\text{ s}} = 1.0 \times 10^8\text{ Hz/s} = 100.0\text{ MHz/s}$.
2. **Continuous Phase Function ($\phi(t)$):**
   $$\phi(t) = 2\pi \int_0^t f(\tau) \, d\tau = 2\pi \left( f_{\text{start}} t + \frac{k}{2} t^2 \right)$$
3. **Theoretical Signal-to-Quantization-Noise Ratio (SQNR):**
   $$\text{SQNR}_{\text{ideal}} = 6.02 \cdot b + 1.76\text{ dB} \approx 6.02(12) + 1.76 = 74.0\text{ dB}$$
   Due to Hann window envelope tapering (which reduces average signal power), the measured simulated SQNR across the chirp pulse is:
   $$\text{SQNR}_{\text{simulated}} = 10 \log_{10} \left( \frac{\sum x_{\text{windowed}}^2[n]}{\sum (x_{\text{windowed}}[n] - x_{\text{quantized}}[n])^2} \right) \approx 69.67\text{ dB}$$
4. **Quantization Bounds:**
   $$\text{Error}[n] = \text{Code}[n] - (2048 + 2047 \cdot x_{\text{windowed}}[n]) \in [-0.5, +0.5]\text{ LSB}$$
   At $V_{\text{REF+}} = 3.300\text{ V}$, $1\text{ LSB} = \frac{3.3\text{ V}}{4095} \approx 0.8058\text{ mV}$. The maximum quantization error is strictly within $\pm 0.403\text{ mV}$.

---

## 4. Acoustic Physics & Propagation Modeling

Acoustic propagation in seawater is modeled using authoritative oceanographic physics equations in `src/profile_evaluator.py` and `src/physics_reference.py`:

### 1. Ainslie-McColm (1998) Acoustic Absorption ($\alpha$)
Computes absorption $\alpha(f)$ in $\text{dB/km}$ for acoustic frequencies $f \in [100, 500]\text{ kHz}$:
$$\alpha(f) = 0.106 \frac{f_1 f^2}{f_1^2 + f^2} e^{(\text{pH} - 8)/0.56} + 0.52 \left(1 + \frac{T}{43}\right)\left(\frac{S}{35}\right) \frac{f_2 f^2}{f_2^2 + f^2} e^{-D/6000} + 0.00049 f^2 e^{-(T/27 + D/17000)}$$

Where:
- **Boric Acid Relaxation Frequency ($f_1$):**
  $$f_1 = 0.78 \sqrt{\frac{S}{35}} \, e^{T/26} \quad [\text{kHz}]$$
- **Magnesium Sulfate Relaxation Frequency ($f_2$):**
  $$f_2 = 42 \, e^{T/17} \quad [\text{kHz}]$$
- **Hydrostatic Depth Pressure Factor ($P_2$):**
  $$P_2 = \exp\left(-\frac{D}{6000}\right)$$
  This accounts for the reduction in chemical relaxation absorption at increasing depth ($D$ in meters).
- **Default Oceanographic Baseline:** $T = 20.0^\circ\text{C}$, $S = 35.0\text{ PSU}$, $D = 50.0\text{ m}$, $\text{pH} = 8.0$.

### 2. Five-Point Discrete Band Evaluation
Because sonar chirps are wideband ($B = 120\text{ to }200\text{ kHz}$), absorption varies significantly across the sweep. The digital twin computes absorption at 5 discrete frequencies across each profile's bandwidth:
$$f_i \in \{ f_{\text{start}}, \; f_{\text{start}} + 0.25B, \; f_c, \; f_{\text{start}} + 0.75B, \; f_{\text{stop}} \}$$
$$\bar{\alpha}_{\text{profile}} = \frac{1}{5} \sum_{i=1}^5 \alpha(f_i)$$

Canonical baseline values calculated:
- **`LOW_FREQUENCY` (100–220 kHz):** $\bar{\alpha} = 63.99\text{ dB/km}$
- **`BALANCED` (200–400 kHz):** $\bar{\alpha} = 105.62\text{ dB/km}$
- **`HIGH_FREQUENCY` (350–500 kHz):** $\bar{\alpha} = 135.86\text{ dB/km}$

### 3. Transmission Loss ($TL$) & Relative Propagation Margin
One-way acoustic transmission loss assuming spherical geometric spreading:
$$TL(R, \bar{\alpha}) = 20 \log_{10}(R) + \bar{\alpha} \cdot \frac{R}{1000} \quad [\text{dB}]$$
The modeled relative propagation margin $M_{\text{rel}}$ against the normalized reference:
$$M_{\text{rel}}(R, \text{Profile}) = SL_{\text{rel}} - TL(R, \bar{\alpha}) - \text{NP}_{\text{sim}}$$
Where $SL_{\text{rel}} = 0.0\text{ dB}$ (normalized) and $\text{NP}_{\text{sim}} = 0.0\text{ dB}$ (noise penalty).

---

## 5. Two-Tier Profile Selection & State Machine

```text
                        ENVIRONMENTAL INPUTS
                 (Range, Temp, Salinity, Depth, Turbidity)
                                  │
                                  ▼
                     PROFILE EVALUATION ENGINE
             Evaluates all 3 profiles simultaneously:
             • Mean Band Attenuation (5-point Ainslie-McColm)
             • Modeled Transmission Loss & Relative Margin
             • Theoretical Range Resolution (ΔR = c / 2B)
             • Relative Theoretical Directivity (θ ∝ c / f·D)
                                  │
                                  ▼
                     PROPAGATION VIABILITY FILTER
               Is Relative Margin >= Thresh_viab (-65.0 dB)?
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
        Multiple Viable Profiles          Single / None Viable
                  │                               │
                  ▼                               ▼
       MISSION OBJECTIVE SELECTOR         FAIL-SAFE SELECTION
      • SURVEY_MODE:                     • Select LOW_FREQUENCY
        Select BALANCED (3.75 mm best)     (Lowest attenuation)
      • DIRECTIVITY_MODE:
        Select HIGH_FREQUENCY
                  │                               │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                        RAW CANDIDATE PROFILE
                                  │
                                  ▼
                        DIRECTIONAL HYSTERESIS
                      (±5% Schmitt-Trigger Bands)
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
                      (DMA TC Interrupt / 50 Hz PRI)
                                  │
                                  ▼
                           ACTIVE PROFILE
```

### Hysteresis & Debounce Specifications:
- **Hysteresis Deadbands:** To transition upward (e.g. from `LOW_FREQUENCY` to `BALANCED`), the channel condition or range must improve by at least $+5\%$ beyond the nominal threshold. To transition downward, condition must degrade by at least $-5\%$. This prevents rapid oscillation ("hunting") when hovering near a switching boundary.
- **Debounce Filter ($N=2$):** A candidate profile must be selected for **two consecutive pings** before it is placed into the `pending_profile` latch. A single transient glitch (e.g. ADC wiper scratch) is immediately rejected.
- **Atomic Ping Boundary Latching:** Even after passing debounce, the active DMA transfer is **never interrupted mid-chirp**. The profile switch occurs strictly inside the DMA Transfer-Complete ISR during the $18.0\text{ ms}$ quiet gap between pings.

---

## 6. The Three Canonical Transmission Profiles

| Parameter | Profile 1: `LOW_FREQUENCY` | Profile 2: `BALANCED` (Default) | Profile 3: `HIGH_FREQUENCY` |
|---|---|---|---|
| **Operational Band** | $100.0\text{ to }220.0\text{ kHz}$ | $200.0\text{ to }400.0\text{ kHz}$ | $350.0\text{ to }500.0\text{ kHz}$ |
| **Center Frequency ($f_c$)** | $160.0\text{ kHz}$ | $300.0\text{ kHz}$ | $425.0\text{ kHz}$ |
| **Sweep Bandwidth ($B$)** | $120.0\text{ kHz}$ | $200.0\text{ kHz}$ | $150.0\text{ kHz}$ |
| **Chirp Slope ($k$)** | $60.0\text{ MHz/s}$ | $100.0\text{ MHz/s}$ | $75.0\text{ MHz/s}$ |
| **Transmit Amplitude ($A$)** | $1.00$ ($0.0\text{ dB}$) | $0.70$ ($-3.1\text{ dB}$) | $0.40$ ($-8.0\text{ dB}$) |
| **Theoretical Range Resolution ($\Delta R = \frac{c}{2B}$)** | $6.25\text{ mm}$ ($c = 1500\text{ m/s}$) | **$3.75\text{ mm}$ (Best Resolution)** | $5.00\text{ mm}$ |
| **Relative Directivity Factor ($\theta \propto \frac{c}{f_c D}$)** | $0.533\times$ | $1.000\times$ (Reference) | **$1.417\times$ (Narrowest Beam)** |
| **Mean Seawater Absorption ($\bar{\alpha}$)** | **$63.99\text{ dB/km}$ (Lowest)** | $105.62\text{ dB/km}$ | $135.86\text{ dB/km}$ |
| **Extinction Range at $-65\text{ dB}$ Viability** | **$260.7\text{ m}$ (Longest Range)** | $185.8\text{ m}$ | $155.7\text{ m}$ |
| **Primary Mission Role** | Long-range navigation & turbid fallback | Default seabed survey & target mapping | Fine angular feature directivity |

---

## 7. STM32G474 Bare-Metal Firmware Architecture

The firmware (`firmware/`) compiles targeting the STMicroelectronics **STM32G474RET6** (ARM Cortex-M4F with FPU, 128 KB SRAM, 512 KB Flash).

### Key Architectural Decisions from Feasibility Audit:
1. **Clock Tree Tuning (160.0 MHz):** SYSCLK is tuned to **160.000 MHz** using the PLL with 8.0 MHz HSE from ST-LINK MCO ($\text{PLLM}=1, \text{PLLN}=40, \text{PLLR}=2$). This enables an exact integer division by 40 ($\text{PSC}=0, \text{ARR}=39$) on TIM2 for a **4,000,000.00 Hz TRGO rate with 0.000% error** (at default 170 MHz, division would yield 4.0476 MHz / +1.19% error).
2. **DAC & OPAMP Routing:** Datasheet DS12288 specifies that the internal DAC output buffer is limited to $1.0\text{ MSPS}$ ($t_{\text{settling}} = 1.6\text{ to }3.0\text{ }\mu\text{s}$), making it unusable at 4.0 MSPS ($T_s = 250\text{ ns}$). The firmware routes **DAC3 Channel 2** (15 MSPS capable, unbuffered) internally on-chip to **OPAMP3** in High-Speed Follower mode ($45\text{ V}/\mu\text{s}$ slew rate, $13\text{ MHz}$ GBW) directly out to pin **PB1** (Morpho connector `CN10 Pin 24`), completely bypassing the slow internal DAC buffer.
3. **High-Frequency Interface Mode:** Configures `DAC_MCR.HFSEL = 0b01` for high-frequency AHB operation ($80\text{ MHz} < \text{AHB} \le 160\text{ MHz}$).
4. **DMA Streaming Throughput:** DMA1 Channel 1 (DMAMUX1 Request ID 103) streams 8,000 half-words from Flash to `DAC3->DHR12R2` at $8.0\text{ MB/s}$ throughput during active ping, consuming only $1.18\%$ of AHB bus matrix capacity.
5. **Low-Power PRI Sleep:** CPU enters `__WFI()` sleep mode during both the pulse and the $18.0\text{ ms}$ quiet gap, waking up only on DMA TC and TIM6 PRI interrupts ($<0.001\%$ CPU duty load).

### Pinout Table (NUCLEO-G474RE):
| Signal Name | Microcontroller Pin | Board Connector | Hardware Role | Status |
|---|---|---|---|---|
| **Sonar Output** | **PB1** | Morpho **CN10 Pin 24** | OPAMP3 Output ($45\text{ V}/\mu\text{s}$ follower) | **FREE** (Dedicated) |
| **Ground Reference** | **GND** | Morpho **CN10 Pin 20** | Oscilloscope ground spring point | **GND** |
| **Transmit LED** | **PA5** | Onboard LED | Green LED (LD2, toggles on active ping) | Onboard LD2 |
| **Profile Button** | **PC13** | Onboard Pushbutton | Blue Button (B1, manual profile cycle) | Onboard B1 |
| **Clock Check MCO** | **PA8** | Morpho **CN10 Pin 23** | SYSCLK / 16 clock check ($10.000\text{ MHz}$) | **FREE** |

---

## 8. Transmitter Duty-Cycle Power Model

Transmitter payload electrical power consumption is analytically modeled across active chirp and idle inter-ping periods:

$$\text{Duty Cycle } (D) = \frac{T_p}{\text{PRI}} = \frac{2.0\text{ ms}}{20.0\text{ ms}} = 0.10 \quad (10.0\%)$$
$$P_{\text{avg}} = P_{\text{active}} \cdot D + P_{\text{idle}} \cdot (1 - D) = 5.0\text{ W}(0.10) + 0.045\text{ W}(0.90) = 0.540\text{ W}$$
$$I_{\text{avg}} = \frac{P_{\text{avg}}}{V_{\text{bat}}} = \frac{0.540\text{ W}}{12.0\text{ V}} = 45.0\text{ mA}$$

### Operating Endurance on Hypothetical 99 Wh Subsea Battery Pack:
$$\text{Endurance}_{\text{TX}} = \frac{99.0\text{ Wh}}{0.540\text{ W}} \approx 183.2\text{ hours}$$

> [!WARNING]
> **Payload Load Only:** This endurance figure isolates the transmitter electronics load alone. Complete AUV mission endurance is dominated by propulsion thrusters ($50\text{–}200\text{ W}$), vehicle computers ($10\text{–}30\text{ W}$), INS/DVL sensors, and communications.

---

## 9. Automated Verification & Cross-Platform Parity Matrix

The repository contains **79 automated unit tests in Python (100% passing)** and **35 tests in MATLAB**:

```text
================================================================================
TEST SUITE SUMMARY: 79 passed in 1.85s (100% pass rate)
================================================================================
```

| Test File | Classes / Tests | Key Requirements Verified |
|---|:---:|---|
| **[`tests/test_simulator.py`](file:///d:/AUV%20sonar/tests/test_simulator.py)** | 7 classes / **36 tests** | • **23 Locked Hardware Requirements:** $N_p=8000$, $T_p=2\text{ ms}$, slope $100\text{ MHz/s}$, Hann tapering, 12-bit DAC bounds ($0\text{–}4095$), midscale $2048$, SQNR $\ge 69.5\text{ dB}$, deadbands, $N=2$ debounce, ping-boundary latching, C header export round-trip<br>• Instantaneous frequency Hilbert derivative linearity<br>• FFT in-band energy concentration ($>99.999\%$) |
| **[`tests/test_profile_evaluation.py`](file:///d:/AUV%20sonar/tests/test_profile_evaluation.py)** | 1 class / **12 tests** | • 5-point discrete frequency evaluation across sweep band<br>• Positive, finite Ainslie-McColm absorption coefficients<br>• Monotonic transmission loss scaling with distance<br>• Attenuation ordering: $\text{HIGH} > \text{BALANCED} > \text{LOW}$<br>• Range resolution: `BALANCED` achieves $3.75\text{ mm}$ limit<br>• Relative directivity: `HIGH_FREQUENCY` achieves $1.417\times$<br>• Survey mode selects `BALANCED`, Directivity mode selects `HIGH` |
| **[`tests/test_physics_regression.py`](file:///d:/AUV%20sonar/tests/test_physics_regression.py)** | 1 class / **9 tests** | • Ainslie-McColm parity against reference literature ($<10^{-10}$ relative error)<br>• Hydrostatic depth factor $P_2 = \exp(-D/6000)$ regression<br>• Frequency & distance unit scaling ($\text{kHz}$ vs $\text{Hz}$, $\text{dB/km}$ vs $\text{dB/m}$)<br>• Canonical extinction boundaries ($155.7\text{ m}, 185.8\text{ m}, 260.7\text{ m}$)<br>• Canonical JSON artifact schema integrity |
| **[`tests/test_matlab_parity.py`](file:///d:/AUV%20sonar/tests/test_matlab_parity.py)** | 1 class / **9 tests** | • Structural and mathematical parity across all 18 MATLAB `.m` files<br>• Configuration parameter synchronization with `src/config.py`<br>• LFM phase equation and channel model score parity |
| **[`tests/test_firmware_lut_parity.py`](file:///d:/AUV%20sonar/tests/test_firmware_lut_parity.py)** | 1 class / **13 tests** | • **Bit-exact identity ($0\text{ LSB}$ max error)** between Python `src/waveform.py` output and C firmware headers in `outputs/headers/*.h`<br>• Header macro definitions (`SAMPLE_RATE_HZ = 4000000`)<br>• Master header `sonar_profiles.h` table consistency |

---

## 10. Repository Codebase Map

```text
d:\AUV sonar\
├── README.md                              # Main landing page with 60-second quickstart
├── REPOSITORY_CONTEXT.md                  # This master context document
├── walkthrough.md                         # Detailed engineering results & verification summary
├── requirements.txt                       # Python dependencies (numpy, scipy, matplotlib, pytest, docx)
│
├── src/                                   # Python Digital Twin Implementation
│   ├── __init__.py                        # Package init
│   ├── config.py                          # Master configuration & parameter taxonomy
│   ├── profiles.py                        # Canonical profile definitions & enums
│   ├── waveform.py                        # LFM chirp synthesis, Hann window, DAC quantizer
│   ├── profile_evaluator.py               # 5-point Ainslie-McColm absorption & mission selector
│   ├── physics_reference.py               # Independent reference acoustic models (Ainslie, Mackenzie)
│   ├── adaptation.py                      # Schmitt-trigger hysteresis & N=2 debounce state machine
│   ├── power_model.py                     # Duty-cycle average power & battery endurance
│   ├── export_c.py                        # C99 header & LUT generator for STM32 firmware
│   ├── experiments.py                     # Priority 1 parameter sweeps (Exp 1–7)
│   ├── validation.py                      # 23-point DSP/waveform verification suite
│   ├── canonical_data.py                  # Canonical reference dataset loader
│   ├── generate_canonical_results.py      # Generates outputs/canonical_profile_results.json
│   ├── main.py                            # Master CLI simulation runner
│   └── README.md                          # Python digital twin documentation
│
├── tests/                                 # Automated Test Framework
│   ├── __init__.py                        # Package init
│   ├── test_simulator.py                  # 23 locked requirements & DSP signal tests (36 tests)
│   ├── test_profile_evaluation.py         # Priority 1 profile evaluation tests (12 tests)
│   ├── test_physics_regression.py         # Acoustic physics & hydrostatic P2 tests (9 tests)
│   ├── test_matlab_parity.py              # Cross-platform Python/MATLAB parity tests (9 tests)
│   ├── test_firmware_lut_parity.py        # Bit-exact C header LUT parity tests (13 tests)
│   └── README.md                          # Test suite architecture & assertion matrix
│
├── firmware/                              # STM32G474 Embedded Firmware
│   ├── Inc/                               # C Header Files
│   │   ├── main.h                         # System constants, pin defines, compile-time assertions
│   │   ├── clock_config.h                 # 160.0 MHz PLL clock prototypes
│   │   ├── dac_opamp.h                    # DAC3 Ch2 & OPAMP3 follower prototypes
│   │   ├── tim_trigger.h                  # TIM2 4.0 MSPS TRGO & TIM6 PRI prototypes
│   │   ├── dma_stream.h                   # DMA1 Ch1 DMAMUX streaming prototypes
│   │   ├── sonar_lut.h                    # LUT accessors consuming precomputed headers
│   │   ├── stm32g4xx_it.h                 # ISR prototypes (DMA TC, PRI timer)
│   │   └── stm32g474_registers.h          # RM0440 hardware register definitions
│   ├── Src/                               # C Source Files
│   │   ├── main.c                         # System init, status reporting, low-power WFI sleep
│   │   ├── clock_config.c                 # PLL configuration (160 MHz, HSE/HSI fallback)
│   │   ├── dac_opamp.c                    # DAC3_OUT2 -> OPAMP3 internal follower -> PB1 setup
│   │   ├── tim_trigger.c                  # TIM2 PSC=0 ARR=39 4.000000 MHz TRGO setup
│   │   ├── dma_stream.c                   # DMA1 Ch1 memory-to-peripheral transfer
│   │   ├── sonar_lut.c                    # Waveform LUT instantiation from headers
│   │   └── stm32g4xx_it.c                 # DMA TC, PRI timer, and User Button PC13 ISRs
│   ├── hardware_bringup_checklist.md      # 8-step lab oscilloscope & DMM bring-up protocol
│   ├── stm32g4_dac_feasibility_audit.md   # Official 30KB hardware & datasheet feasibility audit
│   ├── auv_sonar_g474.ioc                 # STM32CubeMX hardware peripheral configuration
│   ├── Makefile                           # Host verification & ARM cross-compilation build
│   └── README.md                          # Firmware guide & flashing instructions
│
├── matlab/                                # Standalone MATLAB Digital Twin Mirror
│   ├── config_sonar.m                     # Configuration mirror
│   ├── profile_definitions.m              # Profile struct definitions
│   ├── generate_lfm_chirp.m               # LFM phase integration & Hann window synthesis
│   ├── dac_quantize.m                     # 12-bit DAC quantization & SQNR metrics
│   ├── channel_model.m                    # Ainslie-McColm absorption & transmission loss
│   ├── evaluate_profile_performance.m     # Priority 1 evaluation engine mirror
│   ├── adaptive_controller.m              # Schmitt-trigger hysteresis & N=2 debounce
│   ├── power_model.m                      # Duty-cycle power model
│   ├── export_c_headers.m                 # Prototype C header exporter
│   ├── run_simulation.m                   # Master simulation runner (Figures 1–13)
│   ├── run_experiments.m                  # Priority 1 parameter sweeps (Figures 14–20)
│   ├── run_validation_suite.m             # 23-point MATLAB verification suite
│   ├── run_profile_evaluation_tests.m     # 12-point MATLAB profile evaluation suite
│   ├── adaptive_sonar_dashboard.m         # Interactive MATLAB GUI dashboard app
│   ├── generate_matlab_results.py         # Headless Python mirror to run MATLAB pipeline
│   └── README.md                          # MATLAB architecture guide
│
├── outputs/                               # Python Generated Artifacts
│   ├── plots/                             # 4 comprehensive signal analysis figures
│   ├── headers/                           # C99 LUT headers (muddy, balanced, clear, master)
│   └── canonical_profile_results.json     # Reference baseline JSON dataset
│
├── outputs_matlab/                        # MATLAB Mirror Generated Artifacts
│   ├── plots/                             # All 20 engineering figures (01 to 13, exp01 to 07)
│   └── headers/                           # Exported C headers mirror
│
├── generate_report_docx.py                # Compiles 70-page Digital Twin Engineering Report
├── generate_results_report.py             # Compiles Complete Results Interpretation Report
├── report_sections_part1..4.py            # Modular report section generators (Architecture)
└── results_sections_part1..4.py           # Modular report section generators (Results)
```

---

## 11. Developer & Agent Fast-Track Runbook

### Environment Setup
```bash
python -m venv .venv
.venv\Scripts\activate       # On Linux / macOS: source .venv/bin/activate
pip install -r requirements.txt
```

### Running Tests
```bash
# Run all 79 unit tests in Pytest
pytest -v

# Run unittest suite (66 tests)
python -m unittest discover -s tests -p "test_*.py" -v
```

### Running Simulations & Generating Visualizations
```bash
# Generate baseline Python waveforms, spectra, and timelines into outputs/plots/
python src/main.py

# Generate Priority 1 experiment figures into outputs/plots/
python -m src.experiments

# Generate all 20 MATLAB engineering figures into outputs_matlab/plots/ (No MATLAB license required)
python matlab/generate_matlab_results.py
```

### Building & Verifying STM32 Firmware
```bash
cd firmware
# Verify syntax, types, and headers with host GCC:
mingw32-make host            # On Linux / macOS: make host

# When arm-none-eabi-gcc is available:
make target
cd ..
```

### Compiling Comprehensive Word Reports
```bash
# Generates AUV_Adaptive_Sonar_Digital_Twin_Engineering_Report.docx
python generate_report_docx.py

# Generates AUV_Adaptive_Sonar_Complete_Results_and_Output_Interpretation_Report.docx
python generate_results_report.py
```

---

## 12. Future Work & Hardware Bring-Up Roadmap

All performance figures depending on real silicon or physical acoustics remain **`[PENDING HARDWARE VALIDATION]`**.

### Priority Next Steps:
1. **Physical Lab Bench Bring-Up:** Follow [hardware_bringup_checklist.md](file:///d:/AUV%20sonar/firmware/hardware_bringup_checklist.md) on physical NUCLEO-G474RE board:
   - Verify 10.0 MHz clock output on PA8 (MCO).
   - Probe PB1 (`CN10 Pin 24`) using an oscilloscope with a **short coaxial ground spring** to avoid probe ground loop ringing.
   - Confirm 4.0 MSPS DAC update steps and smooth Hann window tapering.
   - Measure DC midscale voltage ($1.650\text{ V} \pm 25\text{ mV}$) and peak-to-peak output swing ($3.3\text{ V}_{\text{p-p}}$).
2. **Analog Reconstruction Filter:** Design and bench-test an external active low-pass reconstruction filter (e.g. 3rd-order Sallen-Key Bessel with cutoff $f_c \approx 600\text{ kHz}$) to suppress 4.0 MHz DAC sample-and-hold imaging artifacts.
3. **Piezoelectric Transducer Interfacing:** Measure real impedance of the subsea ceramic transducer across the $100\text{–}500\text{ kHz}$ band using an impedance analyzer; design an impedance matching network (inductor/transformer) between the power amplifier and transducer.
4. **Physical Hydrophone & Receiver Pipeline:** In future project phases beyond this transmitter payload, develop the hydrophone analog front-end (PGA, bandpass filter, ADC), matched-filter pulse compression DSP, and closed-loop echo SNR feedback.
