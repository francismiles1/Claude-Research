"""
Welcome page — consent, research summary, and call to action.
"""

from __future__ import annotations

import streamlit as st

from lib.supabase_client import generate_session_id


st.header("Right-Sized Maturity for Software Projects")

st.markdown("""
Most maturity models assume more is better — higher capability, higher operational
maturity, maximum everything. **This research challenges that assumption.**

Through simulation of 15 structural project archetypes across 8 dimensions, we find
that **success is not maximum maturity — it is *right-sized* maturity**. Every position
on the Capability vs Operational grid can succeed, but each carries costs that must be
absorbable by the organisation.

The model identifies:
- **Viable zones** — where your project can realistically succeed
- **Cost structures** — what each position actually costs to maintain
- **Binding constraints** — what's actually holding your project back
- **Capacity levers** — which investments move the needle
""")

st.divider()

st.subheader("How It Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**1. Describe Your Project**")
    st.caption(
        "Answer 9 questions about your project's context: scale, delivery model, "
        "regulation, complexity, team stability. Takes about 2 minutes."
    )

with col2:
    st.markdown("**2. See Your Results**")
    st.caption(
        "The model derives your project's structural profile, matches it to the "
        "nearest archetype, and shows where you sit on the viability heatmap."
    )

with col3:
    st.markdown("**3. Identify & Contribute**")
    st.caption(
        "Tell us which persona matches your real-world experience — or define "
        "a new one. Your input helps validate and extend the research."
    )

st.divider()

# Consent
st.subheader("Privacy & Consent")

st.markdown("""
This tool logs **anonymised project configurations** for research purposes.

**What we capture:** Categorical project context (scale, delivery model, etc.),
derived dimension values (1-5), archetype match, and capacity slider positions.
All data is abstract and structural — no company names, no project names, no
personal information.

**What we never capture:** Names, emails, IP addresses, cookies, or any data
that could identify you or your organisation.
""")

consent = st.checkbox(
    "I understand and consent to anonymous data collection for research purposes",
    value=st.session_state.get("consent_given", False),
    key="consent_checkbox",
)

if consent and not st.session_state.get("consent_given", False):
    st.session_state["consent_given"] = True
    st.session_state["session_uuid"] = generate_session_id()

if not consent:
    st.session_state["consent_given"] = False
    st.session_state["session_uuid"] = None

if st.session_state.get("consent_given", False):
    st.success("Consent recorded. Your anonymous session is active.")
    if st.button("Assess Your Project \u2192", type="primary"):
        st.switch_page("pages/02_assessment.py")
else:
    st.info("Please consent above to begin the assessment. The tool still works without consent — data simply won't be logged.")
    if st.button("Continue without logging \u2192"):
        st.switch_page("pages/02_assessment.py")
