"""Safety screening — red flag detection in patient conversations.

Monitors for indicators of clinical emergencies, suicidal ideation,
disordered eating, and other concerns that require immediate professional referral.
"""

import re

# Red flag patterns — these trigger immediate safety responses
RED_FLAGS = {
    "suicidal_ideation": {
        "patterns": [
            r"\b(want to|going to|thinking about|plan to)\s*(die|kill myself|end it|end my life)\b",
            r"\b(suicid|self[- ]?harm|hurt myself|cut myself)\b",
            r"\b(no reason to live|better off dead|wish i was dead|don'?t want to be alive)\b",
            r"\b(goodbye|farewell)\b.*\b(forever|final|last)\b",
        ],
        "severity": "critical",
        "response": (
            "\n  !! SAFETY ALERT !!\n"
            "  I'm concerned about what you've shared. Your safety matters most.\n\n"
            "  Please reach out to one of these resources right now:\n"
            "  - 988 Suicide & Crisis Lifeline: call or text 988\n"
            "  - Crisis Text Line: text HOME to 741741\n"
            "  - Emergency: call 911\n\n"
            "  I'm an AI coach, not a crisis counselor. A trained professional\n"
            "  can give you the support you need right now.\n"
        )
    },
    "disordered_eating": {
        "patterns": [
            r"\b(purg|binge and purg|make myself (throw up|vomit)|laxative)\b",
            r"\b(anorexi|bulimi)\b",
            r"\b(haven'?t eaten|not eating|starving myself|fasting)\b.*(days|week)",
            r"\b(hate my body|disgusting|fat|ugly)\b.*(eat|food|weight)",
        ],
        "severity": "high",
        "response": (
            "\n  I want to pause here. What you're describing sounds like it could\n"
            "  benefit from specialized support beyond lifestyle coaching.\n\n"
            "  I'd recommend talking to your doctor or contacting:\n"
            "  - National Eating Disorders Association: 1-800-931-2237\n"
            "  - NEDA text line: text 'NEDA' to 741741\n\n"
            "  Eating concerns are medical issues, not willpower issues.\n"
            "  A professional can help you build a healthy relationship with food.\n"
        )
    },
    "substance_crisis": {
        "patterns": [
            r"\b(overdos|od'?d|too (many|much) (pills|drugs|medication))\b",
            r"\b(withdrawal|detox|shaking|seizure)\b.*(alcohol|drug|opioid|benzo)",
            r"\b(can'?t stop|addicted|dependent)\b.*(drink|alcohol|drug|pills|opioid)",
        ],
        "severity": "high",
        "response": (
            "\n  What you're describing needs medical attention — substance-related\n"
            "  concerns can be dangerous to manage alone.\n\n"
            "  Please contact:\n"
            "  - SAMHSA National Helpline: 1-800-662-4357 (free, 24/7)\n"
            "  - Your doctor or nearest emergency room\n\n"
            "  Getting help is a sign of strength, not weakness.\n"
        )
    },
    "medical_emergency": {
        "patterns": [
            r"\b(chest\s+(pain|hurts?|pressure|tight|ache)|can'?t breathe|difficulty breathing|crushing pressure|short(ness)? of breath)\b",
            r"\b(stroke|numbness|slurred speech|vision loss|face droop)\b",
            r"\b(passing out|fainted|unconscious|seizure|collaps)\b",
            r"\b(severe\s+(pain|bleeding|allergic|headache))\b",
        ],
        "severity": "critical",
        "response": (
            "\n  !! This sounds like it could be a medical emergency. !!\n\n"
            "  Please call 911 or go to your nearest emergency room immediately.\n"
            "  Do not wait — these symptoms need urgent medical evaluation.\n\n"
            "  I'm a coaching tool, not a substitute for emergency medical care.\n"
        )
    }
}


def screen_message(message):
    """Screen a patient message for red flags.

    Returns a list of triggered flags: [{"category": str, "severity": str, "response": str}]
    Returns empty list if no concerns detected.
    """
    triggered = []
    text = message.lower()

    for category, config in RED_FLAGS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                triggered.append({
                    "category": category,
                    "severity": config["severity"],
                    "response": config["response"]
                })
                break  # One match per category is enough

    return triggered


def handle_safety_flags(flags):
    """Display safety responses for triggered flags.

    Returns True if conversation should pause for safety, False otherwise.
    """
    if not flags:
        return False

    critical = any(f["severity"] == "critical" for f in flags)

    for flag in flags:
        print(flag["response"])

    if critical:
        print("  The coach will continue when you're ready, but please prioritize")
        print("  reaching out to the resources above first.\n")

    return critical
