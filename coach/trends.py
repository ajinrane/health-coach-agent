"""Trend analysis for longitudinal assessment tracking.

Computes and displays changes in assessment scores over time,
enabling both patients and researchers to see progress or regression.
"""

from datetime import datetime


def analyze_trends(profile):
    """Analyze assessment trends for a patient and display results."""
    assessments = profile.get("assessments", [])
    if not assessments:
        print("\n  No assessments recorded yet. Run /assess to take your first screening.\n")
        return

    # Group by assessment type
    by_type = {}
    for a in assessments:
        atype = a["type"]
        by_type.setdefault(atype, []).append(a)

    print(f"\n  {'='*60}")
    print(f"  ASSESSMENT TRENDS — Patient {profile['patient_id']}")
    print(f"  {'='*60}")

    for atype, records in sorted(by_type.items()):
        records = sorted(records, key=lambda x: x.get("timestamp", x.get("date", "")))
        print(f"\n  {atype}")
        print(f"  {'─'*50}")

        if len(records) == 1:
            r = records[0]
            print(f"  Baseline ({r['date']}): {r['score']}/{r['max_score']}")
            print(f"  {r['interpretation']}")
            print(f"  (Need 2+ assessments to show trends)")
        else:
            first = records[0]
            latest = records[-1]
            change = latest["score"] - first["score"]
            pct_change = round(change / max(first["score"], 1) * 100)

            # Determine if change is good or bad based on assessment type
            # For most scales, lower is better (PHQ, GAD, stress, sleep problems)
            # For EVS (exercise) and nutrition, higher is better
            higher_is_better = "exercise" in atype.lower() or "nutrition" in atype.lower() or "dietary" in atype.lower()

            if change == 0:
                direction = "unchanged"
                indicator = "="
            elif (change > 0 and higher_is_better) or (change < 0 and not higher_is_better):
                direction = "improved"
                indicator = "^"
            else:
                direction = "worsened"
                indicator = "v"

            # Print timeline
            for r in records:
                bar = _score_bar(r["score"], r["max_score"])
                print(f"  {r['date']}  {bar}  {r['score']}/{r['max_score']}")

            print(f"\n  Change: {'+' if change > 0 else ''}{change} ({'+' if pct_change > 0 else ''}{pct_change}%) — {direction} {indicator}")
            print(f"  Latest: {latest['interpretation']}")

    # Goal adherence summary
    goals = profile.get("goals", [])
    active_goals = [g for g in goals if g.get("status") == "active"]
    if active_goals:
        print(f"\n  {'─'*50}")
        print(f"  GOAL ADHERENCE SUMMARY")
        print(f"  {'─'*50}")
        for goal in active_goals:
            check_ins = goal.get("check_ins", [])
            if check_ins:
                adherent = sum(1 for c in check_ins if c.get("adherence"))
                total = len(check_ins)
                pct = round(adherent / total * 100)
                bar = _progress_bar(pct)
                print(f"  [{goal['pillar'].upper()}] {goal['description']}")
                print(f"    {bar} {pct}% adherence ({adherent}/{total} check-ins)")
            else:
                print(f"  [{goal['pillar'].upper()}] {goal['description']} — no check-ins yet")

    print(f"\n  {'='*60}\n")


def _score_bar(score, max_score, width=20):
    """Create a visual score bar."""
    if max_score == 0:
        return "[" + " " * width + "]"
    filled = round(score / max_score * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _progress_bar(pct, width=15):
    """Create a progress percentage bar."""
    filled = round(pct / 100 * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def get_trend_data(profile, assessment_type=None):
    """Get raw trend data for research export.

    Returns list of dicts with date, type, score, max_score for each assessment.
    Optionally filtered by assessment type.
    """
    assessments = profile.get("assessments", [])
    if assessment_type:
        assessments = [a for a in assessments if a["type"] == assessment_type]

    return sorted(
        [{"date": a["date"], "type": a["type"], "score": a["score"],
          "max_score": a["max_score"], "interpretation": a["interpretation"]}
         for a in assessments],
        key=lambda x: x["date"]
    )
