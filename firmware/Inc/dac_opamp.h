/**
 * @file    dac_opamp.h
 * @brief   Hardware configuration for internal DAC3 Channel 2 routed to OPAMP3.
 * @target  STM32G474RET6 on NUCLEO-G474RE board (Output on Pin PB1, Morpho CN10-24).
 * @note    All hardware performance claims are marked [PENDING HARDWARE VALIDATION].
 *
 * Audit Reference:
 * - See stm32g4_dac_feasibility_audit.md §C.1 "[CRITICAL] Internal DAC Output Buffer Slew Rate Limitation"
 * - DAC1 internal buffer caps at 1.0 MSPS (t_settling = 1.6 to 3.0 us).
 * - DAC3 Channel 2 is a 15 MSPS internal core (AN5306). When routed internally
 *   to OPAMP3 in High-Speed Follower mode (45 V/us slew rate, 13 MHz bandwidth),
 *   it provides the analog drive required for 4.0 MSPS (250 ns) sampling.
 */

#ifndef DAC_OPAMP_H_
#define DAC_OPAMP_H_

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief  Initializes GPIO PB1 (analog), OPAMP3 (high-speed follower), and
 *         DAC3 Channel 2 (buffer disabled, internal routing, TIM2 TRGO trigger, DMA request).
 */
void DAC3_OPAMP3_Init(void);

/**
 * @brief  Enables the DAC3 Channel 2 hardware trigger from TIM2 TRGO.
 */
void DAC3_EnableHardwareTrigger(void);

/**
 * @brief  Disables the DAC3 Channel 2 hardware trigger.
 */
void DAC3_DisableHardwareTrigger(void);

/**
 * @brief  Sets a static 12-bit DAC code (0 to 4095) for DC calibration and bring-up testing.
 * @param  code: 12-bit unsigned code. 2048 corresponds to nominal midscale (1.65 V).
 */
void DAC3_SetStaticCode(uint16_t code);

/**
 * @brief  Clears the DAC3 Channel 2 DMA underrun flag (DAC_SR.DMAUDR2).
 *         RM0440 §22.4.15 states that when an underrun occurs, DMA requests are disabled
 *         until this flag is explicitly cleared by software.
 */
void DAC3_ClearDMAUnderrunFlag(void);

/**
 * @brief  Returns the address of DAC3 12-bit right-aligned data holding register (DHR12R2)
 *         used as the DMA peripheral destination.
 */
uint32_t DAC3_GetDHR12R2_Address(void);

#ifdef __cplusplus
}
#endif

#endif /* DAC_OPAMP_H_ */
