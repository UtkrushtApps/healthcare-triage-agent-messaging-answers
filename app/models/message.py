from dataclasses import dataclass
from typing import Any, Dict, Optional

REQUIRED_FIELDS = ["sender", "receiver", "conversation_id", "performative", "payload"]


@dataclass
class AgentMessage:
    raw: Dict[str, Any]

    @classmethod
    def from_payload(cls, body: Any) -> "AgentMessage":
        """Create an AgentMessage from arbitrary request JSON.

        Non-object JSON values are treated as an empty message so required-field
        validation can return a deterministic first missing field instead of the
        endpoint crashing on attribute access.
        """
        if isinstance(body, dict):
            return cls(raw=body)
        return cls(raw={})

    def first_missing_required_field(self) -> Optional[str]:
        """Return the first required field that is absent or explicitly null."""
        for field in REQUIRED_FIELDS:
            if field not in self.raw or self.raw.get(field) is None:
                return field
        return None

    @property
    def sender(self) -> Any:
        return self.raw.get("sender")

    @property
    def receiver(self) -> Any:
        return self.raw.get("receiver")

    @property
    def conversation_id(self) -> Any:
        return self.raw.get("conversation_id")

    @property
    def performative(self) -> Any:
        return self.raw.get("performative")

    @property
    def payload(self) -> Any:
        return self.raw.get("payload")

