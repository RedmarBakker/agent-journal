from journal.events.agent.subagent_ended import SubagentEnded
from journal.events.agent_listener import AgentListener
from journal.features.registry import Registry
from journal.hooks.support.researcher_hooks import ResearcherHooks


class ResearcherEnd(AgentListener[SubagentEnded]):
    """A subagent the main agent sent ends: its row hears its end and is ended."""

    def __init__(self, researchers: ResearcherHooks, registry: Registry) -> None:
        self.researchers, self.registry = researchers, registry

    def handle(self, event: SubagentEnded) -> None:
        if self.registry.role_file(event.agent.role).has_researchers():
            self.researchers.ended(event)
