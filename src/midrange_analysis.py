"""
Mid-Range Investigation for Cap/Ops Balance Simulation (Q6).

Is mid-range (roughly 35-65% Cap, 35-65% Ops) a real stable state, or
just an unstable transitional corridor that archetypes pass through
on the way to somewhere else?

No MIRA persona naturally lands in mid-range. This analysis tests:
    1. Which archetypes have mid-range coverage in their viable zone?
    2. Can synthetic mid-range profiles sustain a stable viable zone?
    3. Is mid-range viable along known transition paths?
    4. Does mid-range require specific slider profiles to be stable?

Depends on: src/viable_zones.py, src/dimension_slider_mapping.py,
            src/slider_sensitivity.py
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from viable_zones import (
    sweep_grid,
    test_viable,
    test_sufficient,
    test_sustainable,
    ARCHETYPE_DIMENSIONS,
    ARCHETYPE_DEFAULT_POSITIONS,
    ARCHETYPE_ORDER,
    PASS_THRESHOLD,
    GRID_RESOLUTION,
)
from dimension_slider_mapping import (
    ARCHETYPE_SLIDER_DEFAULTS,
    SLIDER_SHORT,
    DIMENSION_SHORT,
)
from slider_sensitivity import _cached_zone_area


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Mid-range region definition
MID_CAP_LO = 0.35
MID_CAP_HI = 0.65
MID_OPS_LO = 0.35
MID_OPS_HI = 0.65
MID_CENTRE = (0.50, 0.50)  # Centre of the mid-range region


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MidRangeCoverage:
    """How much of an archetype's viable zone falls in mid-range."""
    archetype: str
    total_zone_pct: float         # % of full grid that is viable
    midrange_zone_pct: float      # % of mid-range region that is viable
    midrange_share_pct: float     # What fraction of the viable zone is in mid-range
    centre_viable: bool           # Is (50%, 50%) specifically viable?
    centre_scores: tuple[float, float, float]  # V, S, U at centre
    centre_binding: str


@dataclass
class SyntheticProfile:
    """A synthetic dimension/slider profile for mid-range testing."""
    label: str
    dims: list[int]
    sliders: list[float]
    total_zone_pct: float
    midrange_zone_pct: float
    centre_viable: bool
    centre_scores: tuple[float, float, float]


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

def compute_midrange_coverage(archetype: str) -> MidRangeCoverage:
    """Compute how much of an archetype's viable zone covers mid-range."""
    dims = ARCHETYPE_DIMENSIONS[archetype]
    sliders = ARCHETYPE_SLIDER_DEFAULTS[archetype]

    grid = sweep_grid(dims, sliders)
    combined = grid[:, :, 3]
    steps = np.linspace(0.0, 1.0, GRID_RESOLUTION)

    # Full zone area
    full_viable = combined >= PASS_THRESHOLD
    total_zone_pct = float(np.mean(full_viable)) * 100.0

    # Mid-range mask
    cap_mask = (steps >= MID_CAP_LO) & (steps <= MID_CAP_HI)
    ops_mask = (steps >= MID_OPS_LO) & (steps <= MID_OPS_HI)
    midrange_grid = full_viable[np.ix_(ops_mask, cap_mask)]
    midrange_cells = midrange_grid.size
    midrange_viable = float(np.sum(midrange_grid))
    midrange_zone_pct = (midrange_viable / midrange_cells * 100.0
                         if midrange_cells > 0 else 0.0)

    # What share of the total viable zone is in mid-range?
    total_viable_cells = float(np.sum(full_viable))
    midrange_share_pct = (midrange_viable / total_viable_cells * 100.0
                          if total_viable_cells > 0 else 0.0)

    # Centre point assessment
    cap_c, ops_c = MID_CENTRE
    v = test_viable(cap_c, ops_c, dims, sliders)
    s = test_sufficient(cap_c, ops_c, dims, sliders)
    u = test_sustainable(cap_c, ops_c, dims, sliders)
    centre_viable = min(v, s, u) >= PASS_THRESHOLD

    scores_dict = {"viable": v, "sufficient": s, "sustainable": u}
    binding = min(scores_dict, key=scores_dict.get)

    return MidRangeCoverage(
        archetype=archetype,
        total_zone_pct=total_zone_pct,
        midrange_zone_pct=midrange_zone_pct,
        midrange_share_pct=midrange_share_pct,
        centre_viable=centre_viable,
        centre_scores=(v, s, u),
        centre_binding=binding,
    )


