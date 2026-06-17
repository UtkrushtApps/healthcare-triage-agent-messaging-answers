import logging
from dataclasses import dataclass
from typing import Any, Dict

from app.models.message import AgentMessage
from app.storage.redis_store import RedisStore

logger = logging.getLogger("triage")


@dataclass
class HandlerResult:
    status_code: int
    body: Dict[str, Any]


class TriageCoordinator:
    def __init__(self, store: RedisStore) -> None:
        self.store = store

    def handle_message(self, message: AgentMessage) -> HandlerResult:
        """Validate, deduplicate, and persist an agent message.

        Required field validation is performed before any storage access so bad
        envelopes cannot create partial notes. Persistence is idempotent on the
        conversation_id + performative pair.
        """
        missing_field = message.first_missing_required_field()
        if missing_field is not None:
            logger.warning(
                "agent_message_rejected status=invalid_message missing_field=%s "
                "sender=%r receiver=%r conversation_id=%r performative=%r raw_keys=%s",
                missing_field,
                message.sender,
                message.receiver,
                message.conversation_id,
                message.performative,
                sorted(message.raw.keys()),
            )
            return HandlerResult(
                status_code=400,
                body={"error": f"invalid agent message: {missing_field}"},
            )

        note = {
            "sender": message.sender,
            "receiver": message.receiver,
            "conversation_id": message.conversation_id,
            "performative": message.performative,
            "payload": message.payload,
        }

        try:
            stored = self.store.save_note_once(
                message.conversation_id,
                message.performative,
                note,
            )
        except Exception:
            logger.exception(
                "agent_message_storage_error status=failed sender=%r receiver=%r "
                "conversation_id=%r performative=%r",
                message.sender,
                message.receiver,
                message.conversation_id,
                message.performative,
            )
            return HandlerResult(
                status_code=500,
                body={"error": "internal server error"},
            )

        if stored:
            logger.info(
                "agent_message_accepted status=stored sender=%r receiver=%r "
                "conversation_id=%r performative=%r",
                message.sender,
                message.receiver,
                message.conversation_id,
                message.performative,
            )
            return HandlerResult(status_code=200, body={"status": "stored"})

        logger.info(
            "agent_message_ignored status=duplicate_ignored sender=%r receiver=%r "
            "conversation_id=%r performative=%r",
            message.sender,
            message.receiver,
            message.conversation_id,
            message.performative,
        )
        return HandlerResult(status_code=200, body={"status": "duplicate_ignored"})

