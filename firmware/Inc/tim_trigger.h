/**
 * @file    tim_trigger.h
 * @brief   Hardware Timer configuration for 4.000000 MHz DAC TRGO trigger (TIM2)
 *          and 50 Hz Pulse Repetition Interval timer (TIM6).
 * @target  STM32G474RET6
 * @note    All hardware performance claims are marked [PENDING HARDWARE VALIDATION].
 *
 * Audit Reference:
 * - See stm32g4_dac_feasibility_audit.md §C.2
 * - TIM2 PSC=0, ARR=39 -> 4,000,000.00 Hz EXACT TRGO update rate.
 */

#ifndef TIM_TRIGGER_H_
#define TIM_TRIGGER_H_

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief  Initializes TIM2 counter to generate TRGO update events at 4.000000 MHz.
 *         Does not enable counter until transmission pulse begins.
 */
void TIM2_Trigger_Init(void);

/**
 * @brief  Starts the TIM2 counter to begin streaming TRGO triggers into DAC3/DMA1.
 */
void TIM2_Trigger_Start(void);

/**
 * @brief  Stops the TIM2 counter (disables TRGO triggers during inter-pulse quiet period).
 */
void TIM2_Trigger_Stop(void);

/**
 * @brief  Initializes TIM6 as a single-shot / periodic timer for the 20.0 ms PRI
 *         (18.0 ms inter-pulse dead time).
 */
void PRI_Timer_Init(void);

/**
 * @brief  Arms the PRI timer for an 18.0 ms quiet window. When expired, TIM6 ISR fires.
 */
void PRI_Timer_ArmInterPulse(void);

/**
 * @brief  Stops the PRI timer.
 */
void PRI_Timer_Stop(void);

#ifdef __cplusplus
}
#endif

#endif /* TIM_TRIGGER_H_ */