def build_synthetic_profiles() -> list[SyntheticProfile]:
    """Build synthetic mid-range profiles to test stability.

    Tests several hypothetical dimension/slider configurations that
    might naturally sit at mid-range:
    1. Average of all archetypes (grand mean)
    2. Average of archetypes nearest mid-range (#3, #5)
    3. "Balanced moderate" — all dimensions at 3, moderate sliders
    4. "Resource-rich moderate" — moderate dims, high sliders
    5. "Resource-poor moderate" — moderate dims, low sliders
    """
    profiles = []

    # 1. Grand mean of all 15 archetypes
    all_dims = np.array([ARCHETYPE_DIMENSIONS[a] for a in ARCHETYPE_ORDER])
    all_sliders = np.array([ARCHETYPE_SLIDER_DEFAULTS[a] for a in ARCHETYPE_ORDER])
    mean_dims = list(np.round(np.mean(all_dims, axis=0)).astype(int))
    mean_sliders = list(np.mean(all_sliders, axis=0))
    profiles.append(("Grand mean (all 15)", mean_dims, mean_sliders))

    # 2. Average of nearest-to-midrange archetypes (#3 Scaling, #5 Component)
    near_archs = ["#3 Scaling Startup", "#5 Component Heroes"]
    near_dims = np.array([ARCHETYPE_DIMENSIONS[a] for a in near_archs])
    near_sliders = np.array([ARCHETYPE_SLIDER_DEFAULTS[a] for a in near_archs])
    avg_near_dims = list(np.round(np.mean(near_dims, axis=0)).astype(int))
    avg_near_sliders = list(np.mean(near_sliders, axis=0))
    profiles.append(("Avg of #3+#5 (near mid)", avg_near_dims, avg_near_sliders))

    # 3. Balanced moderate: all dimensions at 3, moderate sliders
    profiles.append(("Balanced moderate (all D=3)",
                     [3, 3, 3, 3, 3, 3, 3, 3],
                     [0.50, 0.50, 0.50, 0.50]))

    # 4. Resource-rich moderate: moderate dims, high sliders
    profiles.append(("Resource-rich moderate",
                     [3, 3, 3, 3, 3, 3, 3, 3],
                     [0.80, 0.65, 0.35, 0.65]))

    # 5. Resource-poor moderate: moderate dims, low sliders
    profiles.append(("Resource-poor moderate",
                     [3, 3, 3, 3, 3, 3, 3, 3],
                     [0.25, 0.25, 0.65, 0.25]))

    # 6. Low-stakes moderate: low consequence/regulation, moderate rest
    profiles.append(("Low-stakes moderate",
                     [1, 3, 2, 1, 3, 1, 3, 4],
                     [0.50, 0.50, 0.35, 0.50]))

    results = []
    for label, dims, sliders in profiles:
        grid = sweep_grid(dims, sliders)
        combined = grid[:, :, 3]
        steps = np.linspace(0.0, 1.0, GRID_RESOLUTION)

        full_viable = combined >= PASS_THRESHOLD
        total_zone_pct = float(np.mean(full_viable)) * 100.0

        # Mid-range coverage
        cap_mask = (steps >= MID_CAP_LO) & (steps <= MID_CAP_HI)
        ops_mask = (steps >= MID_OPS_LO) & (steps <= MID_OPS_HI)
        midrange_grid = full_viable[np.ix_(ops_mask, cap_mask)]
        midrange_zone_pct = (float(np.mean(midrange_grid)) * 100.0
                             if midrange_grid.size > 0 else 0.0)

        # Centre point
        cap_c, ops_c = MID_CENTRE
        v = test_viable(cap_c, ops_c, dims, sliders)
        s = test_sufficient(cap_c, ops_c, dims, sliders)
        u = test_sustainable(cap_c, ops_c, dims, sliders)

        results.append(SyntheticProfile(
            label=label, dims=dims, sliders=sliders,
            total_zone_pct=total_zone_pct,
            midrange_zone_pct=midrange_zone_pct,
            centre_viable=min(v, s, u) >= PASS_THRESHOLD,
            centre_scores=(v, s, u),
        ))

    return results


