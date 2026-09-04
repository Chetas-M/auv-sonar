# Python Digital Twin Architecture (`src/`)

This directory contains the primary Python implementation of the **AUV Low-Power Adaptive Software-Defined Sonar Transmitter Digital Twin** (SIH Problem 26058).

It models the pre-silicon signal synthesis, adaptive channel decision logic, acoustic absorption modeling, and DMA memory architecture targeted for the **STMicroelectronics STM32G474** microcontroller.

---

## 1. Quickstart & Execution

```bash
# Run the complete end-to-end simulation pipeline
python src/main.py

# Run Priority 1 experiments and generate engineering figures
python -m src.experiments

# Generate canonical baseline results artifact
python src/generate_canonical_results.py
```

Outputs will be generated into:
- `outputs/plots/`: Signal waveforms, spectra, spectrograms, DAC error, and power timelines.
- `outputs/headers/`: C99 header lookup tables (`muddy_profile_lut.h`, `balanced_profile_lut.h`, `clear_profile_lut.h`, `sonar_profiles.h`).
- `outputs/canonical_profile_results.json`: Canonical reference baseline dataset.

---

## 2. Pipeline Flow & Module Architecture

```text
                               ENVIRONMENTAL INPUTS
                 (Range [m], Depth [m], Temp [°C], Salinity [PSU])
                                       │
                                       ▼
                             src/profile_evaluator.py
                  ┌────────────────────┼────────────────────┐
                  ▼                    ▼                    ▼
             Profile 1            Profile 2            Profile 3
          (LOW_FREQUENCY)         (BALANCED)        (HIGH_FREQUENCY)
          [100 - 220 kHz]      [200 - 400 kHz]      [350 - 500 kHz]
                  │                    │                    │
                  ▼                    ▼                    ▼
          5-Point Freq Eval    5-Point Freq Eval    5-Point Freq Eval
          Ainslie-McColm Abs   Ainslie-McColm Abs   Ainslie-McColm Abs
          Transmission Loss    Transmission Loss    Transmission Loss
          Propagation Margin   Propagation Margin   Propagation Margin
                  │                    │                    │
                  └────────────────────┼────────────────────┘
                                       ▼
                          Propagation Viability Filter
                         (Relative Margin >= -65.0 dB)
                                       │
                       ┌───────────────┴───────────────┐
                       ▼                               ▼
             Multiple Viable Profiles          Fail-Safe Condition
                       │                               │
                       ▼                               ▼
            Mission Objective Selector        Select LOW_FREQUENCY
            - Default: BALANCED (3.75 mm)     (Lowest Attenuation)
            - Directivity: HIGH_FREQUENCY
                       │                               │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                               src/adaptation.py
                       Directional Schmitt-Trigger Hysteresis
                             Debounce Filter (N = 2)
                                       │
                                       ▼
                       Atomic Ping-Boundary Profile Latch
                             (PRI = 20 ms, 50 Hz)
                                       │
                                       ▼
                               src/waveform.py
                     LFM Chirp Phase Integration (4.0 MSPS)
                          Symmetric Hann Window Taper
                          12-Bit Unsigned DAC Quantization
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
             src/export_c.py                     src/power_model.py
       C99 Firmware Header Tables            Transmitter Duty-Cycle Model
        (8,000 half-words each)              (0.540 W Average Power)
```

---

## 3. Module Breakdown

### `config.py` — Single Source of Truth
Central configuration defining all locked hardware and simulation parameters:
- **DAC Sample Rate ($F_s$):** `4,000,000 Hz` ($4.0\text{ MSPS}$, $T_s = 250\text{ ns}$).
- **DAC Resolution:** `12-bit unsigned` ($0\text{ to }4095$, midscale $2048$).
- **Pulse Duration ($T_p$):** `0.002 s` ($2.0\text{ ms}$, $N_p = 8,000\text{ samples}$).
- **Pulse Repetition Interval ($\text{PRI}$):** `0.020 s` ($20.0\text{ ms}$, $50\text{ Hz}$ ping rate).
- **Target Microcontroller:** `STM32G474` ($160.0\text{ MHz}$ PLL clock).
- **Power Assumptions:** $P_{\text{active}} = 5.0\text{ W}$, $P_{\text{idle}} = 45\text{ mW}$, $P_{\text{elec}} = 0.30\text{ W}$, $V_{\text{bat}} = 12.0\text{ V}$, $E_{\text{bat}} = 99\text{ Wh}$.

