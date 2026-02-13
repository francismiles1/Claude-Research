"""
Data router — static metadata endpoints and Supabase logging.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from api.models import (
    LogAssessmentRequest, LogIdentifyRequest,
    LogFeedbackRequest, LogMaturityRequest,
    LogSelfMapRequest, LogCalibrationRequest, LogResponse,
)

from viable_zones import (
    ARCHETYPE_DIMENSIONS,
    ARCHETYPE_DEFAULT_POSITIONS,
    ARCHETYPE_ORDER,
)
from dimension_slider_mapping import (
    ARCHETYPE_SLIDER_DEFAULTS,
    SLIDER_SHORT,
    DIMENSION_SHORT,
)
from lib.descriptions import ARCHETYPE_DESCRIPTIONS, PERSONA_DESCRIPTIONS
from mira_bridge import PERSONA_CONTEXTS, PERSONA_EXPECTED
from lib.mira_questions import QUESTIONS, CATEGORIES

logger = logging.getLogger(__name__)

router = APIRouter(tags=["data"])


# ---------------------------------------------------------------------------
# Static metadata (cached in-memory, served on app load)
# ---------------------------------------------------------------------------

_ARCHETYPE_META: dict[str, Any] | None = None


def _build_archetype_meta() -> dict[str, Any]:
    """Build the archetype metadata dict once."""
    global _ARCHETYPE_META
    if _ARCHETYPE_META is not None:
        return _ARCHETYPE_META

    archetypes = {}
    for name in ARCHETYPE_ORDER:
        dims = ARCHETYPE_DIMENSIONS.get(name, [])
        pos = ARCHETYPE_DEFAULT_POSITIONS.get(name, (0.5, 0.5))
        sliders = ARCHETYPE_SLIDER_DEFAULTS.get(name, [0.5, 0.5, 0.5, 0.5])
        archetypes[name] = {
            "dimensions": dims,
            "default_position": list(pos),
            "default_sliders": list(sliders),
            "description": ARCHETYPE_DESCRIPTIONS.get(name, ""),
        }

    # Persona list for identification page
    personas = {}
    for key, ctx in PERSONA_CONTEXTS.items():
        expected = PERSONA_EXPECTED.get(key, [])
        personas[key] = {
            "description": PERSONA_DESCRIPTIONS.get(key, ""),
            "expected_archetypes": expected,
            "context": ctx.get("context", {}),
        }

    _ARCHETYPE_META = {
        "archetypes": archetypes,
        "archetype_order": ARCHETYPE_ORDER,
        "dimension_labels": list(DIMENSION_SHORT),
        "slider_labels": list(SLIDER_SHORT),
        "personas": personas,
    }
    return _ARCHETYPE_META


@router.get("/meta/archetypes")
async def get_archetypes():
    """Static archetype metadata — dimensions, positions, sliders, personas."""
    return _build_archetype_meta()


@router.get("/meta/questions")
async def get_questions():
    """Full question definitions and category structure."""
    # Return categories with their question IDs, plus full question dict
    categories = {}
    for cat_id, cat in CATEGORIES.items():
        categories[cat_id] = {
            "name": cat["name"],
            "description": cat.get("description", ""),
            "capability_questions": cat.get("capability_questions", []),
            "operational_questions": cat.get("operational_questions", []),
            "branch_only": cat.get("branch_only", False),
        }

    return {
        "questions": {qid: q for qid, q in QUESTIONS.items()},
        "categories": categories,
    }


# ---------------------------------------------------------------------------
# Supabase logging — direct REST API (avoids supabase-py HTTP/2 issues)
# ---------------------------------------------------------------------------

def _supabase_insert(table: str, row: dict) -> str | None:
    """Insert a row into a Supabase table via PostgREST. Returns id or None."""
    try:
        from api.config import SUPABASE_URL, SUPABASE_KEY
        if not SUPABASE_URL or not SUPABASE_KEY:
            return None
        import httpx
        resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            json=row,
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data[0]["id"] if data else None
    except Exception as e:
        logger.warning("Supabase insert into %s failed: %s", table, e)
        return None


@router.post("/log/assessment", response_model=LogResponse)
async def log_assessment(req: LogAssessmentRequest):
    """Log assessment to Supabase (anonymous, insert-only)."""
    dims = req.bridge_result.get("dimensions", [0] * 8)
    row = {
        "session_id": req.session_id,
        "flow_type": req.flow_type,
        "archetype": req.bridge_result.get("archetype", "unknown"),
        "match_distance": req.bridge_result.get("match_distance", 0),
        "confidence": req.bridge_result.get("confidence", "unknown"),
        "d1_consequence": dims[0] if len(dims) > 0 else 0,
        "d2_market": dims[1] if len(dims) > 1 else 0,
        "d3_complexity": dims[2] if len(dims) > 2 else 0,
        "d4_regulation": dims[3] if len(dims) > 3 else 0,
        "d5_stability": dims[4] if len(dims) > 4 else 0,
        "d6_outsourcing": dims[5] if len(dims) > 5 else 0,
        "d7_lifecycle": dims[6] if len(dims) > 6 else 0,
        "d8_coherence": dims[7] if len(dims) > 7 else 0,
        "slider_inv": req.sliders[0] if len(req.sliders) > 0 else 0.5,
        "slider_rec": req.sliders[1] if len(req.sliders) > 1 else 0.5,
        "slider_owk": req.sliders[2] if len(req.sliders) > 2 else 0.5,
        "slider_time": req.sliders[3] if len(req.sliders) > 3 else 0.5,
        "default_cap": req.cap,
        "default_ops": req.ops,
        "assessed_cap": req.assessed_cap,
        "assessed_ops": req.assessed_ops,
        "ctx_scale": req.context.get("scale", ""),
        "ctx_delivery": req.context.get("delivery_model", ""),
        "ctx_stage": req.context.get("product_stage", ""),
        "ctx_phase": req.context.get("project_phase", ""),
        "ctx_regulatory": req.context.get("regulatory_standards", []),
        "ctx_audit": req.context.get("audit_frequency", "none"),
        "ctx_has_third_party": req.context.get("has_third_party", False),
        "has_calibration_changes": req.has_calibration_changes,
    }
    row_id = _supabase_insert("assessments", row)
    return LogResponse(id=row_id)


@router.post("/log/identify", response_model=LogResponse)
async def log_identify(req: LogIdentifyRequest):
    """Log self-identification to Supabase."""
    row: dict[str, Any] = {
        "session_id": req.session_id,
        "assessment_id": req.assessment_id,
        "id_type": req.id_type,
        "persona_name": req.persona_name,
    }
    if req.new_persona:
        row["new_label"] = req.new_persona.get("label")
        row["new_description"] = req.new_persona.get("description")
    row_id = _supabase_insert("identifications", row)
    return LogResponse(id=row_id)


@router.post("/log/feedback", response_model=LogResponse)
async def log_feedback(req: LogFeedbackRequest):
    """Log feedback to Supabase."""
    row = {
        "session_id": req.session_id,
        "assessment_id": req.assessment_id,
        "feedback_text": req.feedback_text,
        "rating": req.rating,
        "display_name": req.display_name,
        "category_notes_json": req.category_notes or {},
    }
    row_id = _supabase_insert("feedback", row)
    return LogResponse(id=row_id)


@router.post("/log/maturity", response_model=LogResponse)
async def log_maturity(req: LogMaturityRequest):
    """Log maturity assessment answers and scores to Supabase."""
    row = {
        "session_id": req.session_id,
        "assessment_id": req.assessment_id,
        "answers_json": req.answers,
        "capability_pct": req.capability_pct,
        "operational_pct": req.operational_pct,
        "unified_pct": req.unified_pct,
        "category_scores_json": req.category_scores,
        "questions_answered": req.questions_answered,
        "questions_visible": req.questions_visible,
    }
    row_id = _supabase_insert("maturity_scores", row)
    return LogResponse(id=row_id)


@router.post("/log/self_map", response_model=LogResponse)
async def log_self_map(req: LogSelfMapRequest):
    """Log self-mapping choice to Supabase (the key research data)."""
    row = {
        "session_id": req.session_id,
        "assessment_id": req.assessment_id,
        "user_choice": req.user_choice,
        "user_says_none_match": req.user_says_none_match,
        "none_match_description": req.none_match_description,
        "system_match": req.system_match,
        "system_distance": req.system_distance,
        "system_confidence": req.system_confidence,
    }
    row_id = _supabase_insert("self_mappings", row)
    return LogResponse(id=row_id)


@router.post("/log/calibration", response_model=LogResponse)
async def log_calibration(req: LogCalibrationRequest):
    """Log practitioner calibration — slider/position deviations for archetype tuning."""
    row: dict[str, Any] = {
        "session_id": req.session_id,
        "assessment_id": req.assessment_id,
        "archetype": req.archetype,
        "trigger": req.trigger,
        "flow_type": req.flow_type,
        "default_inv": round(req.default_sliders[0], 4),
        "default_rec": round(req.default_sliders[1], 4),
        "default_owk": round(req.default_sliders[2], 4),
        "default_time": round(req.default_sliders[3], 4),
        "adjusted_inv": round(req.current_sliders[0], 4),
        "adjusted_rec": round(req.current_sliders[1], 4),
        "adjusted_owk": round(req.current_sliders[2], 4),
        "adjusted_time": round(req.current_sliders[3], 4),
        "default_cap": round(req.default_cap, 4),
        "default_ops": round(req.default_ops, 4),
        "assessed_cap": round(req.assessed_cap, 4) if req.assessed_cap is not None else None,
        "assessed_ops": round(req.assessed_ops, 4) if req.assessed_ops is not None else None,
        "inspect_cap": round(req.inspect_cap, 4) if req.inspect_cap is not None else None,
        "inspect_ops": round(req.inspect_ops, 4) if req.inspect_ops is not None else None,
        "context_answers": req.context_answers,
        "maturity_answers": req.maturity_answers,
        "capability_pct": round(req.capability_pct, 2) if req.capability_pct is not None else None,
        "operational_pct": round(req.operational_pct, 2) if req.operational_pct is not None else None,
        "reason": req.reason[:500] if req.reason else None,
    }
    row_id = _supabase_insert("practitioner_calibrations", row)
    return LogResponse(id=row_id)
