from journal.events.agent.subagent_started import SubagentStarted
from journal.events.agent_listener import AgentListener
from journal.features.registry import Registry
from journal.hooks.support.researcher_hooks import ResearcherHooks


class ResearcherStart(AgentListener[SubagentStarted]):
    """A subagent the main agent sent starts: its own row is made and put to work researching, before the subagent's first hook."""

    def __init__(self, researchers: ResearcherHooks, registry: Registry) -> None:
        self.researchers, self.registry = researchers, registry

    def handle(self, event: SubagentStarted) -> None:
        if self.registry.role_file(event.agent.role).has_researchers():
            self.researchers.started(event)
