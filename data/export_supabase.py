"""
Export research data from Supabase to CSV files.

Usage:
    cd data
    python export_supabase.py

Requires a .env file in the project root (.env):
    SUPABASE_URL=https://cssybivlexzgrqbsotla.supabase.co
    SUPABASE_KEY=<service_role key from Vercel>

Outputs:
    data/exports/assessments.csv
    data/exports/identifications.csv
    data/exports/feedback.csv
    data/exports/maturity_scores.csv
    data/exports/self_mappings.csv
    data/exports/practitioner_calibrations.csv
    data/exports/sessions_combined.csv   — joined view across all tables
    data/exports/summary.txt             — row counts and basic stats
"""

from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Load .env from project root
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass  # dotenv not installed — rely on environment variables

try:
    import httpx
except ImportError:
    print("httpx not installed. Run: pip install httpx")
    sys.exit(1)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing SUPABASE_URL or SUPABASE_KEY.")
    print("Create a .env file in the project root with:")
    print("  SUPABASE_URL=https://cssybivlexzgrqbsotla.supabase.co")
    print("  SUPABASE_KEY=<your service_role key>")
    sys.exit(1)

EXPORT_DIR = Path(__file__).resolve().parent / "exports"

# All 6 research tables
TABLES = [
    "assessments",
    "identifications",
    "feedback",
    "maturity_scores",
    "self_mappings",
    "practitioner_calibrations",
]


def fetch_table(table: str) -> list[dict]:
    """Fetch all rows from a Supabase table via PostgREST."""
    rows = []
    # PostgREST paginates at 1000 by default; use Range header for larger sets
    offset = 0
    page_size = 1000

    while True:
        resp = httpx.get(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Prefer": "count=exact",
                "Range": f"{offset}-{offset + page_size - 1}",
            },
            params={"order": "created_at.asc"},
            timeout=30.0,
        )
        resp.raise_for_status()
        page = resp.json()
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size

    return rows


def flatten_row(row: dict) -> dict:
    """Flatten JSON/dict columns into string representations for CSV."""
    flat = {}
    for key, value in row.items():
        if isinstance(value, (dict, list)):
            flat[key] = json.dumps(value, ensure_ascii=False)
        else:
            flat[key] = value
    return flat


def write_csv(path: Path, rows: list[dict]) -> int:
    """Write rows to a CSV file. Returns row count."""
    if not rows:
        path.write_text("(no data)\n", encoding="utf-8")
        return 0

    # Collect all keys across all rows (some rows may have different columns)
    all_keys = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                all_keys.append(key)
                seen.add(key)

    flat_rows = [flatten_row(r) for r in rows]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat_rows)

    return len(flat_rows)


