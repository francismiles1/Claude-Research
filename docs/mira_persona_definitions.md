# Simulation Research — Output Validation

## Two Objectives
1. **Risk Snapshot** — Snapshot health, structure, wellbeing of project + org → determine RISK → actionable outcomes
2. **KPI Selection** — Determine which KPIs to track (with severity rankings) for project/org maturity

## The 2x2 Quadrant Model (Capability vs Operational)

| | High Operational | Low Operational |
|---|---|---|
| **High Capability** | Predictable & Assured (Balanced High) | Inefficient Success (Cap > Ops) |
| **Low Capability** | Hidden Risk (Ops > Cap) | Chaotic Delivery (Balanced Low) |

- Maps to MIRA's existing `classify_pair()` diagnostic classification
- Thresholds: high>=60%, low<50%, balanced_gap<=15%, divergence_gap>20%

## Implicit Dimensions (No separate input needed)

### Overwork/Sustainability
- Captured implicitly by Product Stage
- Startup=maximum, Growth=high, Mature=low, Legacy=low
- Affects Objective 1 (risk narrative) NOT Objective 2 (KPI selection)
- Product Stage field exists in Context Setting but is currently INERT in backend services

### Organisational Alignment (Technical Hijacking Risk)
- Left-biased bell curve across Product Stage journey
- Startup: low risk (survival forces alignment)
- Growth: PEAK risk (empire-building, technical hijacking, fractured direction)
- Mature: low risk (engineered out through governance)
- Legacy: low risk (established processes)
- Manifests as gap between technical categories (TST, DEV) and governance (GOV, TL)
- Same governance score means different things at different stages — startup doesn't need it yet vs growth-stage lost control

## Potential Gaps Identified During Persona Definition
- **Product Stage is INERT** — collected but not consumed by any scoring/derivation service
- **Project Phase awareness** — engine may not modulate KPI severity based on phase (P9 planning vs P8 execution)
- **Reuse / Design for Testability** — only covered at TMMi L5 and one question (ARC-C2). No unified assessment question about leveraging previous project assets. Relevant for P9 (planning phase)
- **Outsourcing depth** — context captures `supplier_testing_involved` (boolean) but not the DEGREE of outsourcing dependency. P3/P4/P11 all heavily outsourced but no way to signal this intensity

## Summary Table

| # | Persona | Quadrant | Risk | Product Stage | Alignment Risk |
|---|---------|----------|------|---------------|----------------|
| 1 | Startup Chaos | Hidden Risk | High | startup | Low (survival) |
| 2 | Small Agile Team | Balanced Low | Medium-High | growth | Low-Med (proximity) |
| 3 | Government Waterfall | Inefficient Success | Medium | mature | Low (governed) |
| 4 | Enterprise Financial | Predictable & Assured | Low | mature | Low (governed) |
| 5 | Medical Device | Inefficient Success (intentional) | Medium-Low | growth/mature | Low (mission-driven) |
| 6 | Failing Automation | Capability > Operational | High | growth | PEAK (tool-first hijack) |
| 7 | Greenfield Cloud-Native | Balanced Mid | Medium (latent) | startup/growth | Medium (silo risk) |
| 8 | Late-Stage UAT Crisis | Chaotic Delivery | Critical | mature | Medium (complacency) |
| 9 | Planning Phase | Balanced Low (default) | Medium | startup/growth | N/A (too early) |
| 10 | Golden Enterprise | Predictable & Assured | Low | mature | Low (culture-driven) |
| 11 | Automotive Embedded | Inefficient Success | High | mature | Medium (multi-tier) |
| 12 | Legacy Modernisation | Hidden Risk | High | legacy | Low internal / High cross-team |

## Persona Definitions

