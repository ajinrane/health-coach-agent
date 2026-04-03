"""Research analytics — aggregate statistics across patients.

Generates summary statistics, effect sizes, and research-ready
tabular data for clinical research analysis.
"""

import math
from datetime import datetime

from .memory import list_patients, load_patient
from .session import list_sessions


def research_dashboard():
    """Display aggregate research statistics across all patients."""
    patients_summary = list_patients()

    if not patients_summary:
        print("\n  No patient data yet.\n")
        return

    profiles = []
    for ps in patients_summary:
        p = load_patient(ps["patient_id"])
        if p:
            profiles.append(p)

    print(f"\n  {'='*60}")
    print(f"  RESEARCH DASHBOARD")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  {'='*60}")

    # Enrollment stats
    print(f"\n  ENROLLMENT")
    print(f"  {'─'*50}")
    print(f"  Total patients: {len(profiles)}")

    ages = [p["demographics"]["age"] for p in profiles if p.get("demographics", {}).get("age")]
    if ages:
        print(f"  Age: mean={_mean(ages):.1f}, SD={_sd(ages):.1f}, range={min(ages)}-{max(ages)}")

    sexes = [p["demographics"]["sex"] for p in profiles if p.get("demographics", {}).get("sex")]
    if sexes:
        sex_counts = {}
        for s in sexes:
            sex_counts[s] = sex_counts.get(s, 0) + 1
        sex_str = ", ".join(f"{k}: {v}" for k, v in sorted(sex_counts.items()))
        print(f"  Sex: {sex_str}")

    conditions = []
    for p in profiles:
        conditions.extend(p.get("demographics", {}).get("conditions", []))
    if conditions:
        cond_counts = {}
        for c in conditions:
            c_lower = c.lower().strip()
            cond_counts[c_lower] = cond_counts.get(c_lower, 0) + 1
        top_conditions = sorted(cond_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"  Top conditions: {', '.join(f'{c} (n={n})' for c, n in top_conditions)}")

    # Session engagement
    print(f"\n  ENGAGEMENT")
    print(f"  {'─'*50}")
    all_sessions = list_sessions()
    total_exchanges = sum(p.get("conversation_count", 0) for p in profiles)
    sessions_per_patient = [len(p.get("sessions", [])) for p in profiles]

    print(f"  Total sessions: {len(all_sessions)}")
    print(f"  Total exchanges: {total_exchanges}")
    if sessions_per_patient:
        print(f"  Sessions/patient: mean={_mean(sessions_per_patient):.1f}, SD={_sd(sessions_per_patient):.1f}")

    # Assessment coverage and scores
    print(f"\n  ASSESSMENTS")
    print(f"  {'─'*50}")
    all_assessments = []
    for p in profiles:
        all_assessments.extend(p.get("assessments", []))

    if all_assessments:
        by_type = {}
        for a in all_assessments:
            by_type.setdefault(a["type"], []).append(a)

        print(f"  Total assessments administered: {len(all_assessments)}")
        print(f"  {'Assessment':<35} {'N':>4} {'Mean':>6} {'SD':>6} {'Range':>10}")
        print(f"  {'─'*65}")

        for atype, records in sorted(by_type.items()):
            scores = [r["score"] for r in records]
            max_score = records[0].get("max_score", "?")
            n = len(scores)
            mean = _mean(scores)
            sd = _sd(scores)
            rng = f"{min(scores)}-{max(scores)}"
            print(f"  {atype:<35} {n:>4} {mean:>6.1f} {sd:>6.1f} {rng:>10}")

        # Pre-post analysis for patients with 2+ assessments of same type
        _print_pre_post(profiles, by_type)
    else:
        print("  No assessments recorded yet.")

    # Goal adherence
    print(f"\n  GOAL ADHERENCE")
    print(f"  {'─'*50}")
    all_goals = []
    for p in profiles:
        all_goals.extend(p.get("goals", []))

    if all_goals:
        active = [g for g in all_goals if g.get("status") == "active"]
        completed = [g for g in all_goals if g.get("status") == "completed"]
        total_checkins = sum(len(g.get("check_ins", [])) for g in all_goals)

        print(f"  Total goals set: {len(all_goals)}")
        print(f"  Active: {len(active)}, Completed: {len(completed)}")
        print(f"  Completion rate: {round(len(completed) / len(all_goals) * 100)}%")
        print(f"  Total check-ins: {total_checkins}")

        # Adherence by pillar
        by_pillar = {}
        for g in all_goals:
            pillar = g.get("pillar", "other")
            check_ins = g.get("check_ins", [])
            if check_ins:
                adherent = sum(1 for c in check_ins if c.get("adherence"))
                by_pillar.setdefault(pillar, {"adherent": 0, "total": 0})
                by_pillar[pillar]["adherent"] += adherent
                by_pillar[pillar]["total"] += len(check_ins)

        if by_pillar:
            print(f"\n  {'Pillar':<20} {'Check-ins':>10} {'Adherence':>10}")
            print(f"  {'─'*45}")
            for pillar, data in sorted(by_pillar.items()):
                pct = round(data["adherent"] / data["total"] * 100) if data["total"] else 0
                print(f"  {pillar.capitalize():<20} {data['total']:>10} {pct:>9}%")
    else:
        print("  No goals set yet.")

    print(f"\n  {'='*60}\n")


def _print_pre_post(profiles, by_type):
    """Print pre-post analysis for patients with repeated assessments."""
    has_repeats = False

    for atype, all_records in by_type.items():
        # Group by patient
        by_patient = {}
        for r in all_records:
            # We need to figure out which patient this belongs to
            pass

    # Simpler: iterate profiles directly
    pre_post_data = {}
    for p in profiles:
        assessments = p.get("assessments", [])
        by_type_patient = {}
        for a in assessments:
            by_type_patient.setdefault(a["type"], []).append(a)

        for atype, records in by_type_patient.items():
            if len(records) >= 2:
                records_sorted = sorted(records, key=lambda x: x.get("timestamp", x.get("date", "")))
                first = records_sorted[0]["score"]
                last = records_sorted[-1]["score"]
                pre_post_data.setdefault(atype, {"pre": [], "post": []})
                pre_post_data[atype]["pre"].append(first)
                pre_post_data[atype]["post"].append(last)

    if pre_post_data:
        print(f"\n  PRE-POST ANALYSIS (patients with 2+ assessments)")
        print(f"  {'─'*65}")
        print(f"  {'Assessment':<35} {'N':>4} {'Pre':>6} {'Post':>6} {'d':>6}")
        print(f"  {'─'*65}")

        for atype, data in sorted(pre_post_data.items()):
            n = len(data["pre"])
            pre_mean = _mean(data["pre"])
            post_mean = _mean(data["post"])
            # Cohen's d (paired)
            diffs = [post - pre for pre, post in zip(data["pre"], data["post"])]
            d = _cohens_d(diffs) if len(diffs) > 1 else "N/A"
            d_str = f"{d:.2f}" if isinstance(d, float) else d
            print(f"  {atype:<35} {n:>4} {pre_mean:>6.1f} {post_mean:>6.1f} {d_str:>6}")


def _mean(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def _sd(values):
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def _cohens_d(diffs):
    """Calculate Cohen's d for paired samples."""
    if len(diffs) < 2:
        return 0.0
    m = _mean(diffs)
    sd = _sd(diffs)
    if sd == 0:
        return 0.0
    return m / sd
