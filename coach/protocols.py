"""Evidence-based lifestyle medicine intervention protocols.

Structured, week-by-week programs the coach can recommend based on
a patient's assessment results and goals.
"""

PROTOCOLS = {
    "sleep_hygiene": {
        "name": "Sleep Hygiene Protocol (CBT-I Based)",
        "pillar": "sleep",
        "description": "8-week program based on Cognitive Behavioral Therapy for Insomnia (CBT-I) principles: stimulus control, sleep restriction, and sleep hygiene education.",
        "citation": "Trauer JM, et al. Cognitive Behavioral Therapy for Chronic Insomnia: A Systematic Review and Meta-analysis. Ann Intern Med. 2015;163(3):191-204.",
        "duration_weeks": 8,
        "contraindications": [
            "Untreated sleep apnea (refer to sleep medicine first)",
            "Shift workers (need adapted protocol)",
            "Active substance use disorder affecting sleep"
        ],
        "weeks": [
            {
                "week": 1,
                "theme": "Assessment and Sleep Diary",
                "actions": [
                    "Track bedtime, wake time, and sleep quality for 7 days",
                    "No changes yet — just observe your current patterns",
                    "Note caffeine, alcohol, and screen time before bed"
                ]
            },
            {
                "week": 2,
                "theme": "Stimulus Control",
                "actions": [
                    "Use bed only for sleep (no phones, TV, or work in bed)",
                    "If awake >20 min in bed, get up and do something boring in dim light",
                    "Return to bed only when sleepy"
                ]
            },
            {
                "week": 3,
                "theme": "Sleep Scheduling",
                "actions": [
                    "Set a fixed wake time 7 days/week (even weekends)",
                    "Set bedtime based on your average sleep duration from Week 1",
                    "No naps longer than 20 minutes"
                ]
            },
            {
                "week": 4,
                "theme": "Wind-Down Routine",
                "actions": [
                    "Create a 30-minute wind-down routine before bed",
                    "Dim lights 1 hour before bedtime",
                    "Stop all screens 30 min before bed (or use night mode)"
                ]
            },
            {
                "week": 5,
                "theme": "Environment Optimization",
                "actions": [
                    "Cool bedroom to 65-68°F / 18-20°C",
                    "Ensure room is dark (blackout curtains or sleep mask)",
                    "Use white noise if needed for sound masking"
                ]
            },
            {
                "week": 6,
                "theme": "Caffeine and Substance Audit",
                "actions": [
                    "No caffeine after 2 PM (half-life is 5-6 hours)",
                    "No alcohol within 3 hours of bedtime",
                    "Track how these changes affect sleep quality"
                ]
            },
            {
                "week": 7,
                "theme": "Cognitive Techniques",
                "actions": [
                    "Write a 'worry list' 2 hours before bed — get thoughts out of your head",
                    "Practice 4-7-8 breathing when lying in bed",
                    "Replace 'I must sleep 8 hours' with 'my body knows how to sleep'"
                ]
            },
            {
                "week": 8,
                "theme": "Maintenance and Review",
                "actions": [
                    "Retake sleep assessment to measure improvement",
                    "Identify which 2-3 techniques helped most",
                    "Build a sustainable routine from what worked"
                ]
            }
        ]
    },
    "exercise_starter": {
        "name": "Exercise Starter Protocol",
        "pillar": "exercise",
        "description": "Progressive 8-week program from sedentary to 150 min/week moderate activity, meeting WHO physical activity guidelines.",
        "citation": "Bull FC, et al. World Health Organization 2020 guidelines on physical activity and sedentary behaviour. Br J Sports Med. 2020;54(24):1451-1462.",
        "duration_weeks": 8,
        "contraindications": [
            "Unstable cardiovascular disease (get medical clearance)",
            "Recent surgery or acute injury",
            "Uncontrolled hypertension >180/110 (stabilize first)"
        ],
        "weeks": [
            {
                "week": 1,
                "theme": "Foundation (50 min/week)",
                "actions": [
                    "Walk 10 minutes after a meal, 5 days this week",
                    "Pick a consistent time that works for your schedule",
                    "Pace: you should be able to hold a conversation"
                ]
            },
            {
                "week": 2,
                "theme": "Building (70 min/week)",
                "actions": [
                    "Walk 15 minutes, 5 days this week",
                    "Try walking right after dinner — it improves post-meal glucose by 22%",
                    "Add gentle stretching (5 min) after each walk"
                ]
            },
            {
                "week": 3,
                "theme": "Extending (90 min/week)",
                "actions": [
                    "Walk 20 minutes, 5 days this week",
                    "Increase pace slightly on 2 of the 5 walks (brisk walking)",
                    "Notice how you feel after — log energy levels"
                ]
            },
            {
                "week": 4,
                "theme": "Adding Intensity (100 min/week)",
                "actions": [
                    "Walk 20 minutes, 5 days this week",
                    "3 walks at moderate pace (slight breathlessness, can still talk)",
                    "Add 1 bodyweight exercise session: 3x10 squats, 3x10 push-ups (wall or floor)"
                ]
            },
            {
                "week": 5,
                "theme": "Variety (120 min/week)",
                "actions": [
                    "Walk 25 minutes, 4 days this week",
                    "1 day: try something different (bike, swim, dance, yoga)",
                    "1 day: bodyweight strength (add lunges and planks)"
                ]
            },
            {
                "week": 6,
                "theme": "Approaching Target (135 min/week)",
                "actions": [
                    "Walk/activity 25-30 minutes, 5 days this week",
                    "Include 2 bouts of vigorous walking (hills or fast pace)",
                    "Strength session: 2 sets of 4 exercises"
                ]
            },
            {
                "week": 7,
                "theme": "Meeting Guidelines (150 min/week)",
                "actions": [
                    "30 minutes moderate activity, 5 days this week",
                    "2 strength training sessions (bodyweight or weights)",
                    "You're now meeting WHO physical activity guidelines!"
                ]
            },
            {
                "week": 8,
                "theme": "Maintenance",
                "actions": [
                    "Retake Exercise Vital Sign to measure improvement",
                    "Find activities you enjoy — adherence > optimization",
                    "Plan for obstacles: what will you do when motivation dips?"
                ]
            }
        ]
    },
    "nutrition_basics": {
        "name": "Nutrition Basics Protocol (Mediterranean/DASH)",
        "pillar": "nutrition",
        "description": "4-week gradual transition toward Mediterranean/DASH dietary pattern — the two diets with the strongest cardiovascular evidence.",
        "citation": "Estruch R, et al. Primary Prevention of Cardiovascular Disease with a Mediterranean Diet Supplemented with Extra-Virgin Olive Oil or Nuts. NEJM. 2018;378(25):e34.",
        "duration_weeks": 4,
        "contraindications": [
            "Active eating disorder (refer to specialized care)",
            "Severe food allergies requiring specialized diet",
            "Renal diet restrictions (need dietitian guidance)"
        ],
        "weeks": [
            {
                "week": 1,
                "theme": "Add, Don't Subtract",
                "actions": [
                    "Add 1 serving of vegetables to lunch AND dinner (any vegetable counts)",
                    "Eat 1 piece of fruit as a snack each day",
                    "Drink 1 extra glass of water with each meal"
                ]
            },
            {
                "week": 2,
                "theme": "Upgrade Your Fats",
                "actions": [
                    "Cook with olive oil instead of butter for one meal per day",
                    "Eat a handful of nuts (almonds, walnuts) as a daily snack",
                    "Add one fish meal this week (any fish counts)"
                ]
            },
            {
                "week": 3,
                "theme": "Whole Grains and Fiber",
                "actions": [
                    "Swap one refined grain for whole grain (brown rice, whole wheat bread)",
                    "Add beans or lentils to one meal this week",
                    "Target: 25g fiber/day (track for awareness, not perfection)"
                ]
            },
            {
                "week": 4,
                "theme": "Reduce Processed Foods",
                "actions": [
                    "Cook one more meal at home than you usually do",
                    "Replace one processed snack with fruit/nuts/yogurt",
                    "Retake dietary assessment to measure changes"
                ]
            }
        ]
    },
    "stress_reduction": {
        "name": "Stress Reduction Protocol (MBSR-Adapted)",
        "pillar": "stress",
        "description": "6-week adapted Mindfulness-Based Stress Reduction program with progressive mindfulness and relaxation techniques.",
        "citation": "Khoury B, et al. Mindfulness-based stress reduction for healthy individuals: A meta-analysis. J Psychosom Res. 2015;78(6):519-28.",
        "duration_weeks": 6,
        "contraindications": [
            "Active psychosis or severe dissociation",
            "Recent trauma without therapeutic support",
            "If stress is primarily from an unsafe situation — address safety first"
        ],
        "weeks": [
            {
                "week": 1,
                "theme": "Breath Awareness",
                "actions": [
                    "Practice 5 minutes of focused breathing each morning",
                    "Technique: breathe in for 4 counts, out for 6 counts",
                    "Notice (without judging) when your mind wanders — that IS the practice"
                ]
            },
            {
                "week": 2,
                "theme": "Body Scan",
                "actions": [
                    "Do a 10-minute body scan before bed (head to toe awareness)",
                    "Continue daily 5-minute breathing practice",
                    "Notice where you hold tension (jaw, shoulders, back)"
                ]
            },
            {
                "week": 3,
                "theme": "Mindful Moments",
                "actions": [
                    "Eat one meal mindfully: no phone, taste each bite",
                    "Take 3 conscious breaths before each meal",
                    "Walk mindfully for 5 minutes: notice feet, air, surroundings"
                ]
            },
            {
                "week": 4,
                "theme": "Stress Response Awareness",
                "actions": [
                    "Notice your stress signals (racing thoughts, tight muscles, shallow breathing)",
                    "When you notice stress, pause and take 5 deep breaths",
                    "Journal for 5 minutes before bed: what triggered stress today?"
                ]
            },
            {
                "week": 5,
                "theme": "Progressive Muscle Relaxation",
                "actions": [
                    "Practice PMR: tense and release each muscle group, 15 minutes",
                    "Use the technique when you notice stress building",
                    "Continue breath work and journaling"
                ]
            },
            {
                "week": 6,
                "theme": "Integration",
                "actions": [
                    "Retake stress assessment to measure changes",
                    "Choose 2-3 techniques that work best for you",
                    "Build a 'stress toolkit' — your go-to responses for different situations"
                ]
            }
        ]
    },
    "hydration": {
        "name": "Hydration Protocol",
        "pillar": "nutrition",
        "description": "2-week progressive hydration increase toward recommended daily intake.",
        "citation": "EFSA Panel on Dietetic Products, Nutrition and Allergies. Scientific Opinion on Dietary Reference Values for water. EFSA Journal. 2010;8(3):1459.",
        "duration_weeks": 2,
        "contraindications": [
            "Heart failure or fluid restriction (follow medical advice)",
            "Kidney disease with fluid limits"
        ],
        "weeks": [
            {
                "week": 1,
                "theme": "Baseline and Increase",
                "actions": [
                    "Track current water intake for 2 days",
                    "Add 2 glasses of water per day above your baseline",
                    "Drink one full glass first thing in the morning",
                    "Carry a water bottle everywhere"
                ]
            },
            {
                "week": 2,
                "theme": "Reaching Target",
                "actions": [
                    "Add 1-2 more glasses to reach target (8+ glasses/day)",
                    "Drink a glass of water with every meal and snack",
                    "Set phone reminders if needed",
                    "Notice changes in energy, skin, and digestion"
                ]
            }
        ]
    }
}


