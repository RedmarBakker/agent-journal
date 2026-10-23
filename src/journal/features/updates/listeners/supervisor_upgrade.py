from journal.events.agent.stop import Stop
from journal.events.agent_listener import AgentListener
from journal.features.updates.support.outdated_supervisors import OutdatedSupervisors
from journal.providers.providers import Providers
from journal.repositories.command_outputs import CommandOutputs
from journal.supervisor_link import SupervisorLink


class SupervisorUpgrade(AgentListener[Stop]):
    """A supervisor found at the journal's boot to run older code than its files on disk is restarted once, when its agent ends a turn with none of the environment's commands running, the agent resumed on its conversation, so no turn and no command is cut off and no launch is needed."""

    def __init__(self, supervisor: SupervisorLink, providers: Providers, outdated: OutdatedSupervisors, outputs: CommandOutputs) -> None:
        self.supervisor, self.providers, self.outdated, self.outputs = supervisor, providers, outdated, outputs

    def handle(self, event: Stop) -> None:
        if event.subagent or self.outputs.running(event.environment_id) or not self.outdated.claim(event.environment_id):
            return
        self.supervisor.restart_supervisor(event.environment_id, self.providers.lookup(event.provider).resume(event.session))
