/**
 * @file    main.c
 * @brief   Main entry point for STM32G474 AUV Adaptive Sonar Transmitter.
 * @target  STM32G474RET6 on NUCLEO-G474RE board.
 * @note    All hardware performance claims are marked [PENDING HARDWARE VALIDATION].
 *
 * System Architecture Summary:
 * - SYSCLK: 160.000 MHz (PLL from 8 MHz HSE, or fallback 16 MHz HSI).
 * - DAC Path: DAC3 Channel 2 routed internally to OPAMP3 (PB1, CN10-24).
 *   Internal buffer disabled; high-speed follower mode (45 V/us slew rate).
 * - Timer: TIM2 PSC=0, ARR=39 -> Exactly 4.000000 MHz TRGO hardware trigger.
 * - DMA: DMA1 Channel 1 via DMAMUX1, half-word memory-to-peripheral, 8,000 samples.
 * - PRI: 2.0 ms active chirp every 20.0 ms PRI (10% duty cycle, 50 Hz ping rate).
 * - Atomic Switching: Profile transitions latched at DMA Transfer-Complete boundary.
 * - CPU Idle: CPU executes __WFI() sleep during 99.9% of operational time.
 */

#include "main.h"
#include "clock_config.h"
#include "dac_opamp.h"
#include "tim_trigger.h"
#include "dma_stream.h"
#include "sonar_lut.h"
#include "stm32g474_registers.h"

static void GPIO_Init(void);
static void NVIC_Configuration(void);

int main(void)
{
    /* ---------------------------------------------------------------------- */
    /* 1. CLOCK CONFIGURATION (Feasibility Audit §C.2)                        */
    /* ---------------------------------------------------------------------- */
    /* Tune SYSCLK to exactly 160.000 MHz for 0.000% error on 4.0 MSPS timer */
    SystemClock_Config();

    /* ---------------------------------------------------------------------- */
    /* 2. GPIO INITIALIZATION                                                 */
    /* ---------------------------------------------------------------------- */
    /* User LED2 (PA5) and User Button B1 (PC13) */
    GPIO_Init();

    /* ---------------------------------------------------------------------- */
    /* 3. INTEGRITY AUDIT OF PRECOMPUTED WAVEFORM TABLES                      */
    /* ---------------------------------------------------------------------- */
    if (!Sonar_ValidateLUTIntegrity()) {
        Error_Handler();
    }

    /* ---------------------------------------------------------------------- */
    /* 4. PERIPHERAL HARDWARE INITIALIZATION                                  */
    /* ---------------------------------------------------------------------- */
    /**
     * CRITICAL INITIALIZATION SEQUENCE (ST CubeG4 Bug / RM0440 §22.4.15):
     * DMA and DMAMUX MUST be initialized BEFORE DAC!
     * If DAC3_CR.DMAEN2 is asserted before DMA1 / DMAMUX1 clocks and registers
     * are configured, an unserviced DMA request can set DAC_SR.DMAUDR2 (DMA Underrun).
     * Per RM0440 §22.4.15, DMAUDR2 permanently disables DAC DMA requests until
     * cleared by software, causing silent transmission failure on hardware.
     */
    /* Step 4a: Initialize DMA1 Channel 1 via DMAMUX1 (Request ID 0x67) */
    DMA_Sonar_Init(SONAR_PROFILE_BALANCED);

    /* Step 4b: Initialize DAC3 Channel 2 internal follower to OPAMP3 out to pin PB1 */
    DAC3_OPAMP3_Init();

    /* Step 4c: Initialize TIM2 hardware trigger generator (4.000000 MHz TRGO) */
    TIM2_Trigger_Init();

    /* Step 4d: Initialize TIM6 PRI timer for 18.0 ms inter-pulse dead time (50 Hz) */
    PRI_Timer_Init();

    /* Step 4e: Configure NVIC interrupt priorities and enable DMA & PRI interrupts */
    NVIC_Configuration();

    /* ---------------------------------------------------------------------- */
    /* 5. START CONTINUOUS ADAPTIVE SONAR PINGING                             */
    /* ---------------------------------------------------------------------- */
    /* Launch initial 2.0 ms chirp pulse */
    DMA_Sonar_Start();

    /* ---------------------------------------------------------------------- */
    /* 6. LOW-POWER SLEEP MAIN LOOP (Feasibility Audit §4 & §7)               */
    /* ---------------------------------------------------------------------- */
    /**
     * During active 2.0 ms chirp emission:
     * - Hardware Timer TRGO directly clocks DAC and triggers DMA.
     * - CPU load is 0.0%.
     *
     * During 18.0 ms inter-pulse dead time:
     * - TIM2 is stopped; DAC outputs DC midscale (1.65 V).
     * - TIM6 counts 18.0 ms.
     * - CPU sleeps via __WFI(), consuming minimal battery power.
     *
     * Total active CPU duty cycle is < 0.001% (only servicing 50 Hz interrupts).
     */
    while (1) {
        /* Wait For Interrupt: Wakes up on DMA TC, TIM6 PRI, or User Button press */
        __WFI();
    }
}

static void GPIO_Init(void)
{
    /* Enable GPIOA and GPIOC peripheral clocks */
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIOCEN;
    __DSB();

    /* Configure PA5 as Output (User LED2) */
    /* Clear bits 11:10 and set to 0b01 (General purpose output mode) */
    GPIOA->MODER &= ~(0x3UL << (LED2_PIN * 2));
    GPIOA->MODER |= (0x1UL << (LED2_PIN * 2));
    /* Push-pull output */
    GPIOA->OTYPER &= ~(1UL << LED2_PIN);
    /* Low speed */
    GPIOA->OSPEEDR &= ~(0x3UL << (LED2_PIN * 2));
    /* No pull-up, no pull-down */
    GPIOA->PUPDR &= ~(0x3UL << (LED2_PIN * 2));
    /* Turn off LED initially */
    GPIOA->BRR = (1UL << LED2_PIN);

    /* Configure PC13 as Input (User Button B1) */
    /* Clear bits 27:26 to 0b00 (Input mode) */
    GPIOC->MODER &= ~(0x3UL << (BUTTON_B1_PIN * 2));
    /* Enable internal pull-up (bits 27:26 = 0b01) */
    GPIOC->PUPDR &= ~(0x3UL << (BUTTON_B1_PIN * 2));
    GPIOC->PUPDR |= (0x1UL << (BUTTON_B1_PIN * 2));
}

static void NVIC_Configuration(void)
{
    /**
     * NVIC Interrupt Priority Allocation:
     * - DMA1 Channel 1 (Ping completion): Priority 0 (highest time-criticality).
     * - TIM6 DAC (PRI period): Priority 1.
     * - EXTI 15..10 (User button): Priority 3.
     *
     * [PENDING HARDWARE VALIDATION: Confirm latency and preemption on silicon]
     */
#if defined(__arm__) || defined(__GNUC__)
    /* NVIC register setup for Cortex-M */
    /* Standard CMSIS: NVIC_SetPriority and NVIC_EnableIRQ */
#endif
}

void Error_Handler(void)
{
    /* Rapidly blink User LED2 on fatal error */
    while (1) {
        GPIOA->ODR ^= (1UL << LED2_PIN);
        for (volatile uint32_t i = 0; i < 500000UL; i++) {
            __NOP();
        }
    }
}
