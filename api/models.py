"""
Pydantic request/response models for all API endpoints.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Context endpoint
# ---------------------------------------------------------------------------

class ContextRequest(BaseModel):
    """Project context from the 9-question wizard."""
    scale: str = Field(..., description="small | medium | large | enterprise")
    delivery_model: str = Field(..., description="agile | devops | hybrid_agile | hybrid_traditional | waterfall | v_model")
    product_stage: str = Field(..., description="startup | growth | mature | legacy")
    project_phase: str = Field(..., description="planning | early_dev | mid_dev | testing_phase | transition | closure | maintenance")
    regulatory_standards: list[str] = Field(default_factory=list)
    audit_frequency: str = Field(default="none", description="none | annual | bi_annual | quarterly | continuous")
    complexity: int = Field(default=3, ge=1, le=5, description="System complexity 1-5")
    team_stability: int = Field(default=3, ge=1, le=5, description="Team stability 1-5")
    has_third_party: bool = Field(default=False)


class ContextResponse(BaseModel):
    archetype: str
    dimensions: list[int]
    match_distance: float
    confidence: str
    alternatives: list[list[Any]]
    default_sliders: list[float]
    default_position: list[float]
    cap: float | None = None
    ops: float | None = None


# ---------------------------------------------------------------------------
# Grid endpoint
# ---------------------------------------------------------------------------

class GridRequest(BaseModel):
    dimensions: list[int] = Field(..., min_length=8, max_length=8)
    sliders: list[float] = Field(..., min_length=4, max_length=4)


class GridResponse(BaseModel):
    """101x101 heatmap grid data + zone metrics."""
    grid: list[list[list[float]]]
    gradient_grid: list[list[list[float]]]
    zone_area: float
    cap_range: list[float]
    ops_range: list[float]
    cap_floor: float
    ops_floor: float


class InspectRequest(BaseModel):
    cap: float = Field(..., ge=0.0, le=1.0)
    ops: float = Field(..., ge=0.0, le=1.0)
    dimensions: list[int] = Field(..., min_length=8, max_length=8)
    sliders: list[float] = Field(..., min_length=4, max_length=4)


class InspectResponse(BaseModel):
    scores: dict[str, float]
    cost_breakdown: dict[str, Any]


# ---------------------------------------------------------------------------
# Assessment endpoints
# ---------------------------------------------------------------------------

class VisibleRequest(BaseModel):
    answers: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)


class CategoryInfo(BaseModel):
    id: str
    name: str
    description: str
    questions: list[dict[str, Any]]


class VisibleResponse(BaseModel):
    categories: list[CategoryInfo]
    total_visible: int
    total_answered: int


class ScoresRequest(BaseModel):
    answers: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    phase: str = Field(default="execution")


class ScoresResponse(BaseModel):
    capability_pct: float
    operational_pct: float
    unified_pct: float
    category_scores: dict[str, Any]
    questions_answered: int
    questions_visible: int
    phase: str


# ---------------------------------------------------------------------------
# Logging endpoints
# ---------------------------------------------------------------------------

class LogAssessmentRequest(BaseModel):
    session_id: str
    bridge_result: dict[str, Any]
    context: dict[str, Any]
    sliders: list[float] = Field(default_factory=list)
    cap: float = 0.0
    ops: float = 0.0
    assessed_cap: float | None = None
    assessed_ops: float | None = None


class LogIdentifyRequest(BaseModel):
    session_id: str
    assessment_id: str | None = None
    id_type: str
    persona_name: str | None = None
    new_persona: dict[str, Any] | None = None


class LogFeedbackRequest(BaseModel):
    session_id: str
    assessment_id: str | None = None
    feedback_text: str = ""
    rating: int | None = None
    display_name: str | None = None
    category_notes: dict[str, str] = Field(default_factory=dict)


class LogMaturityRequest(BaseModel):
    session_id: str
    assessment_id: str | None = None
    answers: dict[str, Any] = Field(default_factory=dict)
    capability_pct: float = 0.0
    operational_pct: float = 0.0
    unified_pct: float = 0.0
    category_scores: dict[str, Any] = Field(default_factory=dict)
    questions_answered: int = 0
    questions_visible: int = 0


class LogSelfMapRequest(BaseModel):
    session_id: str
    assessment_id: str | None = None
    user_choice: str | None = None
    user_says_none_match: bool = False
    none_match_description: str = ""
    system_match: str = ""
    system_distance: float = 0.0
    system_confidence: str = ""


class LogCalibrationRequest(BaseModel):
    """Practitioner calibration — slider/position deviations for archetype tuning."""
    session_id: str
    assessment_id: str | None = None
    archetype: str
    trigger: str = Field(..., description="manual | archetype_change")
    default_sliders: list[float] = Field(..., min_length=4, max_length=4)
    current_sliders: list[float] = Field(..., min_length=4, max_length=4)
    default_cap: float
    default_ops: float
    assessed_cap: float | None = None
    assessed_ops: float | None = None
    inspect_cap: float | None = None
    inspect_ops: float | None = None
    context_answers: dict[str, Any] | None = None
    maturity_answers: dict[str, Any] | None = None
    capability_pct: float | None = None
    operational_pct: float | None = None
    reason: str | None = None


class LogResponse(BaseModel):
    id: str | None = None