### `profiles.py` — Canonical Profile Definitions
Defines the `ProfileType` enumeration and `BandProfile` dataclass for the three transmission profiles:
- **`LOW_FREQUENCY` (Profile 1):** $100.0\text{–}220.0\text{ kHz}$ ($f_c = 160\text{ kHz}, B = 120\text{ kHz}$, Amplitude $A = 1.0$). Long-range fallback mode.
- **`BALANCED` (Profile 2):** $200.0\text{–}400.0\text{ kHz}$ ($f_c = 300\text{ kHz}, B = 200\text{ kHz}$, Amplitude $A = 0.7$). Optimal survey resolution mode ($\Delta R \approx 3.75\text{ mm}$).
- **`HIGH_FREQUENCY` (Profile 3):** $350.0\text{–}500.0\text{ kHz}$ ($f_c = 425\text{ kHz}, B = 150\text{ kHz}$, Amplitude $A = 0.4$). High directivity spatial resolution mode.

### `waveform.py` — Signal Synthesis & DAC Quantization
- **`generate_lfm_chirp(...)`:** Synthesizes time-domain LFM chirps using exact continuous phase integration:
  $$\phi(t) = 2\pi \left( f_{\text{start}} t + \frac{k}{2} t^2 \right), \quad k = \frac{f_{\text{stop}} - f_{\text{start}}}{T_p}$$
- **Windowing:** Applies symmetric Hann window $w[n] = 0.5(1 - \cos(2\pi n / (N-1)))$ to taper turn-on/turn-off transients and suppress out-of-band sidelobes.
- **DAC Quantization:** Quantizes continuous float $[-1.0, +1.0]$ into unsigned 12-bit integers:
  $$\text{Code} = \text{round}\left(2048 + 2047 \cdot x_{\text{windowed}}[n]\right) \in [0, 4095]$$
- **SQNR Estimation:** Validates theoretical signal-to-quantization-noise ratio ($\sim 69.7\text{ dB}$).

### `profile_evaluator.py` — Priority 1 Profile Evaluation Engine
- **5-Point Discrete Frequency Evaluation:** Computes acoustic attenuation at 5 points evenly spaced across each profile's bandwidth ($f_{\text{start}}, f_1, f_c, f_2, f_{\text{stop}}$).
- **Acoustic Absorption:** Implements Ainslie-McColm (1998) seawater absorption model with boric acid relaxation ($\text{B(OH)}_3$), magnesium sulfate relaxation ($\text{MgSO}_4$), and pure water viscosity terms, including depth pressure correction.
- **Transmission Loss ($TL$):** Spherical spreading plus frequency-dependent attenuation:
  $$TL(f, R) = 20\log_{10} R + \alpha(f) \cdot \frac{R}{1000}$$
- **Propagation Viability Filter:** Rejects any profile whose modeled relative margin falls below the $-65.0\text{ dB}$ viability threshold.
- **Mission Objective Selector:** Chooses among viable profiles:
  - `SURVEY_MODE`: Selects `BALANCED` for best theoretical range resolution ($\Delta R = 3.75\text{ mm}$).
  - `DIRECTIVITY_MODE`: Selects `HIGH_FREQUENCY` for highest theoretical spatial directivity ($1.417\times$ reference).
  - Long-range fallback: Automatically falls back to `LOW_FREQUENCY` beyond $175\text{ m}$.

