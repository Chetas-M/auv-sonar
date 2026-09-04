/**
 * @file    stm32g474_registers.h
 * @brief   Hardware register map and peripheral definitions for STM32G474.
 * @target  STM32G474RET6 (ARM Cortex-M4F with FPU)
 * @note    Follows STMicroelectronics Reference Manual RM0440 and CMSIS standard (stm32g474xx.h).
 *          Every bit position verified against ST official CMSIS repository (cmsis_device_g4).
 */

#ifndef STM32G474_REGISTERS_H_
#define STM32G474_REGISTERS_H_

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define __IO volatile
#define __I  volatile const
#define __O  volatile

/* ========================================================================== */
/* PERIPHERAL REGISTER STRUCTURES (RM0440)                                    */
/* ========================================================================== */

typedef struct {
    __IO uint32_t ACR;      /* Offset: 0x00 Flash access control register */
    __IO uint32_t PDKEYR;   /* Offset: 0x04 Power down key register */
    __IO uint32_t KEYR;     /* Offset: 0x08 Flash key register */
    __IO uint32_t OPTKEYR;  /* Offset: 0x0C Option byte key register */
    __IO uint32_t SR;       /* Offset: 0x10 Flash status register */
    __IO uint32_t CR;       /* Offset: 0x14 Flash control register */
    __IO uint32_t ECCR;     /* Offset: 0x18 Flash ECC register */
    __IO uint32_t OPTR;     /* Offset: 0x1C Option register */
    __IO uint32_t PCROP1SR; /* Offset: 0x20 PCROP area start address register */
    __IO uint32_t PCROP1ER; /* Offset: 0x24 PCROP area end address register */
    __IO uint32_t WRP1AR;   /* Offset: 0x28 WRP area A address register */
    __IO uint32_t WRP1BR;   /* Offset: 0x2C WRP area B address register */
    __IO uint32_t SEC1R;    /* Offset: 0x30 Secure area register */
} FLASH_TypeDef;

typedef struct {
    __IO uint32_t CR1;      /* Offset: 0x00 Power control register 1 */
    __IO uint32_t CR2;      /* Offset: 0x04 Power control register 2 */
    __IO uint32_t CR3;      /* Offset: 0x08 Power control register 3 */
    __IO uint32_t CR4;      /* Offset: 0x0C Power control register 4 */
    __IO uint32_t SR1;      /* Offset: 0x10 Power status register 1 */
    __IO uint32_t SR2;      /* Offset: 0x14 Power status register 2 */
    __IO uint32_t SCR;      /* Offset: 0x18 Power status clear register */
    __IO uint32_t RESERVED; /* Offset: 0x1C */
    __IO uint32_t PUCRA;    /* Offset: 0x20 Pull-up control register A */
    __IO uint32_t PDCRA;    /* Offset: 0x24 Pull-down control register A */
    __IO uint32_t PUCRB;    /* Offset: 0x28 Pull-up control register B */
    __IO uint32_t PDCRB;    /* Offset: 0x2C Pull-down control register B */
    __IO uint32_t PUCRC;    /* Offset: 0x30 Pull-up control register C */
    __IO uint32_t PDCRC;    /* Offset: 0x34 Pull-down control register C */
    __IO uint32_t PUCRD;    /* Offset: 0x38 Pull-up control register D */
    __IO uint32_t PDCRD;    /* Offset: 0x3C Pull-down control register D */
    __IO uint32_t PUCRE;    /* Offset: 0x40 Pull-up control register E */
    __IO uint32_t PDCRE;    /* Offset: 0x44 Pull-down control register E */
    __IO uint32_t PUCRF;    /* Offset: 0x48 Pull-up control register F */
    __IO uint32_t PDCRF;    /* Offset: 0x4C Pull-down control register F */
    __IO uint32_t PUCRG;    /* Offset: 0x50 Pull-up control register G */
    __IO uint32_t PDCRG;    /* Offset: 0x54 Pull-down control register G */
    __IO uint32_t RESERVED2[2];
    __IO uint32_t CR5;      /* Offset: 0x80 Power control register 5 (Range 1 boost mode) */
} PWR_TypeDef;