def build_session_view(all_data: dict[str, list[dict]]) -> list[dict]:
    """
    Build a combined session-level view joining assessments with other tables.

    Each row represents one assessment session, with key fields from all tables
    joined by session_id. This is the primary analysis-ready export.
    """
    assessments = all_data.get("assessments", [])
    if not assessments:
        return []

    # Index other tables by session_id
    def index_by_session(rows):
        idx = {}
        for r in rows:
            sid = r.get("session_id")
            if sid:
                idx.setdefault(sid, []).append(r)
        return idx

    identifications = index_by_session(all_data.get("identifications", []))
    feedback_items = index_by_session(all_data.get("feedback", []))
    maturity = index_by_session(all_data.get("maturity_scores", []))
    self_maps = index_by_session(all_data.get("self_mappings", []))
    calibrations = index_by_session(all_data.get("practitioner_calibrations", []))

    combined = []
    for a in assessments:
        sid = a.get("session_id", "")
        row = {
            # Assessment core
            "session_id": sid,
            "created_at": a.get("created_at", ""),
            "flow_type": a.get("flow_type", ""),
            "archetype": a.get("archetype", ""),
            "match_distance": a.get("match_distance"),
            "confidence": a.get("confidence", ""),
            # Dimensions
            "d1_consequence": a.get("d1_consequence"),
            "d2_market": a.get("d2_market"),
            "d3_complexity": a.get("d3_complexity"),
            "d4_regulation": a.get("d4_regulation"),
            "d5_stability": a.get("d5_stability"),
            "d6_outsourcing": a.get("d6_outsourcing"),
            "d7_lifecycle": a.get("d7_lifecycle"),
            "d8_coherence": a.get("d8_coherence"),
            # Default sliders & position
            "slider_inv": a.get("slider_inv"),
            "slider_rec": a.get("slider_rec"),
            "slider_owk": a.get("slider_owk"),
            "slider_time": a.get("slider_time"),
            "default_cap": a.get("default_cap"),
            "default_ops": a.get("default_ops"),
            "assessed_cap": a.get("assessed_cap"),
            "assessed_ops": a.get("assessed_ops"),
            # Context
            "ctx_scale": a.get("ctx_scale", ""),
            "ctx_delivery": a.get("ctx_delivery", ""),
            "ctx_stage": a.get("ctx_stage", ""),
            "ctx_phase": a.get("ctx_phase", ""),
            "ctx_regulatory": json.dumps(a.get("ctx_regulatory", [])),
            "ctx_audit": a.get("ctx_audit", ""),
            "has_calibration_changes": a.get("has_calibration_changes", False),
            # Self-assessed capacity (front-loaded before questions)
            "self_inv": a.get("self_inv"),
            "self_rec": a.get("self_rec"),
            "self_owk": a.get("self_owk"),
            "self_time": a.get("self_time"),
            "respondent_role": a.get("respondent_role", ""),
        }

        # Maturity scores (first match)
        mat = (maturity.get(sid) or [None])[0]
        if mat:
            row["capability_pct"] = mat.get("capability_pct")
            row["operational_pct"] = mat.get("operational_pct")
            row["unified_pct"] = mat.get("unified_pct")
            row["questions_answered"] = mat.get("questions_answered")
            row["questions_visible"] = mat.get("questions_visible")
            row["answers_json"] = json.dumps(mat.get("answers_json", {}))
            row["category_scores_json"] = json.dumps(mat.get("category_scores_json", {}))
        else:
            row["capability_pct"] = None
            row["operational_pct"] = None
            row["unified_pct"] = None
            row["questions_answered"] = None
            row["questions_visible"] = None
            row["answers_json"] = ""
            row["category_scores_json"] = ""

        # Self-mapping (first match)
        sm = (self_maps.get(sid) or [None])[0]
        if sm:
            row["self_map_user_choice"] = sm.get("user_choice", "")
            row["self_map_none_match"] = sm.get("user_says_none_match", False)
            row["self_map_none_desc"] = sm.get("none_match_description", "")
            row["system_match"] = sm.get("system_match", "")
            row["system_distance"] = sm.get("system_distance")
            row["system_confidence"] = sm.get("system_confidence", "")
            # Key research metric: did user agree with system?
            row["user_agrees_with_system"] = (
                sm.get("user_choice", "") == sm.get("system_match", "")
                if sm.get("user_choice") else None
            )
        else:
            row["self_map_user_choice"] = ""
            row["self_map_none_match"] = None
            row["self_map_none_desc"] = ""
            row["system_match"] = ""
            row["system_distance"] = None
            row["system_confidence"] = ""
            row["user_agrees_with_system"] = None

        # Identification
        ident = (identifications.get(sid) or [None])[0]
        if ident:
            row["id_type"] = ident.get("id_type", "")
            row["persona_name"] = ident.get("persona_name", "")
            row["new_label"] = ident.get("new_label", "")
            row["new_description"] = ident.get("new_description", "")
        else:
            row["id_type"] = ""
            row["persona_name"] = ""
            row["new_label"] = ""
            row["new_description"] = ""

        # Feedback
        fb = (feedback_items.get(sid) or [None])[0]
        if fb:
            row["feedback_text"] = fb.get("feedback_text", "")
            row["rating"] = fb.get("rating")
            row["display_name"] = fb.get("display_name", "")
            row["category_notes_json"] = json.dumps(fb.get("category_notes_json", {}))
        else:
            row["feedback_text"] = ""
            row["rating"] = None
            row["display_name"] = ""
            row["category_notes_json"] = ""

        # Calibration count
        cals = calibrations.get(sid, [])
        row["calibration_count"] = len(cals)
        if cals:
            # Summarise: max slider deviation across all calibrations
            max_dev = 0.0
            for cal in cals:
                for s in ["inv", "rec", "owk", "time"]:
                    d = abs((cal.get(f"adjusted_{s}") or 0) - (cal.get(f"default_{s}") or 0))
                    max_dev = max(max_dev, d)
            row["max_slider_deviation"] = round(max_dev, 4)
        else:
            row["max_slider_deviation"] = None

        combined.append(row)

    return combined


