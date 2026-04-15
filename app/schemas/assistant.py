"""
app/schemas/assistant.py

Pydantic schemas for the POST /assistant API endpoint.

Using Pydantic v2 models to validate incoming requests and
serialise outgoing responses automatically via FastAPI.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    """
    Payload accepted by POST /assistant.

    Attributes:
        message:  The raw natural-language input from the user.
        timezone: Optional IANA timezone string used when parsing
                  relative date/time expressions (e.g. "tomorrow at 3 pm").
                  Defaults to UTC.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural-language task description from the user.",
        examples=["Schedule a team meeting tomorrow at 10am"],
    )
    timezone: str = Field(
        default="UTC",
        description="IANA timezone of the caller (e.g. 'America/New_York').",
    )


class AssistantResponse(BaseModel):
    """
    Structured response returned by POST /assistant.

    Attributes:
        intent:          The intent detected from the user message.
        title:           Short title of the resulting task.
        description:     Optional longer description.
        due_date:        Parsed due date/time (ISO 8601), if applicable.
        integration_ref: Reference ID from any external integration
                         (e.g. a Google Calendar event ID).
        details:         Additional key-value data for the consumer.
        message:         Human-readable summary of the action taken.
    """

    intent: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    integration_ref: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    message: str
