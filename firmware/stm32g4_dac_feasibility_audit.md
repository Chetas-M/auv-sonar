# STM32G4 DAC Hardware Feasibility Audit — Phase 1 & Phase 2

**Project:** Autonomous Underwater Vehicle (AUV) Adaptive Sonar Transmitter Payload  
**Task:** Architecture and Datasheet Feasibility Audit for 4.0 MSPS Timer-Triggered DMA DAC Generation  
**Target Hardware:** STMicroelectronics STM32G474 Microcontroller (ARM Cortex-M4F @ up to 170 MHz)  
**Date:** September 2026  
**Document Status:** OFFICIAL TECHNICAL AUDIT REPORT  

---

## Executive Summary

This feasibility audit evaluates whether the currently selected STM32G4 microcontroller architecture can reliably generate sonar waveform samples at a target sample rate of **4.0 MSPS** using hardware timer triggering and DMA.

### Primary Question Verdict: CONDITIONAL PASS

> **Can the exact STM32G4 MCU selected for this project reliably support a 4 MHz DAC update/sample rate using hardware timer triggering and DMA?**

**Verdict: CONDITIONAL PASS.**  
- **Digital Bus & DMA Capability (PASS):** The STM32G4 bus matrix, DMA controller, and DAC interface easily support 4.0 MSPS (8.0 MB/s raw half-word throughput). Authoritative ST application note benchmarks (AN4566 Table 2) confirm the STM32G4 DAC DMA interface operates at up to **28.8 MSPS** (and **30.9 MSPS** in DMA double data mode).
- **Analog Settling with Internal Buffer Enabled (FAIL):** The STM32G4 internal DAC output buffer (`DAC_OUTPUTBUFFER_ENABLE`) is rated in datasheet DS12288 for a maximum of **1.0 MSPS**, with a typical settling time of $t_{\text{SETTLING}} = 1.6\text{ }\mu\text{s}$ (up to $2.9\text{ to }3.0\text{ }\mu\text{s}$ max into 50 pF). At 4.0 MSPS, the sample interval is $T_s = 250\text{ ns}$. The internal buffer is 6.4× too slow to settle between arbitrary codes and will severely attenuate and distort a 4.0 MSPS waveform.
- **Analog Settling in High-Speed Unbuffered / Redirected Modes (PASS):** 
  1. **Internal Fast DAC Path (DAC3/DAC4 -> Internal OPAMP -> Pin):** STM32G474 embeds four high-speed internal DAC channels (DAC3 and DAC4) rated for **15 MSPS** (ST AN5306). When routed internally to an on-chip high-speed operational amplifier (`OPAMP3` to pin `PB1` or `OPAMP5` to pin `PA8`) configured in follower mode with $45\text{ V}/\mu\text{s}$ slew rate and $13\text{ MHz}$ bandwidth, 4.0 MSPS playback is fully viable on-chip.
  2. **External Buffer Path (DAC1 -> Buffer Disabled -> External OpAmp):** If external DAC1 (pin `PA4`) is used, the internal buffer must be disabled (`DAC_OUTPUTBUFFER_DISABLE`) and routed immediately to an external high-speed op-amp (e.g., OPA354, LMH6645) as specified in ST AN4566.
- **Timer Frequency (CONDITIONAL / RECONFIGURED):** At the default nominal $170.0\text{ MHz}$ system clock, $170 / 4 = 42.5$ (non-integer). Timer division produces either $4.0476\text{ MHz}$ (+1.19% error) or $3.9535\text{ MHz}$ (-1.16% error). Setting SYSCLK to **160.0 MHz** (or 168.0 MHz) via the PLL achieves **exactly 4,000,000.00 Hz (0.00% error)** with $\text{PSC}=0, \text{ARR}=39$.

Firmware bring-up may proceed provided the DAC routing and clock tree adhere to the prerequisites established in this report.

---

# PHASE 1 — PROJECT ARCHITECTURE AUDIT

An exhaustive inspection of the existing codebase (`src/config.py`, `src/waveform.py`, `src/profiles.py`, `src/export_c.py`, `matlab/config_sonar.m`, `outputs/headers/*.h`, and report documentation) was conducted to extract the actual project assumptions.

### 1. Microcontroller
- **Selected MCU Model:** STMicroelectronics **STM32G474** family.
- **Specific Part Numbers Identified:** `STM32G474RET6` (64-pin LQFP) and `STM32G474CE` (48-pin UFQFPN) referenced in `src/config.py` line 30, `report_sections_part1.py` line 83, and `walkthrough.md` line 211.
- **Core Architecture:** ARM Cortex-M4F with FPU and DSP instructions, operating up to $170\text{ MHz}$ ($213\text{ DMIPS}$).
- **Target Development Board:** **NUCLEO-G474RE** (referenced in `report_sections_part4.py` line 125 and `walkthrough.md` line 187).

