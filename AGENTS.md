# AGENTS.md: AI Pair-Programming & Modeling Guidelines

Welcome, Agent! This repository implements the **AUV Low-Power Adaptive Software-Defined Sonar Transmitter Payload** (SIH Problem 26058).

Before reading individual files or proposing changes, read the master repository context document:
👉 **[`REPOSITORY_CONTEXT.md`](file:///d:/AUV%20sonar/REPOSITORY_CONTEXT.md)**

---

## 1. Golden Engineering Rules

1. **Truth in Engineering (Strict Scope):**
   - This project models and validates the **transmitter payload pipeline**: waveform synthesis $\to$ 12-bit DAC quantization $\to$ DMA memory mapping $\to$ frequency-dependent attenuation $\to$ propagation viability filtering $\to$ mission objective profile selection $\to$ directional hysteresis & debounce $\to$ atomic ping-boundary latching $\to$ duty-cycle power dissipation.
   - It **DOES NOT** validate physical ocean acoustic propagation, real echoes, hydrophone receiver processing, transducer piezoelectric resonance, or analog power amplifier settling.
   - Hardware bring-up is transmitter-side only and marked as `[PENDING HARDWARE VALIDATION]`.
   - Never claim or hallucinate that field ocean tests or receiver echo measurements were conducted.

2. **Locked Hardware Constraints (Single Source of Truth):**
   - Microcontroller: **STMicroelectronics STM32G474RET6** @ 160.0 MHz SYSCLK (PLL HSE/HSI).
   - DAC Update Rate: **4.0 MSPS (12-bit unsigned, $0\text{–}4095$, midscale $2048$)**.
   - Pulse Duration: **$T_p = 2.0\text{ ms}$ ($N_p = 8,000\text{ samples}$ / $16\text{ KB}$ buffer)**.
   - Ping Repetition: **$\text{PRI} = 20.0\text{ ms}$ ($50\text{ Hz}$ ping rate, $10.0\%$ duty cycle)**.
   - DAC Hardware Path: **Internal DAC3 Channel 2** (unbuffered, 15 MSPS capable) routed on-chip directly to **OPAMP3** in High-Speed Follower mode ($45\text{ V}/\mu\text{s}$ slew rate) out to pin **PB1** (Morpho CN10 Pin 24). The slow internal DAC buffer is explicitly bypassed.

3. **Three Canonical Profiles:**
   - **`LOW_FREQUENCY` (100–220 kHz):** $f_c = 160\text{ kHz}, B = 120\text{ kHz}$, Amplitude $A = 1.0$. Lowest absorption ($63.99\text{ dB/km}$); long-range fallback ($>175\text{ m}$).
   - **`BALANCED` (200–400 kHz):** $f_c = 300\text{ kHz}, B = 200\text{ kHz}$, Amplitude $A = 0.7$. Best theoretical range resolution ($\Delta R = 3.75\text{ mm}$); default survey mode.
   - **`HIGH_FREQUENCY` (350–500 kHz):** $f_c = 425\text{ kHz}, B = 150\text{ kHz}$, Amplitude $A = 0.4$. Highest theoretical directivity factor ($1.417\times$ reference); spatial angular resolution mode.

4. **Testing & Verification:**
   - Always run the test suite using `pytest -v` from the workspace root (79 tests must pass).
   - Ensure bit-exact parity between Python waveforms and C firmware header tables in `outputs/headers/`.

---

## 2. Directory Quick Links

- [**`REPOSITORY_CONTEXT.md`**](file:///d:/AUV%20sonar/REPOSITORY_CONTEXT.md): Authoritative architectural manual covering all physics, state machines, math, and firmware.
- [**`src/README.md`**](file:///d:/AUV%20sonar/src/README.md): Python Digital Twin module breakdown & API usage.
- [**`tests/README.md`**](file:///d:/AUV%20sonar/tests/README.md): Automated verification suite architecture (79 tests).
- [**`firmware/README.md`**](file:///d:/AUV%20sonar/firmware/README.md): STM32G474 C11 bare-metal firmware guide & host build.
- [**`firmware/hardware_bringup_checklist.md`**](file:///d:/AUV%20sonar/firmware/hardware_bringup_checklist.md): 8-step lab oscilloscope & DMM protocol.
- [**`firmware/stm32g4_dac_feasibility_audit.md`**](file:///d:/AUV%20sonar/firmware/stm32g4_dac_feasibility_audit.md): Complete 30KB datasheet & hardware feasibility audit.
- [**`matlab/README.md`**](file:///d:/AUV%20sonar/matlab/README.md): MATLAB digital twin mirror & headless execution.
