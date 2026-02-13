"""
MIRA-to-Simulation Bridge — maps MIRA assessment output to simulation inputs.

Accepts MIRA's project context (regulatory standards, scale, delivery model,
etc.) and optionally assessment scores/answers. Derives the 8 simulation
dimensions (1-5 each), selects the nearest archetype from 15 available,
and returns a simulation-ready payload.

Run standalone to validate against the 12 MIRA personas:
    cd src
    python mira_bridge.py

Depends on: viable_zones.py (archetype dimension profiles)
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from viable_zones import ARCHETYPE_DIMENSIONS, ARCHETYPE_ORDER


# ---------------------------------------------------------------------------
# Regulatory consequence tiers — maps standard names to D1 Consequence
# ---------------------------------------------------------------------------

_LIFE_SAFETY_STANDARDS = {
    "fda_21_cfr_11", "iso_13485", "iec_62443", "iso_26262",
    "iec_62304", "aspice", "iso_14971", "iso_26262",
}
_FINANCIAL_STANDARDS = {
    "sox", "pci_dss", "hipaa", "fedramp",
}
_INDUSTRY_STANDARDS = {
    "iso_27001", "iso_9001", "iso_9001_certified", "gdpr",
}
# Standards that don't clearly fit a tier (MIRA allows freeform "other")
_MISC_STANDARDS = {"other"}

# Delivery model speed ranking (higher = faster)
_DELIVERY_SPEED = {
    "continuous": 5,
    "devops": 5,
    "agile": 4,
    "hybrid_agile": 3,
    "hybrid_traditional": 2,
    "v_model": 1,
    "waterfall": 1,
    "traditional": 1,
}

# Product stage → base market pressure
_STAGE_PRESSURE = {
    "startup": 5,
    "growth": 4,
    "mature": 2,
    "legacy": 1,
}

# Scale → base complexity (enterprise=4 not 5; scale != complexity for
# well-run organisations — complexity comes from chaos, not just size)
_SCALE_COMPLEXITY = {
    "small": 1,
    "medium": 2,
    "large": 3,
    "enterprise": 4,
}

# Audit frequency → regulation boost
_AUDIT_BOOST = {
    "none": 0,
    "annual": 0,
    "bi_annual": 1,
    "quarterly": 1,
    "continuous": 2,
}


# ---------------------------------------------------------------------------
# Dimension derivation
# ---------------------------------------------------------------------------

def _derive_d1_consequence(ctx: dict, _answers: dict) -> int:
    """D1 Consequence — from regulatory_standards + scale.

    Scale matters even without regulation: a large company's internal
    platform failure affects more people than a startup's.
    """
    standards = set(ctx.get("regulatory_standards", []))
    scale = ctx.get("scale", "medium")

    # Base from regulatory tier
    # Also check scoring_context.regulatory as a single string (MIRA format)
    scoring_reg = ctx.get("regulatory", "")
    if scoring_reg and scoring_reg != "none":
        standards.add(scoring_reg)

    if standards & _LIFE_SAFETY_STANDARDS:
        base = 5
    elif standards & _FINANCIAL_STANDARDS:
        base = 4
    elif standards & _INDUSTRY_STANDARDS:
        base = 3
    elif standards - _MISC_STANDARDS:
        base = 2  # Known standards not in any tier
    elif standards & _MISC_STANDARDS:
        base = 2  # "other" = some governance exists
    else:
        base = 1

    # Scale bonus — larger scale = higher consequence even without regulation
    scale_bonus = {"small": 0, "medium": 0, "large": 1, "enterprise": 2}
    base += scale_bonus.get(scale, 0)

    return max(1, min(5, base))


def _derive_d2_market_pressure(ctx: dict, _answers: dict) -> int:
    """D2 Market Pressure — from product_stage + delivery_model speed + phase.

    Planning/initiation phases haven't entered market yet, so pressure is
    lower. Uses traditional rounding (0.5 rounds up) to avoid Python's
    banker's rounding giving unintuitive results at half-integer boundaries.
    """
    stage = ctx.get("product_stage", "growth")
    delivery = ctx.get("delivery_model", "hybrid_agile")
    phase = ctx.get("project_phase", "execution")

    stage_score = _STAGE_PRESSURE.get(stage, 3)
    delivery_score = _DELIVERY_SPEED.get(delivery, 3)

    # Average — fast delivery amplifies stage pressure
    combined = (stage_score + delivery_score) / 2.0

    # Planning/initiation = not yet shipping, reduced market pressure
    if phase in ("planning", "initiation", "early_dev"):
        combined -= 0.5

    # Traditional rounding (0.5 rounds up, not banker's rounding)
    return max(1, min(5, int(combined + 0.5)))


def _derive_d3_complexity(ctx: dict, answers: dict) -> int:
    """D3 Complexity — from ARC-O1 answer (preferred) or scale.

    For small/medium orgs, ARC-O1 often reflects code mess rather than
    genuine architectural complexity. A small startup with ARC-O1=7 has
    tangled code, not a complex multi-service architecture. Cap the
    ARC-O1-derived value at scale_val + 1 for these organisations.
    """
    arc_o1 = answers.get("ARC-O1")
    scale = ctx.get("scale", "medium")
    scale_val = _SCALE_COMPLEXITY.get(scale, 2)

    if arc_o1 is not None:
        # ARC-O1 is 1-10 slider; map to 1-5
        arc_val = max(1, min(5, math.ceil(arc_o1 / 2)))
        # Small/medium orgs: cap complexity — mess != architecture
        if scale in ("small", "medium"):
            return min(scale_val + 1, arc_val)
        return arc_val

    return scale_val


def _derive_d4_regulation(ctx: dict, _answers: dict) -> int:
    """D4 Regulation — from regulatory_standards + audit_frequency + context.

    Life-safety regulation at large/enterprise scale = maximum regulatory
    burden (base 5). Traditional delivery models (waterfall, V-model) are
    often CHOSEN because of regulation — their presence signals regulatory
    pressure beyond what the standard name alone implies.
    """
    standards = set(ctx.get("regulatory_standards", []))
    audit = ctx.get("audit_frequency", "none")
    scale = ctx.get("scale", "medium")
    delivery = ctx.get("delivery_model", "hybrid_agile")

    # Also check scoring_context.regulatory (MIRA single-value format)
    scoring_reg = ctx.get("regulatory", "")
    if scoring_reg and scoring_reg != "none":
        standards.add(scoring_reg)

    # Remove "none" if present
    standards.discard("none")

    if not standards:
        return 1

    # Base level from highest-tier standard
    if standards & _LIFE_SAFETY_STANDARDS:
        base = 4
        # Life-safety at scale = maximum regulatory burden
        if scale in ("large", "enterprise"):
            base = 5
    elif standards & _FINANCIAL_STANDARDS:
        base = 3
    elif standards & _INDUSTRY_STANDARDS:
        base = 2
    else:
        base = 2

    # Traditional delivery model signals regulatory pressure
    if delivery in ("waterfall", "v_model", "traditional"):
        base += 1

    # Boost from audit frequency
    boost = _AUDIT_BOOST.get(audit, 0)
    return max(1, min(5, base + boost))


def _derive_d5_team_stability(ctx: dict, answers: dict) -> int:
    """D5 Team Stability — from GOV-O2 answer (preferred) or stage + scale."""
    gov_o2 = answers.get("GOV-O2")
    if gov_o2 is not None:
        # GOV-O2 is 0-100 (% teams with dedicated test leads)
        if gov_o2 >= 80:
            return 5
        if gov_o2 >= 60:
            return 4
        if gov_o2 >= 40:
            return 3
        if gov_o2 >= 20:
            return 2
        return 1

    # Fallback: product_stage × scale heuristic
    stage = ctx.get("product_stage", "growth")
    scale = ctx.get("scale", "medium")

    # Stability correlates with maturity and size.
    # Legacy = people leaving/retiring, startup = no team yet.
    # Growth = team exists and is building (moderate stability).
    stage_stability = {"legacy": 1, "startup": 1, "growth": 3, "mature": 4}
    scale_stability = {"small": 1, "medium": 3, "large": 4, "enterprise": 5}

    s = stage_stability.get(stage, 2)
    c = scale_stability.get(scale, 3)
    return max(1, min(5, round((s + c) / 2.0)))


def _derive_d6_outsourcing(ctx: dict, answers: dict) -> int:
    """D6 Outsourcing — from TPT-O1 supplier count or has_third_party."""
    tpt_o1 = answers.get("TPT-O1")
    if tpt_o1 is not None:
        count = int(tpt_o1) if not isinstance(tpt_o1, (list, tuple)) else len(tpt_o1)
        if count == 0:
            return 1
        if count == 1:
            return 2
        if count <= 3:
            return 3
        if count <= 6:
            return 4
        return 5

    # Check TPP-C2 (boolean: has third-party supplier)
    tpp_c2 = answers.get("TPP-C2")
    if tpp_c2 is True:
        return 3  # Third-party involved, degree unknown

    # Fallback: has_third_party from context
    if ctx.get("has_third_party", False):
        return 3  # Known third-party involvement, degree unknown
    return 1  # Assume in-house


def _derive_d7_lifecycle(ctx: dict, _answers: dict) -> int:
    """D7 Lifecycle — from project_phase + product_stage."""
    phase = ctx.get("project_phase", "execution")
    stage = ctx.get("product_stage", "growth")

    phase_map = {
        # Standard simulation phases
        "initiation": 1,
        "planning": 1,
        "execution": 2,  # adjusted by stage below
        "maturation": 4,
        "transition": 4,
        "closure": 4,
        "maintenance": 4,  # 4 not 5 — matches #10/#11 archetype profiles
        # MIRA-specific phase names
        "early_dev": 1,
        "mid_dev": 2,       # mid-development = early-mid lifecycle
        "testing_phase": 3,  # testing = active mid-lifecycle
    }

    base = phase_map.get(phase, 3)

    # Execution/mid-dev phase varies by product stage
    if phase in ("execution", "mid_dev"):
        if stage in ("mature", "legacy"):
            base = 3
        else:
            base = 2

    # Legacy product stage pushes lifecycle up regardless
    if stage == "legacy" and base < 4:
        base = 4

    return max(1, min(5, base))


def _derive_d8_coherence(ctx: dict, _answers: dict) -> int:
    """D8 Coherence — from delivery_model + scale + product_stage + phase.

    DevOps teams have strong LOCAL coherence but can have poor CROSS-TEAM
    coherence (silo mentality). Growth stage = peak fragmentation risk.
    Maturation/transition phases suggest integration pressure = lower coherence.
    """
    delivery = ctx.get("delivery_model", "hybrid_agile")
    scale = ctx.get("scale", "medium")
    stage = ctx.get("product_stage", "growth")
    phase = ctx.get("project_phase", "execution")

    # Start with base coherence from delivery model + scale
    if delivery in ("devops", "continuous"):
        # DevOps: strong locally but silo risk grows with scale
        if scale == "small":
            base = 4
        elif scale == "medium":
            base = 3  # Medium devops = silo risk emerging
        else:
            base = 4  # Large/enterprise devops that WORKS = high coherence
    elif delivery in ("agile", "hybrid_agile"):
        if scale in ("small", "medium"):
            base = 4
        elif scale == "large":
            base = 3
        else:
            base = 3
    elif delivery in ("waterfall", "traditional", "v_model", "hybrid_traditional"):
        if scale in ("small", "medium"):
            base = 3
        elif scale == "large":
            base = 2
        else:
            base = 1
    else:
        base = 3

    # DevOps at startup/growth with non-trivial scale = silo risk
    # (teams optimise locally, ignore cross-team integration)
    if (stage in ("startup", "growth")
            and delivery in ("devops", "continuous")
            and scale in ("medium", "large")):
        base = min(base, 2)

    # Stage adjustments
    if stage == "startup" and scale == "small":
        base = max(base, 5)  # Forced alignment by survival
    elif stage == "mature":
        base = min(5, base + 1)  # Mature = processes settled, all models
    elif stage == "growth" and scale in ("large", "enterprise"):
        base = min(base, 2)  # Growth at scale = peak fragmentation
    elif stage == "legacy":
        base = min(base, 3)  # Ossified

    # Late phases can indicate integration stress
    if phase in ("maturation", "transition", "closure", "testing_phase"):
        base = max(1, base - 1)

    return max(1, min(5, base))


# Ordered derivation functions matching D1-D8
_DIMENSION_DERIVERS = [
    _derive_d1_consequence,
    _derive_d2_market_pressure,
    _derive_d3_complexity,
    _derive_d4_regulation,
    _derive_d5_team_stability,
    _derive_d6_outsourcing,
    _derive_d7_lifecycle,
    _derive_d8_coherence,
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def context_to_dimensions(mira_data: dict) -> list[int]:
    """
    Derive 8 simulation dimensions (each 1-5) from MIRA context fields.

    Parameters
    ----------
    mira_data : dict
        Must contain a "context" key with MIRA ProjectContext fields.
        Optionally contains "answers" key with specific question responses
        (ARC-O1, GOV-O2, TPT-O1) for better D3/D5/D6 inference.

    Returns
    -------
    list[int]
        8 dimension values [D1, D2, D3, D4, D5, D6, D7, D8], each 1-5.
    """
    ctx = mira_data.get("context", {})

    # MIRA nests context in filter_context/scoring_context — flatten if present
    if "filter_context" in ctx:
        flat = dict(ctx.get("filter_context", {}))
        flat.update(ctx.get("scoring_context", {}))
        # Preserve has_third_party from kpi_context_derived if present
        kpi_derived = ctx.get("kpi_context_derived", {})
        if kpi_derived.get("has_third_party"):
            flat["has_third_party"] = True
        ctx = flat

    answers = mira_data.get("answers", {})
    return [fn(ctx, answers) for fn in _DIMENSION_DERIVERS]


def select_archetype(
    dimensions: list[int],
) -> tuple[str, float, list[tuple[str, float]]]:
    """
    Select the nearest archetype using Euclidean distance in 8D space.

    Parameters
    ----------
    dimensions : list[int]
        8 dimension values [D1..D8], each 1-5.

    Returns
    -------
    tuple of (best_archetype, best_distance, top_3_list)
        - best_archetype: name string (e.g. "#1 Micro Startup")
        - best_distance: float, Euclidean distance to best match
        - top_3_list: list of (archetype, distance) tuples, sorted ascending
    """
    dims_arr = np.array(dimensions, dtype=float)

    distances = []
    for archetype in ARCHETYPE_ORDER:
        arch_dims = np.array(ARCHETYPE_DIMENSIONS[archetype], dtype=float)
        dist = float(np.linalg.norm(dims_arr - arch_dims))
        distances.append((archetype, dist))

    distances.sort(key=lambda x: x[1])
    best = distances[0]
    top_3 = distances[:3]

    return best[0], best[1], top_3


def bridge_mira_to_simulation(mira_data: dict) -> dict[str, Any]:
    """
    Top-level bridge: MIRA output → simulation-ready payload.

    Parameters
    ----------
    mira_data : dict
        MIRA output with "context" (required), optionally "scores" and "answers".

    Returns
    -------
    dict with keys:
        dimensions, archetype, match_distance, alternatives, confidence,
        and optionally cap, ops (if MIRA scores provided).
    """
    dims = context_to_dimensions(mira_data)
    archetype, distance, alternatives = select_archetype(dims)

    result: dict[str, Any] = {
        "dimensions": dims,
        "archetype": archetype,
        "match_distance": round(distance, 3),
        "alternatives": [(a, round(d, 3)) for a, d in alternatives],
        "confidence": (
            "strong" if distance < 2.0
            else "reasonable" if distance < 4.0
            else "ambiguous"
        ),
    }

    # Pre-load Cap/Ops from MIRA scores if available
    scores = mira_data.get("scores", {})
    if "capability_aggregate" in scores:
        result["cap"] = scores["capability_aggregate"] / 100.0
    if "operational_aggregate" in scores:
        result["ops"] = scores["operational_aggregate"] / 100.0

    return result


# ---------------------------------------------------------------------------
# Persona validation — 12 MIRA personas with expected archetype mappings
# ---------------------------------------------------------------------------

# Each persona's context and answers sourced from MIRA's actual assessment
# output at data/mira_persona_assessments.json. Scores included for
# Cap/Ops pre-loading validation.
PERSONA_CONTEXTS: dict[str, dict] = {
    "P1 Startup Chaos": {
        "context": {
            "regulatory_standards": [],
            "regulatory": "none",
            "scale": "small",
            "delivery_model": "agile",
            "product_stage": "startup",
            "project_phase": "mid_dev",
        },
        "answers": {"ARC-O1": 7, "TPP-C2": False},
        "scores": {"capability_aggregate": 15.36, "operational_aggregate": 22.22},
    },
    "P2 Small Agile Team": {
        "context": {
            "regulatory_standards": [],
            "regulatory": "none",
            "scale": "small",
            "delivery_model": "agile",
            "product_stage": "startup",
            "project_phase": "testing_phase",
        },
        "answers": {"ARC-O1": 6, "GOV-O2": 31, "TPP-C2": False},
        "scores": {"capability_aggregate": 30.00, "operational_aggregate": 38.88},
    },
    "P3 Government Waterfall": {
        "context": {
            "regulatory_standards": ["iso_27001"],
            "regulatory": "iso_27001",
            "scale": "large",
            "delivery_model": "waterfall",
            "product_stage": "mature",
            "project_phase": "transition",
            "has_third_party": True,
        },
        "answers": {"ARC-O1": 6, "GOV-O2": 48},
        "scores": {"capability_aggregate": 67.80, "operational_aggregate": 31.53},
    },
    "P4 Enterprise Financial": {
        "context": {
            "regulatory_standards": ["sox"],
            "regulatory": "sox",
            "scale": "enterprise",
            "delivery_model": "hybrid_agile",
            "product_stage": "mature",
            "project_phase": "mid_dev",
            "has_third_party": True,
        },
        "answers": {"ARC-O1": 3, "GOV-O2": 73, "TPP-C2": True},
        "scores": {"capability_aggregate": 83.27, "operational_aggregate": 74.81},
    },
    "P5 Medical Device": {
        "context": {
            "regulatory_standards": ["fda_21_cfr_11"],
            "regulatory": "fda_21_cfr_11",
            "scale": "medium",
            "delivery_model": "hybrid_traditional",
            "product_stage": "mature",
            "project_phase": "testing_phase",
            "has_third_party": True,
        },
        "answers": {"ARC-O1": 5, "GOV-O2": 52, "TPP-C2": True},
        "scores": {"capability_aggregate": 84.76, "operational_aggregate": 55.36},
    },
    "P6 Failing Automation": {
        "context": {
            "regulatory_standards": [],
            "regulatory": "none",
            "scale": "medium",
            "delivery_model": "hybrid_agile",
            "product_stage": "growth",
            "project_phase": "testing_phase",
        },
        "answers": {"ARC-O1": 6, "TPP-C2": True},
        "scores": {"capability_aggregate": 60.08, "operational_aggregate": 25.30},
    },
    "P7 Cloud-Native": {
        "context": {
            "regulatory_standards": [],
            "regulatory": "none",
            "scale": "medium",
            "delivery_model": "devops",
            "product_stage": "startup",
            "project_phase": "early_dev",
        },
        "answers": {"ARC-O1": 4, "GOV-O2": 48, "TPP-C2": True},
        "scores": {"capability_aggregate": 48.12, "operational_aggregate": 61.37},
    },
    "P8 Late-Stage UAT Crisis": {
        "context": {
            "regulatory_standards": [],
            "regulatory": "none",
            "scale": "large",
            "delivery_model": "hybrid_traditional",
            "product_stage": "growth",
            "project_phase": "closure",
            "has_third_party": True,
        },
        "answers": {"ARC-O1": 8},
        "scores": {"capability_aggregate": 41.64, "operational_aggregate": 13.45},
    },
    "P9 Planning Phase": {
        "context": {
            "regulatory_standards": [],
            "regulatory": "none",
            "scale": "medium",
            "delivery_model": "hybrid_agile",
            "product_stage": "growth",
            "project_phase": "planning",
        },
        "answers": {"TPP-C2": False},
        "scores": {"capability_aggregate": 35.55, "operational_aggregate": 10.16},
    },
    "P10 Golden Enterprise": {
        "context": {
            "regulatory_standards": ["iso_9001_certified"],
            "regulatory": "iso_9001_certified",
            "scale": "enterprise",
            "delivery_model": "devops",
            "product_stage": "mature",
            "project_phase": "testing_phase",
            "has_third_party": True,
        },
        "answers": {"ARC-O1": 2, "GOV-O2": 83, "TPP-C2": True},
        "scores": {"capability_aggregate": 94.04, "operational_aggregate": 88.37},
    },
    "P11 Automotive Embedded": {
        "context": {
            "regulatory_standards": ["iec_62443"],
            "regulatory": "iec_62443",
            "scale": "enterprise",
            "delivery_model": "hybrid_traditional",
            "product_stage": "mature",
            "project_phase": "testing_phase",
            "has_third_party": True,
        },
        "answers": {"ARC-O1": 6, "GOV-O2": 57, "TPP-C2": True},
        "scores": {"capability_aggregate": 65.31, "operational_aggregate": 28.67},
    },
    "P12 Legacy Modernisation": {
        "context": {
            "regulatory_standards": ["other"],
            "regulatory": "other",
            "scale": "medium",
            "delivery_model": "waterfall",
            "product_stage": "legacy",
            "project_phase": "maintenance",
        },
        "answers": {"ARC-O1": 8},
        "scores": {"capability_aggregate": 2.84, "operational_aggregate": 14.81},
    },
}

# Expected archetype mappings — each persona can match one or more acceptable archetypes
PERSONA_EXPECTED: dict[str, list[str]] = {
    "P1 Startup Chaos":          ["#1 Micro Startup"],
    "P2 Small Agile Team":       ["#2 Small Agile"],
    "P3 Government Waterfall":   ["#8 Reg Stage-Gate", "#7 Outsource-Managed"],
    "P4 Enterprise Financial":   ["#9 Ent Balanced", "#8 Reg Stage-Gate"],
    "P5 Medical Device":         ["#15 Regulated Startup", "#8 Reg Stage-Gate"],
    "P6 Failing Automation":     ["#3 Scaling Startup", "#5 Component Heroes", "#2 Small Agile", "#14 Platform/Internal"],
    "P7 Cloud-Native":           ["#4 DevOps Native"],
    "P8 Late-Stage UAT Crisis":  ["#12 Crisis/Firefight", "#11 Modernisation", "#5 Component Heroes", "#6 Matrix Programme"],
    "P9 Planning Phase":         ["#13 Planning/Pre-Deliv"],
    "P10 Golden Enterprise":     ["#9 Ent Balanced"],
    "P11 Automotive Embedded":   ["#8 Reg Stage-Gate"],
    "P12 Legacy Modernisation":  ["#10 Legacy Maintenance", "#11 Modernisation"],
}


def validate_against_personas() -> dict[str, Any]:
    """
    Test the bridge against all 12 MIRA personas.

    Returns
    -------
    dict with:
        passed: int, failed: int, total: int,
        results: list of per-persona dicts with dims, archetype, expected, match
    """
    results = []
    passed = 0

    for persona_name, mira_data in PERSONA_CONTEXTS.items():
        dims = context_to_dimensions(mira_data)
        archetype, distance, top_3 = select_archetype(dims)
        expected = PERSONA_EXPECTED[persona_name]
        match = archetype in expected

        if match:
            passed += 1

        results.append({
            "persona": persona_name,
            "dimensions": dims,
            "archetype": archetype,
            "distance": round(distance, 2),
            "top_3": [(a, round(d, 2)) for a, d in top_3],
            "expected": expected,
            "match": match,
        })

    return {
        "passed": passed,
        "failed": len(results) - passed,
        "total": len(results),
        "accuracy": round(passed / len(results) * 100, 1),
        "results": results,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _dim_labels() -> list[str]:
    """Short dimension labels for display."""
    return [
        "Consequence", "Market Pressure", "Complexity", "Regulation",
        "Team Stability", "Outsourcing", "Lifecycle", "Coherence",
    ]


if __name__ == "__main__":
    print("=" * 72)
    print("MIRA-to-Simulation Bridge — Persona Validation")
    print("=" * 72)

    report = validate_against_personas()
    labels = _dim_labels()

    for r in report["results"]:
        status = "PASS" if r["match"] else "FAIL"
        print(f"\n{status}  {r['persona']}")
        dim_str = "  ".join(f"{l}={v}" for l, v in zip(labels, r["dimensions"]))
        print(f"  Dims: {dim_str}")
        print(f"  Matched: {r['archetype']} (dist={r['distance']:.2f})")
        if not r["match"]:
            print(f"  Expected: {r['expected']}")
        print(f"  Top 3: {r['top_3']}")

    print(f"\n{'=' * 72}")
    print(f"Result: {report['passed']}/{report['total']} passed "
          f"({report['accuracy']}%)")
    target = 10
    if report["passed"] >= target:
        print(f"Target met ({target}/{report['total']})")
    else:
        print(f"BELOW TARGET ({target}/{report['total']})")
    print("=" * 72)
