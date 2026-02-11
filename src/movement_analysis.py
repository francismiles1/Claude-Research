"""
Movement & Transition Analysis for Cap/Ops Balance Simulation.

Addresses three research questions:
    Q4: Are off-diagonal positions genuinely successful or just surviving?
        Decomposes sustainability costs at each archetype's default position.
    Q5: What causes transitions between archetypes?
        Models continuous interpolation paths between archetype states.
    Q8: Can the model retrodict the P8 crisis?
        Progressively applies state modifiers to #6 Matrix Programme and
        observes the viable zone collapsing.

Depends on: src/viable_zones.py, src/dimension_slider_mapping.py,
            src/slider_sensitivity.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

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
)
from dimension_slider_mapping import (
    ARCHETYPE_SLIDER_DEFAULTS,
    SLIDER_SHORT,
    DIMENSION_SHORT,
    PHASE_MODIFIERS,
    CRISIS_MODIFIERS,
    EROSION_MODIFIERS,
)
from slider_sensitivity import _cached_zone_area


# ---------------------------------------------------------------------------
# Q4: Off-Diagonal Decomposition
# ---------------------------------------------------------------------------

@dataclass
class OffDiagonalDecomposition:
    """Decomposition of sustainability costs at an archetype's default position."""
    archetype: str
    cap: float
    ops: float
    gap: float
    gap_direction: str          # "Cap>Ops", "Ops>Cap", or "Balanced"

    # Raw cost components (before sigmoid)
    gap_cost: float
    debt_cost: float
    process_cost: float
    execution_cost: float
    total_cost: float
    investment_relief: float
    net_cost: float             # total_cost - investment_relief

    # Which slider compensates the gap
    compensator_name: str
    compensator_value: float

    # Final scores
    sustainable_score: float
    viable_score: float
    sufficient_score: float

    # Classification
    verdict: str


def decompose_off_diagonal(archetype: str) -> OffDiagonalDecomposition:
    """Decompose sustainability costs at an archetype's default position.

    Replicates the arithmetic from test_sustainable() to extract raw cost
    components before the sigmoid, plus viability/sufficiency scores.
    """
    dims = ARCHETYPE_DIMENSIONS[archetype]
    sliders = ARCHETYPE_SLIDER_DEFAULTS[archetype]
    cap, ops = ARCHETYPE_DEFAULT_POSITIONS[archetype]

    investment = sliders[0]
    recovery = sliders[1]
    overwork = sliders[2]
    time_cap = sliders[3]

    # Gap analysis
    gap = abs(cap - ops)
    if cap > ops + 0.02:
        gap_direction = "Cap>Ops"
        gap_cost = gap * (1.0 - time_cap)
        compensator_name = "Time"
        compensator_value = time_cap
    elif ops > cap + 0.02:
        gap_direction = "Ops>Cap"
        gap_cost = gap * (1.0 - max(overwork, recovery))
        compensator_name = "max(Owk,Rec)"
        compensator_value = max(overwork, recovery)
    else:
        gap_direction = "Balanced"
        gap_cost = 0.0
        compensator_name = "none"
        compensator_value = 0.0

    # Debt cost
    avg_maturity = (cap + ops) / 2.0
    debt_cost = max(0.0, 0.30 - avg_maturity) * 2.0

    # Process maintenance cost
    process_cost = cap * 0.45 * (1.0 - investment)

    # Execution overhead
    best_ops_capacity = max(overwork, time_cap, recovery)
    execution_cost = ops * 0.35 * (1.0 - best_ops_capacity)

    # Totals
    total_cost = gap_cost + debt_cost + process_cost + execution_cost
    inv_relief = investment * 0.10
    net_cost = total_cost - inv_relief

    # Scores
    sust_score = test_sustainable(cap, ops, dims, sliders)
    viab_score = test_viable(cap, ops, dims, sliders)
    suff_score = test_sufficient(cap, ops, dims, sliders)

    # Verdict classification
    if sust_score < PASS_THRESHOLD:
        verdict = "Unsustainable"
    elif overwork > 0.6 and gap_cost > 0.05 and gap_direction == "Ops>Cap":
        verdict = "Surviving on overwork"
    elif sust_score > 0.9 and (total_cost < 0.01 or gap_cost / max(total_cost, 0.001) < 0.3):
        verdict = "Genuinely sustainable"
    elif sust_score > 0.9:
        verdict = "Sustainable (compensated)"
    else:
        verdict = "Marginal"

    return OffDiagonalDecomposition(
        archetype=archetype, cap=cap, ops=ops, gap=gap,
        gap_direction=gap_direction,
        gap_cost=gap_cost, debt_cost=debt_cost,
        process_cost=process_cost, execution_cost=execution_cost,
        total_cost=total_cost, investment_relief=inv_relief,
        net_cost=net_cost,
        compensator_name=compensator_name,
        compensator_value=compensator_value,
        sustainable_score=sust_score,
        viable_score=viab_score, sufficient_score=suff_score,
        verdict=verdict,
    )


