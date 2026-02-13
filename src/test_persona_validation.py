"""
Persona Validation — test the ported MIRA question engine against 12 personas.

Generates synthetic answers for each persona using the same maturity profile
approach as MIRA's persona_simulator.py, runs them through compute_scores(),
and validates that diagnostic classifications match expectations.

Usage:
    cd src
    python test_persona_validation.py
"""

from __future__ import annotations

import random
from typing import Any

from lib.mira_questions import (
    QUESTIONS,
    CATEGORIES,
    TYPE_TOGGLE,
    TYPE_SELECT,
    TYPE_SLIDER,
    TYPE_NUMBER,
    TYPE_MULTISELECT,
    ASCENDING,
    DESCENDING,
    CUSTOM,
    UNSCORED,
    GAP,
)
from lib.question_engine import (
    get_visible_questions,
    compute_scores,
    classify_diagnostic,
)


# ---------------------------------------------------------------------------
# Maturity profiles — answer generation parameters per level
# ---------------------------------------------------------------------------
# Identical to MIRA's MATURITY_PROFILES in answer_generation.py

MATURITY_PROFILES = {
    "very_low":  {"pct_range": (5, 25),   "toggle_true_prob": 0.1,  "select_bias": "worst"},
    "low":       {"pct_range": (15, 40),  "toggle_true_prob": 0.3,  "select_bias": "low"},
    "medium":    {"pct_range": (35, 65),  "toggle_true_prob": 0.6,  "select_bias": "mid"},
    "high":      {"pct_range": (55, 85),  "toggle_true_prob": 0.8,  "select_bias": "high"},
    "very_high": {"pct_range": (75, 95),  "toggle_true_prob": 0.95, "select_bias": "best"},
}


# ---------------------------------------------------------------------------
# Answer generator — mirrors MIRA's AnswerGenerator
# ---------------------------------------------------------------------------

def generate_answer(qid: str, q: dict, profile_name: str) -> Any:
    """Generate a single answer based on question type and maturity profile."""
    profile = MATURITY_PROFILES[profile_name]
    qtype = q["type"]

    if qtype == TYPE_TOGGLE:
        return random.random() < profile["toggle_true_prob"]

    if qtype == TYPE_SELECT:
        return _gen_select(q, profile)

    if qtype == TYPE_SLIDER:
        return _gen_slider(q, profile)

    if qtype == TYPE_NUMBER:
        return _gen_number(q, profile)

    if qtype == TYPE_MULTISELECT:
        return _gen_multiselect(q, profile)

    return None


def _gen_select(q: dict, profile: dict) -> Any:
    """Generate select answer consistent with maturity bias."""
    options = q.get("options", [])
    if not options:
        return None

    scoring = q.get("scoring_order", ASCENDING)
    if scoring == UNSCORED:
        return random.choice(options)["value"]

    bias = profile["select_bias"]
    n = len(options)

    # Custom scoring — pick by value_scores
    if scoring in (CUSTOM, GAP):
        score_map = q.get("value_scores", q.get("gap_scoring", {}))
        if score_map:
            if scoring == GAP:
                # Lower gap = better maturity
                sorted_vals = sorted(score_map.items(), key=lambda x: x[1])
            else:
                sorted_vals = sorted(score_map.items(), key=lambda x: x[1])
            if bias == "best":
                return str(sorted_vals[-1][0]) if scoring != GAP else str(sorted_vals[0][0])
            elif bias == "worst":
                return str(sorted_vals[0][0]) if scoring != GAP else str(sorted_vals[-1][0])
            elif bias == "high":
                idx = random.choice(range(max(0, len(sorted_vals) - 2), len(sorted_vals)))
                return str(sorted_vals[idx][0]) if scoring != GAP else str(sorted_vals[max(0, len(sorted_vals)-1 - idx)][0])
            elif bias == "low":
                idx = random.choice(range(min(2, len(sorted_vals))))
                return str(sorted_vals[idx][0]) if scoring != GAP else str(sorted_vals[max(0, len(sorted_vals)-1 - idx)][0])
            else:
                mid = len(sorted_vals) // 2
                candidates = list(range(max(0, mid - 1), min(len(sorted_vals), mid + 2)))
                return str(sorted_vals[random.choice(candidates)][0])

    # Descending order: first option = best
    descending = scoring == DESCENDING

    if n == 1:
        idx = 0
    elif bias == "worst":
        idx = (n - 1) if descending else 0
    elif bias == "low":
        if descending:
            idx = random.choice(range(max(0, n - 2), n))
        else:
            idx = random.choice(range(min(2, n)))
    elif bias == "mid":
        mid = n // 2
        candidates = list(range(max(0, mid - 1), min(n, mid + 2)))
        idx = random.choice(candidates)
    elif bias == "high":
        if descending:
            idx = random.choice(range(min(2, n)))
        else:
            idx = random.choice(range(max(0, n - 2), n))
    elif bias == "best":
        idx = 0 if descending else (n - 1)
    else:
        idx = random.randint(0, n - 1)

    return options[idx]["value"]


