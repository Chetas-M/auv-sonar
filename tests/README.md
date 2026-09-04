# Automated Testing & Verification Suite (`tests/`)

This directory contains the automated unit, regression, and cross-platform parity test suites for the **AUV Adaptive Sonar Transmitter Digital Twin**.

The test framework validates all locked implementation requirements, acoustic physics equations, DAC quantization limits, memory sizing, state machine hysteresis, and bit-exact parity between Python, MATLAB, and STM32 C firmware.

---

## 1. Quickstart & Test Execution

### Running with Pytest (Recommended: 79 Tests Passing)
```bash
# Run all 79 automated tests with verbose output
python -m pytest tests/ -v

# Run with summary only
pytest
```

### Running with Python Unittest (66 Tests Passing)
```bash
# Standard Python unittest runner
python -m unittest discover -s tests -p "test_*.py" -v
```
*(Note: Pytest runs 79 tests because it expands `@pytest.mark.parametrize` test cases across all three transmission profiles in `test_firmware_lut_parity.py`.)*

### Running Specific Test Modules
```bash
# 1. Hardware, signal, and DSP verification (36 tests)
pytest tests/test_simulator.py -v

# 2. Priority 1 profile evaluation and selection (12 tests)
pytest tests/test_profile_evaluation.py -v

# 3. Seawater acoustic physics regression (9 tests)
pytest tests/test_physics_regression.py -v

# 4. MATLAB architecture and math parity (9 tests)
pytest tests/test_matlab_parity.py -v

# 5. STM32 C firmware LUT bit-exact parity (13 tests)
pytest tests/test_firmware_lut_parity.py -v
```

---

## 2. Test Suite Architecture

| Test Module | Test Class / Scope | Tests | Target Subsystem & Primary Assertions |
|---|---|:---:|---|
| **[`test_simulator.py`](file:///d:/AUV%20sonar/tests/test_simulator.py)** | `TestSection21ComprehensiveSuite`<br>`TestWaveformGeneration`<br>`TestDACQuantization`<br>`TestHysteresisAndAdaptation`<br>`TestPowerModel`<br>`TestCHeaderExport`<br>`TestRigorousVerificationChecks` | **36** | **23 Locked Hardware & Signal Requirements:**<br>• $N_p = 8,000$ samples, $T_p = 2.0\text{ ms}$, slope $100\text{ MHz/s}$<br>• Zero NaN/Inf, symmetric Hann tapering<br>• 12-bit unsigned DAC codes ($0\text{–}4095$, midscale $2048$)<br>• Quantization error $\le \pm 0.5\text{ LSB}$, $\text{SQNR} \approx 69.7\text{ dB}$<br>• Directional hysteresis ($\pm 5\%$) and debounce ($N=2$)<br>• Atomic ping-boundary profile latching (50 Hz PRI)<br>• C header code generation and round-trip parse |
| **[`test_profile_evaluation.py`](file:///d:/AUV%20sonar/tests/test_profile_evaluation.py)** | `TestProfilePerformanceEvaluation` | **12** | **Priority 1 Profile Evaluation Engine:**<br>• 5-point discrete frequency evaluation across sweep band<br>• Positive, finite Ainslie-McColm absorption coefficients<br>• Monotonic transmission loss scaling with range<br>• Baseline attenuation ordering ($\text{HIGH} > \text{BALANCED} > \text{LOW}$)<br>• Bandwidth range resolution verification ($\Delta R = 3.75\text{ mm}$ best)<br>• Relative theoretical directivity ordering ($\text{HIGH} > \text{BALANCED} > \text{LOW}$)<br>• Long-range viability fallback to `LOW_FREQUENCY` ($>175\text{ m}$)<br>• Survey Mode selection of `BALANCED`<br>• Directivity Mode selection of `HIGH_FREQUENCY`<br>• Bit-exact execution determinism |
| **[`test_physics_regression.py`](file:///d:/AUV%20sonar/tests/test_physics_regression.py)** | `TestPhysicsRegression` | **9** | **Acoustic Physics & Hydrostatic Regression:**<br>• Frequency & distance unit scaling ($\text{kHz}$ vs $\text{Hz}$, $\text{dB/km}$ vs $\text{dB/m}$)<br>• Implementation parity with independent literature ($<10^{-10}$ error)<br>• Analytical validation of hydrostatic depth factor $P_2 = \exp(-D/6000)$<br>• Canonical attenuation constants ($63.99, 105.62, 135.86\text{ dB/km}$)<br>• Viability extinction boundaries ($155.7\text{ m}, 185.8\text{ m}, 260.7\text{ m}$)<br>• Mackenzie (1981) speed of sound consistency<br>• Canonical JSON artifact schema integrity |
| **[`test_matlab_parity.py`](file:///d:/AUV%20sonar/tests/test_matlab_parity.py)** | `TestMatlabArchitectureParity` | **9** | **Cross-Platform Architecture Parity:**<br>• Verifies existence and sync of all 18 MATLAB `.m` files<br>• Parameter parity across `config.py` and `config_sonar.m`<br>• LFM phase integration formula equivalence<br>• Channel quality score and hysteresis logic parity<br>• Profile frequency band and bandwidth synchronization<br>• $P_2$ hydrostatic pressure term alignment<br>• Plot count and test count parity |
| **[`test_firmware_lut_parity.py`](file:///d:/AUV%20sonar/tests/test_firmware_lut_parity.py)** | `TestFirmwareLUTParity` | **13** | **STM32 C Firmware LUT Parity:**<br>• Quantization code boundaries within 12-bit range ($0\text{–}4095$)<br>• Exactly 8,000 half-words per profile header table<br>• **Bit-exact identity** ($0\text{ LSB}$ difference) between Python `src/waveform.py` output and C firmware headers in `outputs/headers/*.h`<br>• Macro definition consistency (`SAMPLE_RATE_HZ = 4000000`, `PULSE_DURATION_US = 2000`)<br>• Master header `sonar_profiles.h` consistency |

---

## 3. Key Verification Principles

### 1. Bit-Exact Firmware Parity
Every compile-ready C header table in `outputs/headers/` consumed by the STM32G474 firmware is parsed and compared against freshly generated Python waveforms. The test suite asserts that:
$$\max_{0 \le n < 8000} \left| \text{LUT}_{\text{C}}[n] - \text{LUT}_{\text{Python}}[n] \right| = 0$$

### 2. Machine-Precision Physics Cross-Validation
The Ainslie-McColm seawater absorption calculations in `src/profile_evaluator.py` are continuously checked against an independent reference implementation in `src/physics_reference.py`. Relative discrepancies must satisfy:
$$\frac{|\alpha_{\text{eval}} - \alpha_{\text{ref}}|}{\alpha_{\text{ref}}} < 1.0 \times 10^{-10}$$

### 3. State Machine Hysteresis & Debounce Guarantees
Tests simulate rapid potentiometer wiper noise ($\sigma = 0.02$) and step jumps to ensure:
- Single-ping transients never trigger a profile change ($N=2$ debounce).
- Directional hysteresis deadbands ($\pm 5\%$) eliminate boundary chattering.
- Profile changes only take effect at ping repetition boundaries ($20.0\text{ ms}$ PRI).
