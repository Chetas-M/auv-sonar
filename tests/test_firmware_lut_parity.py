"""
Host-side firmware LUT parity verification test suite.
Loads precomputed C header files from outputs/headers/ and validates:
1. Array length matches expected 8,000 samples per profile.
2. All DAC codes fall strictly within valid 12-bit range (0 to 4095).
3. Values match bit-exactly what src/waveform.py generates.
4. Header macro definitions match architectural specifications.
"""

import os
import re
import numpy as np
import pytest

from src.config import (
    DAC_SAMPLE_RATE_HZ,
    DAC_RESOLUTION_BITS,
    DEFAULT_PULSE_DURATION_S,
    DAC_MIN_CODE,
    DAC_MAX_CODE,
)
from src.profiles import BAND_PROFILES, ProfileType
from src.waveform import generate_lfm_chirp


HEADERS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "headers")

PROFILE_FILES = {
    ProfileType.LOW_FREQUENCY: {
        "header": "chirp_low_frequency.h",
        "array_name": "CHIRP_LOW_FREQUENCY_LUT",
        "expected_f_start": 100_000.0,
        "expected_f_end": 220_000.0,
    },
    ProfileType.BALANCED: {
        "header": "chirp_balanced.h",
        "array_name": "CHIRP_BALANCED_LUT",
        "expected_f_start": 200_000.0,
        "expected_f_end": 400_000.0,
    },
    ProfileType.HIGH_FREQUENCY: {
        "header": "chirp_high_frequency.h",
        "array_name": "CHIRP_HIGH_FREQUENCY_LUT",
        "expected_f_start": 350_000.0,
        "expected_f_end": 500_000.0,
    },
}


