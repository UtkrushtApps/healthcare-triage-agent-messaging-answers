import logging
from typing import Any

from fastapi import FastAPI, Request, Response

from app.models.message import AgentMessage
from app.services.coordinator import HandlerResult, TriageCoordinator
from app.storage.redis_store import RedisStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("triage")

app = FastAPI(title="Healthcare Triage Agent Messaging")

store = RedisStore()
coordinator = TriageCoordinator(store)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/agent/message")
async def receive_agent_message(request: Request, response: Response) -> dict:
    """Receive an agent message safely.

    The endpoint intentionally accepts the raw request instead of a strict Pydantic
    model so malformed agent envelopes are handled by our domain validation and
    consistently returned as 400 {"error": "invalid agent message: <field>"}
    instead of leaking framework validation errors or uncaught exceptions.
    """
    body: Any
    try:
        body = await request.json()
    except Exception:
        logger.warning(
            "agent_message_rejected status=invalid_json reason=unparseable_request_body"
        )
        body = {}

    try:
        message = AgentMessage.from_payload(body)
        result: HandlerResult = coordinator.handle_message(message)
    except Exception:
        logger.exception("agent_message_error status=unhandled_exception")
        result = HandlerResult(
            status_code=500,
            body={"error": "internal server error"},
        )

    response.status_code = result.status_code
    return result.body

