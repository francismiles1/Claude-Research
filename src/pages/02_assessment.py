"""
Assessment page — two-phase assessment:
  Phase 1: 9 context questions → archetype match via MIRA bridge
  Phase 2: Full maturity assessment → genuine Cap/Ops scores via engine

Phase 1 determines the project's structural archetype and dimensions.
Phase 2 asks category-by-category maturity questions with adaptive
filtering, producing real capability and operational maturity percentages.
"""

from __future__ import annotations

import streamlit as st

from mira_bridge import bridge_mira_to_simulation
from dimension_slider_mapping import ARCHETYPE_SLIDER_DEFAULTS
from viable_zones import ARCHETYPE_DEFAULT_POSITIONS
from lib.components import (
    SCALE_OPTIONS,
    DELIVERY_OPTIONS,
    STAGE_OPTIONS,
    PHASE_OPTIONS,
    REGULATORY_OPTIONS,
    AUDIT_OPTIONS,
)
from lib.mira_questions import (
    QUESTIONS,
    CATEGORIES,
    TYPE_TOGGLE,
    TYPE_SELECT,
    TYPE_SLIDER,
    TYPE_MULTISELECT,
    TYPE_NUMBER,
)
from lib.question_engine import (
    get_visible_questions,
    compute_scores,
    normalise_answer,
)
from lib.supabase_client import log_assessment


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "mira_answers" not in st.session_state:
    st.session_state["mira_answers"] = {}
if "context_done" not in st.session_state:
    st.session_state["context_done"] = False


# ---------------------------------------------------------------------------
# Widget rendering helpers
# ---------------------------------------------------------------------------

def _render_question(qid: str, q: dict) -> None:
    """Render a single maturity question as a Streamlit widget.

    Stores answer directly in st.session_state['mira_answers'].
    """
    answers = st.session_state["mira_answers"]
    current = answers.get(qid)
    qtype = q["type"]
    text = q["text"]
    key = f"mq_{qid}"

    if qtype == TYPE_TOGGLE:
        options = [opt["label"] for opt in q["options"]]
        values = [opt["value"] for opt in q["options"]]
        idx = values.index(current) if current in values else None
        choice = st.radio(text, options, index=idx, key=key, horizontal=True)
        if choice is not None:
            answers[qid] = values[options.index(choice)]

    elif qtype == TYPE_SELECT:
        options = q.get("options", [])
        labels = [opt["label"] for opt in options]
        values = [opt["value"] for opt in options]
        idx = values.index(current) if current in values else 0
        choice = st.selectbox(text, labels, index=idx, key=key)
        if choice is not None:
            answers[qid] = values[labels.index(choice)]

    elif qtype == TYPE_SLIDER:
        qmin = q.get("min", 0)
        qmax = q.get("max", 100)
        unit = q.get("unit", "")
        labels = q.get("labels", {})
        val = current if current is not None else qmin
        # Determine step
        if qmax - qmin <= 10:
            step = 1
        else:
            step = 5 if qmax - qmin > 50 else 1

        help_text = None
        if labels:
            help_text = f"{labels.get('min', '')} → {labels.get('max', '')}"

        result = st.slider(
            text, min_value=qmin, max_value=qmax,
            value=int(val), step=step, key=key,
            help=help_text,
        )
        answers[qid] = result

    elif qtype == TYPE_NUMBER:
        qmin = q.get("min", 0)
        qmax = q.get("max", 100)
        val = current if current is not None else qmin
        result = st.number_input(
            text, min_value=qmin, max_value=qmax,
            value=int(val), key=key,
        )
        answers[qid] = result

    elif qtype == TYPE_MULTISELECT:
        options = q.get("options", [])
        labels = [opt["label"] for opt in options]
        values = [opt["value"] for opt in options]
        defaults = current if isinstance(current, list) else []
        default_labels = [labels[values.index(v)] for v in defaults if v in values]
        selected = st.multiselect(text, labels, default=default_labels, key=key)
        answers[qid] = [values[labels.index(lbl)] for lbl in selected]


# ---------------------------------------------------------------------------
# Phase 1: Project Context
# ---------------------------------------------------------------------------

st.header("Assess Your Project")

