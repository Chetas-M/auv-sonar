"""
Firmware export module for STM32G4 microcontroller target.
Generates C header files containing uint16_t DAC lookup tables as firmware-ready
prototype headers aligned for timer-triggered DMA playback.
"""

import os
from datetime import datetime
from typing import List, Optional
from .waveform import Waveform
from .config import DAC_RESOLUTION_BITS, MCU_NAME


def export_waveform_to_c_header(
    waveform: Waveform,
    output_path: str,
    array_name: str,
    profile_label: str = "BALANCED",
) -> str:
    """
    Exports a 12-bit DAC waveform table to a firmware-ready prototype C header file.

    Args:
        waveform: Generated Waveform object.
        output_path: Absolute or relative path to the .h file.
        array_name: Name of the C array (e.g. 'CHIRP_BALANCED_LUT').
        profile_label: Human-readable profile name.

    Returns:
        The generated C code string.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    guard_name = os.path.basename(output_path).replace(".", "_").upper() + "_"

    sample_count = waveform.sample_count
    byte_count = sample_count * 2
    f_center = (waveform.f_start_hz + waveform.f_end_hz) / 2.0
    bw = abs(waveform.f_end_hz - waveform.f_start_hz)

    lines: List[str] = [
        "/**",
        f" * @file    {os.path.basename(output_path)}",
        f" * @brief   Firmware-Ready Prototype 12-bit DAC Lookup Table for {profile_label} Sonar Chirp",
        f" * @target  {MCU_NAME} (Timer TRGO -> DMA -> high-speed STM32G4 DAC path, with exact DAC instance/pin verified during board bring-up)",
        f" * @date    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        " *",
        " * @section METADATA",
        f" * - Profile Mode:           {profile_label}",
        f" * - DAC Sample Rate:         {waveform.sample_rate_hz:,} Hz (4.0 MSPS)",
        f" * - Start Frequency (f_0):   {waveform.f_start_hz:,.1f} Hz",
        f" * - End Frequency (f_1):     {waveform.f_end_hz:,.1f} Hz",
        f" * - Center Frequency (f_c):  {f_center:,.1f} Hz",
        f" * - Bandwidth (B):           {bw:,.1f} Hz",
        f" * - Pulse Duration:          {waveform.duration_s * 1000.0:.3f} ms",
        f" * - Total Samples:           {sample_count}",
        f" * - Memory Footprint:        {byte_count:,} bytes ({byte_count / 1024.0:.2f} KB)",
        f" * - DAC Resolution:          {DAC_RESOLUTION_BITS}-bit unsigned (0 to 4095)",
        f" * - Window Function:         {waveform.window_type.capitalize()}",
        f" * - Simulated SQNR:          {waveform.sqnr_db:.2f} dB",
        " *",
        " * @note Prototype header for firmware bring-up. In STM32 firmware, configure DMA",
        " *       in Circular or Normal mode with half-word (16-bit) memory and peripheral sizes.",
        " *       At 4.0 MSPS, external analog buffering and high-speed DAC configuration must be validated on scope.",
        " */",
        "",
        f"#ifndef {guard_name}",
        f"#define {guard_name}",
        "",
        "#include <stdint.h>",
        "",
        "#ifdef __cplusplus",
        'extern "C" {',
        "#endif",
        "",
        "/* DMA alignment helper for 32-bit boundary optimization */",
        "#ifndef DMA_ALIGN",
        "  #if defined(__GNUC__) || defined(__clang__)",
        "    #define DMA_ALIGN __attribute__((aligned(4)))",
        "  #elif defined(__ICCARM__)",
        "    #define DMA_ALIGN #pragma data_alignment=4",
        "  #else",
        "    #define DMA_ALIGN",
        "  #endif",
        "#endif",
        "",
        f"#define {array_name}_SAMPLE_RATE_HZ  ({waveform.sample_rate_hz}UL)",
        f"#define {array_name}_F_START_HZ      ({int(waveform.f_start_hz)}UL)",
        f"#define {array_name}_F_END_HZ        ({int(waveform.f_end_hz)}UL)",
        f"#define {array_name}_DURATION_US     ({int(waveform.duration_s * 1e6)}UL)",
        f"#define {array_name}_SAMPLE_COUNT    ({sample_count}U)",
        f"#define {array_name}_SIZE_BYTES      ({byte_count}U)",
        "",
        f"DMA_ALIGN const uint16_t {array_name}[{sample_count}] = {{",
    ]

    # Format samples: 16 samples per line in 0x0FFF format
    samples = waveform.dac_codes
    samples_per_line = 16
    for i in range(0, sample_count, samples_per_line):
        chunk = samples[i : i + samples_per_line]
        chunk_str = ", ".join(f"0x{val:04X}" for val in chunk)
        if i + samples_per_line < sample_count:
            lines.append(f"    {chunk_str},")
        else:
            lines.append(f"    {chunk_str}")

    lines.extend([
        "};",
        "",
        "#ifdef __cplusplus",
        "}",
        "#endif",
        "",
        f"#endif /* {guard_name} */",
        "",
    ])

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return content


def export_unified_profile_header(output_path: str) -> None:
    """Exports a unified master header linking all profiles with descriptor structs."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    content = """/**
 * @file    sonar_profiles.h
 * @brief   Master header registering all adaptive chirp lookup tables for STM32G4.
 */

#ifndef SONAR_PROFILES_H_
#define SONAR_PROFILES_H_

#include <stdint.h>
#include <stddef.h>
#include "chirp_muddy.h"
#include "chirp_balanced.h"
#include "chirp_clear.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SONAR_PROFILE_MUDDY = 0,     /**< 100-220 kHz for suspended sediment/turbid water */
    SONAR_PROFILE_BALANCED = 1,  /**< 200-400 kHz nominal default */
    SONAR_PROFILE_CLEAR = 2,     /**< 350-500 kHz for high resolution in clear water */
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
        .profile_id     = SONAR_PROFILE_MUDDY,
        .name           = "Muddy (100-220 kHz)",
        .sample_rate_hz = CHIRP_MUDDY_LUT_SAMPLE_RATE_HZ,
        .f_start_hz     = CHIRP_MUDDY_LUT_F_START_HZ,
        .f_end_hz       = CHIRP_MUDDY_LUT_F_END_HZ,
        .duration_us    = CHIRP_MUDDY_LUT_DURATION_US,
        .sample_count   = CHIRP_MUDDY_LUT_SAMPLE_COUNT,
        .size_bytes     = CHIRP_MUDDY_LUT_SIZE_BYTES,
        .waveform_lut   = CHIRP_MUDDY_LUT
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
        .profile_id     = SONAR_PROFILE_CLEAR,
        .name           = "Clear (350-500 kHz)",
        .sample_rate_hz = CHIRP_CLEAR_LUT_SAMPLE_RATE_HZ,
        .f_start_hz     = CHIRP_CLEAR_LUT_F_START_HZ,
        .f_end_hz       = CHIRP_CLEAR_LUT_F_END_HZ,
        .duration_us    = CHIRP_CLEAR_LUT_DURATION_US,
        .sample_count   = CHIRP_CLEAR_LUT_SAMPLE_COUNT,
        .size_bytes     = CHIRP_CLEAR_LUT_SIZE_BYTES,
        .waveform_lut   = CHIRP_CLEAR_LUT
    }
};

#ifdef __cplusplus
}
#endif

#endif /* SONAR_PROFILES_H_ */
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
