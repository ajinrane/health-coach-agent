"""Health Coach Agent — Clinical lifestyle medicine coaching CLI.

A conversational AI health coach that uses validated clinical assessments,
SMART goal tracking, and evidence-based behavior change techniques to help
patients make sustainable lifestyle modifications.
"""

import sys

from dotenv import load_dotenv

load_dotenv()

from coach.memory import create_patient, load_patient, list_patients, save_patient
from coach.agent import chat, extract_profile_updates, apply_profile_updates
from coach.session import start_session, add_exchange, end_session, display_session_summary, list_sessions, load_session
from coach.assessments import get_assessment_list, run_assessment
from coach.goals import display_goals, interactive_check_in, interactive_add_goal, interactive_complete_goal
from coach.export import export_all
from coach.memory import add_assessment


BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                  Health Coach Agent                         ║
║         Clinical Lifestyle Medicine Coaching                ║
╠══════════════════════════════════════════════════════════════╣
║  Commands:                                                  ║
║    /assess    — Run a validated clinical assessment          ║
║    /goals     — View your goals and adherence               ║
║    /newgoal   — Create a new SMART goal                     ║
║    /checkin   — Check in on goal progress                   ║
║    /complete  — Mark a goal as completed                    ║
║    /profile   — View your health profile                    ║
║    /session   — View current session summary                ║
║    /history   — View past sessions                          ║
║    /export    — Export data for research (CSV)              ║
║    /help      — Show this menu                              ║
║    /quit      — End session and save                        ║
╚══════════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
  Commands:
    /assess    — Run a validated clinical screening (PHQ-2, GAD-2, sleep, etc.)
    /goals     — View all goals with adherence tracking
    /newgoal   — Create a new SMART goal
    /checkin   — Check in on your active goals
    /complete  — Mark a goal as completed
    /profile   — View your full health profile
    /session   — View current session notes
    /history   — View past session summaries
    /export    — Export all data to CSV for research analysis
    /help      — Show this help
    /quit      — End session, generate SOAP note, and save

  Or just talk to your coach — type anything to start a conversation.