def parse_c_lut_header(header_path: str, array_name: str) -> np.ndarray:
    """
    Parses a C header file containing a uint16_t lookup table and extracts
    the numeric samples into a NumPy uint16 array.
    """
    assert os.path.isfile(header_path), f"Header file not found: {header_path}"

    with open(header_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to find array definition: DMA_ALIGN const uint16_t ARRAY_NAME[...] = { ... };
    pattern = rf"(?:DMA_ALIGN\s+)?const\s+uint16_t\s+{array_name}\s*\[\s*(\d*)\s*\]\s*=\s*\{{([^}}]+)\}};"
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, f"Could not locate array '{array_name}' in {header_path}"

    declared_size_str = match.group(1).strip()
    raw_elements_str = match.group(2)

    # Extract all hexadecimal or decimal numbers
    hex_values = re.findall(r"0x[0-9a-fA-F]+|\d+", raw_elements_str)
    parsed_samples = np.array([int(val, 0) for val in hex_values], dtype=np.uint16)

    if declared_size_str:
        expected_size = int(declared_size_str)
        assert len(parsed_samples) == expected_size, (
            f"Parsed sample count ({len(parsed_samples)}) does not match "
            f"declared array size ({expected_size}) in {header_path}"
        )

    return parsed_samples


def parse_header_macro(header_path: str, macro_name: str) -> int:
    """Extracts integer value of a #define MACRO (value) from header."""
    with open(header_path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = rf"#define\s+{macro_name}\s+\(?(\d+)(?:UL|U|L)?\)?"
    match = re.search(pattern, content)
    assert match is not None, f"Macro '{macro_name}' not found in {header_path}"
    return int(match.group(1))


class TestFirmwareLUTParity:
    """Test suite for validating firmware LUT headers against Python digital twin."""

    @pytest.mark.parametrize("profile_type", list(ProfileType))
    def test_lut_sample_count_and_sizing(self, profile_type: ProfileType):
        """Verify each profile LUT contains exactly 8,000 samples (16,000 bytes)."""
        cfg = PROFILE_FILES[profile_type]
        header_path = os.path.join(HEADERS_DIR, cfg["header"])
        samples = parse_c_lut_header(header_path, cfg["array_name"])

        # Expected sample count = Fs * Tp = 4,000,000 * 0.002 = 8,000
        expected_samples = 8000
        assert len(samples) == expected_samples, (
            f"Profile {profile_type.value} has {len(samples)} samples, expected {expected_samples}"
        )
        assert samples.nbytes == expected_samples * 2, "LUT memory footprint must be exactly 16,000 bytes"

    @pytest.mark.parametrize("profile_type", list(ProfileType))
    def test_lut_values_within_12bit_dac_range(self, profile_type: ProfileType):
        """Verify all samples are strictly within valid 12-bit unsigned range [0, 4095]."""
        cfg = PROFILE_FILES[profile_type]
        header_path = os.path.join(HEADERS_DIR, cfg["header"])
        samples = parse_c_lut_header(header_path, cfg["array_name"])

        min_val = int(np.min(samples))
        max_val = int(np.max(samples))

        assert min_val >= DAC_MIN_CODE, f"Profile {profile_type.value} min code {min_val} < {DAC_MIN_CODE}"
        assert max_val <= DAC_MAX_CODE, f"Profile {profile_type.value} max code {max_val} > {DAC_MAX_CODE}"

        # Midscale check: Hann window tapers to 0 at start and end -> signal midscale is 2048 (0x0800)
        start_val = samples[0]
        end_val = samples[-1]
        assert abs(int(start_val) - 2048) <= 1, f"Start of tapered chirp must be at midscale (2048), got {start_val}"
        assert abs(int(end_val) - 2048) <= 1, f"End of tapered chirp must be at midscale (2048), got {end_val}"

    @pytest.mark.parametrize("profile_type", list(ProfileType))
    def test_lut_bit_exact_parity_with_python_waveform(self, profile_type: ProfileType):
        """
        Verify bit-exact equality between exported C header LUT and
        src/waveform.py synthesize output.
        """
        cfg = PROFILE_FILES[profile_type]
        band = BAND_PROFILES[profile_type]
        header_path = os.path.join(HEADERS_DIR, cfg["header"])

        # 1. Parse header LUT
        c_lut = parse_c_lut_header(header_path, cfg["array_name"])

        # 2. Synthesize reference waveform from Python digital twin
        py_wf = generate_lfm_chirp(
            f_start_hz=band.f_start_hz,
            f_end_hz=band.f_end_hz,
            duration_s=DEFAULT_PULSE_DURATION_S,
            sample_rate_hz=DAC_SAMPLE_RATE_HZ,
            amplitude_factor=1.0,
            window_type="hann",
        )

        # 3. Assert exact equality
        assert len(c_lut) == len(py_wf.dac_codes), "Length mismatch between C LUT and Python waveform"

        max_diff = int(np.max(np.abs(c_lut.astype(np.int32) - py_wf.dac_codes.astype(np.int32))))
        mismatch_count = int(np.count_nonzero(c_lut != py_wf.dac_codes))

        assert max_diff == 0, (
            f"Bit-exact parity failure on profile {profile_type.value}! "
            f"Max absolute code difference = {max_diff}, mismatched samples = {mismatch_count} / {len(c_lut)}"
        )
        assert np.array_equal(c_lut, py_wf.dac_codes), (
            f"Profile {profile_type.value} LUT is not bit-identical to Python digital twin"
        )

    @pytest.mark.parametrize("profile_type", list(ProfileType))
    def test_header_macro_definitions(self, profile_type: ProfileType):
        """Verify architectural macro constants defined in header files."""
        cfg = PROFILE_FILES[profile_type]
        header_path = os.path.join(HEADERS_DIR, cfg["header"])
        pfx = cfg["array_name"]

        assert parse_header_macro(header_path, f"{pfx}_SAMPLE_RATE_HZ") == DAC_SAMPLE_RATE_HZ
        assert parse_header_macro(header_path, f"{pfx}_DAC_BITS") == DAC_RESOLUTION_BITS
        assert parse_header_macro(header_path, f"{pfx}_F_START_HZ") == int(cfg["expected_f_start"])
        assert parse_header_macro(header_path, f"{pfx}_F_END_HZ") == int(cfg["expected_f_end"])
        assert parse_header_macro(header_path, f"{pfx}_SAMPLE_COUNT") == 8000
        assert parse_header_macro(header_path, f"{pfx}_SIZE_BYTES") == 16000
        assert parse_header_macro(header_path, f"{pfx}_DURATION_US") == 2000

    def test_unified_sonar_profiles_header_exists_and_consistent(self):
        """Verify master sonar_profiles.h header registers all profiles correctly."""
        master_path = os.path.join(HEADERS_DIR, "sonar_profiles.h")
        assert os.path.isfile(master_path), "sonar_profiles.h master header missing"

        with open(master_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check all profiles are registered in enum and struct
        for p in ["SONAR_PROFILE_LOW_FREQUENCY", "SONAR_PROFILE_BALANCED", "SONAR_PROFILE_HIGH_FREQUENCY"]:
            assert p in content, f"Profile identifier {p} missing from sonar_profiles.h"

        for lut in ["CHIRP_LOW_FREQUENCY_LUT", "CHIRP_BALANCED_LUT", "CHIRP_HIGH_FREQUENCY_LUT"]:
            assert lut in content, f"LUT symbol {lut} missing from sonar_profiles.h"