### 2. DAC Architecture
- **Planned Peripheral:** STM32 internal 12-bit Digital-to-Analog Converter. Code documentation in `report_sections_part4.py` line 144 specifies `DAC1` (pin `PA4` for DAC1_OUT1).
- **DAC Resolution:** 12-bit unsigned integer ($0$ to $4095$).
- **Midscale Bias:** Code $2048$ ($1.65\text{ V}$ nominal at $V_{\text{REF+}} = 3.3\text{ V}$) for AC-coupled transducer drive.
- **Channel Configuration:** Single DAC channel currently assumed for transmission (`DAC1_OUT1`), though dual-channel capability exists on the silicon.
- **Output Waveform Type:** Linear Frequency Modulated (LFM) Chirp with symmetric Hann window envelope tapering.
- **Output Acoustic Frequency Range:** $100\text{ kHz}$ to $500\text{ kHz}$ partitioned across three discrete operating profiles:
  - Profile 1 (Low Frequency): $100.0\text{ kHz}$ to $220.0\text{ kHz}$ ($f_c = 160\text{ kHz}, B = 120\text{ kHz}$).
  - Profile 2 (Balanced Default): $200.0\text{ kHz}$ to $400.0\text{ kHz}$ ($f_c = 300\text{ kHz}, B = 200\text{ kHz}$).
  - Profile 3 (High Frequency): $350.0\text{ kHz}$ to $500.0\text{ kHz}$ ($f_c = 425\text{ kHz}, B = 150\text{ kHz}$).
- **Target DAC Sample / Update Rate:** **4.0 MSPS** ($4,000,000\text{ samples/s}$).
- **Distinction of Rates:**
  - *Waveform Sample Rate:* $4.0\text{ MHz}$ ($T_s = 250\text{ ns}$). Discrete points in memory table.
  - *DAC Update Rate:* $4.0\text{ MHz}$. Rate at which the DAC holding/output registers latch new digital words.
  - *Timer Trigger Frequency:* $4.0\text{ MHz}$. Periodic TRGO pulses driving DMA requests and DAC latching.
  - *Actual Analog Waveform Frequency:* $100\text{ kHz}$ to $500\text{ kHz}$ (instantaneous fundamental carrier frequency).

### 3. Timer Architecture
- **Planned Hardware Timer:** General-purpose 32-bit **TIM2** (referenced in `report_sections_part4.py` line 144: *"Configure Timer 2 TRGO at 4.0 MHz driving DMA1 Channel 1 into DAC1"*). Basic timers **TIM6** / **TIM7** are also available alternative TRGO sources.
- **MCU System Clock Assumption:** $170.0\text{ MHz}$ maximum Cortex-M4 clock (`MCU_MAX_SYSCLK_HZ` in `src/config.py`).
- **Peripheral Bus Clock Assumption:** AHB = $170\text{ MHz}$, APB1 / APB2 = $170\text{ MHz}$ (prescaler = 1).
- **Triggering Method:** Hardware Timer Update Event (`TIM_TRGO_UPDATE`) mapped via internal peripheral bus directly to the DAC trigger input (`DAC_TRIGGER_T2_TRGO`).

### 4. DMA Architecture
- **DMA Controller:** DMA1 Channel 1 (`DMA1_Channel1`) coupled with DMAMUX1.
- **Transfer Direction:** Memory-to-Peripheral.
- **Memory Source:** Flash LUT (or SRAM staging buffer) containing `const uint16_t` lookup table.
- **Peripheral Destination:** DAC 12-bit Right-Aligned Data Holding Register (`DAC_DHR12R1` at offset `0x08`).
- **Transfer Width:** Half-Word (16-bit) source and Half-Word (16-bit) destination.
- **Operating Mode:** Circular mode or Normal mode with atomic ping-boundary buffer switching inside the DMA Transfer-Complete (TC) interrupt.
- **Waveform Buffer Size:** 8,000 samples = 16,000 bytes ($15.625\text{ KiB} \approx 16.0\text{ KB}$) per active chirp pulse.
- **Waveform Duration:** $T_p = 2.0\text{ ms}$ active transmit pulse every $PRI = 20.0\text{ ms}$ (10.0% duty cycle).

### 5. Waveform Requirements
- **Target Waveform Sample Rate:** $4.0\text{ MHz}$ ($4.0\times 10^6\text{ samples/s}$).
- **Nominal Chirp Duration ($T_p$):** $2.0\text{ ms}$ ($0.002\text{ s}$).
- **Pulse Repetition Interval (PRI):** $20.0\text{ ms}$ ($50\text{ Hz}$ ping repetition rate).
- **Frequency Coverage:** $100\text{ kHz}$ to $500\text{ kHz}$.
- **Samples per Chirp ($N_p$):** $N_p = F_s \times T_p = 4,000,000 \times 0.002 = 8,000\text{ samples}$.
- **Number of Predefined Profiles:** Exactly 3 canonical profiles (Low, Balanced, High).
- **Windowing / Envelope:** Full symmetric Hann window ($w[n] = 0.5 - 0.5\cos(2\pi n / (N-1))$).
- **Generation Method:** **Precomputed Lookup Tables (LUTs)** stored in non-volatile Flash memory and exported as firmware-ready C headers (`chirp_low_frequency.h`, `chirp_balanced.h`, `chirp_high_frequency.h`, `sonar_profiles.h`). Dynamic runtime synthesis on-the-fly is NOT used for v1.

