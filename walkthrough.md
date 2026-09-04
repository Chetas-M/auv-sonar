# Engineering Walkthrough: AUV Adaptive Sonar Transmitter Digital Twin

A Python- and MATLAB-based engineering digital twin simulator for the transmitter payload of a low-power adaptive software-defined sonar designed for Autonomous Underwater Vehicles (AUVs), implementing **SIH Problem 26058**.

---

> [!IMPORTANT]
> **Standard Engineering Scope Statement**:
> This simulator validates pre-silicon waveform synthesis, adaptation logic, DAC quantization, DMA buffer sizing, and estimated duty-cycle power dissipation. It does not validate physical transducer impedance, acoustic ocean propagation, analog settling, amplifier stability, or actual vehicle power consumption.

---

## 1. System Architecture & Technical Specifications

```text
                      ┌───────────────────────────────────────┐
                      │       Simulated Analog Inputs         │
                      │ 3 Potentiometers: Turbidity, Range,   │
                      │ Target Strength (Emulates RX SNR)     │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │       Hysteresis State Machine        │
                      │     10% Deadband & Debounce (N=2)     │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │         Atomic Ping Boundary          │
                      │      Latch (PRI = 20.0 ms, 50 Hz)     │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │        LFM Phase Integration          │
                      │        & Hann Window Tapering         │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │      12-Bit DAC Quantization          │
                      │    (4.0 MSPS, Code: 0 to 4095)        │
                      └───────────────────┬───────────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
                   ▼                                             ▼
    ┌─────────────────────────────┐               ┌─────────────────────────────┐
    │  Firmware-Ready C Headers   │               │   Duty-Cycle Power Model    │
    │ (8,000 uint16_t half-words) │               │ (P_avg ~ 0.54 W @ 10% Duty) │
    └─────────────────────────────┘               └─────────────────────────────┘
```

### Profile Specifications (at $F_s = 4.0\text{ MSPS}$, $T_p = 2.0\text{ ms}$, $\text{PRI} = 20.0\text{ ms}$)

| Parameter | Profile 1: `LOW_FREQUENCY` | Profile 2: `BALANCED` (Default) | Profile 3: `HIGH_FREQUENCY` |
|---|---|---|---|
| **Frequency Sweep** | $100.0 \to 220.0\text{ kHz}$ | $200.0 \to 400.0\text{ kHz}$ | $350.0 \to 500.0\text{ kHz}$ |
| **Center Freq ($f_c$)** | $160.0\text{ kHz}$ | $300.0\text{ kHz}$ | $425.0\text{ kHz}$ |
| **Bandwidth ($B$)** | $120.0\text{ kHz}$ | $200.0\text{ kHz}$ | $150.0\text{ kHz}$ |
| **Amplitude Scale ($A$)**| $1.00$ ($0\text{ dB}$) | $0.70$ ($-3.1\text{ dB}$) | $0.40$ ($-8.0\text{ dB}$) |
| **Acoustic Rationale** | Lowest absorption envelope ($18\text{ dB/km}$); long-range fallback | Maximum bandwidth; best theoretical range resolution ($\Delta R = 3.75\text{ mm}$) | Highest frequency directivity ($1.417\times$ reference) |
| **Sample Count ($N_p$)**| $8,000\text{ samples}$ | $8,000\text{ samples}$ | $8,000\text{ samples}$ |
| **Memory Footprint** | $16.0\text{ KB}$ ($15.62\text{ KiB}$) | $16.0\text{ KB}$ ($15.62\text{ KiB}$) | $16.0\text{ KB}$ ($15.62\text{ KiB}$) |
| **STM32 SRAM Load** | $12.5\%$ of $128\text{ KB}$ active | $12.5\%$ of $128\text{ KB}$ active | $12.5\%$ of $128\text{ KB}$ active |
| **Flash Load (All 3)** | \multicolumn{3}{c|}{$48.0\text{ KB}$ ($9.37\%$ of $512\text{ KB}$ Flash on STM32G474)} |
| **Simulated SQNR** | $69.67\text{ dB}$ | $69.67\text{ dB}$ | $69.70\text{ dB}$ |

