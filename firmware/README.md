# STM32G474 Firmware: AUV Adaptive Sonar Transmitter Payload

**Target Microcontroller:** STMicroelectronics STM32G474RET6 (ARM Cortex-M4F @ 160.0 MHz)  
**Target Evaluation Board:** NUCLEO-G474RE  
**Project Identifier:** SIH PS 26058 (Autonomous Underwater Vehicle Sonar)  
**Status:** Compile-ready firmware source tree, host verification testbench, and lab bring-up protocol.  
*All hardware-dependent performance figures are marked as `[PENDING HARDWARE VALIDATION]`.*

---

## 1. Quickstart & Build Instructions

### Host Build Verification (Zero Hardware Required)
Test syntax, type correctness, and linker resolution using MinGW GCC on Windows:
```bash
cd firmware
mingw32-make host
# Or on Linux / macOS:
# make host
```
Output binary will be placed at `firmware/build/auv_sonar_transmitter_host.exe`.

### Automated Firmware Parity Tests
Run the Python test suite verifying that the firmware C headers match the Python waveform generator bit-for-bit:
```bash
# From workspace root:
python -m pytest tests/test_firmware_lut_parity.py -v
```

### ARM GCC Cross-Compilation (For STM32 Target)
When the ARM GNU Toolchain (`arm-none-eabi-gcc`) is installed:
```bash
cd firmware
make target
```
Outputs: `build/auv_sonar_transmitter.elf`, `build/auv_sonar_transmitter.bin`, and `build/auv_sonar_transmitter.hex`.

### Flashing to NUCLEO-G474RE Board
```bash
# Via OpenOCD:
openocd -f board/st_nucleo_g4.cfg -c "program build/auv_sonar_transmitter.elf verify reset exit"

# Or via STM32CubeProgrammer CLI:
STM32_Programmer_CLI -c port=SWD -w build/auv_sonar_transmitter.bin 0x08000000 -v -rst
```

---

## 2. Locked Hardware Architecture

