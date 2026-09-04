"""
src/physics_reference.py
Independent Reference Implementation and Canonical Physics Diagnostic
for Ainslie-McColm (1998) Acoustic Absorption.

References:
- Ainslie, M. A., & McColm, J. G. (1998). "A simplified formula for viscous
  and chemical absorption in sea water." The Journal of the Acoustical Society
  of America, 103(3), 1671-1672.
- National Physical Laboratory (NPL) Technical Guide:
  "Calculation of absorption of sound in seawater"
"""

import math
from typing import Dict, List, NamedTuple, Tuple
import numpy as np

from src.profile_evaluator import ainslie_mccolm_absorption as production_absorption


class AbsorptionComponents(NamedTuple):
    frequency_hz: float
    frequency_khz: float
    boric_acid_db_km: float
    magnesium_sulfate_db_km: float
    pure_water_db_km: float
    total_db_km: float
    total_db_m: float
    source_function: str


def independent_ainslie_mccolm_reference(
    f_khz: float,
    temperature_c: float = 20.0,
    salinity_psu: float = 35.0,
    depth_m: float = 50.0,
    pH: float = 8.0,
) -> Tuple[float, float, float, float]:
    """
    Independent reference implementation of Ainslie & McColm (1998).
    
    Formula:
      alpha(f) = Boric + MgSO4 + PureWater  [dB/km]
      
      Boric Acid (B(OH)3):
        f1 = 0.78 * sqrt(S/35) * exp(T/26)  [kHz]
        A1 = 0.106 * exp((pH - 8) / 0.56)  [dB/(km*kHz)]
        Boric = (A1 * f1 * f^2) / (f1^2 + f^2)
        
      Magnesium Sulfate (MgSO4):
        f2 = 42 * exp(T/17)  [kHz]
        A2 = 0.52 * (1 + T/43) * (S/35)  [dB/(km*kHz)]
        P2 = exp(-D_km / 6) = exp(-depth_m / 6000)  [Hydrostatic depth factor]
        MgSO4 = (A2 * P2 * f2 * f^2) / (f2^2 + f^2)
        
      Pure Water:
        A3 = 0.00049 * exp(-(T/27 + D_km/17)) = 0.00049 * exp(-T/27 - depth_m/17000)
        PureWater = A3 * f^2
        
    Returns:
      (boric_db_km, mgso4_db_km, pure_water_db_km, total_db_km)
    """
    f = float(f_khz)
    T = float(temperature_c)
    S = float(salinity_psu)
    D_m = float(depth_m)
    D_km = D_m / 1000.0

    # 1. Boric acid relaxation
    f1 = 0.78 * math.sqrt(S / 35.0) * math.exp(T / 26.0)
    A1 = 0.106 * math.exp((pH - 8.0) / 0.56)
    f_sq = f ** 2
    boric = (A1 * f1 * f_sq) / (f1 ** 2 + f_sq)

    # 2. Magnesium sulfate relaxation (including hydrostatic pressure attenuation)
    f2 = 42.0 * math.exp(T / 17.0)
    A2 = 0.52 * (1.0 + T / 43.0) * (S / 35.0)
    P2 = math.exp(-D_km / 6.0)
    mgso4 = (A2 * P2 * f2 * f_sq) / (f2 ** 2 + f_sq)

    # 3. Pure water viscous absorption
    A3 = 0.00049 * math.exp(-(T / 27.0 + D_km / 17.0))
    pure_water = A3 * f_sq

    total = boric + mgso4 + pure_water
    return boric, mgso4, pure_water, total


def evaluate_production_components(
    f_khz: float,
    temperature_c: float = 20.0,
    salinity_psu: float = 35.0,
    depth_m: float = 50.0,
) -> AbsorptionComponents:
    """
    Decomposes the exact production implementation in src/profile_evaluator.py
    into its three constituent physical terms.
    """
    f = float(f_khz)
    T = float(temperature_c)
    S = float(salinity_psu)
    D = float(depth_m)

    f1 = 0.78 * np.sqrt(S / 35.0) * np.exp(T / 26.0)
    A1 = 0.106 * np.exp((T - 20.0) / 27.0)
    f2 = 42.0 * np.exp(T / 17.0)
    A2 = 0.52 * (1.0 + T / 43.0) * (S / 35.0)
    P2 = np.exp(-D / 6000.0)
    A3 = 0.00049 * np.exp(-(T / 27.0) - (D / 17000.0))

    f_sq = f ** 2
    boric = float((A1 * f1 * f_sq) / (f1 ** 2 + f_sq))
    mgso4 = float((A2 * P2 * f2 * f_sq) / (f2 ** 2 + f_sq))
    pure_water = float(A3 * f_sq)
    total_db_km = float(boric + mgso4 + pure_water)
    total_db_m = total_db_km / 1000.0

    return AbsorptionComponents(
        frequency_hz=f * 1000.0,
        frequency_khz=f,
        boric_acid_db_km=boric,
        magnesium_sulfate_db_km=mgso4,
        pure_water_db_km=pure_water,
        total_db_km=total_db_km,
        total_db_m=total_db_m,
        source_function="src/profile_evaluator.py::ainslie_mccolm_absorption",
    )


