# Simulink Scopes and Graphs: Comprehensive Technical Guide

**SIH Problem 26058: Low-Power, Real-Time Adaptive Software-Defined Sonar Transmitter Payload for Autonomous Underwater Vehicles (AUVs)**

This document provides a thorough engineering explanation of every graph, oscilloscope, display, and telemetry signal in the **AUV Adaptive Sonar Transmitter Simulink Digital Twin** ([`auv_sonar_transmitter_payload.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_transmitter_payload.slx), [`auv_sonar_mission_controller.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_mission_controller.slx), and [`auv_sonar_waveform_pipeline.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_waveform_pipeline.slx)).

---

## 1. Executive Architecture & Time Domains

The Simulink models operate across two distinct time scales reflecting the real microcontroller architecture:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PING-RATE MISSION TIME DOMAIN (Ts = PRI = 20.0 ms, 50 Hz Ping Rate, Total Duration = 3.0 s)      │
│  • Environmental sensing updates (Turbidity, Depth, Temperature, Salinity, Ambient Noise)        │
│  • Medium attenuation calculation via Ainslie-McColm absorption formula                          │
│  • Channel Quality Score Q evaluation & Directional Schmitt Hysteresis (0.30/0.40 & 0.65/0.75)    │
│  • N = 2 Debounce persistence counter & Atomic ping-boundary profile latching                    │
│  • Transmitter average power dissipation across 10% duty cycle (2.0 ms active, 18.0 ms idle)     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │ (Latched Profile ID & Amplitude)
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HIGH-SPEED DAC SAMPLE-RATE TIME DOMAIN (Ts = 250 ns, Fs = 4.0 MSPS, Np = 8000 Samples per Ping)  │
│  • Continuous-phase LFM chirp synthesis: phi(t) = 2*pi*(f0*t + 0.5*k*t^2)                       │
│  • Symmetric Hann window envelope tapering: w[n] = 0.5*(1 - cos(2*pi*n / (N-1)))                │
│  • 12-bit unsigned DAC quantization: 0 to 4095, midscale 2048, Vref = 3.3V                       │
│  • Quantization error residuals: bounded within [-0.5, +0.5] LSB (~0.806 mV/LSB)                 │
│  • STM32G474 OPAMP3 High-Speed Follower (45 V/us slew rate, Pin PB1) & AC coupling              │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. In-Model Simulink Oscilloscopes & Telemetry Blocks

### 2.1 Scope 1: `Scope_Channel_Adaptation_Report_Fig09_12`
Located in: [`auv_sonar_transmitter_payload.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_transmitter_payload.slx) and [`auv_sonar_mission_controller.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_mission_controller.slx)

#### Channel 1: Channel Quality Score $Q(t)$
- **Plotted Quantity**: Non-dimensional quality metric $Q \in [0.0, 1.0]$.
- **Physical Meaning**: Predicts medium suitability for high-frequency transmission. $Q=1.0$ represents pristine calm water with minimal absorption; $Q=0.0$ represents severe channel degradation.
- **Governing Equation** ([`channel_model.m`](file:///c:/AUV/auv-sonar/matlab/channel_model.m)):
  $$Q = w_{\text{env}} Q_{\text{env}} + w_{\text{attn}} Q_{\text{attn}} + w_{\text{noise}} Q_{\text{noise}}$$
  where:
  - $Q_{\text{env}} = 1.0 - \frac{\text{turb}}{100}$ (Particulate scattering penalty, weight $w_{\text{env}} = 0.50$)
  - $Q_{\text{attn}} = 1.0 - \min\left(1.0, \frac{\alpha_{\text{total}}}{160.0}\right)$ (Ainslie-McColm absorption at $425\text{ kHz}$, weight $w_{\text{attn}} = 0.25$)
  - $Q_{\text{noise}} = 1.0 - \min\left(1.0, \frac{\text{noise} - 40.0}{40.0}\right)$ (Ambient noise penalty, weight $w_{\text{noise}} = 0.25$)
- **Simulation Behavior**: Between $t = 1.0\text{ s}$ and $t = 1.8\text{ s}$, the AUV enters a simulated sediment plume where turbidity spikes from $15\text{ NTU}$ to $85\text{ NTU}$. $Q(t)$ rapidly drops from $0.65$ to below $0.30$.

#### Channel 2: Profile Selection State (Active vs Candidate)
- **Plotted Quantity**: Discrete profile integer IDs:
  - `1`: `LOW_FREQUENCY` ($100\text{--}220\text{ kHz}$, $f_c = 160\text{ kHz}, B = 120\text{ kHz}$)
  - `2`: `BALANCED` ($200\text{--}400\text{ kHz}$, $f_c = 300\text{ kHz}, B = 200\text{ kHz}$)
  - `3`: `HIGH_FREQUENCY` ($350\text{--}500\text{ kHz}$, $f_c = 425\text{ kHz}, B = 150\text{ kHz}$)
- **Underlying Logic (Directional Schmitt Hysteresis & Debounce)**:
  - **Directional Deadbands**:
    - Low $\leftrightarrow$ Balanced: Upgrade threshold is $Q > 0.40$; downgrade threshold is $Q \le 0.30$. The deadband $[0.30, 0.40]$ prevents rapid hunting when $Q$ hovers around $0.35$.
    - Balanced $\leftrightarrow$ High: Upgrade threshold is $Q \ge 0.75$; downgrade threshold is $Q < 0.65$. The deadband $[0.65, 0.75]$ prevents oscillations under marginal high-band conditions.
  - **$N = 2$ Debounce Persistence Filter**: When $Q$ drops below $0.30$, candidate profile immediately shifts to $1$. However, the controller increments an internal debounce counter. The active profile will NOT transition until candidate $1$ holds for $2$ consecutive ping periods ($40\text{ ms}$). This rejects false alarms caused by acoustic noise bursts or transient particulate spikes.
  - **Atomic Ping-Boundary Latching**: The active profile update occurs strictly at the start of a ping interval. The transmission waveform DMA transfer is never interrupted mid-pulse.

#### Channel 3: Transmit Amplitude Policy $A(t)$
- **Plotted Quantity**: Digital scaling factor $A \in [0.40, 1.00]$.
- **Logic**:
  - `LOW_FREQUENCY`: $A = 1.00$ ($0\text{ dB}$, full DAC swing) to overcome severe absorption and deliver maximum penetrating acoustic energy.
  - `BALANCED`: $A = 0.70$ ($-3.1\text{ dB}$) for nominal survey range and power conservation.
  - `HIGH_FREQUENCY`: $A = 0.40$ ($-7.96\text{ dB}$) to limit peak output power and prevent analog stage clipping.

---

### 2.2 Scope 2: `Scope_Power_Battery_Report_Fig13`
Located in: [`auv_sonar_transmitter_payload.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_transmitter_payload.slx) and [`auv_sonar_mission_controller.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_mission_controller.slx)

#### Channel 1: Transmitter Average Power $P_{\text{avg}}(t)$ (Watts)
- **Plotted Quantity**: Modeled average electric power dissipation across each $20.0\text{ ms}$ PRI.
- **Governing Equations** ([`power_model.m`](file:///c:/AUV/auv-sonar/matlab/power_model.m)):
  $$P_{\text{active}} = P_{\text{elec}} + (P_{\text{active,max}} - P_{\text{elec}}) A^2 = 0.300 + 4.700 A^2\text{ W}$$
  $$P_{\text{avg}} = P_{\text{active}} \cdot D + P_{\text{idle}} \cdot (1 - D)$$
  where nominal duty cycle $D = \frac{T_p}{\text{PRI}} = \frac{2.0\text{ ms}}{20.0\text{ ms}} = 0.10$ ($10.0\%$), and $P_{\text{idle}} = 0.045\text{ W}$ ($45\text{ mW}$).
- **Observed Values**:
  - Default survey mode (`BALANCED`, $A = 0.70$): $P_{\text{active}} \approx 2.60\text{ W} \implies P_{\text{avg}} \approx 0.301\text{ W}$.
  - Degraded channel fallback (`LOW_FREQUENCY`, $A = 1.00$): $P_{\text{active}} = 5.00\text{ W} \implies P_{\text{avg}} \approx 0.540\text{ W}$.
  - Narrow-beam mode (`HIGH_FREQUENCY`, $A = 0.40$): $P_{\text{active}} \approx 1.05\text{ W} \implies P_{\text{avg}} \approx 0.146\text{ W}$.

#### Channel 2: Average Battery Bus Current $I_{\text{avg}}(t)$ (mA)
- **Plotted Quantity**: DC current supplied by the primary subsea $12.0\text{ V}$ power bus:
  $$I_{\text{avg}} = \frac{P_{\text{avg}}}{V_{\text{bat}}} \times 1000\text{ mA} = \frac{P_{\text{avg}}}{12.0} \times 1000$$
- Ranges between $12.2\text{ mA}$ (High Freq), $25.1\text{ mA}$ (Balanced), and $45.0\text{ mA}$ (Low Freq).

#### Channel 3: Theoretical Transmitter-Only Battery Endurance (Hours)
- **Plotted Quantity**: Estimated operational lifespan against a hypothetical $99.0\text{ Wh}$ battery pack:
  $$T_{\text{endurance}} = \frac{E_{\text{bat}}}{P_{\text{avg}}} = \frac{99.0\text{ Wh}}{P_{\text{avg}}}$$
- Yields $\approx 329\text{ hours}$ in Balanced mode and $\approx 183\text{ hours}$ under continuous Low Frequency full-power transmission.
- *Strict Scope Note*: This models the transmitter payload alone; total AUV operational endurance is dominated by propulsion thrusters, navigation computers, and auxiliary sensors.

---

### 2.3 Scope 3: `Scope_Waveform_Detail`
Located in: [`auv_sonar_waveform_pipeline.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_waveform_pipeline.slx)

#### Channel 1: Synthesized Continuous-Phase Waveform $x(t)$
- **Plotted Quantity**: Normalized time-domain chirp amplitude spanning $t = 0$ to $2.0\text{ ms}$ at $4.0\text{ MSPS}$ ($8000\text{ samples}$).
- **Mathematical Formulation** ([`generate_lfm_chirp.m`](file:///c:/AUV/auv-sonar/matlab/generate_lfm_chirp.m)):
  $$\phi(t) = 2\pi \left(f_0 t + \frac{1}{2} k t^2\right), \quad k = \frac{f_1 - f_0}{T_p}$$
  $$x(t) = A \cdot \cos(\phi(t)) \cdot 0.5 \left(1 - \cos\left(\frac{2\pi t}{T_p}\right)\right)$$
- **Why the shape appears this way**: The sinusoidal oscillations accelerate in frequency from left to right ($200\text{ kHz} \to 400\text{ kHz}$ for BALANCED). The smooth Hann envelope enforces zero-amplitude endpoints ($x(0) = 0$ and $x(T_p) = 0$), completely eliminating the sharp spectral splatter and DC transients that would occur with rectangular pulse gating.

#### Channel 2: Instantaneous Acoustic Frequency $f_{\text{inst}}(t)$ (kHz)
- **Plotted Quantity**: Trajectory of carrier frequency across the pulse:
  $$f_{\text{inst}}(t) = \frac{1}{2\pi} \frac{d\phi}{dt} = f_0 + k t$$
- Shows a linear frequency ramp rising from $200.0\text{ kHz}$ to $400.0\text{ kHz}$ at chirp slope $k = 100.0\text{ MHz/s}$ ($100.0\text{ Hz/\mu s}$).

#### Channel 3: Hann Window Envelope $w(t)$
- **Plotted Quantity**: Envelope function $A \cdot w(t) = 0.70 \times 0.5(1 - \cos(2\pi t / T_p))$.
- Smoothly ramps up to peak amplitude $0.70$ at $t = 1.0\text{ ms}$ before symmetrically tapering to zero.

---

### 2.4 Scope 4: `Scope_DAC_Quantization`
Located in: [`auv_sonar_waveform_pipeline.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_waveform_pipeline.slx)

#### Channel 1: 12-Bit Unsigned Quantized DAC Codes
- **Plotted Quantity**: Unsigned integer codes in range $[0, 4095]$ targeting STM32G474 `DAC_DHR12R2` register.
- **Conversion Formula** ([`dac_quantize.m`](file:///c:/AUV/auv-sonar/matlab/dac_quantize.m)):
  $$\text{Code}[n] = \text{clamp}_{[0, 4095]} \left(\text{round}\left(2047.5 + 2047.5 \cdot x[n]\right)\right)$$
- **Key Characteristics**: Code $2048$ represents the analog midscale ($1.65\text{ V}$ bias). For $A = 0.70$, codes swing between $614$ and $3481$, leaving $\approx 614\text{ codes}$ of headroom at each rail to prevent saturation clipping.

#### Channel 2: Quantization Error Residuals $e[n]$ (LSB & mV)
- **Plotted Quantity**: Residual difference $e[n] = \text{Code}[n] - V_{\text{ideal}}[n]$ in Least Significant Bits (LSBs) and millivolts ($1\text{ LSB} \approx 0.806\text{ mV}$ on $3.3\text{V}$ reference).
- **Physical Validation**: The error trace is uniformly distributed noise strictly contained within $[-0.5, +0.5]\text{ LSB}$ ($\pm 0.403\text{ mV}$). The measured empirical Signal-to-Quantization-Noise Ratio is $\text{SQNR} \approx 66.6\text{ dB}$ (at $A=0.70$) and $\approx 69.7\text{ dB}$ (at $A=1.00$).

---

### 2.5 Scope 5: `Scope_Analog_Output`
Located in: [`auv_sonar_waveform_pipeline.slx`](file:///c:/AUV/auv-sonar/matlab/simulink/auv_sonar_waveform_pipeline.slx)

#### Channel 1: High-Speed Follower Output (Pin PB1 Voltage)
- **Plotted Quantity**: Voltage on STM32G474 Pin PB1 (Morpho CN10 Pin 24) in Volts ($0\text{--}3.3\text{ V}$).
- **Hardware Architecture**: On the STM32G474, the internal DAC buffer is high-impedance ($15\text{ k}\Omega$) and slow. It is explicitly bypassed by routing DAC3 Channel 2 on-chip directly to **OPAMP3** in High-Speed Follower mode. The OPAMP delivers a high slew rate of $45\text{ V}/\mu\text{s}$ (far exceeding the maximum required DAC slew of $\frac{3.3\text{ V}}{250\text{ ns}} = 13.2\text{ V}/\mu\text{s}$).

#### Channel 2: AC-Coupled Drive Voltage ($-1.65\text{ V}$ to $+1.65\text{ V}$)
- **Plotted Quantity**: Symmetrical AC signal after passing through a DC-blocking capacitor into the power amplifier stage, removing the $1.65\text{ V}$ DC offset.

---

## 3. Engineering Report Figures Breakdown (Figures 1 to 13)

The automated script [`generate_simulink_report_figures.m`](file:///c:/AUV/auv-sonar/matlab/simulink/generate_simulink_report_figures.m) saves the exact set of figures matching the Master Engineering Report into [`matlab/simulink/outputs/engineering_report/`](file:///c:/AUV/auv-sonar/matlab/simulink/outputs/engineering_report/):

| Figure File | Engineering Report Section | Visual Layout | Detailed Physical & Engineering Interpretation |
|---|---|---|---|
| **`01_time_domain_waveform.png`** | Section 5.1 (Figure 1) | 3 vertically stacked subplots | **Time-domain waveforms for all 3 canonical profiles** (`LOW`, `BALANCED`, `HIGH`). Shows exact phase continuity and the smooth Hann envelope (red dashed curves) enforcing zero-amplitude at $t=0$ and $t=2.0\text{ ms}$, preventing transient high-frequency spectral leakage. |
| **`02_zoomed_waveform_section.png`** | Section 5.2 (Figure 2) | Microscopic 80 µs time slice | **DAC stair-step quantization tracking**. Displays continuous ideal curve (blue) versus 12-bit discrete staircase (red) updating at $T_s = 250\text{ ns}$ ($4.0\text{ MSPS}$), verifying that the DAC resolution accurately tracks ultrasonic dynamics without slope overload. |
| **`03_instantaneous_frequency.png`** | Section 5.3 (Figure 3) | Linear trajectory with dashed bounds | **Linear Frequency Modulation trajectory**. Verifies exact linear chirp slope ($k = 100.0\text{ MHz/s}$) starting at $f_0 = 200\text{ kHz}$ and terminating at $f_1 = 400\text{ kHz}$. |
| **`04_fft_spectrum.png`** | Section 5.4 (Figure 4) | 32,768-point FFT magnitude spectrum | **Spectral passband & stopband suppression**. Shows flat passband across $200\text{--}400\text{ kHz}$ and $>50\text{ dB}$ sidelobe attenuation achieved by Hann windowing, preventing out-of-band harmonics from interfering with adjacent acoustic instruments. |
| **`05_spectrogram.png`** | Section 5.5 (Figure 5) | 2D STFT spectrogram heat map | **Time-frequency energy concentration**. Shows a straight, continuous diagonal ridge from $(0\text{ ms}, 200\text{ kHz})$ to $(2.0\text{ ms}, 400\text{ kHz})$ with no parasitic spurs, mode hopping, or phase discontinuities. |
| **`06_dac_quantization_error.png`** | Section 5.6 (Figure 6) | Residual error time series | **DAC quantization error distribution**. Confirms error is zero-mean random roundoff strictly confined within the theoretical $[-0.5, +0.5]\text{ LSB}$ boundaries ($\pm 0.403\text{ mV}$), with an RMS error of $0.288\text{ LSB}$. |
| **`07_dac_code_histogram.png`** | Section 5.7 (Figure 7) | 64-bin integer histogram | **DAC integer code distribution**. Exhibits a classic arcsine-like distribution centered around midscale code $2048$, confirming full dynamic utilization without saturation at $0$ or $4095$. |
| **`08_profile_comparison.png`** | Section 5.8 (Figure 8) | Triple-curve spectral overlay | **Spectral comparison of all 3 transmission profiles**. Visualizes the frequency separation: Profile 1 ($100\text{--}220\text{ kHz}$, orange), Profile 2 ($200\text{--}400\text{ kHz}$, blue), and Profile 3 ($350\text{--}500\text{ kHz}$, green), highlighting the transition overlap bands. |
| **`09_channel_quality_timeline.png`** | Section 5.9 (Figure 9) | Quality score Q vs thresholds | **Environmental adaptation timeline**. Shows $Q(t)$ plunging from $0.65$ to $0.20$ as the sediment plume hits, plotted against the 4 directional Schmitt trigger thresholds ($0.75, 0.65, 0.40, 0.30$). |
| **`10_candidate_profile_timeline.png`** | Section 5.10 (Figure 10) | Raw candidate stepped trace | **Raw candidate evaluation timeline**. Displays instantaneous recommendations from the channel evaluator before filtering, showing sensitivity to noise perturbations. |
| **`11_active_profile_timeline.png`** | Section 5.11 (Figure 11) | Solid committed active profile trace | **Committed active profile timeline**. Shows rock-solid active profile switching from BALANCED to LOW_FREQUENCY during the plume event, without high-frequency chattering or premature triggering. |
| **`12_hysteresis_debounce_demo.png`** | Section 5.12 (Figure 12) | 2-panel zoomed detail ($1.0 \to 1.8\text{ s}$) | **Hysteresis deadband & $N=2$ debounce demonstration**. Subplot 1 shows $Q$ crossing thresholds; Subplot 2 shows candidate switching, holding for $2$ consecutive ping cycles ($40\text{ ms}$), and latching into the active profile at the subsequent ping boundary. |
| **`13_estimated_power_summary.png`** | Section 5.13 (Figure 13) | 2-panel power timeline & bar chart | **Transmitter power & sensitivity analysis**. Left panel shows average power timeline ($0.30\text{ W} \to 0.54\text{ W}$ during plume fallback). Right panel compares sensitivity across pulse durations ($1, 2, 3\text{ ms}$) and amplitudes ($1.0, 0.7, 0.4$). |

---

## 4. Parameter Single Source of Truth Summary

| Parameter | Symbol | Nominal Value | Hardware Justification |
|---|---|---|---|
| **DAC Sample Rate** | $F_s$ | $4.0\text{ MSPS}$ | $T_s = 250\text{ ns}$ (Timer TRGO triggered DMA) |
| **DAC Resolution** | — | $12\text{-bit unsigned}$ | Codes $0\text{--}4095$, midscale $2048$ ($1.65\text{ V}$ bias) |
| **Pulse Duration** | $T_p$ | $2.0\text{ ms}$ | $N_p = 8000\text{ samples}$ ($16\text{ KB}$ per ping buffer) |
| **Ping Interval** | $\text{PRI}$ | $20.0\text{ ms}$ | $50\text{ Hz}$ ping rate, $10.0\%$ duty cycle |
| **Profile 1 (`LOW_FREQ`)** | — | $100\text{--}220\text{ kHz}, A=1.0$ | Lowest seawater absorption ($64\text{ dB/km}$); long-range fallback |
| **Profile 2 (`BALANCED`)** | — | $200\text{--}400\text{ kHz}, A=0.7$ | Highest bandwidth ($B=200\text{ kHz}$); best range resolution ($\Delta R = 3.75\text{ mm}$) |
| **Profile 3 (`HIGH_FREQ`)** | — | $350\text{--}500\text{ kHz}, A=0.4$ | Highest theoretical directivity ($1.417\times$); angular resolution mode |
| **Thresholds** | — | $0.40/0.30$ and $0.75/0.65$ | Directional Schmitt hysteresis deadbands |
| **Debounce Count** | $N$ | $2\text{ pings}$ | Consecutive cycle persistence filter ($40\text{ ms}$) |
