"""SMART goal tracking and adherence monitoring."""

from datetime import datetime


def display_goals(profile):
    """Display all goals with adherence stats."""
    goals = profile.get("goals", [])
    if not goals:
        print("\n  No goals set yet. Start a conversation or use /assess to identify areas to work on.\n")
        return

    active = [g for g in goals if g.get("status") == "active"]
    completed = [g for g in goals if g.get("status") == "completed"]

    if active:
        print(f"\n  Active Goals ({len(active)})")
        print(f"  {'─'*50}")
        for g in active:
            _print_goal(g)

    if completed:
        print(f"\n  Completed Goals ({len(completed)})")
        print(f"  {'─'*50}")
        for g in completed:
            _print_goal(g, show_completed=True)

    print()


def _print_goal(goal, show_completed=False):
    """Print a single goal with details."""
    pillar = goal.get("pillar", "other").upper()
    desc = goal["description"]
    target = goal.get("target", "")
    goal_id = goal["id"]

    check_ins = goal.get("check_ins", [])
    if check_ins:
        adherent = sum(1 for c in check_ins if c.get("adherence"))
        pct = round(adherent / len(check_ins) * 100)
        bar = _progress_bar(pct)
        adherence_str = f"{bar} {pct}% ({adherent}/{len(check_ins)} check-ins)"
    else:
        adherence_str = "No check-ins yet"

    print(f"\n  [{pillar}] {desc}  (id: {goal_id})")
    print(f"    Target: {target}")
    if goal.get("timeframe"):
        print(f"    Timeframe: {goal['timeframe']}")
    print(f"    Adherence: {adherence_str}")

    if show_completed and goal.get("completed_at"):
        print(f"    Completed: {goal['completed_at'][:10]}")

    # Show recent check-ins
    if check_ins:
        recent = check_ins[-3:]
        for c in recent:
            status = "+" if c.get("adherence") else "-"
            notes = f" — {c['notes']}" if c.get("notes") else ""
            print(f"    {status} {c['date']}{notes}")


def _progress_bar(pct, width=10):
    """Create a simple ASCII progress bar."""
    filled = round(pct / 100 * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def interactive_check_in(profile):
    """Run an interactive check-in on active goals."""
    from . import memory as mem

    active = [g for g in profile.get("goals", []) if g.get("status") == "active"]
    if not active:
        print("\n  No active goals to check in on.\n")
        return

    print(f"\n  Goal Check-In")
    print(f"  {'='*50}")
    print(f"  Let's see how you did on your goals.\n")

    for goal in active:
        pillar = goal.get("pillar", "other").upper()
        print(f"  [{pillar}] {goal['description']}")
        print(f"  Target: {goal['target']}")

        while True:
            response = input("  Did you meet this goal? (y/n/skip): ").strip().lower()
            if response in ("y", "n", "skip", "s"):
                break
            print("  Please enter y, n, or skip.")

        if response in ("skip", "s"):
            print()
            continue

        adherence = response == "y"
        notes = input("  Any notes? (press Enter to skip): ").strip()

        mem.check_in_goal(profile, goal["id"], adherence, notes)

        if adherence:
            print("  Great work! Keep it up.\n")
        else:
            print("  That's okay — every day is a new chance. What got in the way?\n")

    print(f"  {'─'*50}")
    print("  Check-in complete. Your progress has been saved.\n")


def interactive_add_goal(profile):
    """Interactively add a new goal."""
    from . import memory as mem

    pillars = ["sleep", "nutrition", "exercise", "stress", "connection", "substances", "other"]

    print(f"\n  New Goal")
    print(f"  {'='*50}")
    print("  Pillars:")
    for i, p in enumerate(pillars):
        print(f"    {i+1}) {p.capitalize()}")

    while True:
        try:
            choice = int(input("  Select pillar (1-7): ").strip())
            if 1 <= choice <= 7:
                pillar = pillars[choice - 1]
                break
            print("  Please enter 1-7.")
        except (ValueError, EOFError):
            print("  Please enter a number.")

    description = input("  Describe your goal: ").strip()
    if not description:
        print("  Goal cancelled.\n")
        return

    target = input("  Measurable target (e.g., '30 min walk 5x/week'): ").strip()
    timeframe = input("  Timeframe (e.g., 'next 2 weeks'): ").strip()

    goal = mem.add_goal(profile, pillar, description, target, timeframe)
    print(f"\n  Goal created! (id: {goal['id']})")
    print(f"  [{pillar.upper()}] {description}")
    print(f"  Target: {target}")
    if timeframe:
        print(f"  Timeframe: {timeframe}")
    print()


def interactive_complete_goal(profile):
    """Interactively mark a goal as completed."""
    from . import memory as mem

    active = [g for g in profile.get("goals", []) if g.get("status") == "active"]
    if not active:
        print("\n  No active goals.\n")
        return

    print("\n  Complete a Goal")
    print(f"  {'='*50}")
    for i, g in enumerate(active):
        print(f"  {i+1}) [{g['pillar'].upper()}] {g['description']}  (id: {g['id']})")

    while True:
        try:
            choice = int(input("  Select goal to complete (0 to cancel): ").strip())
            if choice == 0:
                print("  Cancelled.\n")
                return
            if 1 <= choice <= len(active):
                goal = active[choice - 1]
                mem.complete_goal(profile, goal["id"])
                print(f"\n  Congratulations! Goal completed: {goal['description']}\n")
                return
            print(f"  Please enter 0-{len(active)}.")
        except (ValueError, EOFError):
            print("  Please enter a number.")