def print_q4_report(decompositions: list[OffDiagonalDecomposition]) -> None:
    """Print the off-diagonal analysis report (Q4)."""
    print("\n" + "=" * 80)
    print("  Q4: Off-Diagonal Analysis — Genuine Success vs Temporary Survival")
    print("=" * 80)

    # Sort by gap size descending
    by_gap = sorted(decompositions, key=lambda d: d.gap, reverse=True)

    print(f"\n  {'Archetype':<28} {'Pos':>9} {'Dir':>8} {'Gap':>5} "
          f"{'GapCst':>7} {'PrcCst':>7} {'ExeCst':>7} {'Net':>6} "
          f"{'Sust':>5} {'Verdict':<24}")
    print("  " + "-" * 118)

    for d in by_gap:
        pos_str = f"{d.cap:.0%}/{d.ops:.0%}"
        print(f"  {d.archetype:<28} {pos_str:>9} {d.gap_direction:>8} "
              f"{d.gap:>4.0%} {d.gap_cost:>7.3f} {d.process_cost:>7.3f} "
              f"{d.execution_cost:>7.3f} {d.net_cost:>6.3f} "
              f"{d.sustainable_score:>5.3f} {d.verdict:<24}")

    # Key comparisons
    print(f"\n  Key Comparisons:")
    print(f"  {'-' * 76}")

    # #8 vs #12: same quadrant, opposite outcomes
    d8 = next(d for d in decompositions if "#8" in d.archetype)
    d12 = next(d for d in decompositions if "#12" in d.archetype)
    print(f"\n  Cap>Ops quadrant — deliberate vs crisis:")
    print(f"    #8  Reg Stage-Gate:   gap={d8.gap:.0%}, Time={d8.compensator_value:.2f} "
          f"-> gap_cost={d8.gap_cost:.3f}  [{d8.verdict}]")
    print(f"    #12 Crisis/Firefight: gap={d12.gap:.0%}, Time={d12.compensator_value:.2f} "
          f"-> gap_cost={d12.gap_cost:.3f}  [{d12.verdict}]")
    print(f"    Insight: Same Cap>Ops direction, but #8's Time=0.80 absorbs the gap while")
    print(f"    #12's Time=0.10 leaves the gap fully exposed. The difference is deliberate")
    print(f"    pacing (Time) vs crisis urgency.")

    # #4: Ops>Cap with automation
    d4 = next(d for d in decompositions if "#4" in d.archetype)
    print(f"\n  Ops>Cap quadrant — automation-sustained:")
    print(f"    #4  DevOps Native:    gap={d4.gap:.0%}, "
          f"{d4.compensator_name}={d4.compensator_value:.2f} "
          f"-> gap_cost={d4.gap_cost:.3f}  [{d4.verdict}]")
    print(f"    Insight: DevOps sustains Ops>Cap through Recovery (automation), not Overwork.")
    print(f"    If Recovery dropped to 0.10, gap_cost would be "
          f"{d4.gap * (1.0 - 0.10):.3f} — likely unsustainable.")


# ---------------------------------------------------------------------------
# Q5: Archetype Transition Paths
# ---------------------------------------------------------------------------

@dataclass
class TransitionStep:
    """One step along a transition path between archetypes."""
    t: float
    dims: list[int]
    sliders: list[float]
    position: tuple[float, float]
    zone_area: float
    position_viable: bool
    binding_constraint: str
    scores: tuple[float, float, float]  # viable, sufficient, sustainable


