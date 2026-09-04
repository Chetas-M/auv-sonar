#include <assert.h>
#include <stdbool.h>
#include <stdint.h>

#include "sonar_transmitter.h"

static unsigned start_dma_calls;
static unsigned stop_dma_calls;
static unsigned start_timer_calls;
static unsigned stop_timer_calls;
static const uint16_t *last_samples;
static uint16_t last_sample_count;

static bool start_dma(const uint16_t *samples, uint16_t sample_count)
{
    ++start_dma_calls;
    last_samples = samples;
    last_sample_count = sample_count;
    return true;
}
static void stop_dma(void) { ++stop_dma_calls; }
static void start_timer(void) { ++start_timer_calls; }
static void stop_timer(void) { ++stop_timer_calls; }

int main(void)
{
    const SonarTxHardwareOps hw = {start_dma, stop_dma, start_timer, stop_timer};
    SonarTransmitter tx;

    assert(sonar_tx_init(&tx, &hw, SONAR_PROFILE_BALANCED) == SONAR_TX_OK);
    assert(sonar_tx_start_ping(&tx) == SONAR_TX_OK);
    assert(sonar_tx_is_active(&tx));
    assert(last_samples == SONAR_PROFILES[SONAR_PROFILE_BALANCED].waveform_lut);
    assert(last_sample_count == 8000U);

    assert(sonar_tx_request_profile(&tx, SONAR_PROFILE_HIGH_FREQUENCY) == SONAR_TX_OK);
    assert(sonar_tx_active_profile(&tx) == SONAR_PROFILE_BALANCED);
    assert(sonar_tx_start_ping(&tx) == SONAR_TX_BUSY);

    sonar_tx_on_dma_complete(&tx);
    assert(!sonar_tx_is_active(&tx));
    assert(sonar_tx_start_ping(&tx) == SONAR_TX_OK);
    assert(sonar_tx_active_profile(&tx) == SONAR_PROFILE_HIGH_FREQUENCY);
    assert(last_samples == SONAR_PROFILES[SONAR_PROFILE_HIGH_FREQUENCY].waveform_lut);
    assert(start_dma_calls == 2U);
    assert(stop_dma_calls == 1U);
    assert(start_timer_calls == 2U);
    assert(stop_timer_calls == 3U);
    return 0;
}
