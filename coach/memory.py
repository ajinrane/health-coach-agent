"""Patient profile and memory management with structured clinical data."""

import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "patients"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def create_patient(demographics=None):
    """Create a new patient profile."""
    ensure_data_dir()
    patient_id = str(uuid.uuid4())[:8]
    profile = {
        "patient_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "demographics": demographics or {
            "age": None,
            "sex": None,
            "conditions": [],
            "medications": [],
            "notes": ""
        },
        "assessments": [],
        "goals": [],
        "sessions": [],
        "conversation_count": 0
    }
    save_patient(profile)
    return profile


def save_patient(profile):
    """Save patient profile to disk."""
    ensure_data_dir()
    profile["updated_at"] = datetime.now().isoformat()
    path = DATA_DIR / f"{profile['patient_id']}.json"
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)


def load_patient(patient_id):
    """Load a patient profile by ID."""
    path = DATA_DIR / f"{patient_id}.json"
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def list_patients():
    """List all patient profiles."""
    ensure_data_dir()
    patients = []
    for path in DATA_DIR.glob("*.json"):
        with open(path, "r") as f:
            p = json.load(f)
            patients.append({
                "patient_id": p["patient_id"],
                "created_at": p["created_at"],
                "demographics": p.get("demographics", {}),
                "session_count": len(p.get("sessions", [])),
                "goal_count": len([g for g in p.get("goals", []) if g.get("status") == "active"])
            })
    return sorted(patients, key=lambda x: x["created_at"], reverse=True)


def update_demographics(profile, **kwargs):
    """Update patient demographics."""
    for key, value in kwargs.items():
        if key in profile["demographics"]:
            if isinstance(profile["demographics"][key], list) and isinstance(value, str):
                if value not in profile["demographics"][key]:
                    profile["demographics"][key].append(value)
            else:
                profile["demographics"][key] = value
    save_patient(profile)
    return profile


def add_assessment(profile, assessment_type, score, max_score, interpretation, details=None):
    """Record a clinical assessment result."""
    assessment = {
        "id": str(uuid.uuid4())[:8],
        "type": assessment_type,
        "score": score,
        "max_score": max_score,
        "interpretation": interpretation,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
    }
    if details:
        assessment["details"] = details
    profile["assessments"].append(assessment)
    save_patient(profile)
    return assessment


def add_goal(profile, pillar, description, target, timeframe=""):
    """Add a SMART goal to the patient profile."""
    goal = {
        "id": str(uuid.uuid4())[:8],
        "pillar": pillar,
        "description": description,
        "target": target,
        "timeframe": timeframe,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "check_ins": []
    }
    profile["goals"].append(goal)
    save_patient(profile)
    return goal


def check_in_goal(profile, goal_id, adherence, notes=""):
    """Record a check-in for a goal."""
    for goal in profile["goals"]:
        if goal["id"] == goal_id:
            goal["check_ins"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "adherence": adherence,
                "notes": notes
            })
            save_patient(profile)
            return goal
    return None


def complete_goal(profile, goal_id):
    """Mark a goal as completed."""
    for goal in profile["goals"]:
        if goal["id"] == goal_id:
            goal["status"] = "completed"
            goal["completed_at"] = datetime.now().isoformat()
            save_patient(profile)
            return goal
    return None


def get_profile_summary(profile):
    """Generate a text summary of the patient profile for prompt context."""
    lines = []
    demo = profile.get("demographics", {})
    parts = []
    if demo.get("age"):
        parts.append(f"{demo['age']}yo")
    if demo.get("sex"):
        parts.append(demo["sex"])
    if demo.get("conditions"):
        parts.append(f"conditions: {', '.join(demo['conditions'])}")
    if demo.get("medications"):
        parts.append(f"meds: {', '.join(demo['medications'])}")
    if parts:
        lines.append(f"Demographics: {', '.join(parts)}")
    if demo.get("notes"):
        lines.append(f"Notes: {demo['notes']}")

    active_goals = [g for g in profile.get("goals", []) if g.get("status") == "active"]
    if active_goals:
        lines.append("Active goals:")
        for g in active_goals:
            check_ins = g.get("check_ins", [])
            if check_ins:
                adherent = sum(1 for c in check_ins if c.get("adherence"))
                pct = round(adherent / len(check_ins) * 100)
                adherence_str = f" — adherence: {pct}% ({adherent}/{len(check_ins)})"
            else:
                adherence_str = " — no check-ins yet"
            lines.append(f"  [{g['pillar']}] {g['description']} (target: {g['target']}){adherence_str}")

    assessments = profile.get("assessments", [])
    if assessments:
        lines.append("Recent assessments:")
        for a in assessments[-5:]:
            lines.append(f"  {a['type']}: {a['score']}/{a['max_score']} on {a['date']} — {a['interpretation']}")

    return "\n".join(lines) if lines else "New patient — no data yet."
