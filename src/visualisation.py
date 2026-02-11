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
    sweep_grid_gradient,
    raw_margins,
    cost_breakdown,
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

# Gradient mode uses a separate grid (raw margins), not an index into the sigmoid grid
GRADIENT_MODE = "Gradient"

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

# Gradient colourscale: diverging around 0 (the viable boundary)
# Clipped to [-4, +4] range for display
GRADIENT_COLOURSCALE = [
    [0.000, "#8B0000"],   # -4: deep failure
    [0.125, "#CD5C5C"],   # -3: significant failure
    [0.250, "#E88060"],   # -2: moderate failure
    [0.375, "#F0C0A0"],   # -1: marginal failure
    [0.500, "#FFFFCC"],   # 0: boundary (viable threshold)
    [0.625, "#C0E8A0"],   # +1: marginally viable
    [0.750, "#4CAF50"],   # +2: solid
    [0.875, "#2E7D32"],   # +3: strong
    [1.000, "#1B5E20"],   # +4: deep sweet spot
]
GRADIENT_CLIP = 4.0  # Clip raw margins to [-4, +4] for display


# ---------------------------------------------------------------------------
# Cached computation
# ---------------------------------------------------------------------------

@st.cache_data
def compute_grid(dims_tuple: tuple, sliders_tuple: tuple) -> np.ndarray:
    """Compute the 101x101 grid, cached by (dims, sliders)."""
    return sweep_grid(list(dims_tuple), list(sliders_tuple))


@st.cache_data
def compute_gradient_grid(dims_tuple: tuple, sliders_tuple: tuple) -> np.ndarray:
    """Compute the 101x101 raw margin grid, cached by (dims, sliders)."""
    return sweep_grid_gradient(list(dims_tuple), list(sliders_tuple))


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
    vm, sm, um = raw_margins(cap, ops, dims, sliders)
    return {
        "viable": v,
        "sufficient": s,
        "sustainable": u,
        "combined": min(v, s, u),
        "margin": min(vm, sm, um),
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
    gradient_grid: np.ndarray | None = None,
    is_gradient: bool = False,
    show_floors: bool = False,
    show_default: bool = False,
) -> go.Figure:
    """Build the Plotly heatmap with contour, floor lines, and markers."""
    cap_vals = np.linspace(0, 100, grid.shape[1])
    ops_vals = np.linspace(0, 100, grid.shape[0])

    fig = go.Figure()

    if is_gradient and gradient_grid is not None:
        # Gradient mode: show raw margins with smooth colour gradient
        data = np.clip(gradient_grid[:, :, layer_idx], -GRADIENT_CLIP, GRADIENT_CLIP)
        # Normalise to [0, 1] for the colourscale (0 = -CLIP, 0.5 = 0, 1 = +CLIP)
        display_data = (data + GRADIENT_CLIP) / (2 * GRADIENT_CLIP)

        # Customdata: raw margin values for hover
        customdata = np.stack([
            gradient_grid[:, :, 0],
            gradient_grid[:, :, 1],
            gradient_grid[:, :, 2],
            gradient_grid[:, :, 3],
        ], axis=-1)

        fig.add_trace(go.Heatmap(
            z=display_data,
            x=cap_vals,
            y=ops_vals,
            customdata=customdata,
            colorscale=GRADIENT_COLOURSCALE,
            zmin=0.0,
            zmax=1.0,
            colorbar=dict(
                title=dict(text="Margin"),
                tickvals=[0.0, 0.25, 0.5, 0.75, 1.0],
                ticktext=[f"{-GRADIENT_CLIP:.0f}", f"{-GRADIENT_CLIP/2:.0f}",
                          "0", f"+{GRADIENT_CLIP/2:.0f}", f"+{GRADIENT_CLIP:.0f}"],
                len=0.75,
            ),
            hovertemplate=(
                "Cap: %{x:.0f}%<br>"
                "Ops: %{y:.0f}%<br>"
                "---<br>"
                "Viable margin: %{customdata[0]:+.2f}<br>"
                "Sufficient margin: %{customdata[1]:+.2f}<br>"
                "Sustainable margin: %{customdata[2]:+.2f}<br>"
                "Combined margin: %{customdata[3]:+.2f}<br>"
                "---<br>"
                "0 = viable boundary, +ve = inside, -ve = outside"
                "<extra></extra>"
            ),
        ))
    else:
        # Standard sigmoid mode
        data = grid[:, :, layer_idx]

        customdata = np.stack([
            grid[:, :, 0],
            grid[:, :, 1],
            grid[:, :, 2],
            grid[:, :, 3],
        ], axis=-1)

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

    # Viable zone contour at 0.5 (always from sigmoid grid)
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

    # 3. Floor lines (optional)
    if show_floors:
        cap_floor_pct = compute_cap_floor(dims) * 100
        ops_floor_pct = compute_ops_floor(dims) * 100
        fig.add_vline(
            x=cap_floor_pct,
            line_dash="dot",
            line_color="rgba(255,255,255,0.6)",
            annotation_text=f"Cap floor {cap_floor_pct:.0f}%",
            annotation_font_color="white",
            annotation_bgcolor="rgba(0,0,0,0.4)",
        )
        fig.add_hline(
            y=ops_floor_pct,
            line_dash="dot",
            line_color="rgba(255,255,255,0.6)",
            annotation_text=f"Ops floor {ops_floor_pct:.0f}%",
            annotation_font_color="white",
            annotation_bgcolor="rgba(0,0,0,0.4)",
        )

    # 4. Default position marker (optional)
    if show_default:
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

    return archetype, dims, sliders, layer, default_pos, show_floors, show_default


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


