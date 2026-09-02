/**
 * @file    sonar_profiles.h
 * @brief   Master header registering all adaptive chirp lookup tables for STM32G4.
 * @note    Generated simulation prototype waveform. Requires hardware validation.
 */
#ifndef SONAR_PROFILES_H_
#define SONAR_PROFILES_H_

#include <stdint.h>
#include <stddef.h>
#include "chirp_low_frequency.h"
#include "chirp_balanced.h"
#include "chirp_high_frequency.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SONAR_PROFILE_LOW_FREQUENCY = 0, /**< 100-220 kHz for degraded/scattering channel */
    SONAR_PROFILE_BALANCED = 1,      /**< 200-400 kHz nominal default (best range resolution) */
    SONAR_PROFILE_HIGH_FREQUENCY = 2,/**< 350-500 kHz for high frequency beam directivity */
    SONAR_PROFILE_COUNT
} SonarProfileId_t;

typedef struct {
    SonarProfileId_t profile_id;
    const char*      name;
    uint32_t         sample_rate_hz;
    uint32_t         f_start_hz;
    uint32_t         f_end_hz;
    uint32_t         duration_us;
    uint16_t         sample_count;
    uint16_t         size_bytes;
    const uint16_t*  waveform_lut;
} SonarProfileDescriptor_t;

static const SonarProfileDescriptor_t SONAR_PROFILES[SONAR_PROFILE_COUNT] = {
    {
        .profile_id     = SONAR_PROFILE_LOW_FREQUENCY,
        .name           = "Low Frequency (100-220 kHz)",
        .sample_rate_hz = CHIRP_LOW_FREQUENCY_LUT_SAMPLE_RATE_HZ,
        .f_start_hz     = CHIRP_LOW_FREQUENCY_LUT_F_START_HZ,
        .f_end_hz       = CHIRP_LOW_FREQUENCY_LUT_F_END_HZ,
        .duration_us    = CHIRP_LOW_FREQUENCY_LUT_DURATION_US,
        .sample_count   = CHIRP_LOW_FREQUENCY_LUT_SAMPLE_COUNT,
        .size_bytes     = CHIRP_LOW_FREQUENCY_LUT_SIZE_BYTES,
        .waveform_lut   = CHIRP_LOW_FREQUENCY_LUT
    },
    {
        .profile_id     = SONAR_PROFILE_BALANCED,
        .name           = "Balanced (200-400 kHz)",
        .sample_rate_hz = CHIRP_BALANCED_LUT_SAMPLE_RATE_HZ,
        .f_start_hz     = CHIRP_BALANCED_LUT_F_START_HZ,
        .f_end_hz       = CHIRP_BALANCED_LUT_F_END_HZ,
        .duration_us    = CHIRP_BALANCED_LUT_DURATION_US,
        .sample_count   = CHIRP_BALANCED_LUT_SAMPLE_COUNT,
        .size_bytes     = CHIRP_BALANCED_LUT_SIZE_BYTES,
        .waveform_lut   = CHIRP_BALANCED_LUT
    },
    {
        .profile_id     = SONAR_PROFILE_HIGH_FREQUENCY,
        .name           = "High Frequency (350-500 kHz)",
        .sample_rate_hz = CHIRP_HIGH_FREQUENCY_LUT_SAMPLE_RATE_HZ,
        .f_start_hz     = CHIRP_HIGH_FREQUENCY_LUT_F_START_HZ,
        .f_end_hz       = CHIRP_HIGH_FREQUENCY_LUT_F_END_HZ,
        .duration_us    = CHIRP_HIGH_FREQUENCY_LUT_DURATION_US,
        .sample_count   = CHIRP_HIGH_FREQUENCY_LUT_SAMPLE_COUNT,
        .size_bytes     = CHIRP_HIGH_FREQUENCY_LUT_SIZE_BYTES,
        .waveform_lut   = CHIRP_HIGH_FREQUENCY_LUT
    }
};

#ifdef __cplusplus
}
#endif

#endif /* SONAR_PROFILES_H_ */