---

## 2. Signal Validation & Visualizations

The digital twin generates high-resolution figures in `outputs/plots/` and `outputs_matlab/plots/`:

- **Single Pulse Analysis** (`outputs/plots/single_pulse_analysis.png`): Time-domain chirp waveform, 80 µs DAC step detail, FFT magnitude spectrum ($>50\text{ dB}$ sidelobe rejection), and STFT linear frequency ridge.
- **Quantization Analysis** (`outputs/plots/quantization_analysis.png`): Quantization error time series bounded strictly within $[-0.5, +0.5]\text{ LSB}$ ($\pm 0.403\text{ mV}$), code histogram centered at midscale $2048$, and SQNR metric card ($69.67\text{ dB}$).
- **Profile Comparison** (`outputs/plots/profile_comparison.png`): Spectral overlay and envelope comparison across all three canonical transmission bands.
- **Dynamic Simulation Timeline** (`outputs/plots/dynamic_simulation_timeline.png`): 150-ping timeline verifying potentiometer noise rejection, directional Schmitt-trigger hysteresis, $N=2$ debounce, and duty-cycle power dissipation.

### Key Engineering Observations:
1. **Continuous Phase Integration:** Exact numerical integration of instantaneous angular frequency eliminates phase jumps across the chirp sweep.
2. **Spectral Discontinuity Mitigation:** Symmetric Hann windowing smoothly tapers the pulse endpoints to zero, suppressing turn-on transients and attenuating out-of-band spectral sidelobes.
3. **DAC Quantization Modeling:** A 12-bit unsigned DAC running at $4.0\text{ MSPS}$ yields $\sim 69.7\text{ dB}$ simulated SQNR, with errors strictly bounded within $\pm 0.5\text{ LSB}$.
4. **Hysteresis Noise Immunity:** Potentiometer wiper noise ($\sigma = 0.02$) is rejected by the $\pm 5\%$ deadband; profile transitions occur strictly at ping repetition boundaries.

---

## 3. Power Model & Duty-Cycle Estimations

> [!WARNING]
> **Payload-Only Scope for Endurance**:
> The endurance figures below represent **only the modeled transmitter payload load alone** against a hypothetical $99\text{ Wh}$ battery pack. They **do NOT represent full AUV mission life**, which is dominated by thrusters, navigation computers, INS/DVL, cameras, and comms.

Equations applied:
$$\text{Duty Cycle } (D) = \frac{T_{\text{pulse}}}{\text{PRI}} = \frac{2.0\text{ ms}}{20.0\text{ ms}} = 10.0\%$$
$$P_{\text{avg}} = P_{\text{active}} \cdot D + P_{\text{idle}} \cdot (1 - D) = 5.0\text{ W} \times 0.10 + 0.045\text{ W} \times 0.90 = 0.540\text{ W}$$
$$I_{\text{avg}} = \frac{P_{\text{avg}}}{V_{\text{bat}}} = \frac{0.540\text{ W}}{12.0\text{ V}} = 45.0\text{ mA}$$

| Operating Mode | Pulse Duration | PRI | Duty Cycle | Average Power | Current @ 12V | TX Endurance (99 Wh Pack) |
|---|---|---|---|---|---|---|
| **Short (Near-Field)** | $1.0\text{ ms}$ | $20.0\text{ ms}$ | $5.0\%$ | $0.293\text{ W}$ | $24.4\text{ mA}$ | **$338.2\text{ hours}$ (TX alone)** |
| **Nominal Survey ($A=1.0$)** | $2.0\text{ ms}$ | $20.0\text{ ms}$ | $10.0\%$ | $0.540\text{ W}$ | $45.0\text{ mA}$ | **$183.2\text{ hours}$ (TX alone)** |
| **Long (Far-Range)** | $3.0\text{ ms}$ | $20.0\text{ ms}$ | $15.0\%$ | $0.788\text{ W}$ | $65.7\text{ mA}$ | **$125.6\text{ hours}$ (TX alone)** |
| **Strong Target ($A=0.4$)** | $2.0\text{ ms}$ | $20.0\text{ ms}$ | $10.0\%$ | $0.146\text{ W}$ | $12.1\text{ mA}$ | **$679.5\text{ hours}$ (TX alone)** |

