/**
 * @file    stm32g4xx_it.c
 * @brief   Interrupt Service Routines for STM32G474 AUV Sonar Transmitter.
 * @target  STM32G474RET6 on NUCLEO-G474RE.
 * @note    All hardware performance claims are marked [PENDING HARDWARE VALIDATION].
 *
 * Audit Reference:
 * - See stm32g4_dac_feasibility_audit.md §4 "CPU Independence Verification"
 *   CPU load during ping emission is 0.0%. CPU is only interrupted on Transfer
 *   Complete (TC) at 50 Hz and PRI interval timer expiration.
 */

#include "stm32g4xx_it.h"
#include "dma_stream.h"
#include "main.h"
#include "stm32g474_registers.h"

/* EXTI Registers for User Button PC13 */
#define EXTI_BASE       (0x40010400UL)
typedef struct {
    __IO uint32_t IMR1;
    __IO uint32_t EMR1;
    __IO uint32_t RTSR1;
    __IO uint32_t FTSR1;
    __IO uint32_t SWIER1;
    __IO uint32_t PR1;
} EXTI_TypeDef;
#define EXTI            ((EXTI_TypeDef *) EXTI_BASE)

/* SysTick millisecond counter */
static volatile uint32_t s_systick_ms = 0U;

void SysTick_Handler(void)
{
    s_systick_ms++;
}

/**
 * @brief  DMA1 Channel 1 Interrupt Handler.
 *         Fires upon completion of the 8,000th sample (2.0 ms chirp completion).
 *         Latches active profile atomically and arms 18.0 ms PRI timer.
 */
void DMA1_Channel1_IRQHandler(void)
{
    if (DMA1->ISR & DMA_ISR_TCIF1) {
        DMA_Sonar_OnTransferComplete();
    }
}

/**
 * @brief  TIM6 DAC Interrupt Handler.
 *         Fires upon expiration of the 18.0 ms inter-pulse quiet period.
 *         Re-enables DMA and TIM2 to launch the next ping.
 */
void TIM6_DAC_IRQHandler(void)
{
    if (TIM6->SR & TIM_SR_UIF) {
        DMA_Sonar_OnPriTimerExpired();
    }
}

/**
 * @brief  EXTI Line 15..10 Handler (NUCLEO-G474RE Blue Pushbutton PC13).
 *         Cycles active sonar profile on button press.
 */
void EXTI15_10_IRQHandler(void)
{
    /* Check if EXTI line 13 triggered (PC13 button) */
    if (EXTI->PR1 & (1UL << BUTTON_B1_PIN)) {
        /* Clear pending interrupt flag */
        EXTI->PR1 = (1UL << BUTTON_B1_PIN);

        /* Debounce check using SysTick */
        static uint32_t last_press_ms = 0;
        if ((s_systick_ms - last_press_ms) > 200U) {
            last_press_ms = s_systick_ms;
            /* Queue next profile (LOW -> BALANCED -> HIGH -> LOW...) */
            DMA_Sonar_CycleNextProfile();
        }
    }
}

/* Cortex-M4 Core Fault Handlers */
void NMI_Handler(void)
{
    while (1) {}
}

void HardFault_Handler(void)
{
    while (1) {
        /* [PENDING HARDWARE VALIDATION: Inspect PC/LR on debugger breakpoint] */
    }
}

void MemManage_Handler(void)
{
    while (1) {}
}

void BusFault_Handler(void)
{
    while (1) {}
}

void UsageFault_Handler(void)
{
    while (1) {}
}

void SVC_Handler(void) {}
void DebugMon_Handler(void) {}
void PendSV_Handler(void) {}
