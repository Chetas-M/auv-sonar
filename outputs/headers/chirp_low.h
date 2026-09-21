/**
 * @file    chirp_low.h
 * @brief   Compatibility alias header for LOW_FREQUENCY chirp lookup table.
 *          Maps chirp_low and CHIRP_LOW_LENGTH to canonical definitions.
 */

#ifndef CHIRP_LOW_H_
#define CHIRP_LOW_H_

#include "chirp_low_frequency.h"

#ifdef __cplusplus
extern "C" {
#endif

#define chirp_low               CHIRP_LOW_FREQUENCY_LUT
#define CHIRP_LOW_LENGTH        CHIRP_LOW_FREQUENCY_LUT_SAMPLE_COUNT
#define CHIRP_LOW_SAMPLE_COUNT  CHIRP_LOW_FREQUENCY_LUT_SAMPLE_COUNT
#define CHIRP_LOW_SAMPLE_RATE   CHIRP_LOW_FREQUENCY_LUT_SAMPLE_RATE_HZ

#ifdef __cplusplus
}
#endif

#endif /* CHIRP_LOW_H_ */
