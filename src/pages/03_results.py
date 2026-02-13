"""
Results page — interactive heatmap, cost breakdown, and dimension chart.

Refactored from the original visualisation.py. Uses shared components
from lib/components.py for all rendering.
"""

from __future__ import annotations

import numpy as np
import streamlit as st

from viable_zones import (
    cost_breakdown,
    ARCHETYPE_DEFAULT_POSITIONS,
    ARCHETYPE_ORDER,
    compute_cap_floor,
    compute_ops_floor,
)
from dimension_slider_mapping import (
    ARCHETYPE_SLIDER_DEFAULTS,
    SLIDER_SHORT,
)
from lib.components import (
    LAYER_MAP,
    GRADIENT_MODE,
    ARCHETYPE_DESCRIPTIONS,
    compute_grid,
    compute_gradient_grid,
    compute_zone_metrics,
    compute_scores,
    build_heatmap_figure,
    render_score_panel,
    render_zone_metrics,
    render_dimension_chart,
    render_cost_breakdown,
    render_persona_correlation,
)


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
# Extract state
# ---------------------------------------------------------------------------

archetype = bridge_result["archetype"]
dims = bridge_result["dimensions"]
default_pos = ARCHETYPE_DEFAULT_POSITIONS[archetype]
default_sliders = st.session_state.get("default_sliders", list(ARCHETYPE_SLIDER_DEFAULTS[archetype]))


# ---------------------------------------------------------------------------
# Sidebar: capacity sliders + view options
# ---------------------------------------------------------------------------

st.sidebar.subheader("Capacity Sliders")
st.sidebar.caption(
    "Adjust to explore how resourcing decisions change the viable zone."
)

# Initialise current sliders if not set
if "current_sliders" not in st.session_state:
    st.session_state["current_sliders"] = list(default_sliders)

inv = st.sidebar.slider("Investment", 0.0, 1.0,
                         value=st.session_state["current_sliders"][0],
                         step=0.05, format="%.2f", key="slider_inv")
rec = st.sidebar.slider("Recovery", 0.0, 1.0,
                         value=st.session_state["current_sliders"][1],
                         step=0.05, format="%.2f", key="slider_rec")
owk = st.sidebar.slider("Overwork", 0.0, 1.0,
                         value=st.session_state["current_sliders"][2],
                         step=0.05, format="%.2f", key="slider_owk")
tim = st.sidebar.slider("Time", 0.0, 1.0,
                         value=st.session_state["current_sliders"][3],
                         step=0.05, format="%.2f", key="slider_time")
sliders = [inv, rec, owk, tim]
st.session_state["current_sliders"] = sliders

# Slider delta from defaults
deltas = [s - d for s, d in zip(sliders, default_sliders)]
if any(abs(d) > 0.001 for d in deltas):
    delta_parts = []
    for i, d in enumerate(deltas):
        if abs(d) > 0.001:
            sign = "+" if d > 0 else ""
            delta_parts.append(f"{SLIDER_SHORT[i]} {sign}{d:.2f}")
    st.sidebar.caption(f"Delta from defaults: {', '.join(delta_parts)}")

# Reset button
def _reset_sliders():
    st.session_state["current_sliders"] = list(default_sliders)
    st.session_state["slider_inv"] = default_sliders[0]
    st.session_state["slider_rec"] = default_sliders[1]
    st.session_state["slider_owk"] = default_sliders[2]
    st.session_state["slider_time"] = default_sliders[3]

st.sidebar.button("Reset sliders to defaults", on_click=_reset_sliders)

st.sidebar.divider()
st.sidebar.subheader("View Options")

layer_options = [GRADIENT_MODE] + list(LAYER_MAP.keys())
layer = st.sidebar.radio(
    "Display layer",
    layer_options,
    key="view_layer",
    horizontal=True,
    help="Gradient shows smooth margins (default). "
         "Others show binary pass/fail for individual tests.",
)

st.sidebar.divider()
show_floors = st.sidebar.checkbox("Show floor lines", value=False,
                                   help="Cap floor (min viable capability) and Ops floor (min sufficient operations)")
show_default = st.sidebar.checkbox("Show default position", value=False,
                                    help="The archetype's typical real-world Cap/Ops position")


# ---------------------------------------------------------------------------
# Compute grids (cached)
# ---------------------------------------------------------------------------

