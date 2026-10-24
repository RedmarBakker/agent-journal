from journal.events.agent.stop import Stop
from journal.events.agent_listener import AgentListener
from journal.features.mcp.support.pending_restart_claim import PendingRestartClaim


class PendingRestart(AgentListener[Stop]):
    """An agent that needs a restart gets it the moment it stops its turn with no subagent or worker running, on its own conversation."""

    def __init__(self, claim: PendingRestartClaim) -> None:
        self.claim = claim

    def handle(self, event: Stop) -> None:
        self.claim.restarted(event.session)