This firmware implements the locked hardware architecture defined in the [STM32G4 DAC Feasibility Audit](file:///d:/AUV%20sonar/firmware/stm32g4_dac_feasibility_audit.md):

1. **Clock Tree:** SYSCLK is tuned to **160.000 MHz** via RCC PLL (8.0 MHz HSE from ST-LINK MCO: $\text{PLLM}=1, \text{PLLN}=40, \text{PLLR}=2$). This enables an exact integer division by 40 ($\text{PSC}=0, \text{ARR}=39$) for a **4,000,000.00 Hz TIM2 TRGO trigger rate with 0.000% frequency error**.
2. **DAC & OPAMP Signal Path:** Uses internal 15 MSPS **DAC3 Channel 2** routed directly on-chip to **OPAMP3** in High-Speed Follower mode out to pin **PB1** (Morpho connector `CN10 Pin 24`, confirmed conflict-free). The slow internal DAC buffer is explicitly **DISABLED** (`DAC_OUTPUTBUFFER_DISABLE`), eliminating the 1 MSPS bottleneck.
3. **High-Frequency Interface Mode (`DAC_MCR.HFSEL`):** Configured for high-frequency AHB operation (`0b01` for $80\text{ MHz} < \text{AHB} \le 160\text{ MHz}$).
4. **DMA Streaming:** DMA1 Channel 1 mapped to `DAC3_CH2` (DMAMUX1 Request ID 103 / 0x67). Streams 8,000 half-words (16-bit) per chirp pulse directly from Flash to `DAC3->DHR12R2` at $8.0\text{ MB/s}$ throughput (1.18% of AHB bus matrix capacity).
5. **Atomic Profile Switching:** Low-frequency (100–220 kHz), Balanced (200–400 kHz), and High-frequency (350–500 kHz) profile transitions are queued asynchronously and latched **strictly at ping boundaries** inside the 50 Hz DMA Transfer-Complete interrupt.
6. **Low-Power PRI Operation:** $2.000\text{ ms}$ active chirp every $20.000\text{ ms}$ PRI (10.0% duty cycle, 50 Hz ping rate). CPU enters `__WFI()` sleep mode during both the pulse and the 18.0 ms quiet gap ($< 0.001\%$ CPU duty load).

---

## 3. Directory Structure

```text
firmware/
├── Inc/
│   ├── main.h                       # System constants, pin definitions, compile-time assertions
│   ├── clock_config.h               # 160.0 MHz PLL clock tree prototypes
│   ├── dac_opamp.h                  # DAC3 Ch2 and OPAMP3 high-speed follower interface
│   ├── tim_trigger.h                # TIM2 4.0 MSPS TRGO trigger and PRI timer interface
│   ├── dma_stream.h                 # DMA1 Ch1 DMAMUX streaming and atomic profile switching
│   ├── sonar_lut.h                  # LUT accessors consuming precomputed headers
│   ├── stm32g4xx_it.h               # Interrupt service routine prototypes
│   └── stm32g474_registers.h        # Hardware register map conforming to RM0440
├── Src/
│   ├── main.c                       # System init, status reporting, low-power WFI sleep
│   ├── clock_config.c               # PLL configuration (160 MHz, HSE/HSI fallback, Flash 4WS)
│   ├── dac_opamp.c                  # DAC3_OUT2 -> OPAMP3 internal follower -> PB1 setup
│   ├── tim_trigger.c                # TIM2 PSC=0 ARR=39 4.000000 MHz TRGO & TIM6 PRI timer
│   ├── dma_stream.c                 # DMA1 Ch1 memory-to-peripheral transfer & atomic switching
│   ├── sonar_lut.c                  # Waveform LUT instantiation from outputs/headers/*.h
│   └── stm32g4xx_it.c               # DMA TC, PRI timer, and User Button PC13 ISRs
├── hardware_bringup_checklist.md    # Detailed oscilloscope & DMM lab bring-up protocol
├── stm32g4_dac_feasibility_audit.md # Authoritative datasheet & architecture feasibility audit
├── auv_sonar_g474.ioc               # STM32CubeMX hardware peripheral configuration
├── Makefile                         # Host verification and ARM GCC cross-compilation
└── README.md                        # This documentation file
```

---

## 4. Hardware Pinout Table (NUCLEO-G474RE)

| Signal Name | MCU Pin | Board Connector | Hardware Function | Conflict Status |
|---|---|---|---|---|
| **Sonar Output** | **PB1** | Morpho **CN10 Pin 24** | OPAMP3 High-Speed Follower Output ($45\text{ V}/\mu\text{s}$) | **FREE** (Dedicated) |
| **Ground Ref** | **GND** | Morpho **CN10 Pin 20** | Oscilloscope ground spring point | **GND** |
| **Transmit LED** | **PA5** | Onboard LED | Green LED (toggles during active ping) | Onboard LD2 |
| **Profile Button**| **PC13**| Onboard Pushbutton | Blue Button (press to cycle profiles manually) | Onboard B1 |
| **MCO Clock Out**| **PA8** | Morpho **CN10 Pin 23** | SYSCLK / 16 clock check ($10.000\text{ MHz}$) | **FREE** |

---

## 5. Lab Bring-Up Protocol

When physical NUCLEO-G474RE hardware is placed on the test bench, execute the comprehensive 8-step verification procedure documented in:
👉 **[hardware_bringup_checklist.md](file:///d:/AUV%20sonar/firmware/hardware_bringup_checklist.md)**

Key verification checkpoints:
1. Unpowered impedance: $R > 100\text{ k}\Omega$ between PB1 and GND.
2. VREF+ and VDD power rail stability: $3.300\text{ V} \pm 10\text{ mV}$.
3. Clock tree verification: $10.000\text{ MHz} \pm 500\text{ Hz}$ on PA8 (MCO).
4. Timer TRGO trigger: $4,000,000\text{ Hz} \pm 200\text{ Hz}$ on TIM2 trigger.
5. DC midscale DAC level: $1.650\text{ V} \pm 25\text{ mV}$ on PB1.
6. Dynamic chirp playback: $2.000\text{ ms}$ pulse width, $20.000\text{ ms}$ PRI ($50.0\text{ Hz}$).
7. Envelope shape: Smooth Hann window tapering without edge spikes.
8. Spectral purity: Harmonics and DAC imaging rejection.
