"""
app/services/intent_service.py

Rule-based intent detection service.

Design notes
------------
A simple keyword-scanning approach is used here so the project
stays lightweight and has zero external ML dependencies.
Each rule is expressed as a set of trigger keywords associated
with an Intent value.  The first matching rule wins (rules are
evaluated in priority order).

This layer can be replaced by an LLM-based classifier later
without changing any other part of the codebase, because callers
depend only on the `IntentService` interface.
"""

from typing import Dict, List, Tuple

from app.models.task import Intent
from app.utils.logger import logger

# ---------------------------------------------------------------------------
# Rule table
# ---------------------------------------------------------------------------
# Each entry is (Intent, [keywords]).
# Keywords are matched case-insensitively against the full user message.
# Priority: first match wins, so more-specific rules should appear earlier.
_RULES: List[Tuple[Intent, List[str]]] = [
    # DELETE must come before CREATE_EVENT so messages like
    # "Delete the meeting" are not hijacked by the "meeting" keyword.
    (Intent.DELETE_TASK, ["delete", "remove", "cancel", "drop", "clear"]),
    (Intent.CREATE_EVENT, ["schedule", "book", "create event", "add event", "meeting", "appointment"]),
    (Intent.SET_REMINDER, ["remind", "reminder", "alert", "notify", "don't forget", "remember"]),
    (Intent.LIST_TASKS, ["list", "show", "what are my", "display", "tasks", "upcoming"]),
]


class IntentService:
    """
    Detects the intent of a user message using a rule-based approach.

    Complexity: O(R × K) where R is the number of rules and K is the
    average number of keywords per rule – effectively constant for a
    fixed rule table.
    """

    def detect(self, message: str) -> Intent:
        """
        Return the Intent that best matches *message*.

        Falls back to ``Intent.UNKNOWN`` when no rule matches.

        Args:
            message: Raw natural-language input from the user.

        Returns:
            The detected :class:`~app.models.task.Intent`.
        """
        lowered = message.lower()

        for intent, keywords in _RULES:
            if any(kw in lowered for kw in keywords):
                logger.info("Intent detected: %s (message=%r)", intent.value, message[:60])
                return intent

        logger.info("No intent matched for message=%r; defaulting to UNKNOWN", message[:60])
        return Intent.UNKNOWN

    @staticmethod
    def supported_intents() -> Dict[str, List[str]]:
        """Return a human-readable map of supported intents → trigger keywords."""
        return {intent.value: keywords for intent, keywords in _RULES}
