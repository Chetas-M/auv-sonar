# STM32G474 Sonar Transmitter Hardware Bring-Up Checklist

**Target Hardware:** STMicroelectronics NUCLEO-G474RE (STM32G474RET6, 64-pin LQFP)  
**Document Status:** BRING-UP PROCEDURE PROTOCOL  
**Notice:** No physical hardware is currently connected or tested. All hardware-dependent claims, scope timings, and settling performance are explicitly marked as **`[PENDING HARDWARE VALIDATION]`**.

---

## 1. Laboratory Equipment & Environmental Setup

Before applying power to the NUCLEO-G474RE board, assemble and verify the following laboratory instrumentation:

| Instrument | Minimum Specification | Recommended Model | Purpose |
|---|---|---|---|
| **Digital Storage Oscilloscope** | $\ge 100\text{ MHz}$ bandwidth, $\ge 1\text{ GSa/s}$ sample rate | Keysight InfiniiVision / R&S RTB2000 | 4.0 MSPS DAC step & chirp verification |
| **Oscilloscope Probes** | 10:1 passive probes ($\le 12\text{ pF}$ load) with **ground spring** | Standard 10:1 with ground spring accessory | High-frequency step response without ground bounce |
| **Digital Multimeter** | 4.5 digits DC voltage accuracy ($0.05\%$) | Fluke 87V / Keithley DMM6500 | VDD, VREF+, and midscale DC bias measurement |
| **Spectrum Analyzer / FFT** | DC to $5\text{ MHz}$ minimum frequency span | Oscilloscope Math FFT or Rigol DSA815 | Image frequency & harmonic distortion check |
| **Power Supply** | Low-noise regulated 5.0 V USB or 7.0–12.0 V DC | Rigol DP832 / USB isolator | Clean power rail with $< 5\text{ mV}_{\text{RMS}}$ ripple |

> [!CAUTION]
> **Probe Ground Lead Warning:**  
> Standard 6-inch alligator ground clips add approximately $100\text{ to }150\text{ nH}$ of ground lead inductance. At a 4.0 MSPS DAC rate with $250\text{ ns}$ sample periods and $45\text{ V}/\mu\text{s}$ OPAMP slew rates, long ground leads will cause massive ringing ($> 300\text{ mV}_{\text{p-p}}$) that is purely an artifact of probe grounding, NOT firmware or DAC behavior.  
> **Always use a short coaxial ground spring directly to the adjacent header ground.**

---

## 2. Pinout & Header Verification on NUCLEO-G474RE

Confirm the physical pin connections on the NUCLEO-G474RE Morpho (`CN7` / `CN10`) and Arduino (`CN5` / `CN6` / `CN8` / `CN9`) connectors:

```text
       NUCLEO-G474RE Morpho Connector CN10 (Right Side)
       =================================================
       Pin 1:  PC9                  Pin 2:  PC8
       Pin 3:  PB8                  Pin 4:  PC6
       ...                          ...
       Pin 17: VREF+ (Measure rail) Pin 18: BOOT0
       Pin 19: GND                  Pin 20: GND (Probe Ground Spring)
       Pin 21: PA12                 Pin 22: PA11
       Pin 23: PA8 (MCO clock out)  Pin 24: PB1  <=== [TRANSMIT OUTPUT: OPAMP3_OUT]
       Pin 25: PB12                 Pin 26: PB11
       ...                          ...
```

- **OPAMP3 Transmit Output:** **PB1** (Morpho `CN10 Pin 24`).
- **Oscilloscope Ground Reference:** **GND** (Morpho `CN10 Pin 20` or `CN10 Pin 19`).
- **User Activity LED2:** **PA5** (Onboard green LED — flashes at 50 Hz ping rate).
- **User Profile Cycle Button:** **PC13** (Onboard blue pushbutton).
- **Pin Conflict Verification:** Confirmed that PB1 does not connect to ST-LINK Virtual COM Port (`PA2`/`PA3`), onboard LED, or pushbuttons.

---

## 3. Ordered Bring-Up Sequence

Follow these steps strictly in order. Do not skip to dynamic chirps without verifying DC and clock stability first.

