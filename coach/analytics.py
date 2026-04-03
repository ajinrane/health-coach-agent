"""Conversation-level analytics for clinical research.

Provides quantitative measures derived from coaching session transcripts:
  - Readiness to Change scoring (Transtheoretical Model)
  - Engagement metrics (message count, length, question ratio, duration)
  - Sentiment tracking (keyword-based, no ML dependencies)
  - Topic extraction (six-pillar coverage)
  - Motivational Interviewing quality (OARS technique detection)

All functions operate on either a single session dict or across all
sessions for a patient profile.  No external dependencies beyond stdlib.

References:
  Prochaska JO, DiClemente CC. Stages and processes of self-change of
    smoking. J Consult Clin Psychol. 1983;51(4):519-33.
  Miller WR, Rollnick S. Motivational Interviewing (3rd ed). Guilford, 2013.
"""

import math
import re
from datetime import datetime

from .session import list_sessions, load_session


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PILLARS = ["sleep", "nutrition", "exercise", "stress", "connection", "substances"]

# Transtheoretical Model — language markers for each stage.
# Each list contains (pattern, weight) tuples.  Patterns are compiled once.
_STAGE_MARKERS = {
    "precontemplation": [
        (r"\bi\s+don'?t\s+(have|see)\s+a\s+problem\b", 2),
        (r"\bi'?m\s+fine\b", 1),
        (r"\bno\s+need\s+to\s+change\b", 2),
        (r"\beveryone\s+(does|drinks|eats)\b", 1),
        (r"\bnot\s+ready\b", 2),
        (r"\bleave\s+me\s+alone\b", 1),
        (r"\bdon'?t\s+want\s+to\b", 1),
        (r"\bnot\s+a\s+(big\s+)?deal\b", 1),
        (r"\bwhy\s+should\s+i\b", 1),
        (r"\bi\s+can\s+stop\s+whenever\b", 2),
    ],
    "contemplation": [
        (r"\bmaybe\s+i\s+should\b", 2),
        (r"\bi'?ve\s+been\s+thinking\s+about\b", 2),
        (r"\bpart\s+of\s+me\b", 2),
        (r"\bon\s+the\s+other\s+hand\b", 1),
        (r"\bi\s+know\s+i\s+(need|should)\b", 2),
        (r"\bbut\s+i'?m\s+not\s+sure\b", 1),
        (r"\bsometime\b", 1),
        (r"\bpros?\s+and\s+cons?\b", 2),
        (r"\bweighing\b", 1),
        (r"\bam(bivalent|bivalence)\b", 2),
        (r"\bi\s+want\s+to\s+but\b", 2),
    ],
    "preparation": [
        (r"\bi'?m\s+(going|planning|ready)\s+to\b", 2),
        (r"\bnext\s+week\b", 1),
        (r"\bi\s+(signed\s+up|enrolled|registered)\b", 2),
        (r"\bi\s+bought\b", 1),
        (r"\bi\s+set\s+(a\s+)?goal\b", 2),
        (r"\bwhat\s+(steps|should\s+i)\b", 2),
        (r"\bhow\s+do\s+i\s+start\b", 2),
        (r"\bi\s+made\s+an?\s+appointment\b", 2),
        (r"\bi'?m\s+going\s+to\s+try\b", 1),
        (r"\baction\s+plan\b", 2),
    ],
    "action": [
        (r"\bi\s+(started|began|have\s+been)\b", 2),
        (r"\bthis\s+week\s+i\b", 2),
        (r"\bi'?ve\s+been\s+(doing|eating|walking|running|sleeping|exercising)\b", 2),
        (r"\bi\s+quit\b", 2),
        (r"\bi\s+stopped\b", 2),
        (r"\bi'?m\s+(now|currently)\b", 1),
        (r"\bday\s+\d+\b", 1),
        (r"\bso\s+far\s+so\s+good\b", 1),
        (r"\bi\s+did\s+(it|that)\b", 1),
        (r"\bsince\s+i\s+started\b", 2),
    ],
    "maintenance": [
        (r"\bfor\s+(\d+\s+)?(months?|years?)\b", 2),
        (r"\bkeeping\s+(it\s+)?up\b", 2),
        (r"\bhabit\b", 1),
        (r"\broutine\b", 1),
        (r"\bconsistently?\b", 2),
        (r"\bstill\s+(doing|going|eating|sleeping)\b", 2),
        (r"\bpart\s+of\s+my\s+life(style)?\b", 2),
        (r"\blong[\s-]?term\b", 1),
        (r"\bnew\s+normal\b", 2),
        (r"\bi\s+don'?t\s+even\s+think\s+about\s+it\b", 2),
    ],
}

# Pre-compile all stage patterns
_COMPILED_STAGE_MARKERS = {}
for _stage, _patterns in _STAGE_MARKERS.items():
    _COMPILED_STAGE_MARKERS[_stage] = [
        (re.compile(pat, re.IGNORECASE), weight) for pat, weight in _patterns
    ]


