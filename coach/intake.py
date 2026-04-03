"""Guided intake assessment flow for new patients.

Runs a standardized battery of screenings on first visit to establish
baseline measurements across all lifestyle medicine pillars.
"""

from .assessments import run_assessment, ASSESSMENTS
from .memory import add_assessment, save_patient


# The standard intake battery — ordered by clinical priority
INTAKE_BATTERY = [
    ("phq2", "Mental health is foundational — let's start with a quick mood check."),
    ("gad2", "Now let's check in on worry and anxiety."),
    ("sleep", "Sleep affects everything else. Let's see where you stand."),
    ("evs", "Physical activity is medicine. Let's measure your current level."),
    ("nutrition", "Diet quality drives chronic disease outcomes. Quick food check."),
    ("stress", "Finally, let's measure your stress load."),
]


def run_intake(profile):
    """Run the full intake assessment battery.

    Returns a summary dict with all results.
    """
    print(f"\n  {'='*60}")
    print(f"  INTAKE ASSESSMENT")
    print(f"  {'='*60}")
    print(f"  We'll run {len(INTAKE_BATTERY)} quick screenings to understand where you are")
    print(f"  across the major lifestyle medicine pillars.")
    print(f"  This takes about 5-8 minutes.\n")

    proceed = input("  Ready to begin? (y/n): ").strip().lower()
    if proceed != "y":
        print("  No problem — you can run /assess anytime to take individual screenings.\n")
        return None

    results = {}
    completed = 0

    for key, intro in INTAKE_BATTERY:
        assessment = ASSESSMENTS[key]
        print(f"\n  [{completed + 1}/{len(INTAKE_BATTERY)}] {intro}")

        result = run_assessment(key)
        if result:
            score, max_score, interpretation, details = result
            add_assessment(profile, assessment["name"], score, max_score, interpretation, details)
            results[key] = {
                "name": assessment["name"],
                "score": score,
                "max_score": max_score,
                "interpretation": interpretation
            }
            completed += 1

        skip = input("  Continue to next assessment? (y/n): ").strip().lower()
        if skip != "y":
            print(f"\n  Stopped after {completed} assessments. You can complete the rest later with /assess.\n")
            break

    if results:
        _print_intake_summary(results)
        save_patient(profile)

    return results


def _print_intake_summary(results):
    """Print a summary of all intake results."""
    print(f"\n  {'='*60}")
    print(f"  INTAKE SUMMARY")
    print(f"  {'='*60}")

    # Categorize results by concern level
    concerns = []
    strengths = []

    for key, r in results.items():
        interp = r["interpretation"]
        name = r["name"]
        score = r["score"]
        max_score = r["max_score"]

        # Determine if this is a concern based on interpretation keywords
        if any(word in interp.lower() for word in ["positive screen", "high", "poor", "needs_improvement", "inactive", "insufficient"]):
            concerns.append((name, score, max_score, interp))
        elif any(word in interp.lower() for word in ["negative screen", "low", "good", "meeting"]):
            strengths.append((name, score, max_score, interp))
        else:
            # Middle ground — not urgent but room for improvement
            concerns.append((name, score, max_score, interp))

    if strengths:
        print(f"\n  Strengths:")
        for name, score, max_score, interp in strengths:
            print(f"    + {name}: {score}/{max_score}")
            print(f"      {interp}")

    if concerns:
        print(f"\n  Areas to Address:")
        for name, score, max_score, interp in concerns:
            print(f"    ! {name}: {score}/{max_score}")
            print(f"      {interp}")

    # Priority recommendation
    if concerns:
        top = concerns[0]
        print(f"\n  Recommended starting point: {top[0]}")
        print(f"  Let's set a goal around this in our first conversation.")

    print(f"\n  These scores serve as your baseline. Retake assessments over time")
    print(f"  to track your progress. Use /assess to run any screening again.")
    print(f"  {'='*60}\n")
