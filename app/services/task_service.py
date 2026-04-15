"""
app/services/task_service.py

TaskService – the core business-logic layer of SmartFlow-Assistant.

Responsibilities
----------------
1. Accept a user message and an optional timezone hint.
2. Delegate intent detection to IntentService.
3. Build a Task domain object.
4. Route the task to the appropriate handler (calendar event creation,
   reminder confirmation, etc.).
5. Return a structured AssistantResponse to the API layer.

The service layer is deliberately free of FastAPI specifics so it
can be unit-tested without an HTTP server.
"""

from datetime import datetime
from typing import Optional

from app.integrations.google_calendar import GoogleCalendarIntegration
from app.models.task import Intent, Task
from app.schemas.assistant import AssistantResponse
from app.services.intent_service import IntentService
from app.utils.logger import logger


class TaskService:
    """
    Orchestrates intent detection, task creation, and integration calls.

    Attributes:
        _intent_service:   Detects user intent from raw text.
        _calendar:         Google Calendar integration (mock by default).
    """

    def __init__(
        self,
        intent_service: Optional[IntentService] = None,
        calendar_integration: Optional[GoogleCalendarIntegration] = None,
    ) -> None:
        self._intent_service: IntentService = intent_service or IntentService()
        self._calendar: GoogleCalendarIntegration = (
            calendar_integration or GoogleCalendarIntegration()
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, message: str, timezone: str = "UTC") -> AssistantResponse:
        """
        Process a natural-language message and return a structured response.

        Args:
            message:  Raw user input.
            timezone: IANA timezone string (informational; used in future
                      date-parsing enhancements).

        Returns:
            :class:`~app.schemas.assistant.AssistantResponse` ready for
            serialisation by the API layer.
        """
        logger.info("Processing message (tz=%s): %r", timezone, message[:80])

        intent = self._intent_service.detect(message)
        task = Task(
            intent=intent,
            title=self._extract_title(message),
            description=message,
        )

        return self._dispatch(task)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_title(self, message: str) -> str:
        """
        Derive a concise task title from the raw user message.

        Strategy: use the first sentence or the first 60 characters,
        whichever is shorter.
        """
        first_sentence = message.split(".")[0].strip()
        return first_sentence[:60] if first_sentence else message[:60]

    def _dispatch(self, task: Task) -> AssistantResponse:
        """Route a Task to the correct handler based on its intent."""
        handlers = {
            Intent.CREATE_EVENT: self._handle_create_event,
            Intent.SET_REMINDER: self._handle_set_reminder,
            Intent.LIST_TASKS: self._handle_list_tasks,
            Intent.DELETE_TASK: self._handle_delete_task,
            Intent.UNKNOWN: self._handle_unknown,
        }
        handler = handlers.get(task.intent, self._handle_unknown)
        return handler(task)

    # ------------------------------------------------------------------
    # Intent handlers
    # ------------------------------------------------------------------

    def _handle_create_event(self, task: Task) -> AssistantResponse:
        """Create a Google Calendar event and confirm."""
        event = self._calendar.create_calendar_event(
            title=task.title,
            description=task.description,
            start_time=task.due_date,
        )
        return AssistantResponse(
            intent=task.intent.value,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            integration_ref=event.get("id"),
            details={"calendar_link": event.get("htmlLink", "")},
            message=f"✅ Calendar event '{task.title}' has been created.",
        )

    def _handle_set_reminder(self, task: Task) -> AssistantResponse:
        """Acknowledge a reminder request (no external integration yet)."""
        return AssistantResponse(
            intent=task.intent.value,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            message=f"🔔 Reminder set: '{task.title}'.",
        )

    def _handle_list_tasks(self, task: Task) -> AssistantResponse:
        """Fetch upcoming calendar events and return them."""
        result = self._calendar.list_upcoming_events()
        items: list = result.get("items", [])
        return AssistantResponse(
            intent=task.intent.value,
            title="Upcoming tasks",
            description=None,
            details={"events": items, "count": len(items)},
            message=f"📋 You have {len(items)} upcoming event(s).",
        )

    def _handle_delete_task(self, task: Task) -> AssistantResponse:
        """Acknowledge a deletion request (requires an event ID in real use)."""
        return AssistantResponse(
            intent=task.intent.value,
            title=task.title,
            description=task.description,
            message="🗑️ Task deletion request noted. Please provide the event ID to confirm.",
        )

    def _handle_unknown(self, task: Task) -> AssistantResponse:
        """Return a helpful fallback when the intent cannot be determined."""
        return AssistantResponse(
            intent=task.intent.value,
            title=task.title,
            description=task.description,
            message=(
                "🤔 I couldn't determine what you'd like to do. "
                "Try phrases like 'schedule a meeting', 'remind me to…', "
                "or 'show my upcoming tasks'."
            ),
        )
