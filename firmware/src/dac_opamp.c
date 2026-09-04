/**
 * @file    dac_opamp.c
 * @brief   DAC3 Channel 2 and OPAMP3 high-speed driver implementation for STM32G474.
 * @target  STM32G474RET6 on NUCLEO-G474RE board.
 * @note    All hardware performance claims are marked [PENDING HARDWARE VALIDATION].
 *
 * Audit References:
 * - See stm32g4_dac_feasibility_audit.md §C.1 (Internal DAC buffer disabled; 15 MSPS internal core).
 * - See stm32g4_dac_feasibility_audit.md §C.3 (HFSEL high-frequency bus interface timing).
 */

#include "dac_opamp.h"
#include "main.h"
#include "stm32g474_registers.h"

void DAC3_OPAMP3_Init(void)
{
    /* ---------------------------------------------------------------------- */
    /* 1. PERIPHERAL CLOCK ENABLES                                            */
    /* ---------------------------------------------------------------------- */
    /* Enable GPIOB clock (AHB2) */
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOBEN;

    /* Enable DAC3 clock (AHB2) */
    RCC->AHB2ENR |= RCC_AHB2ENR_DAC3EN;

    /* Enable Power interface clock (APB1) */
    RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN;

    /* Enable SYSCFG / OPAMP interface clock on APB2 (RM0440 §23.3 & §9.4.17) */
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;
    __DSB();

    /* ---------------------------------------------------------------------- */
    /* 2. GPIO PB1 (OPAMP3 OUTPUT) CONFIGURATION                              */
    /* ---------------------------------------------------------------------- */
    /**
     * PB1 is the dedicated analog output pin for OPAMP3 (RM0440 Table 14).
     * Broken out on NUCLEO-G474RE Morpho connector CN10 Pin 24.
     * Must be configured in pure ANALOG mode with no pull-up / pull-down.
     */
    /* Clear MODER bits 3:2 and set to 0b11 (Analog mode) */
    GPIOB->MODER |= (0x3UL << (OPAMP3_OUT_PIN * 2));
    /* Clear PUPDR bits 3:2 (No pull-up, no pull-down) */
    GPIOB->PUPDR &= ~(0x3UL << (OPAMP3_OUT_PIN * 2));

    /* ---------------------------------------------------------------------- */
    /* 3. OPAMP3 CONFIGURATION (High-Speed Follower Mode)                     */
    /* ---------------------------------------------------------------------- */
    /**
     * Audit Reference: Feasibility Audit §C.1
     * The internal DAC output buffer cannot settle within 250 ns. We bypass it
     * completely and route DAC3_OUT2 directly into OPAMP3.
     *
     * Register OPAMP3_CSR (RM0440 §23.7.1 & stm32g474xx.h verified):
     * - HIGHSPEEDEN: High-speed mode (Bit 7 = 1) -> Enables 45 V/us slew rate,
     *   13 MHz Gain-Bandwidth Product, full-scale slew in ~73 ns.
     *   (Verified: Bit 1 is FORCEVP; Bit 7 is HIGHSPEEDEN).
     * - VM_SEL: Inverting input connected to output (Bits 6:5 = 0b11) -> Follower.
     * - VP_SEL: Non-inverting input connected internally to DAC3_OUT2 (Bits 3:2 = 0b11).
     * - OPAMP3EN: Enable OPAMP3 (Bit 0 = 1).
     * [PENDING HARDWARE VALIDATION: verify rise time on scope]
     */
    OPAMP3->CSR = OPAMP_CSR_OPAMP3_HIGHSPEED |
                  OPAMP_CSR_VMSEL_FOLLOWER   |
                  OPAMP_CSR_VPSEL_DAC3_CH2   |
                  OPAMP_CSR_OPAMP3EN;

    /* ---------------------------------------------------------------------- */
    /* 4. DAC3 MODE CONTROL (DAC3_MCR: HFSEL & Internal Routing)              */
    /* ---------------------------------------------------------------------- */
    /**
     * Audit Reference: Feasibility Audit §C.3
     * HFSEL[1:0] (Bits 15:14) in DAC3_MCR:
     * - At AHB = 160.0 MHz, HFSEL is set to 0b01 (80 MHz < AHB <= 160 MHz)
     *   via DAC_MCR_HFSEL_ABOVE_80MHZ (Bit 14 = 1).
     *
     * MODE2[2:0] (Bits 18:16) in DAC3_MCR:
     * - Set to 0b011 (0x3 << 16): DAC Channel 2 connected internally to on-chip peripheral
     *   (OPAMP3) with the internal buffer DISABLED.
     *   (Buffer disabled here because internal buffer caps at 1 MSPS, see feasibility audit §C.1).
     */
    DAC3->MCR = DAC_MCR_HFSEL_ABOVE_80MHZ |
                DAC_MCR_MODE2_ONCHIP_BUFFER_DISABLE;

    /* ---------------------------------------------------------------------- */
    /* 5. DAC3 CHANNEL 2 CONTROL (DAC3_CR: Trigger & DMA Configuration)       */
    /* ---------------------------------------------------------------------- */
    /**
     * Register DAC3_CR (RM0440 §22.10.1 & stm32g4xx_ll_dac.h verified):
     * - EN2 (Bit 16 = 1): Enable DAC3 Channel 2 core.
     * - TEN2 (Bit 17 = 1): Hardware trigger enabled (RM0440: Bit 17 is TEN2, NOT 18!).
     * - TSEL2[3:0] (Bits 21:18) = 0b0100: Hardware trigger mapped to TIM2 TRGO.
     *   (Verified: TIM2 TRGO trigger code is 0x4; 0x4 << 18 = 0x00100000 = DAC_CR_TSEL2_2).
     * - DMAEN2 (Bit 28 = 1): DMA request generated on each TIM2 TRGO update event.
     */
    DAC3->CR = DAC_CR_TSEL2_TIM2_TRGO |
               DAC_CR_TEN2            |
               DAC_CR_DMAEN2          |
               DAC_CR_EN2;

    /* Clear any spurious DMA underrun flag before arming (RM0440 §22.4.15) */
    DAC3->SR = DAC_SR_DMAUDR2;

    /* Set default midscale (code 2048 = 0x0800, ~1.65 V) to prevent turn-on click */
    DAC3->DHR12R2 = 2048U;

    /* Small stabilization delay for OPAMP and DAC bandgap (~10 us) */
    for (volatile uint32_t i = 0; i < 2000UL; i++) {
        __NOP();
    }
}

void DAC3_ClearDMAUnderrunFlag(void)
{
    /* Clear DAC3 Channel 2 DMA underrun flag by writing 1 (RM0440 §22.10.6) */
    DAC3->SR = DAC_SR_DMAUDR2;
}

void DAC3_EnableHardwareTrigger(void)
{
    DAC3->CR |= DAC_CR_TEN2;
}

void DAC3_DisableHardwareTrigger(void)
{
    DAC3->CR &= ~DAC_CR_TEN2;
}

void DAC3_SetStaticCode(uint16_t code)
{
    /* Clamp to 12-bit unsigned range (0 to 4095) */
    if (code > 4095U) {
        code = 4095U;
    }
    DAC3->DHR12R2 = (uint32_t)code;
}

uint32_t DAC3_GetDHR12R2_Address(void)
{
    return (uint32_t)(uintptr_t)&(DAC3->DHR12R2);
}