### Persona 1 — Startup Chaos (The MVP Scramble)
- **Context:** Startup, 3-8 people, single decision-maker, shoestring budget
- **Product Stage:** startup | **Scale:** small | **Delivery:** agile-ish | **Regulatory:** none
- **Automation:** minimal | **CI/CD:** none | **Environments:** minimal/shared
- **Capability:** Genuinely low. No governance, no formal processes, single person gates all decisions
- **Operational:** Deceptively functional. Delivers through heroics + client proximity. Heavy right-side V-model (UAT, beta, client validation). Processes emerge organically from pain
- **Target Quadrant:** Hidden Risk (Low Cap, Medium Ops)
- **Classification:** Operational > Capability | **Risk:** High
- **KPIs CRITICAL:** GATE-INTEGRITY, QUALITY-AUTH, REQ-STABILITY, REQ-COVERAGE
- **KPIs HIGH:** CHANGE-FAILURE, PHASE-UNIT-PASS, PHASE-INT-PASS, PHASE-SYS-PASS, PHASE-E2E-PASS, PHASE-UAT-PASS, SHIFT-LEFT
- **KPIs MEDIUM:** AUTOMATION-HEALTH, DEFECT-ESCAPE, REGRESSION-COVERAGE
- **KPIs LOW/EXCLUDED:** SUPPLIER-*, COMPLIANCE-*
- **Narrative:** "You're delivering through effort, not process. That works until it doesn't."

### Persona 2 — Small Agile Team (The Scrappy Professionals)
- **Context:** Small company or autonomous team, 8-15 people, flat structure
- **Product Stage:** growth | **Scale:** small | **Delivery:** agile | **Regulatory:** none/minimal
- **Automation:** moderate (unit tests automated, rest manual) | **CI/CD:** yes (basic) | **Environments:** dev + staging
- **Capability:** Low-to-Medium. Real agile ceremonies, code reviews, DoD exists — but tribal knowledge, not documented. Standards enforced by peer pressure not governance. Key person leaves = process leaves
- **Operational:** Medium. Delivers through sprint cadence. CI catches obvious breaks. Test coverage patchy — unit tests where devs cared, gaps elsewhere. Integration/system testing largely manual
- **Key Distinction from P1:** Chaos replaced by informality. Works because team is good, not process
- **Target Quadrant:** Balanced Low (Low-Med Cap, Low-Med Ops, gap <15%)
- **Classification:** Balanced Low | **Risk:** Medium-High
- **KPIs CRITICAL:** TEST-COVERAGE, REGRESSION-COVERAGE
- **KPIs HIGH:** AUTOMATION-HEALTH, SHIFT-LEFT, DEFECT-ESCAPE, DEV-LEAD-TIME
- **KPIs MEDIUM:** GATE-INTEGRITY, CHANGE-FAILURE, REQ-COVERAGE, QUALITY-AUTH
- **KPIs LOW/EXCLUDED:** SUPPLIER-*, COMPLIANCE-*, heavy governance KPIs
- **Narrative:** "Your team makes this work. Your process doesn't. What happens when the team changes?"

### Persona 3 — Government Waterfall (The Compliance Machine)
- **Context:** Government dept or public-sector contractor, 50-100 people
- **Product Stage:** mature (overwork: low — union/contract boundaries) | **Scale:** large | **Delivery:** traditional (stage-gated waterfall) | **Regulatory:** heavy (govt standards, accessibility, data protection)
- **Automation:** minimal-to-moderate | **CI/CD:** limited/none (manual deploys through CABs) | **Environments:** multiple formal (Dev/SIT/UAT/Pre-prod/Prod)
- **Capability:** Medium-to-High. Governance extensive — everything documented, formal review boards, audit trails. Standards for everything. Process abundant, possibly excessive
- **Operational:** Low-to-Medium. Delivery slow and rigid. Change requests take weeks. Testing thorough but manual and late-cycle. Defects in UAT = expensive rework. Feedback loops measured in months
- **Key Character:** Inverse of Persona 1. V-model followed religiously, left-to-right, never iteratively. Outsources heavily — manages by contract not competence. "Outsources thinking."
- **Target Quadrant:** Inefficient Success (High Cap, Low-Med Ops)
- **Classification:** Capability > Operational | **Risk:** Medium
- **KPIs CRITICAL:** DEV-LEAD-TIME, CHANGE-FAILURE, SHIFT-LEFT, PHASE-INT-PASS (outsourced component integration)
- **KPIs HIGH:** AUTOMATION-HEALTH, DEPLOYMENT-FREQ, DEFECT-ESCAPE, REGRESSION-COVERAGE, SUPPLIER-QUALITY, SUPPLIER-SLA
- **KPIs MEDIUM:** TEST-EXECUTION-PROGRESS, PHASE-SYS-PASS, PHASE-UAT-PASS
- **KPIs LOW/EXCLUDED:** GATE-INTEGRITY (already strong), QUALITY-AUTH (already strong)
- **Narrative:** "You have the structure. Now you need the speed. Process without agility is just expensive documentation."