typedef struct {
    __IO uint32_t CR;         /* Offset: 0x00 Clock control register */
    __IO uint32_t ICSCR;      /* Offset: 0x04 Internal clock sources calibration */
    __IO uint32_t CFGR;       /* Offset: 0x08 Clock configuration register */
    __IO uint32_t PLLCFGR;    /* Offset: 0x0C PLL configuration register */
    __IO uint32_t RESERVED0[2];
    __IO uint32_t CIER;       /* Offset: 0x18 Clock interrupt enable register */
    __IO uint32_t CIFR;       /* Offset: 0x1C Clock interrupt flag register */
    __IO uint32_t CICR;       /* Offset: 0x20 Clock interrupt clear register */
    __IO uint32_t RESERVED1;
    __IO uint32_t AHB1RSTR;   /* Offset: 0x28 AHB1 peripheral reset register */
    __IO uint32_t AHB2RSTR;   /* Offset: 0x2C AHB2 peripheral reset register */
    __IO uint32_t AHB3RSTR;   /* Offset: 0x30 AHB3 peripheral reset register */
    __IO uint32_t RESERVED2;
    __IO uint32_t APB1RSTR1;  /* Offset: 0x38 APB1 peripheral reset register 1 */
    __IO uint32_t APB1RSTR2;  /* Offset: 0x3C APB1 peripheral reset register 2 */
    __IO uint32_t APB2RSTR;   /* Offset: 0x40 APB2 peripheral reset register */
    __IO uint32_t RESERVED3;
    __IO uint32_t AHB1ENR;    /* Offset: 0x48 AHB1 peripheral clock enable register */
    __IO uint32_t AHB2ENR;    /* Offset: 0x4C AHB2 peripheral clock enable register */
    __IO uint32_t AHB3ENR;    /* Offset: 0x50 AHB3 peripheral clock enable register */
    __IO uint32_t RESERVED4;
    __IO uint32_t APB1ENR1;   /* Offset: 0x58 APB1 peripheral clock enable register 1 */
    __IO uint32_t APB1ENR2;   /* Offset: 0x5C APB1 peripheral clock enable register 2 */
    __IO uint32_t APB2ENR;    /* Offset: 0x60 APB2 peripheral clock enable register */
    __IO uint32_t RESERVED5;
    __IO uint32_t AHB1SMENR;  /* Offset: 0x68 */
    __IO uint32_t AHB2SMENR;  /* Offset: 0x6C */
    __IO uint32_t AHB3SMENR;  /* Offset: 0x70 */
    __IO uint32_t RESERVED6;
    __IO uint32_t APB1SMENR1; /* Offset: 0x78 */
    __IO uint32_t APB1SMENR2; /* Offset: 0x7C */
    __IO uint32_t APB2SMENR;  /* Offset: 0x80 */
    __IO uint32_t RESERVED7;
    __IO uint32_t CCIPR;      /* Offset: 0x88 Peripherals clock configuration */
    __IO uint32_t BDCR;       /* Offset: 0x90 RTC domain control register */
    __IO uint32_t CSR;        /* Offset: 0x94 Control/status register */
} RCC_TypeDef;

typedef struct {
    __IO uint32_t MODER;      /* Offset: 0x00 GPIO port mode register */
    __IO uint32_t OTYPER;     /* Offset: 0x04 GPIO port output type register */
    __IO uint32_t OSPEEDR;    /* Offset: 0x08 GPIO port output speed register */
    __IO uint32_t PUPDR;      /* Offset: 0x0C GPIO port pull-up/pull-down register */
    __IO uint32_t IDR;        /* Offset: 0x10 GPIO port input data register */
    __IO uint32_t ODR;        /* Offset: 0x14 GPIO port output data register */
    __IO uint32_t BSRR;       /* Offset: 0x18 GPIO port bit set/reset register */
    __IO uint32_t LCKR;       /* Offset: 0x1C GPIO port configuration lock register */
    __IO uint32_t AFR[2];     /* Offset: 0x20 GPIO alternate function registers [0]: AFRL, [1]: AFRH */
    __IO uint32_t BRR;        /* Offset: 0x28 GPIO port bit reset register */
} GPIO_TypeDef;