### `physics_reference.py` — Acoustic Physics Reference Implementations
Contains canonical, reference-grade implementations of underwater acoustic equations for cross-verification:
- **Ainslie & McColm (1998):** Seawater acoustic absorption formula.
- **Francois & Garrison (1982):** Secondary absorption cross-check.
- **Mackenzie (1981):** Nine-term sound speed equation as a function of temperature ($T$), salinity ($S$), and depth ($D$).
- **Hydrostatic Factor:** Validates the $P_2 = \exp(-D / 6000)$ depth pressure factor on magnesium sulfate relaxation.

### `adaptation.py` — Control Logic & State Machine
- **`AnalogInputs`:** Data container emulating 3 external analog potentiometer inputs: Turbidity ($0\text{–}100\text{ NTU}$), Range/Depth ($10\text{–}200\text{ m}$), and Target Strength / SNR ($0\text{–}100\%$).
- **`HysteresisThreshold`:** Implements directional Schmitt-trigger deadbands ($\pm 5\%$) to reject ADC thermal noise.
- **`AdaptationEngine`:** Enforces debounce persistence ($N=2$ consecutive pings) to eliminate state fluttering.
- **`PingController`:** Latches profile transitions strictly at ping repetition boundaries (compatible with DMA Transfer-Complete interrupts at $50\text{ Hz}$).

### `power_model.py` — Transmitter Power Dissipation Model
Models transmitter payload electrical consumption based on duty cycle:
$$D = \frac{T_p}{\text{PRI}} = \frac{2.0\text{ ms}}{20.0\text{ ms}} = 0.10 \quad (10.0\%)$$
$$P_{\text{avg}} = P_{\text{active}} \cdot D + P_{\text{idle}} \cdot (1 - D) = 5.0\text{ W}(0.10) + 0.045\text{ W}(0.90) = 0.540\text{ W}$$
Calculates battery operating hours against a hypothetical $99\text{ Wh}$ subsea pack ($\sim 183\text{ hours}$ for transmitter payload alone).

### `export_c.py` — C99 Header Lookup Table Generator
Translates quantized waveform arrays into compile-ready C source and header files for the STM32G474 firmware:
- Emits formatted `const uint16_t` arrays with 8,000 samples per profile.
- Emits macro definitions (`SAMPLE_RATE_HZ`, `PULSE_DURATION_US`, `SAMPLE_COUNT`, `DAC_BITS`).
- Generates `outputs/headers/sonar_profiles.h` and individual profile headers.

### `validation.py` — Signal & Controller Verification Suite
Executes the comprehensive 23-point signal verification test suite and exports validation figures into `outputs/plots/`.

### `experiments.py` — Priority 1 Parameter Sweeps & Figures
Executes Priority 1 sensitivity analyses across range, temperature, salinity, and depth, generating the 7 canonical experiment figures (`exp01` to `exp07`).

---

## 4. Programmatic Python API Example

```python
from src.config import DAC_SAMPLE_RATE_HZ, PULSE_DURATION_S
from src.profiles import BAND_PROFILES, ProfileType
from src.waveform import generate_lfm_chirp
from src.profile_evaluator import ProfilePerformanceEvaluator, MissionObjective

# 1. Synthesize a Balanced LFM Chirp
profile = BAND_PROFILES[ProfileType.BALANCED]
waveform = generate_lfm_chirp(profile, DAC_SAMPLE_RATE_HZ, PULSE_DURATION_S)

print(f"Synthesized {waveform.sample_count} samples.")
print(f"DAC Code Range: [{min(waveform.quantized_dac_codes)}, {max(waveform.quantized_dac_codes)}]")
print(f"Simulated SQNR: {waveform.simulated_sqnr_db:.2f} dB")

# 2. Evaluate Propagation & Select Profile at Range = 80 m
evaluator = ProfilePerformanceEvaluator()
decision = evaluator.select_best_profile(
    range_m=80.0,
    objective=MissionObjective.SURVEY_MODE
)

print(f"Selected Profile: {decision.selected_profile.value}")
print(f"Theoretical Range Resolution: {decision.resolution_m * 1000:.2f} mm")
print(f"Viability Confidence: {decision.viability_confidence:.2f}")
```
