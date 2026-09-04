/**
 * @file    sonar_lut.c
 * @brief   Waveform Lookup Table implementation consuming precomputed chirp headers.
 * @target  STM32G474RET6
 *
 * This module is the EXCLUSIVE inclusion point for the generated header tables
 * (outputs/headers/sonar_profiles.h). This design guarantees that the large
 * 16 KB const arrays are instantiated in Flash exactly once without symbol duplication.
 */

/* Flexible include resolution for standalone build or IDE project tree */
#if __has_include("sonar_profiles.h")
  #include "sonar_profiles.h"
#elif __has_include("../../outputs/headers/sonar_profiles.h")
  #include "../../outputs/headers/sonar_profiles.h"
#elif __has_include("../outputs/headers/sonar_profiles.h")
  #include "../outputs/headers/sonar_profiles.h"
#else
  #error "Cannot locate sonar_profiles.h. Please add outputs/headers to compiler include directories (-I)."
#endif

#include "sonar_lut.h"
#include "main.h"

/* ========================================================================== */
/* COMPILE-TIME INTEGRITY AUDIT (Feasibility Audit §6 Memory Feasibility)      */
/* ========================================================================== */
#if defined(__STDC_VERSION__) && (__STDC_VERSION__ >= 201112L)
_Static_assert(CHIRP_LOW_FREQUENCY_LUT_SAMPLE_COUNT == 8000U,
    "Low-frequency LUT must contain exactly 8,000 samples!");
_Static_assert(CHIRP_BALANCED_LUT_SAMPLE_COUNT == 8000U,
    "Balanced LUT must contain exactly 8,000 samples!");
_Static_assert(CHIRP_HIGH_FREQUENCY_LUT_SAMPLE_COUNT == 8000U,
    "High-frequency LUT must contain exactly 8,000 samples!");

_Static_assert(CHIRP_LOW_FREQUENCY_LUT_SAMPLE_RATE_HZ == 4000000UL,
    "Low-frequency sample rate must be 4.000000 MSPS!");
_Static_assert(CHIRP_BALANCED_LUT_SAMPLE_RATE_HZ == 4000000UL,
    "Balanced sample rate must be 4.000000 MSPS!");
_Static_assert(CHIRP_HIGH_FREQUENCY_LUT_SAMPLE_RATE_HZ == 4000000UL,
    "High-frequency sample rate must be 4.000000 MSPS!");

_Static_assert(CHIRP_BALANCED_LUT_SIZE_BYTES == 16000U,
    "Profile table size must be exactly 16,000 bytes (8,000 * 2 bytes)!");
_Static_assert(CHIRP_BALANCED_LUT_DURATION_US == 2000UL,
    "Chirp pulse duration must be exactly 2,000 us (2.0 ms)!");
#endif

/* ========================================================================== */
/* EXPORTED ACCESSOR FUNCTIONS                                                */
/* ========================================================================== */

const SonarProfileDescriptor_t* Sonar_GetProfile(SonarProfileId_t id)
{
    if ((uint32_t)id >= (uint32_t)SONAR_PROFILE_COUNT) {
        /* Fail-loud: Do NOT silently substitute BALANCED. Return NULL so the
         * caller or fault handler detects corrupted state / invalid enums immediately. */
        return NULL;
    }
    return (const SonarProfileDescriptor_t*)&SONAR_PROFILES[id];
}

const uint16_t* Sonar_GetProfileLUT(SonarProfileId_t id)
{
    const SonarProfileDescriptor_t* desc = Sonar_GetProfile(id);
    return (desc != NULL) ? desc->waveform_lut : NULL;
}

uint16_t Sonar_GetProfileSampleCount(SonarProfileId_t id)
{
    const SonarProfileDescriptor_t* desc = Sonar_GetProfile(id);
    return (desc != NULL) ? desc->sample_count : 0U;
}

const char* Sonar_GetProfileName(SonarProfileId_t id)
{
    const SonarProfileDescriptor_t* desc = Sonar_GetProfile(id);
    return (desc != NULL) ? desc->name : NULL;
}

uint32_t Sonar_GetProfileCount(void)
{
    return (uint32_t)SONAR_PROFILE_COUNT;
}

bool Sonar_ValidateLUTIntegrity(void)
{
    for (uint32_t i = 0; i < (uint32_t)SONAR_PROFILE_COUNT; i++) {
        const SonarProfileDescriptor_t* desc = &SONAR_PROFILES[i];
        if (desc->waveform_lut == NULL) {
            return false;
        }
        if (desc->sample_count != SONAR_SAMPLE_COUNT) {
            return false;
        }
        if (desc->sample_rate_hz != 4000000UL) {
            return false;
        }
        if (desc->duration_us != SONAR_PULSE_DURATION_US) {
            return false;
        }
        /* Verify midscale start and end samples (Hann window envelope) */
        uint16_t start_code = desc->waveform_lut[0];
        uint16_t end_code = desc->waveform_lut[desc->sample_count - 1];
        if (start_code < 2046 || start_code > 2050) {
            return false; /* Start code not at midscale */
        }
        if (end_code < 2046 || end_code > 2050) {
            return false; /* End code not at midscale */
        }
    }
    return true;
}
