#ifndef SONAR_TRANSMITTER_H
#define SONAR_TRANSMITTER_H

#include <stdbool.h>
#include <stdint.h>

#include "sonar_profiles.h"

/*
 * Hardware-independent transmitter controller.
 *
 * Configure the STM32 timer to produce a 4 MHz TRGO event and configure the
 * DAC to accept that trigger.  The board-specific callbacks below are the
 * only code that should call STM32 HAL/LL APIs.
 */
typedef struct {
    bool (*start_dac_dma)(const uint16_t *samples, uint16_t sample_count);
    void (*stop_dac_dma)(void);
    void (*start_sample_timer)(void);
    void (*stop_sample_timer)(void);
} SonarTxHardwareOps;

typedef enum {
    SONAR_TX_OK = 0,
    SONAR_TX_BAD_ARGUMENT,
    SONAR_TX_INVALID_PROFILE,
    SONAR_TX_HARDWARE_FAILURE,
    SONAR_TX_BUSY
} SonarTxStatus;

typedef struct {
    const SonarTxHardwareOps *hw;
    volatile SonarProfileId_t active_profile;
    volatile SonarProfileId_t requested_profile;
    volatile bool transmission_active;
} SonarTransmitter;

SonarTxStatus sonar_tx_init(SonarTransmitter *tx, const SonarTxHardwareOps *hw,
                            SonarProfileId_t initial_profile);

/* Safe to call while a chirp is transmitting. The request takes effect only
 * when sonar_tx_start_ping() is called after the current transfer completes. */
SonarTxStatus sonar_tx_request_profile(SonarTransmitter *tx,
                                       SonarProfileId_t requested_profile);

/* Call at the beginning of a PRI, after the previous DMA transfer-complete
 * interrupt has called sonar_tx_on_dma_complete(). */
SonarTxStatus sonar_tx_start_ping(SonarTransmitter *tx);

/* Call from the DAC DMA transfer-complete callback. */
void sonar_tx_on_dma_complete(SonarTransmitter *tx);

SonarProfileId_t sonar_tx_active_profile(const SonarTransmitter *tx);
bool sonar_tx_is_active(const SonarTransmitter *tx);

#endif /* SONAR_TRANSMITTER_H */
