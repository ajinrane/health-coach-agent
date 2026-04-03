"""Core tests for the health coach agent modules.

Covers: patient CRUD, assessments, goal lifecycle, safety screening,
profile summaries, sessions, and trend data.
"""

import json

import pytest

from coach import memory as mem
from coach import session as sess
from coach.safety import screen_message, RED_FLAGS
from coach.assessments import ASSESSMENTS, get_assessment_list
from coach.trends import get_trend_data


# ---------------------------------------------------------------------------
# 1. Patient CRUD
# ---------------------------------------------------------------------------

class TestPatientCRUD:
    """Create, save, load, and list patients."""

    def test_create_patient_returns_valid_profile(self, data_dir):
        profile = mem.create_patient()
        assert "patient_id" in profile
        assert len(profile["patient_id"]) == 8
        assert profile["assessments"] == []
        assert profile["goals"] == []
        assert profile["sessions"] == []
        assert profile["conversation_count"] == 0

    def test_create_patient_with_demographics(self, data_dir):
        demo = {"age": 40, "sex": "M", "conditions": ["diabetes"], "medications": [], "notes": ""}
        profile = mem.create_patient(demographics=demo)
        assert profile["demographics"]["age"] == 40
        assert profile["demographics"]["sex"] == "M"
        assert "diabetes" in profile["demographics"]["conditions"]

    def test_save_and_load_round_trip(self, data_dir):
        profile = mem.create_patient()
        pid = profile["patient_id"]

        # Mutate and save
        profile["demographics"]["age"] = 55
        mem.save_patient(profile)

        loaded = mem.load_patient(pid)
        assert loaded is not None
        assert loaded["demographics"]["age"] == 55

    def test_load_nonexistent_patient_returns_none(self, data_dir):
        assert mem.load_patient("ZZZZZZZZ") is None

    def test_list_patients_empty(self, data_dir):
        assert mem.list_patients() == []

    def test_list_patients_returns_all(self, data_dir):
        mem.create_patient()
        mem.create_patient()
        mem.create_patient()
        patients = mem.list_patients()
        assert len(patients) == 3
        # Each entry should have expected summary keys
        for p in patients:
            assert "patient_id" in p
            assert "created_at" in p
            assert "session_count" in p
            assert "goal_count" in p

    def test_saved_file_is_valid_json(self, data_dir):
        profile = mem.create_patient()
        path = data_dir / f"{profile['patient_id']}.json"
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert data["patient_id"] == profile["patient_id"]


# ---------------------------------------------------------------------------
# 2. Assessment recording
# ---------------------------------------------------------------------------

class TestAssessments:
    """Record assessments and verify they appear in the profile."""

    def test_add_assessment_basic(self, sample_profile):
        assessment = mem.add_assessment(
            sample_profile,
            assessment_type="PHQ-2 (Depression Screen)",
            score=2,
            max_score=6,
            interpretation="Negative screen. No further depression screening indicated.",
        )
        assert assessment["type"] == "PHQ-2 (Depression Screen)"
        assert assessment["score"] == 2
        assert assessment["max_score"] == 6
        assert "id" in assessment
        assert "date" in assessment

    def test_assessment_persisted_in_profile(self, sample_profile, data_dir):
        mem.add_assessment(
            sample_profile,
            assessment_type="GAD-2 (Anxiety Screen)",
            score=4,
            max_score=6,
            interpretation="Positive screen.",
        )
        loaded = mem.load_patient(sample_profile["patient_id"])
        assert len(loaded["assessments"]) == 1
        assert loaded["assessments"][0]["type"] == "GAD-2 (Anxiety Screen)"

    def test_add_assessment_with_details(self, sample_profile):
        details = {"q1": 1, "q2": 2}
        assessment = mem.add_assessment(
            sample_profile,
            assessment_type="PHQ-2 (Depression Screen)",
            score=3,
            max_score=6,
            interpretation="Positive screen.",
            details=details,
        )
        assert assessment["details"] == details

    def test_multiple_assessments_accumulate(self, sample_profile):
        for i in range(3):
            mem.add_assessment(
                sample_profile,
                assessment_type="PHQ-2 (Depression Screen)",
                score=i,
                max_score=6,
                interpretation=f"Result {i}",
            )
        assert len(sample_profile["assessments"]) == 3

    def test_get_assessment_list(self):
        items = get_assessment_list()
        assert len(items) == len(ASSESSMENTS)
        for key, name, description in items:
            assert key in ASSESSMENTS
            assert isinstance(name, str)
            assert isinstance(description, str)


# ---------------------------------------------------------------------------
# 3. Goal lifecycle
# ---------------------------------------------------------------------------