def print_summary(all_data: dict[str, list[dict]], combined: list[dict]) -> str:
    """Generate a text summary of the exported data."""
    lines = []
    lines.append(f"Cap/Ops Research Data Export — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)
    lines.append("")

    # Row counts
    lines.append("Table Row Counts:")
    for table in TABLES:
        lines.append(f"  {table:35s} {len(all_data.get(table, [])):>5d}")
    lines.append(f"  {'sessions_combined':35s} {len(combined):>5d}")
    lines.append("")

    # Assessment breakdown
    assessments = all_data.get("assessments", [])
    if assessments:
        lines.append("Assessment Breakdown:")

        # By flow type
        flow_counts = {}
        for a in assessments:
            ft = a.get("flow_type", "unknown")
            flow_counts[ft] = flow_counts.get(ft, 0) + 1
        for ft, count in sorted(flow_counts.items()):
            lines.append(f"  Flow type '{ft}': {count}")

        # By archetype
        arch_counts = {}
        for a in assessments:
            arch = a.get("archetype", "unknown")
            arch_counts[arch] = arch_counts.get(arch, 0) + 1
        lines.append("")
        lines.append("  Archetype distribution:")
        for arch, count in sorted(arch_counts.items(), key=lambda x: -x[1]):
            lines.append(f"    {arch:40s} {count:>3d}")
        lines.append("")

    # Self-mapping agreement rate
    self_maps = all_data.get("self_mappings", [])
    if self_maps:
        total = len(self_maps)
        agreed = sum(
            1 for sm in self_maps
            if sm.get("user_choice") and sm.get("user_choice") == sm.get("system_match")
        )
        none_match = sum(1 for sm in self_maps if sm.get("user_says_none_match"))
        lines.append(f"Self-Mapping Results ({total} total):")
        lines.append(f"  User agreed with system: {agreed} ({100*agreed/total:.0f}%)")
        lines.append(f"  User said 'none match':  {none_match}")
        lines.append("")

    # Calibration summary
    cals = all_data.get("practitioner_calibrations", [])
    if cals:
        lines.append(f"Practitioner Calibrations ({len(cals)} total):")
        triggers = {}
        for c in cals:
            t = c.get("trigger", "unknown")
            triggers[t] = triggers.get(t, 0) + 1
        for t, count in sorted(triggers.items()):
            lines.append(f"  Trigger '{t}': {count}")

        # Average slider deviations
        devs = {s: [] for s in ["inv", "rec", "owk", "time"]}
        for c in cals:
            for s in devs:
                adj = c.get(f"adjusted_{s}")
                dflt = c.get(f"default_{s}")
                if adj is not None and dflt is not None:
                    devs[s].append(adj - dflt)
        lines.append("  Mean slider deviations (adjusted - default):")
        for s, vals in devs.items():
            if vals:
                mean = sum(vals) / len(vals)
                lines.append(f"    {s:6s}: {mean:+.4f}")
        lines.append("")

    # Feedback
    fbs = all_data.get("feedback", [])
    if fbs:
        ratings = [f.get("rating") for f in fbs if f.get("rating") is not None]
        lines.append(f"Feedback ({len(fbs)} entries):")
        if ratings:
            lines.append(f"  Mean rating: {sum(ratings)/len(ratings):.1f} / 5")
        with_text = sum(1 for f in fbs if f.get("feedback_text"))
        lines.append(f"  With text:   {with_text}")
        lines.append("")

    return "\n".join(lines)


def main():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Connecting to {SUPABASE_URL} ...")
    print()

    all_data = {}
    for table in TABLES:
        print(f"  Fetching {table}...", end=" ", flush=True)
        try:
            rows = fetch_table(table)
            all_data[table] = rows
            count = write_csv(EXPORT_DIR / f"{table}.csv", rows)
            print(f"{count} rows")
        except Exception as e:
            print(f"ERROR: {e}")
            all_data[table] = []

    # Build combined session view
    print()
    print("  Building combined session view...", end=" ", flush=True)
    combined = build_session_view(all_data)
    count = write_csv(EXPORT_DIR / "sessions_combined.csv", combined)
    print(f"{count} sessions")

    # Summary
    summary = print_summary(all_data, combined)
    (EXPORT_DIR / "summary.txt").write_text(summary, encoding="utf-8")
    print()
    print(summary)
    print()
    print(f"Exported to: {EXPORT_DIR}")


if __name__ == "__main__":
    main()
