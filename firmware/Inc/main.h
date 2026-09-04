/**
 * @file    main.h
 * @brief   Master header for STM32G474 AUV Adaptive Sonar Transmitter Payload.
 * @target  STM32G474RET6 on NUCLEO-G474RE board.
 * @note    All hardware performance claims are marked [PENDING HARDWARE VALIDATION].
 *
 * Locked Architectural Decisions (stm32g4_dac_feasibility_audit.md):
 * 1. SYSCLK = 160.0 MHz (RCC PLL tuned for exact integer division).
 * 2. DAC signal path: DAC3 Channel 2 routed internally to OPAMP3 (pin PB1)
 *    in high-speed follower mode. Internal DAC buffer disabled.
 * 3. DAC_MCR.HFSEL: Configured for high-frequency AHB operations.
 * 4. TIM2: PSC = 0, ARR = 39, TRGO on update -> Exactly 4.000000 MHz (0.000% error).
 * 5. DMA: DMA1 Channel 1 via DMAMUX1, memory-to-peripheral, 16-bit half-words,
 *    atomic ping-boundary double-buffer / profile switching on Transfer-Complete ISR.
 * 6. Waveforms: Consumes precomputed 8000-sample LUTs (outputs/headers).
 * 7. PRI: 2.0 ms active pulse every 20.0 ms PRI (10% duty cycle, 50 Hz ping rate),
 *    CPU sleep (__WFI) during inter-pulse gap.
 */

#ifndef MAIN_H_
#define MAIN_H_

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ========================================================================== */
/* CLOCK TREE & TIMING ARCHITECTURE (Feasibility Audit §C.2)                  */
/* ========================================================================== */
/**
 * SYSCLK is locked at 160.0 MHz (NOT the default 170.0 MHz).
 * Rationale: At 170 MHz, 170 / 4 = 42.5 (non-integer, yielding +/-1.18% error).
 * At 160.0 MHz: 160 / 40 = 4.000000 MHz EXACT (0.000% error).
 */
#define SYSCLK_FREQ_HZ              (160000000UL)
#define HCLK_FREQ_HZ                (SYSCLK_FREQ_HZ)
#define PCLK1_FREQ_HZ               (SYSCLK_FREQ_HZ)
#define PCLK2_FREQ_HZ               (SYSCLK_FREQ_HZ)

/* TIM2 DAC Hardware Trigger Configuration */
#define TIM2_PRESCALER              (0U)
#define TIM2_AUTORELOAD             (39U)   /* Period = ARR + 1 = 40 timer ticks */
#define TIM2_TRIGGER_FREQ_HZ        (SYSCLK_FREQ_HZ / ((TIM2_PRESCALER + 1U) * (TIM2_AUTORELOAD + 1U)))
#define DAC_SAMPLE_PERIOD_NS        (250U)  /* 1 / 4.0 MHz = 250 ns */

/* Compile-time verification of exact 4.000000 MHz DAC trigger rate */
#if defined(__STDC_VERSION__) && (__STDC_VERSION__ >= 201112L)
_Static_assert(TIM2_TRIGGER_FREQ_HZ == 4000000UL, 
    "TIM2 trigger frequency must be EXACTLY 4,000,000 Hz! Check SYSCLK, PSC, and ARR.");
_Static_assert((1000000000ULL / TIM2_TRIGGER_FREQ_HZ) == DAC_SAMPLE_PERIOD_NS,
    "DAC sample interval must be EXACTLY 250 ns!");
#endif

/* ========================================================================== */
/* TRANSMITTER PULSE & PRI TIMING (SIH PS 26058)                              */
/* ========================================================================== */
#define SONAR_SAMPLE_COUNT          (8000U)     /* 4 MSPS * 2.0 ms = 8,000 samples */
#define SONAR_PULSE_DURATION_US     (2000UL)    /* 2.0 ms active pulse duration */
#define SONAR_PRI_PERIOD_US         (20000UL)   /* 20.0 ms Pulse Repetition Interval */
#define SONAR_INTER_PULSE_GAP_US    (SONAR_PRI_PERIOD_US - SONAR_PULSE_DURATION_US) /* 18.0 ms */
#define SONAR_PING_RATE_HZ          (50U)       /* 1 / 20 ms = 50 Hz ping repetition */
#define SONAR_DUTY_CYCLE_PCT        (10U)       /* 2.0 ms / 20.0 ms = 10.0% */

/* ========================================================================== */
/* HARDWARE PINOUT MAPPING (NUCLEO-G474RE Confirmed Conflict-Free)            */
/* ========================================================================== */
/**
 * OPAMP3 Output Pin: PB1
 * - Physical Location: Morpho Connector CN10, Pin 24.
 * - Function: High-speed follower output driving the sonar transmit chain.
 * - Slew rate: 45 V/us, Bandwidth: 13 MHz [PENDING HARDWARE VALIDATION].
 * - Conflict status: Confirmed FREE (no ST-LINK, no LED, no buttons).
 */
#define OPAMP3_OUT_PORT             GPIOB
#define OPAMP3_OUT_PIN              (1U)        /* PB1 */

/**
 * User LED2: PA5 (Green LED on NUCLEO-G474RE)
 * - Toggles on transmit pulse boundary to indicate active ping emission.
 */
#define LED2_PORT                   GPIOA
#define LED2_PIN                    (5U)        /* PA5 */

/**
 * User Button B1: PC13 (Blue Pushbutton on NUCLEO-G474RE)
 * - Press to cycle profiles: LOW_FREQUENCY -> BALANCED -> HIGH_FREQUENCY.
 */
#define BUTTON_B1_PORT              GPIOC
#define BUTTON_B1_PIN               (13U)       /* PC13 */

/* ========================================================================== */
/* EXPORTED FUNCTION DECLARATIONS                                             */
/* ========================================================================== */
void Error_Handler(void);
void SystemClock_Config(void);

#ifdef __cplusplus
}
#endif

#endif /* MAIN_H_ */
