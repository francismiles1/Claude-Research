"""
Shared UI components and constants for the Cap/Ops Balance Model.

Extracted from visualisation.py for reuse across multi-page Streamlit app.
All render functions, cached computations, and display constants live here.

Depends on: viable_zones.py, dimension_slider_mapping.py, mira_bridge.py
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
from mira_bridge import (
    bridge_mira_to_simulation,
    PERSONA_CONTEXTS,
    PERSONA_EXPECTED,
)


# ---------------------------------------------------------------------------
# Display constants
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

# Archetype descriptions — what each project type represents
ARCHETYPE_DESCRIPTIONS = {
    "#1 Micro Startup": (
        "1-3 person team, no process, pure hustle. Moving fast with minimal governance. "
        "Success depends almost entirely on individual effort and speed to market."
    ),
    "#2 Small Agile": (
        "Small team (5-15) with lightweight agile practices. Some structure emerging but "
        "still informal. Standups and sprints, but documentation is minimal."
    ),
    "#3 Scaling Startup": (
        "Growing from small to mid-size (15-50+). Processes straining under growth. "
        "What worked at 10 people breaks at 40. Key challenge: adding structure without killing speed."
    ),
    "#4 DevOps Native": (
        "Team built around automation from day one. CI/CD, infrastructure as code, "
        "monitoring. High operational output sustained through tooling rather than formal process."
    ),
    "#5 Component Heroes": (
        "Multiple teams, each owning components, but weak cross-team coordination. "
        "Individual teams perform well; integration and coherence are the pain points."
    ),
    "#6 Matrix Programme": (
        "Large cross-functional programme with matrix reporting. Multiple workstreams, "
        "dependencies, and governance layers. Coordination cost is the dominant challenge."
    ),
    "#7 Outsource-Managed": (
        "Significant outsourced delivery with in-house management. Split accountability, "
        "contract boundaries, and communication overhead define the operating model."
    ),
    "#8 Reg Stage-Gate": (
        "Heavily regulated, formal stage-gate delivery. Compliance-driven governance with "
        "mandatory quality gates, audit trails, and sign-off processes. Slow but controlled."
    ),
    "#9 Ent Balanced": (
        "Mature enterprise with balanced capability and operations. Well-funded, stable teams, "
        "established processes. The 'gold standard' operating model with resources to match."
    ),
    "#10 Legacy Maintenance": (
        "Skeleton crew maintaining ageing systems. Minimal budget, high staff turnover, "
        "no investment in improvement. 'Keep the lights on' mode."
    ),
    "#11 Modernisation": (
        "Legacy system being actively modernised. Investment starting to flow but the team "
        "is still building capability. Transitional state between legacy and modern."
    ),
    "#12 Crisis/Firefight": (
        "Project in active crisis. Process has broken down, team is firefighting, "
        "governance is reactive. Everything is urgent, nothing is planned."
    ),
    "#13 Planning/Pre-Deliv": (
        "Pre-delivery phase — requirements, architecture, planning. High capability "
        "investment but almost zero operational output yet. All preparation, no delivery."
    ),
    "#14 Platform/Internal": (
        "Internal platform or tooling team. Low external stakes, high automation, "
        "well-architected. The team builds for internal users with forgiving requirements."
    ),
    "#15 Regulated Startup": (
        "Startup operating in a regulated industry (fintech, healthtech). Must meet "
        "compliance requirements with startup resources. High ambition, constrained budget."
    ),
}

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
    "Consequence":     {1: "Failure is trivial", 2: "Minor impact", 3: "Moderate impact", 4: "Serious impact", 5: "Catastrophic if it fails"},
    "Market Pressure": {1: "No time pressure", 2: "Relaxed deadlines", 3: "Normal pressure", 4: "Competitive market", 5: "Ship yesterday"},
    "Complexity":      {1: "Simple system", 2: "Low complexity", 3: "Moderately complex", 4: "Highly complex", 5: "Extreme complexity"},
    "Regulation":      {1: "No compliance needed", 2: "Light governance", 3: "Moderate regulation", 4: "Heavily regulated", 5: "Strict regulatory regime"},
    "Team Stability":  {1: "High churn, no retention", 2: "Unstable team", 3: "Some stability", 4: "Stable team", 5: "Very stable, low turnover"},
    "Outsourcing":     {1: "Fully in-house", 2: "Mostly in-house", 3: "Mixed model", 4: "Mostly outsourced", 5: "Fully outsourced"},
    "Lifecycle":       {1: "Brand new / greenfield", 2: "Early stage", 3: "Mid-lifecycle", 4: "Late stage / ageing", 5: "End of life"},
    "Coherence":       {1: "Fragmented, no alignment", 2: "Weak coherence", 3: "Moderate coherence", 4: "Well-aligned", 5: "Fully coherent architecture"},
}

# Dimensions where higher values are BETTER (not more demanding)
INVERTED_DIMS = {"Team Stability", "Coherence"}

# Form field options (shared between assessment page and MIRA import sidebar)
SCALE_OPTIONS = ["small", "medium", "large", "enterprise"]
DELIVERY_OPTIONS = ["agile", "devops", "waterfall", "v_model", "hybrid_agile", "hybrid_traditional"]
STAGE_OPTIONS = ["startup", "growth", "mature", "legacy"]
PHASE_OPTIONS = [
    "initiation", "planning", "early_dev", "mid_dev", "execution",
    "testing_phase", "maturation", "transition", "closure", "maintenance",
]
REGULATORY_OPTIONS = [
    "gdpr", "hipaa", "sox", "pci_dss", "iso_27001", "iso_9001_certified",
    "fda_21_cfr_11", "iso_13485", "iso_26262", "iec_62443", "aspice", "fedramp", "other",
]
AUDIT_OPTIONS = ["none", "annual", "bi_annual", "quarterly", "continuous"]

# Persona descriptions — human-readable explanations for the feedback page.
# Each has a brief context line and a narrative quote from the research definitions.
PERSONA_DESCRIPTIONS = {
    "P1 Startup Chaos": (
        "3–8 person startup, no regulation, shipping through heroics and client proximity. "
        "\"You're delivering through effort, not process. That works until it doesn't.\""
    ),
    "P2 Small Agile Team": (
        "8–15 person team, real agile ceremonies, tribal knowledge instead of documentation. "
        "\"Your team makes this work. Your process doesn't. What happens when the team changes?\""
    ),
    "P3 Government Waterfall": (
        "50–100 person public-sector project, heavy compliance, manual stage-gated delivery. "
        "\"You have the structure. Now you need the speed. Process without agility is just expensive documentation.\""
    ),
    "P4 Enterprise Financial": (
        "200+ person regulated financial platform (SOX, PCI-DSS), mature pipelines, heavy outsourcing. "
        "\"Your machine works, but increasingly it's other people's machines bolted onto yours.\""
    ),
    "P5 Medical Device": (
        "20–50 person safety-critical product (FDA, IEC 62304), slow by design — lives depend on it. "
        "\"Your process exists for a reason — people's lives. The challenge is keeping it sustainable.\""
    ),
    "P6 Failing Automation": (
        "30–60 person growth-stage team, significant automation investment that isn't translating to delivery. "
        "\"You bought the tools before you built the foundations. Your automation is now technical debt wearing a quality hat.\""
    ),
    "P7 Cloud-Native": (
        "15–30 person DevOps team, greenfield product, modern tooling, untested at scale. "
        "\"You've built a perfect island and declared the sea somebody else's problem.\""
    ),
    "P8 Late-Stage UAT Crisis": (
        "80–150+ person project in late delivery, UAT haemorrhaging defects, every gate rubber-stamped. "
        "\"You built what you thought was right, not what the customer asked for.\""
    ),
    "P9 Planning Phase": (
        "20–40 person team starting a new project, nothing built yet — all metrics are blank or baseline. "
        "\"You have the luxury of time and a clean slate. Every decision you make now compounds through the lifecycle.\""
    ),
    "P10 Golden Enterprise": (
        "150–300 person mature company with genuine engineering culture, sustainable pace, quality by conviction. "
        "\"You've built something rare — a quality culture that sustains itself. Guard against the slow drift.\""
    ),
    "P11 Automotive Embedded": (
        "200+ person multi-tier automotive programme (ISO 26262, ASPICE), compliance-driven with deep supplier chains. "
        "\"You've built a compliance fortress around a trust vacuum.\""
    ),
    "P12 Legacy Modernisation": (
        "5–12 person team maintaining a 15-year system, tribal knowledge, retirement risk, forced modernisation. "
        "\"Your system runs on institutional memory, not process. Every retirement letter is a risk event.\""
    ),
}


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


@st.cache_data
def compute_persona_correlation() -> list[dict]:
    """Evaluate all 12 MIRA personas against their matched archetype's viable zone."""
    rows = []
    for name, data in PERSONA_CONTEXTS.items():
        result = bridge_mira_to_simulation(data)
        arch = result["archetype"]
        dims = result["dimensions"]
        sliders = list(ARCHETYPE_SLIDER_DEFAULTS[arch])
        cap = result.get("cap", 0.5)
        ops = result.get("ops", 0.5)

        v = test_viable(cap, ops, dims, sliders)
        s = test_sufficient(cap, ops, dims, sliders)
        u = test_sustainable(cap, ops, dims, sliders)
        combined = min(v, s, u)

        # Identify binding constraint
        scores = {"Viable": v, "Sufficient": s, "Sustainable": u}
        binding = min(scores, key=scores.get)

        rows.append({
            "persona": name,
            "cap": cap,
            "ops": ops,
            "archetype": arch,
            "viable": v,
            "sufficient": s,
            "sustainable": u,
            "combined": combined,
            "passes": combined >= PASS_THRESHOLD,
            "binding": binding if combined < PASS_THRESHOLD else "\u2014",
            "expected": PERSONA_EXPECTED.get(name, []),
            "confidence": result["confidence"],
        })
    return rows


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

    # Floor lines (optional)
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

    # Default position marker (optional)
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

    # Inspected position marker (diamond, only if different from default)
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

    # Layout
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
# Render functions
# ---------------------------------------------------------------------------

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
                   f"{cap_range[0]:.0%}\u2013{cap_range[1]:.0%}")
    cols[2].metric("Ops range",
                   f"{ops_range[0]:.0%}\u2013{ops_range[1]:.0%}")
    cols[3].metric("Cap floor", f"{cap_floor:.0%}")
    cols[4].metric("Ops floor", f"{ops_floor:.0%}")