### 6. Memory Requirements
- **Single Waveform Footprint:**  
  $$8,000\text{ samples} \times 2\text{ bytes/sample} = 16,000\text{ bytes} = 15.625\text{ KiB}$$
- **All Three Waveforms (Flash Storage):**  
  $$3 \times 16,000\text{ bytes} = 48,000\text{ bytes} = 46.875\text{ KiB}$$
- **MCU Flash Capacity:** $512\text{ KB}$ ($524,288\text{ bytes}$).  
  LUTs occupy $\frac{48,000}{524,288} = 9.155\%$ of total Flash ($90.8\%$ headroom).
- **MCU SRAM Capacity:** $128\text{ KB}$ ($131,072\text{ bytes}$).  
  If streamed directly from Flash to DAC: $0\text{ KB}$ SRAM.  
  If staged in SRAM active buffer: $16.0\text{ KB}$ ($12.5\%$ SRAM load, leaving $112\text{ KB}$ free).  
  If double-buffered in SRAM: $32.0\text{ KB}$ ($25.0\%$ SRAM load, leaving $96\text{ KB}$ free).

---

## Phase 1 Required Deliverable

### Architecture Component Summary Table

| Architecture Component | Current Project Assumption | Evidence Source | Confirmed / Unconfirmed |
|---|---|---|---|
| **MCU Model** | STM32G474 (STM32G474RET6 / STM32G474CE) | `src/config.py:30`, `report_sections_part1.py:83` | **CONFIRMED** |
| **Development Board** | NUCLEO-G474RE | `report_sections_part4.py:125`, `walkthrough.md:187` | **CONFIRMED** |
| **System Clock** | 170.0 MHz Cortex-M4F | `src/config.py:32`, `matlab/config_sonar.m:28` | **CONFIRMED** |
| **DAC Peripheral** | DAC1 Channel 1 (PA4) or internal DAC | `report_sections_part4.py:144,245`, `export_c.py:45` | **CONFIRMED** |
| **DAC Resolution** | 12-bit unsigned ($0$ to $4095$) | `src/config.py:12`, `matlab/config_sonar.m:23` | **CONFIRMED** |
| **Target Sample Rate** | 4.0 MSPS ($T_s = 250\text{ ns}$) | `src/config.py:11`, `matlab/config_sonar.m:21` | **CONFIRMED** |
| **Timer Trigger** | TIM2 TRGO update event | `report_sections_part4.py:144`, `main.py:60` | **CONFIRMED** |
| **DMA Usage** | DMA1 Channel 1, Half-Word (16-bit) Mem-to-Peri | `report_sections_part1.py:817`, `export_c.py:75` | **CONFIRMED** |
| **Waveform Buffer** | Precomputed uint16_t array (aligned 4) | `outputs/headers/*.h`, `src/export_c.py:95` | **CONFIRMED** |
| **Chirp Duration** | $T_p = 2.0\text{ ms}$ ($PRI = 20.0\text{ ms}$) | `src/config.py:26-27`, `matlab/config_sonar.m:35-36` | **CONFIRMED** |
| **Chirp Frequency Range** | $100\text{ kHz}$ to $500\text{ kHz}$ (3 bands) | `src/profiles.py:80-112`, `src/config.py:19-20` | **CONFIRMED** |
| **Samples per Chirp** | 8,000 samples | `src/export_c.py:57`, `matlab/config_sonar.m:42` | **CONFIRMED** |
| **Memory Requirement** | 16.0 KB SRAM / 48.0 KB Flash | `report_sections_part1.py:804-806`, `main.py:200` | **CONFIRMED** |

### Concise Architecture Summary

```text
MCU: STM32G474RET6 (ARM Cortex-M4F @ 170 MHz, 512 KB Flash, 128 KB SRAM)
Development Board: NUCLEO-G474RE
System Clock: 170.0 MHz (Nominal) -> 160.0 MHz (Recommended for 4.0 MHz integer division)
DAC: STM32G4 12-bit DAC (DAC1 for external pin, or DAC3/DAC4 for internal high-speed routing)
DAC Channel: DAC1_OUT1 (PA4) or DAC3_OUT2 (internal to OPAMP3 -> PB1)
Target DAC Update Rate: 4,000,000 samples/s (4.0 MSPS, Ts = 250 ns)
Timer Trigger: TIM2 TRGO (or TIM6/TIM7 TRGO) @ 4.0 MHz
DMA Path: Memory-to-Peripheral (DMA1 Channel 1, DMAMUX1, Half-Word uint16_t transfers)
Waveform Buffer: Precomputed 16-bit integer lookup table in Flash (DMA_ALIGN 4-byte boundary)
Waveform Sample Format: uint16_t, 12-bit right-aligned (0x0000 to 0x0FFF)
Chirp Duration: 2.000 ms (8,000 samples @ 4.0 MSPS)
Chirp Frequency Range: 100.0 kHz to 500.0 kHz across 3 adaptive profiles
Samples per Chirp: 8,000 samples (16,000 bytes / profile)
```

