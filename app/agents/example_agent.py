from app.agents.base import BaseAgent


class IntakeAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="IntakeAgent")

    def describe(self) -> str:
        return "Collects patient intake details and forwards triage requests."


class NurseAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="NurseAgent")

    def describe(self) -> str:
        return "Reviews triage requests and records patient notes."

