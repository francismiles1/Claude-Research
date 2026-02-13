"""
Identify page — self-identification against existing personas,
new persona definition, and feedback.
"""

from __future__ import annotations

import streamlit as st

from mira_bridge import bridge_mira_to_simulation, PERSONA_CONTEXTS
from dimension_slider_mapping import ARCHETYPE_SLIDER_DEFAULTS
from viable_zones import ARCHETYPE_DEFAULT_POSITIONS
from lib.components import (
    PERSONA_DESCRIPTIONS,
    ARCHETYPE_DESCRIPTIONS,
    render_persona_correlation,
)
from lib.supabase_client import log_identification, log_feedback


# ---------------------------------------------------------------------------
# Guard: redirect if no assessment result
# ---------------------------------------------------------------------------

bridge_result = st.session_state.get("bridge_result")

if bridge_result is None:
    st.warning("No assessment found. Please complete the assessment first.")
    if st.button("Go to Assessment \u2192"):
        st.switch_page("pages/02_assessment.py")
    st.stop()


# ---------------------------------------------------------------------------
# Self-identification
# ---------------------------------------------------------------------------

st.header("Identify Your Project")
st.caption(
    "Help validate the research by telling us which persona best matches "
    "your real-world project experience."
)

archetype = bridge_result["archetype"]
st.info(
    f"The model matched your project to **{archetype}**. "
    f"Does this feel right, or is your project closer to something else?"
)

id_mode = st.radio(
    "Which best describes your situation?",
    [
        "One of these personas matches my project",
        "My project is different — I'll define a new persona",
        "Prefer not to say",
    ],
    key="id_mode",
)


# ---------------------------------------------------------------------------
# Mode 1: Existing persona
# ---------------------------------------------------------------------------

if id_mode == "One of these personas matches my project":
    persona_names = list(PERSONA_DESCRIPTIONS.keys())
    persona = st.selectbox(
        "Select the persona closest to your project",
        persona_names,
        key="id_persona",
        help="Pick the one that most closely matches your real-world experience.",
    )

    # Show description
    desc = PERSONA_DESCRIPTIONS.get(persona, "")
    st.caption(desc)

    if st.button("Submit identification", type="primary", key="submit_existing"):
        session_id = st.session_state.get("session_uuid")
        assessment_id = st.session_state.get("assessment_id")
        if session_id and st.session_state.get("consent_given", False):
            log_identification(
                session_id=session_id,
                assessment_id=assessment_id,
                id_type="existing_persona",
                persona_name=persona,
            )
        st.success(f"Thanks! You identified as **{persona}**.")
        st.session_state["identification_done"] = True


# ---------------------------------------------------------------------------
# Mode 2: New persona definition (structured categorical)
# ---------------------------------------------------------------------------

elif id_mode == "My project is different — I'll define a new persona":
    st.markdown("#### Define Your Project Persona")
    st.caption(
        "All fields are categorical \u2014 no company or project names needed. "
        "This helps us discover project types not yet covered by the model."
    )

    with st.form("new_persona_form"):
        label = st.text_input(
            "Short persona label (max 50 characters)",
            max_chars=50,
            placeholder="e.g. 'Healthcare SaaS Scale-Up'",
            help="A brief, descriptive name. Do NOT include company or project names.",
        )
        st.caption("\u26a0\ufe0f No company names, project names, or identifying information.")

        col1, col2 = st.columns(2)

        with col1:
            np_scale = st.selectbox(
                "Organisation scale",
                ["small", "medium", "large", "enterprise"],
                index=1,
            )
            np_delivery = st.selectbox(
                "Delivery approach",
                ["agile", "devops", "waterfall", "v_model", "hybrid_agile", "hybrid_traditional"],
                index=0,
            )
            np_stage = st.selectbox(
                "Product stage",
                ["startup", "growth", "mature", "legacy"],
                index=1,
            )
            np_reg_level = st.selectbox(
                "Regulatory pressure",
                ["None", "Light", "Moderate", "Heavy", "Life-safety"],
                index=0,
            )

        with col2:
            np_team_knowledge = st.selectbox(
                "Team knowledge retention",
                ["Tribal", "Informal", "Semi-documented", "Codified", "Institutionalised"],
                index=2,
            )
            np_outsourcing = st.selectbox(
                "Third-party dependency",
                ["In-house", "Selective", "Significant", "Heavy", "Fully outsourced"],
                index=0,
            )
            np_crisis = st.selectbox(
                "Crisis state",
                ["Stable", "Emerging issues", "Active crisis", "Post-crisis"],
                index=0,
            )
            np_overwork = st.selectbox(
                "Overwork reality",
                ["Normal hours", "Regular late nights", "Sustained crunch", "Heroics"],
                index=0,
            )

        submitted = st.form_submit_button("Submit new persona", type="primary")

    if submitted:
        new_persona = {
            "label": label,
            "scale": np_scale,
            "delivery": np_delivery,
            "stage": np_stage,
            "reg_level": np_reg_level,
            "team_knowledge": np_team_knowledge,
            "outsourcing": np_outsourcing,
            "crisis_state": np_crisis,
            "overwork": np_overwork,
        }

        session_id = st.session_state.get("session_uuid")
        assessment_id = st.session_state.get("assessment_id")
        if session_id and st.session_state.get("consent_given", False):
            log_identification(
                session_id=session_id,
                assessment_id=assessment_id,
                id_type="new_persona",
                new_persona=new_persona,
            )

        display_label = label if label.strip() else "(unlabelled)"
        st.success(f"Thanks! New persona **{display_label}** submitted.")
        st.session_state["identification_done"] = True