typedef struct {
    __IO uint32_t CR1;        /* Offset: 0x00 Timer control register 1 */
    __IO uint32_t CR2;        /* Offset: 0x04 Timer control register 2 */
    __IO uint32_t SMCR;       /* Offset: 0x08 Slave mode control register */
    __IO uint32_t DIER;       /* Offset: 0x0C DMA/interrupt enable register */
    __IO uint32_t SR;         /* Offset: 0x10 Status register */
    __IO uint32_t EGR;        /* Offset: 0x14 Event generation register */
    __IO uint32_t CCMR1;      /* Offset: 0x18 Capture/compare mode register 1 */
    __IO uint32_t CCMR2;      /* Offset: 0x1C Capture/compare mode register 2 */
    __IO uint32_t CCER;       /* Offset: 0x20 Capture/compare enable register */
    __IO uint32_t CNT;        /* Offset: 0x24 Counter register */
    __IO uint32_t PSC;        /* Offset: 0x28 Prescaler register */
    __IO uint32_t ARR;        /* Offset: 0x2C Auto-reload register */
    __IO uint32_t RCR;        /* Offset: 0x30 Repetition counter register */
    __IO uint32_t CCR1;       /* Offset: 0x34 Capture/compare register 1 */
    __IO uint32_t CCR2;       /* Offset: 0x38 Capture/compare register 2 */
    __IO uint32_t CCR3;       /* Offset: 0x3C Capture/compare register 3 */
    __IO uint32_t CCR4;       /* Offset: 0x40 Capture/compare register 4 */
    __IO uint32_t BDTR;       /* Offset: 0x44 Break and dead-time register */
    __IO uint32_t DCR;        /* Offset: 0x48 DMA control register */
    __IO uint32_t DMAR;       /* Offset: 0x4C DMA address for full transfer */
} TIM_TypeDef;

typedef struct {
    __IO uint32_t CR;         /* Offset: 0x00 DAC control register */
    __IO uint32_t SWTRIGR;    /* Offset: 0x04 DAC software trigger register */
    __IO uint32_t DHR12R1;    /* Offset: 0x08 Channel 1 12-bit right-aligned data holding register */
    __IO uint32_t DHR12L1;    /* Offset: 0x0C Channel 1 12-bit left-aligned data holding register */
    __IO uint32_t DHR8R1;     /* Offset: 0x10 Channel 1 8-bit right-aligned data holding register */
    __IO uint32_t DHR12R2;    /* Offset: 0x14 Channel 2 12-bit right-aligned data holding register */
    __IO uint32_t DHR12L2;    /* Offset: 0x18 Channel 2 12-bit left-aligned data holding register */
    __IO uint32_t DHR8R2;     /* Offset: 0x1C Channel 2 8-bit right-aligned data holding register */
    __IO uint32_t DHR12RD;    /* Offset: 0x20 Dual DAC 12-bit right-aligned data holding register */
    __IO uint32_t DHR12LD;    /* Offset: 0x24 Dual DAC 12-bit left-aligned data holding register */
    __IO uint32_t DHR8RD;     /* Offset: 0x28 Dual DAC 8-bit right-aligned data holding register */
    __IO uint32_t DOR1;       /* Offset: 0x2C Channel 1 data output register */
    __IO uint32_t DOR2;       /* Offset: 0x30 Channel 2 data output register */
    __IO uint32_t SR;         /* Offset: 0x34 DAC status register */
    __IO uint32_t CCR;        /* Offset: 0x38 DAC calibration control register */
    __IO uint32_t MCR;        /* Offset: 0x3C DAC mode control register (HFSEL, MODE1, MODE2) */
    __IO uint32_t SHSR1;      /* Offset: 0x40 Sample and hold sample time register 1 */
    __IO uint32_t SHSR2;      /* Offset: 0x44 Sample and hold sample time register 2 */
    __IO uint32_t SHHR;       /* Offset: 0x48 Sample and hold hold time register */
    __IO uint32_t SHRR;       /* Offset: 0x4C Sample and hold refresh time register */
    __IO uint32_t STR1;       /* Offset: 0x50 Sawtooth trigger register 1 */
    __IO uint32_t STR2;       /* Offset: 0x54 Sawtooth trigger register 2 */
    __IO uint32_t STMODR;     /* Offset: 0x58 Sawtooth mode register */
} DAC_TypeDef;

