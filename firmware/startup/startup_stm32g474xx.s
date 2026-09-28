.syntax unified
.cpu cortex-m4
.fpu fpv4-sp-d16
.thumb

/* Symbols supplied by the linker script */
.global _estack
.global _sidata
.global _sdata
.global _edata
.global _sbss
.global _ebss

/* Reset and exception handlers */
.global Reset_Handler
.global NMI_Handler
.global HardFault_Handler
.global MemManage_Handler
.global BusFault_Handler
.global UsageFault_Handler
.global SVC_Handler
.global DebugMon_Handler
.global PendSV_Handler
.global SysTick_Handler

/* Peripheral interrupt handlers */
.global DMA1_Channel1_IRQHandler
.global TIM6_DAC_IRQHandler
.global EXTI15_10_IRQHandler

/* Main application */
.extern main

.section .isr_vector,"a",%progbits
.type g_pfnVectors, %object

g_pfnVectors:
    .word _estack
    .word Reset_Handler
    .word NMI_Handler
    .word HardFault_Handler
    .word MemManage_Handler
    .word BusFault_Handler
    .word UsageFault_Handler
    .word 0
    .word 0
    .word 0
    .word 0
    .word SVC_Handler
    .word DebugMon_Handler
    .word 0
    .word PendSV_Handler
    .word SysTick_Handler

    /* STM32G4 external interrupt vectors.
       Unused vectors point to Default_Handler. */

    .word WWDG_IRQHandler
    .word PVD_PVM_IRQHandler
    .word RTC_TAMP_LSECSS_IRQHandler
    .word RTC_WKUP_IRQHandler
    .word FLASH_IRQHandler
    .word RCC_IRQHandler
    .word EXTI0_IRQHandler
    .word EXTI1_IRQHandler
    .word EXTI2_IRQHandler
    .word EXTI3_IRQHandler
    .word EXTI4_IRQHandler
    .word DMA1_Channel1_IRQHandler
    .word DMA1_Channel2_IRQHandler
    .word DMA1_Channel3_IRQHandler
    .word DMA1_Channel4_IRQHandler
    .word DMA1_Channel5_IRQHandler
    .word DMA1_Channel6_IRQHandler
    .word DMA1_Channel7_IRQHandler
    .word ADC1_2_IRQHandler
    .word USB_HP_IRQHandler
    .word USB_LP_IRQHandler
    .word FDCAN1_IT0_IRQHandler
    .word FDCAN1_IT1_IRQHandler
    .word EXTI9_5_IRQHandler
    .word TIM1_BRK_TIM15_IRQHandler
    .word TIM1_UP_TIM16_IRQHandler
    .word TIM1_TRG_COM_TIM17_IRQHandler
    .word TIM1_CC_IRQHandler
    .word TIM2_IRQHandler
    .word TIM3_IRQHandler
    .word TIM4_IRQHandler
    .word I2C1_EV_IRQHandler
    .word I2C1_ER_IRQHandler
    .word I2C2_EV_IRQHandler
    .word I2C2_ER_IRQHandler
    .word SPI1_IRQHandler
    .word SPI2_IRQHandler
    .word USART1_IRQHandler
    .word USART2_IRQHandler
    .word USART3_IRQHandler
    .word EXTI15_10_IRQHandler
    .word RTC_Alarm_IRQHandler
    .word USBWakeUp_IRQHandler
    .word TIM8_BRK_IRQHandler
    .word TIM8_UP_IRQHandler
    .word TIM8_TRG_COM_IRQHandler
    .word TIM8_CC_IRQHandler
    .word ADC3_IRQHandler
    .word FMC_IRQHandler
    .word LPTIM1_IRQHandler
    .word TIM5_IRQHandler
    .word SPI3_IRQHandler
    .word UART4_IRQHandler
    .word UART5_IRQHandler
    .word TIM6_DAC_IRQHandler
    .word TIM7_IRQHandler
    .word DMA2_Channel1_IRQHandler
    .word DMA2_Channel2_IRQHandler
    .word DMA2_Channel3_IRQHandler
    .word DMA2_Channel4_IRQHandler
    .word DMA2_Channel5_IRQHandler
    .word UCPD1_IRQHandler
    .word COMP1_2_3_IRQHandler
    .word COMP4_5_6_IRQHandler
    .word CRS_IRQHandler
    .word SAI1_IRQHandler
    .word FPU_IRQHandler