# ---------------------------------------------------------------------------
# Mode 3: Skip
# ---------------------------------------------------------------------------

elif id_mode == "Prefer not to say":
    if st.button("Skip identification", key="submit_skip"):
        session_id = st.session_state.get("session_uuid")
        assessment_id = st.session_state.get("assessment_id")
        if session_id and st.session_state.get("consent_given", False):
            log_identification(
                session_id=session_id,
                assessment_id=assessment_id,
                id_type="skip",
            )
        st.info("No problem. Thanks for trying the assessment!")
        st.session_state["identification_done"] = True


# ---------------------------------------------------------------------------
# Persona correlation reference
# ---------------------------------------------------------------------------

st.divider()
render_persona_correlation()


# ---------------------------------------------------------------------------
# Feedback section
# ---------------------------------------------------------------------------

st.divider()
st.header("Feedback")
st.caption(
    "Share your thoughts on the model, the results, or the research. "
    "Anonymous by default \u2014 optionally provide a display name if you'd like "
    "to be credited."
)

with st.form("feedback_form"):
    fb_rating = st.select_slider(
        "How well did the model match your experience?",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: {
            1: "1 \u2014 Not at all",
            2: "2 \u2014 Slightly",
            3: "3 \u2014 Somewhat",
            4: "4 \u2014 Closely",
            5: "5 \u2014 Exactly",
        }[x],
    )

    fb_text = st.text_area(
        "Comments (optional, max 2000 characters)",
        max_chars=2000,
        placeholder="What resonated? What felt wrong? Any suggestions?",
        help="No company or project names, please.",
    )

    fb_name = st.text_input(
        "Display name (optional \u2014 leave blank for anonymous)",
        max_chars=100,
        placeholder="e.g. 'Jane, QA Lead' or leave blank",
    )

    fb_submitted = st.form_submit_button("Submit feedback")

if fb_submitted:
    session_id = st.session_state.get("session_uuid")
    assessment_id = st.session_state.get("assessment_id")

    if fb_text.strip() or fb_rating != 3:
        if session_id and st.session_state.get("consent_given", False):
            log_feedback(
                session_id=session_id,
                assessment_id=assessment_id,
                feedback_text=fb_text,
                rating=fb_rating,
                display_name=fb_name if fb_name.strip() else None,
            )
        anonymous_label = "anonymously" if not fb_name.strip() else f"as '{fb_name.strip()}'"
        st.success(f"Thanks for your feedback ({anonymous_label})!")
    else:
        st.info("No feedback to submit \u2014 rating is neutral and no comments entered.")


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("\u2190 Back to Results"):
        st.switch_page("pages/03_results.py")
with col2:
    if st.button("Reassess with different answers \u2192"):
        st.switch_page("pages/02_assessment.py")