---

# PHASE 2 — DATASHEET AND HARDWARE FEASIBILITY VERIFICATION

Authoritative sources evaluated:
1. **Datasheet DS12288 Rev 6:** *STM32G474xB STM32G474xC STM32G474xE Arm Cortex-M4 32-bit MCU+FPU*.
2. **Reference Manual RM0440 Rev 8:** *STM32G4 Series advanced Arm-based 32-bit MCUs*.
3. **Application Note AN4566 Rev 3:** *How to extend the DAC performance on STM32 MCUs*.
4. **Application Note AN5306 Rev 1:** *Operational amplifier applications on STM32G4 Series*.
5. **STM32CubeG4 Firmware Package v1.6.0:** *Examples for DAC_DMADoubleDataMode and DAC_SignalsGeneration2*.

---

### 1. DAC Capability Verification

#### A. Maximum DAC Update Rate and Conversion Rate
- **DATASHEET FACT (DS12288 §5.3.20 Table 74 "DAC characteristics"):**  
  The maximum update rate for the internal DAC with the **output buffer enabled** is officially rated at:
  $$F_{\text{update, max (buffered)}} = 1.0\text{ MSPS}$$
- **DATASHEET FACT (DS12288 §5.3.21 "DAC 15MSPS characteristics"):**  
  The STM32G474 embeds specialized internal DAC channels (on DAC3 and DAC4) that support up to:
  $$F_{\text{update, max (unbuffered/internal)}} = 15.0\text{ MSPS}$$
- **REFERENCE MANUAL FACT (RM0440 §22.4.15 & §22.7.16 `DAC_MCR`):**  
  The High-Frequency Interface Mode register (`DAC_MCR.HFSEL[1:0]`) must be configured when the AHB clock exceeds $80\text{ MHz}$ or $160\text{ MHz}$ to enable the high-speed interface logic. At $170\text{ MHz}$, `HFSEL = 10` (`LL_DAC_HIGH_FREQ_MODE_ABOVE_160MHZ`).
- **APPLICATION NOTE FACT (AN4566 Table 2):**  
  ST benchmark measurements confirm that the digital peripheral interface and DMA bus can push up to **28.8 MSPS** into the STM32G4 DAC in single-data mode and **30.9 MSPS** in DMA double data mode.

> **Explicit Answer:** Can the DAC peripheral theoretically accept and convert samples at 4,000,000 updates per second?  
> **YES.** The internal conversion engine, digital registers, and DMA request interface support up to 15–28.8 MSPS. However, **whether the analog output can physically settle within 250 ns depends entirely on the output buffer mode.**

---

#### B. DAC Settling Time Verification
At 4.0 MSPS, the sample period is:
$$T_s = \frac{1}{4,000,000\text{ Hz}} = 250\text{ ns}$$

- **DATASHEET FACT (DS12288 Table 74):**  
  For external DACs (DAC1 / DAC2) with the **internal output buffer enabled** (`DAC_OUTPUTBUFFER_ENABLE`):
  $$t_{\text{SETTLING (typical)}} = 1.6\text{ }\mu\text{s} = 1600\text{ ns}$$
  $$t_{\text{SETTLING (maximum)}} = 2.9\text{ to }3.0\text{ }\mu\text{s} = 2900\text{ to }3000\text{ ns}$$
  (Specified for a full-scale 12-bit code transition from lowest to highest code with load $R_L \ge 5\text{ k}\Omega, C_L \le 50\text{ pF}$).
  - *Comparison:* $t_{\text{SETTLING}} = 1600\text{ ns} \gg 250\text{ ns}$ ($6.4\times$ the entire sample period).
  - *Conclusion for Buffered DAC1:* **FAIL.** If the firmware enables the internal buffer, the DAC cannot settle. Output will be severely slew-rate limited and attenuated.

- **DATASHEET & APPLICATION NOTE FACT (DS12288 & AN4566 §1.2):**  
  When the internal buffer is **disabled** (`DAC_OUTPUTBUFFER_DISABLE`), the output impedance is purely resistive ($R_{\text{DAC}} \approx 15\text{ k}\Omega$).
  The settling time is dictated by the external RC time constant $\tau = R_{\text{DAC}} \times C_L$.
  - With a typical PCB pad and trace capacitance of $C_L = 10\text{ pF}$, $\tau = 15\text{ k}\Omega \times 10\text{ pF} = 150\text{ ns}$.
  - Settling to within $\pm 1\text{ LSB}$ of a 12-bit value requires $\ln(4096) \times \tau \approx 8.31 \times 150\text{ ns} \approx 1.25\text{ }\mu\text{s}$.
  - *Conclusion for Unbuffered Passive Pin:* Direct connection to an external load at 4.0 MSPS cannot settle passively without external active buffering.

