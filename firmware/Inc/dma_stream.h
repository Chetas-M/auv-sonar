/**
 * @file    dma_stream.h
 * @brief   DMA1 Channel 1 and DMAMUX1 streaming controller for DAC3 Channel 2.
 * @target  STM32G474RET6 on NUCLEO-G474RE.
 * @note    All hardware performance claims are marked [PENDING HARDWARE VALIDATION].
 *
 * Locked Architectural Decision (Feasibility Audit §C.4):
 * - Half-word (16-bit) memory-to-peripheral transfers.
 * - Atomic ping-boundary profile switching on DMA Transfer-Complete interrupt.
 */

#ifndef DMA_STREAM_H_
#define DMA_STREAM_H_

#include <stdint.h>
#include <stdbool.h>
#include "sonar_lut.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SONAR_STATE_UNINITIALIZED = 0,
    SONAR_STATE_IDLE_READY    = 1,
    SONAR_STATE_TRANSMITTING  = 2,
    SONAR_STATE_INTER_PULSE   = 3,
    SONAR_STATE_ERROR         = 4
} SonarTransmitterState_t;

/**
 * @brief  Initializes DMA1 Channel 1 and DMAMUX1 routing for DAC3 Channel 2.
 *         Configures memory-to-peripheral, 16-bit half-word transfers, and TC interrupt.
 * @param  initial_profile: Starting profile ID (typically SONAR_PROFILE_BALANCED).
 */
void DMA_Sonar_Init(SonarProfileId_t initial_profile);

/**
 * @brief  Triggers the immediate start of the first sonar chirp ping.
 */
void DMA_Sonar_Start(void);

/**
 * @brief  Stops sonar transmission cleanly at the end of the current ping.
 */
void DMA_Sonar_Stop(void);

/**
 * @brief  Asynchronously queues a new profile to be latched AT THE NEXT PING BOUNDARY.
 *         Guarantees atomic switching without corrupting ongoing chirps.
 * @param  new_profile: Profile ID to activate on next ping.
 */
void DMA_Sonar_QueueProfile(SonarProfileId_t new_profile);

/**
 * @brief  Cycles to the next profile: LOW_FREQUENCY -> BALANCED -> HIGH_FREQUENCY -> LOW...
 *         Safe to call from GPIO button ISR.
 */
void DMA_Sonar_CycleNextProfile(void);

/**
 * @brief  Returns the profile ID currently being transmitted.
 */
SonarProfileId_t DMA_Sonar_GetActiveProfile(void);

/**
 * @brief  Returns the queued profile ID awaiting the next ping boundary.
 */
SonarProfileId_t DMA_Sonar_GetQueuedProfile(void);

/**
 * @brief  Returns current transmitter operational state.
 */
SonarTransmitterState_t DMA_Sonar_GetState(void);

/**
 * @brief  Returns cumulative count of completed pings since system boot.
 */
uint32_t DMA_Sonar_GetPingCount(void);

/**
 * @brief  ISR Handler called from DMA1_Channel1_IRQHandler on Transfer Complete.
 *         Stops TIM2, updates profile pointer, and arms the 18.0 ms PRI timer.
 */
void DMA_Sonar_OnTransferComplete(void);

/**
 * @brief  ISR Handler called from TIM6_DAC_IRQHandler on PRI quiet period expiration.
 *         Re-arms DMA and restarts TIM2 to launch the next 2.0 ms chirp.
 */
void DMA_Sonar_OnPriTimerExpired(void);

#ifdef __cplusplus
}
#endif

#endif /* DMA_STREAM_H_ */
