"""
Context router — maps project context to archetype via MIRA bridge.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.models import ContextRequest, ContextResponse

from mira_bridge import bridge_mira_to_simulation
from viable_zones import ARCHETYPE_DEFAULT_POSITIONS
from dimension_slider_mapping import ARCHETYPE_SLIDER_DEFAULTS

router = APIRouter(tags=["context"])


@router.post("/context", response_model=ContextResponse)
async def submit_context(req: ContextRequest):
    """Map 9 context questions to archetype + dimensions."""

    # Build mira_data dict matching bridge expectations
    mira_data = {
        "context": {
            "regulatory_standards": req.regulatory_standards,
            "scale": req.scale,
            "delivery_model": req.delivery_model,
            "product_stage": req.product_stage,
            "project_phase": req.project_phase,
            "audit_frequency": req.audit_frequency,
        },
        # Map direct dimension inputs to MIRA answer format
        "answers": {
            "ARC-O1": req.complexity * 2,    # 1-5 → 2-10 complexity scale
            "GOV-O2": req.team_stability * 20,  # 1-5 → 20-100 stability %
            "TPP-C2": req.has_third_party,
        },
    }

    result = bridge_mira_to_simulation(mira_data)

    # Augment with slider defaults and default position
    archetype = result["archetype"]
    default_sliders = list(ARCHETYPE_SLIDER_DEFAULTS.get(archetype, [0.5, 0.5, 0.5, 0.5]))
    default_pos = list(ARCHETYPE_DEFAULT_POSITIONS.get(archetype, (0.5, 0.5)))

    return ContextResponse(
        archetype=result["archetype"],
        dimensions=result["dimensions"],
        match_distance=result["match_distance"],
        confidence=result["confidence"],
        alternatives=result["alternatives"],
        default_sliders=default_sliders,
        default_position=default_pos,
        cap=result.get("cap"),
        ops=result.get("ops"),
    )
