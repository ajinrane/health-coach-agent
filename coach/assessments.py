"""Validated clinical screening instruments for lifestyle medicine.

All instruments here are validated, publicly available screening tools
commonly used in primary care and clinical research settings.
"""

# Each assessment is a dict with:
#   name, description, citation, questions (list of {text, options}),
#   scoring function, and interpretation thresholds.

ASSESSMENTS = {
    "phq2": {
        "name": "PHQ-2 (Depression Screen)",
        "description": "Two-item Patient Health Questionnaire — validated depression screening tool used in primary care.",
        "citation": "Kroenke K, Spitzer RL, Williams JB. The Patient Health Questionnaire-2. Medical Care. 2003;41(11):1284-92.",
        "timeframe": "Over the last 2 weeks, how often have you been bothered by:",
        "questions": [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless"
        ],
        "options": [
            ("Not at all", 0),
            ("Several days", 1),
            ("More than half the days", 2),
            ("Nearly every day", 3)
        ],
        "max_score": 6,
        "thresholds": [
            (0, 2, "low", "Negative screen. No further depression screening indicated."),
            (3, 6, "elevated", "Positive screen. Consider full PHQ-9 and professional follow-up.")
        ]
    },
    "gad2": {
        "name": "GAD-2 (Anxiety Screen)",
        "description": "Two-item Generalized Anxiety Disorder scale — validated anxiety screening tool.",
        "citation": "Kroenke K, Spitzer RL, Williams JB, et al. Anxiety disorders in primary care. Arch Intern Med. 2007;167(11):1092-7.",
        "timeframe": "Over the last 2 weeks, how often have you been bothered by:",
        "questions": [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying"
        ],
        "options": [
            ("Not at all", 0),
            ("Several days", 1),
            ("More than half the days", 2),
            ("Nearly every day", 3)
        ],
        "max_score": 6,
        "thresholds": [
            (0, 2, "low", "Negative screen. No further anxiety screening indicated."),
            (3, 6, "elevated", "Positive screen. Consider full GAD-7 and professional follow-up.")
        ]
    },
    "evs": {
        "name": "Exercise Vital Sign (EVS)",
        "description": "Two-question exercise screening used in clinical settings to assess physical activity levels.",
        "citation": "Coleman KJ, et al. Initial validation of an exercise vital sign in electronic medical records. Med Sci Sports Exerc. 2012;44(11):2071-6.",
        "timeframe": "Thinking about a typical week:",
        "questions": [
            "On average, how many days per week do you engage in moderate to vigorous exercise (like a brisk walk)?",
            "On average, how many minutes do you exercise at this level per session?"
        ],
        "options": None,  # Free-form numeric input
        "max_score": None,  # Calculated as days * minutes
        "thresholds": [
            (0, 0, "inactive", "No regular exercise. Start with 10-minute daily walks."),
            (1, 89, "insufficient", "Below recommended 150 min/week. Gradually increase duration or frequency."),
            (90, 149, "approaching", "Close to target. Small increases will meet the 150 min/week guideline."),
            (150, 9999, "meeting", "Meeting or exceeding the 150 min/week guideline. Maintain and consider adding variety.")
        ]
    },
    "sleep": {
        "name": "Sleep Quality Screen",
        "description": "Brief sleep quality assessment based on Pittsburgh Sleep Quality Index (PSQI) domains.",
        "citation": "Buysse DJ, et al. The Pittsburgh Sleep Quality Index. Psychiatry Research. 1989;28(2):193-213.",
        "timeframe": "Over the past month:",
        "questions": [
            "How would you rate your overall sleep quality?",
            "How long (in minutes) does it usually take you to fall asleep?",
            "How many hours of actual sleep do you get per night?",
            "How often do you have trouble sleeping because you wake up in the middle of the night or early morning?"
        ],
        "options": None,  # Mixed input types
        "max_score": 12,
        "thresholds": [
            (0, 3, "good", "Sleep quality appears adequate. Maintain current habits."),
            (4, 6, "fair", "Some sleep difficulties. Targeted sleep hygiene improvements recommended."),
            (7, 12, "poor", "Significant sleep difficulties. Consider sleep hygiene protocol and professional evaluation.")
        ]
    },
    "nutrition": {
        "name": "Brief Dietary Assessment",
        "description": "Quick dietary pattern screen based on key indicators of diet quality.",
        "citation": "Adapted from Mediterranean Diet Adherence Screener (MEDAS). Schröder H, et al. J Nutr. 2011;141(6):1140-5.",
        "timeframe": "Thinking about your typical eating pattern:",
        "questions": [
            "How many servings of fruits and vegetables do you eat per day? (1 serving = 1 cup raw or 1/2 cup cooked)",
            "How many times per week do you eat fast food or highly processed meals?",
            "How many glasses of water do you drink per day?",
            "How often do you eat fish, beans, or nuts per week?"
        ],
        "options": None,
        "max_score": 12,
        "thresholds": [
            (0, 3, "needs_improvement", "Diet quality is low. Start with one daily fruit or vegetable addition."),
            (4, 7, "fair", "Some healthy patterns. Build on existing strengths."),
            (8, 12, "good", "Generally healthy dietary pattern. Fine-tune as needed.")
        ]
    },
    "stress": {
        "name": "Perceived Stress Screen",
        "description": "Brief stress assessment based on the Perceived Stress Scale (PSS).",
        "citation": "Cohen S, Kamarck T, Mermelstein R. A global measure of perceived stress. J Health Soc Behav. 1983;24(4):385-96.",
        "timeframe": "In the last month:",
        "questions": [
            "How often have you felt that you were unable to control the important things in your life?",
            "How often have you felt confident about your ability to handle personal problems?",
            "How often have you felt that things were going your way?",
            "How often have you felt difficulties were piling up so high that you could not overcome them?"
        ],
        "options": [
            ("Never", 0),
            ("Almost never", 1),
            ("Sometimes", 2),
            ("Fairly often", 3),
            ("Very often", 4)
        ],
        "max_score": 16,
        "thresholds": [
            (0, 4, "low", "Low perceived stress. Maintain current coping strategies."),
            (5, 9, "moderate", "Moderate stress. Stress management techniques recommended."),
            (10, 16, "high", "High perceived stress. Consider stress reduction program and professional support.")
        ]
    }
}


