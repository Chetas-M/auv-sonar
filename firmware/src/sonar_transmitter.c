#include "sonar_transmitter.h"

#include <stddef.h>

static bool profile_is_valid(SonarProfileId_t profile)
{
    return (uint32_t)profile < (uint32_t)SONAR_PROFILE_COUNT;
}

SonarTxStatus sonar_tx_init(SonarTransmitter *tx, const SonarTxHardwareOps *hw,
                            SonarProfileId_t initial_profile)
{
    if ((tx == NULL) || (hw == NULL) || (hw->start_dac_dma == NULL) ||
        (hw->stop_dac_dma == NULL) || (hw->start_sample_timer == NULL) ||
        (hw->stop_sample_timer == NULL)) {
        return SONAR_TX_BAD_ARGUMENT;
    }
    if (!profile_is_valid(initial_profile)) {
        return SONAR_TX_INVALID_PROFILE;
    }

    tx->hw = hw;
    tx->active_profile = initial_profile;
    tx->requested_profile = initial_profile;
    tx->transmission_active = false;
    return SONAR_TX_OK;
}

SonarTxStatus sonar_tx_request_profile(SonarTransmitter *tx,
                                       SonarProfileId_t requested_profile)
{
    if ((tx == NULL) || (tx->hw == NULL)) {
        return SONAR_TX_BAD_ARGUMENT;
    }
    if (!profile_is_valid(requested_profile)) {
        return SONAR_TX_INVALID_PROFILE;
    }

    /* A naturally aligned enum-sized store is atomic on Cortex-M. If this
     * function is called from an ISR with a different priority than the ping
     * ISR, protect this assignment with the board's critical-section API. */
    tx->requested_profile = requested_profile;
    return SONAR_TX_OK;
}

SonarTxStatus sonar_tx_start_ping(SonarTransmitter *tx)
{
    const SonarProfileDescriptor_t *profile;

    if ((tx == NULL) || (tx->hw == NULL)) {
        return SONAR_TX_BAD_ARGUMENT;
    }
    if (tx->transmission_active) {
        return SONAR_TX_BUSY;
    }
    if (!profile_is_valid(tx->requested_profile)) {
        return SONAR_TX_INVALID_PROFILE;
    }

    /* This is the sole latching point. A request received while a DMA transfer
     * is active cannot alter its source pointer or corrupt its chirp. */
    tx->active_profile = tx->requested_profile;
    profile = &SONAR_PROFILES[tx->active_profile];

    tx->hw->stop_sample_timer();
    if (!tx->hw->start_dac_dma(profile->waveform_lut, profile->sample_count)) {
        return SONAR_TX_HARDWARE_FAILURE;
    }

    tx->transmission_active = true;
    tx->hw->start_sample_timer();
    return SONAR_TX_OK;
}

void sonar_tx_on_dma_complete(SonarTransmitter *tx)
{
    if ((tx == NULL) || (tx->hw == NULL)) {
        return;
    }

    tx->hw->stop_sample_timer();
    tx->hw->stop_dac_dma();
    tx->transmission_active = false;
}

SonarProfileId_t sonar_tx_active_profile(const SonarTransmitter *tx)
{
    return (tx == NULL) ? SONAR_PROFILE_COUNT : tx->active_profile;
}

bool sonar_tx_is_active(const SonarTransmitter *tx)
{
    return (tx != NULL) && tx->transmission_active;
}