phase1 = st.container()
with phase1:
    st.subheader("Phase 1: Project Context")
    st.caption(
        "Answer 9 questions about your project context. This determines your "
        "structural archetype and enables adaptive question filtering."
    )

    with st.form("context_form"):
        col1, col2 = st.columns(2)

        with col1:
            scale = st.selectbox(
                "1. Organisation scale", SCALE_OPTIONS, index=1,
                help="small (<10 devs), medium (10-50), large (50-200), enterprise (200+)",
            )
            delivery = st.selectbox(
                "2. Delivery model", DELIVERY_OPTIONS, index=0,
                help="How does your team deliver software?",
            )
            stage = st.selectbox(
                "3. Product stage", STAGE_OPTIONS, index=1,
                help="What stage is your product at?",
            )
            phase = st.selectbox(
                "4. Current project phase", PHASE_OPTIONS, index=4,
                help="Where is the project right now in its lifecycle?",
            )

        with col2:
            regulatory = st.multiselect(
                "5. Regulatory standards that apply",
                REGULATORY_OPTIONS, default=[],
                help="Select all that apply. Leave empty if none.",
            )
            audit = st.selectbox(
                "6. Audit frequency", AUDIT_OPTIONS, index=0,
                help="How often is your project formally audited?",
            )

            complexity_labels = {
                1: "1 — Simple", 2: "2 — Low", 3: "3 — Moderate",
                4: "4 — High", 5: "5 — Extreme",
            }
            complexity = st.select_slider(
                "7. System complexity", options=[1, 2, 3, 4, 5], value=3,
                format_func=lambda x: complexity_labels[x],
                help="How complex is the system architecture?",
            )

            stability_labels = {
                1: "1 — High churn", 2: "2 — Unstable",
                3: "3 — Some stability", 4: "4 — Stable",
                5: "5 — Very stable",
            }
            stability = st.select_slider(
                "8. Team stability", options=[1, 2, 3, 4, 5], value=3,
                format_func=lambda x: stability_labels[x],
                help="How stable is the team composition?",
            )

            has_third_party = st.radio(
                "9. Significant third-party suppliers?",
                ["No", "Yes"], index=0, horizontal=True,
                help="Does your project rely on outsourced or third-party development?",
            )

        context_submitted = st.form_submit_button(
            "Determine Archetype", type="primary",
        )

    # Process Phase 1 submission
    if context_submitted:
        arc_o1_score = complexity * 2
        gov_o2_score = stability * 20
        tpp_c2_score = 80 if has_third_party == "Yes" else 0

        mira_data = {
            "context": {
                "scale": scale,
                "delivery_model": delivery,
                "product_stage": stage,
                "project_phase": phase,
                "regulatory_standards": regulatory,
                "audit_frequency": audit,
            },
            "answers": {
                "ARC-O1": arc_o1_score,
                "GOV-O2": gov_o2_score,
                "TPP-C2": tpp_c2_score,
            },
        }

        result = bridge_mira_to_simulation(mira_data)
        archetype = result["archetype"]
        defaults = ARCHETYPE_SLIDER_DEFAULTS[archetype]
        default_pos = ARCHETYPE_DEFAULT_POSITIONS[archetype]

        st.session_state["bridge_result"] = result
        st.session_state["assessment_context"] = mira_data["context"]
        st.session_state["default_sliders"] = list(defaults)
        st.session_state["current_sliders"] = list(defaults)
        st.session_state["inspect_cap"] = result.get("cap", default_pos[0])
        st.session_state["inspect_ops"] = result.get("ops", default_pos[1])
        st.session_state["context_done"] = True

        # Pre-seed maturity answers from context questions
        answers = st.session_state["mira_answers"]
        answers["ARC-O1"] = arc_o1_score
        answers["GOV-O2"] = gov_o2_score
        if tpp_c2_score > 0:
            answers["TPT-O1"] = 3  # Has suppliers
        else:
            answers["TPT-O1"] = 0  # No suppliers

        st.rerun()


# ---------------------------------------------------------------------------
# Phase 1 result display
# ---------------------------------------------------------------------------

bridge_result = st.session_state.get("bridge_result")

if bridge_result is not None and st.session_state.get("context_done"):
    archetype = bridge_result["archetype"]
    confidence = bridge_result["confidence"]
    conf_icon = {
        "strong": "\U0001f7e2", "reasonable": "\U0001f7e1", "ambiguous": "\U0001f534",
    }
    st.success(
        f"{conf_icon.get(confidence, '')} Matched to **{archetype}** "
        f"({confidence}, distance: {bridge_result['match_distance']:.1f})"
    )

    # Quick path to results (skip Phase 2)
    col_skip, col_continue = st.columns(2)
    with col_skip:
        if st.button("Skip to Results (archetype defaults) \u2192"):
            st.switch_page("pages/03_results.py")
    with col_continue:
        st.caption(
            "Or continue below for the full maturity assessment to "
            "determine your actual Cap/Ops position."
        )


