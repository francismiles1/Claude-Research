# Optimal Cap/Ops Balance Simulation — Handoff Document

## Research Objective

**Core question:** For each software project archetype, is there a derivable "sweet spot" on the Capability vs Operational maturity grid that maximises project success?

**Hypothesis:** Success is not maximum maturity — it is *right-sized* maturity. A startup doesn't need TMMi L5. A medical device doesn't need daily deployments. The optimal Cap/Ops balance is a function of 8 measurable project dimensions, and success is defined as fit between actual and target maturity profiles.

**Novel contribution:** This combines contingency theory (project context determines approach), maturity modelling (TMMi/CMMI/DORA levels), and a two-axis model (capability vs operational) that has never been formally assembled. Prior work treats maturity as a single dimension and assumes higher is always better.

---

## Prior Art & Framework Landscape

### Maturity Models — and Their Biases

Every major maturity framework has an implicit bias toward either capability or operational measurement. None separates them as independent axes.

**CMMI (SEI, 1986→2023)** — The original capability maturity model. 5 levels, 22 process areas (v2.0). Defines maturity by *process institutionalisation* — do you have defined, managed, measured processes? This is overwhelmingly **capability-biased**. A CMMI L3 organisation has documented processes; whether those processes produce good software is a separate question the model doesn't directly answer. CMMI v3.0 (2023) added performance-oriented process areas but the DNA remains capability-first.
- *Gap:* Assumes higher = better. No "right-sized" concept. Single dimension.