- **APPLICATION NOTE & FIRMWARE FACT (AN5306 §3.4.4 & STM32CubeG4 `DAC_DMADoubleDataMode`):**  
  STM32G474 features **four 15 MSPS internal DAC channels** on DAC3 and DAC4.
  These channels are connected internally to the on-chip high-speed operational amplifiers (`OPAMP1` through `OPAMP6`).
  - *Internal OPAMP Specifications (AN5306 Table 1 & DS12288):*
    - Bandwidth (Gain Bandwidth Product): **13 MHz**
    - Slew Rate in High-Speed Mode: **45 V/µs**
    - Open-Loop Gain: **95 dB**
  - *Slew Time Calculation:*
    For a full-scale rail-to-rail step of $\Delta V = 3.3\text{ V}$:
    $$t_{\text{slew}} = \frac{3.3\text{ V}}{45\text{ V}/\mu\text{s}} = 0.0733\text{ }\mu\text{s} = 73.3\text{ ns}$$
  - *Comparison:* $73.3\text{ ns} < 250\text{ ns}$ (leaves $>175\text{ ns}$ for linear small-signal settling).
  - *Conclusion for Internal DAC3/DAC4 -> OPAMP:* **PASS.** ST officially demonstrates full-scale 15 MSPS waveform generation through this path on oscilloscope bench captures (AN5306 Figures 16 & 17).

---

#### C. DAC Clock and Trigger Constraints
- **REFERENCE MANUAL FACT (RM0440 §22.4.2):**  
  The DAC conversion is triggered by an external trigger signal selected via the `TSELx[3:0]` bits in the `DAC_CR` register.
- **AUTHORITATIVE TRIGGER TABLE (RM0440 Table 150 & `stm32g4xx_ll_dac.h`):**  
  Supported hardware timer triggers for DAC1 include:
  - `DAC_CR_TSEL1 = 0100` (4): **TIM2_TRGO** (`LL_DAC_TRIG_EXT_TIM2_TRGO`) — *Project Selected*
  - `DAC_CR_TSEL1 = 0011` (3): **TIM15_TRGO**
  - `DAC_CR_TSEL1 = 0111` (7): **TIM6_TRGO**
  - `DAC_CR_TSEL1 = 0010` (2): **TIM7_TRGO**
  - `DAC_CR_TSEL1 = 0101` (5): **TIM4_TRGO**
  - `DAC_CR_TSEL1 = 1000` (8): **TIM3_TRGO**
  - `DAC_CR_TSEL1 = 1111` (15): **HRTIM_TRGO1**
- **Trigger Latency (RM0440 §22.4.4):**  
  Upon receiving a valid timer trigger, the data from `DAC_DHRx` is transferred to `DAC_DORx` after **3 APB1 clock cycles**.
  At $170\text{ MHz}$, 3 APB cycles = $17.6\text{ ns}$, which is fixed, deterministic, and negligible compared to $250\text{ ns}$.

---

#### D. DAC DMA Support
- **REFERENCE MANUAL FACT (RM0440 §22.4.8):**  
  Each DAC channel has dedicated DMA capability. Setting the `DMAENx` bit in `DAC_CR` generates a DMA request whenever a trigger occurs.
- **DMA Request Generation:** The DAC asserts a DMA request concurrently with latching data to `DAC_DORx`. The DMA controller then fetches the *next* sample from memory into `DAC_DHRx`, making it ready for the subsequent trigger.
- **Overrun Protection:** Setting `DMAUDRIEx` enables interrupt on DMA underrun if the bus fails to deliver data before the next trigger.

---

### 2. Timer Capability Verification

#### Frequency Calculation & Integer Divisibility Analysis
The timer trigger frequency is given by:
$$F_{\text{trigger}} = \frac{F_{\text{TIM\_CLK}}}{(\text{PSC} + 1) \times (\text{ARR} + 1)}$$

For STM32G474, TIM2 is connected to the APB1 bus. When the APB1 prescaler is 1, $F_{\text{TIM\_CLK}} = F_{\text{SYSCLK}}$.

#### Case A: Nominal Clock ($F_{\text{SYSCLK}} = 170.0\text{ MHz}$)
$$\frac{170,000,000\text{ Hz}}{4,000,000\text{ Hz}} = 42.5\text{ (non-integer)}$$

Because PSC and ARR must be integers, an exact $4.000000\text{ MHz}$ cannot be generated at $170.0\text{ MHz}$:
- **Option 1 (ARR = 41, PSC = 0, Divisor = 42):**  
  $$F_{\text{trig}} = \frac{170\text{ MHz}}{42} = 4,047,619.05\text{ Hz}\quad (+47.62\text{ kHz},\quad \mathbf{+1.19\%\text{ error}})$$
- **Option 2 (ARR = 42, PSC = 0, Divisor = 43):**  
  $$F_{\text{trig}} = \frac{170\text{ MHz}}{43} = 3,953,488.37\text{ Hz}\quad (-46.51\text{ kHz},\quad \mathbf{-1.16\%\text{ error}})$$

*Impact of 1.18% error:* Chirp duration shifts from $2.000\text{ ms}$ to $1.976\text{ ms}$ (or $2.024\text{ ms}$), altering the sweep slope by $1.18\%$. This is manageable in software, but introduces unnecessary Doppler/range bias in matched filtering.