# ---------------------------------------------------------------------------
# Phase 2: Maturity Assessment
# ---------------------------------------------------------------------------

if not st.session_state.get("context_done"):
    st.info("Complete Phase 1 above to unlock the maturity assessment.")
    st.stop()

st.divider()
st.subheader("Phase 2: Maturity Assessment")
st.caption(
    "Answer the questions below to determine your actual capability and "
    "operational maturity. Questions adapt based on your answers — not all "
    "categories will apply to every project."
)

# Get current state
answers = st.session_state["mira_answers"]
context = st.session_state.get("assessment_context", {})
visible = set(get_visible_questions(answers, context))

# Progress tracking
total_visible = len(visible)
answered = sum(1 for qid in visible if qid in answers)
if total_visible > 0:
    progress = answered / total_visible
    st.progress(progress, text=f"{answered}/{total_visible} questions answered ({progress:.0%})")

# Render categories as expanders
CORE_CATEGORIES = [
    cat_id for cat_id, cat in CATEGORIES.items()
    if not cat.get("branch_only")
]

for cat_id in CORE_CATEGORIES:
    cat = CATEGORIES[cat_id]

    # Collect visible questions for this category
    cat_qs = []
    for qlist in ("capability_questions", "operational_questions",
                  "conditional_questions"):
        for qid in cat.get(qlist, []):
            if qid in visible:
                cat_qs.append(qid)

    if not cat_qs:
        continue

    # Count answered in this category
    cat_answered = sum(1 for qid in cat_qs if qid in answers)
    status = f"{cat_answered}/{len(cat_qs)}"

    with st.expander(f"{cat['name']} ({status})", expanded=(cat_answered == 0)):
        st.caption(cat["description"])

        for qid in cat_qs:
            q = QUESTIONS[qid]
            _render_question(qid, q)

# Branch categories (only show if triggered)
for cat_id, cat in CATEGORIES.items():
    if not cat.get("branch_only"):
        continue

    branch_qs = [qid for qid in cat.get("branch_questions", []) if qid in visible]
    if not branch_qs:
        continue

    cat_answered = sum(1 for qid in branch_qs if qid in answers)
    status = f"{cat_answered}/{len(branch_qs)}"

    with st.expander(f"\U0001f50d {cat['name']} ({status})", expanded=True):
        st.caption(cat["description"])
        for qid in branch_qs:
            q = QUESTIONS[qid]
            _render_question(qid, q)


# ---------------------------------------------------------------------------
# Complete assessment
# ---------------------------------------------------------------------------

st.divider()

# Compute live scores
phase_name = context.get("project_phase", "execution")
result = compute_scores(answers, context, phase=phase_name)

# Live score preview
col_cap, col_ops, col_uni = st.columns(3)
with col_cap:
    st.metric("Capability", f"{result['capability_pct']:.0f}%")
with col_ops:
    st.metric("Operational", f"{result['operational_pct']:.0f}%")
with col_uni:
    st.metric("Unified", f"{result['unified_pct']:.0f}%")

if st.button("Complete Assessment \u2192", type="primary"):
    # Store engine scores alongside bridge result
    bridge = st.session_state["bridge_result"]
    archetype = bridge["archetype"]
    defaults = ARCHETYPE_SLIDER_DEFAULTS[archetype]
    default_pos = ARCHETYPE_DEFAULT_POSITIONS[archetype]

    # Use engine scores for Cap/Ops position (normalised to 0-1)
    cap = result["capability_pct"] / 100.0
    ops = result["operational_pct"] / 100.0

    st.session_state["engine_scores"] = result
    st.session_state["inspect_cap"] = round(cap, 2)
    st.session_state["inspect_ops"] = round(ops, 2)
    st.session_state["default_sliders"] = list(defaults)
    st.session_state["current_sliders"] = list(defaults)

    # Log to Supabase
    session_id = st.session_state.get("session_uuid")
    if session_id and st.session_state.get("consent_given", False):
        assessment_id = log_assessment(
            session_id=session_id,
            bridge_result=bridge,
            context=context,
            sliders=list(defaults),
            cap=cap,
            ops=ops,
        )
        st.session_state["assessment_id"] = assessment_id

    st.switch_page("pages/03_results.py")
