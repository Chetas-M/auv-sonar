/**
 * @file    chirp_high.h
 * @brief   Compatibility alias header for HIGH_FREQUENCY chirp lookup table.
 *          Maps chirp_high and CHIRP_HIGH_LENGTH to canonical definitions.
 */

#ifndef CHIRP_HIGH_H_
#define CHIRP_HIGH_H_

#include "chirp_high_frequency.h"

#ifdef __cplusplus
extern "C" {
#endif

#define chirp_high               CHIRP_HIGH_FREQUENCY_LUT
#define CHIRP_HIGH_LENGTH        CHIRP_HIGH_FREQUENCY_LUT_SAMPLE_COUNT
#define CHIRP_HIGH_SAMPLE_COUNT  CHIRP_HIGH_FREQUENCY_LUT_SAMPLE_COUNT
#define CHIRP_HIGH_SAMPLE_RATE   CHIRP_HIGH_FREQUENCY_LUT_SAMPLE_RATE_HZ

#ifdef __cplusplus
}
#endif

#endif /* CHIRP_HIGH_H_ */
