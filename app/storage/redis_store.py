import hashlib
import json
import logging
import os
from typing import Any, Dict

import redis

logger = logging.getLogger("triage")

NOTES_KEY = "triage:patient_notes"
IDEMPOTENCY_KEY_PREFIX = "triage:patient_notes:idempotency:"

_SAVE_NOTE_ONCE_SCRIPT = """
if redis.call('EXISTS', KEYS[2]) == 1 then
    return 0
end
redis.call('SET', KEYS[2], '1')
redis.call('RPUSH', KEYS[1], ARGV[1])
return 1
"""


class RedisStore:
    def __init__(self) -> None:
        host = os.environ.get("REDIS_HOST", "redis")
        self.client = redis.Redis(host=host, port=6379, decode_responses=True)

    def _idempotency_key(self, conversation_id: Any, performative: Any) -> str:
        key_payload = json.dumps(
            [conversation_id, performative],
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        digest = hashlib.sha256(key_payload.encode("utf-8")).hexdigest()
        return f"{IDEMPOTENCY_KEY_PREFIX}{digest}"

    def save_note_once(
        self,
        conversation_id: Any,
        performative: Any,
        note: Dict[str, Any],
    ) -> bool:
        """Persist a note only once for conversation_id + performative.

        A Redis Lua script makes the duplicate check and list append atomic, so
        replayed messages cannot create additional patient notes even under
        concurrent requests.
        """
        note_json = json.dumps(note, sort_keys=True, default=str)
        idempotency_key = self._idempotency_key(conversation_id, performative)
        result = self.client.eval(
            _SAVE_NOTE_ONCE_SCRIPT,
            2,
            NOTES_KEY,
            idempotency_key,
            note_json,
        )
        return int(result) == 1

    def save_note(self, conversation_id: Any, performative: Any, note: Dict[str, Any]) -> None:
        """Backward-compatible wrapper that performs idempotent persistence."""
        self.save_note_once(conversation_id, performative, note)

    def note_count(self) -> int:
        return self.client.llen(NOTES_KEY)

    def reset(self) -> None:
        self.client.flushdb()

