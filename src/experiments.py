"""
Priority 1 Parameter Sweep Experiments & Figure Generator
SIH Problem 26058: AUV Adaptive Sonar Transmitter Digital Twin.

Executes:
  1. Range Sweep (10m to 200m)
  2. Noise Sensitivity Sweep (-20 dB to +20 dB)
  3. Environmental Sensitivity Sweep (Temperature, Salinity, Depth)
  4. Turbidity Sensitivity Heuristic (Clear, Moderate, High)

Generates the 7 required figures into outputs_matlab/plots/ and prints tabular reports.
"""

import os
from typing import List, Dict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .profile_evaluator import (
    EnvironmentalScenario,
    ProfilePerformanceMetrics,
    EvaluationDecision,
    evaluate_all_profiles,
    ainslie_mccolm_absorption,
    compute_mackenzie_sound_speed,
)


def run_range_sweep(ranges: List[float], mission_objective: str = "SURVEY") -> List[Dict]:
    """Executes a range sweep evaluating all profiles across distance."""
    results = []
    for r in ranges:
        scenario = EnvironmentalScenario(range_m=r)
        metrics, decision = evaluate_all_profiles(scenario, mission_objective=mission_objective)
        results.append({
            "range_m": r,
            "metrics": metrics,
            "decision": decision,
        })
    return results


def run_noise_sweep(noise_levels: List[float], range_m: float = 75.0) -> List[Dict]:
    """Executes a noise sensitivity sweep at fixed range."""
    results = []
    for n in noise_levels:
        scenario = EnvironmentalScenario(range_m=range_m, ambient_noise_db=n)
        metrics, decision = evaluate_all_profiles(scenario, mission_objective="SURVEY")
        results.append({
            "noise_db": n,
            "metrics": metrics,
            "decision": decision,
        })
    return results


def run_environmental_sweep() -> Dict:
    """Executes sensitivity analysis over Temperature, Salinity, and Depth."""
    temps = np.linspace(-2.0, 35.0, 20)
    salinities = np.linspace(0.0, 40.0, 20)
    depths = np.linspace(0.0, 500.0, 20)

    # 1. Temperature sensitivity (S=35, D=50)
    c_vs_t = [compute_mackenzie_sound_speed(t, 35.0, 50.0) for t in temps]
    alpha_low_t = [ainslie_mccolm_absorption(160.0, t, 35.0, 50.0) for t in temps]
    alpha_high_t = [ainslie_mccolm_absorption(425.0, t, 35.0, 50.0) for t in temps]

    # 2. Salinity sensitivity (T=20, D=50)
    c_vs_s = [compute_mackenzie_sound_speed(20.0, s, 50.0) for s in salinities]
    alpha_low_s = [ainslie_mccolm_absorption(160.0, 20.0, s, 50.0) for s in salinities]
    alpha_high_s = [ainslie_mccolm_absorption(425.0, 20.0, s, 50.0) for s in salinities]

    # 3. Depth sensitivity (T=20, S=35)
    c_vs_d = [compute_mackenzie_sound_speed(20.0, 35.0, d) for d in depths]
    alpha_low_d = [ainslie_mccolm_absorption(160.0, 20.0, 35.0, d) for d in depths]
    alpha_high_d = [ainslie_mccolm_absorption(425.0, 20.0, 35.0, d) for d in depths]

    return {
        "temps": temps, "c_vs_t": c_vs_t, "alpha_low_t": alpha_low_t, "alpha_high_t": alpha_high_t,
        "salinities": salinities, "c_vs_s": c_vs_s, "alpha_low_s": alpha_low_s, "alpha_high_s": alpha_high_s,
        "depths": depths, "c_vs_d": c_vs_d, "alpha_low_d": alpha_low_d, "alpha_high_d": alpha_high_d,
    }