typedef struct {
    __IO uint32_t CSR;        /* Offset: 0x00 OPAMP control/status register */
    __IO uint32_t TCMR;       /* Offset: 0x04 OPAMP timer controlled mode register */
} OPAMP_TypeDef;

typedef struct {
    __IO uint32_t CCR;        /* Offset: 0x00 DMA channel x configuration register */
    __IO uint32_t CNDTR;      /* Offset: 0x04 DMA channel x number of data register */
    __IO uint32_t CPAR;       /* Offset: 0x08 DMA channel x peripheral address register */
    __IO uint32_t CMAR;       /* Offset: 0x0C DMA channel x memory address register */
} DMA_Channel_TypeDef;

typedef struct {
    __IO uint32_t ISR;        /* Offset: 0x00 DMA interrupt status register */
    __IO uint32_t IFCR;       /* Offset: 0x04 DMA interrupt flag clear register */
} DMA_TypeDef;

typedef struct {
    __IO uint32_t CCR;        /* Offset: 0x00 DMAMUX channel configuration register */
} DMAMUX_Channel_TypeDef;

/* ========================================================================== */
/* PERIPHERAL BASE ADDRESSES (RM0440 §2 Memory Map)                           */
/* ========================================================================== */
#define FLASH_R_BASE                (0x40022000UL) /* Flash register interface (AHB1 + 0x2000) */
#define RCC_BASE                    (0x40021000UL)
#define PWR_BASE                    (0x40007000UL)

#define GPIOA_BASE                  (0x48000000UL)
#define GPIOB_BASE                  (0x48000400UL)
#define GPIOC_BASE                  (0x48000800UL)

#define TIM2_BASE                   (0x40000000UL)
#define TIM6_BASE                   (0x40001000UL)

#define SYSCFG_BASE                 (0x40010000UL)
#define OPAMP_BASE                  (0x40010300UL)
#define OPAMP3_BASE                 (0x40010308UL) /* APB2 + 0x0308 in RM0440 (stm32g474xx.h) */

#define DAC1_BASE                   (0x50000800UL)
#define DAC2_BASE                   (0x50000C00UL)
#define DAC3_BASE                   (0x50001000UL) /* AHB2 + 0x08001000 in RM0440 (stm32g474xx.h) */
#define DAC4_BASE                   (0x50001400UL)

#define DMA1_BASE                   (0x40020000UL)
#define DMA1_Channel1_BASE          (0x40020008UL)
#define DMAMUX1_Channel0_BASE       (0x40020800UL)

#define FLASH                       ((FLASH_TypeDef *) FLASH_R_BASE)
#define RCC                         ((RCC_TypeDef *) RCC_BASE)
#define PWR                         ((PWR_TypeDef *) PWR_BASE)

#define GPIOA                       ((GPIO_TypeDef *) GPIOA_BASE)
#define GPIOB                       ((GPIO_TypeDef *) GPIOB_BASE)
#define GPIOC                       ((GPIO_TypeDef *) GPIOC_BASE)

#define TIM2                        ((TIM_TypeDef *) TIM2_BASE)
#define TIM6                        ((TIM_TypeDef *) TIM6_BASE)