### Persona 4 — Enterprise Financial Platform (The Regulated Powerhouse)
- **Context:** Major bank, insurer, or fintech at scale. 200+ people, multiple squads, formal programme governance
- **Product Stage:** mature (overwork: low — structured, well-resourced) | **Scale:** enterprise | **Delivery:** hybrid_agile | **Regulatory:** maximum (SOX, PCI-DSS, ISO 27001, FCA/APRA)
- **Automation:** significant | **CI/CD:** mature pipelines, automated quality gates | **Environments:** full estate (Dev/SIT/SIT2/UAT/Perf/Pre-prod/Prod)
- **Capability:** High. Regulatory pressure forced genuine process maturity — embedded practice, not just documentation. Audit-ready at any time
- **Operational:** High. Delivers consistently with resources, tooling, organisational muscle. Defect escape rates low. Regression suites comprehensive
- **Key Character:** In-house talent experienced but coasting — do the minimum, no more. Real work heavily outsourced. Risk is at the SEAMS between outsourced components. Integration consistency and supplier governance are the critical concerns
- **Target Quadrant:** Predictable & Assured (High Cap, High Ops)
- **Classification:** Balanced High | **Risk:** Low
- **KPIs CRITICAL:** SUPPLIER-QUALITY, SUPPLIER-SLA (outsourced dependency is primary risk vector)
- **KPIs HIGH:** DEV-LEAD-TIME, DEPLOYMENT-FREQ, PHASE-INT-PASS, PHASE-SYS-PASS (integration seams), DEFECT-ESCAPE
- **KPIs MEDIUM:** CHANGE-FAILURE, SHIFT-LEFT, AUTOMATION-HEALTH, REGRESSION-COVERAGE
- **KPIs LOW:** GATE-INTEGRITY, QUALITY-AUTH, TEST-COVERAGE, COMPLIANCE-* (already strong)
- **Narrative:** "Your machine works, but increasingly it's other people's machines bolted onto yours. Your risk is at the seams — and your in-house team has stopped looking closely."

### Persona 5 — Medical Device (The Safety-Critical Regulator's Dream)
- **Context:** Medical device manufacturer, 20-50 people, specialist domain
- **Product Stage:** growth/mature (overwork: moderate — regulatory deadlines, not market speed) | **Scale:** medium | **Delivery:** hybrid_traditional (V-model core, agile within phases) | **Regulatory:** maximum non-negotiable (FDA 21 CFR Part 11, IEC 62304, ISO 13485, ISO 14971)
- **Automation:** moderate (unit/integration automated; validation heavily manual for regulatory evidence) | **CI/CD:** partial | **Environments:** formal + specialised (HIL, simulated patient environments, validation labs)
- **Capability:** High. Regulation forces it AND the team understands why. Traceability complete and genuine. Risk management (ISO 14971) embedded in every decision. Documentation heavy but purposeful — lives depend on it
- **Operational:** Medium. Slow by design — you don't rush a pacemaker. Testing exhaustive, sequential. V-model appropriate here. Bottleneck is validation cycles
- **Key Character:** The one persona where heavy process is CORRECT. P3's bureaucracy is wasteful; P5's is life-preserving. Team deeply technical, domain-expert, motivated by gravity of what they build. Similar to government/military projects in character
- **Target Quadrant:** Inefficient Success (High Cap, Medium Ops) — intentionally so
- **Classification:** Capability > Operational (gap smaller than P3, justified) | **Risk:** Medium-Low
- **KPIs CRITICAL:** COMPLIANCE-COVERAGE, REQ-COVERAGE (regulatory traceability is existential)
- **KPIs HIGH:** REGRESSION-COVERAGE, TEST-COVERAGE, DEFECT-ESCAPE (escapes could harm patients)
- **KPIs MEDIUM:** DEV-LEAD-TIME, CHANGE-FAILURE, AUTOMATION-HEALTH
- **KPIs LOW:** SHIFT-LEFT (less relevant — validation MUST happen late), DEPLOYMENT-FREQ (releases are deliberate)
- **KPIs ACTIVE but well-scored:** GATE-INTEGRITY, QUALITY-AUTH (already strong)
- **Narrative:** "Your process exists for a reason — people's lives. The challenge is keeping it sustainable as the product grows, without cutting corners that can't be cut."

