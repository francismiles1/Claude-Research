# CLAUDE.md — Cap/Ops Balance Simulation Research

## Project Overview

**Research project** exploring whether there is a derivable "sweet spot" on the Capability vs Operational maturity grid that maximises software project success, parameterised by project type.

**Core hypothesis:** Success is not maximum maturity — it is *right-sized* maturity. Every position on the Cap/Ops grid can succeed, but each carries costs that must be absorbable by the organisation. Success is a three-part test: viable (stakes covered), sustainable (team/org can maintain it), sufficient (delivers what stakeholders need).

**Origin:** This research derives from the MIRA platform (QA maturity assessment tool combining TMMi, DORA, and ISO 9001). MIRA separates maturity into two independent axes — Capability (what you *can* do) and Operational (what you *are* doing) — and this project asks: for each project type, where *should* the balance sit?

## Key Documents

All reference material is in `docs/`:

| File | Purpose |
|------|---------|
| `docs/SIMULATION_HANDOFF.md` | **Primary reference** — complete research brief with all variables, archetypes, success function, prior art, calibration data. Start here. |
| `docs/mira_persona_definitions.md` | 12 detailed persona narratives with expected KPI patterns and quadrant positions |
| `docs/cross_framework_mapping.yaml` | MIRA's 15 categories, 35 capabilities, and cross-framework practice mappings |
| `docs/unified_scoring.yaml` | Scoring thresholds, risk levels, phase weights, context modifiers |
| `docs/adaptive_filtering_rules.yaml` | Progressive disclosure rules that gate operational questions behind capability thresholds |

## Key Concepts

### The Two-Axis Model
- **Capability axis:** Process maturity, governance, standards, knowledge codification — "what you can do"
- **Operational axis:** Delivery performance, execution quality, actual outcomes — "what you are doing"
- These are **independent axes**, not a single dimension. TMMi is capability-biased; DORA is operational-biased. Nobody has formally separated them before.

### The Three-Part Success Test
1. **Viable** — does your grid position cover your stakes? (Two layers: defect consequence + project failure consequence)
2. **Sustainable** — can you maintain this position without destroying the team?
3. **Sufficient** — does this position deliver enough for stakeholders?

### The Four Capacity Sliders
These determine which grid positions are accessible and which failure modes are most likely:
1. **Investment capacity** — can you afford to move on the grid?
2. **Recovery capacity** — can you survive if your position bites you?
3. **Overwork capacity** — can the team compensate through effort?
4. **Time capacity** — can you afford to be slow?

### 15 Structural Archetypes
Project types defined by structural shape (team size, delivery model, process weight, outsourcing level), not industry domain. Medical device / automotive / defence / government are the same archetype (#8 Regulated Stage-Gate) — the domain affects slider values, not the structure.

### 8 Project Dimensions
1. Consequence of failure (inconvenience → life-critical)
2. Rate of change / market pressure (deliberate → ship-or-die)
3. System complexity / scale (simple → deeply interconnected)
4. Regulatory burden (none → existential)
5. Team stability / knowledge codification (tribal → institutionalised)
6. Outsourcing dependency (in-house → fully outsourced)
7. Product lifecycle stage (greenfield → end-of-life)
8. Organisational coherence (fragmented → unified)

## Language & Style
- UK English spelling exclusively (visualisation, optimise, colour, etc.)
- Concise, technical communication
- This is a research project — acknowledge uncertainty, state assumptions explicitly, distinguish between derived conclusions and working hypotheses

## Research Approach
- This is exploratory research, not production code
- Favour clarity of model over implementation elegance
- Document assumptions and their sensitivity — if an assumption changes, what breaks?
- Cross-reference against the 12 MIRA personas as calibration data (all 12 have validated outcomes)
- The MIRA source project is at `C:\Projects\qa-strategy-tool` if deeper reference is needed