**TMMi (TMMI Foundation, 2008→present)** — Test-specific maturity model, 5 levels, modelled on CMMI's structure. Levels defined by test process areas: Test Policy (L2), Test Organisation (L3), Test Measurement (L4), Defect Prevention (L5). Assessment criteria overwhelmingly ask "do you have this process defined?" — making TMMi **heavily capability-biased**. Operational outcomes (defect escape rates, test effectiveness) appear implicitly at L4+ but the climb from L1-L3 is almost purely about establishing and documenting test processes. An organisation can achieve TMMi L3 with comprehensive documentation and terrible delivery.
- *Gap:* Capability-focused assessment. No operational counterweight. Assumes L5 is universally desirable.
- *Source:* [TMMi Model](https://www.tmmi.org/tmmi-model/), [TMMi in Financial Domain (2024)](https://www.sciencepublishinggroup.com/article/10.11648/j.ajcst.20240702.13)

**DORA / Accelerate (Forsgren, Humble, Kim, 2014→present)** — Four key metrics: deployment frequency, lead time for changes, change failure rate, mean time to restore. These are all **outcome/operational measures** — how effectively are you shipping and recovering? DORA also identifies ~30 "capabilities" that drive those metrics (trunk-based development, test automation, loosely coupled architecture), but the headline metrics and the classification system (low/medium/high/elite performers) are operational. However, DORA is **DevOps-specific** — continuous delivery focused. A V-model government programme, an automotive ASPICE project, or a medical device validation lifecycle doesn't map well to DORA's worldview. Deployment frequency is meaningless when your release cycle is a vehicle programme milestone.
- *Gap:* Operational focus without capability axis. DevOps-specific — excludes traditional, safety-critical, and hardware-adjacent delivery. No project-type contingency.
- *Source:* [DORA Metrics Guide](https://dora.dev/guides/dora-metrics/), [Octopus DORA Report Summary](https://octopus.com/devops/metrics/dora-metrics/)

**ISO/IEC 33001 (ex-SPICE/ISO 15504)** — Generic process assessment framework. Process capability on a 0-5 scale. ASPICE (automotive) and other domain-specific models derive from it. More flexible than CMMI but still **process/capability-focused** — measures process institutionalisation, not outcomes. The framework allows domain-specific process models, which is a strength, but it provides no guidance on what level is *appropriate* for a given context.
- *Gap:* Process capability only. No outcome axis. No guidance on target levels per project type.
- *Source:* [ISO/IEC 15504 — Wikipedia](https://en.wikipedia.org/wiki/ISO/IEC_15504)

**ISO 25010:2023 (SQuaRE)** — Not a maturity model but a **product quality model** defining 8 quality characteristics: functional suitability, performance efficiency, compatibility, usability, reliability, security, maintainability, and portability. Testability is a sub-characteristic of maintainability. This defines *what* quality means for software, not how mature your process is. Important because it provides the quality target that maturity should serve — and different project types weight these characteristics differently.
- *Gap:* Defines quality targets, not maturity. No process assessment. No Cap/Ops distinction.
- *Source:* [ISO 25010 Exploration (Codacy)](https://blog.codacy.com/iso-25010-software-quality-model), [arc42 Quality Model](https://quality.arc42.org/standards/iso-25010)

### Project Classification Frameworks

**Shenhar & Dvir Diamond Model (2007)** — Classifies projects on 4 dimensions: **Novelty** (derivative → breakthrough), **Technology** (low-tech → super-high-tech), **Complexity** (assembly → array → system), **Pace** (regular → blitz). Purpose: select management style per project type. This is the closest precursor to our dimension-based approach — they recognised that project characteristics should determine management approach. Maps closely to our dimensions 2 (market pressure ≈ pace), 3 (complexity), and 7 (lifecycle stage ≈ novelty). Recent research has asked whether the model needs upgrading, with proposals to split pace into pace + impact.
- *Gap:* Drives methodology selection, not maturity targets. No capability/operational separation. No "optimal profile" derivation. Doesn't address organisational factors (outsourcing, coherence, team stability).
- *Source:* [Diamond Framework (ResearchGate)](https://www.researchgate.net/figure/Diamond-NTCP-model-Source-Shenhar-Dvir-2007_fig1_283435284), [Revisiting the Diamond Model (Springer, 2021)](https://link.springer.com/chapter/10.1007/978-3-030-86248-0_11)

**Boehm & Turner (2004) — *Balancing Agility and Discipline*** — Proposed 5 dimensions (size, criticality, dynamism, personnel, culture) to determine where a project sits on an agility-vs-discipline spectrum. Risk-based approach: identify which end of the spectrum your risks cluster on, then balance accordingly. Influential but limited — it's a **single-axis model** (agile ↔ plan-driven), not a two-axis model. Doesn't separate capability from operational, and doesn't derive target maturity profiles.
- *Gap:* One-dimensional spectrum. No Cap/Ops separation. No quantitative target derivation.
- *Source:* [Balancing Agility and Discipline (ResearchGate)](https://www.researchgate.net/publication/221553462_Balancing_Agility_and_Discipline_Evaluating_and_Integrating_Agile_and_Plan-Driven_Methods)

**Contingency Theory in PM (PMI, various)** — A body of research arguing "no one-size-fits-all" — project characteristics should determine methodology. A contingency fit model identified 37 critical success factors across organisational, team, and customer categories. The theory is sound but stops at methodology selection (waterfall vs agile vs hybrid). Nobody has extended it to derive optimal *maturity profiles* across multiple capability dimensions.
- *Gap:* Drives methodology selection, not maturity targets. No two-axis model.
- *Source:* [PMI Contingency Model](https://www.pmi.org/learning/library/establishing-contingency-approach-model-projects-7115), [Contingency Fit Model for CSFs](https://www.researchgate.net/publication/273301902_A_contingency_fit_model_of_critical_success_factors_for_software_development_projects_A_comparison_of_agile_and_traditional_plan-based_methodologies)

### Organisational & Cultural Models

**Westrum Organisational Culture (1988, adopted by DORA)** — Three typologies: **pathological** (power-oriented, information hoarded), **bureaucratic** (rule-oriented, departments protect turf), **generative** (performance-oriented, information flows freely). Originally developed to predict safety outcomes in aviation and healthcare. DORA's research demonstrated that generative culture predicts software delivery performance. This maps directly to our **Dimension 8 (Organisational Coherence)** — a fragmented/siloed organisation is Westrum-bureaucratic or pathological; a unified one is generative.
- *Gap:* Culture typology, not maturity model. Descriptive not prescriptive. Doesn't connect to specific process or outcome targets.
- *Source:* [IT Revolution — Westrum's Model](https://itrevolution.com/articles/westrums-organizational-model-in-tech-orgs/), [DORA — Generative Culture Capability](https://dora.dev/capabilities/generative-organizational-culture/)

**Conway's Law (1967, formalised by Team Topologies 2019)** — "Organisations design systems that mirror their communication structure." When teams are fragmented, integration seams become failure points. Team Topologies formalised this into actionable patterns (stream-aligned, platform, enabling, complicated-subsystem teams). Directly relevant to Dimension 8 — low organisational coherence produces integration hell not because the technology is hard, but because the organisation is structured to prevent system-level thinking.

### Defining Project Success

**The Iron Triangle (traditional)** — Success = on time + on budget + on scope. Dominated PM thinking for decades. Widely criticised as insufficient — a project can hit all three and still deliver the wrong thing, destroy the team, or fail to generate business value.

**Standish CHAOS Reports (1994→2020)** — The most cited source on IT project success/failure rates. Evolved their success definition significantly: from Iron Triangle (pre-2015) to "on time, on budget, with satisfactory results" (2015) to "good place, good team, good sponsor" (2020). The final edition acknowledged the industry was moving beyond project-based thinking entirely. Their finding that user involvement was the single most important success factor (19 "success points") is relevant — it's an organisational coherence signal.
- *Source:* [CHAOS Report Overview](https://thestory.is/en/journal/chaos-report/), [CHAOS Success Factors (ResearchGate)](https://www.researchgate.net/figure/CHAOS-Report-Success-Factors-by-Rank_tbl1_265009079)

**Beyond the Iron Triangle (APM, PMI, various)** — Growing body of work arguing success should include: stakeholder satisfaction, business value delivered, team sustainability, adaptability to change, and long-term organisational benefit. The Agile Triangle (Jim Highsmith) replaced scope/time/cost with value/quality/constraints. This aligns with our success function — "right-sized maturity" is essentially arguing that the *process investment* should be proportional to the *value at risk*, not maximised for its own sake.
- *Source:* [PMI — Beyond the Iron Triangle](https://www.pmi.org/learning/library/beyond-iron-triangle-year-zero-6381), [APM — Redefining Success](https://www.apm.org.uk/blog/redefining-success-in-project-management/)

### Summary: The Gap

| Aspect | Existing Work | What's Missing |
|--------|--------------|----------------|
| **Maturity measurement** | CMMI, TMMi, SPICE — well-established | All treat maturity as a single dimension. All assume higher = better. |
| **Capability vs Operational** | TMMi (cap-biased), DORA (ops-biased) | Nobody has formally separated them as independent axes or asked where the balance should sit. |
| **Project classification** | Shenhar & Dvir Diamond, Boehm & Turner | Drive methodology selection, not maturity targets. Don't address organisational factors. |
| **Organisational factors** | Westrum culture, Conway's Law, Team Topologies | Descriptive models. Not connected to specific maturity or outcome targets. |
| **Success definition** | Iron Triangle → stakeholder value → CHAOS factors | Evolved beyond time/cost/scope but nobody has formalised success as "fit between actual and target maturity profile." |
| **Right-sized maturity** | Practitioner intuition ("a startup doesn't need L5") | No formal model. No derivation from project characteristics. No quantification of over/under-investment. |

**What's new here:** Contingency theory applied to maturity profiling, on two independent axes (capability and operational), with success defined as fit rather than maximisation, derived from 8 measurable project dimensions. The pieces exist separately — Boehm's project characterisation, Shenhar's diamond, CMMI's levels, DORA's metrics, Westrum's culture types — but nobody has assembled them into a model that says "for *this* project type, *this* is the target maturity profile, and deviation in either direction is waste or risk."

---

## The Two-Axis Model

MIRA separates maturity into two independent axes:

| Axis | What It Measures | Example |
|------|-----------------|---------|
| **Capability** | What the org/team *can* do — process maturity, governance, standards, knowledge codification | "We have a documented test strategy, quality gates, and traceability" |
| **Operational** | What the org/team *is* doing — delivery performance, execution quality, actual outcomes | "Our defect escape rate is 2%, builds pass 95% of the time" |

### The 2×2 Quadrant Model

|  | High Operational | Low Operational |
|---|---|---|
| **High Capability** | **Balanced High** — Predictable & Assured | **Cap > Ops** — Inefficient Success |
| **Low Capability** | **Ops > Cap** — Hidden Risk | **Balanced Low** — Chaotic Delivery |

Plus a **Mid-range** classification for moderate scores without strong divergence.

### Classification Thresholds

```
high_threshold: 60%     — "High" when score >= 60%
low_threshold:  50%     — "Low" when score < 50%
balanced_gap:   15%     — "Balanced" when |cap - ops| <= 15%
divergence_gap: 20%     — "Divergent" when |cap - ops| > 20%
```

### Gap Severity Bands

```
large:    |gap| > 25%
moderate: |gap| 10-25%
small:    |gap| 0-10% (aligned)
```

---

## The 8 Dimensions

These are the project characteristics that determine where the optimal Cap/Ops balance sits. Each is independently measurable and collectively they define the "project type" more precisely than labels like "fintech" or "startup."

### Dimension 1: Consequence of Failure

**What:** The severity of impact when things go wrong.
**Scale:** inconvenience → financial → reputational → regulatory → life-critical
**Effect on sweet spot:** Higher consequence → higher Cap floor (non-negotiable). You cannot under-invest in process when failures kill people or trigger regulatory action.

| Level | Description | Example |
|-------|------------|---------|
| 1 — Inconvenience | Users mildly annoyed, quick fix | Internal tool, hobby project |
| 2 — Financial | Money lost, refunds needed | E-commerce, billing system |
| 3 — Reputational | Brand damage, customer trust eroded | Public-facing platform, SaaS |
| 4 — Regulatory | Fines, legal action, licence revocation | Financial services (PCI-DSS, SOX), GDPR |
| 5 — Life-critical | Physical harm or death possible | Medical devices (FDA), automotive (ISO 26262), aviation |

### Dimension 2: Rate of Change / Market Pressure

**What:** How fast must you ship to survive or compete?
**Scale:** deliberate → measured → competitive → urgent → ship-or-die
**Effect on sweet spot:** Higher pressure → higher Ops floor. You must be executing effectively even if process is lean.

| Level | Description | Example |
|-------|------------|---------|
| 1 — Deliberate | Multi-year timelines, no market urgency | Government, infrastructure |
| 2 — Measured | Quarterly releases, planned roadmap | Enterprise SaaS, banking |
| 3 — Competitive | Monthly releases, market-responsive | Growth-stage product |
| 4 — Urgent | Weekly/daily, fast-follow competitors | Consumer tech, startup scaling |
| 5 — Ship-or-die | Runway burning, pivot-or-perish | Early startup, MVP validation |

### Dimension 3: System Complexity / Scale

**What:** How many moving parts? How interconnected?
**Scale:** simple → modular → integrated → complex → deeply interconnected
**Effect on sweet spot:** Higher complexity → both floors rise. Need Cap to manage complexity, need Ops to test interactions.

| Level | Description | Example |
|-------|------------|---------|
| 1 — Simple | Single service, few dependencies | Internal tool, microsite |
| 2 — Modular | Multiple services, well-bounded | Clean microservices, mobile app |
| 3 — Integrated | Cross-service workflows, shared data | Platform with billing + auth + reporting |
| 4 — Complex | Many teams, external integrations, legacy | Enterprise ERP, multi-vendor platform |
| 5 — Deeply interconnected | Hardware + software + multi-tier supply chain | Automotive ECU, medical device ecosystem |

### Dimension 4: Regulatory Burden

**What:** External mandate for process, documentation, and compliance.
**Scale:** none → light → moderate → heavy → existential
**Effect on sweet spot:** Higher regulation → higher Cap floor. But can push *over*-investment in Cap if regulation drives compliance-theatre rather than genuine maturity.

| Level | Description | Example |
|-------|------------|---------|
| 1 — None | No external compliance requirements | Startup, internal tool |
| 2 — Light | Basic data protection (GDPR basics) | Most B2B SaaS |
| 3 — Moderate | Industry standards (ISO 9001, ISO 27001) | Enterprise products |
| 4 — Heavy | Sector-specific regulation (SOX, PCI-DSS, FCA) | Financial services, healthcare IT |
| 5 — Existential | Multiple safety/security standards, audit-driven | Medical devices (FDA + IEC 62304), automotive (ISO 26262 + ASPICE) |

**MIRA context modifiers for regulatory:**
```yaml
none: 1.0, gdpr: 1.2, hipaa: 1.5, pci_dss: 1.5, sox: 1.4,
fda_21_cfr_11: 1.6, iso_13485: 1.5, iso_27001: 1.3,
iso_9001_certified: 1.2, fedramp: 1.5, iec_62443: 1.5
```

### Dimension 5: Team Stability / Knowledge Codification

**What:** Is knowledge in people's heads or in documented process? How stable is the team?
**Scale:** tribal (fragile) → informal → semi-documented → codified → institutionalised
**Effect on sweet spot:** Low stability → higher Cap needed (process must survive personnel changes). High stability allows leaner Cap.

| Level | Description | Example |
|-------|------------|---------|
| 1 — Tribal | "Ask Dave" — knowledge exists only in individuals | Legacy team, startup |
| 2 — Informal | Shared conventions, not written down | Small agile team |
| 3 — Semi-documented | Key processes documented, gaps remain | Growing company |
| 4 — Codified | Comprehensive documentation, onboarding works | Mature enterprise |
| 5 — Institutionalised | Process embedded in tooling, culture, and hiring | DevOps-native, safety-critical |

### Dimension 6: Outsourcing Dependency

**What:** How much work crosses organisational boundaries?
**Scale:** in-house → selective outsource → significant outsource → heavily outsourced → fully outsourced
**Effect on sweet spot:** Higher outsourcing → need Cap at boundaries (contracts, interface specs, integration governance) + Ops at integration points.

| Level | Description | Example |
|-------|------------|---------|
| 1 — In-house | All development and testing internal | Small team, startup |
| 2 — Selective | Specialist tasks outsourced (perf testing, security audit) | Growing company |
| 3 — Significant | Components or modules outsourced | Enterprise with vendor teams |
| 4 — Heavily outsourced | Most development outsourced, managed by contract | Government, large enterprise |
| 5 — Fully outsourced | All delivery external, internal team = oversight only | Some financial services, government |

### Dimension 7: Product Lifecycle Stage

**What:** Where is the product in its life journey?
**Scale:** greenfield → growth → mature → legacy → end-of-life
**Effect on sweet spot:** Shifts the optimal balance over time. Greenfield favours Ops (learn fast), mature favours balance, legacy demands Cap (codify before knowledge walks out).

| Level | Description | Example |
|-------|------------|---------|
| 1 — Greenfield | New product, clean slate, no legacy | Startup MVP, innovation arm |
| 2 — Growth | Product-market fit found, scaling | Scale-up, expanding features |
| 3 — Mature | Stable, well-established, optimisation focus | Enterprise platform, regulated product |
| 4 — Legacy | Ageing technology, key-person risk, modernisation pressure | Mainframe systems, 15-year-old codebases |
| 5 — End-of-life | Being replaced or decommissioned | Migration source, sunset product |

**Implicit sub-dimensions (derived, not directly input):**
- **Overwork/Sustainability:** startup=maximum, growth=high, mature=low, legacy=low (with spikes). Affects risk narrative.
- **Organisational Alignment Risk:** bell curve peaking at growth stage (empire-building, technical hijacking). Low at startup (survival) and mature (governed).

### Dimension 8: Organisational Coherence

**What:** The degree to which people, teams, and structure are aligned to *this product's* success as a whole.
**Scale:** fragmented → siloed → coordinated → aligned → unified
**Effect on sweet spot:** Low coherence → need higher Cap (integration governance, interface contracts) + higher Ops (integration testing, cross-team transparency). This is Conway's Law as a risk dimension.

| Level | Description | Example |
|-------|------------|---------|
| 1 — Fragmented | Borrowed staff, split allegiance, no system-level ownership | Matrix org, temporary project team |
| 2 — Siloed | Dedicated teams but component-focused, hero mentality | Multi-team programme, micro-service fiefdoms |
| 3 — Coordinated | Integration points acknowledged, some cross-team governance | Growing org with tech leads |
| 4 — Aligned | Shared goals, system-level thinking, transparency | Product-oriented org, strong programme management |
| 5 — Unified | Single team or culturally integrated teams, whole-product mindset | Small team, mature DevOps culture |

**Symptoms of low coherence:**
- Component-level pride without system-level ownership
- "My service is green, integration is someone else's problem"
- Interface governance absent or toothless
- Delivery transparency theatre
- Integration hell at system assembly

---

## MIRA's Assessment Model

### 15 Categories

Each category contains 2-6 capabilities. Categories are the primary unit of scoring.

| # | Category ID | Category Name | Capabilities |
|---|-------------|--------------|-------------|
| 1 | governance | Governance & Leadership | test_policy_strategy, test_monitoring, quality_gates, test_organisation, continuous_improvement, governance_authority |
| 2 | test_strategy | Test Strategy & Design | risk_based_testing, test_planning, nonfunctional_testing |
| 3 | test_assets | Test Assets & Automation | test_automation, automation_diagnostics |
| 4 | development | Development Practices | code_review, coding_standards, unit_testing, static_analysis, build_automation |
| 5 | environment | Environments & Infrastructure | test_environment, cicd_pipeline |
| 6 | requirements | Requirements & Traceability | requirements_traceability |
| 7 | change_management | Change & Release Management | change_control, deployment_safety |
| 8 | feedback | Feedback & Defect Management | defect_management, defect_prevention |
| 9 | ops_readiness | Operational Readiness | incident_management, observability |
| 10 | third_party | Third Party & Suppliers | supplier_quality, supplier_quality_deep_dive |
| 11 | test_phase_progress | Test Phase Progress | phase_execution, phase_governance |
| 12 | architecture | Architecture & Testability | testability_design, legacy_management, architectural_complexity |
| 13 | life_safety | Life Safety Compliance | life_safety_compliance |
| 14 | automotive_safety | Automotive Safety Compliance | automotive_compliance |
| 15 | enterprise_scale | Enterprise Scale | enterprise_operations |

### 35 Capabilities

Each capability maps across TMMi, DORA, ISO 9001, and project risk frameworks. Each has a `dimension` classification (capability or operational) and cross-framework practice references with confidence weights.

| # | Capability ID | Name | Category | Primary Dimension |
|---|--------------|------|----------|------------------|
| 1 | test_policy_strategy | Test Policy & Strategy | governance | capability |
| 2 | risk_based_testing | Risk-Based Test Approach | test_strategy | capability + operational |
| 3 | test_planning | Test Planning & Estimation | test_strategy | capability + operational |
| 4 | test_monitoring | Test Monitoring & Control | governance | operational |
| 5 | defect_management | Defect Tracking & Management | feedback | capability + operational |
| 6 | test_environment | Test Environment Management | environment | operational + capability |
| 7 | test_automation | Test Automation Strategy & Implementation | test_assets | capability + operational |
| 8 | code_review | Code Review Process | development | capability + operational |
| 9 | coding_standards | Coding Standards | development | capability |
| 10 | unit_testing | Unit Testing Practice | development | capability + operational |
| 11 | static_analysis | Static Analysis | development | capability |
| 12 | build_automation | Build Automation & Success | development | operational |
| 13 | cicd_pipeline | CI/CD Pipeline Maturity | environment | capability + operational |
| 14 | requirements_traceability | Requirements Traceability | requirements | capability + operational |
| 15 | deployment_safety | Deployment & Release Safety | change_management | capability + operational |
| 16 | incident_management | Incident Management & Response | ops_readiness | capability + operational |
| 17 | observability | System Observability | ops_readiness | capability + operational |
| 18 | change_control | Change & Configuration Control | change_management | capability + operational |
| 19 | nonfunctional_testing | Non-Functional Testing | test_strategy | capability + operational |
| 20 | test_organisation | Test Organisation & Competency | governance | capability + operational |
| 21 | supplier_quality | Supplier & Third-Party Quality | third_party | capability + operational |
| 22 | defect_prevention | Defect Prevention & Root Cause Analysis | feedback | capability |
| 23 | quality_gates | Quality Gates & Decision Authority | governance | capability + operational |
| 24 | continuous_improvement | Continuous Improvement Culture | governance | capability + operational |
| 25 | phase_execution | Project & Test Phase Execution | test_phase_progress | operational |
| 26 | phase_governance | Test Phase Governance | test_phase_progress | capability |
| 27 | testability_design | Testability by Design | architecture | capability |
| 28 | legacy_management | Legacy System Management | architecture | capability |
| 29 | architectural_complexity | Architectural Complexity | architecture | operational |
| 30 | life_safety_compliance | Life Safety Regulatory Compliance | life_safety | capability |
| 31 | automotive_compliance | Automotive Safety & ASPICE Compliance | automotive_safety | capability |
| 32 | automation_diagnostics | Automation Health Diagnostics | test_assets | operational |
| 33 | enterprise_operations | Enterprise Scale Operations | enterprise_scale | operational + capability |
| 34 | supplier_quality_deep_dive | Supplier Quality Deep Dive | third_party | operational |
| 35 | governance_authority | Governance Authority & Executive Sponsorship | governance | capability + operational |

### 89 KPIs

KPIs are derived from assessment responses. Each has a severity band (CRITICAL/HIGH/MEDIUM/LOW/EXCLUDED) based on urgency scoring.

**Core KPIs (22):**

| KPI ID | Name | Category |
|--------|------|----------|
| TEST-LEAD-COV | Test Leadership Coverage | governance |
| QUALITY-AUTH | Quality Gate Authority | governance |
| SHIFT-LEFT | Shift-Left Index | governance |
| SUPP-RISK | Supplier Risk Exposure | third_party |
| SUPP-COMPLEXITY | Supplier Complexity | third_party |
| SUPP-REQ-VAL | Supplier Requirements Validation | third_party |
| SUPP-FUNC-VAL | Supplier Functional Validation | third_party |
| SUPP-NFR-VAL | Supplier NFR Validation | third_party |
| SUPP-REGR-QUAL | Supplier Regression Quality | third_party |
| SUPP-INT-RISK | Supplier Integration Risk | third_party |
| DEFECT-ESCAPE | Defect Escape Rate | feedback |
| AUTOMATION-HEALTH | Automation Health Index | test_assets |
| GATE-INTEGRITY | Gate Integrity Score | governance |
| REQ-COVERAGE | Requirements Coverage | requirements |
| REQ-STABILITY | Requirements Stability | requirements |
| BUILD-SUCCESS | Build Success Rate | development |
| DEPLOYMENT-FREQ | Deployment Frequency | change_management |
| CHANGE-FAILURE | Change Failure Rate | change_management |
| MTTR | Mean Time to Restore | ops_readiness |
| CODE-REVIEW-COV | Code Review Coverage | development |
| ENV-PARITY | Environment Parity | environment |
| TECH-DEBT | Technical Debt Index | architecture |

**Category aggregate KPIs (13):** CAT-GOVERNANCE, CAT-TEST-STRATEGY, CAT-TEST-ASSETS, CAT-DEVELOPMENT, CAT-ENVIRONMENT, CAT-REQUIREMENTS, CAT-CHANGE-MGMT, CAT-FEEDBACK, CAT-ARCHITECTURE, CAT-OPS-READINESS, CAT-THIRD-PARTY, CAT-PHASE-PROGRESS, plus composites.

**Phase-specific KPIs (36):** PHASE-{UNIT,INT,SYS,E2E,UAT,OAT}-{PASS,PROGRESS,BLOCKED}, plus phase gate templates.

**Defect management KPIs (18):** DEFECT-{PROFILE,TARGET-COMPLIANCE,MGMT-MATURITY,CONTAINMENT,SEVERITY-PROFILE,MATURATION,LEAKAGE,TRIAGE-TIME,FIX-TIME,COUNT-*,LEAKAGE-*}, plus defect gate templates per phase.

**Other derived KPIs:** DEV-UNIT-HEALTH, DEV-CODE-QUALITY, TEST-PASS-RATE, TEST-EXECUTION-PROGRESS, COMPLIANCE-POSTURE, REGULATORY-COMPLIANCE, TEST-CYCLES-*.

### Scoring Model

**Maturity Levels:**
```
Level 1 — Initial:               0-20%   — Ad-hoc processes
Level 2 — Managed:               20-40%  — Basic processes at project level
Level 3 — Defined:               40-60%  — Standardised across organisation
Level 4 — Quantitatively Managed: 60-80%  — Measured and controlled
Level 5 — Optimising:            80-100% — Continuous improvement culture
```

**Risk Levels (derived from score):**
```
low:       score 0-20%  (maturity 4.0-5.0) — Well-managed
moderate:  score 20-40% (maturity 3.0-3.99) — Some concerns
high:      score 40-60% (maturity 2.5-2.99) — Significant risks
very_high: score 60-80% (maturity 2.0-2.49) — Critical risks
extreme:   score 80-100% (maturity 1.0-1.99) — Project viability in question
```
*Note: Risk score is inverted — higher score = higher risk = lower maturity.*

**Phase-Based Dimension Weights (how Cap vs Ops importance shifts by project phase):**
```
initiation:  Cap 90% / Ops 10% — Assessing potential, limited track record
planning:    Cap 80% / Ops 20% — Validating plans exist, some early indicators
execution:   Cap 50% / Ops 50% — Balanced — plans should produce results
maturation:  Cap 25% / Ops 75% — Results matter more than intentions
transition:  Cap 30% / Ops 70% — Proving operational readiness
closure:     Cap 20% / Ops 80% — Did they deliver? Evidence-based
maintenance: Cap 40% / Ops 60% — Sustainable capability + current performance
```

**Context Modifiers:**
```yaml
scale:    small: 0.8, medium: 1.0, large: 1.3, enterprise: 1.5
delivery: waterfall: 1.1, hybrid_traditional: 1.05, hybrid_agile: 1.0, agile: 0.95, devops: 0.9
geographic: local: 0.9, national: 1.0, multinational: 1.2, global: 1.4
```

---

## The Success Function

### The Linear Fallacy

The naive assumption is that success increases linearly from Low Cap/Low Ops to High Cap/High Ops — that the most successful projects are always the most mature. **This is wrong.**

Projects at extreme positions on the grid (High Cap/Low Ops, or Low Cap/High Ops) can be equally successful — they just absorb different costs. A medical device at Cap >> Ops is successful because it can afford to be slow. A startup at Low/Low is successful (short-term) because it compensates through overwork and agility. But these positions carry costs — and whether those costs are survivable depends on the organisation's capacity to absorb them.

Critically, "low consequence" is not the same as "survivable." A startup's quality defects may be minor (nobody dies), but project failure is **existential** — the entire business collapses. An enterprise can absorb a failed project; a startup cannot. The cost profile of a grid position must account for both defect consequences and project failure consequences.

### Success as a Three-Part Test

Success is not a score. It is a **simultaneous pass on three conditions**:

**1. Viable** — does your grid position cover your stakes?

Are the risks you're carrying survivable if they materialise? This has two layers:

| | Low Defect Consequence | High Defect Consequence |
|---|---|---|
| **Survivable Project Failure** | Enterprise internal tool — low stakes all round | Enterprise regulated product — defects hurt, but org survives a project failure |
| **Existential Project Failure** | **Startup** — defects are recoverable, but project failure kills the business | Medical device startup — defects kill people AND the business |

A startup at Balanced Low is not "safe because consequences are low" — they're gambling that defects won't cost them their only customer and that they can fix faster than problems compound. When that bet fails, the business dies.

**2. Sustainable** — can you maintain this position without destroying the team or accumulating fatal debt?

Heroics work for a sprint, not a year. Over-process works for compliance, not delivery. Every off-diagonal position has a temporal limit:
- Low Cap / High Ops → burnout ceiling (someone leaves, knowledge walks out)
- High Cap / Low Ops → delivery stall (process without output, stakeholders lose patience)
- Low / Low → compounding debt (technical, knowledge, quality — all accumulating)

**3. Sufficient** — does this position deliver enough for your stakeholders?

Enough quality, enough speed, enough compliance, enough value. A perfect process that ships too slowly for a competitive market is insufficient. Fast delivery full of defects to a regulated customer is insufficient.

### Failure Modes

Failure happens when **any one** of these three breaks:

| Failure Mode | What Broke | Example |
|---|---|---|
| Not viable | Carrying risk you can't survive | Startup ships critical defect to only customer → business dies |
| Not sustainable | Burning out, accumulating debt | P8 (UAT Crisis) — heroics exhausted, every fix breaks something else |
| Not sufficient | Not delivering what's needed | P3 (Government) — process-perfect but too slow, project cancelled |

### The Four Capacity Sliders

Every grid position has costs. Whether those costs are absorbable depends on four organisational capacities. These are the "compromise sliders" — they determine which grid positions are accessible and which failure modes are most likely.

| Slider | What It Measures | Low End | High End |
|--------|-----------------|---------|----------|
| **Investment capacity** | Can you afford to move to a different grid position? | Startup — no resources for process investment | Enterprise — can fund any improvement programme |
| **Recovery capacity** | If your position bites you, can you survive the hit? | Startup — one bad release = business death | Enterprise — capital buffers, diverse revenue, institutional resilience |
| **Overwork capacity** | Can the team compensate for gaps through effort? | Mature enterprise — unions, contracts, work-life culture | Startup — survival mode, team will do whatever it takes (short-term) |
| **Time capacity** | Can you afford to be slow? | Startup — market won't wait | Medical/Defence — deliberate pace is acceptable, even mandated |

**These are not independent inputs — they are derivable from the 8 dimensions:**
- High consequence of failure → low risk tolerance → recovery capacity must be high OR Cap must be high
- High market pressure → low time capacity → Ops floor rises
- Small scale / startup → high overwork capacity (short-term), low investment capacity, low recovery capacity
- Regulated → time capacity often high (deliberate pace acceptable), investment capacity forced (regulation mandates spend)
- Low coherence → recovery capacity reduced (integration failures cascade unpredictably)

### The Sweet Spot Is a Zone, Not a Point

The "sweet spot" per project type is not a single Cap/Ops coordinate. It is a **viable zone** on the grid where all three tests (viable, sustainable, sufficient) pass simultaneously, given the slider values.

- A startup's viable zone is **narrow and precarious** — low investment and recovery capacity constrain movement, high overwork capacity allows temporary survival at positions that would kill a larger org
- An enterprise's viable zone is **wide with buffers** — can afford to be anywhere from Balanced High to slightly off-diagonal
- A medical device's viable zone is **constrained to upper-left** by regulation (Cap floor non-negotiable) but has time capacity to sit there comfortably
- A matrix programme's viable zone is **fragile** — organisational coherence issues mean the zone shrinks with scale

### MIRA Proxy Metrics for the Three Tests

| Test | MIRA Indicators |
|------|----------------|
| **Viable** | GATE-INTEGRITY, COMPLIANCE-POSTURE, QUALITY-AUTH, DEFECT-ESCAPE, gap severity between Cap/Ops |
| **Sustainable** | CHANGE-FAILURE, SHIFT-LEFT, AUTOMATION-HEALTH, TECH-DEBT, team velocity trends |
| **Sufficient** | DEPLOYMENT-FREQ, DEV-LEAD-TIME, phase pass rates, TEST-PASS-RATE, REQ-COVERAGE |

---

## 15 Structural Archetypes

Project types are defined by structural shape, not industry domain. Medical device, automotive, defence, and government stage-gate projects are structurally identical — process-heavy, governance-burdened, outsource-dependent, V-model. The domain label affects slider values (defect consequence, regulatory burden), not the archetype.

### Archetype Definitions

| # | Archetype | Structure | Default Cap | Default Ops | Natural Quadrant |
|---|-----------|-----------|-------------|-------------|-----------------|
| 1 | **Micro Startup** | 1-5 people, no process, greenfield, ship-or-die | 10-20% | 15-25% | Balanced Low |
| 2 | **Small Agile** | 5-20 people, light process, tribal knowledge, iterative | 20-30% | 25-40% | Balanced Low |
| 3 | **Scaling Startup** | 20-50 people, process emerging, CI/CD adopting, growing pains | 35-50% | 35-50% | Mid-range |
| 4 | **DevOps Native** | Any size, cloud-native, automation-first, continuous delivery | 25-40% | 60-80% | Ops > Cap |
| 5 | **Component Heroes** | Dedicated teams per component, siloed, weak integration ownership | 40-55% | 40-55% | Mid-range (fragile) |
| 6 | **Matrix Programme** | Borrowed staff, split allegiance, multi-team, integration-at-the-end | 40-55% | 20-35% | Cap > Ops |
| 7 | **Outsource-Managed** | Thin internal team, heavy outsourcing, contract-governed | 50-65% | 20-35% | Cap > Ops |
| 8 | **Regulated Stage-Gate** | Formal phases, governance-heavy, V-model (medical/auto/defence/govt) | 60-80% | 25-45% | Cap > Ops |
| 9 | **Enterprise Balanced** | Large, well-resourced, hybrid delivery, mature processes | 65-85% | 65-85% | Balanced High |
| 10 | **Legacy Maintenance** | Small team, old system, tribal knowledge, change-averse | 10-20% | 20-35% | Balanced Low |
| 11 | **Modernisation** | Replacing legacy, dual-running, knowledge transfer critical | 20-35% | 25-40% | Balanced Low |
| 12 | **Crisis / Firefight** | Quality collapsed, late-stage, reactive, every fix breaks something | 35-50% | 10-20% | Cap > Ops |
| 13 | **Planning / Pre-Delivery** | Nothing built yet, aspirational, no execution data | 35-50% | 0-10% | Cap > Ops |
| 14 | **Platform / Internal** | Internal tooling, enabling function, lower external stakes | 25-40% | 40-55% | Ops > Cap |
| 15 | **Regulated Startup** | Small team, high regulatory burden, under-resourced for the process demanded | 50-65% (forced) | 15-25% | Cap > Ops |

### Default Slider Profiles per Archetype

Each archetype has characteristic slider values that determine its viable zone:

| # | Archetype | Investment | Recovery | Overwork | Time |
|---|-----------|-----------|----------|----------|------|
| 1 | Micro Startup | Very Low | Very Low | High (short-term) | Very Low |
| 2 | Small Agile | Low | Low | Medium-High | Low |
| 3 | Scaling Startup | Medium | Low-Med | Medium | Low-Med |
| 4 | DevOps Native | Medium | Medium | Low-Med | Low |
| 5 | Component Heroes | Medium | Medium | Medium | Medium |
| 6 | Matrix Programme | Medium-High | Medium | Low | Medium |
| 7 | Outsource-Managed | Medium-High | Medium-High | Low (internal) | Medium-High |
| 8 | Regulated Stage-Gate | High | Medium-High | Low | High |
| 9 | Enterprise Balanced | High | High | Low | Medium-High |
| 10 | Legacy Maintenance | Very Low | Low | Low | Medium |
| 11 | Modernisation | Low-Med | Low | Medium | Medium |
| 12 | Crisis / Firefight | Low (spent) | Low (eroded) | High (forced) | Very Low |
| 13 | Planning / Pre-Delivery | Medium | Medium | Low (nothing to overwork on) | High |
| 14 | Platform / Internal | Medium | High | Low | Medium |
| 15 | Regulated Startup | Low | Very Low | High | Medium |

### Simulation Output Format

For each archetype, the simulation should produce a sensitivity table showing how each slider deviation shifts the Cap/Ops ratio and whether the position remains viable/sustainable/sufficient:

```
ARCHETYPE: Regulated Stage-Gate
Default position: Cap 70% / Ops 35%
Natural quadrant: Capability > Operational

                    Investment    Recovery      Overwork      Time
                    ──────────    ──────────    ──────────    ──────────
Slider LOW:         Can't build   Defect escape Burnout if    FAILS — can't
                    ops capacity  is existential  compensating  be slow +
                    → stuck at    (med device     for low ops   heavy process
                    Cap>Ops       startup)        → fragile     = stalled

Slider MID:         Natural       Org absorbs   Not needed    Slow but
(default)           state         occasional    at this       correct —
                                  issues        position      viable

Slider HIGH:        Can invest    Enterprise    N/A           Time budget
                    in ops →      defence —     (overwork     allows ops
                    Cap 65%/      buffers       not the       investment →
                    Ops 50%       everywhere    strategy)     Cap 60%/Ops 50%

Three-test result:  Viable: YES   Viable: YES   Sustain: YES  Viable: YES
(at default)        Sustain: YES  Sustain: YES  Sufficient:   Sustain: YES
                    Sufficient:   Sufficient:   MARGINAL      Sufficient:
                    MARGINAL      YES           (slow)        MARGINAL
```

---

## Calibration Data: 12 MIRA Personas Mapped to Archetypes

The 12 personas from MIRA's simulation harness serve as calibration/validation data. Each maps to one of the 15 archetypes and has validated Cap/Ops outcomes from real scoring runs.

### Persona-to-Archetype Mapping

| Persona | Archetype | Notes |
|---------|-----------|-------|
| P1 Startup Chaos | #1 Micro Startup | Textbook case |
| P2 Small Agile Team | #2 Small Agile | Textbook case |
| P3 Government Waterfall | #8 Regulated Stage-Gate | Govt domain, same structure |
| P4 Enterprise Financial | #9 Enterprise Balanced | With regulatory overlay |
| P5 Medical Device | #8 Regulated Stage-Gate | Medical domain, same structure as P3 |
| P6 Failing Automation | #3 Scaling Startup | Growth-stage with automation trap |
| P7 Greenfield Cloud | #4 DevOps Native | With coherence issues |
| P8 UAT Crisis | #12 Crisis / Firefight | Was #6 Matrix, became crisis |
| P9 Planning Phase | #13 Planning / Pre-Delivery | Temporal state, not archetype |
| P10 Golden Enterprise | #9 Enterprise Balanced | Control — benchmark |
| P11 Automotive Embedded | #8 Regulated Stage-Gate | Auto domain, same structure as P3/P5 |
| P12 Legacy Modernisation | #10 Legacy Maintenance | Transitioning toward #11 |

### Persona Dimension Mapping

| # | Persona | D1 Consequence | D2 Market Pressure | D3 Complexity | D4 Regulatory | D5 Team Stability | D6 Outsourcing | D7 Lifecycle | D8 Coherence |
|---|---------|---------------|-------------------|--------------|--------------|------------------|---------------|-------------|-------------|
| 1 | Startup Chaos | 2 (financial) | 5 (ship-or-die) | 1 (simple) | 1 (none) | 1 (tribal) | 1 (in-house) | 1 (greenfield) | 5 (unified) |
| 2 | Small Agile Team | 2 (financial) | 4 (urgent) | 2 (modular) | 1 (none) | 2 (informal) | 1 (in-house) | 2 (growth) | 4 (aligned) |
| 3 | Govt Waterfall | 3 (reputational) | 1 (deliberate) | 4 (complex) | 4 (heavy) | 4 (codified) | 4 (heavily outsourced) | 3 (mature) | 3 (coordinated) |
| 4 | Enterprise Financial | 4 (regulatory) | 2 (measured) | 4 (complex) | 5 (existential) | 4 (codified) | 3 (significant) | 3 (mature) | 3 (coordinated) |
| 5 | Medical Device | 5 (life-critical) | 1 (deliberate) | 3 (integrated) | 5 (existential) | 5 (institutionalised) | 2 (selective) | 3 (mature) | 4 (aligned) |
| 6 | Failing Automation | 2 (financial) | 3 (competitive) | 2 (modular) | 1 (none) | 3 (semi-documented) | 1 (in-house) | 2 (growth) | 2 (siloed) |
| 7 | Greenfield Cloud | 2 (financial) | 4 (urgent) | 2 (modular) | 1 (none) | 2 (informal) | 1 (in-house) | 1 (greenfield) | 2 (siloed) |
| 8 | UAT Crisis | 3 (reputational) | 2 (measured) | 4 (complex) | 1 (none) | 3 (semi-documented) | 3 (significant) | 2 (growth) | 1 (fragmented) |
| 9 | Planning Phase | 2 (financial) | 3 (competitive) | 2 (modular) | 2 (light) | 3 (semi-documented) | 1 (in-house) | 1 (greenfield) | 4 (aligned) |
| 10 | Golden Enterprise | 3 (reputational) | 3 (competitive) | 3 (integrated) | 3 (moderate) | 5 (institutionalised) | 2 (selective) | 3 (mature) | 5 (unified) |
| 11 | Automotive Embedded | 5 (life-critical) | 1 (deliberate) | 5 (deeply interconnected) | 5 (existential) | 4 (codified) | 4 (heavily outsourced) | 3 (mature) | 2 (siloed) |
| 12 | Legacy Modernisation | 3 (reputational) | 2 (measured) | 3 (integrated) | 3 (moderate) | 1 (tribal) | 1 (in-house) | 4 (legacy) | 3 (coordinated) |

### Persona Outcomes (Validated)

| # | Persona | Cap Aggregate | Ops Aggregate | Classification | Risk | Score Range |
|---|---------|--------------|---------------|---------------|------|-------------|
| 1 | Startup Chaos | very low | low | Balanced Low | extreme | ~2-8% |
| 2 | Small Agile Team | low | low-med | Balanced Low | very_high | ~15-25% |
| 3 | Govt Waterfall | high | low-med | Cap > Ops | high | ~35-45% |
| 4 | Enterprise Financial | high | high | Balanced High | moderate | ~70-80% |
| 5 | Medical Device | high-very_high | medium | Cap > Ops | moderate | ~55-65% |
| 6 | Failing Automation | medium | low-very_low | Cap > Ops | high | ~30-40% |
| 7 | Greenfield Cloud | low-med | medium-high | Ops > Cap | high | ~40-50% |
| 8 | UAT Crisis | medium | very_low | Cap > Ops | very_high | ~15-25% |
| 9 | Planning Phase | medium | very_low | Cap > Ops | very_high | ~15-25% |
| 10 | Golden Enterprise | very_high | very_high | Balanced High | low | ~88-95% |
| 11 | Automotive Embedded | med-high | low | Cap > Ops | high | ~35-45% |
| 12 | Legacy Modernisation | very_low | low | Balanced Low | extreme | ~2-8% |

### Full Persona Context Data

Each persona's complete filter/scoring/KPI context and category profiles are available in the source file:
`backend/scripts/persona_simulator.py` — function `_build_personas()`

Key context fields per persona:

```
filter_context:
  scale: small | medium | large | enterprise
  delivery_model: agile | hybrid_agile | hybrid_traditional | waterfall | devops
  project_phase: planning | early_dev | mid_dev | testing_phase | transition | closure | maintenance
  regulatory_applicable: true | false
  regulatory_standards: [list of standards]
  geographic: local | national | multinational
  organisation_type: startup | sme | government | financial_services | healthcare | technology | saas | retail | automotive | insurance | consultancy
  product_stage: startup | growth | mature | legacy

kpi_context:
  current_phase: planning | execution | transition | closure | maintenance
  regulatory_level: low | medium | high
  team_size: integer
  release_frequency: daily | weekly | biweekly | monthly | quarterly | on-demand

scoring_context:
  regulatory: none | iso_9001_certified | iso_27001 | sox | pci_dss | fda_21_cfr_11 | iec_62443 | other
  scale: small | medium | large | enterprise
  delivery_model: (same as filter_context)
  project_phase: (same as kpi_context.current_phase)
```

Category profiles use maturity levels: `very_low`, `low`, `medium`, `high`, `very_high`

---

## Maturity Profiles (Answer Generation Parameters)

Used by the simulation to generate realistic assessment answers:

```python
MATURITY_PROFILES = {
    'very_low':  {'pct_range': (5, 25),   'toggle_true_prob': 0.1,  'select_bias': 'worst'},
    'low':       {'pct_range': (15, 40),  'toggle_true_prob': 0.3,  'select_bias': 'low'},
    'medium':    {'pct_range': (35, 65),  'toggle_true_prob': 0.6,  'select_bias': 'mid'},
    'high':      {'pct_range': (55, 85),  'toggle_true_prob': 0.8,  'select_bias': 'high'},
    'very_high': {'pct_range': (75, 95),  'toggle_true_prob': 0.95, 'select_bias': 'best'},
}
```

---

## Progressive Disclosure Mechanism

MIRA uses a two-pass filter that gates operational questions behind capability thresholds:

1. **Pass 1:** User answers branching questions → filter determines which capability questions to show
2. **Pass 2:** Capability answers feed back → PD-001 evaluates average capability score → if >= 30%, unlocks operational questions for that category

**Implication for simulation:** Low-capability personas never get asked operational questions, so their operational scores remain structurally low. This means the "Ops > Cap" quadrant is **structurally difficult to reach** for low-maturity personas — you need moderate capability (enough to unlock PD) combined with meaningfully higher operational execution.

---

## Key Structural Insights

1. **PD prevents Ops > Cap at low maturity:** The progressive disclosure mechanism means truly low-capability organisations can never show high operational scores — the system won't ask those questions. This is by design (if you can't describe your process, measuring its execution is meaningless).

2. **Product Stage is currently INERT:** Collected in context but not consumed by scoring or derivation. The implicit dimensions (overwork, alignment risk) are narrative concepts, not yet computed.

3. **Organisational Coherence has no direct input:** MIRA captures `supplier_testing_involved` (boolean) but not the degree of internal fragmentation. The dimension exists conceptually but isn't measured.

4. **Phase weights already encode a Cap/Ops balance curve:** The existing `phase_weights` configuration shows MIRA already modulates the Cap/Ops importance by project phase — a proto-version of what this simulation aims to derive more precisely.

---

## What the Simulation Should Explore

### Core Questions

1. **For each of the 15 archetypes, what is the viable zone on the Cap/Ops grid?** Map the region where all three tests (viable, sustainable, sufficient) pass simultaneously at default slider values.

2. **How do the 4 sliders reshape the viable zone?** For each archetype, show how moving each slider from low→high expands or contracts the viable zone, and which slider has the most impact.

3. **Which archetypes are most precarious?** Where is the viable zone smallest? Which have the narrowest margin between "succeeding" and "existential failure"? (Hypothesis: Micro Startup and Regulated Startup are most precarious — narrow zones, low recovery capacity.)

4. **Are off-diagonal positions genuinely successful, or just surviving?** Can we distinguish between "successful at Cap > Ops" (medical device — deliberate, sustainable, correct for context) and "temporarily surviving at Cap > Ops" (crisis — unsustainable, clock ticking)?

5. **What causes transitions between archetypes?** A Scaling Startup (#3) can become Component Heroes (#5) or DevOps Native (#4) depending on choices. What slider changes drive these transitions? Can we model the decision points?

### Secondary Questions

6. **Is Mid-range a real state?** No MIRA persona naturally lands there. Is it an unstable transitional state (passing through between archetypes) or a viable position for some dimension profiles?

7. **What are the interaction effects between sliders?** Does low recovery + low time capacity create compounding failure risk beyond what either alone predicts? Are there toxic combinations?

8. **Can the model predict P8-type failures retroactively?** If we input P8's archetype (#12 Crisis) with pre-crisis slider values (#6 Matrix Programme), can the model show the viable zone shrinking to zero — predicting the crisis before it happened?

9. **What does the "success surface" look like per archetype?** For a given archetype, plot the three-test results across the Cap/Ops grid as a heatmap. Is there a clear viable region? A cliff edge? A plateau?

10. **Can we derive the 8 dimension values from the 4 sliders, or vice versa?** The sliders are supposed to be derivable from the dimensions. Can we formalise that mapping and test it against the 12 persona calibration data?