def render_dimension_chart(dims: list[int]):
    """Horizontal bar chart showing the 8 dimension values (1-5) with descriptions."""
    colours = []
    for label, v in zip(DIMENSION_LABELS, dims):
        inverted = label in INVERTED_DIMS
        if inverted:
            # High = good (green), low = bad (red)
            if v >= 4:
                colours.append("#4CAF50")
            elif v >= 3:
                colours.append("#FFD54F")
            else:
                colours.append("#E57373")
        else:
            # High = demanding (red), low = easy (green)
            if v <= 2:
                colours.append("#4CAF50")
            elif v <= 3:
                colours.append("#FFD54F")
            else:
                colours.append("#E57373")

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

    # Full dimension breakdown in a visible box
    lines = []
    for label, v in zip(DIMENSION_LABELS, dims):
        desc = DIMENSION_DESCRIPTIONS[label].get(v, "")
        inverted = label in INVERTED_DIMS
        if inverted:
            indicator = "\U0001f7e2" if v >= 4 else ("\U0001f7e1" if v >= 3 else "\U0001f534")
        else:
            indicator = "\U0001f7e2" if v <= 2 else ("\U0001f7e1" if v <= 3 else "\U0001f534")
        lines.append(f"{indicator} **{label}** = {v}/5 \u2014 {desc}")
    st.markdown("\n\n".join(lines))