.size g_pfnVectors, .-g_pfnVectors


.section .text.Reset_Handler
.type Reset_Handler, %function

Reset_Handler:

    /* Copy initialized data from FLASH to RAM */
    ldr r0, =_sidata
    ldr r1, =_sdata
    ldr r2, =_edata

1:
    cmp r1, r2
    bcc 2f
    b 3f

2:
    ldr r3, [r0], #4
    str r3, [r1], #4
    b 1b

    /* Zero-initialize .bss */
3:
    ldr r1, =_sbss
    ldr r2, =_ebss
    movs r3, #0

4:
    cmp r1, r2
    bcc 5f
    b 6f

5:
    str r3, [r1], #4
    b 4b

6:
    /* Enter C application */
    bl main

7:
    /* main() should never return */
    b 7b

.size Reset_Handler, .-Reset_Handler


/* Default interrupt handler */

.section .text.Default_Handler
.type Default_Handler, %function

Default_Handler:
    b Default_Handler

.size Default_Handler, .-Default_Handler


/* Weak aliases for unused interrupts */

.weak WWDG_IRQHandler
.set WWDG_IRQHandler, Default_Handler

.weak PVD_PVM_IRQHandler
.set PVD_PVM_IRQHandler, Default_Handler

.weak RTC_TAMP_LSECSS_IRQHandler
.set RTC_TAMP_LSECSS_IRQHandler, Default_Handler

.weak RTC_WKUP_IRQHandler
.set RTC_WKUP_IRQHandler, Default_Handler

.weak FLASH_IRQHandler
.set FLASH_IRQHandler, Default_Handler

.weak RCC_IRQHandler
.set RCC_IRQHandler, Default_Handler

.weak EXTI0_IRQHandler
.set EXTI0_IRQHandler, Default_Handler

.weak EXTI1_IRQHandler
.set EXTI1_IRQHandler, Default_Handler

.weak EXTI2_IRQHandler
.set EXTI2_IRQHandler, Default_Handler

.weak EXTI3_IRQHandler
.set EXTI3_IRQHandler, Default_Handler

.weak EXTI4_IRQHandler
.set EXTI4_IRQHandler, Default_Handler

.weak DMA1_Channel2_IRQHandler
.set DMA1_Channel2_IRQHandler, Default_Handler

.weak DMA1_Channel3_IRQHandler
.set DMA1_Channel3_IRQHandler, Default_Handler

.weak DMA1_Channel4_IRQHandler
.set DMA1_Channel4_IRQHandler, Default_Handler

.weak DMA1_Channel5_IRQHandler
.set DMA1_Channel5_IRQHandler, Default_Handler

.weak DMA1_Channel6_IRQHandler
.set DMA1_Channel6_IRQHandler, Default_Handler

.weak DMA1_Channel7_IRQHandler
.set DMA1_Channel7_IRQHandler, Default_Handler

.weak ADC1_2_IRQHandler
.set ADC1_2_IRQHandler, Default_Handler

.weak USB_HP_IRQHandler
.set USB_HP_IRQHandler, Default_Handler

.weak USB_LP_IRQHandler
.set USB_LP_IRQHandler, Default_Handler

.weak FDCAN1_IT0_IRQHandler
.set FDCAN1_IT0_IRQHandler, Default_Handler

.weak FDCAN1_IT1_IRQHandler
.set FDCAN1_IT1_IRQHandler, Default_Handler

.weak EXTI9_5_IRQHandler
.set EXTI9_5_IRQHandler, Default_Handler

.weak TIM1_BRK_TIM15_IRQHandler
.set TIM1_BRK_TIM15_IRQHandler, Default_Handler

.weak TIM1_UP_TIM16_IRQHandler
.set TIM1_UP_TIM16_IRQHandler, Default_Handler

.weak TIM1_TRG_COM_TIM17_IRQHandler
.set TIM1_TRG_COM_TIM17_IRQHandler, Default_Handler

.weak TIM1_CC_IRQHandler
.set TIM1_CC_IRQHandler, Default_Handler

.weak TIM2_IRQHandler
.set TIM2_IRQHandler, Default_Handler

.weak TIM3_IRQHandler
.set TIM3_IRQHandler, Default_Handler

.weak TIM4_IRQHandler
.set TIM4_IRQHandler, Default_Handler

.weak I2C1_EV_IRQHandler
.set I2C1_EV_IRQHandler, Default_Handler

