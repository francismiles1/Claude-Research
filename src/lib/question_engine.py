"""
MIRA Question Engine — Scoring & Adaptive Filtering

Ported from MIRA's scoring service. Processes answers through:
1. Answer normalisation (any type → 0-100%)
2. Adaptive filtering (dependencies, branches, progressive disclosure)
3. Weighted scoring (per-question weights from KPI tier mapping)
4. Category aggregation (capability + operational per category)
5. Dimension scoring (overall Cap% and Ops%)
6. Phase-weighted unified score

The primary outputs are:
- capability_pct: overall capability maturity (0-100%)
- operational_pct: overall operational maturity (0-100%)
These map directly to the Cap/Ops axes on the viability heatmap.
"""

from __future__ import annotations

from typing import Any

from lib.mira_questions import (
    QUESTIONS,
    CATEGORIES,
    CATEGORY_DEPENDENCIES,
    SECOND_LEVEL_BRANCHES,
    PROGRESSIVE_DISCLOSURE,
    PHASE_WEIGHTS,
    CONTEXT_MODIFIERS,
    TYPE_TOGGLE,
    TYPE_SELECT,
    TYPE_SLIDER,
    TYPE_MULTISELECT,
    TYPE_NUMBER,
    ASCENDING,
    DESCENDING,
    CUSTOM,
    UNSCORED,
    GAP,
)


# ---------------------------------------------------------------------------
# Answer normalisation — any answer → 0-100%
# ---------------------------------------------------------------------------

def normalise_answer(question_id: str, answer: Any) -> float | None:
    """Convert a raw answer to a 0-100% maturity score.

    Returns None for unscored questions or missing answers.
    """
    if answer is None:
        return None

    q = QUESTIONS.get(question_id)
    if q is None:
        return None

    scoring = q.get("scoring_order", ASCENDING)
    if scoring == UNSCORED:
        return None

    qtype = q["type"]

    # Toggle: True=100%, False=0%
    if qtype == TYPE_TOGGLE:
        return 100.0 if answer is True else 0.0

    # Select: ordinal position or custom scoring
    if qtype == TYPE_SELECT:
        return _normalise_select(q, answer, scoring)

    # Slider / Number: linear normalisation
    if qtype in (TYPE_SLIDER, TYPE_NUMBER):
        return _normalise_slider(q, answer)

    # Multiselect: not scored (used for filtering only)
    if qtype == TYPE_MULTISELECT:
        return None

    return None


def _normalise_select(q: dict, answer: Any, scoring: str) -> float | None:
    """Normalise a select-type answer."""
    options = q.get("options", [])
    if not options:
        return None

    # Gap scoring (PROPOSED-DFM-* questions)
    if scoring == GAP:
        gap_scores = q.get("gap_scoring", {})
        gap = gap_scores.get(answer)
        if gap is not None:
            return 100.0 - gap  # Gap of 0 = 100% maturity
        return None

    # Custom value_scores
    if scoring == CUSTOM:
        value_scores = q.get("value_scores", {})
        return float(value_scores.get(answer, 0))

    # Find position in options list
    values = [opt["value"] for opt in options]
    if answer not in values:
        return None
    idx = values.index(answer)
    n = len(values)

    if n == 1:
        return 100.0

    if scoring == DESCENDING:
        # First option = best (100%), last = worst (0%)
        return 100.0 * (1.0 - idx / (n - 1))
    else:
        # Ascending (default): first = worst (0%), last = best (100%)
        return 100.0 * idx / (n - 1)


def _normalise_slider(q: dict, answer: Any) -> float | None:
    """Normalise a slider/number answer."""
    try:
        val = float(answer)
    except (TypeError, ValueError):
        return None

    qmin = float(q.get("min", 0))
    qmax = float(q.get("max", 100))

    if qmax == qmin:
        return 100.0

    pct = (val - qmin) / (qmax - qmin) * 100.0
    pct = max(0.0, min(100.0, pct))

    if q.get("inverse", False):
        pct = 100.0 - pct

    return pct


# ---------------------------------------------------------------------------
# Adaptive filtering — determine which questions are visible
# ---------------------------------------------------------------------------