# Full dimension labels for the profile chart
DIMENSION_LABELS = [
    "Consequence",
    "Market Pressure",
    "Complexity",
    "Regulation",
    "Team Stability",
    "Outsourcing",
    "Lifecycle",
    "Coherence",
]

# What each value means at low (1) and high (5)
DIMENSION_DESCRIPTIONS = {
    "Consequence":    {1: "Failure is trivial", 2: "Minor impact", 3: "Moderate impact", 4: "Serious impact", 5: "Catastrophic if it fails"},
    "Market Pressure":{1: "No time pressure", 2: "Relaxed deadlines", 3: "Normal pressure", 4: "Competitive market", 5: "Ship yesterday"},
    "Complexity":     {1: "Simple system", 2: "Low complexity", 3: "Moderately complex", 4: "Highly complex", 5: "Extreme complexity"},
    "Regulation":     {1: "No compliance needed", 2: "Light governance", 3: "Moderate regulation", 4: "Heavily regulated", 5: "Strict regulatory regime"},
    "Team Stability": {1: "High churn, no retention", 2: "Unstable team", 3: "Some stability", 4: "Stable team", 5: "Very stable, low turnover"},
    "Outsourcing":    {1: "Fully in-house", 2: "Mostly in-house", 3: "Mixed model", 4: "Mostly outsourced", 5: "Fully outsourced"},
    "Lifecycle":      {1: "Brand new / greenfield", 2: "Early stage", 3: "Mid-lifecycle", 4: "Late stage / ageing", 5: "End of life"},
    "Coherence":      {1: "Fragmented, no alignment", 2: "Weak coherence", 3: "Moderate coherence", 4: "Well-aligned", 5: "Fully coherent architecture"},
}


def render_dimension_chart(dims: list[int]):
    """Horizontal bar chart showing the 8 dimension values (1-5) with descriptions."""
    colours = []
    for v in dims:
        if v <= 2:
            colours.append("#4CAF50")   # Low = green (less demanding)
        elif v <= 3:
            colours.append("#FFD54F")   # Medium = amber
        else:
            colours.append("#E57373")   # High = red (more demanding)

    # Build hover text with descriptions
    hover_texts = []
    for label, v in zip(DIMENSION_LABELS, dims):
        desc = DIMENSION_DESCRIPTIONS[label].get(v, "")
        hover_texts.append(f"{label}: {v}/5<br>{desc}")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=DIMENSION_LABELS,
        x=dims,
        orientation="h",
        marker_color=colours,
        text=[str(v) for v in dims],
        textposition="auto",
        textfont=dict(size=13, color="white"),
        hovertext=hover_texts,
        hoverinfo="text",
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 5.5], dtick=1, title="Value (1-5)"),
        yaxis=dict(autorange="reversed"),
        height=250,
        margin=dict(l=110, r=10, t=5, b=30),
        plot_bgcolor="#1a1a1a",
        paper_bgcolor="#0e1117",
        font_color="white",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Compact text summary of key dimensions
    highlights = []
    for label, v in zip(DIMENSION_LABELS, dims):
        desc = DIMENSION_DESCRIPTIONS[label].get(v, "")
        if v <= 2 or v >= 4:  # Only show notable values
            highlights.append(f"**{label}** ({v}): {desc}")
    if highlights:
        st.caption(" | ".join(highlights))


