"""
Archetype and persona descriptions — standalone, no heavy dependencies.

Extracted from components.py so the API can import these without pulling in
streamlit, plotly, or numpy.
"""

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

# Persona descriptions — human-readable explanations for the feedback page.
# Each has a brief context line and a narrative quote from the research definitions.
PERSONA_DESCRIPTIONS = {
    "P1 Startup Chaos": (
        "3\u20138 person startup, no regulation, shipping through heroics and client proximity. "
        "\"You're delivering through effort, not process. That works until it doesn't.\""
    ),
    "P2 Small Agile Team": (
        "8\u201315 person team, real agile ceremonies, tribal knowledge instead of documentation. "
        "\"Your team makes this work. Your process doesn't. What happens when the team changes?\""
    ),
    "P3 Government Waterfall": (
        "50\u2013100 person public-sector project, heavy compliance, manual stage-gated delivery. "
        "\"You have the structure. Now you need the speed. Process without agility is just expensive documentation.\""
    ),
    "P4 Enterprise Financial": (
        "200+ person regulated financial platform (SOX, PCI-DSS), mature pipelines, heavy outsourcing. "
        "\"Your machine works, but increasingly it's other people's machines bolted onto yours.\""
    ),
    "P5 Medical Device": (
        "20\u201350 person safety-critical product (FDA, IEC 62304), slow by design \u2014 lives depend on it. "
        "\"Your process exists for a reason \u2014 people's lives. The challenge is keeping it sustainable.\""
    ),
    "P6 Failing Automation": (
        "30\u201360 person growth-stage team, significant automation investment that isn't translating to delivery. "
        "\"You bought the tools before you built the foundations. Your automation is now technical debt wearing a quality hat.\""
    ),
    "P7 Cloud-Native": (
        "15\u201330 person DevOps team, greenfield product, modern tooling, untested at scale. "
        "\"You've built a perfect island and declared the sea somebody else's problem.\""
    ),
    "P8 Late-Stage UAT Crisis": (
        "80\u2013150+ person project in late delivery, UAT haemorrhaging defects, every gate rubber-stamped. "
        "\"You built what you thought was right, not what the customer asked for.\""
    ),
    "P9 Planning Phase": (
        "20\u201340 person team starting a new project, nothing built yet \u2014 all metrics are blank or baseline. "
        "\"You have the luxury of time and a clean slate. Every decision you make now compounds through the lifecycle.\""
    ),
    "P10 Golden Enterprise": (
        "150\u2013300 person mature company with genuine engineering culture, sustainable pace, quality by conviction. "
        "\"You've built something rare \u2014 a quality culture that sustains itself. Guard against the slow drift.\""
    ),
    "P11 Automotive Embedded": (
        "200+ person multi-tier automotive programme (ISO 26262, ASPICE), compliance-driven with deep supplier chains. "
        "\"You've built a compliance fortress around a trust vacuum.\""
    ),
    "P12 Legacy Modernisation": (
        "5\u201312 person team maintaining a 15-year system, tribal knowledge, retirement risk, forced modernisation. "
        "\"Your system runs on institutional memory, not process. Every retirement letter is a risk event.\""
    ),
}