dims_tuple = tuple(dims)
sliders_tuple = tuple(round(s, 4) for s in sliders)
grid = compute_grid(dims_tuple, sliders_tuple)
gradient_grid = compute_gradient_grid(dims_tuple, sliders_tuple)

is_gradient = (layer == GRADIENT_MODE)

# Zone metrics
zone_area, cap_range, ops_range = compute_zone_metrics(grid)
cap_floor = compute_cap_floor(dims)
ops_floor = compute_ops_floor(dims)


# ---------------------------------------------------------------------------
# Header and archetype description
# ---------------------------------------------------------------------------

st.header(f"{archetype} \u2014 Viable Zone: {zone_area:.1f}%")

# Match confidence indicator
confidence = bridge_result["confidence"]
conf_icon = {"strong": "\U0001f7e2", "reasonable": "\U0001f7e1", "ambiguous": "\U0001f534"}
st.markdown(
    f"{conf_icon.get(confidence, '\u26aa')} **Match confidence: {confidence}** "
    f"(distance: {bridge_result['match_distance']:.1f})"
)

# Alternatives
alts = bridge_result.get("alternatives", [])
if len(alts) > 1:
    alt_text = " | ".join(f"{a} ({d:.1f})" for a, d in alts[1:])
    st.caption(f"Alternatives: {alt_text}")

st.info(ARCHETYPE_DESCRIPTIONS.get(archetype, ""), icon="\U0001f4cb")


# ---------------------------------------------------------------------------
# Side-by-side layout: heatmap left, inspect+breakdown right
# ---------------------------------------------------------------------------

col_map, col_detail = st.columns([3, 2])

with col_detail:
    # Inspect position controls
    st.markdown("#### Inspect Position")
    ctrl1, ctrl2 = st.columns(2)
    with ctrl1:
        inspect_cap = st.number_input(
            "Cap %", min_value=0.0, max_value=1.0, step=0.01,
            key="inspect_cap", format="%.2f",
        )
    with ctrl2:
        inspect_ops = st.number_input(
            "Ops %", min_value=0.0, max_value=1.0, step=0.01,
            key="inspect_ops", format="%.2f",
        )

    # Sweet spot finder
    def _find_sweet_spot():
        combined_margin = gradient_grid[:, :, 3]
        best_idx = np.unravel_index(np.argmax(combined_margin),
                                     combined_margin.shape)
        steps = np.linspace(0.0, 1.0, gradient_grid.shape[0])
        st.session_state["inspect_cap"] = round(float(steps[best_idx[1]]), 2)
        st.session_state["inspect_ops"] = round(float(steps[best_idx[0]]), 2)

    st.button("Find sweet spot", on_click=_find_sweet_spot,
              help="Jump to the position with the highest combined margin")

    inspect_pos = (inspect_cap, inspect_ops)

    # Compute scores and cost breakdown
    scores = compute_scores(
        inspect_pos[0], inspect_pos[1], dims_tuple, sliders_tuple
    )
    bd = cost_breakdown(inspect_pos[0], inspect_pos[1], dims, sliders)

    st.markdown(
        f"**Cap={inspect_pos[0]:.0%}, Ops={inspect_pos[1]:.0%}**"
        f" \u2014 Margin: {scores['margin']:+.2f}"
    )
    render_score_panel(scores)
    st.divider()
    render_cost_breakdown(bd)

with col_map:
    # Build heatmap
    layer_idx = LAYER_MAP.get(layer, 3)
    fig = build_heatmap_figure(
        grid, dims, layer_idx, layer,
        default_pos, inspect_pos,
        gradient_grid=gradient_grid,
        is_gradient=is_gradient,
        show_floors=show_floors,
        show_default=show_default,
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    render_zone_metrics(zone_area, cap_range, ops_range, cap_floor, ops_floor)
    st.caption("**Project Dimensions** \u2014 what makes this project type demanding")
    render_dimension_chart(dims)


# ---------------------------------------------------------------------------
# Persona correlation table
# ---------------------------------------------------------------------------

st.divider()
render_persona_correlation()


# ---------------------------------------------------------------------------
# Call to action
# ---------------------------------------------------------------------------

st.divider()
st.markdown("#### Does this match your experience?")
st.caption(
    "Help validate the research by telling us which persona matches your "
    "real-world project \u2014 or define a new one."
)
if st.button("Identify Your Project \u2192", type="primary"):
    st.switch_page("pages/04_identify.py")