.weak I2C1_ER_IRQHandler
.set I2C1_ER_IRQHandler, Default_Handler

.weak I2C2_EV_IRQHandler
.set I2C2_EV_IRQHandler, Default_Handler

.weak I2C2_ER_IRQHandler
.set I2C2_ER_IRQHandler, Default_Handler

.weak SPI1_IRQHandler
.set SPI1_IRQHandler, Default_Handler

.weak SPI2_IRQHandler
.set SPI2_IRQHandler, Default_Handler

.weak USART1_IRQHandler
.set USART1_IRQHandler, Default_Handler

.weak USART2_IRQHandler
.set USART2_IRQHandler, Default_Handler

.weak USART3_IRQHandler
.set USART3_IRQHandler, Default_Handler

.weak RTC_Alarm_IRQHandler
.set RTC_Alarm_IRQHandler, Default_Handler

.weak USBWakeUp_IRQHandler
.set USBWakeUp_IRQHandler, Default_Handler

.weak TIM8_BRK_IRQHandler
.set TIM8_BRK_IRQHandler, Default_Handler

.weak TIM8_UP_IRQHandler
.set TIM8_UP_IRQHandler, Default_Handler

.weak TIM8_TRG_COM_IRQHandler
.set TIM8_TRG_COM_IRQHandler, Default_Handler

.weak TIM8_CC_IRQHandler
.set TIM8_CC_IRQHandler, Default_Handler

.weak ADC3_IRQHandler
.set ADC3_IRQHandler, Default_Handler

.weak FMC_IRQHandler
.set FMC_IRQHandler, Default_Handler

.weak LPTIM1_IRQHandler
.set LPTIM1_IRQHandler, Default_Handler

.weak TIM5_IRQHandler
.set TIM5_IRQHandler, Default_Handler

.weak SPI3_IRQHandler
.set SPI3_IRQHandler, Default_Handler

.weak UART4_IRQHandler
.set UART4_IRQHandler, Default_Handler

.weak UART5_IRQHandler
.set UART5_IRQHandler, Default_Handler

.weak TIM7_IRQHandler
.set TIM7_IRQHandler, Default_Handler

.weak DMA2_Channel1_IRQHandler
.set DMA2_Channel1_IRQHandler, Default_Handler

.weak DMA2_Channel2_IRQHandler
.set DMA2_Channel2_IRQHandler, Default_Handler

.weak DMA2_Channel3_IRQHandler
.set DMA2_Channel3_IRQHandler, Default_Handler

.weak DMA2_Channel4_IRQHandler
.set DMA2_Channel4_IRQHandler, Default_Handler

.weak DMA2_Channel5_IRQHandler
.set DMA2_Channel5_IRQHandler, Default_Handler

.weak UCPD1_IRQHandler
.set UCPD1_IRQHandler, Default_Handler

.weak COMP1_2_3_IRQHandler
.set COMP1_2_3_IRQHandler, Default_Handler

.weak COMP4_5_6_IRQHandler
.set COMP4_5_6_IRQHandler, Default_Handler

.weak CRS_IRQHandler
.set CRS_IRQHandler, Default_Handler

.weak SAI1_IRQHandler
.set SAI1_IRQHandler, Default_Handler

.weak FPU_IRQHandler
.set FPU_IRQHandler, Default_Handler


/* Exception handlers supplied by stm32g4xx_it.c */

.weak NMI_Handler
.set NMI_Handler, Default_Handler

.weak HardFault_Handler
.set HardFault_Handler, Default_Handler

.weak MemManage_Handler
.set MemManage_Handler, Default_Handler

.weak BusFault_Handler
.set BusFault_Handler, Default_Handler

.weak UsageFault_Handler
.set UsageFault_Handler, Default_Handler

.weak SVC_Handler
.set SVC_Handler, Default_Handler

.weak DebugMon_Handler
.set DebugMon_Handler, Default_Handler

.weak PendSV_Handler
.set PendSV_Handler, Default_Handler

.weak SysTick_Handler
.set SysTick_Handler, Default_Handler

.weak DMA1_Channel1_IRQHandler
.set DMA1_Channel1_IRQHandler, Default_Handler

.weak TIM6_DAC_IRQHandler
.set TIM6_DAC_IRQHandler, Default_Handler

.weak EXTI15_10_IRQHandler
.set EXTI15_10_IRQHandler, Default_Handler