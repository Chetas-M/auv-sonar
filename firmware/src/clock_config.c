/**
 * @file    clock_config.c
 * @brief   Clock tree initialization for SYSCLK = 160.0 MHz on STM32G474.
 * @target  STM32G474RET6 on NUCLEO-G474RE board.
 * @note    All hardware performance claims are marked [PENDING HARDWARE VALIDATION].
 *
 * Audit Reference:
 * - See stm32g4_dac_feasibility_audit.md §C.2 "[HIGH] Clock Prescaler / Frequency Mismatch at 170 MHz"
 * - Setting SYSCLK to 160.0 MHz produces an exact integer divisor of 40 for TIM2 TRGO:
 *     F_trgo = 160,000,000 / (1 * 40) = 4,000,000.00 Hz (0.000% error).
 */

#include "clock_config.h"
#include "main.h"
#include "stm32g474_registers.h"

static uint32_t s_sysclk_hz = SYSCLK_FREQ_HZ;

void SystemClock_Config(void)
{
    /* ---------------------------------------------------------------------- */
    /* 1. POWER INTERFACE CLOCK & VOLTAGE REGULATOR RANGE 1 BOOST MODE        */
    /* ---------------------------------------------------------------------- */
    /* Enable Power Control clock (APB1) */
    RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN;
    __DSB();

    /**
     * Power Regulator Boost Mode Configuration (RM0440 §6.1.1):
     * For SYSCLK > 150 MHz up to 170 MHz, the internal voltage regulator must
     * operate in Range 1 Boost mode (Vcore = 1.28 V nominal).
     * In PWR_CR5, clearing bit R1MODE (bit 8 = 0) enables Boost Mode.
     * [PENDING HARDWARE VALIDATION: Confirm core supply stability on bench]
     */
    PWR->CR5 &= ~PWR_CR5_R1MODE;

    /* ---------------------------------------------------------------------- */
    /* 2. FLASH ACCESS LATENCY & CACHES (RM0440 §3.3.3 Table 17)              */
    /* ---------------------------------------------------------------------- */
    /**
     * In Range 1 Boost mode at 160 MHz:
     * - 0 to 34 MHz:   0 wait states
     * - 34 to 68 MHz:  1 wait state
     * - 68 to 102 MHz: 2 wait states
     * - 102 to 136 MHz: 3 wait states
     * - 136 to 170 MHz: 4 wait states (FLASH_ACR_LATENCY_4WS)
     * Instruction cache, data cache, and prefetch buffer are enabled to prevent
     * Flash wait states from stalling instruction execution.
     */
    FLASH->ACR = FLASH_ACR_LATENCY_4WS | FLASH_ACR_PRFTEN | FLASH_ACR_ICEN | FLASH_ACR_DCEN;

    /* Verify Flash latency was latched */
    while ((FLASH->ACR & 0x0FUL) != FLASH_ACR_LATENCY_4WS) {
        /* Wait for Flash ACR update */
    }

    /* ---------------------------------------------------------------------- */
    /* 3. OSCILLATOR STARTUP & PLL CONFIGURATION (HSE with HSI fallback)      */
    /* ---------------------------------------------------------------------- */
    /**
     * On NUCLEO-G474RE, the ST-LINK MCO delivers an 8.000 MHz clock to OSC_IN (HSE bypass).
     * HSE PLL Equation:
     *   f_vco = (f_in / PLLM) * PLLN = (8.0 MHz / 1) * 40 = 320.0 MHz
     *   f_sysclk = f_vco / PLLR = 320.0 MHz / 2 = 160.000 MHz
     *
     * HSI Fallback Equation (if HSE is not connected / standalone board):
     *   f_vco = (16.0 MHz / 2) * 40 = 320.0 MHz
     *   f_sysclk = 320.0 MHz / 2 = 160.000 MHz
     */
    bool hse_ready = false;
    RCC->CR |= RCC_CR_HSEON;

    /* Spin with timeout (~20 ms) waiting for HSERDY */
    for (volatile uint32_t timeout = 0; timeout < 50000UL; timeout++) {
        if (RCC->CR & RCC_CR_HSERDY) {
            hse_ready = true;
            break;
        }
    }

    /* Disable PLL before reconfiguration */
    RCC->CR &= ~RCC_CR_PLLON;
    while (RCC->CR & RCC_CR_PLLRDY) {
        /* Wait for PLL to unlock */
    }

    if (hse_ready) {
        /* Configure PLL from HSE (8.0 MHz) */
        /* PLLM = 1 (bits 7:4 = 0b0000 -> /1)                                 */
        /* PLLN = 40 (bits 14:8 = 40)                                          */
        /* PLLR = 2 (bits 26:25 = 0b00 -> /2)                                 */
        /* PLLSRC = HSE (bits 1:0 = 0b11)                                     */
        RCC->PLLCFGR = (RCC_PLLCFGR_PLLSRC_HSE) |
                       (0U << 4)                | /* PLLM = 1 */
                       (40U << 8)               | /* PLLN = 40 -> VCO = 320 MHz */
                       (0U << 25)               | /* PLLR = 2 -> SYSCLK = 160 MHz */
                       RCC_PLLCFGR_PLLREN;        /* Enable Main PLL R Output */
    } else {
        /* Enable HSI16 */
        RCC->CR |= RCC_CR_HSION;
        while (!(RCC->CR & RCC_CR_HSIRDY)) {
            /* Wait for HSI ready */
        }

        /* Configure PLL from HSI (16.0 MHz) */
        /* PLLM = 2 (bits 7:4 = 0b0001 -> /2 -> 8.0 MHz input to VCO)        */
        /* PLLN = 40 (bits 14:8 = 40 -> VCO = 320 MHz)                         */
        /* PLLR = 2 (bits 26:25 = 0b00 -> /2 -> SYSCLK = 160 MHz)             */
        RCC->PLLCFGR = (RCC_PLLCFGR_PLLSRC_HSI) |
                       (1U << 4)                | /* PLLM = 2 */
                       (40U << 8)               | /* PLLN = 40 */
                       (0U << 25)               | /* PLLR = 2 */
                       RCC_PLLCFGR_PLLREN;
    }

    /* Enable PLL */
    RCC->CR |= RCC_CR_PLLON;
    while (!(RCC->CR & RCC_CR_PLLRDY)) {
        /* Wait for PLL lock [PENDING HARDWARE VALIDATION] */
    }

    /* ---------------------------------------------------------------------- */
    /* 4. BUS PRESCALERS & SWITCH TO PLL                                      */
    /* ---------------------------------------------------------------------- */
    /**
     * Bus Prescaler Setup:
     * - AHB Prescaler = /1 -> HCLK = 160.0 MHz
     * - APB1 Prescaler = /1 -> PCLK1 = 160.0 MHz (Timer clock = 160.0 MHz)
     * - APB2 Prescaler = /1 -> PCLK2 = 160.0 MHz
     */
    /* RCC_CFGR: Switch system clock source to PLL (SW = 0b11) */
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW_MSK) | RCC_CFGR_SW_PLL;

    /* Wait until PLL is confirmed as system clock source (SWS == 0b11) */
    while ((RCC->CFGR & RCC_CFGR_SWS_MSK) != RCC_CFGR_SWS_PLL) {
        /* Wait for clock switch confirmation */
    }

    s_sysclk_hz = SYSCLK_FREQ_HZ;
}

uint32_t Clock_GetSysClkFreq(void)
{
    return s_sysclk_hz;
}

uint32_t Clock_GetHClkFreq(void)
{
    return s_sysclk_hz; /* AHB Prescaler = 1 */
}

uint32_t Clock_GetPClk1Freq(void)
{
    return s_sysclk_hz; /* APB1 Prescaler = 1 */
}

uint32_t Clock_GetPClk2Freq(void)
{
    return s_sysclk_hz; /* APB2 Prescaler = 1 */
}
