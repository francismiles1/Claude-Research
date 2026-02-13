"""
MIRA Question Engine — Question Definitions & Configuration

Ported from MIRA's YAML configuration files for the public research platform.
Covers the 15-category project_risk assessment that produces Cap/Ops scores.

Excludes:
- Framework-specific rules (TMMi/DORA/ISO 9001 level prerequisites, cross-framework propagation)
- Health-check operational data questions (per-cycle volatile data)
- Deprecated questions replaced by PROPOSED-* consolidations
"""

from __future__ import annotations

from collections import OrderedDict

# ---------------------------------------------------------------------------
# Question type constants
# ---------------------------------------------------------------------------

TYPE_TOGGLE = "toggle"
TYPE_SELECT = "select"
TYPE_SLIDER = "slider"
TYPE_MULTISELECT = "multiselect"
TYPE_COMPOUND = "compound"
TYPE_NUMBER = "number"

# Scoring order constants
ASCENDING = "ascending"      # First option = worst, last = best (default)
DESCENDING = "descending"    # First option = best, last = worst
CUSTOM = "custom"            # Explicit value_scores mapping
UNSCORED = "unscored"       # Doesn't contribute to maturity score
GAP = "gap"                  # Gap scoring (0 = no gap = best)


# ---------------------------------------------------------------------------
# QUESTIONS — all maturity question definitions
# ---------------------------------------------------------------------------
# Each question has:
#   text, category, dimension, type, weight
#   options (toggle/select), min/max (slider/number)
#   Optional: scoring_order, inverse, value_scores, gap_scoring,
#             depends_on, branch, conditional, labels, unit, feeds_kpis
#
# Default scoring_order is ASCENDING unless stated.
# Default weight is 1.0 unless stated.
# Toggle scoring: True=100%, False=0%.
# Select ascending: evenly spaced from 0% to 100%.
# Slider: normalised as (value - min) / (max - min) * 100.
# ---------------------------------------------------------------------------

