"""Shared fixtures for health coach agent tests."""

import pytest

from coach import memory as mem
from coach import session as sess


@pytest.fixture()
def data_dir(tmp_path, monkeypatch):
    """Redirect patient data storage to a temp directory."""
    patients_dir = tmp_path / "patients"
    patients_dir.mkdir()
    monkeypatch.setattr(mem, "DATA_DIR", patients_dir)
    return patients_dir


@pytest.fixture()
def session_dir(tmp_path, monkeypatch):
    """Redirect session storage to a temp directory."""
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    monkeypatch.setattr(sess, "SESSION_DIR", sessions_dir)
    return sessions_dir


@pytest.fixture()
def sample_profile(data_dir):
    """Create and return a sample patient profile persisted to the temp dir."""
    profile = mem.create_patient(demographics={
        "age": 35,
        "sex": "F",
        "conditions": ["hypertension"],
        "medications": ["lisinopril"],
        "notes": "Referred by PCP",
    })
    return profile
