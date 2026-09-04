/**
 * @file    stm32g4xx_it.h
 * @brief   Interrupt Service Routine prototypes for STM32G474 Sonar Transmitter.
 */

#ifndef STM32G4XX_IT_H_
#define STM32G4XX_IT_H_

#ifdef __cplusplus
extern "C" {
#endif

void NMI_Handler(void);
void HardFault_Handler(void);
void MemManage_Handler(void);
void BusFault_Handler(void);
void UsageFault_Handler(void);
void SVC_Handler(void);
void DebugMon_Handler(void);
void PendSV_Handler(void);
void SysTick_Handler(void);

/* Peripheral ISRs */
void DMA1_Channel1_IRQHandler(void);
void TIM6_DAC_IRQHandler(void);
void EXTI15_10_IRQHandler(void);

#ifdef __cplusplus
}
#endif

#endif /* STM32G4XX_IT_H_ */