@dataclass
class TransitionPath:
    """Complete transition path between two archetypes."""
    source: str
    target: str
    steps: list[TransitionStep]
    critical_t: Optional[float]         # Where position leaves/enters zone
    zone_area_at_source: float
    zone_area_at_target: float
    key_dimension_changes: list[tuple[str, int, int]]
    key_slider_changes: list[tuple[str, float, float]]


def compute_transition_path(source: str, target: str,
                            n_steps: int = 11) -> TransitionPath:
    """Compute a transition path by interpolating between two archetype states.

    At each step t in [0, 1], interpolates dimensions (rounded to nearest
    integer), sliders (continuous), and default position (continuous).
    """
    dims_s = np.array(ARCHETYPE_DIMENSIONS[source], dtype=float)
    dims_t = np.array(ARCHETYPE_DIMENSIONS[target], dtype=float)
    sliders_s = np.array(ARCHETYPE_SLIDER_DEFAULTS[source])
    sliders_t = np.array(ARCHETYPE_SLIDER_DEFAULTS[target])
    pos_s = np.array(ARCHETYPE_DEFAULT_POSITIONS[source])
    pos_t = np.array(ARCHETYPE_DEFAULT_POSITIONS[target])

    steps = []
    prev_viable = None
    critical_t = None

    for i in range(n_steps):
        t = i / (n_steps - 1) if n_steps > 1 else 0.0

        # Interpolate
        dims_interp = list(np.round(dims_s + t * (dims_t - dims_s)).astype(int))
        sliders_interp = list(np.clip(sliders_s + t * (sliders_t - sliders_s), 0.0, 1.0))
        pos_interp = tuple(pos_s + t * (pos_t - pos_s))

        # Zone area
        zone_area = _cached_zone_area(dims_interp, sliders_interp)

        # Position assessment
        cap, ops = pos_interp
        v = test_viable(cap, ops, dims_interp, sliders_interp)
        s = test_sufficient(cap, ops, dims_interp, sliders_interp)
        u = test_sustainable(cap, ops, dims_interp, sliders_interp)
        combined = min(v, s, u)
        is_viable = combined >= PASS_THRESHOLD

        scores_dict = {"viable": v, "sufficient": s, "sustainable": u}
        binding = min(scores_dict, key=scores_dict.get)

        # Detect critical transition
        if prev_viable is not None and is_viable != prev_viable:
            critical_t = t

        prev_viable = is_viable

        steps.append(TransitionStep(
            t=t, dims=dims_interp, sliders=sliders_interp,
            position=pos_interp, zone_area=zone_area,
            position_viable=is_viable, binding_constraint=binding,
            scores=(v, s, u),
        ))

    # Key changes
    dim_changes = []
    for i in range(8):
        d_s = int(dims_s[i])
        d_t = int(dims_t[i])
        if d_s != d_t:
            dim_changes.append((DIMENSION_SHORT[i], d_s, d_t))

    slider_changes = []
    for i in range(4):
        s_s = float(sliders_s[i])
        s_t = float(sliders_t[i])
        if abs(s_s - s_t) > 0.05:
            slider_changes.append((SLIDER_SHORT[i], s_s, s_t))

    return TransitionPath(
        source=source, target=target, steps=steps,
        critical_t=critical_t,
        zone_area_at_source=steps[0].zone_area,
        zone_area_at_target=steps[-1].zone_area,
        key_dimension_changes=dim_changes,
        key_slider_changes=slider_changes,
    )


