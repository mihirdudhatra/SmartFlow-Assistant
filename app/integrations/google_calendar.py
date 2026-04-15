"""
app/integrations/google_calendar.py

Mock Google Calendar integration.

This module simulates the Google Calendar API so the rest of the
application can be developed and tested without real credentials.
In production, replace `MockGoogleCalendarClient` with a real
implementation backed by the `google-api-python-client` library –
the `GoogleCalendarIntegration` facade class does not need to change.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.utils.logger import logger


class MockGoogleCalendarClient:
    """
    In-memory stand-in for the real Google Calendar API client.

    All operations are logged and return plausible fake data so that
    the service layer can be exercised end-to-end without credentials.
    """

    def create_event(
        self,
        summary: str,
        description: Optional[str],
        start: datetime,
        end: datetime,
    ) -> Dict[str, Any]:
        event_id = str(uuid.uuid4())
        logger.info(
            "[MockCalendar] Creating event id=%s summary=%r start=%s",
            event_id,
            summary,
            start.isoformat(),
        )
        return {
            "id": event_id,
            "summary": summary,
            "description": description or "",
            "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
            "status": "confirmed",
            "htmlLink": f"https://calendar.google.com/event?eid={event_id}",
        }

    def list_events(self, max_results: int = 10) -> Dict[str, Any]:
        logger.info("[MockCalendar] Listing events (max_results=%d)", max_results)
        return {"items": [], "summary": "mock-calendar@example.com"}

    def delete_event(self, event_id: str) -> bool:
        logger.info("[MockCalendar] Deleting event id=%s", event_id)
        return True


class GoogleCalendarIntegration:
    """
    Facade that wraps a Google Calendar client and exposes high-level
    operations used by the service layer.

    Dependency-injecting the client keeps this class testable without
    any real HTTP calls.
    """

    def __init__(self, client: Optional[MockGoogleCalendarClient] = None) -> None:
        # Default to the mock client; swap in a real client for production.
        self._client: MockGoogleCalendarClient = client or MockGoogleCalendarClient()

    def create_calendar_event(
        self,
        title: str,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Create a calendar event and return the raw API response dict.

        Args:
            title:       Short event title.
            description: Optional longer description.
            start_time:  Event start (defaults to *now* when not provided).

        Returns:
            Dictionary containing at minimum an ``"id"`` key with the
            new event's identifier.
        """
        from datetime import timedelta

        start = start_time or datetime.now(timezone.utc)
        end = start + timedelta(hours=1)  # default 1-hour duration

        return self._client.create_event(
            summary=title,
            description=description,
            start=start,
            end=end,
        )

    def list_upcoming_events(self, max_results: int = 10) -> Dict[str, Any]:
        """Return a list of upcoming calendar events."""
        return self._client.list_events(max_results=max_results)

    def delete_calendar_event(self, event_id: str) -> bool:
        """Delete a calendar event by ID. Returns True on success."""
        return self._client.delete_event(event_id)
