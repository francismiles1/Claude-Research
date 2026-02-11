"""
Slider Sensitivity Analysis for Cap/Ops Balance Simulation.

Addresses two research questions:
    Q2: How do the 4 capacity sliders reshape the viable zone?
        For each archetype, sweeps each slider from 0->1 while holding
        others at default, measuring zone area at each step.
    Q7: Are there toxic slider combinations?
        Tests all 6 pairwise slider interactions using an additive
        independence model to detect compounding failures.

Depends on: src/viable_zones.py, src/dimension_slider_mapping.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from viable_zones import (
    sweep_grid,
    ARCHETYPE_DIMENSIONS,
    ARCHETYPE_DEFAULT_POSITIONS,
    ARCHETYPE_ORDER,
    PASS_THRESHOLD,
)
from dimension_slider_mapping import (
    ARCHETYPE_SLIDER_DEFAULTS,
    SLIDER_SHORT,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SWEEP_STEPS = 11              # 0.0, 0.1, ..., 1.0
INTERACTION_LOW = 0.10        # "Low" slider value for interaction tests
MARGINAL_EPSILON = 0.02       # Half-width for numerical derivative
TOXIC_THRESHOLD = -2.0        # Interaction strength below this = toxic (%)
BUFFERING_THRESHOLD = 2.0     # Interaction strength above this = buffering (%)
SATURATION_THRESHOLD = 0.5    # Marginal gain below this = saturated (%/step)


# ---------------------------------------------------------------------------
# Grid cache
# ---------------------------------------------------------------------------

_GRID_CACHE: dict[tuple, float] = {}


def _cached_zone_area(dims: list[int], sliders: list[float]) -> float:
    """Compute zone area (%) with caching to avoid redundant sweeps."""
    key = (tuple(dims), tuple(round(s, 4) for s in sliders))
    if key not in _GRID_CACHE:
        grid = sweep_grid(dims, sliders)
        _GRID_CACHE[key] = float(np.mean(grid[:, :, 3] >= PASS_THRESHOLD)) * 100.0
    return _GRID_CACHE[key]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SliderSweepResult:
    """Results from sweeping one slider across its full range."""
    slider_idx: int
    slider_name: str
    default_value: float
    values: np.ndarray          # Slider values swept
    zone_areas: np.ndarray      # Zone area (%) at each value
    total_impact: float         # max - min area across sweep
    marginal_at_default: float  # Numerical derivative at default (%/0.1 slider)
    saturation_point: Optional[float]  # Value beyond which gain < threshold


@dataclass
class InteractionResult:
    """Results from testing one pair of sliders for interaction effects."""
    slider_a: int
    slider_b: int
    area_default: float         # Both at archetype defaults
    area_a_low: float           # A at 0.1, B at default
    area_b_low: float           # B at 0.1, A at default
    area_both_low: float        # Both at 0.1
    predicted_both_low: float   # Additive prediction
    interaction_strength: float # actual - predicted (negative = toxic)


@dataclass
class SensitivityProfile:
    """Complete sensitivity analysis for one archetype."""
    archetype: str
    default_zone_area: float
    sweeps: list[SliderSweepResult]       # 4 entries (one per slider)
    interactions: list[InteractionResult]  # 6 entries (one per pair)
    most_impactful_slider: str            # Name of slider with highest total impact
    binding_lever: str                    # Name of slider with highest marginal at default


# ---------------------------------------------------------------------------
# Q2: Individual slider sweeps
# ---------------------------------------------------------------------------

def sweep_single_slider(archetype: str, slider_idx: int,
                        n_steps: int = SWEEP_STEPS) -> SliderSweepResult:
    """Sweep one slider from 0.0 to 1.0, holding others at default.

    Returns a SliderSweepResult with zone area at each step, plus
    total impact, marginal sensitivity, and saturation point.
    """
    dims = ARCHETYPE_DIMENSIONS[archetype]
    defaults = list(ARCHETYPE_SLIDER_DEFAULTS[archetype])
    default_val = defaults[slider_idx]

    values = np.linspace(0.0, 1.0, n_steps)
    areas = np.zeros(n_steps)

    for i, val in enumerate(values):
        sliders = list(defaults)
        sliders[slider_idx] = val
        areas[i] = _cached_zone_area(dims, sliders)

    # Total impact: full range of influence
    total_impact = float(np.max(areas) - np.min(areas))

    # Marginal sensitivity at default position (numerical derivative)
    marginal = _compute_marginal(dims, defaults, slider_idx, default_val)

    # Saturation detection
    saturation = _detect_saturation(values, areas)

    return SliderSweepResult(
        slider_idx=slider_idx,
        slider_name=SLIDER_SHORT[slider_idx],
        default_value=default_val,
        values=values,
        zone_areas=areas,
        total_impact=total_impact,
        marginal_at_default=marginal,
        saturation_point=saturation,
    )


def _compute_marginal(dims: list[int], defaults: list[float],
                      slider_idx: int, at_value: float) -> float:
    """Numerical derivative of zone area w.r.t. slider at given value.

    Returns change in zone area (%) per 0.1 slider movement.
    """
    eps = MARGINAL_EPSILON
    v_lo = max(0.0, at_value - eps)
    v_hi = min(1.0, at_value + eps)

    sliders_lo = list(defaults)
    sliders_lo[slider_idx] = v_lo
    sliders_hi = list(defaults)
    sliders_hi[slider_idx] = v_hi

    area_lo = _cached_zone_area(dims, sliders_lo)
    area_hi = _cached_zone_area(dims, sliders_hi)

    # Scale to per-0.1-slider-unit for readability
    derivative = (area_hi - area_lo) / (v_hi - v_lo) * 0.1
    return derivative


def _detect_saturation(values: np.ndarray, areas: np.ndarray) -> Optional[float]:
    """Find the slider value beyond which marginal gain drops below threshold.

    Returns the saturation point, or None if no saturation detected.
    Requires two consecutive steps below threshold to avoid noise.
    """
    if len(values) < 3:
        return None

    step_size = values[1] - values[0]
    consecutive_low = 0

    for i in range(len(values) - 1):
        marginal = abs(areas[i + 1] - areas[i]) / step_size * 0.1
        if marginal < SATURATION_THRESHOLD:
            consecutive_low += 1
            if consecutive_low >= 2:
                # Saturation started two steps ago
                return float(values[i - 1])
        else:
            consecutive_low = 0

    return None


# ---------------------------------------------------------------------------
# Q7: Pairwise interaction effects
# ---------------------------------------------------------------------------

def analyse_interaction_pair(archetype: str,
                             slider_a: int, slider_b: int) -> InteractionResult:
    """Analyse interaction between two sliders using additive independence model.

    Compares actual zone area when both sliders are low against the
    prediction from an additive model. Negative interaction_strength
    indicates toxic (compounding) failure.
    """
    dims = ARCHETYPE_DIMENSIONS[archetype]
    defaults = list(ARCHETYPE_SLIDER_DEFAULTS[archetype])

    # Configuration 1: both at default
    area_default = _cached_zone_area(dims, defaults)

    # Configuration 2: A low, B default
    sliders_a_low = list(defaults)
    sliders_a_low[slider_a] = INTERACTION_LOW
    area_a_low = _cached_zone_area(dims, sliders_a_low)

    # Configuration 3: B low, A default
    sliders_b_low = list(defaults)
    sliders_b_low[slider_b] = INTERACTION_LOW
    area_b_low = _cached_zone_area(dims, sliders_b_low)

    # Configuration 4: both low
    sliders_both_low = list(defaults)
    sliders_both_low[slider_a] = INTERACTION_LOW
    sliders_both_low[slider_b] = INTERACTION_LOW
    area_both_low = _cached_zone_area(dims, sliders_both_low)

    # Additive independence prediction
    predicted = area_a_low + area_b_low - area_default
    interaction = area_both_low - predicted

    return InteractionResult(
        slider_a=slider_a,
        slider_b=slider_b,
        area_default=area_default,
        area_a_low=area_a_low,
        area_b_low=area_b_low,
        area_both_low=area_both_low,
        predicted_both_low=predicted,
        interaction_strength=interaction,
    )


# ---------------------------------------------------------------------------
# Full archetype analysis
# ---------------------------------------------------------------------------

def analyse_archetype_sensitivity(archetype: str) -> SensitivityProfile:
    """Complete slider sensitivity analysis for one archetype.

    Runs all 4 individual slider sweeps (Q2) and all 6 pairwise
    interaction tests (Q7).
    """
    dims = ARCHETYPE_DIMENSIONS[archetype]
    defaults = list(ARCHETYPE_SLIDER_DEFAULTS[archetype])
    default_area = _cached_zone_area(dims, defaults)

    # Q2: Individual sweeps
    sweeps = [sweep_single_slider(archetype, i) for i in range(4)]

    # Q7: All 6 pairwise interactions
    interactions = []
    for a in range(4):
        for b in range(a + 1, 4):
            interactions.append(analyse_interaction_pair(archetype, a, b))

    # Identify most impactful slider and binding lever
    impacts = [(s.total_impact, s.slider_name) for s in sweeps]
    marginals = [(s.marginal_at_default, s.slider_name) for s in sweeps]
    most_impactful = max(impacts, key=lambda x: x[0])[1]
    binding_lever = max(marginals, key=lambda x: x[0])[1]

    return SensitivityProfile(
        archetype=archetype,
        default_zone_area=default_area,
        sweeps=sweeps,
        interactions=interactions,
        most_impactful_slider=most_impactful,
        binding_lever=binding_lever,
    )


def analyse_all() -> list[SensitivityProfile]:
    """Run sensitivity analysis for all 15 archetypes."""
    return [analyse_archetype_sensitivity(a) for a in ARCHETYPE_ORDER]


# ---------------------------------------------------------------------------
# ASCII sensitivity curve
# ---------------------------------------------------------------------------

def render_sensitivity_curve(sweep: SliderSweepResult,
                             width: int = 55, height: int = 15) -> str:
    """ASCII plot of zone area vs slider value.

    Marks default position with @.
    """
    areas = sweep.zone_areas
    values = sweep.values

    # Scale to plot area
    a_min = max(0.0, float(np.min(areas)) - 2.0)
    a_max = float(np.max(areas)) + 2.0
    if a_max - a_min < 5.0:
        a_max = a_min + 5.0

    lines = []
    lines.append(f"  {sweep.slider_name}: zone area vs slider value  "
                 f"(impact: {sweep.total_impact:+.1f}%)")
    lines.append("")

    # Find default position in plot coordinates
    def_col = -1
    if len(values) > 0:
        def_col = int(round(sweep.default_value * (width - 1)))

    for row in range(height - 1, -1, -1):
        y_val = a_min + (a_max - a_min) * row / (height - 1)

        # Row label
        if row == height - 1 or row == 0 or row == height // 2:
            label = f"{y_val:5.1f}%|"
        else:
            label = "      |"

        chars = [" "] * width
        for col in range(width):
            x_val = col / (width - 1)
            # Interpolate area at this x position
            area_at_x = float(np.interp(x_val, values, areas))

            # Plot if this row corresponds to the area value
            row_y_lo = a_min + (a_max - a_min) * (row - 0.5) / (height - 1)
            row_y_hi = a_min + (a_max - a_min) * (row + 0.5) / (height - 1)

            if row_y_lo <= area_at_x <= row_y_hi:
                if col == def_col:
                    chars[col] = "@"
                else:
                    chars[col] = "#"

        lines.append(label + "".join(chars))

    # X-axis
    lines.append("      +" + "-" * width)
    lines.append(f"       0.0       0.2       0.4       0.6       0.8       1.0")
    lines.append(f"                        {sweep.slider_name} ->")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_cross_archetype_summary(results: list[SensitivityProfile]) -> None:
    """Print summary table of slider impacts across all archetypes."""
    print("\n=== Slider Impact Summary (All 15 Archetypes) ===\n")
    print(f"{'#':<3} {'Archetype':<22} {'Zone%':>6} "
          f"{'Most Impactful':>20} {'Binding Lever':>18} {'Worst Toxic Pair':>22}")
    print("-" * 97)

    for p in results:
        # Find most impactful slider's total impact
        best_sweep = max(p.sweeps, key=lambda s: s.total_impact)
        impact_str = f"{best_sweep.slider_name} {best_sweep.total_impact:+.1f}%"

        # Find binding lever's marginal
        best_marginal = max(p.sweeps, key=lambda s: s.marginal_at_default)
        lever_str = f"{best_marginal.slider_name} {best_marginal.marginal_at_default:+.1f}%"

        # Find worst toxic pair
        worst = min(p.interactions, key=lambda x: x.interaction_strength)
        if worst.interaction_strength < TOXIC_THRESHOLD:
            pair_str = (f"{SLIDER_SHORT[worst.slider_a]}+"
                        f"{SLIDER_SHORT[worst.slider_b]} "
                        f"({worst.interaction_strength:+.1f})")
        else:
            pair_str = "none"

        idx = p.archetype.split(" ")[0]
        name = " ".join(p.archetype.split(" ")[1:])
        print(f"{idx:<3} {name:<22} {p.default_zone_area:>5.1f}% "
              f"{impact_str:>20} {lever_str:>18} {pair_str:>22}")


def print_archetype_detail(profile: SensitivityProfile) -> None:
    """Print detailed sensitivity report for one archetype."""
    print(f"\n{'=' * 70}")
    print(f"  {profile.archetype}  (default zone: {profile.default_zone_area:.1f}%)")
    print(f"  Most impactful: {profile.most_impactful_slider}  |  "
          f"Binding lever: {profile.binding_lever}")
    print(f"{'=' * 70}")

    # Sweep table
    print(f"\n  Individual Slider Impacts (Q2):\n")
    print(f"  {'Slider':<12} {'Default':>8} {'Total':>10} {'Marginal':>12} "
          f"{'At 0.0':>8} {'At 1.0':>8} {'Saturation':>11}")
    print(f"  {'-' * 73}")

    for s in profile.sweeps:
        sat_str = f"{s.saturation_point:.1f}" if s.saturation_point is not None else "none"
        print(f"  {s.slider_name:<12} {s.default_value:>7.2f} "
              f"{s.total_impact:>+9.1f}% {s.marginal_at_default:>+10.1f}%/0.1 "
              f"{s.zone_areas[0]:>7.1f}% {s.zone_areas[-1]:>7.1f}% {sat_str:>11}")

    # Sensitivity curve for most impactful slider
    best = max(profile.sweeps, key=lambda s: s.total_impact)
    print()
    print(render_sensitivity_curve(best))

    # Interaction matrix
    print(f"\n  Pairwise Interactions (Q7):\n")
    print(f"  {'':>12}", end="")
    for name in SLIDER_SHORT:
        print(f" {name:>12}", end="")
    print()
    print(f"  {'-' * 60}")

    # Build 4x4 matrix
    matrix = np.zeros((4, 4))
    for inter in profile.interactions:
        matrix[inter.slider_a, inter.slider_b] = inter.interaction_strength
        matrix[inter.slider_b, inter.slider_a] = inter.interaction_strength

    for i in range(4):
        print(f"  {SLIDER_SHORT[i]:<12}", end="")
        for j in range(4):
            if i == j:
                print(f" {'--':>12}", end="")
            else:
                val = matrix[i, j]
                marker = ""
                if val < TOXIC_THRESHOLD:
                    marker = " TOXIC"
                elif val > BUFFERING_THRESHOLD:
                    marker = " buff"
                print(f" {val:>+6.1f}{marker:>6}", end="")
        print()


def print_toxic_combinations_report(results: list[SensitivityProfile]) -> None:
    """Identify universal and archetype-specific toxic combinations."""
    print(f"\n{'=' * 70}")
    print(f"  Toxic Slider Combinations Report (Q7)")
    print(f"{'=' * 70}")

    # Count how many archetypes each pair is toxic for
    pair_toxic_count: dict[tuple[int, int], list[str]] = {}
    pair_strengths: dict[tuple[int, int], list[float]] = {}

    for p in results:
        for inter in p.interactions:
            pair = (inter.slider_a, inter.slider_b)
            if pair not in pair_toxic_count:
                pair_toxic_count[pair] = []
                pair_strengths[pair] = []
            pair_strengths[pair].append(inter.interaction_strength)
            if inter.interaction_strength < TOXIC_THRESHOLD:
                pair_toxic_count[pair].append(p.archetype)

    # Universal toxic pairs (>10/15)
    print(f"\n  Universal toxic pairs (toxic for >10/15 archetypes):\n")
    found_universal = False
    for pair, archetypes in sorted(pair_toxic_count.items(),
                                    key=lambda x: len(x[1]), reverse=True):
        if len(archetypes) > 10:
            found_universal = True
            avg_str = np.mean(pair_strengths[pair])
            print(f"    {SLIDER_SHORT[pair[0]]} + {SLIDER_SHORT[pair[1]]}: "
                  f"toxic for {len(archetypes)}/15 archetypes "
                  f"(avg interaction: {avg_str:+.1f}%)")
    if not found_universal:
        print(f"    None found (no pair is toxic for >10 archetypes)")

    # Widely toxic pairs (>5/15)
    print(f"\n  Widely toxic pairs (toxic for >5/15 archetypes):\n")
    found_wide = False
    for pair, archetypes in sorted(pair_toxic_count.items(),
                                    key=lambda x: len(x[1]), reverse=True):
        if 5 < len(archetypes) <= 10:
            found_wide = True
            avg_str = np.mean(pair_strengths[pair])
            print(f"    {SLIDER_SHORT[pair[0]]} + {SLIDER_SHORT[pair[1]]}: "
                  f"toxic for {len(archetypes)}/15 archetypes "
                  f"(avg interaction: {avg_str:+.1f}%)")
    if not found_wide:
        print(f"    None found")

    # Archetype-specific toxic pairs (1-5 archetypes)
    print(f"\n  Archetype-specific toxic pairs (1-5 archetypes):\n")
    found_specific = False
    for pair, archetypes in sorted(pair_toxic_count.items(),
                                    key=lambda x: len(x[1]), reverse=True):
        if 1 <= len(archetypes) <= 5:
            found_specific = True
            names = ", ".join(a.split(" ", 1)[0] for a in archetypes)
            avg_str = np.mean([s for s in pair_strengths[pair]
                               if s < TOXIC_THRESHOLD])
            print(f"    {SLIDER_SHORT[pair[0]]} + {SLIDER_SHORT[pair[1]]}: "
                  f"toxic for {names} (avg: {avg_str:+.1f}%)")
    if not found_specific:
        print(f"    None found")

    # Most toxic single archetype
    print(f"\n  Most interaction-sensitive archetypes:\n")
    arch_toxic = []
    for p in results:
        n_toxic = sum(1 for inter in p.interactions
                      if inter.interaction_strength < TOXIC_THRESHOLD)
        worst = min(inter.interaction_strength for inter in p.interactions)
        arch_toxic.append((p.archetype, n_toxic, worst))

    arch_toxic.sort(key=lambda x: x[2])
    for arch, count, worst in arch_toxic[:5]:
        print(f"    {arch:<28} {count}/6 toxic pairs, "
              f"worst: {worst:+.1f}%")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run slider sensitivity analysis for all 15 archetypes."""
    print("=" * 70)
    print("  Slider Sensitivity Analysis")
    print("  Q2: Individual slider impacts  |  Q7: Toxic combinations")
    print("=" * 70)

    print("\nAnalysing 15 archetypes (this may take 30-60 seconds)...\n")

    results = analyse_all()

    # Cross-archetype summary
    print_cross_archetype_summary(results)

    # Toxic combinations report
    print_toxic_combinations_report(results)

    # Detailed reports for key archetypes
    key_archetypes = [
        "#1 Micro Startup",       # Resource-constrained startup
        "#8 Reg Stage-Gate",      # Resource-rich regulated
        "#9 Ent Balanced",        # Enterprise baseline
        "#12 Crisis/Firefight",   # Stressed state
    ]

    print(f"\n\n{'=' * 70}")
    print(f"  Detailed Reports for Key Archetypes")
    print(f"{'=' * 70}")

    for arch in key_archetypes:
        profile = next(r for r in results if r.archetype == arch)
        print_archetype_detail(profile)
        print()


if __name__ == "__main__":
    main()