"""


def select_or_create_patient():
    """Patient selection flow."""
    patients = list_patients()

    if not patients:
        print("\n  Welcome! Let's set up your profile.\n")
        return onboard_new_patient()

    print("\n  Existing profiles:")
    for i, p in enumerate(patients):
        demo = p.get("demographics", {})
        age = demo.get("age", "?")
        sex = demo.get("sex", "")
        conditions = ", ".join(demo.get("conditions", [])) or "none listed"
        sessions = p.get("session_count", 0)
        print(f"    {i+1}) Patient {p['patient_id']} — {age}yo {sex}, {conditions} ({sessions} sessions)")

    print(f"    {len(patients)+1}) Create new profile")

    while True:
        try:
            choice = input("\n  Select profile: ").strip()
            idx = int(choice)
            if 1 <= idx <= len(patients):
                patient = load_patient(patients[idx - 1]["patient_id"])
                print(f"\n  Welcome back, patient {patient['patient_id']}!")
                return patient
            elif idx == len(patients) + 1:
                return onboard_new_patient()
            print(f"  Please enter 1-{len(patients)+1}.")
        except (ValueError, EOFError):
            print("  Please enter a number.")


def onboard_new_patient():
    """Onboard a new patient with demographics."""
    print("  Let's get some basic info.\n")

    age = None
    age_input = input("  Age: ").strip()
    if age_input.isdigit():
        age = int(age_input)

    sex = input("  Sex (male/female/other, or press Enter to skip): ").strip().lower()
    if sex not in ("male", "female", "other"):
        sex = None

    conditions_input = input("  Any health conditions? (comma-separated, or press Enter to skip): ").strip()
    conditions = [c.strip() for c in conditions_input.split(",") if c.strip()] if conditions_input else []

    meds_input = input("  Current medications? (comma-separated, or press Enter to skip): ").strip()
    medications = [m.strip() for m in meds_input.split(",") if m.strip()] if meds_input else []

    demographics = {
        "age": age,
        "sex": sex,
        "conditions": conditions,
        "medications": medications,
        "notes": ""
    }

    profile = create_patient(demographics)
    print(f"\n  Profile created! Your ID: {profile['patient_id']}")
    print("  Tip: Run /assess to take a baseline health assessment.\n")
    return profile


def handle_assess(profile, session):
    """Handle the /assess command."""
    assessments = get_assessment_list()
    print("\n  Available Assessments:")
    for i, (key, name, desc) in enumerate(assessments):
        print(f"    {i+1}) {name}")
        print(f"       {desc}")

    while True:
        try:
            choice = input("\n  Select assessment (0 to cancel): ").strip()
            idx = int(choice)
            if idx == 0:
                return
            if 1 <= idx <= len(assessments):
                key = assessments[idx - 1][0]
                result = run_assessment(key)
                if result:
                    score, max_score, interpretation, details = result
                    assessment_record = add_assessment(
                        profile, assessments[idx - 1][1],
                        score, max_score, interpretation, details
                    )
                    session["assessments_run"].append(key)
                    print(f"  Assessment saved to your profile.")
                return
            print(f"  Please enter 0-{len(assessments)}.")
        except (ValueError, EOFError):
            print("  Please enter a number.")


def handle_profile(profile):
    """Handle the /profile command."""
    from coach.memory import get_profile_summary
    print(f"\n  {'='*50}")
    print(f"  Patient Profile — {profile['patient_id']}")
    print(f"  {'='*50}")
    print(f"  Created: {profile['created_at'][:10]}")
    print(f"  Sessions: {len(profile.get('sessions', []))}")
    print(f"  Total exchanges: {profile.get('conversation_count', 0)}")
    print()

    demo = profile.get("demographics", {})
    print(f"  Demographics:")
    if demo.get("age"):
        print(f"    Age: {demo['age']}")
    if demo.get("sex"):
        print(f"    Sex: {demo['sex']}")
    if demo.get("conditions"):
        print(f"    Conditions: {', '.join(demo['conditions'])}")
    if demo.get("medications"):
        print(f"    Medications: {', '.join(demo['medications'])}")
    if demo.get("notes"):
        print(f"    Notes: {demo['notes']}")

    assessments = profile.get("assessments", [])
    if assessments:
        print(f"\n  Assessment History ({len(assessments)} total):")
        for a in assessments[-5:]:
            print(f"    {a['date']} — {a['type']}: {a['score']}/{a['max_score']} ({a['interpretation'][:60]})")

    goals = profile.get("goals", [])
    active = [g for g in goals if g.get("status") == "active"]
    completed = [g for g in goals if g.get("status") == "completed"]
    print(f"\n  Goals: {len(active)} active, {len(completed)} completed")

    print(f"  {'='*50}\n")


def handle_history(profile):
    """Handle the /history command."""
    session_ids = profile.get("sessions", [])
    if not session_ids:
        print("\n  No past sessions.\n")
        return

    print(f"\n  Session History ({len(session_ids)} sessions)")
    print(f"  {'='*50}")

    for sid in reversed(session_ids[-10:]):
        s = load_session(sid)
        if s:
            date = s.get("start_time", "")[:16].replace("T", " ")
            exchanges = len(s.get("conversation", []))
            soap = s.get("soap_note")
            plan = soap.get("plan", "")[:80] if soap else ""
            print(f"  {sid} | {date} | {exchanges} exchanges")
            if plan:
                print(f"    Plan: {plan}")
    print(f"  {'='*50}\n")


def main():
    print(BANNER)

    # Select or create patient
    profile = select_or_create_patient()
    session = start_session(profile["patient_id"])
    conversation_history = []

    print("  Ready! Type a message or a command (/help for options).\n")

    while True:
        try:
            user_input = input("  You: ").strip()
        except (EOFError, KeyboardInterrupt):
            user_input = "/quit"

        if not user_input:
            continue

        # Handle commands
        command = user_input.lower()

        if command == "/quit" or command == "/exit":
            print("\n  Ending session...")
            session = end_session(session, profile)
            if session.get("soap_note"):
                display_session_summary(session)
            print("  Your progress has been saved. Take care!\n")
            break

        elif command == "/help":
            print(HELP_TEXT)
            continue

        elif command == "/assess":
            handle_assess(profile, session)
            continue

        elif command == "/goals":
            display_goals(profile)
            continue

        elif command == "/newgoal":
            interactive_add_goal(profile)
            continue

        elif command == "/checkin":
            interactive_check_in(profile)
            continue

        elif command == "/complete":
            interactive_complete_goal(profile)
            continue

        elif command == "/profile":
            handle_profile(profile)
            continue

        elif command == "/session":
            display_session_summary(session)
            continue

        elif command == "/history":
            handle_history(profile)
            continue

        elif command == "/export":
            export_all()
            continue

        # Regular conversation
        print()
        try:
            response, conversation_history = chat(
                user_input, profile, conversation_history
            )
            print(f"  Coach: {response}\n")

            # Record in session
            add_exchange(session, user_input, response)

            # Extract and apply profile updates (async-style, non-blocking feel)
            try:
                updates = extract_profile_updates(user_input, response, profile)
                profile = apply_profile_updates(profile, updates)
            except Exception:
                pass  # Don't let extraction failures break the conversation

        except Exception as e:
            print(f"  Error: {e}")
            print("  Please try again or check your API key in .env\n")


if __name__ == "__main__":
    main()
