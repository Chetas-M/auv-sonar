# Member A firmware workstream

This folder bridges the generated waveform lookup tables to an STM32G474
timer-triggered DAC/DMA implementation. It deliberately does not select a DAC
channel, timer, DMA request, or pins: those must match the board schematic and
the STM32CubeMX-generated project.

## Included behaviour

- Uses the generated 8,000-sample, 12-bit chirp tables in
  `outputs_matlab/headers/`.
- Starts one normal-mode DMA transfer for each 2 ms ping.
- Stops the sample timer and DMA at transfer completion.
- Accepts a new profile request during a ping but applies it only at the next
  `sonar_tx_start_ping()` call. The active DMA source is never changed mid-pulse.

## Add it to STM32CubeIDE

1. Create an STM32G474 CubeMX project and configure a DAC channel triggered by
   a timer TRGO at 4 MHz. Configure its DMA as memory-to-peripheral, normal
   mode, half-word memory and peripheral widths, and a length of 8,000 samples.
2. Copy the four generated headers from `outputs_matlab/headers/` into
   `Core/Inc/`, or add that folder to the compiler include paths.
3. Copy `firmware/include/sonar_transmitter.h` to `Core/Inc/` and
   `firmware/src/sonar_transmitter.c` to `Core/Src/`.
4. Implement `SonarTxHardwareOps` in `main.c` with your Cube/HAL handles. Its
   `start_dac_dma` callback should call the DAC DMA-start routine; its timer
   callbacks should start/stop the configured 4 MHz trigger timer.
5. Call `sonar_tx_init()` once after HAL peripheral initialization. Call
   `sonar_tx_start_ping()` from a 20 ms scheduler/timer callback. In the DAC DMA
   transfer-complete callback, call `sonar_tx_on_dma_complete()`.
6. When the adaptive algorithm selects a profile, call
   `sonar_tx_request_profile()`. It is intentionally not a DMA restart.

## Hardware verification required

Confirm the 4 MHz DAC trigger, 2 ms pulse duration, chirp start/end frequency,
and output settling on an oscilloscope before connecting a power amplifier or
transducer.
