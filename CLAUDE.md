# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Research project** exploring whether there is a derivable "sweet spot" on the Capability vs Operational maturity grid that maximises software project success, parameterised by project type.

**Core hypothesis:** Success is not maximum maturity — it is *right-sized* maturity. Every position on the Cap/Ops grid can succeed, but each carries costs that must be absorbable by the organisation.

**Origin:** Derives from the MIRA platform (question-based QA maturity assessment tool). MIRA uses front-loaded project configuration to bias assessment questions, then scores answers into Capability and Operational maturity breakdowns. The cross-framework mappings (TMMi, DORA, ISO 9001) in MIRA are partitioned away from the maturity calculations — this research focuses on the question model, not the framework mappings.

## Running the Code

All modules run from `src/` directory (required for imports):

```bash
cd src
python dimension_slider_mapping.py   # Calibration results, sensitivity matrix
python viable_zones.py               # Zone analysis, heatmaps for all 15 archetypes
python slider_sensitivity.py         # Q2+Q7: slider impacts and toxic combinations (~30-60s)
python movement_analysis.py          # Q4+Q5+Q8: off-diagonal, transitions, P8 retrodiction
python midrange_analysis.py          # Q6: mid-range investigation
```

Dependencies: `numpy`, `scipy` (for L-BFGS-B optimisation in dimension_slider_mapping only).

## Architecture

### Module Dependency Chain

```
dimension_slider_mapping.py          # Layer 0: dimensions -> sliders
        |
        v
viable_zones.py                      # Layer 1: sliders + dims -> viable zones
        |
        +---> slider_sensitivity.py  # Layer 2a: slider impact analysis
        +---> movement_analysis.py   # Layer 2b: transitions and retrodiction
        +---> midrange_analysis.py   # Layer 2c: mid-range investigation
```

### `src/dimension_slider_mapping.py` — Dimension-to-Slider Mapping

Maps 8 project dimensions to 4 capacity sliders using weighted piecewise transforms. Two-layer architecture:
- **Layer 1**: Structural baseline calibrated via L-BFGS-B with L2 regularisation against 12 MIRA personas (MAE=0.092, LOO-CV MAE=0.142)
- **Layer 2**: State modifiers (phase, crisis, culture, erosion) — domain-derived, not optimised (combined MAE=0.058)

Key exports: `ARCHETYPE_SLIDER_DEFAULTS`, `SLIDER_SHORT`, `DIMENSION_SHORT`, `PHASE_MODIFIERS`, `CRISIS_MODIFIERS`, `EROSION_MODIFIERS`

### `src/viable_zones.py` — Viable Zone Derivation

Sweeps the 101x101 Cap/Ops grid for all 15 archetypes evaluating three sigmoid-based success tests:
1. **Viable** — cap >= cap_floor (buffered by Recovery)
2. **Sufficient** — ops >= ops_floor (buffered by Overwork)
3. **Sustainable** — four cost components (gap, debt, process, execution) below threshold

Key exports: `sweep_grid()`, `ARCHETYPE_DIMENSIONS`, `ARCHETYPE_DEFAULT_POSITIONS`, `ARCHETYPE_ORDER`, `PASS_THRESHOLD`, `test_viable()`, `test_sufficient()`, `test_sustainable()`

### `src/slider_sensitivity.py` — Slider Impact Analysis (Q2 + Q7)

Sweeps each slider 0->1 measuring zone area change. Tests all 6 pairwise interactions using additive independence model. Uses grid cache for performance (~800 sweeps).

Key export: `_cached_zone_area()` (reused by other modules)

### `src/movement_analysis.py` — Movement & Transitions (Q4 + Q5 + Q8)

Three analyses: off-diagonal cost decomposition, archetype transition paths (continuous interpolation), and P8 crisis retrodiction (progressive state modifier application).

### `src/midrange_analysis.py` — Mid-Range Investigation (Q6)

Tests whether mid-range (35-65% Cap/Ops) is a stable state using archetype coverage analysis and synthetic profiles.

## Key Research Findings

All 10 research questions from `docs/SIMULATION_HANDOFF.md` are answered:

- **Viable zones**: 10.1% (#10 Legacy) to 71.5% (#14 Platform/Internal); 4 correct default failures
- **Investment dominates** total impact for 14/15 archetypes; #1 Micro Startup uniquely dominated by Overwork
- **Binding lever != most impactful**: saturated enterprises need Recovery/Overwork, not more Investment
- **Recovery+Time** is the worst toxic pair (6/15 archetypes, up to -12.2% compounding)
- **Off-diagonal key**: Time capacity sustains Cap>Ops, Recovery sustains Ops>Cap
- **P8 crisis retrodiction**: resource erosion on acute crisis is the trigger; Investment=0.80 + D8=3 would have prevented it
- **Mid-range is universally viable** (15/15 archetypes) but naturally unpopulated — safe harbour, not attractor

## Known Model Limitations

### Sliders are instantaneous, not time-dependent
All four capacity sliders (Investment, Recovery, Overwork, Time) are treated as **instantaneous state variables**. Moving Investment from 0.5 to 0.7 takes effect immediately in the model. In reality, resource addition has a lag curve — and sometimes a negative initial effect (Brooks's Law). The model cannot distinguish between:

- Hiring engineers (6-month ramp, possible short-term productivity dip)
- Engaging specialist consultancy (weeks to value)
- Buying a platform licence (days to value)

Contract/external resource is the closest real-world analogue to the model's assumption, since it buys pre-formed capacity rather than growing it.

**Implication**: The model answers "what configuration is viable?" (static equilibrium) but not "how long does it take to get there?" or "what happens during the transition?". A future iteration could address this by making sliders time-dependent with characteristic response curves and overshoot/undershoot dynamics — but that would be a dynamic simulation rather than a static equilibrium model.

## Key Concepts

### The Two-Axis Model
- **Capability axis:** Process maturity, governance, standards — "what you can do"
- **Operational axis:** Delivery performance, execution quality — "what you are doing"

### Four Capacity Sliders
1. **Investment** — can you afford to move on the grid? (dominates sustainability upper bound)
2. **Recovery** — can you survive failures? (buffers viability floor + sustains Ops>Cap)
3. **Overwork** — can the team compensate through effort? (buffers sufficiency floor)
4. **Time** — can you afford to be slow? (sustains Cap>Ops positions)

### 15 Structural Archetypes
Project types defined by structural shape, not industry domain. Each has a dimension profile (D1-D8), default slider values, and a default Cap/Ops position.

### 8 Project Dimensions
D1 Consequence, D2 Market Pressure, D3 Complexity, D4 Regulation, D5 Team Stability, D6 Outsourcing, D7 Lifecycle, D8 Coherence. Scale 1-5 each.

## Reference Documents

| File | Purpose |
|------|---------|
| `docs/SIMULATION_HANDOFF.md` | **Primary reference** — complete research brief with all variables, archetypes, success function, calibration data |
| `docs/mira_persona_definitions.md` | 12 persona narratives with validated outcomes |
| `docs/cross_framework_mapping.yaml` | 15 categories, 35 capabilities — reference only, not used in scoring model |
| `docs/unified_scoring.yaml` | Scoring thresholds, phase weights, context modifiers |
| `docs/adaptive_filtering_rules.yaml` | Progressive disclosure rules |

## Language & Style

- UK English spelling exclusively (visualisation, optimise, colour, etc.)
- Concise, technical communication
- Research project — acknowledge uncertainty, state assumptions explicitly