### Step 1: Unpowered Visual & Impedance Inspection
1. Inspect NUCLEO-G474RE board for solder bridges, bent pins, or debris around `CN10 Pin 24` (PB1).
2. Measure resistance between PB1 (`CN10 Pin 24`) and GND (`CN10 Pin 20`) using DMM:
   - **PASS Criteria:** Resistance $> 100\text{ k}\Omega$ (unpowered analog pin).
   - **FAIL Criteria:** Resistance $< 10\text{ }\Omega$ (short to ground or adjacent pin).

### Step 2: Power Rails & 160.0 MHz Clock Tree Validation
1. Connect NUCLEO-G474RE via USB.
2. Measure supply rails using DMM:
   - `+3.3V` Rail (CN7 Pin 16): Target $3.300\text{ V} \pm 50\text{ mV}$ `[PENDING HARDWARE VALIDATION]`.
   - `VREF+` Rail (CN10 Pin 17): Target $3.300\text{ V} \pm 30\text{ mV}$ `[PENDING HARDWARE VALIDATION]`.
   - Power rail ripple on scope ($20\text{ MHz}$ BW limit): $< 10\text{ mV}_{\text{p-p}}$ `[PENDING HARDWARE VALIDATION]`.
3. Clock tree verification:
   - In firmware `clock_config.c`, configure MCO on pin PA8 (`CN10 Pin 23`) with prescaler `/16`.
   - Connect scope probe to PA8.
   - **PASS Criteria:** Exact $10.0000\text{ MHz} \pm 0.01\%$ square wave, confirming $\text{SYSCLK} = 16 \times 10.000\text{ MHz} = \mathbf{160.000\text{ MHz}}$ `[PENDING HARDWARE VALIDATION]`.
   - **FAIL Criteria:** $10.625\text{ MHz}$ measured $\implies$ SYSCLK is running at $170.0\text{ MHz}$, PLL configuration was not applied! Recheck `RCC_PLLCFGR`.

### Step 3: DC Midscale Bias Calibration (Static Zero-Motion Test)
1. In `firmware/Src/main.c`, temporarily bypass continuous chirp playback and call:
   ```c
   DAC3_SetStaticCode(2048U); // Midscale code 0x0800
   ```
2. Connect DMM DC voltmeter to PB1 (`CN10 Pin 24`).
3. **PASS Criteria:**
   - $V_{\text{OUT}} = \frac{2048}{4095} \times V_{\text{REF+}} \approx 1.650\text{ V} \pm 15\text{ mV}$ `[PENDING HARDWARE VALIDATION]`.
   - AC noise on scope ($AC\text{ coupling}, 10\text{ mV/div}$): $< 3.0\text{ mV}_{\text{RMS}}$ `[PENDING HARDWARE VALIDATION]`.
4. Test full-scale static limits:
   - Call `DAC3_SetStaticCode(0U)`: Verify $V_{\text{OUT}} \le 20\text{ mV}$ (rail-to-rail lower bound).
   - Call `DAC3_SetStaticCode(4095U)`: Verify $V_{\text{OUT}} \ge V_{\text{REF+}} - 30\text{ mV}$ (rail-to-rail upper bound).
5. **FAIL Criteria:**
   - $V_{\text{OUT}} = 0.00\text{ V}$ constant $\implies$ OPAMP3 is not enabled (`OPAMP3_CSR.OPAMP3EN == 0`), PB1 GPIO mode is not Analog, or DAC3 Channel 2 is disabled.
   - $V_{\text{OUT}} = 1.65\text{ V}$ but severe high-frequency oscillation ($> 50\text{ mV}_{\text{p-p}}$ @ $> 10\text{ MHz}$) $\implies$ OPAMP3 capacitive load instability (check if long unshielded cable is attached).

