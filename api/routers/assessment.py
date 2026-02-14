"""
Assessment router — question engine endpoints for adaptive filtering + scoring.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.models import (
    VisibleRequest, VisibleResponse, CategoryInfo,
    ScoresRequest, ScoresResponse,
)

from lib.question_engine import (
    get_visible_questions,
    compute_scores,
    classify_diagnostic,
)
from lib.mira_questions import (
    QUESTIONS, CATEGORIES, QUESTION_HELP,
    CATEGORY_DEPENDENCIES, SECOND_LEVEL_BRANCHES, PROGRESSIVE_DISCLOSURE,
)

router = APIRouter(tags=["assessment"])

# Pre-compute all adaptive question IDs — questions whose visibility depends
# on answers to other questions or context. This includes:
# - Questions in skip/add lists of category dependencies
# - Questions added by second-level branches
# - Questions in branch_questions lists
# - Questions in progressive disclosure stages with conditions
_ADAPTIVE_IDS: set[str] = set()

for _cat in CATEGORIES.values():
    _ADAPTIVE_IDS.update(_cat.get("branch_questions", []))
    _ADAPTIVE_IDS.update(_cat.get("conditional_questions", []))

for _dep in CATEGORY_DEPENDENCIES:
    _ADAPTIVE_IDS.update(_dep.get("skip", []))
    _ADAPTIVE_IDS.update(_dep.get("add", []))

for _branch in SECOND_LEVEL_BRANCHES:
    _ADAPTIVE_IDS.update(_branch.get("add", []))

for _pd in PROGRESSIVE_DISCLOSURE:
    for _stage in _pd.get("stages", []):
        if _stage.get("condition"):
            _ADAPTIVE_IDS.update(_stage.get("questions", []))


@router.post("/assessment/visible", response_model=VisibleResponse)
async def get_visible(req: VisibleRequest):
    """Get visible questions with adaptive filtering applied."""
    visible_ids = get_visible_questions(req.answers, req.context)
    visible_set = set(visible_ids)

    # Group by category
    categories = []
    total_answered = 0

    for cat_id, cat in CATEGORIES.items():
        cat_questions = []

        # Collect all questions in this category
        for qlist in ("capability_questions", "operational_questions",
                      "conditional_questions", "branch_questions"):
            for qid in cat.get(qlist, []):
                if qid not in visible_set:
                    continue
                q = QUESTIONS.get(qid)
                if q is None:
                    continue

                is_answered = qid in req.answers
                if is_answered:
                    total_answered += 1

                cat_questions.append({
                    "id": qid,
                    "text": q["text"],
                    "help": QUESTION_HELP.get(qid, ""),
                    "type": q["type"],
                    "dimension": q["dimension"],
                    "weight": q.get("weight", 1.0),
                    "options": q.get("options", []),
                    "min": q.get("min"),
                    "max": q.get("max"),
                    "unit": q.get("unit"),
                    "labels": q.get("labels"),
                    "inverse": q.get("inverse", False),
                    "scoring_order": q.get("scoring_order", "ascending"),
                    "answered": is_answered,
                    "adaptive": qid in _ADAPTIVE_IDS,
                })

        if cat_questions:
            categories.append(CategoryInfo(
                id=cat_id,
                name=cat["name"],
                description=cat.get("description", ""),
                questions=cat_questions,
            ))

    return VisibleResponse(
        categories=categories,
        total_visible=len(visible_ids),
        total_answered=total_answered,
    )


@router.post("/assessment/scores", response_model=ScoresResponse)
async def get_scores(req: ScoresRequest):
    """Compute maturity scores from current answers."""
    result = compute_scores(req.answers, req.context, phase=req.phase)

    return ScoresResponse(
        capability_pct=result["capability_pct"],
        operational_pct=result["operational_pct"],
        unified_pct=result["unified_pct"],
        category_scores=result["category_scores"],
        questions_answered=result["questions_answered"],
        questions_visible=result["questions_visible"],
        phase=result["phase"],
    )
