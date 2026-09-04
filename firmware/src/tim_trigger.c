/**
 * @file    tim_trigger.c
 * @brief   Hardware Timer implementation for exact 4.000000 MHz TRGO triggers (TIM2)
 *          and 50 Hz Pulse Repetition Interval (TIM6).
 * @target  STM32G474RET6 on NUCLEO-G474RE board.
 * @note    All hardware performance claims are marked [PENDING HARDWARE VALIDATION].
 *
 * Audit Reference:
 * - See stm32g4_dac_feasibility_audit.md §C.2 "[HIGH] Clock Prescaler / Frequency Mismatch at 170 MHz"
 * - Exact Math Derivation:
 *     F_timer_in = SYSCLK = 160,000,000 Hz
 *     Prescaler Division Ratio = PSC + 1 = 0 + 1 = 1
 *     Auto-reload Counter Period = ARR + 1 = 39 + 1 = 40
 *     F_trgo = 160,000,000 / (1 * 40) = 4,000,000.00 Hz (0.000% error)
 *     Sample Period T_s = 1 / 4.000000 MHz = 250.000 ns
 */

#include "tim_trigger.h"
#include "main.h"
#include "stm32g474_registers.h"

void TIM2_Trigger_Init(void)
{
    /* Enable TIM2 clock on APB1 bus */
    RCC->APB1ENR1 |= RCC_APB1ENR1_TIM2EN;
    __DSB();

    /* Disable counter during configuration */
    TIM2->CR1 &= ~TIM_CR1_CEN;

    /**
     * Prescaler = 0: Counter runs at full 160.000 MHz bus clock.
     * Auto-reload = 39: Generates an update event every 40 clock cycles.
     * 160,000,000 / 40 = 4,000,000 Hz.
     */
    TIM2->PSC = TIM2_PRESCALER;
    TIM2->ARR = TIM2_AUTORELOAD;

    /**
     * Master Mode Selection (MMS) in TIM2_CR2 (RM0440 §28.4.2):
     * MMS = 0b010 (Update): The Update Event (counter overflow) is selected
     * as the trigger output (TRGO) sent to the DAC3 peripheral.
     */
    TIM2->CR2 = TIM_CR2_MMS_UPDATE;

    /* Enable Auto-reload preload (ARPE) */
    TIM2->CR1 |= TIM_CR1_ARPE;

    /* Force update event to load shadow registers immediately */
    TIM2->EGR = 1U;
    TIM2->SR = 0U; /* Clear any pending status flag */
}

void TIM2_Trigger_Start(void)
{
    /* Reset counter to 0 to align first sample deterministically */
    TIM2->CNT = 0U;
    TIM2->CR1 |= TIM_CR1_CEN;
}

void TIM2_Trigger_Stop(void)
{
    TIM2->CR1 &= ~TIM_CR1_CEN;
    TIM2->CNT = 0U;
}

/* ========================================================================== */
/* PRI INTER-PULSE TIMER (TIM6)                                               */
/* ========================================================================== */

void PRI_Timer_Init(void)
{
    /* Enable TIM6 clock on APB1 bus */
    RCC->APB1ENR1 |= RCC_APB1ENR1_TIM6EN;
    __DSB();

    /* Disable TIM6 counter */
    TIM6->CR1 &= ~TIM_CR1_CEN;

    /**
     * TIM6 Clock = 160.0 MHz.
     * Prescaler = 159 -> 160 MHz / (159 + 1) = 1.0 MHz timer clock (1 us tick).
     * Inter-pulse dead time = 18,000 us (18.0 ms).
     * ARR = 18000 - 1 = 17999.
     */
    TIM6->PSC = 159U;                        /* 1 us per tick */
    TIM6->ARR = (SONAR_INTER_PULSE_GAP_US - 1U); /* 18,000 us = 18.0 ms */

    /* One-pulse mode (OPM = 1): Counter stops automatically at update event */
    TIM6->CR1 = (1UL << 3); /* OPM = 1 */

    /* Enable update interrupt */
    TIM6->DIER |= TIM_DIER_UIE;

    /* Force register reload */
    TIM6->EGR = 1U;
    TIM6->SR = 0U;
}

void PRI_Timer_ArmInterPulse(void)
{
    TIM6->CNT = 0U;
    TIM6->SR = 0U;
    TIM6->CR1 |= TIM_CR1_CEN;
}

void PRI_Timer_Stop(void)
{
    TIM6->CR1 &= ~TIM_CR1_CEN;
    TIM6->SR = 0U;
}