#### Case B: Recommended Tuned Clock ($F_{\text{SYSCLK}} = 160.0\text{ MHz}$)
By configuring the PLL to output $160.0\text{ MHz}$ (using standard $8\text{ MHz}$ HSE crystal: $\text{PLLM}=1, \text{PLLN}=40, \text{PLLR}=2$):
$$\frac{160,000,000\text{ Hz}}{4,000,000\text{ Hz}} = 40.0\text{ (Exact integer)}$$

- **Exact Configuration:**  
  $$\text{PSC} = 0$$  
  $$\text{ARR} = 39\quad (\text{Period} = \text{ARR} + 1 = 40)$$  
  $$F_{\text{trigger}} = \frac{160,000,000}{1 \times 40} = \mathbf{4,000,000.00\text{ Hz}}\quad (\mathbf{0.00\%\text{ error, EXACT}})$$

*Alternative Tuned Clock:* $168.0\text{ MHz}$ ($\text{PSC}=0, \text{ARR}=41$, Divisor=42) also produces **exactly 4,000,000.00 Hz**.

---

### 3. DMA Throughput Verification
- **Required Bandwidth:**  
  $$\text{Throughput} = 4,000,000\text{ transfers/s} \times 2\text{ bytes/transfer} = \mathbf{8.0\text{ MB/s}}$$
- **Bus Architecture:** STM32G4 features a 32-bit Multi-AHB matrix running at $160\text{ to }170\text{ MHz}$.
  - Peak theoretical AHB bus bandwidth:  
    $$170\text{ MHz} \times 4\text{ bytes} = 680\text{ MB/s}$$
  - The sonar DMA transfer of $8.0\text{ MB/s}$ represents:  
    $$\frac{8.0\text{ MB/s}}{680\text{ MB/s}} = \mathbf{1.18\%}\text{ of AHB bus matrix capacity}$$
- **Benchmarked Capability (AN4566 Table 2):**  
  ST explicitly validated continuous DAC DMA transfers on STM32G4 up to **28.8 MSPS (57.6 MB/s)**.  
  The project requirement ($8.0\text{ MB/s}$) operates at **less than 14% of the proven hardware limit**. Bus congestion is virtually impossible.

---

### 4. CPU Independence Verification
- **Hardware Trigger Pipeline:**  
  $$\text{Timer Counter (ARR overflow)} \longrightarrow \text{TIM2 TRGO Pulse} \longrightarrow \text{DAC Trigger Input} \longrightarrow \text{DAC DMA Request} \longrightarrow \text{DMA Controller AHB Fetch} \longrightarrow \text{DAC\_DHR12R1}$$
- **CPU Load During Ping Emission ($2.0\text{ ms}$):** **0.0%**. The entire 8,000-sample chirp is transferred autonomously by hardware.
- **CPU Interactivity:** The CPU is only interrupted on Transfer Complete (TC) at the end of the 2.0 ms chirp to update the DMA buffer pointer or switch profiles. At $PRI = 20\text{ ms}$, this occurs at $50\text{ Hz}$. Handling a 50 Hz interrupt requires $< 500\text{ clock cycles/sec}$, representing $< 0.0003\%$ of the $170\text{ MHz}$ Cortex-M4 capacity.

---

### 5. Analog Output Feasibility
- **Sampling Rate:** $F_s = 4.0\text{ MSPS}$.  
- **Nyquist Limit:** $F_{\text{Nyquist}} = 2.0\text{ MHz}$.  
- **Maximum Chirp Frequency ($f_{\text{max}}$):** $500\text{ kHz}$ (High-Frequency profile: 350 to 500 kHz).
- **Oversampling Ratio at Maximum Frequency:**  
  $$\text{OSR} = \frac{4.0\text{ MHz}}{500\text{ kHz}} = \mathbf{8.0\times}$$  
  (For 100 kHz, $\text{OSR} = 40\times$; for 300 kHz, $\text{OSR} = 13.3\times$).
- **First DAC Image Frequencies:**  
  $$f_{\text{image, 1}} = F_s - f_{\text{signal}} = 4.0\text{ MHz} - 500\text{ kHz} = \mathbf{3.5\text{ MHz}}$$
- **Transition Band Width:**  
  $$f_{\text{image, 1}} - f_{\text{max}} = 3.5\text{ MHz} - 0.5\text{ MHz} = \mathbf{3.0\text{ MHz}}\quad (7:1\text{ frequency span})$$
- **Reconstruction Filter Feasibility:** Because the transition band is an enormous 3.0 MHz wide, an active 3rd or 4th-order Sallen-Key low-pass filter with a cutoff frequency around $750\text{ kHz}$ will provide $> 40\text{ dB}$ of image rejection at 3.5 MHz with minimal passband phase distortion.

---

### 6. Memory Feasibility
- **Flash Utilization:** All 3 precomputed chirp profiles require $48.0\text{ KB}$ out of $512\text{ KB}$ Flash (**9.37% utilized**, leaving **464 KB / 90.6% free** for application code and RTOS).
- **SRAM Utilization:**
  - Zero RAM used if streamed directly from Flash LUT.
  - $16.0\text{ KB}$ used if staged in SRAM (**12.5% utilized**, leaving **112 KB / 87.5% free**).
  - $32.0\text{ KB}$ used if ping-pong double-buffered in SRAM (**25.0% utilized**, leaving **96 KB / 75.0% free**).