def analyse_midrange_stability() -> dict:
    """Test whether mid-range positions are stable or transitional.

    Checks whether small perturbations from (50%, 50%) stay viable,
    using the grand-mean profile. If the zone is large and centred
    around mid-range, the position is stable. If the zone is narrow
    or the position is near a cliff edge, it's transitional.
    """
    # Use grand mean profile
    all_dims = np.array([ARCHETYPE_DIMENSIONS[a] for a in ARCHETYPE_ORDER])
    all_sliders = np.array([ARCHETYPE_SLIDER_DEFAULTS[a] for a in ARCHETYPE_ORDER])
    dims = [int(x) for x in np.round(np.mean(all_dims, axis=0))]
    sliders = [float(x) for x in np.mean(all_sliders, axis=0)]

    grid = sweep_grid(dims, sliders)
    combined = grid[:, :, 3]
    steps = np.linspace(0.0, 1.0, GRID_RESOLUTION)

    # Find the viable zone boundaries along Cap=50% and Ops=50% slices
    cap_50_idx = np.argmin(np.abs(steps - 0.50))
    ops_50_idx = np.argmin(np.abs(steps - 0.50))

    # Ops range at Cap=50%
    col_slice = combined[:, cap_50_idx]
    viable_ops = steps[col_slice >= PASS_THRESHOLD]

    # Cap range at Ops=50%
    row_slice = combined[ops_50_idx, :]
    viable_cap = steps[row_slice >= PASS_THRESHOLD]

    return {
        "dims": dims,
        "sliders": sliders,
        "ops_range_at_cap50": (float(viable_ops[0]), float(viable_ops[-1]))
                              if len(viable_ops) > 0 else (0.0, 0.0),
        "cap_range_at_ops50": (float(viable_cap[0]), float(viable_cap[-1]))
                              if len(viable_cap) > 0 else (0.0, 0.0),
        "ops_width": float(viable_ops[-1] - viable_ops[0])
                     if len(viable_ops) > 0 else 0.0,
        "cap_width": float(viable_cap[-1] - viable_cap[0])
                     if len(viable_cap) > 0 else 0.0,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_q6_report() -> None:
    """Print the full Q6 mid-range investigation report."""
    print("=" * 80)
    print("  Q6: Is Mid-Range a Real State?")
    print("  Mid-range defined as 35-65% Cap, 35-65% Ops")
    print("=" * 80)

    # Part 1: Archetype mid-range coverage
    print(f"\n  Part 1: Which archetypes cover mid-range?\n")
    coverages = [compute_midrange_coverage(a) for a in ARCHETYPE_ORDER]

    print(f"  {'Archetype':<28} {'Zone%':>6} {'MidCov%':>8} {'MidShare%':>10} "
          f"{'Centre':>7} {'V':>6} {'S':>6} {'U':>6} {'Binding':>14}")
    print(f"  {'-' * 100}")

    for c in sorted(coverages, key=lambda x: x.midrange_zone_pct, reverse=True):
        ctr = "PASS" if c.centre_viable else "FAIL"
        v, s, u = c.centre_scores
        print(f"  {c.archetype:<28} {c.total_zone_pct:>5.1f}% {c.midrange_zone_pct:>7.1f}% "
              f"{c.midrange_share_pct:>9.1f}% {ctr:>7} {v:>6.3f} {s:>6.3f} {u:>6.3f} "
              f"{c.centre_binding:>14}")

    # Count how many archetypes have >50% mid-range coverage
    good_mid = [c for c in coverages if c.midrange_zone_pct > 50]
    some_mid = [c for c in coverages if 10 < c.midrange_zone_pct <= 50]
    no_mid = [c for c in coverages if c.midrange_zone_pct <= 10]
    centre_pass = [c for c in coverages if c.centre_viable]

    print(f"\n  Summary:")
    print(f"    {len(centre_pass)}/15 archetypes viable at (50%, 50%)")
    print(f"    {len(good_mid)}/15 have >50% mid-range coverage")
    print(f"    {len(some_mid)}/15 have 10-50% mid-range coverage")
    print(f"    {len(no_mid)}/15 have <10% mid-range coverage")

    # Part 2: Synthetic profiles
    print(f"\n  {'~' * 70}")
    print(f"  Part 2: Synthetic mid-range profiles\n")
    synthetics = build_synthetic_profiles()

    print(f"  {'Profile':<30} {'Dims':>24} {'Zone%':>6} {'MidCov%':>8} "
          f"{'Centre':>7} {'V':>6} {'S':>6} {'U':>6}")
    print(f"  {'-' * 100}")

    for sp in synthetics:
        dims_str = "".join(f"{d}" for d in sp.dims)
        ctr = "PASS" if sp.centre_viable else "FAIL"
        v, s, u = sp.centre_scores
        print(f"  {sp.label:<30} [{dims_str}] {sp.total_zone_pct:>5.1f}% "
              f"{sp.midrange_zone_pct:>7.1f}% {ctr:>7} {v:>6.3f} {s:>6.3f} {u:>6.3f}")

    # Slider detail for synthetics
    print(f"\n  Slider profiles:")
    for sp in synthetics:
        slider_str = " ".join(f"{SLIDER_SHORT[i]}={sp.sliders[i]:.2f}"
                              for i in range(4))
        print(f"    {sp.label:<30} {slider_str}")

    # Part 3: Stability analysis
    print(f"\n  {'~' * 70}")
    print(f"  Part 3: Mid-range stability (grand-mean profile)\n")
    stability = analyse_midrange_stability()

    print(f"  Profile: dims={stability['dims']}, "
          f"sliders=[{', '.join(f'{s:.2f}' for s in stability['sliders'])}]")
    print(f"  At Cap=50%: viable Ops range = "
          f"{stability['ops_range_at_cap50'][0]:.0%} - "
          f"{stability['ops_range_at_cap50'][1]:.0%} "
          f"(width: {stability['ops_width']:.0%})")
    print(f"  At Ops=50%: viable Cap range = "
          f"{stability['cap_range_at_ops50'][0]:.0%} - "
          f"{stability['cap_range_at_ops50'][1]:.0%} "
          f"(width: {stability['cap_width']:.0%})")

    min_width = min(stability['ops_width'], stability['cap_width'])
    if min_width > 0.30:
        stability_verdict = "STABLE"
        explanation = ("Mid-range is a wide, stable plateau. A project at (50%, 50%) "
                       "has substantial room to drift in any direction while remaining viable.")
    elif min_width > 0.15:
        stability_verdict = "CONDITIONALLY STABLE"
        explanation = ("Mid-range is viable but with limited margin. "
                       "Projects can sit here but must actively manage position.")
    elif min_width > 0.0:
        stability_verdict = "NARROW CORRIDOR"
        explanation = ("Mid-range is a thin viable band, not a stable plateau. "
                       "Projects pass through it during transitions but shouldn't aim for it.")
    else:
        stability_verdict = "NOT VIABLE"
        explanation = "Mid-range is not viable for the average profile."

    print(f"\n  Stability verdict: {stability_verdict}")
    print(f"  {explanation}")

    # Part 4: Conclusions
    print(f"\n  {'=' * 70}")
    print(f"  Q6 Conclusions")
    print(f"  {'=' * 70}")

    # Which archetypes naturally own mid-range?
    # "Owns" means mid-range is the core of their zone (>30% of zone is mid-range)
    # AND they have high mid-range coverage (>90%)
    core_mid = [c for c in coverages
                if c.midrange_share_pct > 30 and c.midrange_zone_pct > 90]
    if core_mid:
        names = ", ".join(c.archetype for c in core_mid)
        print(f"\n  Archetypes where mid-range is core (>30% of zone, >90% coverage):")
        print(f"    {names}")
    else:
        print(f"\n  No archetype has mid-range as its core territory.")

    # All archetypes are viable at centre
    centre_count = sum(1 for c in coverages if c.centre_viable)
    print(f"\n  {centre_count}/15 archetypes are viable at (50%, 50%).")
    if centre_count == 15:
        print(f"  Mid-range is universally accessible — the safest region on the grid.")
        print(f"  Yet no persona defaults here, confirming it's viable but not natural.")

    # Default position proximity
    near_mid = []
    for a in ARCHETYPE_ORDER:
        cap, ops = ARCHETYPE_DEFAULT_POSITIONS[a]
        if MID_CAP_LO <= cap <= MID_CAP_HI and MID_OPS_LO <= ops <= MID_OPS_HI:
            near_mid.append(a)

    if near_mid:
        print(f"\n  Archetypes with defaults IN mid-range: {', '.join(near_mid)}")
    else:
        # Find nearest
        min_dist = float('inf')
        nearest = ""
        for a in ARCHETYPE_ORDER:
            cap, ops = ARCHETYPE_DEFAULT_POSITIONS[a]
            dist = ((cap - 0.50)**2 + (ops - 0.50)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                nearest = a
        cap, ops = ARCHETYPE_DEFAULT_POSITIONS[nearest]
        print(f"\n  No archetype defaults sit in mid-range.")
        print(f"  Nearest: {nearest} at ({cap:.0%}, {ops:.0%}), "
              f"distance {min_dist:.0%} from centre.")

    print(f"\n  Final answer: ", end="")
    if stability_verdict == "STABLE":
        print("Mid-range IS a real, stable state for appropriately-resourced projects.")
        print("  It represents the 'balanced moderate' position where capability and")
        print("  operations are roughly aligned at moderate maturity. However, no MIRA")
        print("  persona lands here because real projects tend to specialise — the")
        print("  pressures of market, regulation, or resources push them off-centre.")
    elif stability_verdict in ("CONDITIONALLY STABLE", "NARROW CORRIDOR"):
        print("Mid-range is viable but NOT a natural attractor.")
        print("  Projects can pass through it during transitions, and some can sustain it")
        print("  with adequate resources, but real-world pressures tend to push projects")
        print("  toward more specialised positions (high-cap/low-ops or vice versa).")
    else:
        print("Mid-range is NOT a viable state for the average project profile.")
        print("  The sustainability costs of maintaining moderate maturity in both")
        print("  dimensions exceed what typical slider profiles can sustain.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run mid-range investigation (Q6)."""
    print_q6_report()


if __name__ == "__main__":
    main()