def _gen_slider(q: dict, profile: dict) -> int:
    """Generate slider answer within profile range."""
    min_val = q.get("min", 0)
    max_val = q.get("max", 100)
    pct_low, pct_high = profile["pct_range"]

    if q.get("inverse", False):
        pct_low, pct_high = 100 - pct_high, 100 - pct_low

    scaled_low = min_val + (pct_low / 100) * (max_val - min_val)
    scaled_high = min_val + (pct_high / 100) * (max_val - min_val)

    return random.randint(int(scaled_low), int(scaled_high))


def _gen_number(q: dict, profile: dict) -> int:
    """Generate number answer within profile range."""
    min_val = q.get("min", 0)
    max_val = q.get("max", 100)
    pct_low, pct_high = profile["pct_range"]

    scaled_low = min_val + (pct_low / 100) * (max_val - min_val)
    scaled_high = min_val + (pct_high / 100) * (max_val - min_val)

    return random.randint(int(scaled_low), int(scaled_high))


def _gen_multiselect(q: dict, profile: dict) -> list:
    """Generate multiselect answer."""
    options = q.get("options", [])
    if not options:
        return []

    bias = profile["select_bias"]
    if bias in ("worst", "low"):
        count = random.randint(0, min(2, len(options)))
    elif bias in ("mid",):
        count = random.randint(1, min(3, len(options)))
    elif bias in ("high", "best"):
        count = random.randint(2, min(5, len(options)))
    else:
        count = random.randint(0, len(options))

    if count == 0:
        return []

    selected = random.sample(options, min(count, len(options)))
    return [opt["value"] for opt in selected if "value" in opt]


