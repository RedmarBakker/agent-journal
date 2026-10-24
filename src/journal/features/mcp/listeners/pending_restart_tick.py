from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.mcp.support.pending_restart_claim import PendingRestartClaim


class PendingRestartTick(AgentListener[Ticked]):
    """An agent that needs a restart and was busy when its turn ended gets it at the first tick that finds it idle."""

    def __init__(self, claim: PendingRestartClaim) -> None:
        self.claim = claim

    def handle(self, event: Ticked) -> None:
        self.claim.restarted(event.session)