QUESTIONS = OrderedDict([

    # ===== GOVERNANCE =====

    ("GOV-C1", {
        "text": "Is there a dedicated Test Manager/Lead?",
        "category": "governance", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 1.00,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("GOV-C2", {
        "text": "Does the Test Lead have authority to stop releases on quality grounds?",
        "category": "governance", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.65,
        "options": [
            {"value": "no", "label": "No"},
            {"value": "escalate_only", "label": "Escalate only"},
            {"value": "can_delay", "label": "Can delay"},
            {"value": "can_stop", "label": "Can stop"},
        ],
    }),
    ("GOV-C3", {
        "text": "Are quality gates defined with entry/exit criteria?",
        "category": "governance", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.65,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "informal", "label": "Informal"},
            {"value": "defined", "label": "Defined"},
            {"value": "enforced", "label": "Enforced with metrics"},
        ],
    }),
    ("GOV-C4", {
        "text": "Who makes release decisions?",
        "category": "governance", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "scoring_order": DESCENDING,
        "options": [
            {"value": "test_manager", "label": "Test Manager"},
            {"value": "pm_with_test", "label": "PM with Test input"},
            {"value": "pm_alone", "label": "PM alone"},
            {"value": "business_pressure", "label": "Business pressure"},
        ],
    }),
    ("GOV-O1", {
        "text": "When did Test expertise join the project?",
        "category": "governance", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "scoring_order": DESCENDING,
        "options": [
            {"value": "planning", "label": "Planning"},
            {"value": "early_dev", "label": "Early development"},
            {"value": "mid_dev", "label": "Mid development"},
            {"value": "testing_phase", "label": "Testing phase"},
            {"value": "no_dedicated", "label": "No dedicated lead"},
        ],
    }),
    ("GOV-O2", {
        "text": "How widely are dedicated test leads deployed across teams?",
        "category": "governance", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "few", "label": "A few teams"},
            {"value": "some", "label": "Some teams"},
            {"value": "most", "label": "Most teams"},
            {"value": "all", "label": "All teams"},
        ],
    }),
    ("GOV-O3", {
        "text": "What is the quality gate pass/waiver rate?",
        "category": "governance", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.50,
        "scoring_order": DESCENDING,
        "options": [
            {"value": "mostly_pass", "label": "Mostly pass"},
            {"value": "some_waivers", "label": "Some waivers"},
            {"value": "many_waivers", "label": "Many waivers"},
            {"value": "gates_ignored", "label": "Gates ignored"},
        ],
    }),
    ("GOV-O4", {
        "text": "Is there a test leadership development path?",
        "category": "governance", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 0.60,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("GOV-O5", {
        "text": "Are test-related decisions documented?",
        "category": "governance", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "never", "label": "Never"},
            {"value": "sometimes", "label": "Sometimes"},
            {"value": "usually", "label": "Usually"},
            {"value": "always", "label": "Always"},
        ],
    }),

    # ===== TEST STRATEGY =====

    ("TST-C1", {
        "text": "Is there a documented test strategy?",
        "category": "test_strategy", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.65,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "informal", "label": "Informal"},
            {"value": "documented", "label": "Documented"},
            {"value": "approved_maintained", "label": "Approved & maintained"},
        ],
    }),
    ("TST-C2", {
        "text": "Is the test approach risk-based?",
        "category": "test_strategy", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.50,
        "options": [
            {"value": "no", "label": "No"},
            {"value": "partially", "label": "Partially"},
            {"value": "yes_business_input", "label": "Yes, with business input"},
            {"value": "quantified_risk_model", "label": "Quantified risk model"},
        ],
    }),
    ("TST-C3", {
        "text": "Is there a documented automation strategy?",
        "category": "test_strategy", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 1.00,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("TST-C4", {
        "text": "Is test estimation based on historical data?",
        "category": "test_strategy", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "no", "label": "No"},
            {"value": "guesswork", "label": "Guesswork"},
            {"value": "some_data", "label": "Some data"},
            {"value": "data_driven", "label": "Data-driven model"},
        ],
    }),
    ("TST-O1", {
        "text": "Test type balance (functional, NFR, integration, regression)?",
        "category": "test_strategy", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "single_type", "label": "Single type only"},
            {"value": "some_types", "label": "Some types"},
            {"value": "most_types", "label": "Most types"},
            {"value": "comprehensive", "label": "Comprehensive"},
        ],
    }),
    ("TST-O2", {
        "text": "What level of requirements coverage do tests achieve?",
        "category": "test_strategy", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.50,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "minimal", "label": "Minimal (key areas only)"},
            {"value": "partial", "label": "Partial (major requirements)"},
            {"value": "good", "label": "Good (most requirements)"},
            {"value": "comprehensive", "label": "Comprehensive (nearly all)"},
        ],
    }),
    ("TST-O3", {
        "text": "What is the defect escape rate to production?",
        "category": "test_strategy", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.50,
        "scoring_order": DESCENDING,
        "options": [
            {"value": "high", "label": "High (>20%)"},
            {"value": "medium", "label": "Medium (10-20%)"},
            {"value": "low", "label": "Low (5-10%)"},
            {"value": "very_low", "label": "Very low (<5%)"},
        ],
    }),
    ("TST-O4", {
        "text": "Are test metrics collected and analysed?",
        "category": "test_strategy", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "basic", "label": "Basic counts"},
            {"value": "analysed", "label": "Analysed"},
            {"value": "actioned", "label": "Analysed and actioned"},
        ],
    }),
    ("TST-O5", {
        "text": "Is test execution aligned with release cycles?",
        "category": "test_strategy", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "no", "label": "No alignment"},
            {"value": "partial", "label": "Partial"},
            {"value": "aligned", "label": "Aligned"},
            {"value": "integrated", "label": "Fully integrated"},
        ],
    }),

    # ===== TEST ASSETS =====

    ("TAM-C1", {
        "text": "Is there a test suite health monitoring process?",
        "category": "test_assets", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 1.00,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("TAM-C2", {
        "text": "Is there a test retirement/pruning process?",
        "category": "test_assets", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 1.00,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("TAM-C3", {
        "text": "Is automation ROI measured or understood?",
        "category": "test_assets", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 1.00,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("TAM-O1", {
        "text": "What is the current automation state?",
        "category": "test_assets", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "scoring_order": CUSTOM,
        "value_scores": {
            "none": 0, "failing": 10, "struggling": 25,
            "some_manual": 50, "established": 100,
        },
        "options": [
            {"value": "none", "label": "None"},
            {"value": "some_manual", "label": "Some, mostly manual"},
            {"value": "established", "label": "Established"},
            {"value": "struggling", "label": "Struggling"},
            {"value": "failing", "label": "Failing/abandoned"},
        ],
    }),
    ("TAM-O2", {
        "text": "How often do tests fail intermittently (flakiness)?",
        "category": "test_assets", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "scoring_order": DESCENDING,
        "options": [
            {"value": "negligible", "label": "Negligible"},
            {"value": "low", "label": "Low (occasional flaky tests)"},
            {"value": "moderate", "label": "Moderate"},
            {"value": "high", "label": "High (frequent false failures)"},
            {"value": "severe", "label": "Severe (results unreliable)"},
        ],
    }),
    ("TAM-O3", {
        "text": "How much test effort goes to maintenance vs building new coverage?",
        "category": "test_assets", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.15,
        "scoring_order": DESCENDING,
        "options": [
            {"value": "mostly_new", "label": "Mostly new coverage"},
            {"value": "some_maintenance", "label": "Some maintenance"},
            {"value": "balanced", "label": "About balanced"},
            {"value": "mostly_maintenance", "label": "Mostly maintenance"},
            {"value": "almost_all_maintenance", "label": "Almost all maintenance"},
        ],
    }),
    ("TAM-O4", {
        "text": "Rate team trust in automation results",
        "category": "test_assets", "dimension": "operational",
        "type": TYPE_SLIDER, "weight": 1.65,
        "min": 1, "max": 10,
        "labels": {"min": "No trust, failures ignored", "max": "Full trust, drives decisions"},
    }),

    # ===== DEVELOPMENT PRACTICES =====

    ("DEV-C1", {
        "text": "Are coding standards defined and enforced?",
        "category": "development", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.30,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "defined", "label": "Defined"},
            {"value": "enforced_manual", "label": "Enforced manually"},
            {"value": "automated", "label": "Automated enforcement"},
        ],
    }),
    ("DEV-C2", {
        "text": "Is there a mandatory code review process?",
        "category": "development", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.15,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "optional", "label": "Optional"},
            {"value": "mandatory", "label": "Mandatory"},
            {"value": "mandatory_metrics", "label": "Mandatory with metrics"},
        ],
    }),
    ("DEV-C3", {
        "text": "Are unit testing expectations defined?",
        "category": "development", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.15,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "guidelines", "label": "Guidelines"},
            {"value": "targets", "label": "Targets"},
            {"value": "enforced_gates", "label": "Enforced coverage gates"},
        ],
    }),
    ("DEV-C4", {
        "text": "Is static analysis integrated in the pipeline?",
        "category": "development", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.15,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "adhoc", "label": "Ad-hoc"},
            {"value": "ci_integrated", "label": "CI integrated"},
            {"value": "blocking_gates", "label": "Blocking gates"},
        ],
    }),
    ("DEV-O1", {
        "text": "What proportion of code changes go through review?",
        "category": "development", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "few", "label": "A few"},
            {"value": "some", "label": "Some"},
            {"value": "most", "label": "Most"},
            {"value": "all", "label": "All or nearly all"},
        ],
    }),
    ("DEV-O2", {
        "text": "What is the unit test coverage level?",
        "category": "development", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.15,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "minimal", "label": "Minimal (critical paths only)"},
            {"value": "partial", "label": "Partial"},
            {"value": "good", "label": "Good"},
            {"value": "comprehensive", "label": "Comprehensive"},
        ],
    }),
    ("DEV-O3", {
        "text": "How reliable are builds?",
        "category": "development", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "mostly_failing", "label": "Mostly failing"},
            {"value": "unreliable", "label": "Unreliable (frequent failures)"},
            {"value": "moderate", "label": "Moderate (occasional failures)"},
            {"value": "reliable", "label": "Reliable (rare failures)"},
            {"value": "very_reliable", "label": "Very reliable (nearly always pass)"},
        ],
    }),

    # ===== ENVIRONMENT =====

    ("ENV-C1", {
        "text": "Is there a test data strategy (classification, obfuscation, refresh)?",
        "category": "environment", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "adhoc", "label": "Ad-hoc"},
            {"value": "defined", "label": "Defined"},
            {"value": "comprehensive", "label": "Comprehensive"},
        ],
    }),
    ("ENV-C2", {
        "text": "What is the configuration management approach?",
        "category": "environment", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "manual", "label": "Manual"},
            {"value": "scripts", "label": "Scripts"},
            {"value": "iac_basic", "label": "IaC basic"},
            {"value": "iac_mature", "label": "IaC mature with CI/CD"},
        ],
    }),
    ("ENV-C3", {
        "text": "What is the deployment model?",
        "category": "environment", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.0,
        "scoring_order": UNSCORED,
        "options": [
            {"value": "onprem", "label": "On-premises"},
            {"value": "cloud", "label": "Cloud"},
            {"value": "hybrid", "label": "Hybrid"},
            {"value": "edge", "label": "Edge"},
        ],
    }),
    ("ENV-O1", {
        "text": "Rate test environment quality (production-likeness)",
        "category": "environment", "dimension": "operational",
        "type": TYPE_SLIDER, "weight": 0.75,
        "min": 1, "max": 10,
        "labels": {"min": "Poor - nothing like production", "max": "Production-like"},
    }),
    ("ENV-O2", {
        "text": "Rate environment parity (dev/test/prod similarity)",
        "category": "environment", "dimension": "operational",
        "type": TYPE_SLIDER, "weight": 0.60,
        "min": 1, "max": 10,
        "labels": {"min": "Very different", "max": "Identical"},
    }),
    ("ENV-O3", {
        "text": "Rate DevOps/CI-CD maturity",
        "category": "environment", "dimension": "capability",
        "type": TYPE_SLIDER, "weight": 1.15,
        "min": 1, "max": 10,
        "labels": {"min": "Ad-hoc", "max": "Fully automated"},
    }),
    ("ENV-O4", {
        "text": "Rate deployment consistency and reliability",
        "category": "environment", "dimension": "operational",
        "type": TYPE_SLIDER, "weight": 1.15,
        "min": 1, "max": 10,
        "labels": {"min": "Frequent failures", "max": "Highly reliable"},
    }),
    ("ENV-O5", {
        "text": "How well is test data managed and refreshed?",
        "category": "environment", "dimension": "operational",
        "type": TYPE_SLIDER, "weight": 0.60,
        "min": 1, "max": 10,
        "labels": {"min": "No management", "max": "Fully automated"},
    }),

    # ===== REQUIREMENTS =====

    ("REQ-C1", {
        "text": "Is there a defined requirements elicitation process?",
        "category": "requirements", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.50,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "adhoc", "label": "Ad-hoc"},
            {"value": "defined", "label": "Defined"},
            {"value": "managed", "label": "Managed"},
            {"value": "optimised", "label": "Optimised"},
        ],
    }),
    ("REQ-C2", {
        "text": "Are acceptance criteria defined for requirements?",
        "category": "requirements", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "never", "label": "Never"},
            {"value": "sometimes", "label": "Sometimes"},
            {"value": "usually", "label": "Usually"},
            {"value": "always_signoff", "label": "Always with sign-off"},
        ],
    }),
    ("REQ-C3", {
        "text": "Is there a traceability mechanism (requirements to tests to defects)?",
        "category": "requirements", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.50,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "partial", "label": "Partial"},
            {"value": "full_manual", "label": "Full manual"},
            {"value": "tooled", "label": "Tooled"},
        ],
    }),
    ("REQ-O1", {
        "text": "What proportion of requirements have acceptance criteria?",
        "category": "requirements", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.50,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "few", "label": "A few"},
            {"value": "some", "label": "Some"},
            {"value": "most", "label": "Most"},
            {"value": "all", "label": "All or nearly all"},
        ],
    }),
    ("REQ-O2", {
        "text": "How much do requirements change during development?",
        "category": "requirements", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60,
        "scoring_order": DESCENDING,
        "options": [
            {"value": "stable", "label": "Very stable (minimal changes)"},
            {"value": "low", "label": "Low churn (occasional changes)"},
            {"value": "moderate", "label": "Moderate churn (regular changes)"},
            {"value": "high", "label": "High churn (frequent changes)"},
            {"value": "chaotic", "label": "Chaotic (constant flux)"},
        ],
    }),

    # ===== CHANGE MANAGEMENT =====

    ("CHG-C1", {
        "text": "Is there a baseline management process?",
        "category": "change_management", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "adhoc", "label": "Ad-hoc"},
            {"value": "defined", "label": "Defined"},
            {"value": "controlled", "label": "Controlled"},
        ],
    }),
    ("CHG-C2", {
        "text": "Is there a scope change control process?",
        "category": "change_management", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "informal", "label": "Informal"},
            {"value": "formal", "label": "Formal"},
            {"value": "gate_controlled", "label": "Gate-controlled"},
        ],
    }),
    ("CHG-C3", {
        "text": "Is there a release management process?",
        "category": "change_management", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "adhoc", "label": "Ad-hoc"},
            {"value": "defined", "label": "Defined"},
            {"value": "automated", "label": "Automated"},
        ],
    }),
    ("CHG-O1", {
        "text": "What is the scope change volume this period?",
        "category": "change_management", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "scoring_order": DESCENDING,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "low", "label": "Low"},
            {"value": "medium", "label": "Medium"},
            {"value": "high", "label": "High"},
            {"value": "chaotic", "label": "Chaotic"},
        ],
    }),
    ("CHG-O2", {
        "text": "Rate build reproducibility confidence",
        "category": "change_management", "dimension": "operational",
        "type": TYPE_SLIDER, "weight": 0.60,
        "min": 1, "max": 10,
        "labels": {"min": "Unreliable", "max": "Fully reproducible"},
    }),

    # ===== FEEDBACK & METRICS =====

    ("FBK-C1", {
        "text": "Is there a defect tracking and classification process?",
        "category": "feedback", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "basic", "label": "Basic tracking"},
            {"value": "classified", "label": "Classified by type/severity"},
            {"value": "analysed", "label": "Analysed with root cause"},
        ],
    }),
    ("FBK-O1", {
        "text": "How effective is defect containment (catching defects before production)?",
        "category": "feedback", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "very_low", "label": "Very low (most escape)"},
            {"value": "low", "label": "Low"},
            {"value": "moderate", "label": "Moderate"},
            {"value": "high", "label": "High"},
            {"value": "very_high", "label": "Very high (nearly all caught)"},
        ],
    }),
    ("FBK-O2", {
        "text": "How often are metrics reviewed and acted upon?",
        "category": "feedback", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "never", "label": "Never"},
            {"value": "rarely", "label": "Rarely"},
            {"value": "regularly", "label": "Regularly"},
            {"value": "continuously", "label": "Continuously with actions"},
        ],
    }),

    # ===== ARCHITECTURE =====

    ("ARC-C1", {
        "text": "What type of system architecture does this project use?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.0,
        "scoring_order": UNSCORED,
        "options": [
            {"value": "monolith", "label": "Monolith"},
            {"value": "layered", "label": "Layered"},
            {"value": "microservices", "label": "Microservices"},
            {"value": "distributed", "label": "Distributed"},
            {"value": "embedded", "label": "Embedded"},
            {"value": "hybrid", "label": "Hybrid"},
        ],
    }),
    ("ARC-C2", {
        "text": "Was testability explicitly designed into the architecture?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 0.60,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("ARC-C3", {
        "text": "Rate how well components can be tested in isolation",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_SLIDER, "weight": 0.60,
        "min": 1, "max": 10,
        "labels": {"min": "Tightly coupled", "max": "Fully isolated"},
    }),
    ("ARC-C4", {
        "text": "Is there a technical debt tracking process?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 0.60,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("ARC-C5", {
        "text": "Does the project involve legacy code/systems?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 0.60,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("ARC-O1", {
        "text": "Rate overall architectural complexity",
        "category": "architecture", "dimension": "operational",
        "type": TYPE_SLIDER, "weight": 0.60,
        "min": 1, "max": 10, "inverse": True,
        "labels": {"min": "Simple", "max": "Highly complex"},
    }),
    ("ARC-O2", {
        "text": "Rate system observability and logging maturity",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_SLIDER, "weight": 0.60,
        "min": 1, "max": 10,
        "labels": {"min": "Poor", "max": "Comprehensive"},
    }),

    # ===== ARCHITECTURE — CONDITIONAL (legacy sub-questions) =====

    ("ARC-C5a", {
        "text": "Is there a legacy modernisation plan?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 0.60, "conditional": True,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("ARC-C5b", {
        "text": "How much of the codebase is legacy?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "options": [
            {"value": "minimal", "label": "Minimal (< 10%)"},
            {"value": "some", "label": "Some (10\u201330%)"},
            {"value": "significant", "label": "Significant (30\u201360%)"},
            {"value": "majority", "label": "Majority (60\u201385%)"},
            {"value": "almost_all", "label": "Almost all (85%+)"},
        ],
    }),
    ("ARC-C5c", {
        "text": "Is there documentation for legacy components?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "partial", "label": "Partial"},
            {"value": "complete", "label": "Complete"},
        ],
    }),

    # ===== OPS READINESS =====

    ("OPS-C1", {
        "text": "Is there a defined support model (L1/L2/L3, SLAs)?",
        "category": "ops_readiness", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "basic", "label": "Basic"},
            {"value": "defined", "label": "Defined"},
            {"value": "comprehensive", "label": "Comprehensive"},
        ],
    }),
    ("OPS-C2", {
        "text": "Is there an operational readiness testing approach (DR, rollback, backup)?",
        "category": "ops_readiness", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "adhoc", "label": "Ad-hoc"},
            {"value": "planned", "label": "Planned"},
            {"value": "comprehensive", "label": "Comprehensive with rehearsals"},
        ],
    }),
    ("OPS-C3", {
        "text": "Is there a training/handover process?",
        "category": "ops_readiness", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 1.00,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("OPS-O1", {
        "text": "Rate documentation completeness (runbooks, support guides)",
        "category": "ops_readiness", "dimension": "capability",
        "type": TYPE_SLIDER, "weight": 1.00,
        "min": 1, "max": 10,
        "labels": {"min": "None", "max": "Comprehensive"},
    }),
    ("OPS-O2", {
        "text": "What are the DR/rollback test results?",
        "category": "ops_readiness", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.15,
        "options": [
            {"value": "not_tested", "label": "Not tested"},
            {"value": "failed", "label": "Failed"},
            {"value": "passed_issues", "label": "Passed with issues"},
            {"value": "clean_pass", "label": "Clean pass"},
        ],
    }),

    # ===== THIRD PARTY =====

    ("TPT-C1", {
        "text": "Is there a dependency identification/tracking process (SBOM)?",
        "category": "third_party", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "adhoc", "label": "Ad-hoc"},
            {"value": "documented", "label": "Documented"},
            {"value": "automated", "label": "Automated"},
        ],
    }),
    ("TPT-C2", {
        "text": "Do supplier contracts include quality provisions?",
        "category": "third_party", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "basic_slas", "label": "Basic SLAs"},
            {"value": "quality_metrics", "label": "Quality metrics"},
            {"value": "incentivised", "label": "Incentivised"},
        ],
    }),
    ("TPT-C3", {
        "text": "Is there a security assessment process for third parties?",
        "category": "third_party", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 1.15,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("TPT-C4", {
        "text": "Do suppliers provide test evidence before delivery?",
        "category": "third_party", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "never", "label": "Never"},
            {"value": "sometimes", "label": "Sometimes"},
            {"value": "usually", "label": "Usually"},
            {"value": "always_formal", "label": "Always formal"},
        ],
    }),
    ("TPT-O1", {
        "text": "How many external suppliers or vendors are involved?",
        "category": "third_party", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "few", "label": "Few (1\u20133)"},
            {"value": "several", "label": "Several (4\u20138)"},
            {"value": "many", "label": "Many (9\u201315)"},
            {"value": "extensive", "label": "Extensive (15+)"},
        ],
    }),
    ("TPT-O2", {
        "text": "How many critical third-party dependencies does the project have?",
        "category": "third_party", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "options": [
            {"value": "none", "label": "None"},
            {"value": "few", "label": "Few (1\u20133)"},
            {"value": "several", "label": "Several (4\u20138)"},
            {"value": "many", "label": "Many (9\u201315)"},
            {"value": "extensive", "label": "Extensive (15+)"},
        ],
    }),
    ("TPT-O3", {
        "text": "What proportion of defects originate from third-party suppliers?",
        "category": "third_party", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 1.00,
        "scoring_order": DESCENDING,
        "options": [
            {"value": "negligible", "label": "Negligible"},
            {"value": "low", "label": "Low"},
            {"value": "moderate", "label": "Moderate"},
            {"value": "high", "label": "High"},
            {"value": "dominant", "label": "Dominant (most defects)"},
        ],
    }),
    ("TPT-O4", {
        "text": "Rate level of control over integrated systems",
        "category": "third_party", "dimension": "operational",
        "type": TYPE_SLIDER, "weight": 1.00,
        "min": 1, "max": 10, "inverse": True,
        "labels": {"min": "Full control", "max": "No control"},
    }),

    # ===== DEFECT MANAGEMENT (HOLISTIC) =====

    ("PROPOSED-DFM-01", {
        "text": "How would you describe your defect management process maturity?",
        "category": "defect_management", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.65,
        "scoring_order": GAP,
        "gap_scoring": {
            "optimised": 0, "formal": 20, "defined": 40,
            "informal": 70, "none": 100,
        },
        "options": [
            {"value": "none", "label": "None — defects handled ad-hoc, no categorisation or tracking"},
            {"value": "informal", "label": "Informal — developers decide priority, basic tracking only"},
            {"value": "defined", "label": "Defined — regular triage, categorised by type/severity, some targets"},
            {"value": "formal", "label": "Formal — documented triage with severity definitions and targets"},
            {"value": "optimised", "label": "Optimised — metrics-driven triage with root cause analysis"},
        ],
    }),
    ("DFM-C-TARGETS", {
        "text": "Are release defect targets formally defined?",
        "category": "defect_management", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00, "conditional": True,
        "scoring_order": GAP,
        "gap_scoring": {
            "formal": 0, "defined": 25, "informal": 60, "none": 100,
        },
        "depends_on": {
            "question": "PROPOSED-DFM-01",
            "condition": "in",
            "value": ["defined", "formal", "optimised"],
        },
        "options": [
            {"value": "none", "label": "No release defect targets"},
            {"value": "informal", "label": "Informal understanding, nothing documented"},
            {"value": "defined", "label": "Yes — defined targets, informally agreed"},
            {"value": "formal", "label": "Yes — formal targets by severity with sign-off"},
        ],
    }),

    # ===== TEST PHASE PROGRESS (base capability questions only) =====

    ("TPP-O1", {
        "text": "Which project and test phases are active on this project?",
        "category": "test_phase_progress", "dimension": "operational",
        "type": TYPE_MULTISELECT, "weight": 0.0,
        "scoring_order": UNSCORED,
        "options": [
            {"value": "discovery", "label": "Discovery / Inception"},
            {"value": "requirements", "label": "Requirements Analysis"},
            {"value": "design", "label": "Design / Architecture"},
            {"value": "unit", "label": "Unit Testing"},
            {"value": "integration", "label": "Integration Testing"},
            {"value": "system", "label": "System Testing"},
            {"value": "e2e", "label": "End-to-End Testing"},
            {"value": "uat", "label": "User Acceptance Testing (UAT)"},
            {"value": "oat", "label": "Operational Acceptance Testing (OAT)"},
            {"value": "release", "label": "Release / Deployment"},
            {"value": "hypercare", "label": "Hypercare / Stabilisation"},
        ],
    }),
    ("TPP-C1", {
        "text": "Are entry and exit criteria defined for each test phase?",
        "category": "test_phase_progress", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "none", "label": "Not defined"},
            {"value": "some_phases", "label": "Defined for some phases"},
            {"value": "all_phases", "label": "Defined for all phases"},
            {"value": "enforced", "label": "Defined and enforced with metrics"},
        ],
    }),
    ("TPP-C2", {
        "text": "Are test blockers formally tracked and escalated?",
        "category": "test_phase_progress", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 0.60,
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("TPP-C3", {
        "text": "How is phase transition governance handled?",
        "category": "test_phase_progress", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "none", "label": "No formal transition process"},
            {"value": "informal", "label": "Informal review before moving on"},
            {"value": "formal", "label": "Formal go/no-go at each gate"},
            {"value": "automated", "label": "Automated gates with metric thresholds"},
        ],
    }),
    ("TPP-EC1", {
        "text": "Are formal entry/exit criteria defined for each test phase?",
        "category": "test_phase_progress", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60,
        "options": [
            {"value": "none", "label": "No criteria defined"},
            {"value": "informal", "label": "Informal understanding"},
            {"value": "defined", "label": "Defined but not enforced"},
            {"value": "enforced", "label": "Defined and enforced"},
        ],
    }),

    # ===== BRANCH: Life-Safety Regulatory =====

    ("RC-LS-01", {
        "text": "Is there a formal validation master plan?",
        "category": "life_safety", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 1.50, "conditional": True,
        "branch": "life_safety_regulatory",
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("RC-LS-02", {
        "text": "Are design controls (IEC 62304 / FDA design controls) implemented?",
        "category": "life_safety", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.50, "conditional": True,
        "branch": "life_safety_regulatory",
        "options": [
            {"value": "none", "label": "None"},
            {"value": "partial", "label": "Partial"},
            {"value": "full", "label": "Full"},
            {"value": "certified", "label": "Certified"},
        ],
    }),
    ("RC-LS-03", {
        "text": "Is there a CAPA (Corrective and Preventive Action) process?",
        "category": "life_safety", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.50, "conditional": True,
        "branch": "life_safety_regulatory",
        "options": [
            {"value": "none", "label": "None"},
            {"value": "informal", "label": "Informal"},
            {"value": "documented", "label": "Documented"},
            {"value": "integrated", "label": "Integrated"},
        ],
    }),
    ("RC-LS-04", {
        "text": "Software categorisation (safety class)?",
        "category": "life_safety", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.0, "conditional": True,
        "scoring_order": UNSCORED,
        "branch": "life_safety_regulatory",
        "options": [
            {"value": "class_a", "label": "Class A (no injury)"},
            {"value": "class_b", "label": "Class B (non-serious)"},
            {"value": "class_c", "label": "Class C (serious/death)"},
        ],
    }),
    ("RC-LS-05", {
        "text": "Is there 21 CFR Part 11 compliant audit trail?",
        "category": "life_safety", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 1.00, "conditional": True,
        "branch": "life_safety_regulatory",
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),

    # ===== BRANCH: Automotive Safety =====

    ("RC-AUTO-01", {
        "text": "What is the highest ASIL for this system?",
        "category": "automotive_safety", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.0, "conditional": True,
        "scoring_order": UNSCORED,
        "branch": "automotive_regulatory",
        "options": [
            {"value": "qm", "label": "QM (no safety requirements)"},
            {"value": "asil_a", "label": "ASIL A (lowest)"},
            {"value": "asil_b", "label": "ASIL B"},
            {"value": "asil_c", "label": "ASIL C"},
            {"value": "asil_d", "label": "ASIL D (highest)"},
            {"value": "mixed", "label": "Mixed ASILs"},
        ],
    }),
    ("RC-AUTO-02", {
        "text": "Status of the Safety Case / Safety Plan documentation?",
        "category": "automotive_safety", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.50, "conditional": True,
        "branch": "automotive_regulatory",
        "options": [
            {"value": "none", "label": "Not started"},
            {"value": "draft", "label": "Draft in progress"},
            {"value": "review", "label": "Under review"},
            {"value": "approved", "label": "Approved and maintained"},
            {"value": "certified", "label": "Externally assessed/certified"},
        ],
    }),
    ("RC-AUTO-03", {
        "text": "What ASPICE capability level is targeted?",
        "category": "automotive_safety", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "branch": "automotive_regulatory",
        "options": [
            {"value": "none", "label": "No ASPICE target"},
            {"value": "cl1", "label": "CL1 - Performed"},
            {"value": "cl2", "label": "CL2 - Managed"},
            {"value": "cl3", "label": "CL3 - Established"},
        ],
    }),
    ("RC-AUTO-04", {
        "text": "Most recent ASPICE assessment result?",
        "category": "automotive_safety", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.0, "conditional": True,
        "scoring_order": UNSCORED,
        "branch": "automotive_regulatory",
        "options": [
            {"value": "not_assessed", "label": "Not yet assessed"},
            {"value": "below_target", "label": "Below target level"},
            {"value": "at_target", "label": "At target level"},
            {"value": "above_target", "label": "Above target level"},
            {"value": "gaps_identified", "label": "Significant gaps identified"},
        ],
    }),
    ("RC-AUTO-05", {
        "text": "Is there a cybersecurity TARA per ISO/SAE 21434?",
        "category": "automotive_safety", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00, "conditional": True,
        "branch": "automotive_regulatory",
        "options": [
            {"value": "none", "label": "No TARA performed"},
            {"value": "partial", "label": "Partial / informal"},
            {"value": "complete", "label": "Complete TARA documented"},
            {"value": "maintained", "label": "TARA maintained throughout lifecycle"},
        ],
    }),
    ("RC-AUTO-06", {
        "text": "How is open source and third-party software tracked (SBOM)?",
        "category": "automotive_safety", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "branch": "automotive_regulatory",
        "options": [
            {"value": "none", "label": "No formal tracking"},
            {"value": "manual", "label": "Manual tracking / spreadsheet"},
            {"value": "tooled", "label": "Automated SBOM generation"},
            {"value": "integrated", "label": "Integrated with vulnerability monitoring"},
        ],
    }),
    ("RC-AUTO-07", {
        "text": "Is bidirectional traceability maintained from requirements to test results?",
        "category": "automotive_safety", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 1.00, "conditional": True,
        "branch": "automotive_regulatory",
        "options": [
            {"value": "none", "label": "No traceability"},
            {"value": "partial", "label": "Partial / forward-only"},
            {"value": "manual", "label": "Full bidirectional (manual)"},
            {"value": "tooled", "label": "Full bidirectional (tool-supported)"},
            {"value": "verified", "label": "Bidirectional with coverage analysis"},
        ],
    }),
    ("RC-AUTO-08", {
        "text": "Are suppliers required to demonstrate ASPICE compliance?",
        "category": "automotive_safety", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "branch": "automotive_regulatory",
        "options": [
            {"value": "none", "label": "No supplier quality requirements"},
            {"value": "contractual", "label": "Contractual requirements only"},
            {"value": "evidence", "label": "Require evidence of compliance"},
            {"value": "assessed", "label": "Conduct supplier assessments"},
            {"value": "joint", "label": "Joint development with shared processes"},
        ],
    }),

    # ===== BRANCH: Automation Diagnostics =====

    ("TAM-DX-01", {
        "text": "Primary cause of automation instability?",
        "category": "test_assets", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.0, "conditional": True,
        "scoring_order": UNSCORED,
        "branch": "automation_diagnostics",
        "options": [
            {"value": "environment", "label": "Environment issues"},
            {"value": "timing_sync", "label": "Timing/sync problems"},
            {"value": "test_data", "label": "Test data"},
            {"value": "locators", "label": "Locators/selectors"},
            {"value": "external_deps", "label": "External dependencies"},
            {"value": "architecture", "label": "Architecture"},
        ],
    }),
    ("TAM-DX-02", {
        "text": "How long has automation been in troubled state?",
        "category": "test_assets", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "scoring_order": DESCENDING,
        "branch": "automation_diagnostics",
        "options": [
            {"value": "under_3_months", "label": "Less than 3 months"},
            {"value": "3_to_6_months", "label": "3-6 months"},
            {"value": "6_to_12_months", "label": "6-12 months"},
            {"value": "over_1_year", "label": "Over 1 year"},
        ],
    }),
    ("TAM-DX-03", {
        "text": "Has there been a previous remediation attempt?",
        "category": "test_assets", "dimension": "operational",
        "type": TYPE_TOGGLE, "weight": 0.60, "conditional": True,
        "branch": "automation_diagnostics",
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("TAM-DX-04", {
        "text": "What proportion of test failures are properly investigated (vs dismissed as flaky)?",
        "category": "test_assets", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "branch": "automation_diagnostics",
        "options": [
            {"value": "none", "label": "None (all dismissed)"},
            {"value": "few", "label": "A few"},
            {"value": "some", "label": "Some"},
            {"value": "most", "label": "Most"},
            {"value": "all", "label": "All or nearly all"},
        ],
    }),
    ("TAM-DX-05", {
        "text": "Is there pressure to 'just make tests green'?",
        "category": "test_assets", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "scoring_order": DESCENDING,
        "branch": "automation_diagnostics",
        "options": [
            {"value": "none", "label": "None"},
            {"value": "some", "label": "Some"},
            {"value": "significant", "label": "Significant"},
            {"value": "overwhelming", "label": "Overwhelming"},
        ],
    }),
    ("TAM-DX-06", {
        "text": "Would starting fresh be considered?",
        "category": "test_assets", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.0, "conditional": True,
        "scoring_order": UNSCORED,
        "branch": "automation_diagnostics",
        "options": [
            {"value": "not_an_option", "label": "Not an option"},
            {"value": "last_resort", "label": "Last resort"},
            {"value": "under_consideration", "label": "Under consideration"},
            {"value": "preferred", "label": "Preferred"},
        ],
    }),

    # ===== BRANCH: Enterprise Scale Operations =====

    ("SC-ENT-01", {
        "text": "Is there a follow-the-sun support model?",
        "category": "enterprise_scale", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "branch": "enterprise_scale_ops",
        "options": [
            {"value": "no", "label": "No"},
            {"value": "planned", "label": "Planned"},
            {"value": "partial", "label": "Partial coverage"},
            {"value": "full_24_7", "label": "Full 24/7"},
        ],
    }),
    ("SC-ENT-02", {
        "text": "Are there regional data residency requirements?",
        "category": "enterprise_scale", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 0.60, "conditional": True,
        "branch": "enterprise_scale_ops",
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("SC-ENT-03", {
        "text": "Multi-region deployment architecture?",
        "category": "enterprise_scale", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.0, "conditional": True,
        "scoring_order": UNSCORED,
        "branch": "enterprise_scale_ops",
        "options": [
            {"value": "single_region", "label": "Single region"},
            {"value": "active_passive", "label": "Active-passive"},
            {"value": "active_active", "label": "Active-active"},
            {"value": "geo_distributed", "label": "Geo-distributed"},
        ],
    }),
    ("SC-ENT-04", {
        "text": "Release coordination across regions?",
        "category": "enterprise_scale", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.0, "conditional": True,
        "scoring_order": UNSCORED,
        "branch": "enterprise_scale_ops",
        "options": [
            {"value": "big_bang", "label": "Big bang"},
            {"value": "rolling", "label": "Rolling by region"},
            {"value": "feature_flags", "label": "Feature flags"},
            {"value": "independent", "label": "Independent"},
        ],
    }),
    ("SC-ENT-05", {
        "text": "Regional compliance variations tracked?",
        "category": "enterprise_scale", "dimension": "capability",
        "type": TYPE_TOGGLE, "weight": 0.60, "conditional": True,
        "branch": "enterprise_scale_ops",
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),

    # ===== BRANCH: Legacy System Complexity =====

    ("ARC-LG-01", {
        "text": "Legacy system role in project?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "scoring_order": DESCENDING,
        "branch": "legacy_complexity",
        "options": [
            {"value": "being_replaced", "label": "Being replaced"},
            {"value": "being_wrapped", "label": "Being wrapped"},
            {"value": "being_extended", "label": "Being extended"},
            {"value": "core_dependency", "label": "Core dependency"},
        ],
    }),
    ("ARC-LG-02", {
        "text": "Legacy system documentation quality?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_SLIDER, "weight": 0.60, "conditional": True,
        "branch": "legacy_complexity",
        "min": 1, "max": 10, "unit": "/10",
    }),
    ("ARC-LG-03", {
        "text": "Access to legacy system expertise?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "branch": "legacy_complexity",
        "options": [
            {"value": "none", "label": "None available"},
            {"value": "limited", "label": "Limited"},
            {"value": "constrained", "label": "Available but constrained"},
            {"value": "readily_available", "label": "Readily available"},
        ],
    }),
    ("ARC-LG-04", {
        "text": "Legacy system test coverage?",
        "category": "architecture", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "branch": "legacy_complexity",
        "options": [
            {"value": "unknown", "label": "Unknown"},
            {"value": "none", "label": "None"},
            {"value": "partial", "label": "Partial"},
            {"value": "comprehensive", "label": "Comprehensive"},
        ],
    }),

    # ===== BRANCH: Supplier Quality Deep-Dive =====

    ("TPT-SQ-01", {
        "text": "Is there a supplier quality scorecard?",
        "category": "third_party", "dimension": "operational",
        "type": TYPE_TOGGLE, "weight": 0.60, "conditional": True,
        "branch": "supplier_quality",
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("TPT-SQ-02", {
        "text": "Supplier integration testing approach?",
        "category": "third_party", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "branch": "supplier_quality",
        "options": [
            {"value": "none", "label": "None"},
            {"value": "ad_hoc", "label": "Ad-hoc"},
            {"value": "defined", "label": "Defined"},
            {"value": "contractual", "label": "Contractual requirement"},
        ],
    }),
    ("TPT-SQ-03", {
        "text": "Defect attribution to specific suppliers tracked?",
        "category": "third_party", "dimension": "operational",
        "type": TYPE_TOGGLE, "weight": 0.60, "conditional": True,
        "branch": "supplier_quality",
        "options": [{"value": True, "label": "Yes"}, {"value": False, "label": "No"}],
    }),
    ("TPT-SQ-04", {
        "text": "Remedies exercised for poor supplier quality?",
        "category": "third_party", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "branch": "supplier_quality",
        "options": [
            {"value": "none", "label": "None"},
            {"value": "informal", "label": "Informal escalation"},
            {"value": "formal", "label": "Formal process"},
            {"value": "penalties", "label": "Contract penalties applied"},
        ],
    }),

    # ===== BRANCH: Governance Authority Gap =====

    ("GOV-AG-01", {
        "text": "Why does test lead lack release authority?",
        "category": "governance", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.0, "conditional": True,
        "scoring_order": UNSCORED,
        "branch": "governance_authority_gap",
        "options": [
            {"value": "org_policy", "label": "Organisational policy"},
            {"value": "pm_preference", "label": "PM preference"},
            {"value": "not_requested", "label": "Not requested"},
            {"value": "previously_lost", "label": "Previously had but lost"},
        ],
    }),
    ("GOV-AG-02", {
        "text": "Has quality been overridden to meet deadlines?",
        "category": "governance", "dimension": "operational",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "scoring_order": DESCENDING,
        "branch": "governance_authority_gap",
        "options": [
            {"value": "never", "label": "Never"},
            {"value": "rarely", "label": "Rarely"},
            {"value": "sometimes", "label": "Sometimes"},
            {"value": "frequently", "label": "Frequently"},
        ],
    }),
    ("GOV-AG-03", {
        "text": "Is there executive sponsorship for quality?",
        "category": "governance", "dimension": "capability",
        "type": TYPE_SELECT, "weight": 0.60, "conditional": True,
        "branch": "governance_authority_gap",
        "options": [
            {"value": "none", "label": "None"},
            {"value": "nominal", "label": "Nominal"},
            {"value": "active", "label": "Active"},
            {"value": "strategic", "label": "Quality is strategic priority"},
        ],
    }),
])


# ---------------------------------------------------------------------------
# CATEGORIES — ordered assessment structure
# ---------------------------------------------------------------------------

CATEGORIES = OrderedDict([
    ("governance", {
        "name": "Governance",
        "description": "Test leadership, authority, and oversight",
        "capability_questions": ["GOV-C1", "GOV-C2", "GOV-C3", "GOV-C4"],
        "operational_questions": ["GOV-O1", "GOV-O2", "GOV-O3", "GOV-O4", "GOV-O5"],
        "branch_questions": ["GOV-AG-01", "GOV-AG-02", "GOV-AG-03"],
    }),
    ("test_strategy", {
        "name": "Test Strategy",
        "description": "Test approach, coverage, and design",
        "capability_questions": ["TST-C1", "TST-C2", "TST-C3", "TST-C4"],
        "operational_questions": ["TST-O1", "TST-O2", "TST-O3", "TST-O4", "TST-O5"],
    }),
    ("test_assets", {
        "name": "Test Assets",
        "description": "Test automation and asset management",
        "capability_questions": ["TAM-C1", "TAM-C2", "TAM-C3"],
        "operational_questions": ["TAM-O1", "TAM-O2", "TAM-O3", "TAM-O4"],
        "branch_questions": ["TAM-DX-01", "TAM-DX-02", "TAM-DX-03",
                             "TAM-DX-04", "TAM-DX-05", "TAM-DX-06"],
    }),
    ("development", {
        "name": "Development Practices",
        "description": "Code quality, reviews, and build practices",
        "capability_questions": ["DEV-C1", "DEV-C2", "DEV-C3", "DEV-C4"],
        "operational_questions": ["DEV-O1", "DEV-O2", "DEV-O3"],
    }),
    ("environment", {
        "name": "Environment",
        "description": "Test environments, CI/CD, and infrastructure",
        "capability_questions": ["ENV-C1", "ENV-C2", "ENV-C3"],
        "operational_questions": ["ENV-O1", "ENV-O2", "ENV-O3", "ENV-O4", "ENV-O5"],
    }),
    ("requirements", {
        "name": "Requirements",
        "description": "Requirements quality and traceability",
        "capability_questions": ["REQ-C1", "REQ-C2", "REQ-C3"],
        "operational_questions": ["REQ-O1", "REQ-O2"],
    }),
    ("change_management", {
        "name": "Change Management",
        "description": "Change control and release management",
        "capability_questions": ["CHG-C1", "CHG-C2", "CHG-C3"],
        "operational_questions": ["CHG-O1", "CHG-O2"],
    }),
    ("feedback", {
        "name": "Feedback & Metrics",
        "description": "Defect tracking and quality metrics",
        "capability_questions": ["FBK-C1"],
        "operational_questions": ["FBK-O1", "FBK-O2"],
    }),
    ("defect_management", {
        "name": "Defect Management",
        "description": "Defect triage, tracking, and release targets",
        "capability_questions": ["PROPOSED-DFM-01"],
        "operational_questions": [],
        "conditional_questions": ["DFM-C-TARGETS"],
    }),
    ("architecture", {
        "name": "Architecture",
        "description": "System architecture and testability",
        "capability_questions": ["ARC-C1", "ARC-C2", "ARC-C3", "ARC-C4", "ARC-C5"],
        "operational_questions": ["ARC-O1", "ARC-O2"],
        "conditional_questions": ["ARC-C5a", "ARC-C5b", "ARC-C5c"],
        "branch_questions": ["ARC-LG-01", "ARC-LG-02", "ARC-LG-03", "ARC-LG-04"],
    }),
    ("ops_readiness", {
        "name": "Ops Readiness",
        "description": "Operational readiness and support",
        "capability_questions": ["OPS-C1", "OPS-C2", "OPS-C3"],
        "operational_questions": ["OPS-O1", "OPS-O2"],
    }),
    ("third_party", {
        "name": "Third Party",
        "description": "Vendor and supplier management",
        "capability_questions": ["TPT-C1", "TPT-C2", "TPT-C3", "TPT-C4"],
        "operational_questions": ["TPT-O1", "TPT-O2", "TPT-O3", "TPT-O4"],
        "branch_questions": ["TPT-SQ-01", "TPT-SQ-02", "TPT-SQ-03", "TPT-SQ-04"],
    }),
    ("test_phase_progress", {
        "name": "Test Phase Progress",
        "description": "Active test phases, criteria, and governance",
        "capability_questions": ["TPP-O1", "TPP-C1", "TPP-C2", "TPP-C3", "TPP-EC1"],
        "operational_questions": [],
    }),
    # Branch-only categories (appear when triggered by context/answers)
    ("life_safety", {
        "name": "Life-Safety Compliance",
        "description": "FDA, HIPAA, and medical device regulatory compliance",
        "capability_questions": [],
        "operational_questions": [],
        "branch_questions": ["RC-LS-01", "RC-LS-02", "RC-LS-03", "RC-LS-04", "RC-LS-05"],
        "branch_only": True,
    }),
    ("automotive_safety", {
        "name": "Automotive Safety & Compliance",
        "description": "ISO 26262, ASPICE, cybersecurity (ISO 21434), and supply chain",
        "capability_questions": [],
        "operational_questions": [],
        "branch_questions": ["RC-AUTO-01", "RC-AUTO-02", "RC-AUTO-03", "RC-AUTO-04",
                             "RC-AUTO-05", "RC-AUTO-06", "RC-AUTO-07", "RC-AUTO-08"],
        "branch_only": True,
    }),
    ("enterprise_scale", {
        "name": "Enterprise Scale Operations",
        "description": "Multi-region deployment, data residency, and global coordination",
        "capability_questions": [],
        "operational_questions": [],
        "branch_questions": ["SC-ENT-01", "SC-ENT-02", "SC-ENT-03",
                             "SC-ENT-04", "SC-ENT-05"],
        "branch_only": True,
    }),
])


# ---------------------------------------------------------------------------
# CATEGORY DEPENDENCIES — answer-reactive question filtering
# ---------------------------------------------------------------------------

CATEGORY_DEPENDENCIES = [
    {
        "id": "CD-001",
        "description": "No suppliers — skip supplier management",
        "trigger": {"question_id": "TPT-O1", "operator": "equals", "value": "none"},
        "skip": ["TPT-C2", "TPT-C3", "TPT-C4", "TPT-O2", "TPT-O3", "TPT-O4"],
    },
    {
        "id": "CD-002",
        "description": "No automation — skip automation health",
        "trigger": {"question_id": "TAM-O1", "operator": "equals", "value": "none"},
        "skip": ["TAM-O2", "TAM-O3", "TAM-O4", "TAM-C1", "TAM-C2", "TAM-C3"],
    },
    {
        "id": "CD-003",
        "description": "No test lead — skip authority questions",
        "trigger": {"question_id": "GOV-C1", "operator": "equals", "value": False},
        "skip": ["GOV-C2", "GOV-O1", "GOV-O2"],
    },
    {
        "id": "CD-004",
        "description": "Legacy code — add legacy sub-questions",
        "trigger": {"question_id": "ARC-C5", "operator": "equals", "value": True},
        "add": ["ARC-C5a", "ARC-C5b", "ARC-C5c"],
    },
    {
        "id": "CD-006",
        "description": "No CI/CD — skip pipeline health",
        "trigger": {"question_id": "ENV-O3", "operator": "less_than", "value": 3},
        "skip": ["ENV-O4", "ENV-O5", "DEV-O3"],
    },
    {
        "id": "CD-007",
        "description": "No estimation data — skip metrics alignment",
        "trigger": {"question_id": "TST-C4", "operator": "equals", "value": "no"},
        "skip": ["TST-O4", "TST-O5"],
    },
    {
        "id": "CD-008",
        "description": "No leadership path — skip scaling questions",
        "trigger": {"question_id": "GOV-O4", "operator": "equals", "value": False},
        "skip": ["GOV-C4", "GOV-O5"],
    },
    {
        "id": "CD-DFM-GATE-NONE",
        "description": "No defect process — skip all detailed defect questions",
        "trigger": {"question_id": "PROPOSED-DFM-01", "operator": "equals",
                    "value": "none"},
        "skip": ["DFM-C-TARGETS"],
    },
    {
        "id": "CD-DFM-GATE-INFORMAL",
        "description": "Informal defect process — skip target questions",
        "trigger": {"question_id": "PROPOSED-DFM-01", "operator": "in",
                    "value": ["none", "informal"]},
        "skip": ["DFM-C-TARGETS"],
    },
    {
        "id": "CD-029",
        "description": "No test metrics — skip metrics review",
        "trigger": {"question_id": "TST-O4", "operator": "equals", "value": "none"},
        "skip": ["FBK-O2"],
    },
]


# ---------------------------------------------------------------------------
# SECOND-LEVEL BRANCHES — compound condition triggers
# ---------------------------------------------------------------------------

SECOND_LEVEL_BRANCHES = [
    {
        "id": "SLB-001",
        "branch_id": "life_safety_regulatory",
        "label": "Life-Safety Compliance Deep-Dive",
        "trigger": {
            "conditions": [{
                "context_field": "regulatory_standards",
                "operator": "contains_any",
                "value": ["fda", "hipaa", "iso_13485"],
            }],
        },
        "add": ["RC-LS-01", "RC-LS-02", "RC-LS-03", "RC-LS-04", "RC-LS-05"],
    },
    {
        "id": "SLB-002",
        "branch_id": "automation_diagnostics",
        "label": "Automation Diagnostics",
        "trigger": {
            "conditions": [{
                "question_id": "TAM-O1",
                "operator": "in",
                "value": ["struggling", "failing"],
            }],
        },
        "add": ["TAM-DX-01", "TAM-DX-02", "TAM-DX-03",
                "TAM-DX-04", "TAM-DX-05", "TAM-DX-06"],
    },
    {
        "id": "SLB-003",
        "branch_id": "enterprise_scale_ops",
        "label": "Enterprise Scale Operations",
        "trigger": {
            "conditions": [
                {"context_field": "scale", "operator": "equals", "value": "enterprise"},
                {"context_field": "geographic", "operator": "in",
                 "value": ["multinational", "global"]},
            ],
        },
        "add": ["SC-ENT-01", "SC-ENT-02", "SC-ENT-03", "SC-ENT-04", "SC-ENT-05"],
    },
    {
        "id": "SLB-004",
        "branch_id": "legacy_complexity",
        "label": "Legacy System Complexity",
        "trigger": {
            "conditions": [
                {"question_id": "ARC-C5b", "operator": "in",
                 "value": ["significant", "majority", "almost_all"]},
                {"question_id": "ARC-C5c", "operator": "equals", "value": "none"},
            ],
        },
        "add": ["ARC-LG-01", "ARC-LG-02", "ARC-LG-03", "ARC-LG-04"],
    },
    {
        "id": "SLB-005",
        "branch_id": "supplier_quality",
        "label": "Supplier Quality Deep-Dive",
        "trigger": {
            "conditions": [
                {"question_id": "TPT-O1", "operator": "in",
                 "value": ["several", "many", "extensive"]},
                {"question_id": "TPT-O3", "operator": "in",
                 "value": ["moderate", "high", "dominant"]},
            ],
        },
        "add": ["TPT-SQ-01", "TPT-SQ-02", "TPT-SQ-03", "TPT-SQ-04"],
    },
    {
        "id": "SLB-006",
        "branch_id": "governance_authority_gap",
        "label": "Governance Authority Gap",
        "trigger": {
            "conditions": [
                {"question_id": "GOV-C1", "operator": "equals", "value": True},
                {"question_id": "GOV-C2", "operator": "in",
                 "value": ["no", "escalate_only"]},
            ],
        },
        "add": ["GOV-AG-01", "GOV-AG-02", "GOV-AG-03"],
    },
    {
        "id": "SLB-007",
        "branch_id": "automotive_regulatory",
        "label": "Automotive Safety & Compliance Deep-Dive",
        "trigger": {
            "conditions": [{
                "context_field": "regulatory_standards",
                "operator": "contains_any",
                "value": ["iso_26262", "aspice", "iso_21434", "autosar"],
            }],
        },
        "add": ["RC-AUTO-01", "RC-AUTO-02", "RC-AUTO-03", "RC-AUTO-04",
                "RC-AUTO-05", "RC-AUTO-06", "RC-AUTO-07", "RC-AUTO-08"],
    },
]


# ---------------------------------------------------------------------------
# PROGRESSIVE DISCLOSURE — staged question revelation
# ---------------------------------------------------------------------------

PROGRESSIVE_DISCLOSURE = [
    {
        "id": "PD-001",
        "description": "Standard: capability before operational",
        "scope": "all_categories",
        "stages": [
            {"stage": 1, "dimension": "capability"},
            {"stage": 2, "dimension": "operational",
             "condition": {"stage_1_average_threshold": 30}},
        ],
        "skip_message": "Capability too low for operational assessment — "
                        "focus on building basics",
    },
    {
        "id": "PD-002",
        "description": "Test Assets: automation state first",
        "scope": "test_assets",
        "stages": [
            {"stage": 1, "questions": ["TAM-O1"]},
            {"stage": 2, "questions": ["TAM-C1", "TAM-C2", "TAM-C3"],
             "condition": {"question_id": "TAM-O1", "operator": "not_equals",
                           "value": "none"}},
            {"stage": 3, "questions": ["TAM-O2", "TAM-O3", "TAM-O4"],
             "condition": {"question_id": "TAM-O1", "operator": "in",
                           "value": ["established", "struggling", "failing"]}},
        ],
    },
    {
        "id": "PD-003",
        "description": "Governance: leadership first",
        "scope": "governance",
        "stages": [
            {"stage": 1, "questions": ["GOV-C1"]},
            {"stage": 2, "questions": ["GOV-C2", "GOV-C3"],
             "condition": {"question_id": "GOV-C1", "operator": "equals",
                           "value": True}},
            {"stage": 3, "questions": ["GOV-O1", "GOV-O2", "GOV-O3"],
             "condition": {"question_id": "GOV-C2", "operator": "not_equals",
                           "value": "no"}},
        ],
    },
    {
        "id": "PD-004",
        "description": "Third Party: supplier count first",
        "scope": "third_party",
        "stages": [
            {"stage": 1, "questions": ["TPT-O1"]},
            {"stage": 2, "questions": ["TPT-C1", "TPT-C2"],
             "condition": {"question_id": "TPT-O1", "operator": "not_equals",
                           "value": "none"}},
            {"stage": 3, "questions": ["TPT-C3", "TPT-C4", "TPT-O2", "TPT-O3", "TPT-O4"],
             "condition": {"question_id": "TPT-O1", "operator": "in",
                           "value": ["several", "many", "extensive"]}},
        ],
    },
]


# ---------------------------------------------------------------------------
# CONTEXT FILTERS — project-context-based question scope
# ---------------------------------------------------------------------------

CONTEXT_FILTERS = [
    {
        "id": "CF-002",
        "description": "Small scale — simplify environment",
        "trigger": {"context_field": "scale", "operator": "equals", "value": "small"},
        "keep_only": {"category": "environment",
                      "questions": ["ENV-C2", "ENV-O1", "ENV-O3"]},
    },
    {
        "id": "CF-004",
        "description": "Early phase — reduce operational questions",
        "trigger": {"context_field": "project_phase", "operator": "in",
                    "value": ["initiation", "planning"]},
        "reduce": {"dimension": "operational", "keep_percentage": 30},
    },
    {
        "id": "CF-005",
        "description": "Late phase — reduce capability questions",
        "trigger": {"context_field": "project_phase", "operator": "in",
                    "value": ["transition", "closure", "maintenance"]},
        "reduce": {"dimension": "capability", "keep_percentage": 50},
    },
    {
        "id": "CF-007",
        "description": "Enterprise — expand scale-sensitive categories",
        "trigger": {"context_field": "scale", "operator": "in",
                    "value": ["large", "enterprise"]},
        "expand": {"categories": ["third_party", "governance", "environment"]},
    },
]


# ---------------------------------------------------------------------------
# PHASE WEIGHTS — capability vs operational emphasis by project phase
# ---------------------------------------------------------------------------

PHASE_WEIGHTS = {
    "initiation":  {"capability": 0.90, "operational": 0.10},
    "planning":    {"capability": 0.80, "operational": 0.20},
    "execution":   {"capability": 0.50, "operational": 0.50},
    "maturation":  {"capability": 0.25, "operational": 0.75},
    "transition":  {"capability": 0.30, "operational": 0.70},
    "closure":     {"capability": 0.20, "operational": 0.80},
    "maintenance": {"capability": 0.40, "operational": 0.60},
}


# ---------------------------------------------------------------------------
# CONTEXT MODIFIERS — risk multipliers based on project context
# ---------------------------------------------------------------------------

CONTEXT_MODIFIERS = {
    "regulatory": {
        "none": 1.0, "gdpr": 1.2, "hipaa": 1.5, "pci_dss": 1.5,
        "sox": 1.4, "fda_21_cfr_11": 1.6, "iso_13485": 1.5,
        "iso_27001": 1.3, "iso_9001_certified": 1.2, "fedramp": 1.5,
        "iec_62443": 1.5, "other": 1.3,
        # Automotive
        "iso_26262": 1.5, "aspice": 1.3, "iso_21434": 1.4, "autosar": 1.3,
    },
    "audit_frequency": {
        "none": 0.0, "annual": 0.0, "bi_annual": 0.05,
        "quarterly": 0.1, "continuous": 0.2,
    },
    "scale": {
        "small": 0.8, "medium": 1.0, "large": 1.3, "enterprise": 1.5,
    },
    "delivery_model": {
        "waterfall": 1.1, "hybrid_traditional": 1.05, "hybrid_agile": 1.0,
        "agile": 0.95, "devops": 0.9, "v_model": 1.1,
    },
}


# ---------------------------------------------------------------------------
# SCORING CONSTANTS
# ---------------------------------------------------------------------------

# N/P/L/F normalisation midpoints (percentage)
NPLF_MIDPOINTS = {"N": 7.5, "P": 32.5, "L": 67.5, "F": 92.5}

# Maturity level definitions
MATURITY_LEVELS = {
    1: {"name": "Initial",       "min": 0,  "max": 20},
    2: {"name": "Managed",       "min": 20, "max": 40},
    3: {"name": "Defined",       "min": 40, "max": 60},
    4: {"name": "Quantitatively Managed", "min": 60, "max": 80},
    5: {"name": "Optimising",    "min": 80, "max": 100},
}

# Risk level thresholds (score as %)
RISK_LEVELS = [
    {"level": "low",       "min": 0,  "max": 20, "colour": "#22c55e"},
    {"level": "moderate",  "min": 20, "max": 40, "colour": "#eab308"},
    {"level": "high",      "min": 40, "max": 60, "colour": "#f97316"},
    {"level": "very_high", "min": 60, "max": 80, "colour": "#ef4444"},
    {"level": "extreme",   "min": 80, "max": 100, "colour": "#991b1b"},
]

# Diagnostic classification thresholds
DIAGNOSTIC = {
    "high_threshold": 60,
    "low_threshold": 50,
    "balanced_gap": 15,
    "divergence_gap": 20,
    "gap_severity": {"large": 25, "moderate": 10, "small": 0},
}


# ---------------------------------------------------------------------------
# QUESTION HELP — contextual hover explanations for each question
# ---------------------------------------------------------------------------
# Centralised help text mapping. Served via the API alongside question data.
# Each entry explains what the question is asking and why it matters for
# QA maturity assessment.

QUESTION_HELP: dict[str, str] = {

    # ===== GOVERNANCE =====
    "GOV-C1": (
        "A dedicated test lead provides focused quality oversight, ensures "
        "test strategy alignment, and acts as the quality advocate in project "
        "decisions."
    ),
    "GOV-C2": (
        "Release authority determines whether quality concerns can actually "
        "block a release, or if testing is advisory-only. Stronger authority "
        "correlates with fewer production escapes."
    ),
    "GOV-C3": (
        "Quality gates are formal checkpoints where work must meet specific "
        "criteria before progressing. Entry criteria define prerequisites; "
        "exit criteria define what 'done' means."
    ),
    "GOV-C4": (
        "The release decision-maker determines how much weight quality data "
        "carries. Test Manager-led decisions prioritise quality; "
        "business-pressure-driven decisions often bypass it."
    ),
    "GOV-O1": (
        "Earlier involvement means test considerations influence architecture "
        "and design. Late involvement leads to costly rework and testing that "
        "can only verify, not prevent, issues."
    ),
    "GOV-O2": (
        "Wider deployment of test leads ensures consistent quality standards "
        "and practices across the organisation, not just in flagship teams."
    ),
    "GOV-O3": (
        "Waivers indicate quality criteria being bypassed. Frequent waivers "
        "suggest gates exist on paper but don't drive real quality behaviour."
    ),
    "GOV-O4": (
        "A career development path for test professionals signals "
        "organisational commitment to quality as a discipline, improving "
        "retention and capability."
    ),
    "GOV-O5": (
        "Documentation of test decisions (scope changes, risk acceptance, "
        "approach choices) creates an audit trail and enables organisational "
        "learning."
    ),

    # ===== TEST STRATEGY =====
    "TST-C1": (
        "A test strategy defines the overall approach to testing \u2014 scope, "
        "techniques, environments, tools, and risk mitigation. Without one, "
        "testing is reactive and inconsistent."
    ),
    "TST-C2": (
        "Risk-based testing focuses effort on the highest-risk areas rather "
        "than testing everything equally. It optimises limited resources and "
        "catches the most impactful defects first."
    ),
    "TST-C3": (
        "An automation strategy defines what to automate, why, and how \u2014 "
        "preventing ad-hoc automation that becomes costly to maintain without "
        "delivering value."
    ),
    "TST-C4": (
        "Data-driven estimation uses past project metrics to predict test "
        "effort more accurately, reducing schedule overruns and unrealistic "
        "commitments."
    ),
    "TST-O1": (
        "A balanced test portfolio covers different risk types. Over-reliance "
        "on one test type (e.g. only functional) leaves blind spots in areas "
        "like performance, security, or integration."
    ),
    "TST-O2": (
        "Requirements coverage measures how much of the specified "
        "functionality is verified by tests. Low coverage means unknown areas "
        "of risk."
    ),
    "TST-O3": (
        "Defect escape rate measures the percentage of defects found in "
        "production versus pre-production. Lower rates indicate more "
        "effective testing."
    ),
    "TST-O4": (
        "Metrics like pass rates, defect trends, and coverage data enable "
        "evidence-based decisions. Without metrics, quality management "
        "relies on intuition."
    ),
    "TST-O5": (
        "Alignment ensures testing is integrated into the delivery rhythm "
        "rather than being a bottleneck or afterthought at the end of each "
        "cycle."
    ),

    # ===== TEST ASSETS =====
    "TAM-C1": (
        "Monitoring test suite health (pass rates, execution times, flakiness "
        "trends) catches degradation early before the suite becomes "
        "unreliable."
    ),
    "TAM-C2": (
        "Retiring obsolete or redundant tests keeps the suite lean and "
        "maintainable. Without pruning, suites grow unsustainably and slow "
        "down feedback cycles."
    ),
    "TAM-C3": (
        "Understanding the return on automation investment helps justify "
        "continued investment and identifies where automation delivers (or "
        "fails to deliver) value."
    ),
    "TAM-O1": (
        "Current automation health determines which follow-up questions are "
        "relevant. 'Struggling' or 'Failing' automation may need diagnostic "
        "investigation."
    ),
    "TAM-O2": (
        "Flaky tests erode trust in the test suite. Teams start ignoring "
        "failures, and real defects hide among false alarms."
    ),
    "TAM-O3": (
        "Heavy maintenance burden indicates fragile automation that consumes "
        "effort without extending protection. Healthy suites allow most "
        "effort on new coverage."
    ),
    "TAM-O4": (
        "Trust determines whether automation actually influences decisions. "
        "If teams don't trust results, automation exists but doesn't "
        "contribute to quality."
    ),

    # ===== DEVELOPMENT PRACTICES =====
    "DEV-C1": (
        "Coding standards reduce defect introduction at source. Enforcement "
        "(manual or automated) ensures consistency across the team."
    ),
    "DEV-C2": (
        "Code reviews catch defects, share knowledge, and enforce standards "
        "before code reaches testing. They are one of the most cost-effective "
        "quality practices."
    ),
    "DEV-C3": (
        "Defined expectations (guidelines, targets, or enforced gates) set "
        "the bar for developer-level testing and shift quality left."
    ),
    "DEV-C4": (
        "Static analysis tools catch code quality issues, security "
        "vulnerabilities, and common bugs automatically without executing "
        "the code."
    ),
    "DEV-O1": (
        "Coverage of code review indicates whether the process is universal "
        "or only applied to some changes, leaving gaps."
    ),
    "DEV-O2": (
        "Unit test coverage measures how much code has developer-level tests. "
        "Higher coverage catches more issues before integration."
    ),
    "DEV-O3": (
        "Build reliability indicates CI/CD pipeline health. Frequent failures "
        "waste time, delay feedback, and create 'cry wolf' fatigue."
    ),

    # ===== ENVIRONMENT =====
    "ENV-C1": (
        "A test data strategy ensures realistic, compliant, and refreshable "
        "data for testing. Poor test data is a common cause of invalid test "
        "results."
    ),
    "ENV-C2": (
        "Configuration management (manual to IaC) determines how reliably "
        "and quickly environments can be provisioned and maintained."
    ),
    "ENV-C3": (
        "The deployment model (on-premises, cloud, hybrid, edge) affects "
        "the testing approach, environment provisioning, and operational "
        "considerations."
    ),
    "ENV-O1": (
        "Production-like test environments reduce the risk of "
        "environment-specific defects escaping to production. Poor "
        "environments produce unreliable test results."
    ),
    "ENV-O2": (
        "Environment parity ensures that behaviour observed in testing "
        "accurately predicts production behaviour. Divergence introduces "
        "uncertainty."
    ),
    "ENV-O3": (
        "CI/CD maturity determines how quickly and reliably code changes "
        "flow from development through testing to production."
    ),
    "ENV-O4": (
        "Consistent, reliable deployments reduce the risk of "
        "deployment-related defects and enable faster release cycles."
    ),
    "ENV-O5": (
        "Regular data refresh prevents tests from becoming stale. Good "
        "management includes masking sensitive data and maintaining "
        "referential integrity."
    ),

    # ===== REQUIREMENTS =====
    "REQ-C1": (
        "A defined process for gathering requirements reduces ambiguity "
        "and ensures testing has clear, testable specifications to verify "
        "against."
    ),
    "REQ-C2": (
        "Acceptance criteria make requirements testable by defining "
        "specific, verifiable conditions that must be met."
    ),
    "REQ-C3": (
        "Traceability links requirements to their tests and associated "
        "defects, enabling coverage analysis and impact assessment when "
        "requirements change."
    ),
    "REQ-O1": (
        "Coverage of acceptance criteria indicates whether testability is "
        "universal or spotty. Gaps mean some features lack clear pass/fail "
        "definitions."
    ),
    "REQ-O2": (
        "Requirements churn increases rework and invalidates completed "
        "testing. High churn indicates planning issues or poor stakeholder "
        "alignment."
    ),

    # ===== CHANGE MANAGEMENT =====
    "CHG-C1": (
        "Baseline management controls the approved state of deliverables. "
        "Without it, testing against moving targets produces unreliable "
        "results."
    ),
    "CHG-C2": (
        "Change control ensures scope changes are assessed for impact on "
        "testing, timelines, and quality before being accepted."
    ),
    "CHG-C3": (
        "Release management coordinates the packaging, scheduling, and "
        "deployment of changes, ensuring testing is complete before release."
    ),
    "CHG-O1": (
        "High change volume disrupts test planning, invalidates completed "
        "work, and increases the risk of untested changes reaching "
        "production."
    ),
    "CHG-O2": (
        "Reproducible builds ensure that the same source code always "
        "produces the same binary. This is critical for reliable testing "
        "and deployment."
    ),

    # ===== FEEDBACK & METRICS =====
    "FBK-C1": (
        "Structured defect tracking enables trend analysis, root cause "
        "identification, and prioritisation. Without it, defects are "
        "managed reactively."
    ),
    "FBK-O1": (
        "Defect containment effectiveness measures the proportion of "
        "defects caught before production \u2014 a key indicator of testing "
        "effectiveness."
    ),
    "FBK-O2": (
        "Collecting metrics without reviewing them provides no value. "
        "Regular review with follow-up actions drives continuous "
        "improvement."
    ),

    # ===== DEFECT MANAGEMENT =====
    "PROPOSED-DFM-01": (
        "Defect management maturity ranges from ad-hoc handling to "
        "metrics-driven triage with root cause analysis. Higher maturity "
        "prevents recurring issues."
    ),
    "DFM-C-TARGETS": (
        "Release defect targets (e.g. zero critical, fewer than N "
        "high-severity) provide objective go/no-go criteria and prevent "
        "subjective release decisions."
    ),

    # ===== ARCHITECTURE =====
    "ARC-C1": (
        "Architecture type influences testing strategy \u2014 monoliths need "
        "end-to-end testing; microservices need contract and integration "
        "testing."
    ),
    "ARC-C2": (
        "Testability by design (dependency injection, observable interfaces, "
        "configurable components) dramatically reduces the cost of effective "
        "testing."
    ),
    "ARC-C3": (
        "Isolation testability indicates coupling levels. Tightly coupled "
        "systems require expensive, slow integration tests for even basic "
        "verification."
    ),
    "ARC-C4": (
        "Tracked technical debt can be managed and prioritised. Untracked "
        "debt accumulates silently until it causes quality failures."
    ),
    "ARC-C5": (
        "Legacy involvement triggers additional questions about "
        "documentation, modernisation plans, and expertise availability."
    ),
    "ARC-O1": (
        "Higher complexity increases the testing surface area and the "
        "likelihood of unexpected interactions between components."
    ),
    "ARC-O2": (
        "Observability (logging, monitoring, tracing) is essential for "
        "diagnosing production issues and understanding system behaviour "
        "during testing."
    ),

    # ===== ARCHITECTURE — CONDITIONAL (legacy) =====
    "ARC-C5a": (
        "A modernisation plan indicates active investment in reducing "
        "legacy risk, rather than accepting permanent technical debt."
    ),
    "ARC-C5b": (
        "Legacy proportion affects testing complexity \u2014 more legacy means "
        "more untested, undocumented code requiring careful regression "
        "management."
    ),
    "ARC-C5c": (
        "Legacy documentation quality determines how confidently teams "
        "can test and modify legacy code without introducing regressions."
    ),

    # ===== OPS READINESS =====
    "OPS-C1": (
        "A support model (L1/L2/L3, SLAs) defines how production issues "
        "are handled post-release, affecting operational quality."
    ),
    "OPS-C2": (
        "Operational readiness testing (disaster recovery, rollback, backup) "
        "validates that the system can be operated safely in production."
    ),
    "OPS-C3": (
        "Training and handover ensure operations teams can support the "
        "system effectively. Gaps here lead to operational incidents."
    ),
    "OPS-O1": (
        "Operational documentation enables consistent incident response "
        "and reduces dependency on specific individuals' knowledge."
    ),
    "OPS-O2": (
        "DR/rollback test results validate whether recovery procedures "
        "actually work when needed, rather than existing only on paper."
    ),

    # ===== THIRD PARTY =====
    "TPT-C1": (
        "Dependency tracking (including SBOM) ensures visibility of "
        "third-party components, their versions, and known vulnerabilities."
    ),
    "TPT-C2": (
        "Quality provisions in contracts set expectations for testing "
        "evidence, defect SLAs, and quality metrics from suppliers."
    ),
    "TPT-C3": (
        "Security assessment of third-party components protects against "
        "supply chain vulnerabilities being inherited into your system."
    ),
    "TPT-C4": (
        "Test evidence from suppliers (test reports, coverage data) gives "
        "confidence in delivered quality before integration."
    ),
    "TPT-O1": (
        "Supplier count affects coordination complexity, integration "
        "testing burden, and quality management overhead."
    ),
    "TPT-O2": (
        "Critical dependencies are those whose failure would impact your "
        "system. More critical dependencies mean more integration risk."
    ),
    "TPT-O3": (
        "High third-party defect rates indicate supplier quality issues "
        "that may need contractual remediation or additional integration "
        "testing."
    ),
    "TPT-O4": (
        "Less control over integrated systems means more reliance on "
        "contract-based quality assurance and more defensive integration "
        "testing."
    ),

    # ===== TEST PHASE PROGRESS =====
    "TPP-O1": (
        "Active phases determine which testing concerns are most relevant "
        "and help scope the assessment appropriately."
    ),
    "TPP-C1": (
        "Phase criteria ensure orderly progression \u2014 entry criteria prevent "
        "premature starts, exit criteria prevent premature sign-off."
    ),
    "TPP-C2": (
        "Formal blocker tracking ensures impediments to testing are visible "
        "to management and get resolved rather than silently delaying "
        "progress."
    ),
    "TPP-C3": (
        "Phase transition governance ensures quality criteria are met before "
        "moving to the next phase, preventing defects from accumulating."
    ),
    "TPP-EC1": (
        "Formal criteria provide objective evidence that a phase is ready "
        "to start or has been completed satisfactorily."
    ),

    # ===== BRANCH: Life-Safety Regulatory =====
    "RC-LS-01": (
        "A validation master plan is required by FDA and similar regulators "
        "to document the overall approach to validating computerised systems."
    ),
    "RC-LS-02": (
        "Design controls ensure that medical device software is developed "
        "with appropriate planning, verification, and validation at each "
        "stage."
    ),
    "RC-LS-03": (
        "CAPA (Corrective and Preventive Action) is a regulatory requirement "
        "for systematically addressing quality issues and preventing "
        "recurrence."
    ),
    "RC-LS-04": (
        "IEC 62304 safety classification (A/B/C) determines the rigour of "
        "development and testing required based on potential harm."
    ),
    "RC-LS-05": (
        "21 CFR Part 11 requires electronic records to have tamper-evident "
        "audit trails, electronic signatures, and access controls."
    ),

    # ===== BRANCH: Automotive Safety =====
    "RC-AUTO-01": (
        "ASIL (Automotive Safety Integrity Level) from ISO 26262 ranges "
        "from QM (no safety) to ASIL D (highest). Higher levels require "
        "more rigorous verification and validation."
    ),
    "RC-AUTO-02": (
        "The safety plan documents how ISO 26262 will be applied. Its "
        "maturity indicates how systematically safety is being managed."
    ),
    "RC-AUTO-03": (
        "ASPICE (Automotive SPICE) is a process assessment model. Higher "
        "capability levels indicate more mature and controlled development "
        "processes."
    ),
    "RC-AUTO-04": (
        "Assessment results show current process maturity against the "
        "target, identifying gaps that need remediation."
    ),
    "RC-AUTO-05": (
        "TARA (Threat Analysis and Risk Assessment) identifies cybersecurity "
        "threats and countermeasures required by ISO/SAE 21434."
    ),
    "RC-AUTO-06": (
        "SBOM tracking is increasingly required in automotive to manage "
        "supply chain security and ensure licence compliance."
    ),
    "RC-AUTO-07": (
        "Bidirectional traceability (requirements \u2194 design \u2194 tests \u2194 "
        "results) is mandatory in safety-critical development to demonstrate "
        "completeness."
    ),
    "RC-AUTO-08": (
        "Supply chain quality requirements ensure that outsourced components "
        "meet the same process standards as in-house development."
    ),

    # ===== BRANCH: Automation Diagnostics =====
    "TAM-DX-01": (
        "Identifying the root cause helps determine whether the fix is "
        "technical (locators, timing), infrastructure (environments), or "
        "process (data management)."
    ),
    "TAM-DX-02": (
        "Duration of instability indicates whether this is a recent "
        "regression (potentially fixable) or a chronic structural issue."
    ),
    "TAM-DX-03": (
        "Failed previous attempts suggest deeper architectural issues "
        "rather than simple configuration problems."
    ),
    "TAM-DX-04": (
        "Dismissing failures as 'flaky' without investigation allows real "
        "defects to escape and prevents root cause resolution."
    ),
    "TAM-DX-05": (
        "Pressure to suppress failures rather than fix them undermines test "
        "suite integrity and masks real quality issues."
    ),
    "TAM-DX-06": (
        "Sometimes a fresh start is more cost-effective than remediating "
        "deeply flawed automation. This gauges openness to that option."
    ),

    # ===== BRANCH: Enterprise Scale Operations =====
    "SC-ENT-01": (
        "Follow-the-sun provides continuous support coverage across time "
        "zones, important for globally deployed enterprise systems."
    ),
    "SC-ENT-02": (
        "Data residency requirements (GDPR, etc.) affect test data "
        "management, environment location, and deployment architecture."
    ),
    "SC-ENT-03": (
        "Deployment topology affects testing strategy \u2014 active-active and "
        "geo-distributed architectures require cross-region integration "
        "testing."
    ),
    "SC-ENT-04": (
        "Regional release coordination determines the complexity of "
        "deployment testing and rollback procedures."
    ),
    "SC-ENT-05": (
        "Different regions may have different regulatory requirements, "
        "requiring variant testing and compliance verification."
    ),

    # ===== BRANCH: Legacy System Complexity =====
    "ARC-LG-01": (
        "Whether the legacy system is being replaced, wrapped, extended, "
        "or depended upon determines the testing approach and risk level."
    ),
    "ARC-LG-02": (
        "Documentation quality determines how well the team can understand "
        "and safely test changes to legacy components."
    ),
    "ARC-LG-03": (
        "Expert availability is critical for understanding undocumented "
        "behaviour and making safe changes to legacy systems."
    ),
    "ARC-LG-04": (
        "Existing test coverage for legacy code determines how safely "
        "changes can be made without risking unknown regressions."
    ),

    # ===== BRANCH: Supplier Quality Deep-Dive =====
    "TPT-SQ-01": (
        "A scorecard objectively tracks supplier quality performance over "
        "time, enabling data-driven vendor management decisions."
    ),
    "TPT-SQ-02": (
        "Defined integration testing with suppliers ensures that interfaces "
        "work correctly before delivered components enter your system."
    ),
    "TPT-SQ-03": (
        "Attribution enables accountability and identifies which suppliers "
        "need quality improvement or closer oversight."
    ),
    "TPT-SQ-04": (
        "Available and exercised remedies (escalation, penalties) create "
        "incentives for suppliers to maintain quality standards."
    ),

    # ===== BRANCH: Governance Authority Gap =====
    "GOV-AG-01": (
        "Understanding the reason (policy, preference, not requested) helps "
        "identify whether the gap is structural or can be addressed."
    ),
    "GOV-AG-02": (
        "Quality overrides indicate whether the lack of release authority "
        "has real consequences \u2014 frequent overrides suggest systemic risk."
    ),
    "GOV-AG-03": (
        "Executive sponsorship determines whether quality has organisational "
        "backing to push back against schedule pressure."
    ),
}