def generate_persona_answers(
    visible_questions: list[str],
    branching_answers: dict[str, Any],
    category_profiles: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Generate answers for all visible questions based on maturity profiles."""
    answers = dict(branching_answers)

    for qid in visible_questions:
        if qid in answers:
            continue

        q = QUESTIONS.get(qid)
        if q is None:
            continue

        category = q.get("category", "unknown")
        dimension = q.get("dimension", "capability")

        cat_profile = category_profiles.get(category, {})
        profile_name = cat_profile.get(dimension, "medium")

        if profile_name not in MATURITY_PROFILES:
            profile_name = "medium"

        answer = generate_answer(qid, q, profile_name)
        if answer is not None:
            answers[qid] = answer

    return answers


# ---------------------------------------------------------------------------
# Persona definitions — extracted from MIRA persona_simulator.py
# ---------------------------------------------------------------------------

PERSONAS = [
    {
        "id": 1,
        "name": "Startup Chaos",
        "desc": "MVP scramble — heroics over process",
        "filter_context": {
            "scale": "small", "delivery_model": "agile",
            "project_phase": "execution", "regulatory_standards": [],
            "product_stage": "startup",
        },
        "branching_answers": {
            "GOV-C1": False, "GOV-O4": False,
            "TAM-O1": "none", "TPT-O1": "none",
            "ARC-C5": False, "PROPOSED-DFM-01": "none",
        },
        "category_profiles": {
            "governance":        {"capability": "very_low", "operational": "low"},
            "test_strategy":     {"capability": "very_low", "operational": "low"},
            "test_assets":       {"capability": "very_low", "operational": "low"},
            "development":       {"capability": "low",      "operational": "medium"},
            "environment":       {"capability": "very_low", "operational": "low"},
            "requirements":      {"capability": "very_low", "operational": "low"},
            "change_management": {"capability": "very_low", "operational": "low"},
            "feedback":          {"capability": "very_low", "operational": "medium"},
            "architecture":      {"capability": "low",      "operational": "low"},
            "ops_readiness":     {"capability": "very_low", "operational": "low"},
            "third_party":       {"capability": "very_low", "operational": "very_low"},
            "test_phase_progress": {"capability": "very_low", "operational": "medium"},
            "defect_management": {"capability": "very_low", "operational": "low"},
        },
        "expected_classification": "Balanced Low",
        "alternatives": ["Mid-range"],
        "scoring_context": {"project_phase": "execution"},
    },
    {
        "id": 2,
        "name": "Small Agile Team",
        "desc": "Scrappy professionals — works because team is good",
        "filter_context": {
            "scale": "small", "delivery_model": "agile",
            "project_phase": "execution", "regulatory_standards": [],
            "product_stage": "startup",
        },
        "branching_answers": {
            "GOV-C1": True, "GOV-C2": "escalate_only", "GOV-O4": False,
            "TAM-O1": "some_manual", "TPT-O1": "none",
            "ARC-C5": False, "PROPOSED-DFM-01": "informal",
        },
        "category_profiles": {
            "governance":        {"capability": "very_low", "operational": "low"},
            "test_strategy":     {"capability": "very_low", "operational": "low"},
            "test_assets":       {"capability": "low",      "operational": "medium"},
            "development":       {"capability": "medium",   "operational": "medium"},
            "environment":       {"capability": "low",      "operational": "medium"},
            "requirements":      {"capability": "very_low", "operational": "low"},
            "change_management": {"capability": "low",      "operational": "low"},
            "feedback":          {"capability": "low",      "operational": "medium"},
            "architecture":      {"capability": "medium",   "operational": "medium"},
            "ops_readiness":     {"capability": "low",      "operational": "low"},
            "third_party":       {"capability": "very_low", "operational": "very_low"},
            "test_phase_progress": {"capability": "low",    "operational": "medium"},
            "defect_management": {"capability": "low",      "operational": "low"},
        },
        "expected_classification": "Balanced Low",
        "alternatives": ["Operational > Capability"],
        "scoring_context": {"project_phase": "execution"},
    },
    {
        "id": 3,
        "name": "Government Waterfall",
        "desc": "Compliance machine — structure without speed",
        "filter_context": {
            "scale": "large", "delivery_model": "waterfall",
            "project_phase": "transition", "regulatory_standards": ["iso_27001"],
            "product_stage": "mature",
        },
        "branching_answers": {
            "GOV-C1": True, "GOV-C2": "can_delay", "GOV-O4": False,
            "TAM-O1": "some_manual", "TPT-O1": "several", "TPT-O3": "moderate",
            "ARC-C5": True, "ARC-C5b": "some", "ARC-C5c": "partial",
            "PROPOSED-DFM-01": "formal",
        },
        "category_profiles": {
            "governance":        {"capability": "high",   "operational": "medium"},
            "test_strategy":     {"capability": "high",   "operational": "low"},
            "test_assets":       {"capability": "medium", "operational": "low"},
            "development":       {"capability": "medium", "operational": "low"},
            "environment":       {"capability": "high",   "operational": "medium"},
            "requirements":      {"capability": "high",   "operational": "medium"},
            "change_management": {"capability": "high",   "operational": "low"},
            "feedback":          {"capability": "medium", "operational": "low"},
            "architecture":      {"capability": "medium", "operational": "low"},
            "ops_readiness":     {"capability": "medium", "operational": "low"},
            "third_party":       {"capability": "medium", "operational": "low"},
            "test_phase_progress": {"capability": "high", "operational": "low"},
            "defect_management": {"capability": "high",   "operational": "low"},
        },
        "expected_classification": "Capability > Operational",
        "alternatives": ["Mid-range"],
        "scoring_context": {"project_phase": "transition"},
    },
    {
        "id": 4,
        "name": "Enterprise Financial Platform",
        "desc": "Regulated powerhouse — high both axes",
        "filter_context": {
            "scale": "enterprise", "delivery_model": "hybrid_agile",
            "project_phase": "execution", "regulatory_standards": ["pci_dss"],
            "product_stage": "mature",
        },
        "branching_answers": {
            "GOV-C1": True, "GOV-C2": "can_stop", "GOV-O4": True,
            "TAM-O1": "established", "TPT-O1": "several", "TPT-O3": "moderate",
            "ARC-C5": False, "PROPOSED-DFM-01": "optimised",
        },
        "category_profiles": {
            "governance":        {"capability": "high",      "operational": "high"},
            "test_strategy":     {"capability": "high",      "operational": "high"},
            "test_assets":       {"capability": "high",      "operational": "high"},
            "development":       {"capability": "high",      "operational": "high"},
            "environment":       {"capability": "very_high", "operational": "high"},
            "requirements":      {"capability": "high",      "operational": "high"},
            "change_management": {"capability": "high",      "operational": "high"},
            "feedback":          {"capability": "high",      "operational": "high"},
            "architecture":      {"capability": "high",      "operational": "high"},
            "ops_readiness":     {"capability": "high",      "operational": "high"},
            "third_party":       {"capability": "high",      "operational": "medium"},
            "test_phase_progress": {"capability": "high",    "operational": "high"},
            "defect_management": {"capability": "high",      "operational": "high"},
            "enterprise_scale":  {"capability": "high",      "operational": "high"},
        },
        "expected_classification": "Balanced High",
        "alternatives": [],
        "scoring_context": {"project_phase": "execution"},
    },
    {
        "id": 5,
        "name": "Medical Device",
        "desc": "Safety-critical — slow by design, process exists for a reason",
        "filter_context": {
            "scale": "medium", "delivery_model": "hybrid_traditional",
            "project_phase": "execution", "regulatory_standards": ["fda", "iso_13485"],
            "product_stage": "mature",
        },
        "branching_answers": {
            "GOV-C1": True, "GOV-C2": "can_delay", "GOV-O4": True,
            "TAM-O1": "established", "TPT-O1": "few",
            "ARC-C5": False, "PROPOSED-DFM-01": "formal",
        },
        "category_profiles": {
            "governance":        {"capability": "high",      "operational": "medium"},
            "test_strategy":     {"capability": "very_high", "operational": "medium"},
            "test_assets":       {"capability": "high",      "operational": "medium"},
            "development":       {"capability": "high",      "operational": "medium"},
            "environment":       {"capability": "high",      "operational": "medium"},
            "requirements":      {"capability": "very_high", "operational": "medium"},
            "change_management": {"capability": "high",      "operational": "medium"},
            "feedback":          {"capability": "high",      "operational": "medium"},
            "architecture":      {"capability": "high",      "operational": "medium"},
            "ops_readiness":     {"capability": "high",      "operational": "medium"},
            "third_party":       {"capability": "medium",    "operational": "medium"},
            "test_phase_progress": {"capability": "high",    "operational": "medium"},
            "defect_management": {"capability": "high",      "operational": "medium"},
            "life_safety":       {"capability": "very_high", "operational": "high"},
        },
        "expected_classification": "Capability > Operational",
        "alternatives": ["Mid-range"],
        "scoring_context": {"project_phase": "execution"},
    },
    {
        "id": 6,
        "name": "Failing Automation Rescue",
        "desc": "Tool-first trap — investment not translating to outcomes",
        "filter_context": {
            "scale": "medium", "delivery_model": "hybrid_agile",
            "project_phase": "execution", "regulatory_standards": [],
            "product_stage": "growth",
        },
        "branching_answers": {
            "GOV-C1": True, "GOV-C2": "no", "GOV-O4": True,
            "TAM-O1": "failing", "TPT-O1": "none",
            "ARC-C5": False, "PROPOSED-DFM-01": "informal",
        },
        "category_profiles": {
            "governance":        {"capability": "medium",   "operational": "low"},
            "test_strategy":     {"capability": "medium",   "operational": "low"},
            "test_assets":       {"capability": "high",     "operational": "very_low"},
            "development":       {"capability": "medium",   "operational": "low"},
            "environment":       {"capability": "medium",   "operational": "very_low"},
            "requirements":      {"capability": "medium",   "operational": "low"},
            "change_management": {"capability": "medium",   "operational": "low"},
            "feedback":          {"capability": "low",      "operational": "low"},
            "architecture":      {"capability": "medium",   "operational": "low"},
            "ops_readiness":     {"capability": "medium",   "operational": "low"},
            "third_party":       {"capability": "very_low", "operational": "very_low"},
            "test_phase_progress": {"capability": "medium", "operational": "very_low"},
            "defect_management": {"capability": "medium",   "operational": "low"},
        },
        "expected_classification": "Capability > Operational",
        "alternatives": ["Mid-range"],
        "scoring_context": {"project_phase": "execution"},
    },
    {
        "id": 7,
        "name": "Greenfield Cloud-Native",
        "desc": "Clean slate — false confidence, silo blind spot",
        "filter_context": {
            "scale": "medium", "delivery_model": "devops",
            "project_phase": "execution", "regulatory_standards": [],
            "product_stage": "startup",
        },
        "branching_answers": {
            "GOV-C1": True, "GOV-C2": "escalate_only", "GOV-O4": False,
            "TAM-O1": "established", "TPT-O1": "none",
            "ARC-C5": False, "PROPOSED-DFM-01": "defined",
        },
        "category_profiles": {
            "governance":        {"capability": "low",      "operational": "medium"},
            "test_strategy":     {"capability": "low",      "operational": "high"},
            "test_assets":       {"capability": "medium",   "operational": "high"},
            "development":       {"capability": "high",     "operational": "high"},
            "environment":       {"capability": "high",     "operational": "high"},
            "requirements":      {"capability": "low",      "operational": "medium"},
            "change_management": {"capability": "low",      "operational": "medium"},
            "feedback":          {"capability": "low",      "operational": "medium"},
            "architecture":      {"capability": "high",     "operational": "high"},
            "ops_readiness":     {"capability": "low",      "operational": "medium"},
            "third_party":       {"capability": "very_low", "operational": "very_low"},
            "test_phase_progress": {"capability": "medium", "operational": "high"},
            "defect_management": {"capability": "low",      "operational": "medium"},
        },
        "expected_classification": "Operational > Capability",
        "alternatives": ["Mid-range"],
        "scoring_context": {"project_phase": "execution"},
    },
    {
        "id": 8,
        "name": "Late-Stage UAT Crisis",
        "desc": "Chickens come home — complacency not burnout",
        "filter_context": {
            "scale": "large", "delivery_model": "hybrid_traditional",
            "project_phase": "closure", "regulatory_standards": [],
            "product_stage": "growth",
        },
        "branching_answers": {
            "GOV-C1": True, "GOV-C2": "no", "GOV-O4": True,
            "TAM-O1": "struggling", "TPT-O1": "several", "TPT-O3": "high",
            "ARC-C5": True, "ARC-C5b": "significant", "ARC-C5c": "partial",
            "PROPOSED-DFM-01": "formal",
        },
        "category_profiles": {
            "governance":        {"capability": "medium", "operational": "low"},
            "test_strategy":     {"capability": "medium", "operational": "very_low"},
            "test_assets":       {"capability": "low",    "operational": "very_low"},
            "development":       {"capability": "medium", "operational": "very_low"},
            "environment":       {"capability": "low",    "operational": "very_low"},
            "requirements":      {"capability": "medium", "operational": "very_low"},
            "change_management": {"capability": "low",    "operational": "very_low"},
            "feedback":          {"capability": "medium", "operational": "very_low"},
            "architecture":      {"capability": "low",    "operational": "very_low"},
            "ops_readiness":     {"capability": "low",    "operational": "very_low"},
            "third_party":       {"capability": "low",    "operational": "very_low"},
            "test_phase_progress": {"capability": "medium", "operational": "very_low"},
            "defect_management": {"capability": "medium", "operational": "very_low"},
        },
        "expected_classification": "Capability > Operational",
        "alternatives": ["Balanced Low"],
        "scoring_context": {"project_phase": "closure"},
    },
    {
        "id": 9,
        "name": "Planning Phase Assessment",
        "desc": "Fresh start — nothing to measure yet",
        "filter_context": {
            "scale": "medium", "delivery_model": "hybrid_agile",
            "project_phase": "planning", "regulatory_standards": [],
            "product_stage": "growth",
        },
        "branching_answers": {
            "GOV-C1": True, "GOV-C2": "can_stop", "GOV-O4": True,
            "TAM-O1": "none", "TPT-O1": "none",
            "ARC-C5": False, "PROPOSED-DFM-01": "none",
        },
        "category_profiles": {
            "governance":        {"capability": "medium",   "operational": "very_low"},
            "test_strategy":     {"capability": "medium",   "operational": "very_low"},
            "test_assets":       {"capability": "low",      "operational": "very_low"},
            "development":       {"capability": "medium",   "operational": "very_low"},
            "environment":       {"capability": "low",      "operational": "very_low"},
            "requirements":      {"capability": "medium",   "operational": "very_low"},
            "change_management": {"capability": "low",      "operational": "very_low"},
            "feedback":          {"capability": "low",      "operational": "very_low"},
            "architecture":      {"capability": "medium",   "operational": "very_low"},
            "ops_readiness":     {"capability": "low",      "operational": "very_low"},
            "third_party":       {"capability": "very_low", "operational": "very_low"},
            "test_phase_progress": {"capability": "low",    "operational": "very_low"},
            "defect_management": {"capability": "low",      "operational": "very_low"},
        },
        "expected_classification": "Capability > Operational",
        "alternatives": ["Balanced Low"],
        "scoring_context": {"project_phase": "planning"},
    },
    {
        "id": 10,
        "name": "Golden Enterprise",
        "desc": "CONTROL — benchmark, genuinely mature",
        "filter_context": {
            "scale": "enterprise", "delivery_model": "devops",
            "project_phase": "execution",
            "regulatory_standards": ["iso_9001", "iso_27001"],
            "product_stage": "mature",
        },
        "branching_answers": {
            "GOV-C1": True, "GOV-C2": "can_stop", "GOV-O4": True,
            "TAM-O1": "established", "TPT-O1": "several", "TPT-O3": "low",
            "ARC-C5": False, "PROPOSED-DFM-01": "optimised",
        },
        "category_profiles": {
            "governance":        {"capability": "very_high", "operational": "very_high"},
            "test_strategy":     {"capability": "very_high", "operational": "very_high"},
            "test_assets":       {"capability": "very_high", "operational": "very_high"},
            "development":       {"capability": "very_high", "operational": "very_high"},
            "environment":       {"capability": "very_high", "operational": "very_high"},
            "requirements":      {"capability": "very_high", "operational": "very_high"},
            "change_management": {"capability": "very_high", "operational": "very_high"},
            "feedback":          {"capability": "very_high", "operational": "very_high"},
            "architecture":      {"capability": "very_high", "operational": "very_high"},
            "ops_readiness":     {"capability": "very_high", "operational": "very_high"},
            "third_party":       {"capability": "high",      "operational": "high"},
            "test_phase_progress": {"capability": "very_high", "operational": "very_high"},
            "defect_management": {"capability": "very_high", "operational": "very_high"},
            "enterprise_scale":  {"capability": "very_high", "operational": "very_high"},
        },
        "expected_classification": "Balanced High",
        "alternatives": [],
        "scoring_context": {"project_phase": "execution"},
    },
    {
        "id": 11,
        "name": "Automotive Embedded Platform",
        "desc": "Multi-tier minefield — compliance fortress around trust vacuum",
        "filter_context": {
            "scale": "enterprise", "delivery_model": "hybrid_traditional",
            "project_phase": "execution",
            "regulatory_standards": ["iso_26262", "aspice"],
            "product_stage": "mature",
        },
        "branching_answers": {
            "GOV-C1": True, "GOV-C2": "escalate_only", "GOV-O4": True,
            "TAM-O1": "struggling", "TPT-O1": "many", "TPT-O3": "moderate",
            "ARC-C5": True, "ARC-C5b": "significant", "ARC-C5c": "partial",
            "PROPOSED-DFM-01": "formal",
        },
        "category_profiles": {
            "governance":        {"capability": "high",   "operational": "medium"},
            "test_strategy":     {"capability": "high",   "operational": "low"},
            "test_assets":       {"capability": "medium", "operational": "low"},
            "development":       {"capability": "medium", "operational": "low"},
            "environment":       {"capability": "medium", "operational": "low"},
            "requirements":      {"capability": "high",   "operational": "low"},
            "change_management": {"capability": "high",   "operational": "medium"},
            "feedback":          {"capability": "medium", "operational": "low"},
            "architecture":      {"capability": "medium", "operational": "low"},
            "ops_readiness":     {"capability": "medium", "operational": "low"},
            "third_party":       {"capability": "medium", "operational": "low"},
            "test_phase_progress": {"capability": "high", "operational": "low"},
            "defect_management": {"capability": "high",   "operational": "low"},
            "automotive_safety": {"capability": "high",   "operational": "medium"},
            "enterprise_scale":  {"capability": "high",   "operational": "medium"},
        },
        "expected_classification": "Capability > Operational",
        "alternatives": ["Mid-range"],
        "scoring_context": {"project_phase": "execution"},
    },
    {
        "id": 12,
        "name": "Legacy Modernisation",
        "desc": "Ticking clock — institutional memory, not process",
        "filter_context": {
            "scale": "medium", "delivery_model": "waterfall",
            "project_phase": "maintenance",
            "regulatory_standards": [],
            "product_stage": "legacy",
        },
        "branching_answers": {
            "GOV-C1": False, "GOV-O4": False,
            "TAM-O1": "none", "TPT-O1": "none",
            "ARC-C5": True, "ARC-C5b": "majority", "ARC-C5c": "none",
            "PROPOSED-DFM-01": "informal",
        },
        "category_profiles": {
            "governance":        {"capability": "very_low", "operational": "low"},
            "test_strategy":     {"capability": "very_low", "operational": "low"},
            "test_assets":       {"capability": "very_low", "operational": "low"},
            "development":       {"capability": "very_low", "operational": "medium"},
            "environment":       {"capability": "very_low", "operational": "low"},
            "requirements":      {"capability": "very_low", "operational": "low"},
            "change_management": {"capability": "very_low", "operational": "low"},
            "feedback":          {"capability": "very_low", "operational": "medium"},
            "architecture":      {"capability": "very_low", "operational": "very_low"},
            "ops_readiness":     {"capability": "very_low", "operational": "low"},
            "third_party":       {"capability": "very_low", "operational": "very_low"},
            "test_phase_progress": {"capability": "very_low", "operational": "medium"},
            "defect_management": {"capability": "very_low", "operational": "low"},
        },
        "expected_classification": "Balanced Low",
        "alternatives": ["Operational > Capability"],
        "scoring_context": {"project_phase": "maintenance"},
    },
]


# ---------------------------------------------------------------------------
# Validation runner
# ---------------------------------------------------------------------------

def run_validation(seed: int = 42) -> bool:
    """Run all 12 personas through the ported engine and validate."""
    print("=" * 90)
    print("MIRA QUESTION ENGINE — PERSONA VALIDATION")
    print(f"Seed: {seed}")
    print("=" * 90)
    print()

    # Header
    print(f"{'#':>2}  {'Persona':<30}  {'Cap%':>5}  {'Ops%':>5}  "
          f"{'Classification':<26}  {'Expected':<26}  {'Status'}")
    print("-" * 130)

    passed = 0
    total = len(PERSONAS)
    results = []

    for persona in PERSONAS:
        # Per-persona seed (matches MIRA's approach)
        random.seed(seed + persona["id"])

        ctx = persona["filter_context"]

        # Two-pass answer generation (mimics MIRA's progressive disclosure)
        # Pass 1: get visible questions with branching answers only
        visible_pass1 = get_visible_questions(persona["branching_answers"], ctx)

        # Generate answers for pass 1 (capability-focused)
        answers_pass1 = generate_persona_answers(
            visible_pass1,
            persona["branching_answers"],
            persona["category_profiles"],
        )

        # Pass 2: re-evaluate with all answers — PD may unlock operational
        visible_pass2 = get_visible_questions(answers_pass1, ctx)
        all_answers = generate_persona_answers(
            visible_pass2,
            answers_pass1,  # includes branching + pass 1 answers
            persona["category_profiles"],
        )

        # Score
        phase = persona["scoring_context"].get("project_phase", "execution")
        scores = compute_scores(all_answers, ctx, phase=phase)

        cap = scores["capability_pct"]
        ops = scores["operational_pct"]

        # Classify
        diag = classify_diagnostic(cap, ops)
        actual_cls = diag["classification"]
        expected_cls = persona["expected_classification"]
        alternatives = persona.get("alternatives", [])

        # Check match
        if actual_cls == expected_cls:
            match = True
            status = "PASS"
        elif actual_cls in alternatives:
            match = True
            status = "PASS (alt)"
        else:
            match = False
            status = "FAIL"

        if match:
            passed += 1

        results.append({
            "persona": persona,
            "cap": cap,
            "ops": ops,
            "classification": actual_cls,
            "expected": expected_cls,
            "match": match,
            "status": status,
            "questions_visible": scores["questions_visible"],
            "questions_answered": scores["questions_answered"],
        })

        print(f"{persona['id']:>2}  {persona['name']:<30}  {cap:>5.1f}  {ops:>5.1f}  "
              f"{actual_cls:<26}  {expected_cls:<26}  {status}")

    # Summary
    print("-" * 130)
    print(f"\nPassed: {passed}/{total}")

    # Additional diagnostics
    print("\n" + "=" * 90)
    print("DIAGNOSTIC DETAIL")
    print("=" * 90)

    for r in results:
        p = r["persona"]
        print(f"\nP{p['id']:>2}: {p['name']}")
        print(f"     Cap: {r['cap']:.1f}%  Ops: {r['ops']:.1f}%  "
              f"Gap: {abs(r['cap'] - r['ops']):.1f}")
        print(f"     Questions: {r['questions_answered']} answered / "
              f"{r['questions_visible']} visible")
        print(f"     Classification: {r['classification']}")
        if not r["match"]:
            print(f"     *** EXPECTED: {r['expected']} "
                  f"(alternatives: {r['persona'].get('alternatives', [])})")

    # Relative ordering check
    print("\n" + "=" * 90)
    print("RELATIVE ORDERING")
    print("=" * 90)
    print("\nCapability ranking (high to low):")
    by_cap = sorted(results, key=lambda r: r["cap"], reverse=True)
    for i, r in enumerate(by_cap, 1):
        p = r["persona"]
        print(f"  {i:>2}. P{p['id']:>2} {p['name']:<30} Cap={r['cap']:.1f}%")

    print("\nOperational ranking (high to low):")
    by_ops = sorted(results, key=lambda r: r["ops"], reverse=True)
    for i, r in enumerate(by_ops, 1):
        p = r["persona"]
        print(f"  {i:>2}. P{p['id']:>2} {p['name']:<30} Ops={r['ops']:.1f}%")

    # Quadrant coverage
    print("\nQuadrant coverage:")
    quadrants: dict[str, list] = {}
    for r in results:
        cls = r["classification"]
        if cls not in quadrants:
            quadrants[cls] = []
        quadrants[cls].append(f"P{r['persona']['id']}")
    for cls, personas in sorted(quadrants.items()):
        print(f"  {cls:<30} {', '.join(personas)}")

    all_passed = passed == total
    print("\n" + "=" * 90)
    print(f"RESULT: {'ALL PASSED' if all_passed else f'{total - passed} FAILURES'}")
    print("=" * 90)

    return all_passed


if __name__ == "__main__":
    import sys
    success = run_validation()
    sys.exit(0 if success else 1)
