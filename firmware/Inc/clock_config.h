/**
 * @file    clock_config.h
 * @brief   Clock tree configuration for STM32G474 locked to SYSCLK = 160.0 MHz.
 * @target  STM32G474RET6 on NUCLEO-G474RE.
 *
 * Rationale (Feasibility Audit §C.2):
 * - At 170.0 MHz (nominal default), TIM2 ARR=41.5 (non-integer). Divisors of 42
 *   or 41 yield 4.048 MHz (+1.19%) or 3.953 MHz (-1.16%), violating exact sonar
 *   range resolution equations.
 * - At 160.0 MHz, 160.0 MHz / 40 = EXACTLY 4.000000 MHz (0.000% error) with
 *   TIM2 PSC=0, ARR=39.
 */

#ifndef CLOCK_CONFIG_H_
#define CLOCK_CONFIG_H_

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief  Configures RCC PLL to achieve SYSCLK = 160.000 MHz.
 *         Tries 8.0 MHz HSE (from ST-LINK MCO) first; falls back to 16.0 MHz HSI if HSE absent.
 *         Configures Flash 4-wait-states and Power Range 1 Boost mode.
 */
void SystemClock_Config(void);

/**
 * @brief  Returns active SYSCLK frequency in Hz (160000000UL).
 */
uint32_t Clock_GetSysClkFreq(void);

/**
 * @brief  Returns active AHB (HCLK) frequency in Hz (160000000UL).
 */
uint32_t Clock_GetHClkFreq(void);

/**
 * @brief  Returns active APB1 peripheral clock frequency in Hz (160000000UL).
 */
uint32_t Clock_GetPClk1Freq(void);

/**
 * @brief  Returns active APB2 peripheral clock frequency in Hz (160000000UL).
 */
uint32_t Clock_GetPClk2Freq(void);

#ifdef __cplusplus
}
#endif

#endif /* CLOCK_CONFIG_H_ */
