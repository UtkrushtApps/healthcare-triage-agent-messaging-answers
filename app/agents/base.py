from abc import ABC, abstractmethod

from app.models.message import AgentMessage


class BaseAgent(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def describe(self) -> str:
        ...

    def accepts(self, message: AgentMessage) -> bool:
        return message.receiver == self.name