---

## 4. Firmware-Ready C Headers & Memory Layout

Waveform LUTs are exported as C99 headers in `outputs/headers/` and `firmware/Inc/`:

1. [`chirp_muddy.h`](file:///d:/AUV%20sonar/outputs/headers/chirp_muddy.h): 8,000 samples for $100\text{–}220\text{ kHz}$ chirp table (`CHIRP_MUDDY_LUT`).
2. [`chirp_balanced.h`](file:///d:/AUV%20sonar/outputs/headers/chirp_balanced.h): 8,000 samples for $200\text{–}400\text{ kHz}$ chirp table (`CHIRP_BALANCED_LUT`).
3. [`chirp_clear.h`](file:///d:/AUV%20sonar/outputs/headers/chirp_clear.h): 8,000 samples for $350\text{–}500\text{ kHz}$ chirp table (`CHIRP_CLEAR_LUT`).
4. [`sonar_profiles.h`](file:///d:/AUV%20sonar/outputs/headers/sonar_profiles.h): Master registration table with `SonarProfileDescriptor_t` structs for direct lookup by profile ID.

---

## 5. Automated Verification Results (79 Tests Passing)

The test suite in [`tests/`](file:///d:/AUV%20sonar/tests/README.md) passes 100% across all 79 automated checks:

- **Hardware & Signal DSP Suite (36 tests)**: $8,000$ samples, $2.0\text{ ms}$ duration, $100\text{ MHz/s}$ slope, Hann tapering, 12-bit DAC bounds, $2048$ midscale, SQNR $\ge 69.5\text{ dB}$, deadband hysteresis, $N=2$ debounce, ping-boundary latching, and C header round-trip integrity.
- **Priority 1 Profile Evaluation Suite (12 tests)**: 5-point discrete frequency evaluation, positive finite attenuation, monotonic transmission loss with range, baseline attenuation ordering ($\text{HIGH} > \text{BALANCED} > \text{LOW}$), range resolution ordering ($\text{BALANCED}$ best at $3.75\text{ mm}$), theoretical directivity ordering ($\text{HIGH}$ highest), and long-range viability fallback.
- **Acoustic Physics & Hydrostatic Regression Suite (9 tests)**: Hydrostatic depth factor $P_2 = \exp(-D/6000)$ regression, Ainslie-McColm parity against reference literature ($<10^{-10}$ error), canonical baseline constants, and JSON artifact integrity.
- **MATLAB Architecture Parity Suite (9 tests)**: Mathematical and structural parity across all 18 MATLAB `.m` files.
- **STM32 Firmware LUT Parity Suite (13 tests)**: Bit-exact parity ($0\text{ LSB}$ max error) between Python waveforms and C firmware header tables.

```bash
python -m pytest tests/ -v
# ============================= 79 passed in 1.85s ==============================
```

---

## 6. STM32G474 Hardware Bring-Up Reference

For physical hardware bring-up on the NUCLEO-G474RE development board:
1. Review the [STM32G4 DAC Feasibility Audit](file:///d:/AUV%20sonar/firmware/stm32g4_dac_feasibility_audit.md) for clock tree and analog op-amp follower rationale.
2. Follow the 8-step bring-up protocol in [hardware_bringup_checklist.md](file:///d:/AUV%20sonar/firmware/hardware_bringup_checklist.md).
3. Connect oscilloscope probe with coaxial ground spring to **PB1** (Morpho `CN10 Pin 24`) and **GND** (`CN10 Pin 20`).