def run_canonical_physics_diagnostic(
    temperature_c: float = 20.0,
    salinity_psu: float = 35.0,
    depth_m: float = 50.0,
    pH: float = 8.0,
) -> Dict[str, Dict]:
    """
    Executes the canonical diagnostic across all 3 profiles and 5 sampling points each.
    Prints the formatted diagnostic report.
    """
    profiles = {
        "LOW_FREQUENCY": np.linspace(100.0, 220.0, 5),
        "BALANCED": np.linspace(200.0, 400.0, 5),
        "HIGH_FREQUENCY": np.linspace(350.0, 500.0, 5),
    }

    results = {}

    print("\n" + "=" * 80)
    print("  CANONICAL UNDERWATER ACOUSTIC ABSORPTION DIAGNOSTIC")
    print("  Model: Ainslie & McColm (1998)")
    print(f"  Environmental Baseline: T={temperature_c}°C, S={salinity_psu} PSU, D={depth_m} m, pH={pH}")
    print("=" * 80)

    for profile_name, freqs in profiles.items():
        results[profile_name] = {"samples": [], "mean_db_km": 0.0, "mean_db_m": 0.0}
        print(f"\n================================================")
        print(f"PROFILE: {profile_name}")
        print("================================================")

        sample_totals = []
        for f_k in freqs:
            comp = evaluate_production_components(f_k, temperature_c, salinity_psu, depth_m)
            sample_totals.append(comp.total_db_km)
            results[profile_name]["samples"].append(comp)

            print(f"Frequency: {comp.frequency_hz:,.1f} Hz")
            print(f"Frequency: {comp.frequency_khz:.1f} kHz")
            print(f"\nEnvironmental Parameters:")
            print(f"Temperature: {temperature_c:.1f} °C")
            print(f"Salinity: {salinity_psu:.1f} PSU")
            print(f"Depth: {depth_m:.1f} m")
            print(f"pH: {pH:.1f}")
            print(f"Pressure: Hydrostatic equivalent (depth D={depth_m} m, P2={np.exp(-depth_m/6000.0):.6f})")
            print(f"\nAinslie-McColm Components:")
            print(f"Boric Acid Contribution: {comp.boric_acid_db_km:.4f} dB/km")
            print(f"Magnesium Sulfate Contribution: {comp.magnesium_sulfate_db_km:.4f} dB/km")
            print(f"Pure Water Contribution: {comp.pure_water_db_km:.4f} dB/km")
            print(f"\nTotal Absorption:")
            print(f"{comp.total_db_km:.4f} dB/km")
            print(f"\nConverted Value:")
            print(f"{comp.total_db_m:.6f} dB/m")
            print(f"\nSource Function:")
            print(f"{comp.source_function}")
            print("-" * 48)

        mean_db_km = float(np.mean(sample_totals))
        mean_db_m = mean_db_km / 1000.0
        results[profile_name]["mean_db_km"] = mean_db_km
        results[profile_name]["mean_db_m"] = mean_db_m

        print(f"CANONICAL MEAN ATTENUATION ({profile_name}):")
        print(f"  {mean_db_km:.4f} dB/km  ({mean_db_m:.6f} dB/m)")

    return results