def recommend_protocols(profile):
    """Recommend protocols based on a patient's assessment scores.

    Returns a list of (protocol_key, reason) tuples, ordered by priority.
    """
    recommendations = []
    assessments = profile.get("assessments", [])

    # Build a map of latest assessment scores
    latest = {}
    for a in assessments:
        atype = a["type"].lower()
        latest[atype] = a

    # Sleep
    for key in latest:
        if "sleep" in key:
            a = latest[key]
            if a["score"] >= 4:  # fair or poor sleep
                recommendations.append((
                    "sleep_hygiene",
                    f"Sleep score {a['score']}/{a['max_score']} indicates room for improvement"
                ))
            break

    # Exercise
    for key in latest:
        if "exercise" in key or "evs" in key:
            a = latest[key]
            if a["score"] < 150:  # Below WHO guideline
                recommendations.append((
                    "exercise_starter",
                    f"Exercise: {a['score']} min/week (target: 150 min/week)"
                ))
            break

    # Nutrition
    for key in latest:
        if "nutrition" in key or "diet" in key:
            a = latest[key]
            if a["score"] <= 7:  # fair or needs improvement
                recommendations.append((
                    "nutrition_basics",
                    f"Dietary score {a['score']}/{a['max_score']} — Mediterranean/DASH approach can help"
                ))
            break

    # Stress
    for key in latest:
        if "stress" in key:
            a = latest[key]
            if a["score"] >= 5:  # moderate or high
                recommendations.append((
                    "stress_reduction",
                    f"Stress score {a['score']}/{a['max_score']} — MBSR techniques can help"
                ))
            break

    return recommendations