def get_assessment_list():
    """Return list of available assessments."""
    return [(key, a["name"], a["description"]) for key, a in ASSESSMENTS.items()]


def run_assessment(assessment_key):
    """Run a clinical assessment interactively. Returns (score, max_score, interpretation, details)."""
    if assessment_key not in ASSESSMENTS:
        return None

    assessment = ASSESSMENTS[assessment_key]
    print(f"\n{'='*60}")
    print(f"  {assessment['name']}")
    print(f"  {assessment['citation']}")
    print(f"{'='*60}")
    print(f"\n{assessment['timeframe']}\n")

    total_score = 0
    details = {}

    if assessment_key == "evs":
        total_score, details = _run_evs(assessment)
    elif assessment_key == "sleep":
        total_score, details = _run_sleep(assessment)
    elif assessment_key == "nutrition":
        total_score, details = _run_nutrition(assessment)
    elif assessment["options"]:
        total_score, details = _run_likert(assessment)
    else:
        return None

    max_score = assessment["max_score"] or total_score
    interpretation = _interpret(total_score, assessment["thresholds"])

    print(f"\n{'─'*40}")
    print(f"  Score: {total_score}/{max_score}")
    print(f"  Result: {interpretation}")
    print(f"{'─'*40}\n")

    return total_score, max_score, interpretation, details


def _run_likert(assessment):
    """Run a Likert-scale assessment (PHQ-2, GAD-2, stress)."""
    total = 0
    details = {}
    options = assessment["options"]

    for i, question in enumerate(assessment["questions"]):
        print(f"  {i+1}. {question}")
        for j, (label, value) in enumerate(options):
            print(f"     {j}) {label}")

        while True:
            try:
                choice = int(input(f"     > ").strip())
                if 0 <= choice < len(options):
                    score = options[choice][1]
                    # Reverse score items 2 and 3 for stress assessment (positive items)
                    if assessment is ASSESSMENTS.get("stress") and i in [1, 2]:
                        score = options[-1][1] - score
                    total += score
                    details[f"q{i+1}"] = {"question": question, "answer": options[choice][0], "score": score}
                    break
                print("     Please enter a valid option number.")
            except (ValueError, EOFError):
                print("     Please enter a number.")
        print()

    return total, details


def _run_evs(assessment):
    """Run the Exercise Vital Sign assessment."""
    questions = assessment["questions"]

    print(f"  1. {questions[0]}")
    while True:
        try:
            days = int(input("     Days per week (0-7): ").strip())
            if 0 <= days <= 7:
                break
            print("     Please enter 0-7.")
        except (ValueError, EOFError):
            print("     Please enter a number.")

    print(f"\n  2. {questions[1]}")
    while True:
        try:
            minutes = int(input("     Minutes per session: ").strip())
            if 0 <= minutes <= 300:
                break
            print("     Please enter 0-300.")
        except (ValueError, EOFError):
            print("     Please enter a number.")

    total = days * minutes
    details = {"days_per_week": days, "minutes_per_session": minutes, "weekly_minutes": total}
    return total, details