def generate_all_experiment_plots(output_dir: str) -> List[str]:
    """Generates all 7 required figures and saves them into output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []

    # Colors for profiles
    c_low = "#d35400"
    c_bal = "#2980b9"
    c_high = "#27ae60"

    # --------------------------------------------------------------------------
    # Figure 1: Attenuation vs Frequency
    # --------------------------------------------------------------------------
    fig1, ax1 = plt.subplots(figsize=(9, 5), dpi=150)
    f_axis_khz = np.linspace(80.0, 520.0, 300)
    alpha_clear = [ainslie_mccolm_absorption(f, 20.0, 35.0, 50.0) for f in f_axis_khz]
    # Sensitivity heuristic
    alpha_turb_mod = [alpha_clear[i] + 35.0 * 0.30 * ((f / 300.0) ** 2) for i, f in enumerate(f_axis_khz)]
    alpha_turb_high = [alpha_clear[i] + 35.0 * 0.80 * ((f / 300.0) ** 2) for i, f in enumerate(f_axis_khz)]

    ax1.plot(f_axis_khz, alpha_clear, "k-", lw=2.0, label="Baseline Clear Seawater (T=20°C, S=35, D=50m)")
    ax1.plot(f_axis_khz, alpha_turb_mod, "k--", lw=1.2, alpha=0.7, label="Turbidity Heuristic: Moderate (turb=30)")
    ax1.plot(f_axis_khz, alpha_turb_high, "k:", lw=1.2, alpha=0.7, label="Turbidity Heuristic: High (turb=80)")

    # Mark 5 discrete frequency points for each profile
    p_low_pts = np.linspace(100.0, 220.0, 5)
    p_bal_pts = np.linspace(200.0, 400.0, 5)
    p_high_pts = np.linspace(350.0, 500.0, 5)

    ax1.scatter(p_low_pts, [ainslie_mccolm_absorption(f, 20.0, 35.0, 50.0) for f in p_low_pts],
                color=c_low, s=50, zorder=5, label="LOW_FREQUENCY (100-220 kHz 5-pt)")
    ax1.scatter(p_bal_pts, [ainslie_mccolm_absorption(f, 20.0, 35.0, 50.0) for f in p_bal_pts],
                color=c_bal, s=50, zorder=5, label="BALANCED (200-400 kHz 5-pt)")
    ax1.scatter(p_high_pts, [ainslie_mccolm_absorption(f, 20.0, 35.0, 50.0) for f in p_high_pts],
                color=c_high, s=50, zorder=5, label="HIGH_FREQUENCY (350-500 kHz 5-pt)")

    ax1.axvspan(100, 220, color=c_low, alpha=0.08)
    ax1.axvspan(200, 400, color=c_bal, alpha=0.08)
    ax1.axvspan(350, 500, color=c_high, alpha=0.08)

    ax1.set_xlabel("Frequency (kHz)")
    ax1.set_ylabel("Attenuation α (dB/km)")
    ax1.set_title("Fig 1: Frequency-Dependent Seawater Attenuation (Ainslie-McColm 1998 & 5-Pt Sampling)")
    ax1.grid(True, ls="--", alpha=0.6)
    ax1.legend(loc="upper left", fontsize=8)
    fig1.tight_layout()
    p1 = os.path.join(output_dir, "exp01_attenuation_vs_frequency.png")
    fig1.savefig(p1)
    plt.close(fig1)
    generated_files.append(p1)

    # --------------------------------------------------------------------------
    # Figure 2: Predicted Propagation Performance vs Range
    # --------------------------------------------------------------------------
    fig2, ax2 = plt.subplots(figsize=(9, 5), dpi=150)
    ranges_dense = np.linspace(5.0, 200.0, 80)
    m_low_r, m_bal_r, m_high_r = [], [], []

    for r in ranges_dense:
        m, _ = evaluate_all_profiles(EnvironmentalScenario(range_m=r))
        m_low_r.append(m[0].relative_margin_db)
        m_bal_r.append(m[1].relative_margin_db)
        m_high_r.append(m[2].relative_margin_db)

    ax2.plot(ranges_dense, m_low_r, color=c_low, lw=2.0, label="LOW_FREQUENCY (100-220 kHz)")
    ax2.plot(ranges_dense, m_bal_r, color=c_bal, lw=2.0, label="BALANCED (200-400 kHz)")
    ax2.plot(ranges_dense, m_high_r, color=c_high, lw=2.0, label="HIGH_FREQUENCY (350-500 kHz)")

    ax2.axhline(-65.0, color="r", ls="--", lw=1.5, label="Viability Threshold (-65 dB policy assumption)")
    ax2.set_xlabel("Target Range R (meters)")
    ax2.set_ylabel("Relative Propagation Margin (dB)")
    ax2.set_title("Fig 2: Modeled One-Way Propagation Margin vs Range (Policy Viability Limits)")
    ax2.grid(True, ls="--", alpha=0.6)
    ax2.legend(loc="upper right", fontsize=9)
    fig2.tight_layout()
    p2 = os.path.join(output_dir, "exp02_propagation_vs_range.png")
    fig2.savefig(p2)
    plt.close(fig2)
    generated_files.append(p2)

    # --------------------------------------------------------------------------
    # Figure 3: Theoretical Range Resolution Comparison
    # --------------------------------------------------------------------------
    fig3, ax3 = plt.subplots(figsize=(8, 4.5), dpi=150)
    names = ["LOW_FREQUENCY\n(B = 120 kHz)", "BALANCED\n(B = 200 kHz)", "HIGH_FREQUENCY\n(B = 150 kHz)"]
    resolutions = [6.25, 3.75, 5.00]
    bars = ax3.bar(names, resolutions, color=[c_low, c_bal, c_high], width=0.5, edgecolor="k")

    for b, res in zip(bars, resolutions):
        ax3.text(b.get_x() + b.get_width() / 2.0, res + 0.15, f"{res:.2f} mm",
                 ha="center", va="bottom", fontweight="bold")

    ax3.set_ylabel("Idealized Range Resolution ΔR = c / (2B) (mm)")
    ax3.set_ylim(0, 8.0)
    ax3.set_title("Fig 3: Theoretical Bandwidth-Based Range Resolution (c = 1500 m/s)")
    ax3.grid(axis="y", ls="--", alpha=0.6)
    fig3.tight_layout()
    p3 = os.path.join(output_dir, "exp03_theoretical_range_resolution.png")
    fig3.savefig(p3)
    plt.close(fig3)
    generated_files.append(p3)

    # --------------------------------------------------------------------------
    # Figure 4: Relative Theoretical Directivity Comparison
    # --------------------------------------------------------------------------
    fig4, ax4 = plt.subplots(figsize=(8, 4.5), dpi=150)
    dir_names = ["LOW_FREQUENCY\n(fc = 160 kHz)", "BALANCED\n(fc = 300 kHz)", "HIGH_FREQUENCY\n(fc = 425 kHz)"]
    directivity = [0.533, 1.000, 1.417]
    bars4 = ax4.bar(dir_names, directivity, color=[c_low, c_bal, c_high], width=0.5, edgecolor="k")

    for b, d in zip(bars4, directivity):
        ax4.text(b.get_x() + b.get_width() / 2.0, d + 0.04, f"{d:.3f}x",
                 ha="center", va="bottom", fontweight="bold")

    ax4.axhline(1.0, color="gray", ls="--", lw=1.0)
    ax4.set_ylabel("Relative Directivity Factor (fc / 300 kHz)")
    ax4.set_ylim(0, 1.8)
    ax4.set_title("Fig 4: Relative Theoretical Directivity (Fixed Physical Aperture Assumption)")
    ax4.text(0.5, -0.15, "Note: Relative theoretical metric (θ ∝ c / (f·D)). Transducer beam patterns are NOT currently modeled.",
             transform=ax4.transAxes, ha="center", fontsize=8, style="italic")
    ax4.grid(axis="y", ls="--", alpha=0.6)
    fig4.tight_layout()
    p4 = os.path.join(output_dir, "exp04_relative_directivity_comparison.png")
    fig4.savefig(p4)
    plt.close(fig4)
    generated_files.append(p4)

    # --------------------------------------------------------------------------
    # Figure 5: Profile Winner vs Range (Survey vs Directivity Objectives)
    # --------------------------------------------------------------------------
    fig5, (ax5a, ax5b) = plt.subplots(2, 1, figsize=(9, 6), sharex=True, dpi=150)
    ranges_test = np.linspace(10.0, 200.0, 100)
    cand_survey = []
    cand_directivity = []

    for r in ranges_test:
        _, d_surv = evaluate_all_profiles(EnvironmentalScenario(range_m=r), mission_objective="SURVEY")
        _, d_dir = evaluate_all_profiles(EnvironmentalScenario(range_m=r), mission_objective="DIRECTIVITY")
        cand_survey.append(d_surv.candidate_profile_id)
        cand_directivity.append(d_dir.candidate_profile_id)

    ax5a.step(ranges_test, cand_survey, where="post", color=c_bal, lw=2.0)
    ax5a.set_yticks([1, 2, 3])
    ax5a.set_yticklabels(["LOW_FREQ", "BALANCED", "HIGH_FREQ"])
    ax5a.set_ylim(0.5, 3.5)
    ax5a.set_ylabel("Selected Profile")
    ax5a.set_title("Fig 5a: Profile Selection vs Range under SURVEY Objective (Resolution Priority)")
    ax5a.grid(True, ls="--", alpha=0.6)

    ax5b.step(ranges_test, cand_directivity, where="post", color=c_high, lw=2.0)
    ax5b.set_yticks([1, 2, 3])
    ax5b.set_yticklabels(["LOW_FREQ", "BALANCED", "HIGH_FREQ"])
    ax5b.set_ylim(0.5, 3.5)
    ax5b.set_xlabel("Target Range R (meters)")
    ax5b.set_ylabel("Selected Profile")
    ax5b.set_title("Fig 5b: Profile Selection vs Range under DIRECTIVITY Objective (Narrow-Beam Priority)")
    ax5b.grid(True, ls="--", alpha=0.6)
    fig5.tight_layout()
    p5 = os.path.join(output_dir, "exp05_profile_winner_vs_range.png")
    fig5.savefig(p5)
    plt.close(fig5)
    generated_files.append(p5)

    # --------------------------------------------------------------------------
    # Figure 6: Best-Profile Performance Margin & Dual Confidence Metrics vs Range
    # --------------------------------------------------------------------------
    fig6, ax6 = plt.subplots(figsize=(9, 4.8), dpi=150)
    margin_above_survey = []
    viab_conf_survey = []
    sel_conf_survey = []

    for r in ranges_dense:
        _, d = evaluate_all_profiles(EnvironmentalScenario(range_m=r), mission_objective="SURVEY")
        margin_above_survey.append(d.margin_above_viability_db)
        viab_conf_survey.append(d.viability_confidence)
        sel_conf_survey.append(d.selection_confidence)

    ax6.plot(ranges_dense, margin_above_survey, "b-", lw=1.8, label="Margin Above Viability (dB)")
    ax6.axhline(0.0, color="r", ls="--", lw=1.2, label="Viability Limit (Margin = 0 dB)")
    ax6.axhline(15.0, color="g", ls=":", lw=1.2, label="Full Viability Margin (+15 dB)")

    ax6_r = ax6.twinx()
    ax6_r.plot(ranges_dense, viab_conf_survey, "m-.", lw=1.5, label="viability_confidence [0, 1]")
    ax6_r.plot(ranges_dense, sel_conf_survey, "c--", lw=1.5, label="selection_confidence [0, 1]")
    ax6_r.set_ylabel("Confidence Metrics (0.0 to 1.0)")
    ax6_r.set_ylim(-0.05, 1.1)

    ax6.set_xlabel("Target Range R (meters)")
    ax6.set_ylabel("Viability Margin (dB)", color="b")
    ax6.set_title("Fig 6: Candidate Margin & Dual Confidence Metrics (Viability & Selection) vs Range")
    ax6.grid(True, ls="--", alpha=0.6)

    # Combine legends
    lines_1, labels_1 = ax6.get_legend_handles_labels()
    lines_2, labels_2 = ax6_r.get_legend_handles_labels()
    ax6.legend(lines_1 + lines_2, labels_1 + labels_2, loc="lower left", fontsize=8)

    fig6.tight_layout()
    p6 = os.path.join(output_dir, "exp06_performance_margin_vs_range.png")
    fig6.savefig(p6)
    plt.close(fig6)
    generated_files.append(p6)

    # --------------------------------------------------------------------------
    # Figure 7: Environmental Sensitivity Summary
    # --------------------------------------------------------------------------
    env_data = run_environmental_sweep()
    fig7, (ax7a, ax7b, ax7c) = plt.subplots(1, 3, figsize=(14, 4.5), dpi=150)

    # Subplot A: Temperature impact
    ax7a.plot(env_data["temps"], env_data["c_vs_t"], "b-", lw=1.5, label="Sound Speed c (m/s)")
    ax7a.set_xlabel("Temperature (°C)")
    ax7a.set_ylabel("Sound Speed (m/s)", color="b")
    ax7a_r = ax7a.twinx()
    ax7a_r.plot(env_data["temps"], env_data["alpha_high_t"], "r--", lw=1.2, label="α @ 425 kHz (dB/km)")
    ax7a_r.set_ylabel("Attenuation (dB/km)", color="r")
    ax7a.set_title("Temperature Sensitivity")
    ax7a.grid(True, ls="--", alpha=0.6)

    # Subplot B: Salinity impact
    ax7b.plot(env_data["salinities"], env_data["c_vs_s"], "b-", lw=1.5)
    ax7b.set_xlabel("Salinity (PSU)")
    ax7b.set_ylabel("Sound Speed (m/s)", color="b")
    ax7b_r = ax7b.twinx()
    ax7b_r.plot(env_data["salinities"], env_data["alpha_high_s"], "r--", lw=1.2)
    ax7b_r.set_ylabel("Attenuation (dB/km)", color="r")
    ax7b.set_title("Salinity Sensitivity")
    ax7b.grid(True, ls="--", alpha=0.6)

    # Subplot C: Depth impact
    ax7c.plot(env_data["depths"], env_data["c_vs_d"], "b-", lw=1.5)
    ax7c.set_xlabel("Depth (m)")
    ax7c.set_ylabel("Sound Speed (m/s)", color="b")
    ax7c_r = ax7c.twinx()
    ax7c_r.plot(env_data["depths"], env_data["alpha_high_d"], "r--", lw=1.2)
    ax7c_r.set_ylabel("Attenuation (dB/km)", color="r")
    ax7c.set_title("Depth Sensitivity")
    ax7c.grid(True, ls="--", alpha=0.6)

    fig7.suptitle("Fig 7: Environmental Parameter Sensitivity Analysis (Mackenzie 1981 & Ainslie-McColm 1998)", fontsize=11, fontweight="bold")
    fig7.tight_layout()
    p7 = os.path.join(output_dir, "exp07_environmental_sensitivity_summary.png")
    fig7.savefig(p7)
    plt.close(fig7)
    generated_files.append(p7)

    return generated_files


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(root, "outputs_matlab", "plots")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 78)
    print("  EXECUTING PRIORITY 1 PARAMETER SWEEP EXPERIMENTS")
    print("=" * 78)

    # 1. Range Sweep Analysis
    print("\n[*] Experiment 1: Range Sweep Analysis (SURVEY Objective)...")
    ranges = [10.0, 25.0, 50.0, 75.0, 100.0, 125.0, 150.0, 175.0, 200.0]
    range_results = run_range_sweep(ranges, mission_objective="SURVEY")
    print(f"  {'Range':<8} {'LOW Margin':<12} {'BAL Margin':<12} {'HIGH Margin':<12} {'Selected Profile':<16} {'Viab Conf':<11} {'Mission Conf'}")
    print("  " + "-" * 82)
    for res in range_results:
        r = res["range_m"]
        m = res["metrics"]
        d = res["decision"]
        print(f"  {r:5.1f} m  {m[0].relative_margin_db:7.2f} dB   {m[1].relative_margin_db:7.2f} dB   {m[2].relative_margin_db:7.2f} dB   {d.candidate_name:<16} {d.viability_confidence:5.2f}       {d.selection_confidence:5.2f}")

    # 2. Noise Sensitivity Sweep
    print("\n[*] Experiment 2: Relative Noise Penalty Sensitivity Sweep (at Range = 75 m)...")
    noise_levels = [-20.0, -10.0, 0.0, 10.0, 20.0]
    noise_results = run_noise_sweep(noise_levels, range_m=75.0)
    print(f"  {'Noise Penalty':<16} {'LOW Viable':<12} {'BAL Viable':<12} {'HIGH Viable':<12} {'Selected Profile'}")
    print("  " + "-" * 70)
    for res in noise_results:
        n = res["noise_db"]
        m = res["metrics"]
        d = res["decision"]
        print(f"  {n:7.1f} dB        {str(m[0].is_viable):<12} {str(m[1].is_viable):<12} {str(m[2].is_viable):<12} {d.candidate_name}")

    # 3. Generate 7 Engineering Figures
    print("\n[*] Generating the 7 Required Engineering Visualizations...")
    generated_plots = generate_all_experiment_plots(output_dir)
    for p in generated_plots:
        print(f"  [+] Generated: {p}")

    print("\n" + "=" * 78)
    print("  ALL 7 PRIORITY 1 EXPERIMENT FIGURES GENERATED")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