def display_protocol(protocol_key):
    """Display a protocol's full plan."""
    if protocol_key not in PROTOCOLS:
        print(f"\n  Unknown protocol: {protocol_key}")
        print(f"  Available: {', '.join(PROTOCOLS.keys())}\n")
        return

    p = PROTOCOLS[protocol_key]
    print(f"\n  {'='*60}")
    print(f"  {p['name']}")
    print(f"  {'='*60}")
    print(f"  {p['description']}")
    print(f"  Citation: {p['citation']}")
    print(f"  Duration: {p['duration_weeks']} weeks")

    if p["contraindications"]:
        print(f"\n  Contraindications:")
        for c in p["contraindications"]:
            print(f"    - {c}")

    for week in p["weeks"]:
        print(f"\n  Week {week['week']}: {week['theme']}")
        print(f"  {'─'*50}")
        for action in week["actions"]:
            print(f"    * {action}")

    print(f"\n  {'='*60}\n")


def get_weekly_actions(protocol_key, week_number):
    """Get specific actions for a given week of a protocol."""
    if protocol_key not in PROTOCOLS:
        return None
    weeks = PROTOCOLS[protocol_key]["weeks"]
    for week in weeks:
        if week["week"] == week_number:
            return week
    return None


def display_recommendations(profile):
    """Display protocol recommendations based on assessments."""
    recs = recommend_protocols(profile)

    if not recs:
        if not profile.get("assessments"):
            print("\n  Run /assess or /intake first to get personalized protocol recommendations.\n")
        else:
            print("\n  Your assessment scores look good! No specific protocols recommended at this time.\n")
        return

    print(f"\n  Recommended Protocols")
    print(f"  {'='*50}")
    for i, (key, reason) in enumerate(recs):
        p = PROTOCOLS[key]
        print(f"\n  {i+1}) {p['name']}")
        print(f"     Reason: {reason}")
        print(f"     Duration: {p['duration_weeks']} weeks")

    print(f"\n  Type a number to view the full protocol, or 0 to cancel.")

    while True:
        try:
            choice = input("  > ").strip()
            idx = int(choice)
            if idx == 0:
                return
            if 1 <= idx <= len(recs):
                display_protocol(recs[idx - 1][0])
                return
            print(f"  Please enter 0-{len(recs)}.")
        except (ValueError, EOFError):
            print("  Please enter a number.")