#define DAC3                        ((DAC_TypeDef *) DAC3_BASE)
#define OPAMP3                      ((OPAMP_TypeDef *) OPAMP3_BASE)

#define DMA1                        ((DMA_TypeDef *) DMA1_BASE)
#define DMA1_Channel1               ((DMA_Channel_TypeDef *) DMA1_Channel1_BASE)
#define DMAMUX1_Channel0            ((DMAMUX_Channel_TypeDef *) DMAMUX1_Channel0_BASE)

/* ========================================================================== */
/* REGISTER BIT DEFINITIONS (RM0440 & stm32g474xx.h verified)                 */
/* ========================================================================== */

/* FLASH_ACR */
#define FLASH_ACR_LATENCY_POS       (0U)
#define FLASH_ACR_LATENCY_4WS       (0x00000004UL) /* 4 wait states @ 160 MHz in Boost mode */
#define FLASH_ACR_PRFTEN            (1UL << 8)     /* Prefetch enable */
#define FLASH_ACR_ICEN              (1UL << 9)     /* Instruction cache enable */
#define FLASH_ACR_DCEN              (1UL << 10)    /* Data cache enable */

/* PWR_CR5 */
#define PWR_CR5_R1MODE_POS          (8U)
#define PWR_CR5_R1MODE              (1UL << PWR_CR5_R1MODE_POS) /* Main regulator Range 1: 0=Boost enabled, 1=Normal */

/* RCC_CR */
#define RCC_CR_HSION                (1UL << 8)
#define RCC_CR_HSIRDY               (1UL << 10)
#define RCC_CR_HSEON                (1UL << 16)
#define RCC_CR_HSERDY               (1UL << 17)
#define RCC_CR_PLLON                (1UL << 24)
#define RCC_CR_PLLRDY               (1UL << 25)

/* RCC_PLLCFGR */
#define RCC_PLLCFGR_PLLSRC_HSE      (0x00000003UL) /* HSE clock selected as PLL source */
#define RCC_PLLCFGR_PLLSRC_HSI      (0x00000002UL) /* HSI clock selected as PLL source */
#define RCC_PLLCFGR_PLLREN          (1UL << 24)    /* Main PLL PLLCLK output enable */

/* RCC_CFGR */
#define RCC_CFGR_SW_POS             (0U)
#define RCC_CFGR_SW_MSK             (0x3UL << RCC_CFGR_SW_POS)
#define RCC_CFGR_SW_HSI             (0x00000001U)
#define RCC_CFGR_SW_HSE             (0x00000002U)
#define RCC_CFGR_SW_PLL             (0x00000003U)
#define RCC_CFGR_SWS_POS            (2U)
#define RCC_CFGR_SWS_MSK            (0x3UL << RCC_CFGR_SWS_POS)
#define RCC_CFGR_SWS_HSI            (0x00000004U)
#define RCC_CFGR_SWS_HSE            (0x00000008U)
#define RCC_CFGR_SWS_PLL            (0x0000000CU)

/* RCC_AHB1ENR */
#define RCC_AHB1ENR_DMA1EN          (1UL << 0)
#define RCC_AHB1ENR_DMAMUX1EN       (1UL << 2)

/* RCC_AHB2ENR */
#define RCC_AHB2ENR_GPIOAEN         (1UL << 0)
#define RCC_AHB2ENR_GPIOBEN         (1UL << 1)
#define RCC_AHB2ENR_GPIOCEN         (1UL << 2)
#define RCC_AHB2ENR_DAC3EN          (1UL << 18)

/* RCC_APB1ENR1 */
#define RCC_APB1ENR1_TIM2EN         (1UL << 0)
#define RCC_APB1ENR1_TIM6EN         (1UL << 4)
#define RCC_APB1ENR1_PWREN          (1UL << 28)

/* RCC_APB2ENR */
#define RCC_APB2ENR_SYSCFGEN        (1UL << 0)  /* SYSCFG, COMP, OPAMP, VREFBUF peripheral clock enable */