### Step 4: Low-Speed Single-Frequency Sanity Waveform (100 kHz Sine)
1. Before enabling 4.0 MSPS chirps, stream a static 100 kHz sinusoidal lookup table (40 samples per cycle @ 4.0 MSPS) via DMA.
2. Trigger oscilloscope on Channel 2 (PA5 LED2).
3. Observe Channel 1 on PB1 (`CN10 Pin 24`):
   - **PASS Criteria:** Clean 100.0 kHz sine wave spanning $0.1\text{ V}$ to $3.2\text{ V}$, zero visible staircasing at $1\text{ }\mu\text{s/div}$, THD $< -40\text{ dB}$ `[PENDING HARDWARE VALIDATION]`.
   - **FAIL Criteria:** Severely attenuated amplitude ($< 1.0\text{ V}_{\text{p-p}}$) $\implies$ OPAMP is not in high-speed mode or DAC internal buffer is inadvertently enabled.

### Step 5: Dynamic 4.0 MSPS LFM Chirp Verification (Profiles 1, 2, 3)
1. Re-enable full adaptive sonar firmware (`DMA_Sonar_Start()`). Default active profile is **Balanced** ($200\text{ to }400\text{ kHz}$).
2. Oscilloscope Channel 1: PB1 (`CN10 Pin 24`), 10:1 probe with ground spring, DC coupled, $500\text{ mV/div}$, center line at $1.65\text{ V}$.
3. Oscilloscope Channel 2: PA5 (LED2 pulse indicator), $1.0\text{ V/div}$, falling edge trigger.
4. **Macro Timing Verification (Timebase $2.0\text{ ms/div}$):**
   - Active Pulse Duration ($T_p$): Measure burst width.  
     **PASS Criteria:** Exactly $2.000\text{ ms} \pm 0.5\text{ }\mu\text{s}$ (8,000 cycles $\times 250\text{ ns}$) `[PENDING HARDWARE VALIDATION]`.
   - Pulse Repetition Interval ($PRI$): Measure time between successive pulse starts.  
     **PASS Criteria:** Exactly $20.000\text{ ms} \pm 2\text{ }\mu\text{s}$ ($50.00\text{ Hz}$ ping rate, $10.0\%$ duty cycle) `[PENDING HARDWARE VALIDATION]`.
   - Envelope Shape: Confirm smooth Hann window tapering to zero amplitude at start and end.
5. **Micro Step Settling Verification (Timebase $100\text{ ns/div}$, zoom into chirp mid-pulse):**
   - Measure individual $250\text{ ns}$ sample steps.
   - Slew Rate: Measure $\Delta V / \Delta t$ during large code steps.  
     **PASS Criteria:** Slew rate $\ge 35\text{ V}/\mu\text{s}$ ($45\text{ V}/\mu\text{s}$ typical in High-Speed mode) `[PENDING HARDWARE VALIDATION]`.
   - Settling Time ($t_{\text{settling}}$): Time required for voltage to settle within $\pm 1\text{ LSB}$ ($0.8\text{ mV}$) of final value.  
     **PASS Criteria:** $t_{\text{settling}} < 80\text{ ns}$ `[PENDING HARDWARE VALIDATION]`. Margin remaining in $250\text{ ns}$ window: $> 170\text{ ns}$.
   - **FAIL Criteria (Buffer Bottleneck):** If output shows slow exponential rise with $t_{\text{settling}} > 1.5\text{ }\mu\text{s}$ and rounded staircase:
     * `DAC3_MCR.MODE2` was incorrectly configured with buffer enabled!
     * `OPAMP3_CSR.OPAPHYSM` was set to normal power mode instead of high speed!
6. **Spectral Verification (FFT Mode on Oscilloscope):**
   - Set FFT window: Blackman-Harris, span: 0 to 5.0 MHz.
   - For Balanced Profile ($200\text{ to }400\text{ kHz}$):
     - In-band energy: Concentrated strictly between $200\text{ kHz}$ and $400\text{ kHz}$.
     - Nyquist frequency: $2.0\text{ MHz}$.
     - First DAC sampling images: Appear at $F_s - f = 4.0\text{ MHz} - 400\text{ kHz} = \mathbf{3.6\text{ MHz}}$ and $4.0\text{ MHz} - 200\text{ kHz} = \mathbf{3.8\text{ MHz}}$ `[PENDING HARDWARE VALIDATION]`.
     - Image Rejection: Image amplitudes should naturally adhere to the $\sin(x)/x$ zero-order hold response ($-14\text{ dB}$ unattenuated before external reconstruction filter).