# Sentiment lexicons — deliberately compact, no ML needed.
_POSITIVE_WORDS = {
    "good", "great", "better", "best", "happy", "glad", "excited", "hopeful",
    "motivated", "proud", "accomplished", "improved", "progress", "grateful",
    "thankful", "confident", "strong", "amazing", "wonderful", "fantastic",
    "awesome", "excellent", "love", "enjoy", "energized", "optimistic",
    "encouraged", "relieved", "calm", "peaceful", "refreshed", "thriving",
    "determined", "committed", "success", "achieved", "milestone",
}

_NEGATIVE_WORDS = {
    "bad", "worse", "worst", "sad", "unhappy", "depressed", "anxious",
    "worried", "stressed", "tired", "exhausted", "frustrated", "angry",
    "hopeless", "helpless", "overwhelmed", "struggling", "failed", "painful",
    "difficult", "hard", "terrible", "awful", "miserable", "lonely",
    "isolated", "guilty", "ashamed", "scared", "afraid", "nervous",
    "upset", "disappointed", "discouraged", "stuck", "can't", "impossible",
    "never", "hate", "quit", "relapsed", "setback", "lapsed",
}


# Topic keyword maps — map to the six pillars.
_TOPIC_KEYWORDS = {
    "sleep": {
        "sleep", "sleeping", "insomnia", "nap", "napping", "rest", "resting",
        "bed", "bedtime", "wake", "waking", "tired", "fatigue", "melatonin",
        "dream", "snore", "snoring", "apnea", "circadian", "pillow",
        "mattress", "alarm", "oversleep", "nighttime", "sleepy",
    },
    "nutrition": {
        "eat", "eating", "food", "diet", "meal", "meals", "breakfast",
        "lunch", "dinner", "snack", "snacking", "calorie", "calories",
        "protein", "carb", "carbs", "fat", "fats", "sugar", "fruit",
        "vegetable", "vegetables", "cooking", "recipe", "water", "hydration",
        "vitamin", "supplement", "fiber", "portion", "hungry", "hunger",
        "appetite", "fast", "fasting", "nutrition", "nutrient", "organic",
    },
    "exercise": {
        "exercise", "exercising", "workout", "gym", "run", "running",
        "walk", "walking", "jog", "jogging", "swim", "swimming", "bike",
        "biking", "cycling", "yoga", "stretch", "stretching", "lift",
        "lifting", "weights", "strength", "cardio", "steps", "active",
        "activity", "hike", "hiking", "sport", "sports", "fitness",
        "training", "pushup", "squat", "plank", "marathon",
    },
    "stress": {
        "stress", "stressed", "anxiety", "anxious", "worry", "worrying",
        "overwhelm", "overwhelmed", "relax", "relaxation", "meditation",
        "meditate", "mindful", "mindfulness", "breathe", "breathing",
        "therapy", "therapist", "counselor", "cope", "coping", "burnout",
        "panic", "tension", "calm", "journal", "journaling", "gratitude",
        "mental", "pressure",
    },
    "connection": {
        "friend", "friends", "family", "social", "relationship",
        "relationships", "partner", "spouse", "community", "church",
        "group", "volunteer", "volunteering", "lonely", "loneliness",
        "isolated", "isolation", "support", "belonging", "together",
        "connection", "connect", "connected", "love", "loved", "hug",
        "call", "visit", "text", "bond", "bonding",
    },
    "substances": {
        "alcohol", "drink", "drinking", "beer", "wine", "liquor", "sober",
        "sobriety", "smoke", "smoking", "cigarette", "vape", "vaping",
        "nicotine", "tobacco", "marijuana", "cannabis", "weed", "drug",
        "drugs", "caffeine", "coffee", "substance", "addiction", "addicted",
        "relapse", "recovery", "abstinence", "moderation", "binge",
    },
}