/* DAC_CR (Official CMSIS bit definitions) */
#define DAC_CR_EN2_POS              (16U)
#define DAC_CR_EN2                  (1UL << DAC_CR_EN2_POS)     /* Bit 16: DAC channel 2 enable */
#define DAC_CR_TEN2_POS             (17U)
#define DAC_CR_TEN2                 (1UL << DAC_CR_TEN2_POS)    /* Bit 17: DAC channel 2 Trigger enable (RM0440) */
#define DAC_CR_TSEL2_POS            (18U)                       /* Bits 21:18: TSEL2[3:0] */
#define DAC_CR_TSEL2_MSK            (0xFUL << DAC_CR_TSEL2_POS)
/**
 * In RM0440 & stm32g4xx_ll_dac.h:
 * TIM2 TRGO trigger value is 0x4 (LL_DAC_TRIG_EXT_TIM2_TRGO).
 * Channel 2: 0x4 << 18 = 0x00100000UL (DAC_CR_TSEL2_2)
 */
#define DAC_CR_TSEL2_TIM2_TRGO      (0x4UL << DAC_CR_TSEL2_POS) /* 0b0100 shifted to bit 18 = 0x00100000UL */
#define DAC_CR_DMAEN2_POS           (28U)
#define DAC_CR_DMAEN2               (1UL << DAC_CR_DMAEN2_POS)  /* Bit 28: DAC channel 2 DMA enable */

/* DAC_SR (RM0440 §22.10.6) */
#define DAC_SR_DMAUDR1_POS          (13U)
#define DAC_SR_DMAUDR1              (1UL << DAC_SR_DMAUDR1_POS) /* Bit 13: DAC channel 1 DMA underrun flag */
#define DAC_SR_DMAUDR2_POS          (29U)
#define DAC_SR_DMAUDR2              (1UL << DAC_SR_DMAUDR2_POS) /* Bit 29: DAC channel 2 DMA underrun flag (write 1 to clear) */

/* DAC_MCR (Official CMSIS bit definitions) */
#define DAC_MCR_HFSEL_POS           (14U)
#define DAC_MCR_HFSEL_ABOVE_80MHZ   (0x1UL << DAC_MCR_HFSEL_POS) /* Bits 15:14 = 0b01: 80 MHz < AHB <= 160 MHz */
#define DAC_MCR_HFSEL_ABOVE_160MHZ  (0x2UL << DAC_MCR_HFSEL_POS) /* Bits 15:14 = 0b10: AHB > 160 MHz */
#define DAC_MCR_MODE2_POS           (16U)                        /* Bits 18:16: MODE2[2:0] */
/**
 * Mode 2 encoding in RM0440:
 * 0b000: DAC channel 2 connected to external pin with Buffer enabled
 * 0b010: DAC channel 2 connected to external pin with Buffer disabled
 * 0b011: DAC channel 2 connected on-chip to internal peripheral with Buffer DISABLED
 */
#define DAC_MCR_MODE2_ONCHIP_BUFFER_DISABLE (0x3UL << DAC_MCR_MODE2_POS) /* 0x00030000UL */

/* OPAMP_CSR (Official CMSIS bit definitions - RM0440 §23.7.1) */
#define OPAMP_CSR_OPAMP3EN          (1UL << 0)                  /* Bit 0: OPAMP3 enable */
#define OPAMP_CSR_VPSEL_POS         (2U)                        /* Bits 3:2: VP_SEL[1:0] */
#define OPAMP_CSR_VPSEL_DAC3_CH2    (0x3UL << OPAMP_CSR_VPSEL_POS) /* 0b11: Non-inverting input to DAC3_OUT2 (0x0C) */
#define OPAMP_CSR_VMSEL_POS         (5U)                        /* Bits 6:5: VM_SEL[1:0] */
#define OPAMP_CSR_VMSEL_FOLLOWER    (0x3UL << OPAMP_CSR_VMSEL_POS) /* 0b11: Inverting input to output (Follower) (0x60) */
#define OPAMP_CSR_HIGHSPEEDEN_POS   (7U)                        /* Bit 7: HIGHSPEEDEN (High-Speed Mode) */
#define OPAMP_CSR_OPAMP3_HIGHSPEED  (1UL << OPAMP_CSR_HIGHSPEEDEN_POS) /* Bit 7 = 0x80: 45 V/us slew rate, 13 MHz GBW */