def render_cost_breakdown(bd: dict):
    """Display the full cost decomposition for the inspected position."""
    st.markdown("#### Cost Breakdown")

    # Summary verdict
    if bd["sustainable"]:
        st.success(
            f"Sustainable (headroom: +{bd['headroom']:.3f}). "
            f"Dominant cost: **{bd['dominant_cost']}** ({bd['dominant_value']:.3f})"
        )
    else:
        st.error(
            f"Unsustainable (over threshold by {-bd['headroom']:.3f}). "
            f"Dominant cost: **{bd['dominant_cost']}** ({bd['dominant_value']:.3f})"
        )

    # Cost bar chart
    cost_names = ["Gap cost", "Debt cost", "Process cost", "Execution cost"]
    cost_values = [bd["gap_cost"], bd["debt_cost"],
                   bd["process_cost"], bd["execution_cost"]]

    fig = go.Figure()
    colours = ["#E57373" if v > 0.05 else "#A5D6A7" for v in cost_values]
    fig.add_trace(go.Bar(
        x=cost_names,
        y=cost_values,
        marker_color=colours,
        text=[f"{v:.3f}" for v in cost_values],
        textposition="auto",
    ))

    # Threshold line
    fig.add_hline(
        y=bd["threshold"],
        line_dash="dash",
        line_color="white",
        annotation_text=f"Threshold ({bd['threshold']:.2f})",
        annotation_font_color="white",
    )

    # Net cost line
    fig.add_hline(
        y=bd["net_cost"],
        line_dash="solid",
        line_color="#FFD54F",
        annotation_text=f"Net cost ({bd['net_cost']:.3f})",
        annotation_font_color="#FFD54F",
        annotation_position="bottom right",
    )

    fig.update_layout(
        yaxis_title="Cost",
        height=220,
        margin=dict(l=40, r=20, t=20, b=40),
        plot_bgcolor="#1a1a1a",
        paper_bgcolor="#0e1117",
        font_color="white",
        yaxis=dict(range=[0, max(0.5, max(cost_values) * 1.2)]),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Compact cost explanations
    gap_text = ""
    if bd["gap"] < 0.02:
        gap_text = "Balanced — no gap penalty."
    else:
        gap_text = f"{bd['gap_direction']} ({bd['gap']:.0%} gap)"
        if bd["gap_cost"] > 0.05:
            if bd["gap_direction"] == "Cap > Ops":
                gap_text += " — need more **Time** to absorb"
            else:
                gap_text += " — need more **Recovery/Overwork** to sustain"

    debt_text = "No debt." if bd["debt_cost"] < 0.01 else f"Avg maturity {(bd['cap']+bd['ops'])/2:.0%} < 30% — debt accumulating"
    proc_text = f"Cap={bd['cap']:.0%} maintenance: {bd['process_cost']:.3f}"
    if bd["process_cost"] > 0.10:
        proc_text += " — **increase Investment**"
    exec_text = f"Ops={bd['ops']:.0%} overhead: {bd['execution_cost']:.3f}"
    if bd["execution_cost"] > 0.10:
        exec_text += f" — best lever: **{bd['exec_compensator']}**"

    st.caption(f"**Gap**: {gap_text}")
    st.caption(f"**Debt**: {debt_text}")
    st.caption(f"**Process**: {proc_text}")
    st.caption(f"**Execution**: {exec_text}")
    st.caption(
        f"Net: {bd['net_cost']:.3f} vs threshold {bd['threshold']:.2f} "
        f"(relief: -{bd['investment_relief']:.3f})"
    )


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
    (archetype, dims, sliders, layer, default_pos,
     show_floors, show_default) = render_sidebar()

    # Compute grids (cached)
    dims_tuple = tuple(dims)
    sliders_tuple = tuple(round(s, 4) for s in sliders)
    grid = compute_grid(dims_tuple, sliders_tuple)

    # Compute gradient grid (needed for sweet spot finder and gradient view)
    gradient_grid = compute_gradient_grid(dims_tuple, sliders_tuple)

    is_gradient = (layer == GRADIENT_MODE)

    # Zone metrics
    zone_area, cap_range, ops_range = compute_zone_metrics(grid)
    cap_floor = compute_cap_floor(dims)
    ops_floor = compute_ops_floor(dims)

    # Header
    st.header(f"{archetype} — Viable Zone: {zone_area:.1f}%")

    # Side-by-side layout: heatmap left, inspect+breakdown right
    col_map, col_detail = st.columns([3, 2])

    with col_detail:
        # Inspect position controls — prominent, at the top
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

        # Sweet spot finder button
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

        # Compute scores and cost breakdown at inspected position
        scores = compute_scores(
            inspect_pos[0], inspect_pos[1], dims_tuple, sliders_tuple
        )
        bd = cost_breakdown(inspect_pos[0], inspect_pos[1], dims, sliders)

        st.markdown(
            f"**Cap={inspect_pos[0]:.0%}, Ops={inspect_pos[1]:.0%}**"
            f" — Margin: {scores['margin']:+.2f}"
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
        st.caption("**Project Dimensions** — what makes this project type demanding")
        render_dimension_chart(dims)


if __name__ == "__main__":
    main()
