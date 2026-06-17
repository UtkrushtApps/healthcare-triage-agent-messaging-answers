import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("REDIS_HOST", "127.0.0.1")

from app.main import app, store

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_store():
    store.reset()
    yield
    store.reset()


def valid_message():
    return {
        "sender": "IntakeAgent",
        "receiver": "NurseAgent",
        "conversation_id": "conv-001",
        "performative": "request",
        "payload": {"symptom": "fever"},
    }


def test_valid_message_is_stored_once():
    resp = client.post("/agent/message", json=valid_message())
    assert resp.status_code == 200
    assert resp.json() == {"status": "stored"}
    assert store.note_count() == 1


def test_duplicate_message_is_ignored():
    client.post("/agent/message", json=valid_message())
    resp = client.post("/agent/message", json=valid_message())
    assert resp.status_code == 200
    assert resp.json() == {"status": "duplicate_ignored"}
    assert store.note_count() == 1


def test_missing_field_is_rejected():
    bad = valid_message()
    del bad["performative"]
    resp = client.post("/agent/message", json=bad)
    assert resp.status_code == 400
    assert resp.json() == {"error": "invalid agent message: performative"}
    assert store.note_count() == 0

