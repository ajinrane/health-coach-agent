"""Session management with SOAP note documentation."""

import json
import uuid
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from .memory import get_profile_summary, save_patient
from .prompts import SESSION_SUMMARY_PROMPT

load_dotenv()

SESSION_DIR = Path(__file__).parent.parent / "data" / "sessions"


def ensure_session_dir():
    SESSION_DIR.mkdir(parents=True, exist_ok=True)


def start_session(patient_id):
    """Start a new coaching session."""
    ensure_session_dir()
    session = {
        "session_id": str(uuid.uuid4())[:8],
        "patient_id": patient_id,
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "conversation": [],
        "soap_note": None,
        "assessments_run": [],
        "goals_created": [],
        "goals_checked_in": []
    }
    return session


def add_exchange(session, user_message, assistant_response):
    """Record a conversation exchange."""
    session["conversation"].append({
        "user": user_message,
        "assistant": assistant_response,
        "timestamp": datetime.now().isoformat()
    })


def end_session(session, profile):
    """End a session, generate SOAP note, and save."""
    session["end_time"] = datetime.now().isoformat()

    # Generate SOAP note if there was meaningful conversation
    if len(session["conversation"]) >= 2:
        session["soap_note"] = generate_soap_note(session, profile)

    # Save session file
    ensure_session_dir()
    path = SESSION_DIR / f"{session['session_id']}.json"
    with open(path, "w") as f:
        json.dump(session, f, indent=2)

    # Add session reference to patient profile
    if session["session_id"] not in profile.get("sessions", []):
        profile.setdefault("sessions", []).append(session["session_id"])
        profile["conversation_count"] = profile.get("conversation_count", 0) + len(session["conversation"])
        save_patient(profile)

    return session


def generate_soap_note(session, profile):
    """Use Claude to generate a SOAP note from the session."""
    try:
        client = anthropic.Anthropic()

        profile_summary = get_profile_summary(profile)
        conversation_text = ""
        for ex in session["conversation"]:
            conversation_text += f"Patient: {ex['user']}\nCoach: {ex['assistant']}\n\n"

        prompt = SESSION_SUMMARY_PROMPT.format(
            profile_summary=profile_summary,
            conversation=conversation_text
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)
    except Exception:
        return {
            "subjective": "Session completed — auto-summary unavailable.",
            "objective": f"{len(session['conversation'])} exchanges.",
            "assessment": "See conversation log.",
            "plan": "Continue at next session."
        }


def display_session_summary(session):
    """Display a session summary."""
    print(f"\n  {'='*60}")
    print(f"  Session Summary — {session['session_id']}")
    print(f"  {'='*60}")
    print(f"  Start: {session['start_time'][:16].replace('T', ' ')}")
    if session.get("end_time"):
        print(f"  End:   {session['end_time'][:16].replace('T', ' ')}")
    print(f"  Exchanges: {len(session['conversation'])}")

    soap = session.get("soap_note")
    if soap:
        print(f"\n  SOAP Note")
        print(f"  {'─'*50}")
        print(f"  S (Subjective): {soap.get('subjective', 'N/A')}")
        print(f"  O (Objective):  {soap.get('objective', 'N/A')}")
        print(f"  A (Assessment): {soap.get('assessment', 'N/A')}")
        print(f"  P (Plan):       {soap.get('plan', 'N/A')}")

    if session.get("assessments_run"):
        print(f"\n  Assessments: {', '.join(session['assessments_run'])}")
    if session.get("goals_created"):
        print(f"  Goals created: {len(session['goals_created'])}")

    print(f"  {'='*60}\n")


def load_session(session_id):
    """Load a session by ID."""
    path = SESSION_DIR / f"{session_id}.json"
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def list_sessions(patient_id=None):
    """List all sessions, optionally filtered by patient."""
    ensure_session_dir()
    sessions = []
    for path in SESSION_DIR.glob("*.json"):
        with open(path, "r") as f:
            s = json.load(f)
            if patient_id is None or s.get("patient_id") == patient_id:
                sessions.append(s)
    return sorted(sessions, key=lambda x: x.get("start_time", ""), reverse=True)