def render_transition_path(path: TransitionPath) -> str:
    """ASCII visualisation of a transition path on the grid."""
    lines = []

    # Header
    zone_delta = path.zone_area_at_target - path.zone_area_at_source
    lines.append(f"  {path.source} -> {path.target}")
    lines.append(f"  Zone area: {path.zone_area_at_source:.1f}% -> "
                 f"{path.zone_area_at_target:.1f}% ({zone_delta:+.1f}%)")
    if path.critical_t is not None:
        lines.append(f"  Critical transition at t={path.critical_t:.1f}")
    lines.append("")

    # Simple grid plot (20 wide x 11 tall)
    grid_w, grid_h = 41, 21
    plot = [[" "] * grid_w for _ in range(grid_h)]

    # Plot path points
    for step in path.steps:
        col = int(round(step.position[0] * (grid_w - 1)))
        row = int(round(step.position[1] * (grid_h - 1)))
        col = max(0, min(grid_w - 1, col))
        row = max(0, min(grid_h - 1, row))
        if step.position_viable:
            plot[row][col] = "#"
        else:
            plot[row][col] = "x"

    # Mark source and target
    s0 = path.steps[0]
    s1 = path.steps[-1]
    sc = int(round(s0.position[0] * (grid_w - 1)))
    sr = int(round(s0.position[1] * (grid_h - 1)))
    tc = int(round(s1.position[0] * (grid_w - 1)))
    tr = int(round(s1.position[1] * (grid_h - 1)))
    plot[max(0, min(grid_h - 1, sr))][max(0, min(grid_w - 1, sc))] = "S"
    plot[max(0, min(grid_h - 1, tr))][max(0, min(grid_w - 1, tc))] = "T"

    # Render (top = high Ops)
    for row_idx in range(grid_h - 1, -1, -1):
        ops_val = row_idx / (grid_h - 1)
        if row_idx % 5 == 0:
            label = f"  {ops_val:4.0%}|"
        else:
            label = "      |"
        lines.append(label + "".join(plot[row_idx]))

    lines.append("      +" + "-" * grid_w)
    lines.append("       0%        25%       50%       75%      100%")
    lines.append("                          Cap ->")
    lines.append("")
    lines.append("  S=source  T=target  #=viable  x=not viable")

    return "\n".join(lines)


def print_transition_step_table(path: TransitionPath) -> None:
    """Print step-by-step detail for a transition path."""
    print(f"\n  {'Step':>4} {'t':>5} {'Cap':>5} {'Ops':>5} {'Zone%':>7} "
          f"{'Pos':>5} {'V':>6} {'S':>6} {'U':>6} {'Binding':>14}")
    print(f"  {'-' * 72}")

    for step in path.steps:
        cap, ops = step.position
        v, s, u = step.scores
        pos_str = "PASS" if step.position_viable else "FAIL"
        print(f"  {step.t:>5.1f} {cap:>4.0%} {ops:>4.0%} "
              f"{step.zone_area:>6.1f}% {pos_str:>5} "
              f"{v:>6.3f} {s:>6.3f} {u:>6.3f} {step.binding_constraint:>14}")


def print_q5_report(paths: list[TransitionPath]) -> None:
    """Print the transition paths report (Q5)."""
    print("\n" + "=" * 80)
    print("  Q5: Archetype Transition Paths")
    print("=" * 80)

    for path in paths:
        print(f"\n{'~' * 80}")
        print(render_transition_path(path))

        # Dimension changes
        if path.key_dimension_changes:
            changes = ", ".join(f"{d}: {f}->{t}" for d, f, t in path.key_dimension_changes)
            print(f"  Dimension changes: {changes}")

        # Slider changes
        if path.key_slider_changes:
            changes = ", ".join(f"{s}: {f:.2f}->{t:.2f}" for s, f, t in path.key_slider_changes)
            print(f"  Slider changes: {changes}")

        print_transition_step_table(path)


# ---------------------------------------------------------------------------
# Q8: P8 Crisis Retrodiction
# ---------------------------------------------------------------------------

@dataclass
class CrisisStage:
    """One stage in a crisis escalation sequence."""
    label: str
    state_description: str
    sliders: list[float]
    zone_area: float
    position_viable: bool
    scores: tuple[float, float, float]


def compute_crisis_escalation(
    base_dims: list[int],
    base_sliders: list[float],
    eval_position: tuple[float, float],
    stages: list[tuple[str, str, np.ndarray]],
) -> list[CrisisStage]:
    """Compute zone area and position viability at each crisis stage.

    Args:
        base_dims: Dimension profile (stays constant).
        base_sliders: Structural slider baseline before any modifiers.
        eval_position: (Cap, Ops) position to evaluate at each stage.
        stages: List of (label, description, cumulative_modifier) tuples.
    """
    results = []
    cap, ops = eval_position

    for label, description, modifier in stages:
        sliders = list(np.clip(np.array(base_sliders) + modifier, 0.0, 1.0))
        zone_area = _cached_zone_area(base_dims, sliders)

        v = test_viable(cap, ops, base_dims, sliders)
        s = test_sufficient(cap, ops, base_dims, sliders)
        u = test_sustainable(cap, ops, base_dims, sliders)
        is_viable = min(v, s, u) >= PASS_THRESHOLD

        results.append(CrisisStage(
            label=label, state_description=description,
            sliders=sliders, zone_area=zone_area,
            position_viable=is_viable, scores=(v, s, u),
        ))

    return results


