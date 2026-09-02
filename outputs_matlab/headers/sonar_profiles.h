/**
 * @file    sonar_profiles.h
 * @brief   Master header registering all adaptive chirp lookup tables for STM32G4.
 */
#ifndef SONAR_PROFILES_H_
#define SONAR_PROFILES_H_

#include "chirp_muddy.h"
#include "chirp_balanced.h"
#include "chirp_clear.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SONAR_PROFILE_MUDDY = 0,
    SONAR_PROFILE_BALANCED = 1,
    SONAR_PROFILE_CLEAR = 2,
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
    { SONAR_PROFILE_MUDDY,    "Muddy (100-220k)",    CHIRP_MUDDY_LUT_SAMPLE_RATE_HZ,    CHIRP_MUDDY_LUT_F_START_HZ,    CHIRP_MUDDY_LUT_F_END_HZ,    CHIRP_MUDDY_LUT_DURATION_US,    CHIRP_MUDDY_LUT_SAMPLE_COUNT,    CHIRP_MUDDY_LUT_SIZE_BYTES,    CHIRP_MUDDY_LUT },
    { SONAR_PROFILE_BALANCED, "Balanced (200-400k)", CHIRP_BALANCED_LUT_SAMPLE_RATE_HZ, CHIRP_BALANCED_LUT_F_START_HZ, CHIRP_BALANCED_LUT_F_END_HZ, CHIRP_BALANCED_LUT_DURATION_US, CHIRP_BALANCED_LUT_SAMPLE_COUNT, CHIRP_BALANCED_LUT_SIZE_BYTES, CHIRP_BALANCED_LUT },
    { SONAR_PROFILE_CLEAR,    "Clear (350-500k)",    CHIRP_CLEAR_LUT_SAMPLE_RATE_HZ,    CHIRP_CLEAR_LUT_F_START_HZ,    CHIRP_CLEAR_LUT_F_END_HZ,    CHIRP_CLEAR_LUT_DURATION_US,    CHIRP_CLEAR_LUT_SAMPLE_COUNT,    CHIRP_CLEAR_LUT_SIZE_BYTES,    CHIRP_CLEAR_LUT }
};

#ifdef __cplusplus
}
#endif
#endif /* SONAR_PROFILES_H_ */