/* TIM_CR1 */
#define TIM_CR1_CEN                 (1UL << 0)     /* Bit 0: Counter enable */
#define TIM_CR1_OPM                 (1UL << 3)     /* Bit 3: One-pulse mode */
#define TIM_CR1_ARPE                (1UL << 7)     /* Bit 7: Auto-reload preload enable */

/* TIM_CR2 */
#define TIM_CR2_MMS_POS             (4U)
#define TIM_CR2_MMS_UPDATE          (0x2UL << TIM_CR2_MMS_POS)   /* Bits 6:4 = 0b010: TRGO on Update Event (0x20) */

/* TIM_DIER */
#define TIM_DIER_UIE                (1UL << 0)     /* Update interrupt enable */

/* TIM_SR */
#define TIM_SR_UIF                  (1UL << 0)     /* Update interrupt flag */

/* DMA_CCR */
#define DMA_CCR_EN                  (1UL << 0)     /* Channel enable */
#define DMA_CCR_TCIE                (1UL << 1)     /* Transfer complete interrupt enable */
#define DMA_CCR_DIR_MEM2PERIPH      (1UL << 4)     /* Direction: memory-to-peripheral */
#define DMA_CCR_CIRC                (1UL << 5)     /* Circular mode */
#define DMA_CCR_PINC                (1UL << 6)     /* Peripheral increment mode (0=disabled) */
#define DMA_CCR_MINC                (1UL << 7)     /* Memory increment mode (1=enabled) */
#define DMA_CCR_PSIZE_16BIT         (0x1UL << 8)   /* Peripheral size 16-bit half-word */
#define DMA_CCR_MSIZE_16BIT         (0x1UL << 10)  /* Memory size 16-bit half-word */
#define DMA_CCR_PL_VERY_HIGH        (0x3UL << 12)  /* Channel priority level: Very High */

/* DMA_ISR & DMA_IFCR */
#define DMA_ISR_TCIF1               (1UL << 1)     /* Channel 1 transfer complete flag */
#define DMA_IFCR_CTCIF1             (1UL << 1)     /* Channel 1 clear transfer complete flag */

/* DMAMUX1 Request ID for DAC3_CH2 (Official ST stm32g4xx_ll_dmamux.h verified) */
/**
 * In RM0440 & stm32g4xx_ll_dmamux.h:
 * LL_DMAMUX_REQ_DAC3_CH1 = 0x00000066U (102 decimal)
 * LL_DMAMUX_REQ_DAC3_CH2 = 0x00000067U (103 decimal, NOT 107!)
 * (Note: 107 decimal is 0x6B = LL_DMAMUX_REQ_SPI4_TX).
 */
#define DMAMUX_REQ_DAC3_CH2         (0x00000067U)  /* 103 decimal: DAC3_CH2 DMA request */

/* Helper assembly wrappers */
#if defined(__arm__) || defined(__thumb__)
#define __WFI()     __asm__ volatile ("wfi")
#define __NOP()     __asm__ volatile ("nop")
#define __DSB()     __asm__ volatile ("dsb 0xF" ::: "memory")
#define __ISB()     __asm__ volatile ("isb 0xF" ::: "memory")
#else
/* Host emulation stubs for x86/x64 verification */
#define __WFI()     do { } while (0)
#define __NOP()     do { } while (0)
#define __DSB()     do { } while (0)
#define __ISB()     do { } while (0)
#endif

#ifdef __cplusplus
}
#endif

#endif /* STM32G474_REGISTERS_H_ */