- **Memory Bus Bandwidth:** Reading 8.0 MB/s from Flash or SRAM introduces zero bus wait states on the AHB matrix. Memory capacity and bandwidth are completely unconstrained.

---

## Phase 2 Required Feasibility Table

| Requirement | Project Requirement | Hardware Capability | Authoritative Evidence | Status | Risk Level |
|---|---:|---|---|---|---|
| **DAC Update Rate (Digital)** | 4.0 MSPS | 15.0 MSPS (internal) / 28.8 MSPS (DMA interface) | DS12288 Table 74; AN4566 Table 2; AN5306 | **PASS** | LOW |
| **DAC Settling (Buffered DAC1)** | 250 ns sample period | 1600 ns typ / 3000 ns max (1 MSPS max) | DS12288 §5.3.20 Table 74 | **FAIL** | **CRITICAL** |
| **DAC Settling (Internal OPAMP)** | 250 ns sample period | 73.3 ns full-scale slew ($45\text{ V}/\mu\text{s}$, 13 MHz GBW) | AN5306 §3.4.4; DS12288 §5.3.23 | **PASS** | MEDIUM |
| **DAC Settling (Ext. OpAmp)** | 250 ns sample period | < 80 ns slew with external wideband buffer | AN4566 §2.1 (e.g. LMH6645, OPA354) | **PASS** | LOW |
| **Timer Trigger Rate** | 4.0 MHz | 170.0 MHz counter clock; TRGO supported | RM0440 §22.4.2; `stm32g4xx_ll_dac.h` | **PASS** | LOW |
| **Timer Accuracy** | Exact 4.000000 MHz | 4.048 MHz (+1.19%) @ 170 MHz; Exact 4.000 MHz @ 160 MHz | Timer clock division math ($160\text{ MHz} / 40 = 4\text{ MHz}$) | **CONDITIONAL** | MEDIUM |
| **DMA Throughput** | 8.0 MB/s | Up to 57.6 MB/s benchmarked on STM32G4 | AN4566 Table 2; RM0440 §11 | **PASS** | LOW |
| **DAC DMA Support** | Required | Dedicated DMA request per DAC trigger | RM0440 §22.4.8; STM32CubeG4 examples | **PASS** | LOW |
| **Continuous Waveform Output** | Autonomous 2.0 ms | Fully autonomous hardware Timer->DMA->DAC | STM32CubeG4 `DAC_DMADoubleDataMode` | **PASS** | LOW |
| **Memory Capacity** | 48 KB Flash, 16 KB RAM | 512 KB Flash (9.37% used), 128 KB RAM (12.5% used) | DS12288 §3; `src/config.py` | **PASS** | LOW |
| **CPU Independence** | Zero per-sample CPU | 0.0% CPU during pulse; 50 Hz TC interrupt | RM0440 DMA / DAC hardware synchronization | **PASS** | LOW |
| **Analog Bandwidth Plausibility** | 100 to 500 kHz chirps | Nyquist = 2.0 MHz; OSR = 8×; Images @ 3.5 MHz | Discrete sampling theory; 3 MHz transition band | **PASS** | LOW |

---

# FINAL DELIVERABLE — ARCHITECTURE GATE REPORT

## A. Confirmed Architecture
The audit confirms that the project's digital twin architecture relies on:
- Microcontroller: **STM32G474RET6** (170 MHz ARM Cortex-M4F, 128 KB SRAM, 512 KB Flash) on a **NUCLEO-G474RE** board.
- Waveform Playback: Precomputed 12-bit unsigned lookup tables (8,000 samples / 16 KB per profile, 48 KB total Flash) transferred via DMA1 Channel 1.
- Triggering: Hardware Timer (TIM2) generating TRGO update events at 4.0 MHz.
- Acoustic Emission: LFM chirps ($100\text{ kHz}$ to $500\text{ kHz}$) with Hann window envelopes for $2.0\text{ ms}$ pulse duration at $20.0\text{ ms}$ PRI (10% duty cycle).

---

## B. Confirmed Hardware Limits
1. **DAC Maximum Buffered Rate (Datasheet DS12288):** 1.0 MSPS ($t_{\text{SETTLING}} = 1.6\text{ }\mu\text{s}$ typical, $3.0\text{ }\mu\text{s}$ max into 50 pF).
2. **DAC Maximum Internal Rate (Datasheet DS12288 & AN5306):** 15.0 MSPS for internal DAC3/DAC4 channels.
3. **DAC DMA Benchmark (Application Note AN4566):** 28.8 MSPS (57.6 MB/s) single data mode; 30.9 MSPS (61.8 MB/s) double data mode.
4. **Internal OPAMP Bandwidth & Slew Rate (AN5306 & DS12288):** 13 MHz Gain-Bandwidth Product, 45 V/µs slew rate in high-speed mode.
5. **Timer TRGO Hardware Synchronization (Reference Manual RM0440):** Deterministic 3 APB1 cycle latency ($17.6\text{ ns}$ @ 170 MHz) from TRGO to DAC_DOR transfer.

