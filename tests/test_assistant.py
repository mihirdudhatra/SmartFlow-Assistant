"""
tests/test_assistant.py

Test suite for SmartFlow-Assistant.

Tests are organised into three groups:
  1. Unit tests for IntentService (pure logic, no I/O)
  2. Unit tests for TaskService (mocked calendar integration)
  3. Integration tests for the FastAPI HTTP layer (TestClient)
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.task import Intent
from app.services.intent_service import IntentService
from app.services.task_service import TaskService

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client() -> TestClient:
    """Return a synchronous TestClient wrapping the FastAPI app."""
    return TestClient(app)


@pytest.fixture()
def intent_service() -> IntentService:
    return IntentService()


@pytest.fixture()
def task_service() -> TaskService:
    return TaskService()


# ---------------------------------------------------------------------------
# 1. IntentService unit tests
# ---------------------------------------------------------------------------

class TestIntentService:
    def test_detect_create_event(self, intent_service: IntentService) -> None:
        assert intent_service.detect("Schedule a team meeting tomorrow") == Intent.CREATE_EVENT

    def test_detect_create_event_book(self, intent_service: IntentService) -> None:
        assert intent_service.detect("Book an appointment with the dentist") == Intent.CREATE_EVENT

    def test_detect_set_reminder(self, intent_service: IntentService) -> None:
        assert intent_service.detect("Remind me to take my medication at 8pm") == Intent.SET_REMINDER

    def test_detect_list_tasks(self, intent_service: IntentService) -> None:
        assert intent_service.detect("Show my upcoming tasks for this week") == Intent.LIST_TASKS

    def test_detect_delete_task(self, intent_service: IntentService) -> None:
        assert intent_service.detect("Delete the standup meeting") == Intent.DELETE_TASK

    def test_detect_unknown(self, intent_service: IntentService) -> None:
        assert intent_service.detect("Hello, how are you?") == Intent.UNKNOWN

    def test_case_insensitive(self, intent_service: IntentService) -> None:
        assert intent_service.detect("SCHEDULE A CALL") == Intent.CREATE_EVENT

    def test_supported_intents_returns_dict(self, intent_service: IntentService) -> None:
        intents = IntentService.supported_intents()
        assert isinstance(intents, dict)
        assert Intent.CREATE_EVENT.value in intents


# ---------------------------------------------------------------------------
# 2. TaskService unit tests
# ---------------------------------------------------------------------------

class TestTaskService:
    def test_process_create_event_returns_response(self, task_service: TaskService) -> None:
        response = task_service.process("Schedule a meeting with Alice tomorrow")
        assert response.intent == Intent.CREATE_EVENT.value
        assert response.integration_ref is not None  # calendar event was "created"
        assert "Calendar event" in response.message

    def test_process_set_reminder(self, task_service: TaskService) -> None:
        response = task_service.process("Remind me to call Bob at noon")
        assert response.intent == Intent.SET_REMINDER.value
        assert "Reminder" in response.message

    def test_process_list_tasks(self, task_service: TaskService) -> None:
        response = task_service.process("Show my upcoming tasks")
        assert response.intent == Intent.LIST_TASKS.value
        assert "count" in response.details

    def test_process_delete_task(self, task_service: TaskService) -> None:
        response = task_service.process("Delete the board meeting event")
        assert response.intent == Intent.DELETE_TASK.value

    def test_process_unknown(self, task_service: TaskService) -> None:
        response = task_service.process("What is the weather like?")
        assert response.intent == Intent.UNKNOWN.value

    def test_title_truncated_to_60_chars(self, task_service: TaskService) -> None:
        long_message = "Schedule " + "a" * 100
        response = task_service.process(long_message)
        assert len(response.title) <= 60


# ---------------------------------------------------------------------------
# 3. HTTP layer integration tests
# ---------------------------------------------------------------------------

class TestAssistantEndpoint:
    def test_post_assistant_create_event(self, client: TestClient) -> None:
        payload = {"message": "Schedule a project kickoff meeting tomorrow at 9am"}
        resp = client.post("/assistant", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == Intent.CREATE_EVENT.value
        assert "message" in data
        assert "title" in data

    def test_post_assistant_set_reminder(self, client: TestClient) -> None:
        payload = {"message": "Remind me to send the weekly report every Friday"}
        resp = client.post("/assistant", json=payload)
        assert resp.status_code == 200
        assert resp.json()["intent"] == Intent.SET_REMINDER.value

    def test_post_assistant_list_tasks(self, client: TestClient) -> None:
        payload = {"message": "Show all my upcoming tasks"}
        resp = client.post("/assistant", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == Intent.LIST_TASKS.value
        assert "count" in data["details"]

    def test_post_assistant_unknown_intent(self, client: TestClient) -> None:
        payload = {"message": "Tell me a joke"}
        resp = client.post("/assistant", json=payload)
        assert resp.status_code == 200
        assert resp.json()["intent"] == Intent.UNKNOWN.value

    def test_post_assistant_empty_message_rejected(self, client: TestClient) -> None:
        resp = client.post("/assistant", json={"message": ""})
        assert resp.status_code == 422  # Pydantic validation error

    def test_post_assistant_with_timezone(self, client: TestClient) -> None:
        payload = {"message": "Book a dentist appointment", "timezone": "America/New_York"}
        resp = client.post("/assistant", json=payload)
        assert resp.status_code == 200

    def test_get_intents(self, client: TestClient) -> None:
        resp = client.get("/assistant/intents")
        assert resp.status_code == 200
        data = resp.json()
        assert "supported_intents" in data
        assert Intent.CREATE_EVENT.value in data["supported_intents"]

    def test_health_check(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