def build_p8_escalation_stages() -> list[tuple[str, str, np.ndarray]]:
    """Build the P8 crisis escalation stages with cumulative modifiers.

    Each stage applies modifiers cumulatively to the #6 Matrix Programme
    structural baseline.
    """
    zero = np.zeros(4)
    phase_late = PHASE_MODIFIERS["late_execution"]
    crisis_emerging = CRISIS_MODIFIERS["emerging"]
    crisis_acute = CRISIS_MODIFIERS["acute"]
    erosion_mod = EROSION_MODIFIERS["moderate"]

    return [
        ("Baseline",
         "Execution phase, no crisis",
         zero),

        ("Late execution",
         "phase=late_execution",
         phase_late),

        ("Late + emerging",
         "phase=late_execution, crisis=emerging",
         phase_late + crisis_emerging),

        ("Late + acute",
         "phase=late_execution, crisis=acute",
         phase_late + crisis_acute),

        ("Late + acute + erosion",
         "phase=late_execution, crisis=acute, erosion=moderate",
         phase_late + crisis_acute + erosion_mod),
    ]


def print_q8_report() -> None:
    """Print the P8 crisis retrodiction report (Q8)."""
    print("\n" + "=" * 80)
    print("  Q8: P8 Crisis Retrodiction")
    print("  Can the model predict the #6 Matrix Programme -> #12 Crisis collapse?")
    print("=" * 80)

    dims_6 = ARCHETYPE_DIMENSIONS["#6 Matrix Programme"]
    sliders_6 = list(ARCHETYPE_SLIDER_DEFAULTS["#6 Matrix Programme"])
    pos_6 = ARCHETYPE_DEFAULT_POSITIONS["#6 Matrix Programme"]
    pos_12 = ARCHETYPE_DEFAULT_POSITIONS["#12 Crisis/Firefight"]

    stages = build_p8_escalation_stages()

    # Evaluate at #6 default position
    print(f"\n  Evaluation at #6 default position ({pos_6[0]:.0%} Cap, {pos_6[1]:.0%} Ops):")
    print(f"  Base sliders: Inv={sliders_6[0]:.2f} Rec={sliders_6[1]:.2f} "
          f"Owk={sliders_6[2]:.2f} Time={sliders_6[3]:.2f}")
    print()

    results_6 = compute_crisis_escalation(dims_6, sliders_6, pos_6, stages)

    print(f"  {'Stage':<24} {'Sliders':>28} {'Zone%':>7} {'Pos':>5} "
          f"{'V':>6} {'S':>6} {'U':>6}")
    print(f"  {'-' * 88}")

    for r in results_6:
        slider_str = (f"I={r.sliders[0]:.2f} R={r.sliders[1]:.2f} "
                      f"O={r.sliders[2]:.2f} T={r.sliders[3]:.2f}")
        pos_str = "PASS" if r.position_viable else "FAIL"
        v, s, u = r.scores
        print(f"  {r.label:<24} {slider_str:>28} {r.zone_area:>6.1f}% {pos_str:>5} "
              f"{v:>6.3f} {s:>6.3f} {u:>6.3f}")

    # Find critical stage
    for i, r in enumerate(results_6):
        if not r.position_viable:
            if i == 0:
                print(f"\n  Result: Position was NEVER viable (even at baseline)")
            else:
                print(f"\n  Result: Position becomes unviable at stage '{r.label}'")
                print(f"  The {results_6[i-1].label} -> {r.label} transition is the crisis trigger.")
            break
    else:
        print(f"\n  Result: Position remains viable through all stages (unexpected)")

    # Also evaluate at #12 default position
    print(f"\n  Cross-check at #12 default position ({pos_12[0]:.0%} Cap, {pos_12[1]:.0%} Ops):")
    results_12 = compute_crisis_escalation(dims_6, sliders_6, pos_12, stages)

    for r in results_12:
        pos_str = "PASS" if r.position_viable else "FAIL"
        v, s, u = r.scores
        print(f"    {r.label:<24} {pos_str:>5} (V={v:.3f} S={s:.3f} U={u:.3f})")

    # Counterfactual: what if #6 had better baseline?
    print(f"\n  {'~' * 60}")
    print(f"  Counterfactual: What if #6 had Investment=0.80 and D8=3?")
    print(f"  (Better-funded, more coherent team)")
    print(f"  {'~' * 60}")

    # Modified baseline
    dims_cf = list(dims_6)
    dims_cf[7] = 3  # D8: Coherence 1 -> 3
    sliders_cf = list(sliders_6)
    sliders_cf[0] = 0.80  # Investment 0.65 -> 0.80

    print(f"\n  Modified sliders: Inv={sliders_cf[0]:.2f} Rec={sliders_cf[1]:.2f} "
          f"Owk={sliders_cf[2]:.2f} Time={sliders_cf[3]:.2f}")
    print(f"  Modified dims: D8={dims_cf[7]} (was {dims_6[7]})")
    print()

    results_cf = compute_crisis_escalation(dims_cf, sliders_cf, pos_6, stages)

    print(f"  {'Stage':<24} {'Sliders':>28} {'Zone%':>7} {'Pos':>5} "
          f"{'V':>6} {'S':>6} {'U':>6}")
    print(f"  {'-' * 88}")

    for r in results_cf:
        slider_str = (f"I={r.sliders[0]:.2f} R={r.sliders[1]:.2f} "
                      f"O={r.sliders[2]:.2f} T={r.sliders[3]:.2f}")
        pos_str = "PASS" if r.position_viable else "FAIL"
        v, s, u = r.scores
        print(f"  {r.label:<24} {slider_str:>28} {r.zone_area:>6.1f}% {pos_str:>5} "
              f"{v:>6.3f} {s:>6.3f} {u:>6.3f}")

    # Compare
    orig_fail_stage = None
    cf_fail_stage = None
    for i, r in enumerate(results_6):
        if not r.position_viable:
            orig_fail_stage = i
            break
    for i, r in enumerate(results_cf):
        if not r.position_viable:
            cf_fail_stage = i
            break

    if orig_fail_stage is not None and cf_fail_stage is not None:
        if cf_fail_stage > orig_fail_stage:
            print(f"\n  Counterfactual result: Crisis delayed from stage {orig_fail_stage} "
                  f"({results_6[orig_fail_stage].label}) to stage {cf_fail_stage} "
                  f"({results_cf[cf_fail_stage].label})")
            print(f"  Higher Investment + better Coherence buys "
                  f"{cf_fail_stage - orig_fail_stage} additional stage(s) of resilience.")
        elif cf_fail_stage == orig_fail_stage:
            print(f"\n  Counterfactual result: Crisis occurs at same stage "
                  f"({results_cf[cf_fail_stage].label}) — improvements insufficient.")
        else:
            print(f"\n  Counterfactual result: Unexpectedly fails earlier (investigate).")
    elif cf_fail_stage is None:
        print(f"\n  Counterfactual result: Position survives ALL escalation stages!")
        print(f"  Higher Investment + better Coherence would have PREVENTED the crisis.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run movement and transition analysis (Q4, Q5, Q8)."""
    print("=" * 80)
    print("  Movement & Transition Analysis")
    print("  Q4: Off-diagonal  |  Q5: Transitions  |  Q8: P8 retrodiction")
    print("=" * 80)

    # Q4: Off-diagonal decomposition
    decompositions = [decompose_off_diagonal(a) for a in ARCHETYPE_ORDER]
    print_q4_report(decompositions)

    # Q5: Transition paths
    transition_specs = [
        ("#1 Micro Startup", "#2 Small Agile"),
        ("#3 Scaling Startup", "#4 DevOps Native"),
        ("#3 Scaling Startup", "#5 Component Heroes"),
        ("#6 Matrix Programme", "#12 Crisis/Firefight"),
        ("#10 Legacy Maintenance", "#11 Modernisation"),
    ]

    print("\nComputing transition paths...")
    paths = [compute_transition_path(s, t) for s, t in transition_specs]
    print_q5_report(paths)

    # Q8: P8 crisis retrodiction
    print_q8_report()


if __name__ == "__main__":
    main()
