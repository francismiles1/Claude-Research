"""
Anonymous data capture layer for the Cap/Ops Balance Model.

Provides insert-only access to Supabase (EU, free tier) for logging
assessment results and self-identifications. No PII is captured.

Graceful fallback: if Supabase is unavailable or unconfigured, all
logging functions silently return None — the app continues to work.

Configure via Streamlit secrets (.streamlit/secrets.toml or Cloud dashboard):
    [supabase]
    url = "https://your-project.supabase.co"
    key = "your-anon-key"
"""

from __future__ import annotations

import uuid
import logging

import streamlit as st

logger = logging.getLogger(__name__)


def _get_client():
    """Return a cached Supabase client, or None if unavailable."""
    try:
        from supabase import create_client
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception:
        # Supabase not configured or package not installed — silent fallback
        return None


def generate_session_id() -> str:
    """Generate a random session UUID (no tracking, no cookies)."""
    return str(uuid.uuid4())


def log_assessment(
    session_id: str,
    bridge_result: dict,
    context: dict,
    sliders: list[float],
    cap: float,
    ops: float,
) -> str | None:
    """
    Log an assessment to the assessments table.

    Returns the assessment UUID on success, or None on failure/fallback.
    """
    client = _get_client()
    if client is None:
        return None

    try:
        dims = bridge_result["dimensions"]
        row = {
            "session_id": session_id,
            "d1_consequence": dims[0],
            "d2_market": dims[1],
            "d3_complexity": dims[2],
            "d4_regulation": dims[3],
            "d5_stability": dims[4],
            "d6_outsourcing": dims[5],
            "d7_lifecycle": dims[6],
            "d8_coherence": dims[7],
            "archetype": bridge_result["archetype"],
            "match_distance": round(bridge_result["match_distance"], 3),
            "confidence": bridge_result["confidence"],
            "slider_inv": round(sliders[0], 4),
            "slider_rec": round(sliders[1], 4),
            "slider_owk": round(sliders[2], 4),
            "slider_time": round(sliders[3], 4),
            "default_cap": round(cap, 4),
            "default_ops": round(ops, 4),
            "ctx_scale": context.get("scale", "medium"),
            "ctx_delivery": context.get("delivery_model", "hybrid_agile"),
            "ctx_stage": context.get("product_stage", "growth"),
            "ctx_phase": context.get("project_phase", "execution"),
            "ctx_regulatory": context.get("regulatory_standards", []),
            "ctx_audit": context.get("audit_frequency", "none"),
            "ctx_has_third_party": context.get("has_third_party", False),
        }

        result = client.table("assessments").insert(row).execute()
        if result.data:
            return result.data[0].get("id")
        return None
    except Exception as exc:
        logger.warning("Failed to log assessment: %s", exc)
        return None


def log_identification(
    session_id: str,
    assessment_id: str | None,
    id_type: str,
    persona_name: str | None = None,
    new_persona: dict | None = None,
) -> str | None:
    """
    Log a self-identification to the identifications table.

    id_type: "existing_persona" | "new_persona" | "skip"

    Returns the identification UUID on success, or None on failure/fallback.
    """
    client = _get_client()
    if client is None:
        return None

    try:
        row = {
            "session_id": session_id,
            "assessment_id": assessment_id,
            "id_type": id_type,
            "persona_name": persona_name,
        }

        # Structured new persona fields (all categorical)
        if new_persona:
            row["new_label"] = new_persona.get("label", "")[:50]
            row["new_scale"] = new_persona.get("scale")
            row["new_delivery"] = new_persona.get("delivery")
            row["new_stage"] = new_persona.get("stage")
            row["new_reg_level"] = new_persona.get("reg_level")
            row["new_team_knowledge"] = new_persona.get("team_knowledge")
            row["new_outsourcing"] = new_persona.get("outsourcing")
            row["new_crisis_state"] = new_persona.get("crisis_state")
            row["new_overwork"] = new_persona.get("overwork")

        result = client.table("identifications").insert(row).execute()
        if result.data:
            return result.data[0].get("id")
        return None
    except Exception as exc:
        logger.warning("Failed to log identification: %s", exc)
        return None


def log_slider_adjustment(
    session_id: str,
    assessment_id: str | None,
    sliders: list[float],
    inspect_cap: float,
    inspect_ops: float,
) -> str | None:
    """
    Log a slider adjustment (Phase 3 — table may not exist yet).

    Returns the row UUID on success, or None on failure/fallback.
    """
    client = _get_client()
    if client is None:
        return None

    try:
        row = {
            "session_id": session_id,
            "assessment_id": assessment_id,
            "slider_inv": round(sliders[0], 4),
            "slider_rec": round(sliders[1], 4),
            "slider_owk": round(sliders[2], 4),
            "slider_time": round(sliders[3], 4),
            "inspect_cap": round(inspect_cap, 4),
            "inspect_ops": round(inspect_ops, 4),
        }
        result = client.table("slider_adjustments").insert(row).execute()
        if result.data:
            return result.data[0].get("id")
        return None
    except Exception as exc:
        logger.warning("Failed to log slider adjustment: %s", exc)
        return None


def log_feedback(
    session_id: str,
    assessment_id: str | None,
    feedback_text: str,
    rating: int | None = None,
    display_name: str | None = None,
) -> str | None:
    """
    Log user feedback to the feedback table.

    display_name is optional — anonymous by default, declared if provided.
    feedback_text is free-form (max 2000 chars, sanitised at capture).
    rating is 1-5 (optional).

    Returns the feedback UUID on success, or None on failure/fallback.
    """
    client = _get_client()
    if client is None:
        return None

    try:
        row = {
            "session_id": session_id,
            "assessment_id": assessment_id,
            "feedback_text": feedback_text[:2000],
            "rating": rating,
            "display_name": display_name[:100] if display_name else None,
            "is_anonymous": display_name is None or display_name.strip() == "",
        }
        result = client.table("feedback").insert(row).execute()
        if result.data:
            return result.data[0].get("id")
        return None
    except Exception as exc:
        logger.warning("Failed to log feedback: %s", exc)
        return None


def fetch_aggregate_stats() -> list[dict] | None:
    """
    Fetch aggregate statistics from the aggregate_stats view.

    Returns a list of dicts (one per archetype with n>=3), or None if unavailable.
    """
    client = _get_client()
    if client is None:
        return None

    try:
        result = client.table("aggregate_stats").select("*").execute()
        return result.data if result.data else []
    except Exception as exc:
        logger.warning("Failed to fetch aggregate stats: %s", exc)
        return None
