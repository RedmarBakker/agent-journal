from journal.events.agent.session_ended import SessionEnded
from journal.events.agent_listener import AgentListener
from journal.features.registry import Registry
from journal.hooks.support.researcher_hooks import ResearcherHooks


class ResearchersClosed(AgentListener[SessionEnded]):
    """The main agent's session ends: every researcher row of it is ended."""

    def __init__(self, researchers: ResearcherHooks, registry: Registry) -> None:
        self.researchers, self.registry = researchers, registry

    def handle(self, event: SessionEnded) -> None:
        if self.registry.role_file(event.agent.role).has_researchers():
            self.researchers.main_ended(event)
