# SmartFlow-Assistant

> AI-powered smart assistant for task management with Google Calendar integration.

SmartFlow-Assistant is a lightweight **FastAPI** backend that accepts natural-language messages, detects the user's intent (create event, set reminder, list tasks, delete task), and responds with structured JSON results – optionally integrating with Google Calendar (mock implementation included).

---

## Project structure

```
SmartFlow-Assistant/
├── app/
│   ├── main.py                        # FastAPI app + lifespan hooks
│   ├── api/
│   │   └── routes/
│   │       └── assistant.py           # POST /assistant, GET /assistant/intents
│   ├── services/
│   │   ├── intent_service.py          # Rule-based intent detection
│   │   └── task_service.py            # Business logic / orchestration
│   ├── integrations/
│   │   └── google_calendar.py         # Mock Google Calendar client + facade
│   ├── models/
│   │   └── task.py                    # Task dataclass + Intent enum
│   ├── schemas/
│   │   └── assistant.py               # Pydantic request / response schemas
│   └── utils/
│       └── logger.py                  # Centralised logging
├── tests/
│   └── test_assistant.py              # Unit + HTTP integration tests
├── requirements.txt
└── README.md
```

---

## Quick start

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the development server

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://127.0.0.1:8000`.

---

## API reference

### `POST /assistant`

Send a natural-language message; receive a structured response.

**Request body**

| Field      | Type   | Required | Description                             |
|------------|--------|----------|-----------------------------------------|
| `message`  | string | ✅        | Natural-language task description       |
| `timezone` | string | ❌        | IANA timezone (default: `"UTC"`)        |

**Example request**

```bash
curl -X POST http://127.0.0.1:8000/assistant \
     -H "Content-Type: application/json" \
     -d '{"message": "Schedule a team meeting tomorrow at 10am"}'
```

**Example response**

```json
{
  "intent": "create_event",
  "title": "Schedule a team meeting tomorrow at 10am",
  "description": "Schedule a team meeting tomorrow at 10am",
  "due_date": null,
  "integration_ref": "e3f2a1b4-...",
  "details": {
    "calendar_link": "https://calendar.google.com/event?eid=e3f2a1b4-..."
  },
  "message": "✅ Calendar event 'Schedule a team meeting tomorrow at 10am' has been created."
}
```

### `GET /assistant/intents`

Returns the list of supported intents and their trigger keywords.

### `GET /health`

Liveness probe – returns `{"status": "ok"}`.

### Interactive docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc:       `http://127.0.0.1:8000/redoc`

---

## Supported intents

| Intent          | Trigger keywords                                                 |
|-----------------|------------------------------------------------------------------|
| `delete_task`   | delete, remove, cancel, drop, clear                             |
| `create_event`  | schedule, book, create event, add event, meeting, appointment   |
| `set_reminder`  | remind, reminder, alert, notify, don't forget, remember         |
| `list_tasks`    | list, show, what are my, display, tasks, upcoming               |
| `unknown`       | *(fallback when no rule matches)*                               |

---

## Running the tests

```bash
pytest tests/ -v
```

All 22 tests should pass.

---

## Google Calendar integration

`app/integrations/google_calendar.py` contains a `MockGoogleCalendarClient` that
simulates API responses without any credentials.  To connect to the real Google
Calendar API, replace `MockGoogleCalendarClient` with a client built using
`google-api-python-client` and inject it into `GoogleCalendarIntegration` –
no other code changes are required.