### Step 6: Atomic Profile Switching & Inter-Pulse Gap Verification
1. While sonar is transmitting, press the blue User Pushbutton (**PC13**).
2. Monitor PB1 and PA5 on scope:
   - **PASS Criteria:** The active chirp pulse must complete its entire $2.000\text{ ms}$ duration uninterrupted. The profile switch from Balanced ($200\text{--}400\text{ kHz}$) to High Frequency ($350\text{--}500\text{ kHz}$) must occur **strictly on the next ping boundary after the 18.0 ms quiet gap** `[PENDING HARDWARE VALIDATION]`.
   - **FAIL Criteria:** Glitch, phase jump, or immediate frequency change mid-pulse $\implies$ DMA buffer was updated asynchronously without waiting for Transfer-Complete ISR!
3. Measure PB1 during the $18.0\text{ ms}$ inter-pulse quiet period:
   - **PASS Criteria:** Signal holds completely flat at DC midscale ($1.650\text{ V} \pm 5\text{ mV}$) with zero residual carrier oscillation or TRGO trigger bleed-through `[PENDING HARDWARE VALIDATION]`.

---

## 4. Comprehensive Troubleshooting Matrix

| Observed Phenomenon | Probable Root Cause | Verification & Corrective Action |
|---|---|---|
| **No output on PB1 (0.0 V flat line)** | OPAMP3 not powered or output not routed | Check `RCC->AHB2ENR` for `DAC3EN`, `RCC->APB1ENR1` for `PWREN`, `RCC->APB2ENR` for `SYSCFGEN`. Check `OPAMP3->CSR` bit 0 (`OPAMP3EN=1`). Check `GPIOB->MODER` bits 3:2 (`0b11` Analog). |
| **Output stuck at 1.65 V DC, no pulses** | DMA underrun lockout (`DMAUDR2`) or init order | In `main.c`, confirm DMA is initialized BEFORE DAC. Check `DAC3->SR` bit 29 (`DMAUDR2`): if set, DAC hardware permanently disabled DMA requests (RM0440 §22.4.15). Clear by writing 1: `DAC3->SR = (1UL << 29);`. Check `DMAMUX1_Channel0->CCR` (must equal 103 / 0x67 for `DAC3_CH2`). Check `DMA1_Channel1->CCR` bit 0 (`EN=1`). Check `TIM2->CR1` bit 0 (`CEN=1`). |
| **Waveform heavily rounded/distorted ($t_{\text{rise}} > 1\text{ }\mu\text{s}$)** | Internal buffer active or OPAMP in low-power mode | In `DAC3_MCR`, ensure `MODE2 = 0b011` (buffer DISABLED). In `OPAMP3_CSR`, ensure bit 7 `HIGHSPEEDEN = 1` (High-Speed mode, slew rate 45 V/us). |
| **Chirp pulse duration is 1.88 ms instead of 2.00 ms** | Clock tree running at 170 MHz instead of 160 MHz | $8000 / (170\text{ MHz} / 40) = 1.882\text{ ms}$. Recheck `clock_config.c`: Ensure PLLN=40, PLLR=2, and SYSCLK switch completed. |
| **Random glitches or DAC codes corrupted** | `DAC_MCR.HFSEL` timing violation | At AHB $\ge 160\text{ MHz}$, `DAC_MCR` bits 15:14 must be set to `0b01` or `0b10`. Ensure `DAC_MCR_HFSEL_ABOVE_80MHZ` is written during init. |
| **Severe ringing / overshoot (> 500 mV) on steps** | Oscilloscope probe ground lead inductance | Remove 6-inch alligator ground clip. Use short coaxial ground spring directly to Morpho `CN10 Pin 20`. |
| **Profile switches mid-chirp with audible/visible click** | Non-atomic profile change in firmware | Ensure profile switching ONLY updates `s_queued_profile`. Latching must occur inside `DMA1_Channel1_IRQHandler` after TIM2 is halted. |
