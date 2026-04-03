"""Research data export — CSV and JSON formats for clinical analysis."""

import csv
import json
from datetime import datetime
from pathlib import Path

from .memory import list_patients, load_patient, DATA_DIR
from .session import list_sessions, load_session, SESSION_DIR

EXPORT_DIR = Path(__file__).parent.parent / "data" / "exports"


def ensure_export_dir():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def export_patient_trajectories(output_path=None):
    """Export longitudinal assessment data across all patients.

    Creates a CSV with one row per assessment per patient, suitable for
    tracking changes over time in clinical research.

    Columns: patient_id, date, assessment_type, score, max_score, interpretation, details
    """
    ensure_export_dir()
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = EXPORT_DIR / f"assessment_trajectories_{timestamp}.csv"

    rows = []
    for p_summary in list_patients():
        profile = load_patient(p_summary["patient_id"])
        if not profile:
            continue
        demo = profile.get("demographics", {})
        for assessment in profile.get("assessments", []):
            rows.append({
                "patient_id": profile["patient_id"],
                "age": demo.get("age", ""),
                "sex": demo.get("sex", ""),
                "conditions": "|".join(demo.get("conditions", [])),
                "date": assessment.get("date", ""),
                "assessment_type": assessment.get("type", ""),
                "score": assessment.get("score", ""),
                "max_score": assessment.get("max_score", ""),
                "interpretation": assessment.get("interpretation", ""),
                "details": json.dumps(assessment.get("details", {}))
            })

    if not rows:
        print("  No assessment data to export.")
        return None

    fieldnames = ["patient_id", "age", "sex", "conditions", "date",
                  "assessment_type", "score", "max_score", "interpretation", "details"]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Exported {len(rows)} assessment records to {output_path}")
    return output_path


def export_goal_adherence(output_path=None):
    """Export goal adherence data across all patients.

    Creates a CSV with one row per check-in per goal per patient.

    Columns: patient_id, goal_id, pillar, description, target, status,
             check_in_date, adherence, notes
    """
    ensure_export_dir()
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = EXPORT_DIR / f"goal_adherence_{timestamp}.csv"

    rows = []
    for p_summary in list_patients():
        profile = load_patient(p_summary["patient_id"])
        if not profile:
            continue
        for goal in profile.get("goals", []):
            check_ins = goal.get("check_ins", [])
            if not check_ins:
                # Still include the goal even without check-ins
                rows.append({
                    "patient_id": profile["patient_id"],
                    "goal_id": goal["id"],
                    "pillar": goal.get("pillar", ""),
                    "description": goal.get("description", ""),
                    "target": goal.get("target", ""),
                    "status": goal.get("status", ""),
                    "created_at": goal.get("created_at", "")[:10],
                    "check_in_date": "",
                    "adherence": "",
                    "notes": ""
                })
            else:
                for ci in check_ins:
                    rows.append({
                        "patient_id": profile["patient_id"],
                        "goal_id": goal["id"],
                        "pillar": goal.get("pillar", ""),
                        "description": goal.get("description", ""),
                        "target": goal.get("target", ""),
                        "status": goal.get("status", ""),
                        "created_at": goal.get("created_at", "")[:10],
                        "check_in_date": ci.get("date", ""),
                        "adherence": ci.get("adherence", ""),
                        "notes": ci.get("notes", "")
                    })

    if not rows:
        print("  No goal data to export.")
        return None

    fieldnames = ["patient_id", "goal_id", "pillar", "description", "target",
                  "status", "created_at", "check_in_date", "adherence", "notes"]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Exported {len(rows)} goal records to {output_path}")
    return output_path


def export_session_notes(output_path=None):
    """Export SOAP notes from all sessions.

    Creates a CSV with one row per session.

    Columns: session_id, patient_id, date, duration_min, exchange_count,
             subjective, objective, assessment, plan
    """
    ensure_export_dir()
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = EXPORT_DIR / f"session_notes_{timestamp}.csv"

    rows = []
    for session in list_sessions():
        soap = session.get("soap_note") or {}
        start = session.get("start_time", "")
        end = session.get("end_time", "")

        duration = ""
        if start and end:
            try:
                s = datetime.fromisoformat(start)
                e = datetime.fromisoformat(end)
                duration = round((e - s).total_seconds() / 60, 1)
            except (ValueError, TypeError):
                pass

        rows.append({
            "session_id": session["session_id"],
            "patient_id": session.get("patient_id", ""),
            "date": start[:10] if start else "",
            "start_time": start,
            "end_time": end,
            "duration_min": duration,
            "exchange_count": len(session.get("conversation", [])),
            "subjective": soap.get("subjective", ""),
            "objective": soap.get("objective", ""),
            "assessment": soap.get("assessment", ""),
            "plan": soap.get("plan", "")
        })

    if not rows:
        print("  No session data to export.")
        return None

    fieldnames = ["session_id", "patient_id", "date", "start_time", "end_time",
                  "duration_min", "exchange_count", "subjective", "objective",
                  "assessment", "plan"]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Exported {len(rows)} session records to {output_path}")
    return output_path


def export_all():
    """Run all exports and return paths."""
    print(f"\n  Research Data Export")
    print(f"  {'='*50}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    paths = []
    p = export_patient_trajectories()
    if p:
        paths.append(p)
    p = export_goal_adherence()
    if p:
        paths.append(p)
    p = export_session_notes()
    if p:
        paths.append(p)

    if paths:
        print(f"\n  All exports saved to: {EXPORT_DIR}")
    else:
        print("\n  No data to export yet. Use the coach to build up patient data first.")
    print(f"  {'='*50}\n")
    return paths
