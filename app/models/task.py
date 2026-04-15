"""
app/models/task.py

Domain models for SmartFlow-Assistant.

These plain Python dataclasses represent the core business objects.
They are intentionally kept free from any framework or persistence
dependencies so that they can be reused across layers (services,
integrations, API).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class Intent(str, Enum):
    """Recognised user intents that the assistant can act on."""

    CREATE_EVENT = "create_event"
    SET_REMINDER = "set_reminder"
    LIST_TASKS = "list_tasks"
    DELETE_TASK = "delete_task"
    UNKNOWN = "unknown"


@dataclass
class Task:
    """
    Represents a user task produced by the assistant after intent detection.

    Attributes:
        intent:      The detected intent for this task.
        title:       Short human-readable description of the task.
        description: Optional longer description extracted from user input.
        due_date:    Optional deadline / event time for calendar integration.
        created_at:  Timestamp when the task was created (defaults to now).
        metadata:    Arbitrary key-value pairs for additional context
                     (e.g., calendar event ID returned by the integration).
    """

    intent: Intent
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)