def render_persona_correlation(selected_persona: str | None = None):
    """Display the MIRA persona correlation table."""
    st.markdown("#### MIRA Persona Correlation")
    st.caption(
        "Each persona's MIRA-derived Cap/Ops position evaluated against "
        "the simulation's viable zone for their matched archetype."
    )

    rows = compute_persona_correlation()

    # Build markdown table
    lines = [
        "| Persona | Cap | Ops | Archetype | Viable | Sufficient | Sustainable | Verdict | Binding |",
        "|---------|----:|----:|-----------|-------:|-----------:|------------:|---------|---------|",
    ]
    for r in rows:
        verdict = "VIABLE" if r["passes"] else "FAIL"
        highlight = "**" if r["persona"] == selected_persona else ""
        lines.append(
            f"| {highlight}{r['persona']}{highlight} "
            f"| {r['cap']:.0%} "
            f"| {r['ops']:.0%} "
            f"| {r['archetype']} "
            f"| {r['viable']:.3f} "
            f"| {r['sufficient']:.3f} "
            f"| {r['sustainable']:.3f} "
            f"| {verdict} "
            f"| {r['binding']} |"
        )
    st.markdown("\n".join(lines))

    # Summary stats
    passing = sum(1 for r in rows if r["passes"])
    failing = sum(1 for r in rows if not r["passes"])
    st.markdown(
        f"**{passing} viable, {failing} failing** \u2014 "
        f"failures: {', '.join(r['persona'] for r in rows if not r['passes'])}"
    )

    # Narrative for failures
    for r in rows:
        if not r["passes"]:
            cap_pct = f"{r['cap']:.0%}"
            ops_pct = f"{r['ops']:.0%}"
            if r["binding"] == "Viable":
                reason = f"Cap at {cap_pct} is below the viability floor \u2014 insufficient process capability."
            elif r["binding"] == "Sufficient":
                reason = f"Ops at {ops_pct} is below the sufficiency floor \u2014 not enough delivery output."
            else:
                reason = f"Position ({cap_pct}/{ops_pct}) exceeds sustainable cost threshold."
            st.caption(f"**{r['persona']}**: {reason}")


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

    # Detailed cost explanations with real-world context
    # Gap cost
    if bd["gap"] < 0.02:
        gap_text = "Cap and Ops are balanced \u2014 no mismatch penalty."
    elif bd["gap_direction"] == "Cap > Ops":
        gap_text = (
            f"**Cap > Ops by {bd['gap']:.0%}** \u2014 you have more governance/process "
            f"than delivery output. In practice: review cycles with little to review, "
            f"compliance checkpoints with few deliverables passing through, quality gates "
            f"that slow work but aren't justified by throughput. "
            f"**{bd['gap_compensator']}** ({bd['gap_compensator_value']:.2f}) absorbs "
            f"{'most' if bd['gap_cost'] < 0.05 else 'some'} of this \u2014 "
        )
        if bd["gap_cost"] < 0.05:
            gap_text += "the organisation can afford to be slow and thorough."
        else:
            gap_text += "but not enough. Need more **Time** (schedule slack) to justify heavy process with low output."
    else:
        gap_text = (
            f"**Ops > Cap by {bd['gap']:.0%}** \u2014 you're delivering beyond what your "
            f"processes support. In practice: shipping without adequate testing, deploying "
            f"without proper review, making commitments governance can't back up. "
            f"**{bd['gap_compensator']}** ({bd['gap_compensator_value']:.2f}) absorbs "
            f"{'most' if bd['gap_cost'] < 0.05 else 'some'} of this \u2014 "
        )
        if bd["gap_cost"] < 0.05:
            gap_text += "automation/effort compensates for the process gap."
        else:
            gap_text += "but not enough. Need more **Recovery** (automation) or **Overwork** to sustain delivery without process."

    # Debt cost
    avg = (bd["cap"] + bd["ops"]) / 2
    if bd["debt_cost"] < 0.01:
        debt_text = "Maturity high enough \u2014 no compounding debt."
    else:
        debt_text = (
            f"Average maturity ({avg:.0%}) is below 30%. Technical debt, knowledge gaps, "
            f"and undocumented decisions are accumulating faster than they're resolved."
        )

    # Process cost
    if bd["process_cost"] < 0.03:
        proc_text = f"Low capability ({bd['cap']:.0%}) means minimal governance overhead."
    else:
        proc_text = (
            f"Maintaining Cap={bd['cap']:.0%} costs {bd['process_cost']:.3f}. "
            f"This covers: documentation standards, quality gates, review processes, "
            f"compliance evidence, training. "
        )
        if bd["process_cost"] > 0.10:
            proc_text += "This is significant \u2014 **increase Investment** to reduce the burden."

    # Execution cost
    if bd["execution_cost"] < 0.03:
        exec_text = f"Low operations ({bd['ops']:.0%}) means minimal delivery overhead."
    else:
        exec_text = (
            f"Sustaining Ops={bd['ops']:.0%} costs {bd['execution_cost']:.3f}. "
            f"This covers: delivery cadence, deployment pipelines, incident response, "
            f"monitoring, release management. "
            f"Best compensator: **{bd['exec_compensator']}** ({bd['exec_compensator_value']:.2f}). "
        )
        if bd["execution_cost"] > 0.10:
            exec_text += f"Consider increasing **{bd['exec_compensator']}** to reduce this."

    st.caption(f"**Gap**: {gap_text}")
    st.caption(f"**Debt**: {debt_text}")
    st.caption(f"**Process**: {proc_text}")
    st.caption(f"**Execution**: {exec_text}")
    st.caption(
        f"Net: {bd['net_cost']:.3f} vs threshold {bd['threshold']:.2f} "
        f"(relief: -{bd['investment_relief']:.3f})"
    )