def run_cross_validation_table(
    tolerance_pct: float = 1e-6,
    temperature_c: float = 20.0,
    salinity_psu: float = 35.0,
    depth_m: float = 50.0,
    pH: float = 8.0,
) -> List[Dict]:
    """
    Compares production implementation against independent reference implementation.
    Documents difference and evaluates pass/fail within strict numerical tolerance.
    """
    profiles = {
        "LOW_FREQUENCY": np.linspace(100.0, 220.0, 5),
        "BALANCED": np.linspace(200.0, 400.0, 5),
        "HIGH_FREQUENCY": np.linspace(350.0, 500.0, 5),
    }

    all_freqs = []
    for freqs in profiles.values():
        for f in freqs:
            if f not in all_freqs:
                all_freqs.append(f)
    all_freqs.sort()

    table_data = []

    print("\n" + "=" * 95)
    print("  INDEPENDENT CROSS-VALIDATION TABLE (NUMERICAL PRECISION)")
    print("  Production: src/profile_evaluator.py::ainslie_mccolm_absorption")
    print("  Reference:  src/physics_reference.py::independent_ainslie_mccolm_reference")
    print(f"  Numerical Tolerance: {tolerance_pct:.1e}% relative difference")
    print("=" * 95)
    print(f"{'Frequency (kHz)':<16} | {'Production (dB/km)':<20} | {'Reference (dB/km)':<20} | {'Diff (dB/km)':<14} | {'Diff (%)':<10} | {'Status':<6}")
    print("-" * 95)

    for f_k in all_freqs:
        prod_val = production_absorption(f_k, temperature_c, salinity_psu, depth_m)
        _, _, _, ref_val = independent_ainslie_mccolm_reference(f_k, temperature_c, salinity_psu, depth_m, pH)

        abs_diff = abs(prod_val - ref_val)
        pct_diff = (abs_diff / ref_val) * 100.0 if ref_val > 0 else 0.0
        passed = pct_diff <= tolerance_pct

        status = "PASS" if passed else "FAIL"
        print(f"{f_k:<16.1f} | {prod_val:<20.6f} | {ref_val:<20.6f} | {abs_diff:<14.2e} | {pct_diff:<10.2e} | {status:<6}")

        table_data.append({
            "frequency_khz": f_k,
            "production_db_km": prod_val,
            "reference_db_km": ref_val,
            "diff_db_km": abs_diff,
            "diff_pct": pct_diff,
            "passed": passed,
        })

    print("-" * 95)
    all_passed = all(row["passed"] for row in table_data)
    print(f"Summary: {'ALL FREQUENCIES PASSED with machine precision parity.' if all_passed else 'SOME CHECKS FAILED'}")
    return table_data


def run_depth_sweep_matrix(
    depths: List[float] = [10.0, 50.0, 100.0, 200.0, 300.0],
    temperature_c: float = 20.0,
    salinity_psu: float = 35.0,
    pH: float = 8.0,
) -> Dict[str, List[Dict]]:
    """
    Computes before vs after and production vs reference across the full operational depth envelope.
    """
    profiles = {
        "LOW_FREQUENCY": np.linspace(100.0, 220.0, 5),
        "BALANCED": np.linspace(200.0, 400.0, 5),
        "HIGH_FREQUENCY": np.linspace(350.0, 500.0, 5),
    }

    depth_data = {}
    for prof_name, freqs in profiles.items():
        depth_data[prof_name] = []
        for d in depths:
            p2 = math.exp(-d / 6000.0)
            prod_alphas = [production_absorption(f, temperature_c, salinity_psu, d) for f in freqs]
            ref_alphas = [independent_ainslie_mccolm_reference(f, temperature_c, salinity_psu, d, pH)[3] for f in freqs]
            
            prod_mean = float(np.mean(prod_alphas))
            ref_mean = float(np.mean(ref_alphas))
            abs_diff = abs(prod_mean - ref_mean)
            rel_diff_pct = (abs_diff / ref_mean) * 100.0 if ref_mean > 0 else 0.0
            
            # Transmission loss at R=50m and R=200m
            tl_50 = 20.0 * math.log10(50.0) + prod_mean * 0.05
            tl_200 = 20.0 * math.log10(200.0) + prod_mean * 0.20

            depth_data[prof_name].append({
                "depth_m": d,
                "p2_factor": p2,
                "p2_reduction_pct": (1.0 - p2) * 100.0,
                "production_mean_db_km": prod_mean,
                "reference_mean_db_km": ref_mean,
                "abs_diff_db_km": abs_diff,
                "rel_diff_pct": rel_diff_pct,
                "tl_50m_db": tl_50,
                "tl_200m_db": tl_200,
            })
    return depth_data


if __name__ == "__main__":
    run_canonical_physics_diagnostic()
    run_cross_validation_table()
