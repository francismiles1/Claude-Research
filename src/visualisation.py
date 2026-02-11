"""
Interactive Viable Zone Explorer — Streamlit application.

Provides a browser-based interface for exploring the Cap/Ops balance
model. Users can select archetypes, adjust capacity sliders, and
watch the viable zone heatmap update in real-time.

Run from the src/ directory:
    streamlit run visualisation.py

Depends on: viable_zones.py, dimension_slider_mapping.py
"""

from __future__ import annotations

import numpy as np
import streamlit as st
import plotly.graph_objects as go

from viable_zones import (
    sweep_grid,
    test_viable,
    test_sufficient,
    test_sustainable,
    ARCHETYPE_DIMENSIONS,
    ARCHETYPE_DEFAULT_POSITIONS,
    ARCHETYPE_ORDER,
    PASS_THRESHOLD,
    compute_cap_floor,
    compute_ops_floor,
)
from dimension_slider_mapping import (
    ARCHETYPE_SLIDER_DEFAULTS,
    SLIDER_SHORT,
    DIMENSION_SHORT,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LAYER_MAP = {
    "Combined": 3,
    "Viable": 0,
    "Sufficient": 1,
    "Sustainable": 2,
}

# Custom diverging colourscale: red (fail) -> pale yellow (threshold) -> green (pass)
ZONE_COLOURSCALE = [
    [0.00, "#8B0000"],   # Dark red — deep failure
    [0.25, "#CD5C5C"],   # Indian red — moderate failure
    [0.45, "#F0C0A0"],   # Peach — approaching threshold
    [0.50, "#FFFFCC"],   # Pale yellow — threshold boundary
    [0.55, "#C0E8A0"],   # Light green — just passing
    [0.75, "#4CAF50"],   # Medium green — solid pass
    [1.00, "#1B5E20"],   # Dark green — strong pass
]


# ---------------------------------------------------------------------------
# Cached computation
# ---------------------------------------------------------------------------

@st.cache_data
def compute_grid(dims_tuple: tuple, sliders_tuple: tuple) -> np.ndarray:
    """Compute the 101x101 grid, cached by (dims, sliders)."""
    return sweep_grid(list(dims_tuple), list(sliders_tuple))


def compute_zone_metrics(grid: np.ndarray):
    """Derive zone area and cap/ops ranges from a grid."""
    combined = grid[:, :, 3]
    viable_mask = combined >= PASS_THRESHOLD
    zone_area_pct = float(np.mean(viable_mask)) * 100.0

    steps = np.linspace(0.0, 1.0, grid.shape[0])

    if np.any(viable_mask):
        coords = np.argwhere(viable_mask)
        cap_range = (float(steps[coords[:, 1].min()]),
                     float(steps[coords[:, 1].max()]))
        ops_range = (float(steps[coords[:, 0].min()]),
                     float(steps[coords[:, 0].max()]))
    else:
        cap_range = (0.0, 0.0)
        ops_range = (0.0, 0.0)

    return zone_area_pct, cap_range, ops_range


@st.cache_data
def compute_scores(cap: float, ops: float,
                   dims_tuple: tuple, sliders_tuple: tuple) -> dict:
    """Evaluate the three tests at a specific position."""
    dims = list(dims_tuple)
    sliders = list(sliders_tuple)
    v = test_viable(cap, ops, dims, sliders)
    s = test_sufficient(cap, ops, dims, sliders)
    u = test_sustainable(cap, ops, dims, sliders)
    return {
        "viable": v,
        "sufficient": s,
        "sustainable": u,
        "combined": min(v, s, u),
    }


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def _sync_archetype_change():
    """Reset sliders and inspect position when archetype changes."""
    current = st.session_state.get("archetype", ARCHETYPE_ORDER[0])
    previous = st.session_state.get("prev_archetype", None)

    if current != previous:
        defaults = ARCHETYPE_SLIDER_DEFAULTS[current]
        st.session_state["slider_inv"] = defaults[0]
        st.session_state["slider_rec"] = defaults[1]
        st.session_state["slider_owk"] = defaults[2]
        st.session_state["slider_time"] = defaults[3]

        cap, ops = ARCHETYPE_DEFAULT_POSITIONS[current]
        st.session_state["inspect_cap"] = cap
        st.session_state["inspect_ops"] = ops
        st.session_state["prev_archetype"] = current


# ---------------------------------------------------------------------------
# Figure builder
# ---------------------------------------------------------------------------

def build_heatmap_figure(
    grid: np.ndarray,
    dims: list[int],
    layer_idx: int,
    layer_name: str,
    default_pos: tuple[float, float],
    inspect_pos: tuple[float, float],
) -> go.Figure:
    """Build the Plotly heatmap with contour, floor lines, and markers."""
    data = grid[:, :, layer_idx]
    cap_vals = np.linspace(0, 100, grid.shape[1])
    ops_vals = np.linspace(0, 100, grid.shape[0])

    # Customdata: all 4 scores per cell for hover
    customdata = np.stack([
        grid[:, :, 0],
        grid[:, :, 1],
        grid[:, :, 2],
        grid[:, :, 3],
    ], axis=-1)

    fig = go.Figure()

    # 1. Heatmap
    fig.add_trace(go.Heatmap(
        z=data,
        x=cap_vals,
        y=ops_vals,
        customdata=customdata,
        colorscale=ZONE_COLOURSCALE,
        zmin=0.0,
        zmax=1.0,
        colorbar=dict(
            title=dict(text=f"{layer_name} Score"),
            tickformat=".2f",
            len=0.75,
        ),
        hovertemplate=(
            "Cap: %{x:.0f}%<br>"
            "Ops: %{y:.0f}%<br>"
            "---<br>"
            "Viable: %{customdata[0]:.3f}<br>"
            "Sufficient: %{customdata[1]:.3f}<br>"
            "Sustainable: %{customdata[2]:.3f}<br>"
            "Combined: %{customdata[3]:.3f}"
            "<extra></extra>"
        ),
    ))

    # 2. Viable zone contour at 0.5 (always on combined layer)
    combined = grid[:, :, 3]
    fig.add_trace(go.Contour(
        z=combined,
        x=cap_vals,
        y=ops_vals,
        contours=dict(start=0.5, end=0.5, size=0.1, coloring="none"),
        line=dict(color="white", width=2, dash="dash"),
        showscale=False,
        hoverinfo="skip",
        name="Viable boundary",
    ))

    # 3. Floor lines
    cap_floor = compute_cap_floor(dims) * 100
    ops_floor = compute_ops_floor(dims) * 100
    fig.add_vline(
        x=cap_floor,
        line_dash="dot",
        line_color="rgba(255,255,255,0.6)",
        annotation_text=f"Cap floor {cap_floor:.0f}%",
        annotation_font_color="white",
        annotation_bgcolor="rgba(0,0,0,0.4)",
    )
    fig.add_hline(
        y=ops_floor,
        line_dash="dot",
        line_color="rgba(255,255,255,0.6)",
        annotation_text=f"Ops floor {ops_floor:.0f}%",
        annotation_font_color="white",
        annotation_bgcolor="rgba(0,0,0,0.4)",
    )

    # 4. Default position marker (star)
    fig.add_trace(go.Scatter(
        x=[default_pos[0] * 100],
        y=[default_pos[1] * 100],
        mode="markers+text",
        marker=dict(symbol="star", size=16, color="white",
                    line=dict(color="black", width=1.5)),
        text=["Default"],
        textposition="top center",
        textfont=dict(color="white", size=11),
        name="Default position",
        hovertemplate=(
            "Default: Cap %{x:.0f}%, Ops %{y:.0f}%<extra></extra>"
        ),
    ))

    # 5. Inspected position marker (diamond, only if different)
    insp_cap_pct = inspect_pos[0] * 100
    insp_ops_pct = inspect_pos[1] * 100
    def_cap_pct = default_pos[0] * 100
    def_ops_pct = default_pos[1] * 100

    if abs(insp_cap_pct - def_cap_pct) > 0.5 or abs(insp_ops_pct - def_ops_pct) > 0.5:
        fig.add_trace(go.Scatter(
            x=[insp_cap_pct],
            y=[insp_ops_pct],
            mode="markers+text",
            marker=dict(symbol="diamond", size=14, color="white",
                        line=dict(color="black", width=1.5)),
            text=["Inspect"],
            textposition="top center",
            textfont=dict(color="white", size=11),
            name="Inspected position",
            hovertemplate=(
                "Inspect: Cap %{x:.0f}%, Ops %{y:.0f}%<extra></extra>"
            ),
        ))

    # 6. Layout
    fig.update_layout(
        xaxis_title="Capability Maturity (%)",
        yaxis_title="Operational Maturity (%)",
        xaxis=dict(range=[0, 100], dtick=10, constrain="domain"),
        yaxis=dict(range=[0, 100], dtick=10, constrain="domain",
                   scaleanchor="x", scaleratio=1),
        height=650,
        margin=dict(l=60, r=20, t=40, b=60),
        legend=dict(
            yanchor="top", y=0.99, xanchor="left", x=0.01,
            bgcolor="rgba(0,0,0,0.5)",
            font=dict(color="white"),
        ),
        plot_bgcolor="#1a1a1a",
    )

    return fig


# ---------------------------------------------------------------------------
# UI components
# ---------------------------------------------------------------------------

def render_sidebar():
    """Render all sidebar controls. Returns current parameters."""
    st.sidebar.title("Viable Zone Explorer")
    st.sidebar.caption(
        "Cap/Ops balance model for software project success. "
        "Adjust sliders to see the viable zone change in real-time."
    )

    # Archetype selector
    archetype = st.sidebar.selectbox(
        "Project archetype",
        options=ARCHETYPE_ORDER,
        key="archetype",
        on_change=_sync_archetype_change,
    )

    dims = ARCHETYPE_DIMENSIONS[archetype]
    default_pos = ARCHETYPE_DEFAULT_POSITIONS[archetype]

    # Dimension profile (read-only)
    st.sidebar.caption("Dimension profile")
    dim_text = "  ".join(
        f"**{DIMENSION_SHORT[i]}**:{dims[i]}" for i in range(8)
    )
    st.sidebar.markdown(dim_text)

    st.sidebar.divider()
    st.sidebar.subheader("Capacity Sliders")

    inv = st.sidebar.slider("Investment", 0.0, 1.0,
                            key="slider_inv", step=0.05,
                            format="%.2f")
    rec = st.sidebar.slider("Recovery", 0.0, 1.0,
                            key="slider_rec", step=0.05,
                            format="%.2f")
    owk = st.sidebar.slider("Overwork", 0.0, 1.0,
                            key="slider_owk", step=0.05,
                            format="%.2f")
    tim = st.sidebar.slider("Time", 0.0, 1.0,
                            key="slider_time", step=0.05,
                            format="%.2f")
    sliders = [inv, rec, owk, tim]

    # Slider delta from defaults
    defaults = ARCHETYPE_SLIDER_DEFAULTS[archetype]
    deltas = [s - d for s, d in zip(sliders, defaults)]
    if any(abs(d) > 0.001 for d in deltas):
        delta_parts = []
        for i, d in enumerate(deltas):
            if abs(d) > 0.001:
                sign = "+" if d > 0 else ""
                delta_parts.append(f"{SLIDER_SHORT[i]} {sign}{d:.2f}")
        st.sidebar.caption(f"Delta from defaults: {', '.join(delta_parts)}")

    # Reset button — uses callback so state is set before widgets render
    def _reset_sliders():
        defs = ARCHETYPE_SLIDER_DEFAULTS[st.session_state["archetype"]]
        st.session_state["slider_inv"] = defs[0]
        st.session_state["slider_rec"] = defs[1]
        st.session_state["slider_owk"] = defs[2]
        st.session_state["slider_time"] = defs[3]

    st.sidebar.button("Reset sliders to defaults", on_click=_reset_sliders)

    st.sidebar.divider()
    st.sidebar.subheader("View Options")

    layer = st.sidebar.radio(
        "Display layer",
        list(LAYER_MAP.keys()),
        key="view_layer",
        horizontal=True,
    )

    st.sidebar.divider()
    st.sidebar.subheader("Inspect Position")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        inspect_cap = st.number_input(
            "Cap", min_value=0.0, max_value=1.0, step=0.01,
            key="inspect_cap", format="%.2f",
        )
    with col2:
        inspect_ops = st.number_input(
            "Ops", min_value=0.0, max_value=1.0, step=0.01,
            key="inspect_ops", format="%.2f",
        )

    return archetype, dims, sliders, layer, (inspect_cap, inspect_ops), default_pos


def render_score_panel(scores: dict):
    """Display test scores in a four-column layout with pass/fail indicators."""
    cols = st.columns(4)
    tests = [
        ("Viable", scores["viable"]),
        ("Sufficient", scores["sufficient"]),
        ("Sustainable", scores["sustainable"]),
        ("Combined", scores["combined"]),
    ]

    for col, (name, score) in zip(cols, tests):
        passes = score >= PASS_THRESHOLD
        status = "PASS" if passes else "FAIL"
        col.metric(
            label=name,
            value=f"{score:.3f}",
            delta=status,
            delta_color="normal" if passes else "inverse",
        )


def render_zone_metrics(zone_area: float,
                        cap_range: tuple[float, float],
                        ops_range: tuple[float, float],
                        cap_floor: float,
                        ops_floor: float):
    """Display zone area and boundary metrics."""
    cols = st.columns(5)
    cols[0].metric("Zone area", f"{zone_area:.1f}%")
    cols[1].metric("Cap range",
                   f"{cap_range[0]:.0%}–{cap_range[1]:.0%}")
    cols[2].metric("Ops range",
                   f"{ops_range[0]:.0%}–{ops_range[1]:.0%}")
    cols[3].metric("Cap floor", f"{cap_floor:.0%}")
    cols[4].metric("Ops floor", f"{ops_floor:.0%}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="Viable Zone Explorer",
        layout="wide",
    )

    # Initialise session state on first run
    if "prev_archetype" not in st.session_state:
        first = ARCHETYPE_ORDER[0]
        defaults = ARCHETYPE_SLIDER_DEFAULTS[first]
        cap, ops = ARCHETYPE_DEFAULT_POSITIONS[first]
        st.session_state["prev_archetype"] = first
        st.session_state["slider_inv"] = defaults[0]
        st.session_state["slider_rec"] = defaults[1]
        st.session_state["slider_owk"] = defaults[2]
        st.session_state["slider_time"] = defaults[3]
        st.session_state["inspect_cap"] = cap
        st.session_state["inspect_ops"] = ops

    # Render sidebar and collect parameters
    archetype, dims, sliders, layer, inspect_pos, default_pos = render_sidebar()

    # Compute grid (cached)
    dims_tuple = tuple(dims)
    sliders_tuple = tuple(round(s, 4) for s in sliders)
    grid = compute_grid(dims_tuple, sliders_tuple)

    # Zone metrics
    zone_area, cap_range, ops_range = compute_zone_metrics(grid)
    cap_floor = compute_cap_floor(dims)
    ops_floor = compute_ops_floor(dims)

    # Header
    st.header(f"{archetype} — Viable Zone: {zone_area:.1f}%")

    # Build and display heatmap
    layer_idx = LAYER_MAP[layer]
    fig = build_heatmap_figure(
        grid, dims, layer_idx, layer,
        default_pos, inspect_pos,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Score readout at inspected position
    st.subheader(
        f"Scores at Cap={inspect_pos[0]:.0%}, Ops={inspect_pos[1]:.0%}"
    )
    scores = compute_scores(
        inspect_pos[0], inspect_pos[1], dims_tuple, sliders_tuple
    )
    render_score_panel(scores)

    # Zone boundary metrics
    st.divider()
    render_zone_metrics(zone_area, cap_range, ops_range, cap_floor, ops_floor)


if __name__ == "__main__":
    main()