class TestGoalLifecycle:
    """Add goals, check in, and complete them."""

    def test_add_goal(self, sample_profile):
        goal = mem.add_goal(
            sample_profile,
            pillar="exercise",
            description="Walk 30 minutes daily",
            target="30 min/day, 5 days/week",
            timeframe="next 4 weeks",
        )
        assert goal["pillar"] == "exercise"
        assert goal["status"] == "active"
        assert goal["check_ins"] == []
        assert "id" in goal

    def test_goal_persisted(self, sample_profile, data_dir):
        mem.add_goal(sample_profile, "sleep", "Lights out by 10pm", "10pm bedtime")
        loaded = mem.load_patient(sample_profile["patient_id"])
        assert len(loaded["goals"]) == 1
        assert loaded["goals"][0]["pillar"] == "sleep"

    def test_check_in_goal_adherent(self, sample_profile):
        goal = mem.add_goal(sample_profile, "nutrition", "Eat 5 servings veg", "5/day")
        updated = mem.check_in_goal(sample_profile, goal["id"], adherence=True, notes="Had a salad")
        assert updated is not None
        assert len(updated["check_ins"]) == 1
        assert updated["check_ins"][0]["adherence"] is True
        assert updated["check_ins"][0]["notes"] == "Had a salad"

    def test_check_in_goal_not_adherent(self, sample_profile):
        goal = mem.add_goal(sample_profile, "exercise", "Run 5k", "3x/week")
        updated = mem.check_in_goal(sample_profile, goal["id"], adherence=False, notes="Rained")
        assert updated["check_ins"][0]["adherence"] is False

    def test_check_in_nonexistent_goal_returns_none(self, sample_profile):
        result = mem.check_in_goal(sample_profile, "FAKEID00", adherence=True)
        assert result is None

    def test_complete_goal(self, sample_profile):
        goal = mem.add_goal(sample_profile, "stress", "Meditate daily", "10 min/day")
        completed = mem.complete_goal(sample_profile, goal["id"])
        assert completed is not None
        assert completed["status"] == "completed"
        assert "completed_at" in completed

    def test_complete_nonexistent_goal_returns_none(self, sample_profile):
        result = mem.complete_goal(sample_profile, "FAKEID00")
        assert result is None

    def test_full_goal_lifecycle(self, sample_profile, data_dir):
        """Add -> check-in multiple times -> complete -> verify on disk."""
        goal = mem.add_goal(sample_profile, "sleep", "No screens after 9pm", "9pm cutoff")
        gid = goal["id"]

        mem.check_in_goal(sample_profile, gid, True, "Did it")
        mem.check_in_goal(sample_profile, gid, False, "Watched TV")
        mem.check_in_goal(sample_profile, gid, True, "Read a book instead")

        mem.complete_goal(sample_profile, gid)

        loaded = mem.load_patient(sample_profile["patient_id"])
        g = loaded["goals"][0]
        assert g["status"] == "completed"
        assert len(g["check_ins"]) == 3


# ---------------------------------------------------------------------------
# 4. Safety screening
# ---------------------------------------------------------------------------

class TestSafetyScreening:
    """Ensure red flags are detected and safe messages pass clean."""

    def test_safe_message_returns_empty(self):
        flags = screen_message("I went for a nice walk today and ate a salad.")
        assert flags == []

    def test_safe_greeting(self):
        flags = screen_message("Hello! How are you?")
        assert flags == []

    def test_detects_suicidal_ideation(self):
        flags = screen_message("I've been thinking about ending my life lately.")
        assert len(flags) >= 1
        categories = [f["category"] for f in flags]
        assert "suicidal_ideation" in categories

    def test_detects_self_harm(self):
        flags = screen_message("I've started to cut myself again.")
        assert any(f["category"] == "suicidal_ideation" for f in flags)

    def test_detects_disordered_eating(self):
        flags = screen_message("I've been purging after every meal.")
        assert any(f["category"] == "disordered_eating" for f in flags)

    def test_detects_medical_emergency(self):
        flags = screen_message("I'm having severe chest pain and can't breathe.")
        assert any(f["category"] == "medical_emergency" for f in flags)

    def test_detects_substance_crisis(self):
        flags = screen_message("I think I overdosed on pills last night.")
        assert any(f["category"] == "substance_crisis" for f in flags)

    def test_flag_has_required_keys(self):
        flags = screen_message("I want to kill myself.")
        assert len(flags) >= 1
        flag = flags[0]
        assert "category" in flag
        assert "severity" in flag
        assert "response" in flag

    def test_red_flags_dict_has_expected_categories(self):
        expected = {"suicidal_ideation", "disordered_eating", "substance_crisis", "medical_emergency"}
        assert expected == set(RED_FLAGS.keys())

    def test_each_category_has_severity_and_patterns(self):
        for category, config in RED_FLAGS.items():
            assert "patterns" in config, f"{category} missing patterns"
            assert "severity" in config, f"{category} missing severity"
            assert "response" in config, f"{category} missing response"
            assert len(config["patterns"]) > 0


# ---------------------------------------------------------------------------
# 5. Profile summary generation
# ---------------------------------------------------------------------------