def _run_sleep(assessment):
    """Run the sleep quality screen."""
    total = 0
    details = {}

    # Q1: Overall quality (0-3)
    print(f"  1. {assessment['questions'][0]}")
    print("     0) Very good")
    print("     1) Fairly good")
    print("     2) Fairly bad")
    print("     3) Very bad")
    while True:
        try:
            q1 = int(input("     > ").strip())
            if 0 <= q1 <= 3:
                total += q1
                details["quality_rating"] = q1
                break
            print("     Please enter 0-3.")
        except (ValueError, EOFError):
            print("     Please enter a number.")

    # Q2: Sleep latency
    print(f"\n  2. {assessment['questions'][1]}")
    while True:
        try:
            latency = int(input("     Minutes: ").strip())
            if latency >= 0:
                score = 0 if latency <= 15 else (1 if latency <= 30 else (2 if latency <= 60 else 3))
                total += score
                details["sleep_latency_min"] = latency
                details["sleep_latency_score"] = score
                break
            print("     Please enter a non-negative number.")
        except (ValueError, EOFError):
            print("     Please enter a number.")

    # Q3: Hours of sleep
    print(f"\n  3. {assessment['questions'][2]}")
    while True:
        try:
            hours = float(input("     Hours: ").strip())
            if 0 <= hours <= 24:
                score = 0 if hours >= 7 else (1 if hours >= 6 else (2 if hours >= 5 else 3))
                total += score
                details["sleep_hours"] = hours
                details["sleep_duration_score"] = score
                break
            print("     Please enter 0-24.")
        except (ValueError, EOFError):
            print("     Please enter a number.")

    # Q4: Night awakenings
    print(f"\n  4. {assessment['questions'][3]}")
    print("     0) Not during the past month")
    print("     1) Less than once a week")
    print("     2) Once or twice a week")
    print("     3) Three or more times a week")
    while True:
        try:
            q4 = int(input("     > ").strip())
            if 0 <= q4 <= 3:
                total += q4
                details["night_awakenings"] = q4
                break
            print("     Please enter 0-3.")
        except (ValueError, EOFError):
            print("     Please enter a number.")

    return total, details


def _run_nutrition(assessment):
    """Run the brief dietary assessment."""
    total = 0
    details = {}

    # Q1: Fruits and vegetables (0-3)
    print(f"  1. {assessment['questions'][0]}")
    while True:
        try:
            fv = int(input("     Servings per day: ").strip())
            if fv >= 0:
                score = 0 if fv < 2 else (1 if fv < 4 else (2 if fv < 6 else 3))
                total += score
                details["fruit_veg_servings"] = fv
                break
            print("     Please enter a non-negative number.")
        except (ValueError, EOFError):
            print("     Please enter a number.")

    # Q2: Fast food (reverse scored, 0-3)
    print(f"\n  2. {assessment['questions'][1]}")
    while True:
        try:
            ff = int(input("     Times per week: ").strip())
            if ff >= 0:
                score = 3 if ff == 0 else (2 if ff <= 1 else (1 if ff <= 3 else 0))
                total += score
                details["fast_food_per_week"] = ff
                break
            print("     Please enter a non-negative number.")
        except (ValueError, EOFError):
            print("     Please enter a number.")

    # Q3: Water intake (0-3)
    print(f"\n  3. {assessment['questions'][2]}")
    while True:
        try:
            water = int(input("     Glasses per day: ").strip())
            if water >= 0:
                score = 0 if water < 4 else (1 if water < 6 else (2 if water < 8 else 3))
                total += score
                details["water_glasses"] = water
                break
            print("     Please enter a non-negative number.")
        except (ValueError, EOFError):
            print("     Please enter a number.")

    # Q4: Healthy proteins (0-3)
    print(f"\n  4. {assessment['questions'][3]}")
    while True:
        try:
            hp = int(input("     Times per week: ").strip())
            if hp >= 0:
                score = 0 if hp < 1 else (1 if hp < 3 else (2 if hp < 5 else 3))
                total += score
                details["healthy_protein_per_week"] = hp
                break
            print("     Please enter a non-negative number.")
        except (ValueError, EOFError):
            print("     Please enter a number.")

    return total, details


def _interpret(score, thresholds):
    """Look up interpretation for a score."""
    for low, high, level, text in thresholds:
        if low <= score <= high:
            return text
    return "Unable to interpret score."