---

## C. Critical Risks Ranking

### 1. [CRITICAL] Internal DAC Output Buffer Slew Rate Limitation on DAC1
- **Severity:** CRITICAL
- **Description:** If firmware initializes DAC1 with `sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE`, the hardware will physically low-pass filter the 4.0 MSPS signal to ~1 MSPS, distorting the chirp and destroying fidelity.
- **Mandatory Mitigation:** **DO NOT use DAC1 with the internal buffer enabled.** The firmware must implement one of two approved paths:
  - *Path A (Recommended - Fully Integrated):* Use internal **DAC3 Channel 2** or **DAC4 Channel 2** routed internally to **OPAMP3 (pin PB1)** or **OPAMP5 (pin PA8)** in High-Speed Follower Mode, as proven in STM32CubeG4 `DAC_DMADoubleDataMode` and AN5306.
  - *Path B (External Buffer):* Configure DAC1 with `DAC_OUTPUTBUFFER_DISABLE` and route pin PA4 directly into an external high-speed op-amp (e.g. OPA354 / LMH6645, GBW > 50 MHz, slew rate > 40 V/µs) on the transmitter PCB.

### 2. [HIGH] Clock Prescaler / Frequency Mismatch at 170 MHz
- **Severity:** HIGH
- **Description:** Running SYSCLK at the maximum 170.0 MHz makes an exact 4.000000 MHz timer trigger impossible ($170 / 42 = 4.0476\text{ MHz}$, a +1.19% error).
- **Mandatory Mitigation:** Configure the PLL clock tree for **SYSCLK = 160.0 MHz** (or 168.0 MHz). At 160.0 MHz, TIM2 with $\text{PSC}=0, \text{ARR}=39$ generates **exactly 4.000000 MHz (0.000% error)**.

### 3. [MEDIUM] High-Frequency Interface Mode Configuration (`DAC_MCR.HFSEL`)
- **Severity:** MEDIUM
- **Description:** If the `HFSEL` bits in `DAC_MCR` are not explicitly configured for AHB > 80 MHz or > 160 MHz, the internal DAC logic timing violation can corrupt conversion data.
- **Mandatory Mitigation:** Ensure `DAC_HighFrequency = DAC_HIGH_FREQUENCY_INTERFACE_MODE_AUTOMATIC` (or `LL_DAC_HIGH_FREQ_MODE_ABOVE_80MHZ` / `LL_DAC_HIGH_FREQ_MODE_ABOVE_160MHZ`) is programmed during DAC initialization.

### 4. [LOW] Bus Contention / DMA Starvation
- **Severity:** LOW
- **Description:** Required DMA bandwidth is 8.0 MB/s, which is only 1.18% of the AHB bus matrix capacity. Negligible risk.

---

## D. Architecture Verdict

### **CONDITIONAL PASS**

```text
The architecture appears theoretically feasible, but one or more critical 
specifications remain unverified or require physical hardware testing.
```

### Justification and Prerequisites for Phase 3 Firmware Development:
The project's planned **4 MHz Timer → DMA → Internal DAC** pipeline is **theoretically feasible** and backed by official ST benchmarks (AN4566 / AN5306), **PROVIDED THAT THE FOLLOWING THREE MANDATORY ARCHITECTURAL CONDITIONS ARE OBSERVED**:

1. **DAC Output Channel Selection (Crucial):**  
   The firmware must NOT use DAC1 with the internal buffer enabled. The design must explicitly adopt either:
   - **Internal High-Speed Architecture:** Use internal 15 MSPS **DAC3_OUT2** redirected through **OPAMP3** in high-speed follower mode out to pin **PB1** (or DAC4_OUT2 -> OPAMP5 -> PA8); **OR**
   - **External Wideband Buffer Architecture:** Use **DAC1_OUT1 (PA4)** with the internal buffer **DISABLED** (`DAC_OUTPUTBUFFER_DISABLE`), routed immediately on the PCB to an external high-slew-rate op-amp buffer (e.g. OPA354, $250\text{ V}/\mu\text{s}$).
2. **Clock Tree Adjustment:**  
   Configure the RCC PLL tree for **SYSCLK = 160.0 MHz** rather than 170.0 MHz, ensuring TIM2 TRGO operates at **exactly 4,000,000 Hz with 0.00% frequency error** ($\text{PSC}=0, \text{ARR}=39$).
3. **Physical Bring-Up Scope Verification:**  
   Before connecting to the power amplifier stage, the DAC output pin must be inspected on a high-bandwidth oscilloscope (>100 MHz bandwidth) to verify rise times ($< 80\text{ ns}$), absence of DAC glitch impulses, and Total Harmonic Distortion (THD < -40 dB).

**Conclusion:** The project is cleared to proceed from Stage 1 into Stage 2 hardware firmware bring-up under these conditions.