def get_visible_questions(
    answers: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> list[str]:
    """Return ordered list of question IDs that should be visible.

    Applies filtering in priority order:
    1. Context filters (project context)
    2. Category dependencies (answer-reactive skipping/adding)
    3. Second-level branches (compound condition triggers)
    4. Progressive disclosure (capability before operational)

    Args:
        answers: Current answers {question_id: value}
        context: Project context dict (scale, delivery_model, regulatory_standards, etc.)
    """
    context = context or {}

    # Start with all base questions from categories (not branch-only)
    visible = set()
    for cat_id, cat in CATEGORIES.items():
        if cat.get("branch_only"):
            continue
        for qlist in ("capability_questions", "operational_questions"):
            visible.update(cat.get(qlist, []))

    # Apply category dependencies
    skip_set = set()
    add_set = set()
    for dep in CATEGORY_DEPENDENCIES:
        if _evaluate_trigger(dep["trigger"], answers, context):
            skip_set.update(dep.get("skip", []))
            add_set.update(dep.get("add", []))

    visible -= skip_set
    visible |= add_set

    # Apply second-level branches
    for branch in SECOND_LEVEL_BRANCHES:
        if _evaluate_branch_trigger(branch["trigger"], answers, context):
            visible.update(branch.get("add", []))

    # Apply context filters
    visible = _apply_context_filters(visible, context)

    # Apply progressive disclosure
    visible = _apply_progressive_disclosure(visible, answers)

    # Return in category order
    return _order_questions(visible)


def _evaluate_trigger(
    trigger: dict, answers: dict, context: dict
) -> bool:
    """Evaluate a single trigger condition."""
    # Question-based trigger
    if "question_id" in trigger:
        qid = trigger["question_id"]
        val = answers.get(qid)
        if val is None:
            return False
        return _compare(val, trigger["operator"], trigger["value"])

    # Context-based trigger
    if "context_field" in trigger:
        field = trigger["context_field"]
        val = context.get(field)
        if val is None:
            return False
        return _compare(val, trigger["operator"], trigger["value"])

    return False


def _evaluate_branch_trigger(
    trigger: dict, answers: dict, context: dict
) -> bool:
    """Evaluate compound branch trigger (all conditions must be true)."""
    conditions = trigger.get("conditions", [])
    if not conditions:
        return False

    for cond in conditions:
        if "question_id" in cond:
            val = answers.get(cond["question_id"])
            if val is None:
                return False
            if not _compare(val, cond["operator"], cond["value"]):
                return False
        elif "context_field" in cond:
            val = context.get(cond["context_field"])
            if val is None:
                return False
            if not _compare(val, cond["operator"], cond["value"]):
                return False
        else:
            return False

    return True


def _compare(actual: Any, operator: str, expected: Any) -> bool:
    """Compare a value against a trigger condition."""
    if operator == "equals":
        return actual == expected
    if operator == "not_equals":
        return actual != expected
    if operator == "in":
        return actual in expected
    if operator == "not_in":
        return actual not in expected
    if operator == "contains_any":
        # actual is a list, expected is a list — any overlap
        if isinstance(actual, (list, tuple)):
            return bool(set(actual) & set(expected))
        return actual in expected
    if operator == "not_contains":
        if isinstance(actual, (list, tuple)):
            return expected not in actual
        return actual != expected
    if operator in ("gt", "greater_than"):
        return float(actual) > float(expected)
    if operator in ("gte", "greater_than_or_equal"):
        return float(actual) >= float(expected)
    if operator in ("lt", "less_than"):
        return float(actual) < float(expected)
    if operator in ("lte", "less_than_or_equal"):
        return float(actual) <= float(expected)
    return False


def _apply_context_filters(
    visible: set[str], context: dict
) -> set[str]:
    """Apply context-based filtering."""
    from lib.mira_questions import CONTEXT_FILTERS

    for cf in CONTEXT_FILTERS:
        trigger = cf.get("trigger", {})
        field = trigger.get("context_field")
        if not field:
            continue

        ctx_val = context.get(field)
        if ctx_val is None:
            continue

        if not _compare(ctx_val, trigger["operator"], trigger["value"]):
            continue

        # Keep-only filter: restrict a category to specific questions
        if "keep_only" in cf:
            keep = cf["keep_only"]
            cat_id = keep["category"]
            allowed = set(keep["questions"])
            cat = CATEGORIES.get(cat_id, {})
            all_cat_qs = set()
            for qlist in ("capability_questions", "operational_questions",
                          "conditional_questions", "branch_questions"):
                all_cat_qs.update(cat.get(qlist, []))
            # Remove category questions not in allowed set
            visible -= (all_cat_qs - allowed)

        # Reduce dimension: keep only high-priority questions
        if "reduce" in cf:
            red = cf["reduce"]
            dim = red["dimension"]
            keep_pct = red["keep_percentage"] / 100.0
            dim_qs = [qid for qid in visible
                      if QUESTIONS.get(qid, {}).get("dimension") == dim]
            # Sort by weight descending, keep top N%
            dim_qs.sort(
                key=lambda qid: QUESTIONS.get(qid, {}).get("weight", 1.0),
                reverse=True,
            )
            keep_n = max(1, int(len(dim_qs) * keep_pct))
            to_remove = set(dim_qs[keep_n:])
            visible -= to_remove

    return visible


def _apply_progressive_disclosure(
    visible: set[str], answers: dict
) -> set[str]:
    """Apply progressive disclosure rules.

    For categories with specific PD rules, check stage conditions.
    For PD-001 (general): skip operational questions if capability
    average is below threshold.
    """
    result = set(visible)

    for pd in PROGRESSIVE_DISCLOSURE:
        scope = pd.get("scope")
        stages = pd.get("stages", [])

        if scope == "all_categories":
            # PD-001: general rule — skip ops if cap avg < 30%
            threshold = 30
            for s in stages:
                if s.get("condition", {}).get("stage_1_average_threshold"):
                    threshold = s["condition"]["stage_1_average_threshold"]

            for cat_id, cat in CATEGORIES.items():
                if cat.get("branch_only"):
                    continue
                # Check for category-specific PD rules
                has_specific = any(
                    p.get("scope") == cat_id for p in PROGRESSIVE_DISCLOSURE
                )
                if has_specific:
                    continue

                cap_qs = cat.get("capability_questions", [])
                cap_scores = []
                for qid in cap_qs:
                    if qid in answers and qid in visible:
                        score = normalise_answer(qid, answers[qid])
                        if score is not None:
                            cap_scores.append(score)

                # If capability questions answered and average below threshold,
                # hide operational questions
                if cap_scores and (sum(cap_scores) / len(cap_scores)) < threshold:
                    ops_qs = cat.get("operational_questions", [])
                    result -= set(ops_qs)

        else:
            # Category-specific PD (PD-002, PD-003, PD-004)
            for i, stage in enumerate(stages):
                if "condition" not in stage:
                    continue
                cond = stage["condition"]
                # Check if condition is met
                if "question_id" in cond:
                    val = answers.get(cond["question_id"])
                    if val is None or not _compare(
                        val, cond["operator"], cond["value"]
                    ):
                        # Condition not met — hide this stage's questions
                        qs = stage.get("questions", [])
                        result -= set(qs)
                        # Also hide all later stages
                        for later in stages[i + 1:]:
                            result -= set(later.get("questions", []))
                        break

    return result


def _order_questions(visible: set[str]) -> list[str]:
    """Order visible questions by category, then capability before operational."""
    ordered = []
    for cat_id, cat in CATEGORIES.items():
        for qlist in ("capability_questions", "operational_questions",
                      "conditional_questions", "branch_questions"):
            for qid in cat.get(qlist, []):
                if qid in visible and qid not in ordered:
                    ordered.append(qid)
    return ordered


# ---------------------------------------------------------------------------
# Scoring pipeline — answers → Cap/Ops percentages
# ---------------------------------------------------------------------------

def compute_scores(
    answers: dict[str, Any],
    context: dict[str, Any] | None = None,
    phase: str = "execution",
) -> dict[str, Any]:
    """Compute maturity scores from answers.

    Returns dict with:
        capability_pct: overall capability % (0-100)
        operational_pct: overall operational % (0-100)
        unified_pct: phase-weighted composite (0-100)
        category_scores: {cat_id: {capability: float, operational: float}}
        question_scores: {question_id: float} (normalised 0-100)
        questions_answered: int
        questions_visible: int
    """
    context = context or {}

    # Get visible questions for this context
    visible = get_visible_questions(answers, context)

    # Normalise all answers
    question_scores = {}
    for qid in visible:
        if qid in answers:
            score = normalise_answer(qid, answers[qid])
            if score is not None:
                question_scores[qid] = score

    # Aggregate by category and dimension
    category_scores = {}
    for cat_id, cat in CATEGORIES.items():
        cap_total = 0.0
        cap_weight = 0.0
        ops_total = 0.0
        ops_weight = 0.0

        # Collect all question lists for this category
        all_qs = set()
        for qlist in ("capability_questions", "operational_questions",
                      "conditional_questions", "branch_questions"):
            all_qs.update(cat.get(qlist, []))

        for qid in all_qs:
            if qid not in question_scores:
                continue
            if qid not in visible:
                continue

            q = QUESTIONS[qid]
            w = q.get("weight", 1.0)
            if w <= 0:
                continue

            score = question_scores[qid]
            dim = q["dimension"]

            if dim == "capability":
                cap_total += score * w
                cap_weight += w
            elif dim == "operational":
                ops_total += score * w
                ops_weight += w

        cap_avg = cap_total / cap_weight if cap_weight > 0 else None
        ops_avg = ops_total / ops_weight if ops_weight > 0 else None

        if cap_avg is not None or ops_avg is not None:
            category_scores[cat_id] = {
                "capability": cap_avg,
                "operational": ops_avg,
                "cap_weight": cap_weight,
                "ops_weight": ops_weight,
            }

    # Overall dimension scores (weighted average across categories)
    total_cap = 0.0
    total_cap_w = 0.0
    total_ops = 0.0
    total_ops_w = 0.0

    for cat_id, cs in category_scores.items():
        if cs["capability"] is not None:
            w = cs["cap_weight"]
            total_cap += cs["capability"] * w
            total_cap_w += w
        if cs["operational"] is not None:
            w = cs["ops_weight"]
            total_ops += cs["operational"] * w
            total_ops_w += w

    capability_pct = total_cap / total_cap_w if total_cap_w > 0 else 0.0
    operational_pct = total_ops / total_ops_w if total_ops_w > 0 else 0.0

    # Phase-weighted unified score
    pw = PHASE_WEIGHTS.get(phase, PHASE_WEIGHTS["execution"])
    unified_pct = (
        capability_pct * pw["capability"] +
        operational_pct * pw["operational"]
    )

    return {
        "capability_pct": round(capability_pct, 1),
        "operational_pct": round(operational_pct, 1),
        "unified_pct": round(unified_pct, 1),
        "category_scores": category_scores,
        "question_scores": question_scores,
        "questions_answered": len(question_scores),
        "questions_visible": len(visible),
        "phase": phase,
    }


def classify_diagnostic(cap_pct: float, ops_pct: float) -> dict[str, str]:
    """Classify the Cap/Ops position diagnostically.

    Returns:
        classification: e.g. "Balanced High", "Capability > Operational"
        gap_severity: "aligned", "moderate", "large"
        description: Human-readable interpretation
    """
    from lib.mira_questions import DIAGNOSTIC

    gap = abs(cap_pct - ops_pct)

    # Gap severity
    if gap >= DIAGNOSTIC["gap_severity"]["large"]:
        gap_sev = "large"
    elif gap >= DIAGNOSTIC["gap_severity"]["moderate"]:
        gap_sev = "moderate"
    else:
        gap_sev = "aligned"

    # Classification
    high = DIAGNOSTIC["high_threshold"]
    low = DIAGNOSTIC["low_threshold"]
    balanced_gap = DIAGNOSTIC["balanced_gap"]

    if gap <= balanced_gap:
        if cap_pct >= high and ops_pct >= high:
            cls = "Balanced High"
        elif cap_pct < low and ops_pct < low:
            cls = "Balanced Low"
        else:
            cls = "Mid-range"
    elif cap_pct > ops_pct:
        cls = "Capability > Operational"
    else:
        cls = "Operational > Capability"

    descriptions = {
        "Balanced High": "Strong foundation and execution — maintain and optimise",
        "Balanced Low": "Weak across both dimensions — prioritise fundamentals",
        "Capability > Operational": "Capability without execution — close the delivery gap",
        "Operational > Capability": "Doing without structure — formalise practices",
        "Mid-range": "Mixed maturity — targeted improvements needed",
    }

    return {
        "classification": cls,
        "gap_severity": gap_sev,
        "description": descriptions.get(cls, ""),
    }


# ---------------------------------------------------------------------------
# Category summary — human-readable per-category breakdown
# ---------------------------------------------------------------------------

def category_summary(
    category_scores: dict[str, dict],
) -> list[dict[str, Any]]:
    """Generate ordered summary of category scores for display.

    Returns list of dicts with: id, name, capability, operational, overall.
    """
    result = []
    for cat_id, cat in CATEGORIES.items():
        if cat.get("branch_only"):
            # Only include if there are scores for this branch category
            if cat_id not in category_scores:
                continue

        cs = category_scores.get(cat_id)
        if cs is None:
            continue

        cap = cs.get("capability")
        ops = cs.get("operational")

        # Simple average for overall (unweighted at category level)
        parts = [x for x in (cap, ops) if x is not None]
        overall = sum(parts) / len(parts) if parts else None

        result.append({
            "id": cat_id,
            "name": cat["name"],
            "capability": round(cap, 1) if cap is not None else None,
            "operational": round(ops, 1) if ops is not None else None,
            "overall": round(overall, 1) if overall is not None else None,
        })

    return result


# ---------------------------------------------------------------------------
# Questions-by-category helper — for UI rendering
# ---------------------------------------------------------------------------

def get_category_questions(
    cat_id: str,
    answers: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Get visible questions for a single category, with metadata.

    Returns list of question dicts augmented with:
        id, visible, answered, current_answer, score
    """
    visible_set = set(get_visible_questions(answers, context or {}))
    cat = CATEGORIES.get(cat_id, {})
    result = []

    for qlist in ("capability_questions", "operational_questions",
                  "conditional_questions", "branch_questions"):
        for qid in cat.get(qlist, []):
            q = QUESTIONS.get(qid)
            if q is None:
                continue
            is_visible = qid in visible_set
            ans = answers.get(qid)
            score = normalise_answer(qid, ans) if ans is not None else None

            result.append({
                **q,
                "id": qid,
                "visible": is_visible,
                "answered": ans is not None,
                "current_answer": ans,
                "score": score,
            })

    return result