### Persona 6 — Failing Automation Rescue (The Tool-First Trap)
- **Context:** Mid-size tech company, 30-60 people, growth-stage trying to "level up"
- **Product Stage:** growth (overwork: high — stretched between broken automation AND manual fallback) | **Scale:** medium | **Delivery:** agile/hybrid_agile | **Regulatory:** minimal/none
- **Automation:** significant on paper, minimal in practice (high volume, low value — flaky, unmaintained, poorly designed) | **CI/CD:** exists but distrusted, frequently red, teams bypass | **Environments:** exist but unstable — root cause of flaky tests
- **Capability:** Medium. Invested — strategy exists, tooling purchased, people hired. But tool-first, not fundamentals-first. Test design weak, data management afterthought, environment parity poor
- **Operational:** Low-to-Medium and TRENDING DOWNWARD. Automation actively hurting delivery. Flaky tests block pipelines, false positives erode trust. Manual testing was honestly more effective
- **Key Character:** PEAK alignment risk. Technical leader championed automation as THE transformation. Business funded it. Fundamentals skipped. Now trapped: too invested to abandon, too broken to rely on. Team demoralised
- **Target Quadrant:** Capability > Operational (investment exists on paper, doesn't translate to outcomes)
- **Classification:** Capability > Operational | **Risk:** High (and rising — trajectory wrong)
- **KPIs CRITICAL:** AUTOMATION-HEALTH (core crisis), TEST-COVERAGE (think they have it, don't), DEFECT-ESCAPE (automation not catching real defects)
- **KPIs HIGH:** REGRESSION-COVERAGE, SHIFT-LEFT, CHANGE-FAILURE (broken pipeline = risky changes), ENV-STABILITY
- **KPIs MEDIUM:** DEV-LEAD-TIME, DEPLOYMENT-FREQ, PHASE-INT-PASS, PHASE-SYS-PASS
- **KPIs LOW/EXCLUDED:** SUPPLIER-*, COMPLIANCE-*, GATE-INTEGRITY (gates exist, they're just gating rubbish)
- **Narrative:** "You bought the tools before you built the foundations. Your automation is now technical debt wearing a quality hat."

### Persona 7 — Greenfield Cloud-Native (The Clean Slate)
- **Context:** Modern tech company or innovation arm, 15-30 people, DevOps-oriented
- **Product Stage:** startup/growth (overwork: moderate — energised, not yet burnt out) | **Scale:** medium | **Delivery:** devops (CI/CD native, trunk-based, feature flags) | **Regulatory:** none/light
- **Automation:** significant (started automated, test pyramid understood) | **CI/CD:** mature from day one | **Environments:** ephemeral, containerised, infrastructure-as-code
- **Capability:** Medium. Good choices, clean architecture, automated from start. But nothing battle-tested. Documentation light. Standards are conventions in heads, not written down
- **Operational:** Medium-to-High. Modern tooling gives velocity out of the box. But it's a honeymoon — no legacy, no production incidents at scale, no complex migrations
- **Key Character:** FALSE CONFIDENCE. Dashboard green, metrics great, team motivated. But product hasn't hit real users at scale. Edge cases haven't materialised. One production incident away from discovering gaps
- **CRITICAL BLIND SPOT — Silo mentality:** Test their services in isolation beautifully. Never tested the SYSTEM. Contract tests validate agreements, not reality. Regard external defects as "interfering" and deprioritise unless governed otherwise. Optimised for left side of V-model, ignored the right
- **Target Quadrant:** Balanced Mid (Med Cap, Med-High Ops, gap <15%)
- **Classification:** Balanced | **Risk:** Medium (latent — deceptively calm)
- **KPIs CRITICAL:** PHASE-SYS-PASS, PHASE-INT-PASS (core blind spot — system/integration testing), DEFECT-ESCAPE (refusing external defects back), GATE-INTEGRITY (must enforce external defect triage)
- **KPIs HIGH:** QUALITY-AUTH (who says "this defect IS yours"?), REQ-COVERAGE (moving fast, requirements implicit), ENV-STABILITY (ephemeral great until you need to reproduce production state)
- **KPIs MEDIUM:** REGRESSION-COVERAGE, TEST-COVERAGE (good but untested at scale), PHASE-E2E-PASS
- **KPIs LOW:** AUTOMATION-HEALTH (naturally strong), SHIFT-LEFT (already shifted), DEV-LEAD-TIME, DEPLOYMENT-FREQ
- **KPIs EXCLUDED:** SUPPLIER-*, COMPLIANCE-*
- **Narrative:** "You've built a perfect island and declared the sea somebody else's problem. Your metrics are green because you're only measuring yourself."

### Persona 8 — Late-Stage UAT Crisis (The Chickens Come Home)
- **Context:** Large company/programme, 80-150+ people. Any industry — this is a project STATE, not an org type
- **Product Stage:** mature (overwork: LOW — and that's the problem. Complacency, not exhaustion. Org FIGHTING to enforce harder work but can't) | **Scale:** large | **Delivery:** hybrid_traditional/hybrid_agile (whatever was planned collapsed into firefighting) | **Regulatory:** varies
- **Automation:** moderate on paper but regression suites being skipped | **CI/CD:** exists but being bypassed — hotfixes direct, pipelines skipped | **Environments:** exist but contested, UAT unstable, shared, deployment queue bottlenecked
- **Capability:** Medium — it existed. Test strategy written, governance defined, gates planned. But every phase rubber-stamped exit criteria under schedule pressure. Capability was real on paper, never enforced
- **Operational:** Low and collapsing. UAT haemorrhaging defects. Every fix introduces new breakage. Scope negotiations daily. Blame game started
- **Key Character:** "Rest on their laurels" trap. Forgot the customer is part of the picture. Delivered what THEY felt was good, not what customer wants. UAT is first time real users see it. Gap between expectation and delivery is enormous. Not a burnout problem — a COMPLACENCY problem
- **Target Quadrant:** Chaotic Delivery (both axes collapsing)
- **Classification:** Balanced Low | **Risk:** Critical
- **KPIs CRITICAL:** DEFECT-ESCAPE (earlier phases didn't catch), GATE-INTEGRITY (every gate rubber-stamped), TEST-EXECUTION-PROGRESS (can't get through test cases), REQ-STABILITY (scope STILL changing in UAT), PHASE-UAT-PASS, PHASE-E2E-PASS (customer-facing validation where truth emerges)
- **KPIs HIGH:** REGRESSION-COVERAGE (fixes without regression), SHIFT-LEFT (root cause — everything deferred), CHANGE-FAILURE (every hotfix risks new breakage), REQ-COVERAGE (didn't validate with customer continuously), DEFECT-SEVERITY-PROFILE (defects aren't minor — functional gaps)
- **KPIs MEDIUM:** QUALITY-AUTH (who's making "ship it anyway" decisions?), DEV-LEAD-TIME, PHASE-SYS-PASS (SIT was inadequate)
- **KPIs LOW/EXCLUDED:** AUTOMATION-HEALTH (irrelevant in crisis), DEPLOYMENT-FREQ, SUPPLIER-*
- **Narrative:** "You built what you thought was right, not what the customer asked for. And nobody worked hard enough to find out sooner."

### Persona 9 — Planning Phase Assessment (The Fresh Start)
- **Context:** Competent mid-size company starting new project, 20-40 people allocated. Done this before
- **Product Stage:** startup/growth (overwork: low — early days, energy high) | **Scale:** medium | **Delivery:** agile/hybrid_agile | **Regulatory:** light/moderate
- **Automation:** minimal (planned, not built — framework selected, no tests written) | **CI/CD:** being configured | **Environments:** being provisioned
- **Project Phase:** planning (the defining characteristic)
- **Capability:** Medium and aspirational. Org has competence from previous projects. Test strategy being written, governance being defined. For THIS project, nothing proven yet
- **Operational:** Effectively zero. No delivery, no tests run, no defects, no deployments. Every metric blank or baseline
- **Key Character:** Temporal state, not dysfunction. Challenge: can engine provide useful FORWARD-LOOKING guidance when nothing to measure? Low scores are EXPECTED, not alarming. Planning-phase low ≠ execution-phase low
- **Potential gap:** Reuse / design for testability question missing from unified assessment. Only ARC-C2 + TMMi L5. Planning phase is when reuse decisions are made
- **Target Quadrant:** Balanced Low by default (misleadingly so)
- **Classification:** Balanced Low | **Risk:** Medium (potential, not actual)
- **KPIs CRITICAL:** REQ-COVERAGE (capture requirements properly from start), REQ-STABILITY (stable enough to baseline?)
- **KPIs HIGH:** GATE-INTEGRITY (define gates before needed), QUALITY-AUTH (decide ownership now), SHIFT-LEFT (plan early testing before too late)
- **KPIs MEDIUM:** TEST-COVERAGE (strategy exists?), AUTOMATION-HEALTH (framework planned?), REGRESSION-COVERAGE (how managed as scope grows?)
- **KPIs LOW/EXCLUDED:** PHASE-*-PASS (nothing executed), DEFECT-ESCAPE, DEPLOYMENT-FREQ, DEV-LEAD-TIME, CHANGE-FAILURE, SUPPLIER-*
- **Narrative:** "You have the luxury of time and a clean slate. Every decision you make now — or fail to make — compounds through the entire lifecycle."

### Persona 10 — Golden Enterprise (The Benchmark)
- **Context:** Mature tech company that grew successfully, 150-300 people, strong engineering culture retained through scaling
- **Product Stage:** mature (overwork: minimal — sustainable pace is principle, not slogan) | **Scale:** enterprise | **Delivery:** devops/hybrid_agile (genuine DevOps culture) | **Regulatory:** moderate
- **Automation:** significant (comprehensive test pyramid, performance automated, chaos engineering) | **CI/CD:** mature (full pipeline, canary deployments, automated rollback) | **Environments:** comprehensive, production-like, infrastructure-as-code
- **Capability:** High. Processes mature, documented, followed BY CHOICE not coercion. Governance built by the team through retros and CI. Knowledge codified, shared, continuously updated
- **Operational:** High. Delivery consistent and predictable. Quality tracked and acted upon. Automation comprehensive and trusted. Deployments routine. Incident response structured, blameless, produces genuine improvement
- **Key Distinction from P4:** P4 is high-maturity enforced by regulation, talent coasting, work outsourced. P10 is high-maturity earned by culture, talent engaged, work owned
- **Real-world examples:** Apple, Atlassian, Spotify (early era), Toyota, Netflix
- **Target Quadrant:** Predictable & Assured (High Cap, High Ops)
- **Classification:** Balanced High | **Risk:** Low
- **KPIs CRITICAL:** (none — validation point; genuinely mature org should produce silence at critical)
- **KPIs HIGH:** (none or at most one — perhaps TECH-DEBT if product aged)
- **KPIs MEDIUM:** DEV-LEAD-TIME, REGRESSION-COVERAGE (growing product), DEPLOYMENT-FREQ (maintaining pace)
- **KPIs LOW:** Most KPIs score well — GATE-INTEGRITY, QUALITY-AUTH, TEST-COVERAGE, AUTOMATION-HEALTH, SHIFT-LEFT
- **CONTROL PERSONA:** If engine fires CRITICAL KPIs here, scoring is miscalibrated. Sweet spot = handful of MEDIUM, nothing above
- **Narrative:** "You've built something rare — a quality culture that sustains itself. Your risk is assuming it always will. Guard against the slow drift."

### Persona 11 — Automotive Embedded Platform (The Multi-Tier Minefield)
- **Context:** Automotive OEM or Tier 1 supplier. 200+ people, multi-site, multi-vendor, multi-country
- **Product Stage:** mature (overwork: low-to-moderate for OEM — suppliers absorb the pressure) | **Scale:** enterprise | **Delivery:** hybrid_traditional (ASPICE V-model for safety, agile aspirations within sprints) | **Regulatory:** maximum and layered (ISO 26262/ASIL, ASPICE, ISO 21434, type approval)
- **Automation:** moderate (unit/component automated; integration/system requires physical hardware) | **CI/CD:** partial (automated for SW, system validation requires HIL/SIL/vehicle) | **Environments:** highly specialised (HIL, SIL, bench rigs, vehicle prototypes — expensive, shared, bottlenecked)
- **Capability:** Medium-to-High on paper. ASPICE forces process maturity, ISO 26262 forces safety analysis. Documentation vast. But often COMPLIANCE-DRIVEN not conviction-driven. OEM understands process framework without understanding engineering beneath it. Can audit ASPICE rating but can't critically evaluate technical decisions
- **Operational:** Low-to-Medium. Integration chain brutally complex — HW supplier + low-level SW + application layer + calibration data. Each supplier works to own timeline, own interpretation of requirements, own test approach. OEM orchestrates by contract and milestone, rarely by technical competence
- **Key Character:** Combines worst dynamics: P3's bureaucracy + P4's outsourcing dependency (but safety-critical) + P5's regulatory burden (without conviction) + meddling dynamic (OEM interferes without competence, suppliers hide truth, trust erodes). Integration moment on real vehicle/hardware is where reality hits — defects cross supplier boundaries, require contractual negotiation, trace to requirements ambiguity never resolved
- **V-Model Anti-Pattern:** Massively over-emphasises left side of V-model — requirements, specifications, design. Spends months/years perfecting requirements documents because hardware engineering "measure twice, cut once" mindset applied to software. Requirements are technically "complete" but practically untestable or disconnected from engineering reality. Organisation REFUSES to accept requirements need to change because entire compliance chain (safety case, ASPICE work products, traceability) would need re-baselining. This is a lack of development experience masquerading as rigour — they've shifted left on PAPER, not on LEARNING. A team with genuine SW engineering depth would prototype early and validate assumptions against real hardware
- **Multi-Tier Information Asymmetry:** OEM writes ambiguous/changing system requirements → Tier 1 interprets (interpretation gap = defect source) → Tier 1 test results reported but OEM can't critically evaluate → when integration fails, contractual question ("whose fault?") trumps engineering question ("what's the root cause?"). OEM "technical oversight" teams review Tier 1 work but lack domain depth — their feedback creates rework without improving quality. Tier 1 responds rationally: manages the client, presents sanitised status, routes real engineering through internal channels OEM can't see
- **Target Quadrant:** Inefficient Success (Med-High Cap on paper, Low-Med Ops in practice)
- **Classification:** Capability > Operational | **Risk:** High
- **KPIs CRITICAL:** SUPPLIER-QUALITY (multi-tier, multi-vendor primary risk), SUPPLIER-SLA (delivery consistency across suppliers), PHASE-INT-PASS (first real integration is where specification fantasy meets hardware reality), REQ-STABILITY (org refuses to accept requirements need changing — spec "frozen" while reality diverges), REQ-COVERAGE (traceability exists on paper but requirements themselves untestable/disconnected from engineering reality)
- **KPIs HIGH:** COMPLIANCE-COVERAGE (ISO 26262/ASPICE existential), GATE-INTEGRITY (supplier boundary gates — validating reality or paperwork?), DEFECT-ESCAPE (safety-critical — escapes can kill), PHASE-SYS-PASS (system validation on real hardware), SHIFT-LEFT (they THINK they're shifted left because they spend forever on requirements — but actual engineering validation/prototyping/early integration is missing)
- **KPIs MEDIUM:** CHANGE-FAILURE (changes ripple across suppliers), DEV-LEAD-TIME (glacial), REGRESSION-COVERAGE (across supplier boundaries), QUALITY-AUTH (who arbitrates OEM vs supplier quality disputes?)
- **KPIs LOW:** DEPLOYMENT-FREQ (vehicle programmes, not sprints), AUTOMATION-HEALTH (constrained by HW dependency)
- **Narrative:** "You've built a compliance fortress around a trust vacuum. Your suppliers can deliver — if you let them. Your process can work — if it serves engineering, not politics. And your 18-month requirements phase isn't rigour — it's fear of starting."

### Persona 12 — Legacy Modernisation (The Ticking Clock)
- **Context:** Any size org, but legacy team itself is small: 5-12 people, mostly long-tenured, some approaching retirement
- **Product Stage:** legacy (overwork: low normally, SPIKES violently during forced changes) | **Scale:** medium/large (system serves whole business; team is small) | **Delivery:** traditional (technology dictates it) | **Regulatory:** varies — often compliance landscape has CHANGED since system was built, creating gap that drives modernisation
- **Automation:** minimal (technology predates modern test frameworks; "automation" is a spreadsheet of manual test cases) | **CI/CD:** none (manual deployments by 1-2 people who know the sequence; monthly/quarterly windows) | **Environments:** minimal, fragile (single test env drifted from prod; data refresh is multi-day manual process)
- **Capability:** Low and atrophied. Whatever governance existed at build time (2005-2010) is gone. Documentation non-existent or hopelessly outdated. Process is tribal knowledge — "ask Dave, he was here when it was built." No formal test strategy. Change management is informal risk assessment in someone's head
- **Operational:** Low-to-Medium, deceptively so. System WORKS — 15 years running, processing transactions. Uptime good because team knows every quirk. But changes terrifying — every modification risks breaking unknown dependencies. Regression = "known happy paths and pray." Delivers maintenance through deep institutional knowledge, not process
- **Key Character:** System is the business, held together by 3-4 people who could retire next year. Modernisation forced by: platform end-of-life, regulatory mandate, security audit, or all three. Legacy team caught between: keep lights on, support modernisation, document everything, don't break anything. The people best placed to guide modernisation are the same ones keeping legacy alive — can't do both. Cruel irony
- **Target Quadrant:** Hidden Risk (Low Cap, Low-Med Ops)
- **Classification:** Operational > Capability | **Risk:** High (time-bounded — clock ticking on people, platform, compliance)
- **KPIs CRITICAL:** TECH-DEBT (system IS debt), TEST-COVERAGE (near zero), REGRESSION-COVERAGE (changes break things unpredictably), REQ-COVERAGE (requirements are the running system, not any document)
- **KPIs HIGH:** CHANGE-FAILURE (every change high-risk), DEFECT-ESCAPE (inadequate testing = leaks), AUTOMATION-HEALTH (non-existent, critical for modernisation), SHIFT-LEFT (irrelevant today, essential for migration)
- **KPIs MEDIUM:** GATE-INTEGRITY (informal, gut-feel), QUALITY-AUTH (one person decides), DEV-LEAD-TIME (glacial from fear and complexity), ENV-STABILITY (test env drifted)
- **KPIs LOW:** DEPLOYMENT-FREQ (rare by necessity), PHASE-*-PASS (no formal phases), SUPPLIER-* (unless modernisation involves new vendors)
- **KPIs CONDITIONAL:** COMPLIANCE-* (EXCLUDED unless compliance gap is modernisation driver — then CRITICAL)
- **Overwork pattern:** Unique — low baseline with violent spikes during forced changes
- **Alignment:** Low risk within legacy team (aligned by survival), HIGH risk between legacy team and modernisation programme (different priorities, mutual distrust, competing for same people)
- **Narrative:** "Your system runs on institutional memory, not process. Every retirement letter is a risk event. The clock is ticking — modernise before the knowledge walks out the door."
