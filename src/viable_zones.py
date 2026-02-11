"""
Viable Zone Derivation for Cap/Ops Balance Simulation.

For each of the 15 structural archetypes, sweeps the Cap/Ops grid and
evaluates three success tests at every position:
    1. Viable    — are the project's stakes covered at this position?
    2. Sufficient — does this position deliver enough for stakeholders?
    3. Sustainable — can this position be maintained over time?

The viable zone is the region where all three tests pass simultaneously.
Zone shape, size, and binding constraints reveal which archetypes are
most precarious and where the "sweet spot" sits.

Depends on: src/dimension_slider_mapping.py (slider model, archetype data)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from dimension_slider_mapping import (
    ARCHETYPE_SLIDER_DEFAULTS,
    SLIDER_SHORT,
    DIMENSION_SHORT,
    to_categorical,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GRID_RESOLUTION = 101  # 0% to 100% in 1% steps
PASS_THRESHOLD = 0.5   # Score >= this means the test passes
SIGMOID_K = 12         # Sharpness of sigmoid transitions


# ---------------------------------------------------------------------------
# Archetype dimension profiles
# ---------------------------------------------------------------------------
# For archetypes with a persona mapping, we use the persona's validated
# dimension vector. For unmapped archetypes, we derive representative
# profiles from the archetype descriptions in SIMULATION_HANDOFF.
#
# Format: [D1, D2, D3, D4, D5, D6, D7, D8]

ARCHETYPE_DIMENSIONS = {
    "#1 Micro Startup":       [2, 5, 1, 1, 1, 1, 1, 5],  # P1
    "#2 Small Agile":         [2, 4, 2, 1, 2, 1, 2, 4],  # P2
    "#3 Scaling Startup":     [2, 3, 2, 1, 3, 1, 2, 2],  # P6
    "#4 DevOps Native":       [2, 4, 2, 1, 2, 1, 1, 2],  # P7
    "#5 Component Heroes":    [3, 3, 4, 2, 3, 2, 3, 2],  # Derived
    "#6 Matrix Programme":    [3, 2, 4, 2, 3, 3, 2, 1],  # Derived
    "#7 Outsource-Managed":   [3, 2, 3, 3, 4, 4, 3, 2],  # Derived
    "#8 Reg Stage-Gate":      [5, 1, 4, 5, 4, 3, 3, 3],  # Avg of P3/P5/P11
    "#9 Ent Balanced":        [3, 3, 3, 3, 5, 2, 3, 5],  # P10
    "#10 Legacy Maintenance":  [3, 2, 3, 3, 1, 1, 4, 3],  # P12
    "#11 Modernisation":      [3, 2, 3, 3, 2, 1, 4, 3],  # Derived
    "#12 Crisis/Firefight":   [3, 2, 4, 1, 3, 3, 2, 1],  # P8
    "#13 Planning/Pre-Deliv": [2, 3, 2, 2, 3, 1, 1, 4],  # P9
    "#14 Platform/Internal":  [1, 3, 2, 1, 3, 1, 3, 4],  # Derived
    "#15 Regulated Startup":  [4, 4, 2, 5, 2, 1, 1, 3],  # Derived
}

# Archetype default Cap/Ops positions (midpoints of the ranges in SIMULATION_HANDOFF)
ARCHETYPE_DEFAULT_POSITIONS = {
    "#1 Micro Startup":       (0.15, 0.20),
    "#2 Small Agile":         (0.25, 0.33),
    "#3 Scaling Startup":     (0.43, 0.43),
    "#4 DevOps Native":       (0.33, 0.70),
    "#5 Component Heroes":    (0.48, 0.48),
    "#6 Matrix Programme":    (0.48, 0.28),
    "#7 Outsource-Managed":   (0.58, 0.28),
    "#8 Reg Stage-Gate":      (0.70, 0.35),
    "#9 Ent Balanced":        (0.75, 0.75),
    "#10 Legacy Maintenance":  (0.15, 0.28),
    "#11 Modernisation":      (0.28, 0.33),
    "#12 Crisis/Firefight":   (0.43, 0.15),
    "#13 Planning/Pre-Deliv": (0.43, 0.05),
    "#14 Platform/Internal":  (0.33, 0.48),
    "#15 Regulated Startup":  (0.58, 0.20),
}

# Ordered list for consistent iteration
ARCHETYPE_ORDER = [
    "#1 Micro Startup", "#2 Small Agile", "#3 Scaling Startup",
    "#4 DevOps Native", "#5 Component Heroes", "#6 Matrix Programme",
    "#7 Outsource-Managed", "#8 Reg Stage-Gate", "#9 Ent Balanced",
    "#10 Legacy Maintenance", "#11 Modernisation", "#12 Crisis/Firefight",
    "#13 Planning/Pre-Deliv", "#14 Platform/Internal", "#15 Regulated Startup",
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _norm(d: int) -> float:
    """Normalise dimension value from 1-5 to 0-1."""
    return (d - 1) / 4.0


def _sigmoid(x: float) -> float:
    """Smooth sigmoid with configurable sharpness."""
    return 1.0 / (1.0 + math.exp(-SIGMOID_K * x))


# ---------------------------------------------------------------------------
# Floor functions
# ---------------------------------------------------------------------------

def compute_cap_floor(dims: list[int]) -> float:
    """Minimum viable capability given project stakes.

    Driven by consequence (D1), complexity (D3), regulation (D4),
    and outsourcing (D6). Higher stakes -> higher floor.
    """
    d1 = _norm(dims[0])  # Consequence
    d3 = _norm(dims[2])  # Complexity
    d4 = _norm(dims[3])  # Regulation
    d6 = _norm(dims[5])  # Outsourcing

    floor = 0.10 + 0.15 * d1 + 0.10 * d3 + 0.15 * d4 + 0.05 * d6
    return min(floor, 0.80)


def compute_ops_floor(dims: list[int]) -> float:
    """Minimum sufficient operations given market demands.

    Driven by market pressure (D2) and complexity (D3).
    Higher pressure -> higher floor.
    """
    d2 = _norm(dims[1])  # Market pressure
    d3 = _norm(dims[2])  # Complexity

    floor = 0.08 + 0.20 * d2 + 0.10 * d3
    return min(floor, 0.60)


# ---------------------------------------------------------------------------
# Three success tests
# ---------------------------------------------------------------------------

def test_viable(cap: float, ops: float,
                dims: list[int], sliders: list[float]) -> float:
    """Test 1: Are the project's stakes covered at this Cap/Ops position?

    Recovery capacity provides a buffer — organisations with high recovery
    can tolerate being slightly below the capability floor.
    """
    cap_floor = compute_cap_floor(dims)
    recovery = sliders[1]

    # Recovery provides a safety buffer on the cap floor
    effective_cap = cap + recovery * 0.15
    temperature = 0.08

    return _sigmoid((effective_cap - cap_floor) / temperature)


def test_sufficient(cap: float, ops: float,
                    dims: list[int], sliders: list[float]) -> float:
    """Test 2: Does this position deliver enough for stakeholders?

    Overwork capacity compensates for low operational performance —
    teams working harder can ship despite weak operational metrics.
    """
    ops_floor = compute_ops_floor(dims)
    overwork = sliders[2]

    # Overwork compensates for ops deficit
    effective_ops = ops + overwork * 0.15
    temperature = 0.08

    return _sigmoid((effective_ops - ops_floor) / temperature)


def test_sustainable(cap: float, ops: float,
                     dims: list[int], sliders: list[float]) -> float:
    """Test 3: Can this position be maintained over time?

    Four cost components:
        1. Gap cost     — off-diagonal positions are inherently costly
        2. Debt cost    — very low maturity accumulates compounding debt
        3. Process cost — high capability requires ongoing investment to maintain
        4. Execution cost — high operations requires ongoing capacity to sustain

    These create both lower bounds (debt cost) and upper bounds (process/
    execution costs) on the viable zone, with the bounds depending on
    slider values. A startup can't sustain Cap=80% (no investment budget
    for process maintenance). An enterprise can.
    """
    investment = sliders[0]
    recovery = sliders[1]
    overwork = sliders[2]
    time_cap = sliders[3]

    # Gap cost: off-diagonal positions are costly
    gap = abs(cap - ops)
    if cap > ops:
        # Cap > Ops: process without execution -> needs time capacity
        gap_cost = gap * (1.0 - time_cap)
    else:
        # Ops > Cap: execution without process -> needs overwork OR recovery
        # Recovery (automation, resilient processes) is an alternative to human
        # overwork for sustaining ops beyond formal capability (e.g. DevOps)
        gap_cost = gap * (1.0 - max(overwork, recovery))

    # Debt cost: very low maturity accumulates compounding debt
    avg_maturity = (cap + ops) / 2.0
    debt_cost = max(0.0, 0.30 - avg_maturity) * 2.0

    # Process maintenance cost: high cap requires investment to maintain
    # governance, documentation, standards, quality gates
    process_cost = cap * 0.45 * (1.0 - investment)

    # Execution overhead: high ops requires capacity to sustain delivery
    # cadence, automation, monitoring, incident response
    # Recovery (automation) can sustain execution cadence alongside overwork/time
    best_ops_capacity = max(overwork, time_cap, recovery)
    execution_cost = ops * 0.35 * (1.0 - best_ops_capacity)

    # Total cost with investment relief
    total_cost = gap_cost + debt_cost + process_cost + execution_cost
    investment_relief = investment * 0.10
    temperature = 0.08

    return _sigmoid((0.35 - (total_cost - investment_relief)) / temperature)


def combined_score(cap: float, ops: float,
                   dims: list[int], sliders: list[float]) -> float:
    """Combined success: minimum of all three test scores."""
    return min(
        test_viable(cap, ops, dims, sliders),
        test_sufficient(cap, ops, dims, sliders),
        test_sustainable(cap, ops, dims, sliders),
    )


def raw_margins(cap: float, ops: float,
                dims: list[int], sliders: list[float]) -> tuple[float, float, float]:
    """Pre-sigmoid margins for all three tests.

    Returns the sigmoid input values before squashing. Positive = passing,
    negative = failing, zero = exactly at threshold. The magnitude tells
    you how far inside/outside the viable zone the position is.

    Returns: (viable_margin, sufficient_margin, sustainable_margin)
    """
    # Viable margin
    cap_floor = compute_cap_floor(dims)
    recovery = sliders[1]
    effective_cap = cap + recovery * 0.15
    viable_m = (effective_cap - cap_floor) / 0.08

    # Sufficient margin
    ops_floor = compute_ops_floor(dims)
    overwork = sliders[2]
    effective_ops = ops + overwork * 0.15
    sufficient_m = (effective_ops - ops_floor) / 0.08

    # Sustainable margin (replicate cost arithmetic)
    investment = sliders[0]
    time_cap = sliders[3]
    gap = abs(cap - ops)
    if cap > ops:
        gap_cost = gap * (1.0 - time_cap)
    else:
        gap_cost = gap * (1.0 - max(overwork, recovery))
    avg_maturity = (cap + ops) / 2.0
    debt_cost = max(0.0, 0.30 - avg_maturity) * 2.0
    process_cost = cap * 0.45 * (1.0 - investment)
    best_ops_capacity = max(overwork, time_cap, recovery)
    execution_cost = ops * 0.35 * (1.0 - best_ops_capacity)
    total_cost = gap_cost + debt_cost + process_cost + execution_cost
    investment_relief = investment * 0.10
    sustainable_m = (0.35 - (total_cost - investment_relief)) / 0.08

    return viable_m, sufficient_m, sustainable_m


def cost_breakdown(cap: float, ops: float,
                   dims: list[int], sliders: list[float]) -> dict:
    """Full cost decomposition at a specific Cap/Ops position.

    Returns a dict with all individual cost components, compensator
    information, and plain-English explanations of what's driving
    the result.
    """
    investment = sliders[0]
    recovery = sliders[1]
    overwork = sliders[2]
    time_cap = sliders[3]

    # Floors
    cap_floor = compute_cap_floor(dims)
    ops_floor = compute_ops_floor(dims)
    cap_headroom = cap - cap_floor
    ops_headroom = ops - ops_floor

    # Gap analysis
    gap = abs(cap - ops)
    if abs(cap - ops) < 0.02:
        gap_direction = "Balanced"
        gap_compensator = "N/A"
        gap_compensator_value = 0.0
        gap_cost = 0.0
    elif cap > ops:
        gap_direction = "Cap > Ops"
        gap_compensator = "Time"
        gap_compensator_value = time_cap
        gap_cost = gap * (1.0 - time_cap)
    else:
        gap_direction = "Ops > Cap"
        gap_compensator = "Recovery" if recovery >= overwork else "Overwork"
        gap_compensator_value = max(overwork, recovery)
        gap_cost = gap * (1.0 - max(overwork, recovery))

    # Debt cost
    avg_maturity = (cap + ops) / 2.0
    debt_cost = max(0.0, 0.30 - avg_maturity) * 2.0

    # Process cost
    process_cost = cap * 0.45 * (1.0 - investment)

    # Execution cost
    best_ops_capacity = max(overwork, time_cap, recovery)
    if time_cap >= overwork and time_cap >= recovery:
        exec_compensator = "Time"
    elif recovery >= overwork:
        exec_compensator = "Recovery"
    else:
        exec_compensator = "Overwork"
    execution_cost = ops * 0.35 * (1.0 - best_ops_capacity)

    # Totals
    total_cost = gap_cost + debt_cost + process_cost + execution_cost
    investment_relief = investment * 0.10
    net_cost = total_cost - investment_relief
    threshold = 0.35
    headroom = threshold - net_cost

    # Find the dominant cost
    costs = {
        "Gap cost": gap_cost,
        "Debt cost": debt_cost,
        "Process cost": process_cost,
        "Execution cost": execution_cost,
    }
    dominant = max(costs, key=costs.get)

    return {
        # Position info
        "cap": cap,
        "ops": ops,
        "gap": gap,
        "gap_direction": gap_direction,
        "gap_compensator": gap_compensator,
        "gap_compensator_value": gap_compensator_value,
        # Floors
        "cap_floor": cap_floor,
        "ops_floor": ops_floor,
        "cap_headroom": cap_headroom,
        "ops_headroom": ops_headroom,
        # Individual costs
        "gap_cost": gap_cost,
        "debt_cost": debt_cost,
        "process_cost": process_cost,
        "execution_cost": execution_cost,
        "exec_compensator": exec_compensator,
        "exec_compensator_value": best_ops_capacity,
        # Totals
        "total_cost": total_cost,
        "investment_relief": investment_relief,
        "net_cost": net_cost,
        "threshold": threshold,
        "headroom": headroom,
        "sustainable": headroom >= 0,
        # Dominant cost
        "dominant_cost": dominant,
        "dominant_value": costs[dominant],
    }


# ---------------------------------------------------------------------------
# Grid sweep
# ---------------------------------------------------------------------------

def sweep_grid(dims: list[int], sliders: list[float],
               resolution: int = GRID_RESOLUTION) -> np.ndarray:
    """Sweep the Cap/Ops grid and evaluate all three tests.

    Returns array of shape (resolution, resolution, 4):
        [:, :, 0] = viable scores
        [:, :, 1] = sufficient scores
        [:, :, 2] = sustainable scores
        [:, :, 3] = combined (min of all three)

    Axis 0 = Ops (row 0 = Ops 0%, row N = Ops 100%)
    Axis 1 = Cap (col 0 = Cap 0%, col N = Cap 100%)
    """
    grid = np.zeros((resolution, resolution, 4))
    steps = np.linspace(0.0, 1.0, resolution)

    for i, ops in enumerate(steps):
        for j, cap in enumerate(steps):
            v = test_viable(cap, ops, dims, sliders)
            s = test_sufficient(cap, ops, dims, sliders)
            u = test_sustainable(cap, ops, dims, sliders)
            grid[i, j, 0] = v
            grid[i, j, 1] = s
            grid[i, j, 2] = u
            grid[i, j, 3] = min(v, s, u)

    return grid


def sweep_grid_gradient(dims: list[int], sliders: list[float],
                        resolution: int = GRID_RESOLUTION) -> np.ndarray:
    """Sweep the Cap/Ops grid and return pre-sigmoid margin values.

    Returns array of shape (resolution, resolution, 4):
        [:, :, 0] = viable margin
        [:, :, 1] = sufficient margin
        [:, :, 2] = sustainable margin
        [:, :, 3] = combined (min of all three)

    Positive = passing, negative = failing. Magnitude indicates how far
    inside/outside the viable zone. Gives smooth gradients unlike the
    binary sigmoid output.
    """
    grid = np.zeros((resolution, resolution, 4))
    steps = np.linspace(0.0, 1.0, resolution)

    for i, ops in enumerate(steps):
        for j, cap in enumerate(steps):
            vm, sm, um = raw_margins(cap, ops, dims, sliders)
            grid[i, j, 0] = vm
            grid[i, j, 1] = sm
            grid[i, j, 2] = um
            grid[i, j, 3] = min(vm, sm, um)

    return grid


# ---------------------------------------------------------------------------
# Zone analysis
# ---------------------------------------------------------------------------

@dataclass
class ZoneAnalysis:
    """Results of viable zone analysis for one archetype."""
    archetype: str
    dims: list[int]
    sliders: list[float]
    default_pos: tuple[float, float]

    # Zone metrics
    zone_area_pct: float        # % of total grid that passes all three tests
    cap_range: tuple[float, float]  # Min/max cap within viable zone
    ops_range: tuple[float, float]  # Min/max ops within viable zone

    # Default position assessment
    default_viable: float
    default_sufficient: float
    default_sustainable: float
    default_combined: float
    default_passes: bool

    # Binding constraint at default position
    binding_constraint: str     # Which test has the lowest score

    # Floor values
    cap_floor: float
    ops_floor: float

    # Grid data (for heatmap rendering)
    grid: np.ndarray


def analyse_archetype(archetype: str) -> ZoneAnalysis:
    """Full viable zone analysis for one archetype."""
    dims = ARCHETYPE_DIMENSIONS[archetype]
    sliders = ARCHETYPE_SLIDER_DEFAULTS[archetype]
    default_cap, default_ops = ARCHETYPE_DEFAULT_POSITIONS[archetype]

    # Sweep grid
    grid = sweep_grid(dims, sliders)
    combined = grid[:, :, 3]

    # Find viable zone (combined >= threshold)
    viable_mask = combined >= PASS_THRESHOLD
    zone_area_pct = float(np.mean(viable_mask)) * 100.0

    # Zone boundaries
    if np.any(viable_mask):
        viable_coords = np.argwhere(viable_mask)
        ops_indices = viable_coords[:, 0]
        cap_indices = viable_coords[:, 1]
        steps = np.linspace(0.0, 1.0, GRID_RESOLUTION)
        cap_range = (float(steps[cap_indices.min()]), float(steps[cap_indices.max()]))
        ops_range = (float(steps[ops_indices.min()]), float(steps[ops_indices.max()]))
    else:
        cap_range = (0.0, 0.0)
        ops_range = (0.0, 0.0)

    # Default position assessment
    dv = test_viable(default_cap, default_ops, dims, sliders)
    ds = test_sufficient(default_cap, default_ops, dims, sliders)
    du = test_sustainable(default_cap, default_ops, dims, sliders)
    dc = min(dv, ds, du)

    scores = {"viable": dv, "sufficient": ds, "sustainable": du}
    binding = min(scores, key=scores.get)

    return ZoneAnalysis(
        archetype=archetype,
        dims=dims,
        sliders=sliders,
        default_pos=(default_cap, default_ops),
        zone_area_pct=zone_area_pct,
        cap_range=cap_range,
        ops_range=ops_range,
        default_viable=dv,
        default_sufficient=ds,
        default_sustainable=du,
        default_combined=dc,
        default_passes=dc >= PASS_THRESHOLD,
        binding_constraint=binding,
        cap_floor=compute_cap_floor(dims),
        ops_floor=compute_ops_floor(dims),
        grid=grid,
    )


def analyse_all_archetypes() -> list[ZoneAnalysis]:
    """Analyse all 15 archetypes and return sorted by zone area."""
    results = [analyse_archetype(a) for a in ARCHETYPE_ORDER]
    return results


# ---------------------------------------------------------------------------
# ASCII heatmap
# ---------------------------------------------------------------------------

def render_heatmap(analysis: ZoneAnalysis, width: int = 61, height: int = 31) -> str:
    """Render an ASCII heatmap of the viable zone.

    Legend:
        # = all three tests pass (viable zone)
        V = only viability fails
        S = only sufficiency fails
        U = only sustainability fails
        . = multiple tests fail
        @ = default position (overlaid)
    """
    grid = analysis.grid
    res = grid.shape[0]
    lines = []

    # Title
    lines.append(f"  {analysis.archetype}  (zone: {analysis.zone_area_pct:.1f}% of grid)")
    lines.append(f"  Cap floor: {analysis.cap_floor:.0%}  Ops floor: {analysis.ops_floor:.0%}  "
                 f"Sliders: Inv={analysis.sliders[0]:.2f} Rec={analysis.sliders[1]:.2f} "
                 f"Owk={analysis.sliders[2]:.2f} Time={analysis.sliders[3]:.2f}")
    lines.append("")

    # Map default position to grid coordinates
    def_j = int(round(analysis.default_pos[0] * (width - 1)))
    def_i = int(round(analysis.default_pos[1] * (height - 1)))

    # Render grid (top = high Ops, bottom = low Ops)
    for row in range(height - 1, -1, -1):
        ops_val = row / (height - 1)
        # Row label
        if row % 5 == 0:
            label = f"{ops_val:4.0%}|"
        else:
            label = "    |"

        chars = []
        for col in range(width):
            cap_val = col / (width - 1)

            # Sample from grid (nearest neighbour)
            gi = int(round(ops_val * (res - 1)))
            gj = int(round(cap_val * (res - 1)))

            v = grid[gi, gj, 0] >= PASS_THRESHOLD
            s = grid[gi, gj, 1] >= PASS_THRESHOLD
            u = grid[gi, gj, 2] >= PASS_THRESHOLD

            # Default position marker
            if row == def_i and col == def_j:
                chars.append("@")
            elif v and s and u:
                chars.append("#")
            elif not v and s and u:
                chars.append("V")
            elif v and not s and u:
                chars.append("S")
            elif v and s and not u:
                chars.append("U")
            else:
                chars.append(".")

        lines.append(label + "".join(chars))

    # X-axis
    lines.append("    +" + "-" * width)
    x_labels = "     "
    for col in range(0, width, 10):
        cap_val = col / (width - 1)
        x_labels += f"{cap_val:<10.0%}"
    lines.append(x_labels)
    lines.append("     " + " " * (width // 2 - 2) + "Cap ->")
    lines.append("")
    lines.append(f"  Legend: # viable zone  @ default position  "
                 f"V viability fails  S sufficiency fails  U sustainability fails  . multiple fail")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Summary output
# ---------------------------------------------------------------------------

def print_summary_table(results: list[ZoneAnalysis]) -> None:
    """Print a summary table across all archetypes."""
    print("\n=== Viable Zone Summary (All 15 Archetypes) ===\n")
    print(f"{'#':<3} {'Archetype':<22} {'Zone%':>6} {'CapFloor':>8} {'OpsFloor':>8} "
          f"{'CapRange':>12} {'OpsRange':>12} {'Default':>8} {'Binding':>14}")
    print("-" * 105)

    for r in results:
        cap_r = f"{r.cap_range[0]:.0%}-{r.cap_range[1]:.0%}"
        ops_r = f"{r.ops_range[0]:.0%}-{r.ops_range[1]:.0%}"
        pass_str = "PASS" if r.default_passes else "FAIL"
        idx = r.archetype.split(" ")[0]
        name = " ".join(r.archetype.split(" ")[1:])
        print(f"{idx:<3} {name:<22} {r.zone_area_pct:>5.1f}% {r.cap_floor:>7.0%} {r.ops_floor:>7.0%} "
              f"{cap_r:>12} {ops_r:>12} {pass_str:>8} {r.binding_constraint:>14}")


def print_precariousness_ranking(results: list[ZoneAnalysis]) -> None:
    """Rank archetypes from most to least precarious (smallest viable zone)."""
    ranked = sorted(results, key=lambda r: r.zone_area_pct)

    print("\n=== Precariousness Ranking (smallest viable zone = most precarious) ===\n")
    print(f"{'Rank':<5} {'Archetype':<28} {'Zone%':>6} {'Default':>8} {'Binding':>14}")
    print("-" * 65)

    for i, r in enumerate(ranked, 1):
        pass_str = "PASS" if r.default_passes else "FAIL"
        print(f"{i:<5} {r.archetype:<28} {r.zone_area_pct:>5.1f}% {pass_str:>8} {r.binding_constraint:>14}")


def print_default_position_detail(results: list[ZoneAnalysis]) -> None:
    """Show detailed test scores at each archetype's default position."""
    print("\n=== Default Position Assessment (All 15 Archetypes) ===\n")
    print(f"{'Archetype':<28} {'Cap':>5} {'Ops':>5} {'Viable':>7} {'Suff':>7} {'Sust':>7} "
          f"{'Combined':>9} {'Result':>7}")
    print("-" * 85)

    for r in results:
        cap, ops = r.default_pos
        pass_str = "PASS" if r.default_passes else "FAIL"
        print(f"{r.archetype:<28} {cap:>4.0%} {ops:>4.0%} {r.default_viable:>7.3f} "
              f"{r.default_sufficient:>7.3f} {r.default_sustainable:>7.3f} "
              f"{r.default_combined:>9.3f} {pass_str:>7}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run viable zone analysis for all 15 archetypes."""
    print("=" * 70)
    print("  Viable Zone Derivation: Cap/Ops Grid Analysis")
    print("  Three-test model: Viable × Sufficient × Sustainable")
    print("=" * 70)

    # Analyse all archetypes
    results = analyse_all_archetypes()

    # Summary table
    print_summary_table(results)

    # Default position detail
    print_default_position_detail(results)

    # Precariousness ranking
    print_precariousness_ranking(results)

    # Heatmaps for key archetypes (most precarious, most stable, and two
    # interesting mid-range cases)
    key_archetypes = [
        "#1 Micro Startup",       # Most precarious (hypothesis)
        "#8 Reg Stage-Gate",      # Cap-constrained
        "#9 Ent Balanced",        # Widest zone (hypothesis)
        "#12 Crisis/Firefight",   # Collapsed zone (hypothesis)
        "#4 DevOps Native",       # Ops-heavy diagonal
        "#15 Regulated Startup",  # Tension between regulation and resources
    ]

    print("\n=== Heatmaps for Key Archetypes ===")
    for archetype in key_archetypes:
        r = next(x for x in results if x.archetype == archetype)
        print()
        print(render_heatmap(r))
        print()


if __name__ == "__main__":
    main()