# OARS patterns for Motivational Interviewing quality scoring.
# Applied to *assistant* (coach) messages.
_OARS_PATTERNS = {
    "open_questions": [
        # Open-ended questions typically start with what/how/tell me/describe
        (re.compile(r"\bwhat\b.*\?", re.IGNORECASE), 1),
        (re.compile(r"\bhow\b.*\?", re.IGNORECASE), 1),
        (re.compile(r"\btell\s+me\s+(more\s+)?about\b", re.IGNORECASE), 1),
        (re.compile(r"\bdescribe\b.*\?", re.IGNORECASE), 1),
        (re.compile(r"\bin\s+what\s+way\b", re.IGNORECASE), 1),
        (re.compile(r"\bwhat\s+(would|does|do|did|might|could)\b.*\?", re.IGNORECASE), 1),
        (re.compile(r"\bhow\s+(would|does|do|did|might|could)\b.*\?", re.IGNORECASE), 1),
        (re.compile(r"\bwhat\s+comes\s+to\s+mind\b", re.IGNORECASE), 1),
        (re.compile(r"\bwhat\s+(are|were)\s+your\s+thoughts\b", re.IGNORECASE), 1),
    ],
    "affirmations": [
        (re.compile(r"\bthat\s+takes?\s+(a\s+lot\s+of\s+)?courage\b", re.IGNORECASE), 2),
        (re.compile(r"\bi\s+appreciate\b", re.IGNORECASE), 1),
        (re.compile(r"\bthat'?s?\s+(really\s+)?(great|wonderful|impressive|amazing)\b", re.IGNORECASE), 1),
        (re.compile(r"\byou('?ve|\s+have)\s+(shown|demonstrated|made)\b", re.IGNORECASE), 2),
        (re.compile(r"\byou\s+should\s+be\s+proud\b", re.IGNORECASE), 2),
        (re.compile(r"\bit\s+sounds?\s+like\s+you('?ve|\s+have)\s+(really|worked)\b", re.IGNORECASE), 2),
        (re.compile(r"\bstrong\s+step\b", re.IGNORECASE), 2),
        (re.compile(r"\bgreat\s+(job|work|effort|progress)\b", re.IGNORECASE), 1),
        (re.compile(r"\bthat\s+(shows?|reflect)\b", re.IGNORECASE), 1),
        (re.compile(r"\byour\s+(strength|commitment|determination|dedication)\b", re.IGNORECASE), 2),
    ],
    "reflections": [
        (re.compile(r"\bit\s+sounds?\s+like\b", re.IGNORECASE), 2),
        (re.compile(r"\bso\s+(what\s+)?you'?re\s+saying\b", re.IGNORECASE), 2),
        (re.compile(r"\bif\s+i'?m\s+hearing\s+you\b", re.IGNORECASE), 2),
        (re.compile(r"\byou('?re|\s+are)\s+feeling\b", re.IGNORECASE), 2),
        (re.compile(r"\bit\s+seems?\s+like\b", re.IGNORECASE), 1),
        (re.compile(r"\byou\s+(mentioned|said|shared|described|expressed)\b", re.IGNORECASE), 1),
        (re.compile(r"\bon\s+one\s+hand\b.*\bon\s+the\s+other\b", re.IGNORECASE), 2),
        (re.compile(r"\bso\s+for\s+you\b", re.IGNORECASE), 1),
        (re.compile(r"\bwhat\s+i'?m\s+hearing\b", re.IGNORECASE), 2),
        (re.compile(r"\bi\s+hear\s+you\s+saying\b", re.IGNORECASE), 2),
    ],
    "summaries": [
        (re.compile(r"\blet\s+me\s+(summarize|recap|sum\s+up)\b", re.IGNORECASE), 2),
        (re.compile(r"\bso\s+far\s+(we'?ve|you'?ve|today)\b", re.IGNORECASE), 2),
        (re.compile(r"\bto\s+summarize\b", re.IGNORECASE), 2),
        (re.compile(r"\boverall\b.*\bwe('?ve|\s+have)\s+(discussed|talked|covered)\b", re.IGNORECASE), 2),
        (re.compile(r"\blooking\s+back\s+at\s+(our|this)\b", re.IGNORECASE), 1),
        (re.compile(r"\bhere'?s?\s+what\s+(i'?ve|we'?ve)\s+(heard|covered|discussed)\b", re.IGNORECASE), 2),
        (re.compile(r"\bin\s+summary\b", re.IGNORECASE), 2),
        (re.compile(r"\bto\s+wrap\s+up\b", re.IGNORECASE), 1),
    ],
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _tokenize(text):
    """Lowercase word tokenization (alphanumeric + apostrophes)."""
    return re.findall(r"[a-z'\-]+", text.lower())


def _mean(values):
    """Arithmetic mean, returns 0.0 for empty lists."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def _sd(values):
    """Sample standard deviation, returns 0.0 for < 2 values."""
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def _safe_ratio(numerator, denominator, default=0.0):
    """Division that never raises ZeroDivisionError."""
    if denominator == 0:
        return default
    return numerator / denominator


def _parse_iso(ts):
    """Parse an ISO datetime string, returning None on failure."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def _patient_messages(session):
    """Extract all patient (user) messages from a session."""
    return [ex["user"] for ex in session.get("conversation", []) if ex.get("user")]


def _coach_messages(session):
    """Extract all coach (assistant) messages from a session."""
    return [ex["assistant"] for ex in session.get("conversation", []) if ex.get("assistant")]


def _all_sessions_for_patient(profile):
    """Load all sessions referenced in a patient profile."""
    sessions = []
    for sid in profile.get("sessions", []):
        s = load_session(sid)
        if s:
            sessions.append(s)
    # Sort chronologically
    return sorted(sessions, key=lambda s: s.get("start_time", ""))


# ---------------------------------------------------------------------------
# 1. Readiness to Change (Transtheoretical Model)
# ---------------------------------------------------------------------------

def score_readiness_session(session):
    """Score a single session for readiness-to-change stage indicators.

    Returns a dict with:
      - stage_scores: {stage_name: weighted_score}
      - dominant_stage: the stage with highest score (or "indeterminate")
      - confidence: 0.0-1.0 indicating how clearly one stage dominates
      - matches: {stage_name: [matched_phrase, ...]} for auditability
    """
    patient_text = " ".join(_patient_messages(session))
    stage_scores = {}
    matches = {}

    for stage, compiled_patterns in _COMPILED_STAGE_MARKERS.items():
        total_weight = 0
        found = []
        for pattern, weight in compiled_patterns:
            hits = pattern.findall(patient_text)
            if hits:
                total_weight += weight * len(hits)
                found.extend(hits if isinstance(hits[0], str) else [h[0] for h in hits])
        stage_scores[stage] = total_weight
        matches[stage] = found

    total = sum(stage_scores.values())
    if total == 0:
        return {
            "stage_scores": stage_scores,
            "dominant_stage": "indeterminate",
            "confidence": 0.0,
            "matches": matches,
        }

    dominant = max(stage_scores, key=stage_scores.get)
    # Confidence: proportion of total score captured by dominant stage
    confidence = round(stage_scores[dominant] / total, 2)

    return {
        "stage_scores": stage_scores,
        "dominant_stage": dominant,
        "confidence": confidence,
        "matches": matches,
    }


def score_readiness_longitudinal(profile):
    """Track readiness-to-change stage across all sessions for a patient.

    Returns a list of dicts ordered chronologically:
      [{session_id, date, dominant_stage, confidence, stage_scores}, ...]

    Useful for plotting stage progression over time in a research paper.
    """
    results = []
    for session in _all_sessions_for_patient(profile):
        r = score_readiness_session(session)
        results.append({
            "session_id": session["session_id"],
            "date": (session.get("start_time") or "")[:10],
            "dominant_stage": r["dominant_stage"],
            "confidence": r["confidence"],
            "stage_scores": r["stage_scores"],
        })
    return results


# ---------------------------------------------------------------------------
# 2. Engagement Metrics
# ---------------------------------------------------------------------------

def engagement_metrics_session(session):
    """Compute engagement metrics for a single session.

    Returns a dict with:
      - message_count: total exchanges
      - patient_message_count / coach_message_count
      - patient_avg_length: mean character count of patient messages
      - coach_avg_length: mean character count of coach messages
      - patient_avg_word_count: mean word count of patient messages
      - question_count: patient messages ending with '?'
      - statement_count: patient messages not ending with '?'
      - question_ratio: questions / total patient messages
      - session_duration_min: minutes between first and last timestamp
      - messages_per_minute: message rate
    """
    conversation = session.get("conversation", [])
    patient_msgs = _patient_messages(session)
    coach_msgs = _coach_messages(session)

    patient_lengths = [len(m) for m in patient_msgs]
    coach_lengths = [len(m) for m in coach_msgs]
    patient_word_counts = [len(_tokenize(m)) for m in patient_msgs]

    questions = sum(1 for m in patient_msgs if m.strip().endswith("?"))
    statements = len(patient_msgs) - questions

    # Duration
    timestamps = [_parse_iso(ex.get("timestamp")) for ex in conversation]
    timestamps = [t for t in timestamps if t is not None]
    if len(timestamps) >= 2:
        duration_sec = (max(timestamps) - min(timestamps)).total_seconds()
    else:
        # Fall back to session start/end
        start = _parse_iso(session.get("start_time"))
        end = _parse_iso(session.get("end_time"))
        duration_sec = (end - start).total_seconds() if start and end else 0

    duration_min = round(duration_sec / 60, 1) if duration_sec > 0 else 0

    return {
        "message_count": len(conversation),
        "patient_message_count": len(patient_msgs),
        "coach_message_count": len(coach_msgs),
        "patient_avg_length": round(_mean(patient_lengths), 1),
        "coach_avg_length": round(_mean(coach_lengths), 1),
        "patient_avg_word_count": round(_mean(patient_word_counts), 1),
        "question_count": questions,
        "statement_count": statements,
        "question_ratio": round(_safe_ratio(questions, len(patient_msgs)), 2),
        "session_duration_min": duration_min,
        "messages_per_minute": round(
            _safe_ratio(len(conversation), duration_min), 2
        ) if duration_min > 0 else 0,
    }


def engagement_metrics_longitudinal(profile):
    """Engagement metrics across all sessions for a patient.

    Returns a list of per-session metric dicts ordered chronologically,
    plus an 'aggregate' dict with means and SDs across sessions.
    """
    per_session = []
    for session in _all_sessions_for_patient(profile):
        metrics = engagement_metrics_session(session)
        metrics["session_id"] = session["session_id"]
        metrics["date"] = (session.get("start_time") or "")[:10]
        per_session.append(metrics)

    # Aggregate
    if per_session:
        agg_keys = [
            "message_count", "patient_avg_length", "patient_avg_word_count",
            "question_ratio", "session_duration_min",
        ]
        aggregate = {}
        for key in agg_keys:
            values = [s[key] for s in per_session]
            aggregate[key] = {
                "mean": round(_mean(values), 2),
                "sd": round(_sd(values), 2),
                "min": min(values),
                "max": max(values),
            }
        aggregate["total_sessions"] = len(per_session)
        aggregate["total_messages"] = sum(s["message_count"] for s in per_session)
    else:
        aggregate = {}

    return {"per_session": per_session, "aggregate": aggregate}


# ---------------------------------------------------------------------------
# 3. Sentiment Tracking
# ---------------------------------------------------------------------------

def sentiment_score_message(text):
    """Score a single message for sentiment.

    Returns a dict:
      - positive_count: number of positive keywords found
      - negative_count: number of negative keywords found
      - sentiment: "positive" | "negative" | "neutral" | "mixed"
      - valence: float in [-1, 1], computed as (pos - neg) / (pos + neg)
    """
    words = set(_tokenize(text))
    pos = len(words & _POSITIVE_WORDS)
    neg = len(words & _NEGATIVE_WORDS)
    total = pos + neg

    if total == 0:
        sentiment = "neutral"
        valence = 0.0
    elif pos > 0 and neg > 0 and abs(pos - neg) <= 1:
        sentiment = "mixed"
        valence = round((pos - neg) / total, 2)
    elif pos > neg:
        sentiment = "positive"
        valence = round((pos - neg) / total, 2)
    else:
        sentiment = "negative"
        valence = round((pos - neg) / total, 2)

    return {
        "positive_count": pos,
        "negative_count": neg,
        "sentiment": sentiment,
        "valence": valence,
    }


def sentiment_session(session):
    """Aggregate sentiment for all patient messages in a session.

    Returns:
      - per_message: list of sentiment dicts for each patient message
      - session_valence: mean valence across messages
      - sentiment_distribution: {positive: n, negative: n, neutral: n, mixed: n}
      - sentiment_trend: "improving" | "declining" | "stable" | "insufficient"
        (based on first-half vs second-half valence comparison)
    """
    patient_msgs = _patient_messages(session)
    per_message = [sentiment_score_message(m) for m in patient_msgs]

    valences = [s["valence"] for s in per_message]
    session_valence = round(_mean(valences), 2)

    distribution = {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0}
    for s in per_message:
        distribution[s["sentiment"]] += 1

    # Within-session trend
    if len(valences) >= 4:
        mid = len(valences) // 2
        first_half = _mean(valences[:mid])
        second_half = _mean(valences[mid:])
        diff = second_half - first_half
        if diff > 0.15:
            trend = "improving"
        elif diff < -0.15:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient"

    return {
        "per_message": per_message,
        "session_valence": session_valence,
        "sentiment_distribution": distribution,
        "sentiment_trend": trend,
    }


def sentiment_longitudinal(profile):
    """Track session-level sentiment across all sessions for a patient.

    Returns a list of {session_id, date, session_valence, distribution, trend}
    ordered chronologically.
    """
    results = []
    for session in _all_sessions_for_patient(profile):
        s = sentiment_session(session)
        results.append({
            "session_id": session["session_id"],
            "date": (session.get("start_time") or "")[:10],
            "session_valence": s["session_valence"],
            "distribution": s["sentiment_distribution"],
            "trend": s["sentiment_trend"],
        })
    return results


# ---------------------------------------------------------------------------
# 4. Topic Extraction (Six-Pillar Coverage)
# ---------------------------------------------------------------------------

def topic_coverage_session(session):
    """Identify which pillars are discussed in a session.

    Returns:
      - pillar_counts: {pillar: keyword_hit_count}
      - pillar_proportions: {pillar: proportion_of_total_hits}
      - primary_topic: pillar with most hits (or "none")
      - topics_discussed: list of pillars with > 0 hits, ordered by count
    """
    all_text = " ".join(_patient_messages(session) + _coach_messages(session))
    words = _tokenize(all_text)
    word_set = set(words)

    pillar_counts = {}
    for pillar, keywords in _TOPIC_KEYWORDS.items():
        # Count keyword occurrences (not just presence) for weight
        count = sum(1 for w in words if w in keywords)
        pillar_counts[pillar] = count

    total = sum(pillar_counts.values())
    pillar_proportions = {
        p: round(_safe_ratio(c, total), 2) for p, c in pillar_counts.items()
    }

    topics_discussed = sorted(
        [p for p, c in pillar_counts.items() if c > 0],
        key=lambda p: pillar_counts[p],
        reverse=True,
    )
    primary = topics_discussed[0] if topics_discussed else "none"

    return {
        "pillar_counts": pillar_counts,
        "pillar_proportions": pillar_proportions,
        "primary_topic": primary,
        "topics_discussed": topics_discussed,
    }


def topic_coverage_longitudinal(profile):
    """Track pillar coverage across all sessions.

    Returns:
      - per_session: [{session_id, date, pillar_counts, primary_topic}, ...]
      - aggregate_counts: {pillar: total_hits_across_all_sessions}
      - aggregate_proportions: {pillar: proportion_of_all_hits}
      - coverage_breadth: how many distinct pillars were ever discussed (0-6)
    """
    per_session = []
    aggregate_counts = {p: 0 for p in PILLARS}

    for session in _all_sessions_for_patient(profile):
        tc = topic_coverage_session(session)
        per_session.append({
            "session_id": session["session_id"],
            "date": (session.get("start_time") or "")[:10],
            "pillar_counts": tc["pillar_counts"],
            "primary_topic": tc["primary_topic"],
        })
        for p in PILLARS:
            aggregate_counts[p] += tc["pillar_counts"].get(p, 0)

    total = sum(aggregate_counts.values())
    aggregate_proportions = {
        p: round(_safe_ratio(c, total), 2) for p, c in aggregate_counts.items()
    }
    coverage_breadth = sum(1 for c in aggregate_counts.values() if c > 0)

    return {
        "per_session": per_session,
        "aggregate_counts": aggregate_counts,
        "aggregate_proportions": aggregate_proportions,
        "coverage_breadth": coverage_breadth,
    }


# ---------------------------------------------------------------------------
# 5. Motivational Interviewing Quality (OARS)
# ---------------------------------------------------------------------------

def oars_score_session(session):
    """Analyze coach messages for OARS technique usage in a session.

    Returns:
      - technique_counts: {open_questions, affirmations, reflections, summaries}
      - technique_per_message: average OARS techniques per coach message
      - total_oars: total technique instances detected
      - oars_ratio: OARS techniques / total coach messages
      - closed_question_count: coach questions that are not open-ended
      - open_to_closed_ratio: open / (open + closed), higher is better
      - detail: per-technique match examples for auditability
    """
    coach_msgs = _coach_messages(session)
    if not coach_msgs:
        return {
            "technique_counts": {k: 0 for k in _OARS_PATTERNS},
            "technique_per_message": 0,
            "total_oars": 0,
            "oars_ratio": 0,
            "closed_question_count": 0,
            "open_to_closed_ratio": 0,
            "detail": {},
        }

    technique_counts = {}
    detail = {}

    for technique, patterns in _OARS_PATTERNS.items():
        count = 0
        examples = []
        for msg in coach_msgs:
            for pattern, weight in patterns:
                hits = pattern.findall(msg)
                if hits:
                    count += weight * len(hits)
                    # Store first few examples
                    if len(examples) < 3:
                        snippet = msg[:120] + ("..." if len(msg) > 120 else "")
                        if snippet not in examples:
                            examples.append(snippet)
        technique_counts[technique] = count
        detail[technique] = examples

    total_oars = sum(technique_counts.values())

    # Detect closed questions (any question mark not matched by open patterns)
    total_questions = sum(1 for m in coach_msgs if "?" in m)
    open_q_messages = 0
    for msg in coach_msgs:
        if "?" in msg:
            for pattern, _ in _OARS_PATTERNS["open_questions"]:
                if pattern.search(msg):
                    open_q_messages += 1
                    break
    closed_questions = max(0, total_questions - open_q_messages)

    return {
        "technique_counts": technique_counts,
        "technique_per_message": round(_safe_ratio(total_oars, len(coach_msgs)), 2),
        "total_oars": total_oars,
        "oars_ratio": round(_safe_ratio(total_oars, len(coach_msgs)), 2),
        "closed_question_count": closed_questions,
        "open_to_closed_ratio": round(
            _safe_ratio(open_q_messages, open_q_messages + closed_questions), 2
        ),
        "detail": detail,
    }


def oars_score_longitudinal(profile):
    """Track OARS quality across all sessions for a patient.

    Returns per-session scores and aggregate trend.
    """
    per_session = []
    for session in _all_sessions_for_patient(profile):
        oars = oars_score_session(session)
        per_session.append({
            "session_id": session["session_id"],
            "date": (session.get("start_time") or "")[:10],
            "technique_counts": oars["technique_counts"],
            "oars_ratio": oars["oars_ratio"],
            "open_to_closed_ratio": oars["open_to_closed_ratio"],
        })

    # Trend: compare first half to second half of sessions
    if len(per_session) >= 4:
        mid = len(per_session) // 2
        first_half_ratio = _mean([s["oars_ratio"] for s in per_session[:mid]])
        second_half_ratio = _mean([s["oars_ratio"] for s in per_session[mid:]])
        if second_half_ratio > first_half_ratio + 0.1:
            trend = "improving"
        elif second_half_ratio < first_half_ratio - 0.1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient"

    return {"per_session": per_session, "trend": trend}


# ---------------------------------------------------------------------------
# 6. Composite Display
# ---------------------------------------------------------------------------

def display_conversation_analytics(profile):
    """Print a comprehensive conversation analytics summary for a patient.

    Covers all five analytics domains across all sessions.
    """
    sessions = _all_sessions_for_patient(profile)
    pid = profile.get("patient_id", "unknown")

    print(f"\n  {'='*64}")
    print(f"  CONVERSATION ANALYTICS — Patient {pid}")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Sessions analyzed: {len(sessions)}")
    print(f"  {'='*64}")

    if not sessions:
        print("\n  No sessions found. Complete at least one coaching session first.\n")
        return

    # --- Engagement ---
    eng = engagement_metrics_longitudinal(profile)
    agg = eng.get("aggregate", {})
    print(f"\n  ENGAGEMENT METRICS")
    print(f"  {'─'*56}")
    if agg:
        print(f"  Total sessions: {agg.get('total_sessions', 0)}")
        print(f"  Total messages: {agg.get('total_messages', 0)}")
        mc = agg.get("message_count", {})
        print(f"  Messages/session: {mc.get('mean', 0):.1f} (SD={mc.get('sd', 0):.1f}, "
              f"range {mc.get('min', 0)}-{mc.get('max', 0)})")
        pal = agg.get("patient_avg_length", {})
        print(f"  Patient msg length: {pal.get('mean', 0):.0f} chars "
              f"(SD={pal.get('sd', 0):.0f})")
        pawc = agg.get("patient_avg_word_count", {})
        print(f"  Patient msg words: {pawc.get('mean', 0):.1f} words "
              f"(SD={pawc.get('sd', 0):.1f})")
        qr = agg.get("question_ratio", {})
        print(f"  Question ratio: {qr.get('mean', 0):.0%} of patient messages are questions")
        dur = agg.get("session_duration_min", {})
        if dur.get("mean", 0) > 0:
            print(f"  Session duration: {dur.get('mean', 0):.1f} min "
                  f"(SD={dur.get('sd', 0):.1f})")

    # --- Readiness to Change ---
    rtc = score_readiness_longitudinal(profile)
    print(f"\n  READINESS TO CHANGE (Transtheoretical Model)")
    print(f"  {'─'*56}")
    if rtc:
        stage_order = ["precontemplation", "contemplation", "preparation",
                       "action", "maintenance"]
        # Show progression
        for r in rtc:
            stage = r["dominant_stage"]
            conf = r["confidence"]
            scores_str = "  ".join(
                f"{s[:5]}={r['stage_scores'].get(s, 0)}"
                for s in stage_order if r["stage_scores"].get(s, 0) > 0
            )
            print(f"  {r['date']}  {stage:<20} (conf={conf:.0%})  [{scores_str}]")

        # Summarize trajectory
        stages = [r["dominant_stage"] for r in rtc if r["dominant_stage"] != "indeterminate"]
        if len(stages) >= 2:
            first_idx = stage_order.index(stages[0]) if stages[0] in stage_order else -1
            last_idx = stage_order.index(stages[-1]) if stages[-1] in stage_order else -1
            if first_idx >= 0 and last_idx >= 0:
                if last_idx > first_idx:
                    print(f"\n  Trajectory: PROGRESSING ({stages[0]} -> {stages[-1]})")
                elif last_idx < first_idx:
                    print(f"\n  Trajectory: REGRESSING ({stages[0]} -> {stages[-1]})")
                else:
                    print(f"\n  Trajectory: STABLE ({stages[-1]})")
    else:
        print("  No data.")

    # --- Sentiment ---
    sent = sentiment_longitudinal(profile)
    print(f"\n  SENTIMENT TRACKING")
    print(f"  {'─'*56}")
    if sent:
        for s in sent:
            valence = s["session_valence"]
            bar = _valence_bar(valence)
            dist = s["distribution"]
            dist_str = (f"+{dist['positive']} -{dist['negative']} "
                        f"={dist['neutral']} ~{dist['mixed']}")
            print(f"  {s['date']}  {bar}  val={valence:+.2f}  ({dist_str})  {s['trend']}")

        # Overall trend
        valences = [s["session_valence"] for s in sent]
        if len(valences) >= 2:
            first_val = valences[0]
            last_val = valences[-1]
            overall_change = last_val - first_val
            if overall_change > 0.15:
                print(f"\n  Overall sentiment: IMPROVING ({first_val:+.2f} -> {last_val:+.2f})")
            elif overall_change < -0.15:
                print(f"\n  Overall sentiment: DECLINING ({first_val:+.2f} -> {last_val:+.2f})")
            else:
                print(f"\n  Overall sentiment: STABLE (mean={_mean(valences):+.2f})")
    else:
        print("  No data.")

    # --- Topic Coverage ---
    topics = topic_coverage_longitudinal(profile)
    print(f"\n  TOPIC COVERAGE (Six Pillars)")
    print(f"  {'─'*56}")
    agg_counts = topics.get("aggregate_counts", {})
    agg_props = topics.get("aggregate_proportions", {})
    breadth = topics.get("coverage_breadth", 0)

    # Sort pillars by count descending
    sorted_pillars = sorted(PILLARS, key=lambda p: agg_counts.get(p, 0), reverse=True)
    for pillar in sorted_pillars:
        count = agg_counts.get(pillar, 0)
        prop = agg_props.get(pillar, 0)
        bar = _topic_bar(prop)
        print(f"  {pillar.capitalize():<14} {bar}  {count:>4} mentions  ({prop:.0%})")

    print(f"\n  Coverage breadth: {breadth}/6 pillars discussed")
    neglected = [p.capitalize() for p in PILLARS if agg_counts.get(p, 0) == 0]
    if neglected:
        print(f"  Neglected pillars: {', '.join(neglected)}")

    # Per-session primary topics
    if topics.get("per_session"):
        primary_seq = [s["primary_topic"] for s in topics["per_session"]]
        print(f"  Session focus sequence: {' -> '.join(primary_seq)}")

    # --- OARS Quality ---
    oars = oars_score_longitudinal(profile)
    print(f"\n  MOTIVATIONAL INTERVIEWING QUALITY (OARS)")
    print(f"  {'─'*56}")
    if oars.get("per_session"):
        for s in oars["per_session"]:
            tc = s["technique_counts"]
            o2c = s["open_to_closed_ratio"]
            oars_r = s["oars_ratio"]
            print(f"  {s['date']}  O={tc.get('open_questions', 0):<3} "
                  f"A={tc.get('affirmations', 0):<3} "
                  f"R={tc.get('reflections', 0):<3} "
                  f"S={tc.get('summaries', 0):<3} "
                  f" OARS/msg={oars_r:.1f}  open:closed={o2c:.0%}")

        # Overall quality assessment
        avg_oars = _mean([s["oars_ratio"] for s in oars["per_session"]])
        avg_o2c = _mean([s["open_to_closed_ratio"] for s in oars["per_session"]])

        print(f"\n  Avg OARS/message: {avg_oars:.2f}")
        print(f"  Avg open-question ratio: {avg_o2c:.0%}")

        if avg_oars >= 1.5:
            quality = "STRONG"
        elif avg_oars >= 0.8:
            quality = "ADEQUATE"
        elif avg_oars >= 0.3:
            quality = "DEVELOPING"
        else:
            quality = "MINIMAL"
        print(f"  MI quality rating: {quality}")

        if oars["trend"] != "insufficient":
            print(f"  Trend: {oars['trend'].upper()}")

        # Identify weakest OARS component
        total_by_technique = {}
        for s in oars["per_session"]:
            for tech, count in s["technique_counts"].items():
                total_by_technique[tech] = total_by_technique.get(tech, 0) + count
        if total_by_technique:
            weakest = min(total_by_technique, key=total_by_technique.get)
            label_map = {
                "open_questions": "Open Questions",
                "affirmations": "Affirmations",
                "reflections": "Reflections",
                "summaries": "Summaries",
            }
            print(f"  Area for growth: {label_map.get(weakest, weakest)}")
    else:
        print("  No data.")

    print(f"\n  {'='*64}\n")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _valence_bar(valence, width=11):
    """Render a [-1, +1] valence as a centered bar.

    Example: [------|####-]  for valence ~+0.4
    """
    mid = width // 2
    if valence >= 0:
        filled = round(valence * mid)
        bar = "-" * mid + "#" * filled + "-" * (mid - filled)
    else:
        filled = round(abs(valence) * mid)
        bar = "-" * (mid - filled) + "#" * filled + "-" * mid
    return f"[{bar}]"


def _topic_bar(proportion, width=20):
    """Render a [0, 1] proportion as a horizontal bar."""
    filled = round(proportion * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


# ---------------------------------------------------------------------------
# Convenience: get all analytics as a single dict (for export/API use)
# ---------------------------------------------------------------------------

def get_all_analytics(profile):
    """Return all analytics for a patient as a serializable dict.

    Intended for JSON export or integration with other research tools.
    """
    return {
        "patient_id": profile.get("patient_id"),
        "generated_at": datetime.now().isoformat(),
        "engagement": engagement_metrics_longitudinal(profile),
        "readiness_to_change": score_readiness_longitudinal(profile),
        "sentiment": sentiment_longitudinal(profile),
        "topic_coverage": topic_coverage_longitudinal(profile),
        "oars_quality": oars_score_longitudinal(profile),
    }