class TestProfileSummary:
    """Verify the text summary produced for prompt context."""

    def test_new_patient_summary(self, data_dir):
        profile = mem.create_patient()
        summary = mem.get_profile_summary(profile)
        assert summary == "New patient — no data yet."

    def test_summary_includes_demographics(self, sample_profile):
        summary = mem.get_profile_summary(sample_profile)
        assert "35yo" in summary
        assert "F" in summary
        assert "hypertension" in summary
        assert "lisinopril" in summary

    def test_summary_includes_active_goals(self, sample_profile):
        mem.add_goal(sample_profile, "exercise", "Walk 30 min", "5x/week")
        summary = mem.get_profile_summary(sample_profile)
        assert "Active goals" in summary
        assert "Walk 30 min" in summary

    def test_summary_includes_assessments(self, sample_profile):
        mem.add_assessment(
            sample_profile,
            assessment_type="PHQ-2",
            score=1,
            max_score=6,
            interpretation="Negative screen.",
        )
        summary = mem.get_profile_summary(sample_profile)
        assert "Recent assessments" in summary
        assert "PHQ-2" in summary
        assert "1/6" in summary

    def test_summary_shows_goal_adherence(self, sample_profile):
        goal = mem.add_goal(sample_profile, "sleep", "Bed by 10", "10pm")
        mem.check_in_goal(sample_profile, goal["id"], True)
        mem.check_in_goal(sample_profile, goal["id"], False)
        summary = mem.get_profile_summary(sample_profile)
        assert "adherence" in summary.lower() or "%" in summary


# ---------------------------------------------------------------------------
# 6. Session creation and exchange recording
# ---------------------------------------------------------------------------

class TestSession:
    """Start sessions, record exchanges, verify structure."""

    def test_start_session_structure(self, session_dir):
        session = sess.start_session("abc12345")
        assert session["patient_id"] == "abc12345"
        assert "session_id" in session
        assert session["conversation"] == []
        assert session["soap_note"] is None

    def test_add_exchange(self, session_dir):
        session = sess.start_session("abc12345")
        sess.add_exchange(session, "I slept poorly last night.", "Let's talk about your sleep habits.")
        assert len(session["conversation"]) == 1
        ex = session["conversation"][0]
        assert ex["user"] == "I slept poorly last night."
        assert ex["assistant"] == "Let's talk about your sleep habits."
        assert "timestamp" in ex

    def test_multiple_exchanges(self, session_dir):
        session = sess.start_session("abc12345")
        sess.add_exchange(session, "Hi", "Hello! How can I help?")
        sess.add_exchange(session, "I need help with sleep", "Tell me more about your sleep patterns.")
        sess.add_exchange(session, "I wake up a lot", "That's common. Let's look at sleep hygiene.")
        assert len(session["conversation"]) == 3

    def test_session_id_format(self, session_dir):
        session = sess.start_session("abc12345")
        assert len(session["session_id"]) == 8

    def test_session_has_timestamps(self, session_dir):
        session = sess.start_session("abc12345")
        assert "start_time" in session
        assert session["end_time"] is None


# ---------------------------------------------------------------------------
# 7. Trend data extraction
# ---------------------------------------------------------------------------

class TestTrendData:
    """Extract raw trend data for analysis/export."""

    def test_empty_profile_returns_empty(self, sample_profile):
        data = get_trend_data(sample_profile)
        assert data == []

    def test_single_assessment_trend(self, sample_profile):
        mem.add_assessment(sample_profile, "PHQ-2", 2, 6, "Negative screen.")
        data = get_trend_data(sample_profile)
        assert len(data) == 1
        assert data[0]["type"] == "PHQ-2"
        assert data[0]["score"] == 2

    def test_multiple_assessment_trends_sorted(self, sample_profile):
        mem.add_assessment(sample_profile, "PHQ-2", 2, 6, "Negative.")
        mem.add_assessment(sample_profile, "PHQ-2", 4, 6, "Positive.")
        mem.add_assessment(sample_profile, "GAD-2", 1, 6, "Negative.")
        data = get_trend_data(sample_profile)
        assert len(data) == 3
        # Results are sorted by date
        dates = [d["date"] for d in data]
        assert dates == sorted(dates)

    def test_filter_by_type(self, sample_profile):
        mem.add_assessment(sample_profile, "PHQ-2", 2, 6, "Neg.")
        mem.add_assessment(sample_profile, "GAD-2", 3, 6, "Pos.")
        mem.add_assessment(sample_profile, "PHQ-2", 5, 6, "Pos.")

        phq_data = get_trend_data(sample_profile, assessment_type="PHQ-2")
        assert len(phq_data) == 2
        assert all(d["type"] == "PHQ-2" for d in phq_data)

        gad_data = get_trend_data(sample_profile, assessment_type="GAD-2")
        assert len(gad_data) == 1

    def test_trend_data_keys(self, sample_profile):
        mem.add_assessment(sample_profile, "PHQ-2", 2, 6, "Negative screen.")
        data = get_trend_data(sample_profile)
        entry = data[0]
        expected_keys = {"date", "type", "score", "max_score", "interpretation"}
        assert set(entry.keys()) == expected_keys

    def test_filter_nonexistent_type_returns_empty(self, sample_profile):
        mem.add_assessment(sample_profile, "PHQ-2", 2, 6, "Neg.")
        data = get_trend_data(sample_profile, assessment_type="NONEXISTENT")
        assert data == []
