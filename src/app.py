"""
Cap/Ops Balance Model — Public Research Platform

Multi-page Streamlit application for exploring whether there is a derivable
"sweet spot" on the Capability vs Operational maturity grid that maximises
software project success, parameterised by project type.

Run from the src/ directory:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st


# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Cap/Ops Balance — Right-Sized Maturity",
    page_icon="\u2696\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "consent_given" not in st.session_state:
    st.session_state["consent_given"] = False

if "session_uuid" not in st.session_state:
    st.session_state["session_uuid"] = None

if "bridge_result" not in st.session_state:
    st.session_state["bridge_result"] = None

if "assessment_context" not in st.session_state:
    st.session_state["assessment_context"] = None

if "assessment_id" not in st.session_state:
    st.session_state["assessment_id"] = None


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

welcome_page = st.Page("pages/01_welcome.py", title="Welcome", icon="\U0001f3e0", default=True)
assessment_page = st.Page("pages/02_assessment.py", title="Assess Your Project", icon="\U0001f4cb")
results_page = st.Page("pages/03_results.py", title="Results", icon="\U0001f4ca")
identify_page = st.Page("pages/04_identify.py", title="Identify", icon="\U0001f464")

nav = st.navigation(
    {
        "Research": [welcome_page],
        "Assessment": [assessment_page, results_page],
        "Community": [identify_page],
    }
)


# ---------------------------------------------------------------------------
# Shared sidebar branding
# ---------------------------------------------------------------------------

st.sidebar.markdown("### Cap/Ops Balance Model")
st.sidebar.caption(
    "Exploring right-sized maturity for software projects. "
    "No personal data is captured."
)
st.sidebar.divider()


# ---------------------------------------------------------------------------
# Run the selected page
# ---------------------------------------------------------------------------

nav.run()
