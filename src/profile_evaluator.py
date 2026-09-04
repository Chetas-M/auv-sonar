"""
Profile Performance Evaluation & Physically Justified Selection Module
SIH Problem 26058: Low-Power Adaptive Sonar Transmitter Digital Twin.

Evaluates frequency-dependent acoustic absorption (Ainslie-McColm 1998),
simplified relative transmission loss, theoretical range resolution,
and relative theoretical directivity for all three transmission profiles.

Implements two-tier selection:
  1. Propagation Viability Filter (Relative Margin >= Viability Threshold)
  2. Mission Objective Selector (Survey -> BALANCED, Directivity -> HIGH_FREQUENCY, Fallback -> LOW_FREQUENCY)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import numpy as np

from .profiles import ProfileType, BAND_PROFILES


@dataclass
class EnvironmentalScenario:
    """Environmental parameters for simulated propagation."""
    range_m: float = 50.0
    depth_m: float = 50.0
    temperature_c: float = 20.0
    salinity_psu: float = 35.0
    pH: float = 8.0                  # Seawater pH (Ainslie & McColm 1998 baseline: 8.0)
    turbidity: float = 0.0           # Optional sensitivity analysis heuristic
    noise_penalty_db: float = 0.0    # Normalized relative noise penalty (dB)
    ambient_noise_db: float = 0.0    # Backward compatibility alias

    def __post_init__(self):
        # Support either noise_penalty_db or ambient_noise_db
        if self.ambient_noise_db != 0.0 and self.noise_penalty_db == 0.0:
            self.noise_penalty_db = self.ambient_noise_db
        elif self.noise_penalty_db != 0.0 and self.ambient_noise_db == 0.0:
            self.ambient_noise_db = self.noise_penalty_db


@dataclass
class ProfilePerformanceMetrics:
    """Individual, unhidden performance metrics for a single transmission profile."""
    profile_id: int
    name: str
    f_start_hz: float
    f_end_hz: float
    f_center_hz: float
    bandwidth_hz: float
    f_points_khz: List[float]
    alpha_points_db_km: List[float]
    alpha_band_db_km: float
    transmission_loss_db: float
    relative_margin_db: float
    is_viable: bool
    viability_threshold_db: float
    range_resolution_mm: float
    relative_directivity: float
    sound_speed_m_s: float
    range_m: float
    assumptions: List[str] = field(default_factory=list)


@dataclass
class EvaluationDecision:
    """Result of profile evaluation and mission objective selection."""
    candidate_profile_id: int
    candidate_name: str
    mission_objective: str
    selection_rationale: str
    viability_confidence: float       # How comfortably viable is the candidate above the threshold
    selection_confidence: float       # How clearly separated the winner is under the mission objective
    profile_selection_confidence: float # Canonical confidence metric (viability confidence)
    margin_above_viability_db: float
    all_viable: List[bool]
    range_m: float


def compute_mackenzie_sound_speed(temperature_c: float, salinity_psu: float, depth_m: float) -> float:
    """Computes seawater sound speed using the Mackenzie (1981) 9-term equation."""
    T = float(temperature_c)
    S = float(salinity_psu)
    D = float(depth_m)
    return (
        1448.96
        + 4.591 * T
        - 0.05304 * (T ** 2)
        + 0.0002374 * (T ** 3)
        + 1.340 * (S - 35.0)
        + 0.0163 * D
        + 0.0001675 * (D ** 2)
        - 0.01025 * T * (S - 35.0)
        - 0.0000007139 * T * (D ** 3)
    )


def ainslie_mccolm_absorption(
    f_khz: float,
    temperature_c: float,
    salinity_psu: float,
    depth_m: float,
    pH: float = 8.0,
) -> float:
    """
    Computes chemical relaxation and viscous absorption in seawater (dB/km)
    using the published Ainslie & McColm (1998) model.
    
    Constituent Physical Terms:
      1. Boric Acid relaxation (B(OH)3):
         f1 = 0.78 * sqrt(S/35) * exp(T/26)              [kHz]
         A1 = 0.106 * exp((pH - 8)/0.56)                 [dB/(km*kHz)]
         Boric = (A1 * f1 * f^2) / (f1^2 + f^2)
         
      2. Magnesium Sulfate relaxation (MgSO4):
         f2 = 42.0 * exp(T/17)                           [kHz]
         A2 = 0.52 * (1 + T/43) * (S/35)                 [dB/(km*kHz)]
         P2 = exp(-D_km / 6) = exp(-depth_m / 6000.0)    [Hydrostatic pressure reduction factor]
         MgSO4 = (A2 * P2 * f2 * f^2) / (f2^2 + f^2)
         
      3. Pure Water viscous absorption:
         A3 = 0.00049 * exp(-(T/27) - (depth_m/17000.0)) [dB/(km*kHz^2)]
         PureWater = A3 * f^2
         
    Units:
      f_khz: Frequency in kilohertz (kHz)
      temperature_c: Water temperature in degrees Celsius (C)
      salinity_psu: Practical Salinity Units (PSU or ppt)
      depth_m: Water depth in metres (m)
      pH: Seawater acidity/alkalinity (standard open ocean pH = 8.0)
      returns: Total absorption coefficient in dB/km
    """
    T = float(temperature_c)
    S = float(salinity_psu)
    D = float(depth_m)
    ph = float(pH)

    # Boric acid relaxation (published Ainslie & McColm 1998 formula with pH dependence)
    f1 = 0.78 * np.sqrt(S / 35.0) * np.exp(T / 26.0)
    A1 = 0.106 * np.exp((ph - 8.0) / 0.56)

    # Magnesium sulfate relaxation (including hydrostatic pressure correction factor P2)
    # D enters in metres, so D_km / 6.0 = D / 6000.0
    f2 = 42.0 * np.exp(T / 17.0)
    A2 = 0.52 * (1.0 + T / 43.0) * (S / 35.0)
    P2 = np.exp(-D / 6000.0)

    # Pure water viscous absorption (D enters in metres, so D_km / 17.0 = D / 17000.0)
    A3 = 0.00049 * np.exp(-(T / 27.0) - (D / 17000.0))

    f_sq = f_khz ** 2
    alpha = (A1 * f1 * f_sq) / (f1 ** 2 + f_sq) + (A2 * P2 * f2 * f_sq) / (f2 ** 2 + f_sq) + A3 * f_sq
    return float(alpha)



def evaluate_single_profile(
    profile_id: int,
    name: str,
    f_start_hz: float,
    f_end_hz: float,
    bandwidth_hz: float,
    scenario: EnvironmentalScenario,
    viability_threshold_db: float = -65.0,
) -> ProfilePerformanceMetrics:
    """Evaluates a single transmission profile across 5 discrete frequency points."""
    c = compute_mackenzie_sound_speed(scenario.temperature_c, scenario.salinity_psu, scenario.depth_m)
    f_center = (f_start_hz + f_end_hz) / 2.0

    # 5 evenly spaced discrete frequency points across the active band
    f_pts_hz = np.linspace(f_start_hz, f_end_hz, 5)
    f_pts_khz = (f_pts_hz / 1000.0).tolist()
    alpha_pts: List[float] = []

    for f_k in f_pts_khz:
        alpha_chem = ainslie_mccolm_absorption(f_k, scenario.temperature_c, scenario.salinity_psu, scenario.depth_m)
        # Optional sensitivity heuristic for turbidity scattering
        if scenario.turbidity > 0:
            alpha_turb = 35.0 * (scenario.turbidity / 100.0) * ((f_k / 300.0) ** 2)
        else:
            alpha_turb = 0.0
        alpha_pts.append(alpha_chem + alpha_turb)

    alpha_band = float(np.mean(alpha_pts))
    r_eff = max(1.0, float(scenario.range_m))

    # Simplified relative transmission loss (1-way spherical spreading + absorption)
    # TL(R) = 20*log10(R) + alpha*(R/1000)
    tl_db = 20.0 * np.log10(r_eff) + alpha_band * (r_eff / 1000.0)

    # Relative propagation margin (0 dB reference transmit level - TL - noise penalty)
    rel_margin = -tl_db - scenario.noise_penalty_db

    # Viability: whether waveform maintains sufficient relative margin over one-way scenario path
    is_viable = bool(rel_margin >= viability_threshold_db)

    # Theoretical range resolution: Delta_R = c / (2B)
    delta_r_mm = (c / (2.0 * bandwidth_hz)) * 1000.0

    # Relative theoretical directivity proxy: Dir_rel = fc / 300 kHz (fixed aperture assumption)
    dir_rel = f_center / 300_000.0

    assumptions = [
        "Five-point discrete frequency approximation across chirp band",
        "Ainslie-McColm (1998) chemical relaxation absorption model",
        "Simplified spherical spreading one-way transmission loss 20*log10(R) + alpha*R",
        "Normalized relative source level (0 dB reference, no absolute acoustic SPL claimed)",
        "[SIMULATION ASSUMPTION] Viability threshold = -65 dB (policy parameter, not physical detection limit)",
        "Theoretical range resolution assumes ideal matched-filter pulse compression c/(2B)",
        "Theoretical directivity metric is a frequency proxy (fc/300kHz) under fixed aperture assumption",
        "Turbidity scattering is an unvalidated sensitivity heuristic when turbidity > 0",
    ]

    return ProfilePerformanceMetrics(
        profile_id=profile_id,
        name=name,
        f_start_hz=f_start_hz,
        f_end_hz=f_end_hz,
        f_center_hz=f_center,
        bandwidth_hz=bandwidth_hz,
        f_points_khz=f_pts_khz,
        alpha_points_db_km=alpha_pts,
        alpha_band_db_km=alpha_band,
        transmission_loss_db=float(tl_db),
        relative_margin_db=float(rel_margin),
        is_viable=is_viable,
        viability_threshold_db=viability_threshold_db,
        range_resolution_mm=float(delta_r_mm),
        relative_directivity=float(dir_rel),
        sound_speed_m_s=float(c),
        range_m=float(scenario.range_m),
        assumptions=assumptions,
    )


def evaluate_all_profiles(
    scenario: Optional[EnvironmentalScenario] = None,
    mission_objective: str = "SURVEY",
    viability_threshold_db: float = -65.0,
) -> Tuple[List[ProfilePerformanceMetrics], EvaluationDecision]:
    """
    Evaluates all 3 canonical profiles and applies the multi-tier selection hierarchy:
      Tier 1: Propagation Viability Check (Can the waveform maintain sufficient modeled margin?)
      Tier 2: Mission Objective Selector (Survey vs Directivity vs Fallback)
    """
    if scenario is None:
        scenario = EnvironmentalScenario()

    profiles_config = [
        (1, "LOW_FREQUENCY", 100_000.0, 220_000.0, 120_000.0),
        (2, "BALANCED", 200_000.0, 400_000.0, 200_000.0),
        (3, "HIGH_FREQUENCY", 350_000.0, 500_000.0, 150_000.0),
    ]

    metrics: List[ProfilePerformanceMetrics] = []
    for pid, name, f0, f1, bw in profiles_config:
        m = evaluate_single_profile(pid, name, f0, f1, bw, scenario, viability_threshold_db)
        metrics.append(m)

    p1_viable = metrics[0].is_viable
    p2_viable = metrics[1].is_viable
    p3_viable = metrics[2].is_viable

    candidate_id = 1
    rationale = ""
    obj = mission_objective.upper()

    if obj == "DIRECTIVITY":
        if p3_viable:
            candidate_id = 3
            rationale = "HIGH_FREQUENCY selected: propagation is viable and directivity objective is active (narrowest theoretical beam)."
        elif p2_viable:
            candidate_id = 2
            rationale = "BALANCED selected: HIGH_FREQUENCY falls below simulation viability threshold; BALANCED provides next best directivity."
        else:
            candidate_id = 1
            rationale = "LOW_FREQUENCY fallback: higher-frequency profiles fall below viability threshold; LOW experiences lower modeled attenuation."

    elif obj == "PENETRATION":
        candidate_id = 1
        rationale = "LOW_FREQUENCY selected: penetration objective prioritizes lowest frequency-dependent attenuation."

    else:  # Default: "SURVEY"
        if p2_viable:
            candidate_id = 2
            rationale = "BALANCED selected: propagation is viable and BALANCED delivers superior range resolution (3.75 mm limit)."
        elif p1_viable:
            candidate_id = 1
            rationale = "LOW_FREQUENCY fallback: BALANCED falls below simulation viability threshold at this range."
        else:
            candidate_id = 1
            rationale = "LOW_FREQUENCY fallback: all profiles propagation-limited; selecting profile with lowest modeled transmission loss."

    cand_metric = metrics[candidate_id - 1]
    margin_above = cand_metric.relative_margin_db - viability_threshold_db

    # 1. Viability confidence: how comfortably viable is the selected profile relative to the policy floor
    # C_v = clip((Margin - Margin_threshold) / 15.0, 0.0, 1.0)
    viab_conf = float(np.clip(margin_above / 15.0, 0.0, 1.0))

    # 2. Mission selection confidence: utility difference among viable candidates under active mission mode
    # In Survey Mode, utility is normalized sweep bandwidth: U = B / 200 kHz
    # In Directivity Mode, utility is normalized directivity: U = fc / 425 kHz
    viable_profiles = [m for m in metrics if m.is_viable]
    num_viable = len(viable_profiles)

    if num_viable == 0:
        # Fail-safe condition: no profile meets viability threshold
        sel_conf = 0.50
    elif num_viable == 1:
        # Uniquely viable profile: selection is completely unambiguous
        sel_conf = 1.00
    else:
        # Multiple viable candidates: compare utility of chosen winner against second-best viable profile
        if obj == "DIRECTIVITY":
            utility_map = {1: 160.0 / 425.0, 2: 300.0 / 425.0, 3: 1.00}
        else:  # Default: SURVEY or PENETRATION
            utility_map = {1: 120.0 / 200.0, 2: 1.00, 3: 150.0 / 200.0}

        winner_u = utility_map[candidate_id]
        other_u = [utility_map[m.profile_id] for m in viable_profiles if m.profile_id != candidate_id]
        second_u = max(other_u) if other_u else winner_u
        delta_u = winner_u - second_u
        sel_conf = float(np.clip(delta_u / 0.25, 0.0, 1.0))

    decision = EvaluationDecision(
        candidate_profile_id=candidate_id,
        candidate_name=cand_metric.name,
        mission_objective=mission_objective,
        selection_rationale=rationale,
        viability_confidence=viab_conf,
        selection_confidence=sel_conf,
        profile_selection_confidence=viab_conf,  # Canonical metric preserved
        margin_above_viability_db=float(margin_above),
        all_viable=[p1_viable, p2_viable, p3_viable],
        range_m=scenario.range_m,
    )

    return metrics, decision
