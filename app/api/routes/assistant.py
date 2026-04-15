"""
app/api/routes/assistant.py

API routes for the SmartFlow-Assistant.

Endpoints
---------
POST /assistant
    Accept natural-language user input, process it through TaskService,
    and return a structured AssistantResponse.

GET /assistant/intents
    Return the list of supported intents and their trigger keywords.
    Useful for developer tooling and documentation.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.assistant import AssistantRequest, AssistantResponse
from app.services.intent_service import IntentService
from app.services.task_service import TaskService
from app.utils.logger import logger

router = APIRouter(prefix="/assistant", tags=["assistant"])

# Module-level service instances (singleton pattern for a lightweight app).
# In a larger project these would be injected via FastAPI's Depends mechanism.
_task_service = TaskService()
_intent_service = IntentService()


@router.post(
    "",
    response_model=AssistantResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a natural-language task request",
    description=(
        "Send a plain-English message to the assistant. "
        "The assistant detects your intent (e.g. create event, set reminder) "
        "and responds with a structured result, optionally integrating with "
        "Google Calendar."
    ),
)
def process_message(request: AssistantRequest) -> AssistantResponse:
    """
    Main entry point for the SmartFlow AI assistant.

    - Validates the incoming payload (via Pydantic).
    - Delegates processing to TaskService.
    - Returns a structured AssistantResponse.

    Raises:
        HTTPException 422: When the request body fails Pydantic validation
                           (handled automatically by FastAPI).
        HTTPException 500: For unexpected errors during processing.
    """
    logger.info("POST /assistant – message=%r", request.message[:60])
    try:
        response = _task_service.process(
            message=request.message,
            timezone=request.timezone,
        )
        return response
    except Exception as exc:
        logger.exception("Unexpected error while processing assistant request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request.",
        ) from exc


@router.get(
    "/intents",
    summary="List supported intents",
    description="Returns all intent names and their corresponding trigger keywords.",
)
def list_intents() -> dict:
    """Return supported intents and their trigger keywords."""
    return {
        "supported_intents": _intent_service.supported_intents(),
    }
